"""Tests for memory management."""

import pytest
from src.memory import (
    get_session_memory,
    clear_session_memory,
    clear_all_memories,
    get_active_session_count,
)


def test_get_session_memory_creates_new():
    """Test that get_session_memory creates new memory for unknown session."""
    memory = get_session_memory("new-session-123")
    assert memory is not None
    assert get_active_session_count() == 1


def test_get_session_memory_returns_existing():
    """Test that get_session_memory returns same memory for same session."""
    memory1 = get_session_memory("session-abc")
    memory2 = get_session_memory("session-abc")
    assert memory1 is memory2
    assert get_active_session_count() == 1


def test_clear_session_memory():
    """Test clearing a specific session."""
    get_session_memory("session-to-clear")
    assert get_active_session_count() == 1
    
    clear_session_memory("session-to-clear")
    assert get_active_session_count() == 0


def test_clear_all_memories():
    """Test clearing all sessions."""
    get_session_memory("session-1")
    get_session_memory("session-2")
    get_session_memory("session-3")
    assert get_active_session_count() == 3
    
    clear_all_memories()
    assert get_active_session_count() == 0


def test_memory_window_size():
    """Test that memory respects window size configuration."""
    memory = get_session_memory("windowed-session", window_size=5)
    assert memory.k == 5
