"""Tests for chain implementations."""

import os
import pytest
from src.chains import DIRECTOR_SYSTEM_PROMPT
from src.langchain_client import MODELS


# Tests that require API keys
@pytest.mark.skipif(
    not os.environ.get("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set"
)
class TestChainCreation:
    """Tests that require API keys for chain creation."""
    
    def test_create_director_chain(self):
        """Test that director chain is created successfully."""
        from src.chains import create_director_chain
        chain = create_director_chain(
            session_id="test-chain-session",
            model_id=MODELS["GEMINI_FLASH"],
        )
        assert chain is not None
        assert chain.memory is not None

    def test_director_chain_with_custom_prompt(self):
        """Test director chain with custom system prompt."""
        from src.chains import create_director_chain
        custom_prompt = "You are a helpful assistant."
        chain = create_director_chain(
            session_id="custom-prompt-session",
            system_prompt=custom_prompt,
        )
        assert chain is not None


# Tests that don't require API keys
def test_director_system_prompt_not_empty():
    """Test that default system prompt is defined."""
    assert len(DIRECTOR_SYSTEM_PROMPT) > 100
    assert "creative director" in DIRECTOR_SYSTEM_PROMPT.lower()


def test_models_defined():
    """Test that model constants are defined."""
    assert "GEMINI_FLASH" in MODELS
    assert "CLAUDE_SONNET" in MODELS
    assert "GPT4_TURBO" in MODELS
