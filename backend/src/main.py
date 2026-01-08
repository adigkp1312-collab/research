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
from .langchain_client import GEMINI_MODEL


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
    
    if settings.gemini_api_key:
        print("✅ Gemini API key configured")
    else:
        print("⚠️ GEMINI_API_KEY not set - API calls will fail")
        print("   Set it via Lambda environment variables")
    
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


class ChatResponse(BaseModel):
    """Non-streaming chat response."""
    response: str
    session_id: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app_name: str
    gemini_configured: bool
    langsmith_enabled: bool
    active_sessions: int
    model: str


# Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        gemini_configured=bool(settings.gemini_api_key),
        langsmith_enabled=settings.langchain_tracing_v2 and bool(settings.langchain_api_key),
        active_sessions=get_active_session_count(),
        model=GEMINI_MODEL,
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
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY not configured. Set it in Lambda environment variables."
        )
    
    try:
        response = await quick_chat(
            session_id=request.session_id,
            message=request.message,
        )
        
        return ChatResponse(
            response=response,
            session_id=request.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint.
    
    Returns tokens as they are generated for real-time display.
    """
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY not configured. Set it in Lambda environment variables."
        )
    
    async def generate():
        try:
            async for token in stream_chat(
                session_id=request.session_id,
                message=request.message,
            ):
                yield token
        except ValueError as e:
            yield f"\n\n[Configuration Error: {str(e)}]"
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
    """Get current model information."""
    return {
        "model": GEMINI_MODEL,
        "model_name": "Gemini 3 Flash (Experimental)",
        "provider": "Google",
        "api_type": "Direct (via GEMINI_API_KEY)",
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
