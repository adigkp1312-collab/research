"""
API Routes

Modular route definitions.

Team: Backend
"""

from .chat import router as chat_router
from .health import router as health_router
from .models import router as models_router
from .datastore import router as datastore_router

__all__ = ["chat_router", "health_router", "models_router", "datastore_router"]
