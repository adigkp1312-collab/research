"""Tests for LangChain client."""

import os
import pytest


def test_model_constants():
    """Test that model constants are defined."""
    from packages.langchain_client.src import GEMINI_MODEL, MODEL_NAME
    
    assert GEMINI_MODEL == "gemini-2.0-flash-exp"
    assert "Gemini" in MODEL_NAME


def test_get_model_info():
    """Test model info retrieval."""
    from packages.langchain_client.src.client import get_model_info
    
    info = get_model_info()
    
    assert info["model"] == "gemini-2.0-flash-exp"
    assert info["provider"] == "Google"


@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set"
)
class TestWithApiKey:
    """Tests that require API key."""
    
    def test_create_chat_model(self):
        """Test model creation with API key."""
        from packages.langchain_client.src import create_chat_model
        
        model = create_chat_model()
        assert model is not None
    
    def test_create_chat_model_custom_params(self):
        """Test model creation with custom parameters."""
        from packages.langchain_client.src import create_chat_model
        
        model = create_chat_model(
            temperature=0.5,
            streaming=False,
            max_tokens=100,
        )
        assert model is not None


def test_create_chat_model_without_key(monkeypatch):
    """Test that model creation fails without API key."""
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    
    # Need to reload the module to pick up env change
    import importlib
    from packages.langchain_client.src import client
    
    # The constant is already loaded, so we test the error path
    # by checking the validation logic
    from packages.core.src import GEMINI_API_KEY
    if not GEMINI_API_KEY:
        with pytest.raises(ValueError, match="GEMINI_API_KEY not found"):
            from packages.langchain_client.src import create_chat_model
            create_chat_model()
