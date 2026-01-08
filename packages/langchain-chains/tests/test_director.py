"""Tests for director chain."""

import os
import pytest


def test_director_system_prompt_defined():
    """Test that director system prompt is defined."""
    from packages.langchain_chains.src import DIRECTOR_SYSTEM_PROMPT
    
    assert len(DIRECTOR_SYSTEM_PROMPT) > 100
    assert "creative director" in DIRECTOR_SYSTEM_PROMPT.lower()


def test_prompts_registry():
    """Test prompts registry."""
    from packages.langchain_chains.src import PROMPTS
    
    assert "director" in PROMPTS
    assert "assistant" in PROMPTS
    assert "brainstorm" in PROMPTS


def test_get_prompt():
    """Test prompt retrieval."""
    from packages.langchain_chains.src.prompts import get_prompt
    
    prompt = get_prompt("director")
    assert "creative director" in prompt.lower()


def test_get_unknown_prompt():
    """Test error on unknown prompt."""
    from packages.langchain_chains.src.prompts import get_prompt
    
    with pytest.raises(ValueError, match="Unknown prompt"):
        get_prompt("nonexistent")


@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set"
)
class TestWithApiKey:
    """Tests that require API key."""
    
    def test_create_director_chain(self):
        """Test chain creation."""
        from packages.langchain_chains.src import create_director_chain
        
        chain = create_director_chain("test-chain-session")
        assert chain is not None
        assert chain.memory is not None
    
    def test_create_chain_with_custom_prompt(self):
        """Test chain with custom prompt."""
        from packages.langchain_chains.src import create_director_chain
        
        custom_prompt = "You are a helpful assistant."
        chain = create_director_chain(
            "custom-prompt-session",
            system_prompt=custom_prompt,
        )
        assert chain is not None
