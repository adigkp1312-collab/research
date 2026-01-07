"""
LangChain POC - FastAPI Application

Main entry point for the backend API with streaming support.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .config import settings
from .chains import stream_chat, quick_chat
from .memory import clear_session_memory, get_active_session_count
from .langchain_client import MODELS


# Configure LangSmith tracing on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    if settings.langchain_tracing_v2 and settings.langchain_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
        print(f"✅ LangSmith tracing enabled for project: {settings.langchain_project}")
    else:
        print("⚠️ LangSmith tracing disabled (missing API key)")
    
    if settings.openrouter_api_key:
        print("✅ OpenRouter API key configured")
    else:
        print("⚠️ OpenRouter API key not set - API calls will fail")
    
    print(f"🚀 {settings.app_name} started")
    
    yield
    
    # Shutdown
    print(f"👋 {settings.app_name} shutting down")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="LangChain + OpenRouter POC for Adiyogi Arts",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request payload."""
    message: str
    session_id: str
    model_id: str = MODELS["GEMINI_FLASH"]


class ChatResponse(BaseModel):
    """Non-streaming chat response."""
    response: str
    session_id: str
    model_id: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app_name: str
    openrouter_configured: bool
    langsmith_enabled: bool
    active_sessions: int


# Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        openrouter_configured=bool(settings.openrouter_api_key),
        langsmith_enabled=settings.langchain_tracing_v2 and bool(settings.langchain_api_key),
        active_sessions=get_active_session_count(),
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint (alias)."""
    return await root()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Non-streaming chat endpoint.
    
    Returns the complete response after generation is finished.
    """
    if not settings.openrouter_api_key:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    
    try:
        response = await quick_chat(
            session_id=request.session_id,
            message=request.message,
            model_id=request.model_id,
        )
        
        return ChatResponse(
            response=response,
            session_id=request.session_id,
            model_id=request.model_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint.
    
    Returns tokens as they are generated for real-time display.
    """
    if not settings.openrouter_api_key:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    
    async def generate():
        try:
            async for token in stream_chat(
                session_id=request.session_id,
                message=request.message,
                model_id=request.model_id,
            ):
                yield token
        except Exception as e:
            yield f"\n\n[Error: {str(e)}]"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear memory for a specific session."""
    clear_session_memory(session_id)
    return {"status": "ok", "message": f"Session {session_id} cleared"}


@app.get("/models")
async def list_models():
    """List available models."""
    return {
        "models": MODELS,
        "default": MODELS["GEMINI_FLASH"],
    }


# Development server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
