"""
API + Chains Integration Tests

Tests the full flow from API to chains.

Team: QA
"""

import os
import pytest


def test_health_returns_chain_model(api_client):
    """Test that health endpoint returns correct model from chains."""
    response = api_client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["model"] == "gemini-2.0-flash-exp"


def test_session_memory_persists(api_client, session_id):
    """Test that session memory persists across requests."""
    from packages.langchain_memory.src import get_session_memory, get_active_session_count
    
    # Get initial count
    initial_count = get_active_session_count()
    
    # Access session
    memory = get_session_memory(session_id)
    assert memory is not None
    
    # Count should increase
    assert get_active_session_count() == initial_count + 1


@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set"
)
class TestFullFlow:
    """Full integration tests requiring API key."""
    
    def test_chat_uses_director_chain(self, api_client, session_id):
        """Test that chat endpoint uses director chain."""
        response = api_client.post(
            "/chat",
            json={
                "message": "What do you specialize in?",
                "session_id": session_id,
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Director should mention video production or storytelling
        content = data["response"].lower()
        assert any(word in content for word in ["video", "story", "creative", "production"])
    
    def test_memory_maintains_context(self, api_client, session_id):
        """Test that conversation memory maintains context."""
        # First message
        response1 = api_client.post(
            "/chat",
            json={
                "message": "My name is Test User.",
                "session_id": session_id,
            }
        )
        assert response1.status_code == 200
        
        # Second message asking about name
        response2 = api_client.post(
            "/chat",
            json={
                "message": "What is my name?",
                "session_id": session_id,
            }
        )
        assert response2.status_code == 200
        
        # Should remember the name
        assert "test" in response2.json()["response"].lower()
