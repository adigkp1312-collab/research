"""
LangChain Chains Package - Conversation Logic

Implements conversation chains for different use cases.

Team: AI/ML
"""

from .director import (
    quick_chat,
    stream_chat,
)
from .prompts import (
    DIRECTOR_SYSTEM_PROMPT,
    PROMPTS,
    get_prompt,
)

__all__ = [
    "quick_chat",
    "stream_chat",
    "DIRECTOR_SYSTEM_PROMPT",
    "PROMPTS",
    "get_prompt",
]
