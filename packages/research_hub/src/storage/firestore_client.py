"""
Firestore Client for Research Hub.

Provides async operations for Google Cloud Firestore.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from ..config import GOOGLE_CLOUD_PROJECT


class FirestoreClient:
    """
    Google Cloud Firestore client for research data.

    Uses the Firestore native mode for document storage.
    """

    COLLECTION_NAME = "research_hub_entries"

    def __init__(self, project_id: str = None):
        self.project_id = project_id or GOOGLE_CLOUD_PROJECT
        self._client: Optional[firestore.Client] = None

    @property
    def is_configured(self) -> bool:
        """Check if Firestore is properly configured."""
        return bool(self.project_id)

    def _get_client(self) -> firestore.Client:
        """Get or create Firestore client."""
        if self._client is None:
            self._client = firestore.Client(project=self.project_id)
        return self._client

    @property
    def collection(self):
        """Get the research entries collection."""
        return self._get_client().collection(self.COLLECTION_NAME)

    async def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a document into the collection.

        Args:
            data: Document data (must include 'id' field)

        Returns:
            Inserted document data
        """
        if not self.is_configured:
            raise Exception("Firestore not configured")

        doc_id = data.get("id")
        if not doc_id:
            raise ValueError("Document must have an 'id' field")

        # Add timestamps
        data["created_at"] = data.get("created_at", datetime.utcnow().isoformat())
        data["updated_at"] = datetime.utcnow().isoformat()

        # Use set() with document ID
        doc_ref = self.collection.document(doc_id)
        doc_ref.set(data)

        return data

    async def select(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = "created_at",
        order_desc: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Query documents from the collection.

        Args:
            filters: Field filters as {field: value}
            order_by: Field to order by
            order_desc: Whether to order descending
            limit: Maximum documents to return
            offset: Number of documents to skip

        Returns:
            List of matching documents
        """
        if not self.is_configured:
            raise Exception("Firestore not configured")

        query = self.collection

        # Apply filters
        if filters:
            for field, value in filters.items():
                if value is not None:
                    query = query.where(filter=FieldFilter(field, "==", value))

        # Apply ordering
        direction = firestore.Query.DESCENDING if order_desc else firestore.Query.ASCENDING
        query = query.order_by(order_by, direction=direction)

        # Apply pagination
        if offset > 0:
            # Firestore doesn't have native offset, so we need to fetch and skip
            # For production, use cursor-based pagination instead
            query = query.limit(limit + offset)
            docs = list(query.stream())
            docs = docs[offset:offset + limit]
        else:
            query = query.limit(limit)
            docs = list(query.stream())

        return [doc.to_dict() for doc in docs]

    async def select_one(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document data or None
        """
        if not self.is_configured:
            raise Exception("Firestore not configured")

        doc_ref = self.collection.document(doc_id)
        doc = doc_ref.get()

        if doc.exists:
            return doc.to_dict()
        return None

    async def update(
        self,
        doc_id: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update a document.

        Args:
            doc_id: Document ID
            data: Fields to update
            user_id: Optional user ID for ownership check

        Returns:
            Updated document or None
        """
        if not self.is_configured:
            raise Exception("Firestore not configured")

        doc_ref = self.collection.document(doc_id)
        doc = doc_ref.get()

        if not doc.exists:
            return None

        # Check ownership if user_id provided
        if user_id:
            doc_data = doc.to_dict()
            if doc_data.get("user_id") != user_id:
                return None

        # Add updated timestamp
        data["updated_at"] = datetime.utcnow().isoformat()

        # Update document
        doc_ref.update(data)

        # Return updated document
        return (await self.select_one(doc_id))

    async def delete(
        self,
        doc_id: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Delete a document.

        Args:
            doc_id: Document ID
            user_id: Optional user ID for ownership check

        Returns:
            True if deleted successfully
        """
        if not self.is_configured:
            raise Exception("Firestore not configured")

        doc_ref = self.collection.document(doc_id)
        doc = doc_ref.get()

        if not doc.exists:
            return False

        # Check ownership if user_id provided
        if user_id:
            doc_data = doc.to_dict()
            if doc_data.get("user_id") != user_id:
                return False

        doc_ref.delete()
        return True

    async def search(
        self,
        query: str,
        project_id: Optional[str] = None,
        research_types: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Search documents by text fields.

        Note: Firestore doesn't support full-text search natively.
        For production, consider using Firestore + Algolia or
        Cloud Search integration.

        This implementation does a basic filter and client-side search.

        Args:
            query: Search query
            project_id: Optional project filter
            research_types: Optional research type filter
            limit: Maximum results

        Returns:
            Matching documents
        """
        if not self.is_configured:
            raise Exception("Firestore not configured")

        # Start with base query
        base_query = self.collection

        if project_id:
            base_query = base_query.where(
                filter=FieldFilter("project_id", "==", project_id)
            )

        # Fetch documents and filter client-side
        # Note: For production, use a proper search service
        docs = list(base_query.limit(500).stream())

        query_lower = query.lower()
        results = []

        for doc in docs:
            data = doc.to_dict()

            # Filter by research_types if provided
            if research_types:
                if data.get("research_type") not in research_types:
                    continue

            # Search in title, summary, and input_query
            searchable = " ".join([
                str(data.get("title", "")),
                str(data.get("summary", "")),
                str(data.get("input_query", "")),
            ]).lower()

            if query_lower in searchable:
                results.append(data)

            if len(results) >= limit:
                break

        return results

    async def list_by_project(
        self,
        project_id: str,
        research_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        List all documents for a project.

        Args:
            project_id: Project ID
            research_type: Optional filter by research type
            limit: Maximum documents

        Returns:
            List of documents
        """
        filters = {"project_id": project_id}
        if research_type:
            filters["research_type"] = research_type

        return await self.select(
            filters=filters,
            order_by="created_at",
            order_desc=True,
            limit=limit,
        )


# Singleton instance
_client: Optional[FirestoreClient] = None


def get_firestore_client() -> FirestoreClient:
    """Get the singleton Firestore client."""
    global _client
    if _client is None:
        _client = FirestoreClient()
    return _client
