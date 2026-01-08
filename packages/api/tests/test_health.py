"""Tests for health endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client."""
    from packages.api.src import app
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint returns health info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app_name" in data


def test_health_endpoint(client):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_health_response_fields(client):
    """Test health response contains all fields."""
    response = client.get("/health")
    data = response.json()
    
    assert "status" in data
    assert "app_name" in data
    assert "gemini_configured" in data
    assert "langsmith_enabled" in data
    assert "active_sessions" in data
    assert "model" in data
