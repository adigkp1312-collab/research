"""
CORS Middleware Configuration

Team: Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def configure_cors(app: FastAPI, origins: list[str] = None):
    """
    Configure CORS middleware.
    
    Args:
        app: FastAPI application
        origins: List of allowed origins (default: ["*"])
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
