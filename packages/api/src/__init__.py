"""
API Package - FastAPI Application

REST API endpoints for the LangChain chat service.

Team: Backend
"""

from .app import create_app, app

__all__ = ["create_app", "app"]
