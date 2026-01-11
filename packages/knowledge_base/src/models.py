"""
Data models for the knowledge base system.

Team: AI/ML
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class FileStatus(Enum):
    """File processing status."""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"


class FileType(Enum):
    """Supported file types."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    CSV = "csv"
    JSON = "json"


@dataclass
class FileMetadata:
    """Metadata for an uploaded file."""
    id: str
    filename: str
    file_type: FileType
    size_bytes: int
    
    # Processing info
    status: FileStatus = FileStatus.PENDING
    error_message: Optional[str] = None
    chunk_count: int = 0
    character_count: int = 0
    
    # Storage references
    gcs_uri: Optional[str] = None
    datastore_document_id: Optional[str] = None
    
    # Metadata
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    indexed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "filename": self.filename,
            "file_type": self.file_type.value,
            "size_bytes": self.size_bytes,
            "status": self.status.value,
            "error_message": self.error_message,
            "chunk_count": self.chunk_count,
            "character_count": self.character_count,
            "gcs_uri": self.gcs_uri,
            "datastore_document_id": self.datastore_document_id,
            "description": self.description,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "indexed_at": self.indexed_at.isoformat() if self.indexed_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileMetadata":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            filename=data["filename"],
            file_type=FileType(data["file_type"]),
            size_bytes=data["size_bytes"],
            status=FileStatus(data.get("status", "pending")),
            error_message=data.get("error_message"),
            chunk_count=data.get("chunk_count", 0),
            character_count=data.get("character_count", 0),
            gcs_uri=data.get("gcs_uri"),
            datastore_document_id=data.get("datastore_document_id"),
            description=data.get("description"),
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.utcnow(),
            indexed_at=datetime.fromisoformat(data["indexed_at"]) if data.get("indexed_at") else None,
        )


@dataclass
class SearchResult:
    """A single search result from the datastore."""
    document_id: str
    content: str
    source: str
    relevance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatastoreInfo:
    """Information about a datastore."""
    datastore_id: str
    display_name: str
    project: str
    location: str
    document_count: int = 0
    status: str = "unknown"
    created_at: Optional[datetime] = None
