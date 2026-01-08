"""
Health Check Routes

/health and / endpoints.

Team: Backend
"""

from fastapi import APIRouter
from pydantic import BaseModel

# PYTHONPATH is set by handler.py or main.py entry point
from packages.core.src import APP_NAME, GEMINI_API_KEY, LANGCHAIN_TRACING_V2, LANGCHAIN_API_KEY
from packages.langchain_memory.src import get_active_session_count
from packages.langchain_client.src import GEMINI_MODEL

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app_name: str
    gemini_configured: bool
    langsmith_enabled: bool
    active_sessions: int
    model: str


@router.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return HealthResponse(
        status="ok",
        app_name=APP_NAME,
        gemini_configured=bool(GEMINI_API_KEY),
        langsmith_enabled=LANGCHAIN_TRACING_V2 and bool(LANGCHAIN_API_KEY),
        active_sessions=get_active_session_count(),
        model=GEMINI_MODEL,
    )


@router.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return await root()
