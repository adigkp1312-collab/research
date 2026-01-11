"""
FastAPI Application Factory

Creates and configures the FastAPI application.

Team: Backend
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import from core package
# PYTHONPATH is set by handler.py or main.py entry point
from packages.core.src import (
    GOOGLE_CLOUD_PROJECT,
    LANGCHAIN_TRACING_V2,
    LANGCHAIN_API_KEY,
    LANGCHAIN_PROJECT,
    APP_NAME,
    CORS_ORIGINS,
    validate_config,
)

# Import routes
from .routes import chat_router, health_router, models_router, datastore_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    if not validate_config():
        print(f"[{APP_NAME}] Warning: Missing required configuration")
    else:
        print(f"[{APP_NAME}] Configuration validated")
    
    # Configure LangSmith tracing (optional)
    if LANGCHAIN_TRACING_V2 and LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
        print(f"✅ LangSmith tracing enabled: {LANGCHAIN_PROJECT}")
    
    if GOOGLE_CLOUD_PROJECT:
        print("✅ Vertex AI configured")
    else:
        print("⚠️ GOOGLE_CLOUD_PROJECT not set")
    
    print(f"🚀 {APP_NAME} started")
    
    yield
    
    print(f"👋 {APP_NAME} shutting down")


def create_app() -> FastAPI:
    """
    Application factory.
    
    Returns:
        Configured FastAPI application
    """
    application = FastAPI(
        title=APP_NAME,
        description="Vertex AI + Gemini for Adiyogi Arts",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    application.include_router(health_router, tags=["Health"])
    application.include_router(chat_router, prefix="/chat", tags=["Chat"])
    application.include_router(models_router, prefix="/models", tags=["Models"])
    application.include_router(datastore_router, prefix="/datastore", tags=["Datastore"])
    
    return application


# Create default app instance
app = create_app()
