"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint returns OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app_name" in data


def test_root_endpoint(client: TestClient):
    """Test root endpoint returns health info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_list_models(client: TestClient):
    """Test models listing endpoint."""
    response = client.get("/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "default" in data
    assert "GEMINI_FLASH" in data["models"]


def test_clear_session(client: TestClient, session_id: str):
    """Test session clearing endpoint."""
    response = client.delete(f"/session/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


# Integration tests (require API keys)
@pytest.mark.skipif(
    not pytest.importorskip("os").environ.get("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set"
)
class TestChatIntegration:
    """Integration tests that require API keys."""
    
    def test_chat_endpoint(self, client: TestClient, session_id: str):
        """Test non-streaming chat endpoint."""
        response = client.post(
            "/chat",
            json={
                "message": "Hello, who are you?",
                "session_id": session_id,
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert len(data["response"]) > 0
    
    def test_chat_stream_endpoint(self, client: TestClient, session_id: str):
        """Test streaming chat endpoint."""
        with client.stream(
            "POST",
            "/chat/stream",
            json={
                "message": "Say hello in one word",
                "session_id": session_id,
            }
        ) as response:
            assert response.status_code == 200
            content = b"".join(response.iter_bytes())
            assert len(content) > 0
