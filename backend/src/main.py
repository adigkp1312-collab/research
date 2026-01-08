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

from .config import (
    GEMINI_API_KEY,
    LANGCHAIN_TRACING_V2,
    LANGCHAIN_API_KEY,
    LANGCHAIN_PROJECT,
    APP_NAME,
    CORS_ORIGINS,
    validate_config,
)
from .chains import stream_chat, quick_chat
from .memory import clear_session_memory, get_active_session_count
from .langchain_client import GEMINI_MODEL


# Configure LangSmith tracing on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup - validate configuration
    if not validate_config():
        print(f"[{APP_NAME}] Warning: Some required environment variables are missing.")
    else:
        print(f"[{APP_NAME}] Configuration validated successfully.")
    
    # Configure LangSmith tracing (optional)
    if LANGCHAIN_TRACING_V2 and LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
        print(f"✅ LangSmith tracing enabled for project: {LANGCHAIN_PROJECT}")
    else:
        print("⚠️ LangSmith tracing disabled (missing API key)")
    
    if GEMINI_API_KEY:
        print("✅ Gemini API key configured")
    else:
        print("⚠️ GEMINI_API_KEY not set - API calls will fail")
        print("   Set it via Lambda environment variables")
    
    print(f"🚀 {APP_NAME} started")
    
    yield
    
    # Shutdown
    print(f"👋 {APP_NAME} shutting down")


# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    description="LangChain POC - Gemini 3 Flash for Adiyogi Arts",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
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
        app_name=APP_NAME,
        gemini_configured=bool(GEMINI_API_KEY),
        langsmith_enabled=LANGCHAIN_TRACING_V2 and bool(LANGCHAIN_API_KEY),
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
    if not GEMINI_API_KEY:
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
    if not GEMINI_API_KEY:
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
