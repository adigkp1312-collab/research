"""
Integration Test Configuration

Shared fixtures for integration tests.

Team: QA
"""

import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def api_client():
    """Create API test client."""
    from packages.api.src import app
    return TestClient(app)


@pytest.fixture(scope="function")
def session_id():
    """Generate unique session ID for each test."""
    return f"integration-test-{os.urandom(4).hex()}"


@pytest.fixture(autouse=True)
def clear_memory_after_test(session_id):
    """Clear session memory after each test."""
    yield
    from packages.langchain_memory.src import clear_session_memory
    clear_session_memory(session_id)
