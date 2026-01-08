"""Tests for chat endpoints."""

import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client."""
    from packages.api.src import app
    return TestClient(app)


@pytest.fixture
def session_id():
    """Generate unique session ID."""
    return f"test-session-{os.urandom(4).hex()}"


def test_clear_session(client, session_id):
    """Test session clearing endpoint."""
    response = client.delete(f"/chat/session/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set"
)
class TestChatIntegration:
    """Integration tests requiring API key."""
    
    def test_chat_endpoint(self, client, session_id):
        """Test non-streaming chat."""
        response = client.post(
            "/chat",
            json={
                "message": "Say hello",
                "session_id": session_id,
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert len(data["response"]) > 0
    
    def test_chat_stream_endpoint(self, client, session_id):
        """Test streaming chat."""
        with client.stream(
            "POST",
            "/chat/stream",
            json={
                "message": "Say hi in one word",
                "session_id": session_id,
            }
        ) as response:
            assert response.status_code == 200
            content = b"".join(response.iter_bytes())
            assert len(content) > 0
