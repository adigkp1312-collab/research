"""
Knowledge Base Package - Vertex AI Datastore RAG System

Provides RAG capabilities using Vertex AI Agent Builder (Discovery Engine)
for storing and retrieving knowledge from uploaded files.

Team: AI/ML
"""

from .datastore import (
    DatastoreManager,
    init_datastore,
    get_datastore_info,
    list_datastores,
)
from .processor import (
    FileProcessor,
    process_file,
    extract_text,
    chunk_document,
    upload_to_gcs,
    ingest_to_datastore,
)
from .retriever import (
    RAGRetriever,
    retrieve_context,
)
from .metadata import (
    MetadataStore,
)
from .models import (
    FileMetadata,
    FileStatus,
    FileType,
    SearchResult,
    DatastoreInfo,
)

__all__ = [
    # Datastore
    "DatastoreManager",
    "init_datastore",
    "get_datastore_info",
    "list_datastores",
    # Processor
    "FileProcessor",
    "process_file",
    "extract_text",
    "chunk_document",
    "upload_to_gcs",
    "ingest_to_datastore",
    # Retriever
    "RAGRetriever",
    "retrieve_context",
    # Metadata
    "MetadataStore",
    # Models
    "FileMetadata",
    "FileStatus",
    "FileType",
    "SearchResult",
    "DatastoreInfo",
]
