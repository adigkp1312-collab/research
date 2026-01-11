"""
RAG Retriever using Vertex AI Agent Builder Search.

Provides semantic search over indexed documents and formats
results for chat context injection.

Team: AI/ML
"""

import os
from typing import List, Dict, Any, Optional

from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core import exceptions as google_exceptions

from packages.core.src import GOOGLE_CLOUD_PROJECT

from .models import SearchResult


# Configuration
RAG_TOP_K = int(os.environ.get('RAG_TOP_K', '5'))
DATASTORE_ID = os.environ.get('VERTEX_AI_DATASTORE_ID', '')
DATASTORE_LOCATION = os.environ.get('VERTEX_AI_DATASTORE_LOCATION', 'global')


class RAGRetriever:
    """
    Retrieves relevant context from Vertex AI Agent Builder.
    
    Uses Discovery Engine Search API for semantic search
    over indexed documents.
    
    Usage:
        retriever = RAGRetriever()
        results = retriever.retrieve("How do I process payments?")
        context = retriever.format_context(results)
    """
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        datastore_id: Optional[str] = None,
        location: Optional[str] = None,
    ):
        """
        Initialize RAG retriever.
        
        Args:
            project_id: GCP project ID
            datastore_id: Agent Builder datastore ID
            location: Datastore location (default: global)
        """
        self.project_id = project_id or GOOGLE_CLOUD_PROJECT
        self.datastore_id = datastore_id or DATASTORE_ID
        self.location = location or DATASTORE_LOCATION
        
        self._client = None
    
    @property
    def client(self) -> discoveryengine.SearchServiceClient:
        """Lazy-load search client."""
        if self._client is None:
            self._client = discoveryengine.SearchServiceClient()
        return self._client
    
    @property
    def serving_config(self) -> str:
        """Get serving config path for search."""
        return (
            f"projects/{self.project_id}"
            f"/locations/{self.location}"
            f"/collections/default_collection"
            f"/dataStores/{self.datastore_id}"
            f"/servingConfigs/default_search"
        )
    
    @property
    def is_configured(self) -> bool:
        """Check if retriever is properly configured."""
        return bool(self.project_id and self.datastore_id)
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional filter expression
            
        Returns:
            List of SearchResult objects
        """
        if not self.is_configured:
            return []
        
        top_k = top_k or RAG_TOP_K
        
        # Build search request
        request = discoveryengine.SearchRequest(
            serving_config=self.serving_config,
            query=query,
            page_size=top_k,
            content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                # Enable snippets
                snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                    return_snippet=True,
                    max_snippet_count=3,
                ),
                # Enable extractive answers
                extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                    max_extractive_answer_count=1,
                    max_extractive_segment_count=3,
                ),
                # Enable summary (optional)
                summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                    summary_result_count=3,
                    include_citations=True,
                ),
            ),
            query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
                condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
            ),
            spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
                mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO,
            ),
        )
        
        # Add filter if provided
        if filters:
            request.filter = filters
        
        try:
            response = self.client.search(request)
            
            results = []
            for result in response.results:
                doc = result.document
                
                # Extract content from document
                content = self._extract_content(doc, result)
                source = self._extract_source(doc)
                
                results.append(SearchResult(
                    document_id=doc.id,
                    content=content,
                    source=source,
                    relevance_score=getattr(result, 'relevance_score', 0.0) or 0.0,
                    metadata=self._extract_metadata(doc),
                ))
            
            return results
            
        except google_exceptions.NotFound:
            print(f"Warning: Datastore '{self.datastore_id}' not found")
            return []
        except google_exceptions.PermissionDenied as e:
            print(f"Warning: Permission denied for datastore: {e}")
            return []
        except Exception as e:
            print(f"Warning: RAG retrieval failed: {e}")
            return []
    
    def _extract_content(
        self,
        doc: discoveryengine.Document,
        result: Any,
    ) -> str:
        """Extract relevant content from document."""
        parts = []
        
        # Try extractive segments first (most relevant)
        if hasattr(result, 'document') and hasattr(result.document, 'derived_struct_data'):
            derived = result.document.derived_struct_data
            
            # Extractive segments
            if 'extractive_segments' in derived:
                for segment in derived['extractive_segments']:
                    if 'content' in segment:
                        parts.append(segment['content'])
            
            # Snippets
            if 'snippets' in derived:
                for snippet in derived['snippets']:
                    if 'snippet' in snippet:
                        parts.append(snippet['snippet'])
        
        # Fall back to struct_data content
        if not parts and doc.struct_data:
            if 'content' in doc.struct_data:
                parts.append(str(doc.struct_data['content']))
            elif 'text' in doc.struct_data:
                parts.append(str(doc.struct_data['text']))
        
        # Fall back to document content field
        if not parts and doc.content:
            if doc.content.raw_bytes:
                parts.append(doc.content.raw_bytes.decode('utf-8', errors='ignore')[:2000])
        
        return "\n".join(parts) if parts else ""
    
    def _extract_source(self, doc: discoveryengine.Document) -> str:
        """Extract source information from document."""
        if doc.struct_data:
            for key in ['source', 'filename', 'title', 'url']:
                if key in doc.struct_data:
                    return str(doc.struct_data[key])
        return doc.id or "Unknown"
    
    def _extract_metadata(self, doc: discoveryengine.Document) -> Dict[str, Any]:
        """Extract metadata from document."""
        metadata = {}
        
        if doc.struct_data:
            for key in ['title', 'author', 'date', 'tags', 'category']:
                if key in doc.struct_data:
                    metadata[key] = doc.struct_data[key]
        
        return metadata
    
    def format_context(
        self,
        results: List[SearchResult],
        max_length: int = 4000,
    ) -> str:
        """
        Format search results for prompt injection.
        
        Args:
            results: List of search results
            max_length: Maximum context length in characters
    
    Returns:
        Formatted context string
    """
        if not results:
        return ""
    
        parts = ["## Retrieved Knowledge:\n\n"]
        current_length = len(parts[0])
        
        for i, result in enumerate(results, 1):
            # Build entry
            entry_parts = [
                f"### Source {i}: {result.source}\n",
                f"*Relevance: {result.relevance_score:.2f}*\n\n",
                f"{result.content}\n\n",
            ]
            entry = "".join(entry_parts)
            
            # Check length limit
            if current_length + len(entry) > max_length:
                # Truncate content if needed
                available = max_length - current_length - 100
                if available > 200:
                    truncated = result.content[:available] + "..."
                    entry = f"### Source {i}: {result.source}\n{truncated}\n\n"
                    parts.append(entry)
                break
            
            parts.append(entry)
            current_length += len(entry)
        
        return "".join(parts)


# Convenience function for backward compatibility
def retrieve_context(
    query: str,
    top_k: int = None,
    datastore_id: str = None,
) -> str:
    """
    Retrieve and format context for a query.
    
    Args:
        query: Search query
        top_k: Number of results
        datastore_id: Optional datastore ID override
    
    Returns:
        Formatted context string (empty if not configured)
    """
    retriever = RAGRetriever(datastore_id=datastore_id)
    
    if not retriever.is_configured:
        return ""
    
    results = retriever.retrieve(query, top_k=top_k)
    return retriever.format_context(results)
