"""
Memory Buffer - Session State Management

Provides BufferWindowMemory for conversation context.

Team: AI/ML
"""

from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import ChatMessageHistory

# Store session memories (in production, use Redis or database)
_session_memories: dict[str, ConversationBufferWindowMemory] = {}


def get_session_memory(
    session_id: str,
    window_size: int = 10,
) -> ConversationBufferWindowMemory:
    """
    Creates or retrieves a BufferWindowMemory for a session.
    
    BufferWindowMemory keeps the last K messages in context,
    which is ideal for chat applications with limited context windows.
    
    Args:
        session_id: Unique session identifier
        window_size: Number of messages to keep (default: 10)
    
    Returns:
        BufferWindowMemory instance
    
    Example:
        >>> memory = get_session_memory("user-123")
        >>> memory.save_context({"input": "Hi"}, {"output": "Hello!"})
    """
    # Return existing memory if available
    if session_id in _session_memories:
        return _session_memories[session_id]
    
    # Create new memory for this session
    memory = ConversationBufferWindowMemory(
        k=window_size,
        return_messages=True,
        memory_key="history",
        chat_memory=ChatMessageHistory(),
    )
    
    _session_memories[session_id] = memory
    return memory


def clear_session_memory(session_id: str) -> bool:
    """
    Clears memory for a specific session.
    
    Args:
        session_id: Session to clear
    
    Returns:
        True if session existed and was cleared, False otherwise
    """
    if session_id in _session_memories:
        del _session_memories[session_id]
        return True
    return False


def clear_all_memories() -> int:
    """
    Clears all session memories.
    
    Useful for cleanup or testing.
    
    Returns:
        Number of sessions cleared
    """
    count = len(_session_memories)
    _session_memories.clear()
    return count


def get_active_session_count() -> int:
    """Gets the number of active sessions."""
    return len(_session_memories)


def get_session_ids() -> list[str]:
    """Gets list of all active session IDs."""
    return list(_session_memories.keys())
