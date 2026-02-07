"""
Orbital Nexus — FastAPI Backend Entrypoint

Multi-Satellite Data Fusion Dashboard
Hyperspace Innovation Hackathon 2026 — PS #4
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from app.api.routes import router as api_router
from app.api.auth import router as auth_router

app = FastAPI(
    title="Orbital Nexus API",
    description="Multi-Satellite Data Fusion Dashboard — Backend",
    version="0.1.0",
)

# Allow frontend dev server to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://orbitalnexus.online",
        "http://orbitalnexus.online"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api_router)
app.include_router(auth_router)


@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint — confirms the backend is running."""
    return {"status": "ok", "project": "orbital-nexus", "version": "0.1.0"}
