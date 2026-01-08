"""Tests for core configuration."""

import os
import pytest


def test_config_imports():
    """Test that config module imports successfully."""
    from packages.core.src import config
    assert hasattr(config, 'GEMINI_API_KEY')
    assert hasattr(config, 'validate_config')


def test_validate_config_without_key(monkeypatch):
    """Test validation fails without GEMINI_API_KEY."""
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    
    # Re-import to get fresh config
    import importlib
    from packages.core.src import config
    importlib.reload(config)
    
    with pytest.warns(UserWarning, match="Missing required"):
        result = config.validate_config()
    
    # Note: validate_config checks the module-level constant
    # which may have been set before monkeypatch


def test_get_config_summary():
    """Test config summary generation."""
    from packages.core.src.config import get_config_summary
    
    summary = get_config_summary()
    
    assert 'gemini_configured' in summary
    assert 'langsmith_enabled' in summary
    assert 'debug' in summary


def test_types_defined():
    """Test that all types are defined."""
    from packages.core.src.types import (
        MessageRole,
        Message,
        ChatRequest,
        ChatResponse,
        HealthStatus,
    )
    
    assert MessageRole.USER == "user"
    assert MessageRole.ASSISTANT == "assistant"
