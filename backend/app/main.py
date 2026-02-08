"""
Orbital Nexus — FastAPI Backend Entrypoint

Multi-Satellite Data Fusion Dashboard
Hyperspace Innovation Hackathon 2026 — PS #4
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

load_dotenv()

from app.api.routes import router as api_router
from app.api.auth import router as auth_router

app = FastAPI(
    title="Orbital Nexus API",
    description="Multi-Satellite Data Fusion Dashboard — Backend",
    version="0.1.0",
)

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "orbital_nexus")
db_client = None

@app.on_event("startup")
async def startup_db_client():
    global db_client
    if MONGO_URI:
        try:
            db_client = AsyncIOMotorClient(MONGO_URI)
            print(f"✅ Connected to MongoDB Atlas: {DB_NAME}")
        except Exception as e:
            print(f"❌ MongoDB Connection Failed: {e}")
    else:
        print("⚠️ MONGO_URI not found. Running without persistence.")

@app.on_event("shutdown")
async def shutdown_db_client():
    if db_client:
        db_client.close()

# Allow frontend dev server to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://orbitalnexus.online",
        "http://orbitalnexus.online",
        "https://orbital-nexus.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api_router)
app.include_router(auth_router)

# Feedback Model
class Feedback(BaseModel):
    query: str
    response: dict
    user_id: str | None = None

@app.post("/api/feedback", tags=["system"])
async def log_feedback(feedback: Feedback):
    """Log user queries and AI responses for audit/improvements."""
    if db_client:
        try:
            db = db_client[DB_NAME]
            result = await db.logs.insert_one(feedback.dict())
            return {"status": "logged", "id": str(result.inserted_id)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    return {"status": "skipped", "reason": "No DB connection"}


@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint — confirms the backend is running."""
    from app.ai.gemini_service import is_ai_available

    return {
        "status": "ok",
        "project": "orbital-nexus",
        "version": "0.1.0",
        "ai_enabled": is_ai_available(),
    }
