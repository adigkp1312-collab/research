"""
Research Repository - High-level data access layer.

Provides domain-specific operations for research entries using Firestore.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from .firestore_client import get_firestore_client, FirestoreClient
from ..models import (
    ResearchEntry,
    ResearchResult,
    ResearchInput,
    ResearchType,
    ResearchStatus,
    InputType,
)


class ResearchRepository:
    """
    Repository for research entry CRUD operations.

    Handles conversion between domain models and Firestore documents.
    """

    def __init__(self, client: Optional[FirestoreClient] = None):
        self._client = client or get_firestore_client()

    @property
    def is_configured(self) -> bool:
        """Check if storage is configured."""
        return self._client.is_configured

    async def create(
        self,
        project_id: str,
        user_id: str,
        research_type: ResearchType,
        input: ResearchInput,
        result: ResearchResult,
        title: str,
        tags: List[str] = None,
    ) -> ResearchEntry:
        """
        Create a new research entry.

        Args:
            project_id: Project UUID
            user_id: User UUID
            research_type: Type of research
            input: Research input data
            result: Research result data
            title: Display title
            tags: Optional tags

        Returns:
            Created ResearchEntry
        """
        entry = ResearchEntry.create(
            project_id=project_id,
            user_id=user_id,
            research_type=research_type,
            input=input,
            result=result,
            title=title,
            tags=tags,
        )

        data = entry.to_dict()
        await self._client.insert(data)

        return entry

    async def get_by_id(self, research_id: str) -> Optional[ResearchEntry]:
        """
        Get a research entry by ID.

        Args:
            research_id: Research entry UUID

        Returns:
            ResearchEntry or None
        """
        data = await self._client.select_one(research_id)
        if data:
            return ResearchEntry.from_dict(data)
        return None

    async def list_by_project(
        self,
        project_id: str,
        research_types: Optional[List[ResearchType]] = None,
        tags: Optional[List[str]] = None,
        status: Optional[ResearchStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ResearchEntry]:
        """
        List research entries for a project.

        Args:
            project_id: Project UUID
            research_types: Optional filter by research types
            tags: Optional filter by tags
            status: Optional filter by status
            limit: Maximum entries to return
            offset: Number of entries to skip

        Returns:
            List of ResearchEntry objects
        """
        filters = {"project_id": project_id}

        if status:
            filters["status"] = status.value

        records = await self._client.select(
            filters=filters,
            limit=limit,
            offset=offset,
        )

        entries = [ResearchEntry.from_dict(r) for r in records]

        # Filter by research_types in Python
        if research_types:
            type_values = [t.value for t in research_types]
            entries = [e for e in entries if e.research_type.value in type_values]

        # Filter by tags in Python
        if tags:
            entries = [e for e in entries if any(t in e.tags for t in tags)]

        return entries

    async def update(
        self,
        research_id: str,
        user_id: str,
        updates: Dict[str, Any],
    ) -> Optional[ResearchEntry]:
        """
        Update a research entry.

        Args:
            research_id: Research entry UUID
            user_id: User UUID (for ownership check)
            updates: Fields to update

        Returns:
            Updated ResearchEntry or None
        """
        updates["updated_at"] = datetime.utcnow().isoformat()

        data = await self._client.update(research_id, updates, user_id)
        if data:
            return ResearchEntry.from_dict(data)
        return None

    async def delete(
        self,
        research_id: str,
        user_id: str,
    ) -> bool:
        """
        Delete a research entry.

        Args:
            research_id: Research entry UUID
            user_id: User UUID (for ownership check)

        Returns:
            True if deleted successfully
        """
        return await self._client.delete(research_id, user_id)

    async def search(
        self,
        query: str,
        project_id: Optional[str] = None,
        research_types: Optional[List[ResearchType]] = None,
        limit: int = 20,
    ) -> List[ResearchEntry]:
        """
        Search across research entries.

        Args:
            query: Search query
            project_id: Optional project filter
            research_types: Optional research type filter
            limit: Maximum results

        Returns:
            List of matching ResearchEntry objects
        """
        type_values = None
        if research_types:
            type_values = [t.value for t in research_types]

        records = await self._client.search(
            query=query,
            project_id=project_id,
            research_types=type_values,
            limit=limit,
        )

        return [ResearchEntry.from_dict(r) for r in records]

    async def get_project_summary(
        self,
        project_id: str,
    ) -> Dict[str, Any]:
        """
        Get a summary of research for a project.

        Args:
            project_id: Project UUID

        Returns:
            Summary with counts by type and status
        """
        entries = await self.list_by_project(project_id, limit=1000)

        by_type = {}
        by_status = {}

        for entry in entries:
            type_key = entry.research_type.value
            status_key = entry.status.value

            by_type[type_key] = by_type.get(type_key, 0) + 1
            by_status[status_key] = by_status.get(status_key, 0) + 1

        return {
            "project_id": project_id,
            "total_entries": len(entries),
            "by_type": by_type,
            "by_status": by_status,
            "latest_entry": entries[0].created_at.isoformat() if entries else None,
        }

    async def pin(self, research_id: str, user_id: str) -> Optional[ResearchEntry]:
        """Pin a research entry."""
        return await self.update(research_id, user_id, {"is_pinned": True})

    async def unpin(self, research_id: str, user_id: str) -> Optional[ResearchEntry]:
        """Unpin a research entry."""
        return await self.update(research_id, user_id, {"is_pinned": False})

    async def add_tags(
        self,
        research_id: str,
        user_id: str,
        tags: List[str],
    ) -> Optional[ResearchEntry]:
        """Add tags to a research entry."""
        entry = await self.get_by_id(research_id)
        if not entry:
            return None

        new_tags = list(set(entry.tags + tags))
        return await self.update(research_id, user_id, {"tags": new_tags})

    async def get_recent(
        self,
        project_id: str,
        limit: int = 10,
    ) -> List[ResearchEntry]:
        """Get most recent research entries."""
        return await self.list_by_project(project_id, limit=limit)

    async def get_by_type(
        self,
        project_id: str,
        research_type: ResearchType,
        limit: int = 50,
    ) -> List[ResearchEntry]:
        """Get research entries of a specific type."""
        return await self.list_by_project(
            project_id,
            research_types=[research_type],
            limit=limit,
        )
