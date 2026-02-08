"""
Vercel Serverless Function Entry Point

Wraps the FastAPI app for Vercel's Python runtime.
"""

import sys
from pathlib import Path

# Add backend directory to Python path so imports work
backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the FastAPI app
from app.main import app  # noqa: E402, F401
