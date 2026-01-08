"""Tests for memory buffer."""

import pytest


def test_get_session_memory():
    """Test creating a new session memory."""
    from packages.langchain_memory.src import get_session_memory, clear_all_memories
    
    # Clear any existing state
    clear_all_memories()
    
    memory = get_session_memory("test-session-1")
    
    assert memory is not None
    assert memory.memory_key == "history"


def test_get_same_session_memory():
    """Test retrieving existing session memory."""
    from packages.langchain_memory.src import get_session_memory, clear_all_memories
    
    clear_all_memories()
    
    memory1 = get_session_memory("test-session-2")
    memory2 = get_session_memory("test-session-2")
    
    assert memory1 is memory2


def test_clear_session_memory():
    """Test clearing a specific session."""
    from packages.langchain_memory.src import (
        get_session_memory,
        clear_session_memory,
        clear_all_memories,
    )
    
    clear_all_memories()
    
    get_session_memory("test-session-3")
    
    result = clear_session_memory("test-session-3")
    assert result is True
    
    result = clear_session_memory("nonexistent")
    assert result is False


def test_get_active_session_count():
    """Test counting active sessions."""
    from packages.langchain_memory.src import (
        get_session_memory,
        get_active_session_count,
        clear_all_memories,
    )
    
    clear_all_memories()
    
    assert get_active_session_count() == 0
    
    get_session_memory("session-a")
    get_session_memory("session-b")
    
    assert get_active_session_count() == 2


def test_clear_all_memories():
    """Test clearing all sessions."""
    from packages.langchain_memory.src import (
        get_session_memory,
        clear_all_memories,
        get_active_session_count,
    )
    
    get_session_memory("session-x")
    get_session_memory("session-y")
    
    count = clear_all_memories()
    
    assert count >= 2
    assert get_active_session_count() == 0


def test_custom_window_size():
    """Test custom window size."""
    from packages.langchain_memory.src import get_session_memory, clear_all_memories
    
    clear_all_memories()
    
    memory = get_session_memory("test-window", window_size=5)
    
    assert memory.k == 5
