"""
Test Helpers

Shared utilities for testing.

Team: QA
"""

import os
import json
from pathlib import Path


def get_fixture(name: str) -> dict:
    """Load a fixture by name."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures"
    fixture_file = fixtures_dir / f"{name}.json"
    
    if not fixture_file.exists():
        raise FileNotFoundError(f"Fixture not found: {name}")
    
    with open(fixture_file) as f:
        return json.load(f)


def requires_api_key(func):
    """Decorator to skip tests without API key."""
    import pytest
    return pytest.mark.skipif(
        not os.environ.get("GEMINI_API_KEY"),
        reason="GEMINI_API_KEY not set"
    )(func)


def generate_session_id() -> str:
    """Generate a unique session ID for testing."""
    return f"test-{os.urandom(4).hex()}"


class MockResponse:
    """Mock response object for testing."""
    
    def __init__(self, data: dict, status_code: int = 200):
        self.data = data
        self.status_code = status_code
    
    def json(self):
        return self.data
