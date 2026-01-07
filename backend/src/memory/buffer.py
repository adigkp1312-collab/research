"""
Memory Management for LangChain Conversations

Provides conversation memory that maintains context across chat turns.
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


def clear_session_memory(session_id: str) -> None:
    """Clears memory for a specific session."""
    if session_id in _session_memories:
        del _session_memories[session_id]


def clear_all_memories() -> None:
    """Clears all session memories. Useful for cleanup or testing."""
    _session_memories.clear()


def get_active_session_count() -> int:
    """Gets the number of active sessions."""
    return len(_session_memories)
