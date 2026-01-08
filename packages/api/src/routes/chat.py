"""
Chat Routes

/chat endpoints for conversation.

Team: Backend
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import sys
sys.path.insert(0, str(__file__).replace('/packages/api/src/routes/chat.py', ''))
from packages.core.src import GEMINI_API_KEY
from packages.langchain_chains.src import stream_chat, quick_chat
from packages.langchain_memory.src import clear_session_memory

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request payload."""
    message: str
    session_id: str


class ChatResponse(BaseModel):
    """Non-streaming chat response."""
    response: str
    session_id: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Non-streaming chat endpoint.
    
    Returns complete response after generation.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY not configured"
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


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint.
    
    Returns tokens as they are generated.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY not configured"
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


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear memory for a specific session."""
    result = clear_session_memory(session_id)
    return {
        "status": "ok",
        "message": f"Session {session_id} {'cleared' if result else 'not found'}",
    }
