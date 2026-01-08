"""
Models Routes

/models endpoints for model information.

Team: Backend
"""

from fastapi import APIRouter

# PYTHONPATH is set by handler.py or main.py entry point
from packages.langchain_client.src import GEMINI_MODEL, MODEL_NAME
from packages.langchain_client.src.client import get_model_info

router = APIRouter()


@router.get("")
async def list_models():
    """Get current model information."""
    return get_model_info()


@router.get("/current")
async def current_model():
    """Get current model details."""
    return {
        "model": GEMINI_MODEL,
        "name": MODEL_NAME,
    }
