"""
Memory Buffer - Session State Management

Provides custom conversation memory for Vertex AI.

Team: AI/ML
"""

from typing import List, Dict

# Store session memories (in production, use Redis or database)
_session_memories: dict[str, 'ConversationMemory'] = {}


class ConversationMemory:
    """Custom conversation memory with windowing."""
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.messages: List[Dict[str, str]] = []
    
    def save_context(self, input_dict: Dict[str, str], output_dict: Dict[str, str]):
        """Save a user input and assistant output."""
        if "input" in input_dict:
            self.messages.append({"role": "user", "content": input_dict["input"]})
        if "output" in output_dict:
            self.messages.append({"role": "assistant", "content": output_dict["output"]})
        
        # Keep only last window_size messages
        if len(self.messages) > self.window_size * 2:  # *2 because each exchange has 2 messages
            self.messages = self.messages[-(self.window_size * 2):]
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in memory."""
        return self.messages.copy()
    
    def clear(self):
        """Clear all messages."""
        self.messages = []


def get_session_memory(
    session_id: str,
    window_size: int = 10,
) -> ConversationMemory:
    """
    Creates or retrieves a ConversationMemory for a session.
    
    ConversationMemory keeps the last K message exchanges in context,
    which is ideal for chat applications with limited context windows.
    
    Args:
        session_id: Unique session identifier
        window_size: Number of message exchanges to keep (default: 10)
    
    Returns:
        ConversationMemory instance
    
    Example:
        >>> memory = get_session_memory("user-123")
        >>> memory.save_context({"input": "Hi"}, {"output": "Hello!"})
    """
    # Return existing memory if available
    if session_id in _session_memories:
        return _session_memories[session_id]
    
    # Create new memory for this session
    memory = ConversationMemory(window_size=window_size)
    
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
