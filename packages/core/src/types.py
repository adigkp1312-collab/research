"""
Shared Type Definitions

Common types used across all packages.

Team: Platform
"""

from typing import TypedDict, Optional, List
from enum import Enum


class MessageRole(str, Enum):
    """Role of a message in a conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(TypedDict):
    """A single message in a conversation."""
    role: MessageRole
    content: str


class ChatRequest(TypedDict):
    """Request payload for chat endpoints."""
    message: str
    session_id: str


class ChatResponse(TypedDict):
    """Response payload for chat endpoints."""
    response: str
    session_id: str


class HealthStatus(TypedDict):
    """Health check response."""
    status: str
    app_name: str
    gemini_configured: bool
    langsmith_enabled: bool
    active_sessions: int
    model: str


class ModelInfo(TypedDict):
    """Model information."""
    model: str
    model_name: str
    provider: str
    api_type: str
