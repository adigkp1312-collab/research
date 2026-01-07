"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.memory import clear_all_memories


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_memories():
    """Clear all memories before and after each test."""
    clear_all_memories()
    yield
    clear_all_memories()


@pytest.fixture
def session_id():
    """Generate a unique session ID for tests."""
    import uuid
    return f"test-session-{uuid.uuid4()}"
