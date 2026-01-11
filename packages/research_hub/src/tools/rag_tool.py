"""
RAG Tool for Research Hub.

Integrates with the existing knowledge_base package for retrieval-augmented generation.
"""

import os
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path

from ..config import VERTEX_AI_DATASTORE_ID, RAG_ENABLED, RAG_TOP_K


class RAGTool:
    """
    RAG tool for retrieving context from the knowledge base.

    Integrates with the existing knowledge_base package.
    """

    def __init__(
        self,
        datastore_id: str = None,
        top_k: int = None,
    ):
        self.datastore_id = datastore_id or VERTEX_AI_DATASTORE_ID
        self.top_k = top_k or RAG_TOP_K
        self._retriever = None
        self._available = None

    @property
    def is_configured(self) -> bool:
        """Check if RAG is configured."""
        return bool(RAG_ENABLED and self.datastore_id)

    @property
    def is_available(self) -> bool:
        """Check if the knowledge_base package is available."""
        if self._available is None:
            self._available = self._check_knowledge_base_available()
        return self._available

    def _check_knowledge_base_available(self) -> bool:
        """Check if knowledge_base package can be imported."""
        try:
            # Try to import the knowledge_base retriever
            from packages.knowledge_base.src.retriever import RAGRetriever
            return True
        except ImportError:
            return False

    def _get_retriever(self):
        """Get or create the RAG retriever."""
        if self._retriever is None and self.is_available:
            try:
                from packages.knowledge_base.src.retriever import RAGRetriever
                self._retriever = RAGRetriever(datastore_id=self.datastore_id)
            except Exception:
                self._retriever = None
        return self._retriever

    def retrieve(
        self,
        query: str,
        top_k: int = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents from the knowledge base.

        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional filters for the search

        Returns:
            List of search results with content and metadata
        """
        if not self.is_configured:
            return []

        retriever = self._get_retriever()
        if not retriever:
            return []

        k = top_k or self.top_k

        try:
            results = retriever.retrieve(query, top_k=k)

            # Convert to standard format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result.content if hasattr(result, 'content') else str(result),
                    "source": result.source if hasattr(result, 'source') else "",
                    "relevance_score": result.relevance_score if hasattr(result, 'relevance_score') else 0.0,
                    "metadata": result.metadata if hasattr(result, 'metadata') else {},
                })

            return formatted_results

        except Exception as e:
            return [{"error": str(e)}]

    def get_context(
        self,
        query: str,
        top_k: int = None,
        max_length: int = 4000,
    ) -> str:
        """
        Get formatted context for prompt injection.

        Args:
            query: Search query
            top_k: Number of results to use
            max_length: Maximum context length in characters

        Returns:
            Formatted context string
        """
        results = self.retrieve(query, top_k=top_k)

        if not results or (len(results) == 1 and "error" in results[0]):
            return ""

        context_parts = ["## Relevant Knowledge Base Context\n"]
        current_length = len(context_parts[0])

        for i, result in enumerate(results):
            if "error" in result:
                continue

            content = result.get("content", "")
            source = result.get("source", "Unknown")

            section = f"\n### Source {i+1}: {source}\n{content}\n"

            if current_length + len(section) > max_length:
                # Truncate if necessary
                remaining = max_length - current_length - 50
                if remaining > 100:
                    section = f"\n### Source {i+1}: {source}\n{content[:remaining]}...\n"
                    context_parts.append(section)
                break

            context_parts.append(section)
            current_length += len(section)

        return "".join(context_parts)

    def augment_prompt(
        self,
        base_prompt: str,
        query: str,
        top_k: int = None,
    ) -> str:
        """
        Augment a prompt with relevant context from RAG.

        Args:
            base_prompt: The original prompt
            query: Query to search for context
            top_k: Number of results to use

        Returns:
            Augmented prompt with context
        """
        context = self.get_context(query, top_k=top_k)

        if not context:
            return base_prompt

        return f"""
{context}

---

Based on the above knowledge context and your own capabilities:

{base_prompt}
"""

    def check_datastore_status(self) -> Dict[str, Any]:
        """
        Check the status of the RAG datastore.

        Returns:
            Status information
        """
        return {
            "configured": self.is_configured,
            "available": self.is_available,
            "datastore_id": self.datastore_id if self.is_configured else None,
            "top_k": self.top_k,
            "rag_enabled": RAG_ENABLED,
        }


class SimpleRAGTool:
    """
    Simplified RAG tool that works without the knowledge_base package.

    Uses Vertex AI Discovery Engine directly.
    """

    def __init__(
        self,
        datastore_id: str = None,
        project_id: str = None,
        location: str = None,
    ):
        from ..config import GOOGLE_CLOUD_PROJECT, VERTEX_AI_LOCATION

        self.datastore_id = datastore_id or VERTEX_AI_DATASTORE_ID
        self.project_id = project_id or GOOGLE_CLOUD_PROJECT
        self.location = location or VERTEX_AI_LOCATION
        self._client = None

    @property
    def is_configured(self) -> bool:
        """Check if RAG is configured."""
        return bool(RAG_ENABLED and self.datastore_id and self.project_id)

    def _get_client(self):
        """Get or create Discovery Engine client."""
        if self._client is None and self.is_configured:
            try:
                from google.cloud import discoveryengine_v1 as discoveryengine
                self._client = discoveryengine.SearchServiceClient()
            except ImportError:
                self._client = None
        return self._client

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search the datastore.

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            Search results
        """
        if not self.is_configured:
            return []

        client = self._get_client()
        if not client:
            return []

        try:
            from google.cloud import discoveryengine_v1 as discoveryengine

            serving_config = (
                f"projects/{self.project_id}/locations/{self.location}"
                f"/dataStores/{self.datastore_id}/servingConfigs/default_config"
            )

            request = discoveryengine.SearchRequest(
                serving_config=serving_config,
                query=query,
                page_size=top_k,
            )

            response = client.search(request)

            results = []
            for result in response.results:
                doc = result.document
                results.append({
                    "id": doc.id,
                    "content": doc.derived_struct_data.get("snippets", [{}])[0].get("snippet", ""),
                    "source": doc.derived_struct_data.get("link", ""),
                    "title": doc.derived_struct_data.get("title", ""),
                })

            return results

        except Exception as e:
            return [{"error": str(e)}]


# Factory function
def create_rag_tool(
    datastore_id: str = None,
    use_simple: bool = False,
) -> RAGTool:
    """
    Create a RAG tool instance.

    Args:
        datastore_id: Optional datastore ID override
        use_simple: Use SimpleRAGTool instead of integrating with knowledge_base

    Returns:
        RAG tool instance
    """
    if use_simple:
        return SimpleRAGTool(datastore_id=datastore_id)
    return RAGTool(datastore_id=datastore_id)
