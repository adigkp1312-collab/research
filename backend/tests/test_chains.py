"""Tests for chain implementations."""

import pytest
from src.chains import create_director_chain, DIRECTOR_SYSTEM_PROMPT
from src.langchain_client import MODELS


def test_create_director_chain():
    """Test that director chain is created successfully."""
    chain = create_director_chain(
        session_id="test-chain-session",
        model_id=MODELS["GEMINI_FLASH"],
    )
    assert chain is not None
    assert chain.memory is not None


def test_director_chain_with_custom_prompt():
    """Test director chain with custom system prompt."""
    custom_prompt = "You are a helpful assistant."
    chain = create_director_chain(
        session_id="custom-prompt-session",
        system_prompt=custom_prompt,
    )
    assert chain is not None


def test_director_system_prompt_not_empty():
    """Test that default system prompt is defined."""
    assert len(DIRECTOR_SYSTEM_PROMPT) > 100
    assert "creative director" in DIRECTOR_SYSTEM_PROMPT.lower()
