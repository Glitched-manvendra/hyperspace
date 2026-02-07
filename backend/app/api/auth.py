"""
Auth Routes — Orbital Nexus

Simple phone + password authentication for farmers.
Uses JWT tokens for session management. Stores users in a local JSON file
(no external DB dependency — perfect for hackathon demo).

Endpoints:
  POST /api/auth/signup   — register with phone + password + name
  POST /api/auth/login    — login with phone + password
  GET  /api/auth/me       — get current user from JWT token
"""

import json
import hashlib
import hmac
import time
import os
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

logger = logging.getLogger("orbital.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ── Config ────────────────────────────────────────────────────────
JWT_SECRET = os.environ.get("JWT_SECRET", "orbital-nexus-hackathon-2026-secret-key")
TOKEN_EXPIRY = 86400 * 7  # 7 days
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_USERS_FILE = _DATA_DIR / "users.json"


# ── Schemas ───────────────────────────────────────────────────────
class SignupRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15, description="Mobile number")
    password: str = Field(..., min_length=4, description="Password")
    name: str = Field(..., min_length=1, description="Farmer's name")
    village: str = Field(default="", description="Village / city name")


class LoginRequest(BaseModel):
    phone: str = Field(..., description="Mobile number")
    password: str = Field(..., description="Password")


class AuthResponse(BaseModel):
    token: str
    user: dict[str, Any]


class UserProfile(BaseModel):
    phone: str
    name: str
    village: str
    created_at: float


# ── Helpers ───────────────────────────────────────────────────────
def _hash_password(password: str) -> str:
    """SHA-256 hash with salt."""
    return hashlib.sha256(f"orbital:{password}:nexus".encode()).hexdigest()


def _create_token(phone: str) -> str:
    """Create a simple HMAC-based token (JWT-like, no library needed)."""
    payload = f"{phone}:{int(time.time()) + TOKEN_EXPIRY}"
    sig = hmac.new(JWT_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"


def _verify_token(token: str) -> str | None:
    """Verify token and return phone number, or None if invalid/expired."""
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return None
        phone, expiry_str, sig = parts
        payload = f"{phone}:{expiry_str}"
        expected = hmac.new(
            JWT_SECRET.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        if int(expiry_str) < int(time.time()):
            return None
        return phone
    except Exception:
        return None


def _load_users() -> dict[str, Any]:
    """Load user store from JSON file."""
    if not _USERS_FILE.exists():
        return {}
    try:
        return json.loads(_USERS_FILE.read_text())
    except Exception:
        return {}


def _save_users(users: dict[str, Any]) -> None:
    """Persist user store to JSON file."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _USERS_FILE.write_text(json.dumps(users, indent=2))


# ── Endpoints ─────────────────────────────────────────────────────
@router.post("/signup", response_model=AuthResponse)
async def signup(req: SignupRequest) -> AuthResponse:
    """Register a new farmer account."""
    users = _load_users()

    if req.phone in users:
        raise HTTPException(status_code=409, detail="Phone number already registered")

    user_data = {
        "phone": req.phone,
        "name": req.name,
        "village": req.village,
        "password_hash": _hash_password(req.password),
        "created_at": time.time(),
    }
    users[req.phone] = user_data
    _save_users(users)

    token = _create_token(req.phone)
    logger.info("New user registered: %s (%s)", req.name, req.phone)

    return AuthResponse(
        token=token,
        user={"phone": req.phone, "name": req.name, "village": req.village},
    )


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest) -> AuthResponse:
    """Login with phone + password."""
    users = _load_users()

    user = users.get(req.phone)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid phone number or password")

    if user["password_hash"] != _hash_password(req.password):
        raise HTTPException(status_code=401, detail="Invalid phone number or password")

    token = _create_token(req.phone)
    logger.info("User logged in: %s", req.phone)

    return AuthResponse(
        token=token,
        user={
            "phone": user["phone"],
            "name": user["name"],
            "village": user.get("village", ""),
        },
    )


@router.get("/me")
async def get_current_user(authorization: str = Header(default="")) -> dict:
    """Get the currently authenticated user from the token."""
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")

    phone = _verify_token(token)
    if not phone:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    users = _load_users()
    user = users.get(phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "phone": user["phone"],
        "name": user["name"],
        "village": user.get("village", ""),
        "created_at": user["created_at"],
    }
