"""Storage layer for research data using Google Cloud Firestore."""

from .firestore_client import FirestoreClient, get_firestore_client
from .research_repo import ResearchRepository

__all__ = [
    "FirestoreClient",
    "get_firestore_client",
    "ResearchRepository",
]
