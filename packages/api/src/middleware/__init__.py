"""
API Middleware

Custom middleware for the API.

Team: Backend
"""

from .cors import configure_cors

__all__ = ["configure_cors"]
