"""
File metadata storage and tracking.

MVP: JSON file storage
Production: Migrate to Firestore

Team: AI/ML
"""

import os
import json
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from .models import FileMetadata, FileStatus


class MetadataStore:
    """
    Thread-safe file metadata storage.
    
    MVP Implementation: JSON file
    Production: Replace with Firestore client
    
    Usage:
        store = MetadataStore()
        store.save(file_metadata)
        files = store.list_all(status=FileStatus.INDEXED)
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize metadata store.
        
        Args:
            storage_path: Path to JSON storage file.
                         Defaults to ~/.knowledge_base/metadata.json
        """
        if storage_path is None:
            storage_dir = Path.home() / ".knowledge_base"
            storage_dir.mkdir(exist_ok=True)
            storage_path = str(storage_dir / "metadata.json")
        
        self.storage_path = storage_path
        self._lock = threading.RLock()
        self._cache: Dict[str, FileMetadata] = {}
        self._load()
    
    def _load(self) -> None:
        """Load metadata from storage."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._cache = {
                        k: FileMetadata.from_dict(v)
                        for k, v in data.items()
                    }
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Failed to load metadata: {e}")
                self._cache = {}
    
    def _persist(self) -> None:
        """Persist metadata to storage."""
        data = {k: v.to_dict() for k, v in self._cache.items()}
        
        # Write atomically
        tmp_path = f"{self.storage_path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, self.storage_path)
    
    def save(self, metadata: FileMetadata) -> None:
        """
        Save or update file metadata.
        
        Args:
            metadata: FileMetadata instance to save
        """
        with self._lock:
            metadata.updated_at = datetime.utcnow()
            self._cache[metadata.id] = metadata
            self._persist()
    
    def get(self, file_id: str) -> Optional[FileMetadata]:
        """
        Get metadata by file ID.
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            FileMetadata if found, None otherwise
        """
        with self._lock:
            return self._cache.get(file_id)
    
    def list_all(
        self,
        status: Optional[FileStatus] = None,
        file_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[FileMetadata]:
        """
        List files with optional filtering.
        
        Args:
            status: Filter by status
            file_type: Filter by file type
            limit: Maximum results
            offset: Skip first N results
            
        Returns:
            List of FileMetadata sorted by created_at (newest first)
        """
        with self._lock:
            items = list(self._cache.values())
        
        # Apply filters
        if status:
            items = [m for m in items if m.status == status]
        if file_type:
            items = [m for m in items if m.file_type.value == file_type]
        
        # Sort by creation date (newest first)
        items.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        return items[offset:offset + limit]
    
    def delete(self, file_id: str) -> bool:
        """
        Delete file metadata.
        
        Args:
            file_id: File to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if file_id in self._cache:
                del self._cache[file_id]
                self._persist()
                return True
            return False
    
    def update_status(
        self,
        file_id: str,
        status: FileStatus,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Update file processing status.
        
        Args:
            file_id: File to update
            status: New status
            error_message: Error message if failed
            
        Returns:
            True if updated, False if not found
        """
        with self._lock:
            if file_id in self._cache:
                self._cache[file_id].status = status
                self._cache[file_id].error_message = error_message
                self._cache[file_id].updated_at = datetime.utcnow()
                
                if status == FileStatus.INDEXED:
                    self._cache[file_id].indexed_at = datetime.utcnow()
                
                self._persist()
                return True
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored files."""
        with self._lock:
            items = list(self._cache.values())
        
        by_status = {}
        by_type = {}
        total_size = 0
        total_chunks = 0
        
        for item in items:
            status = item.status.value
            by_status[status] = by_status.get(status, 0) + 1
            
            file_type = item.file_type.value
            by_type[file_type] = by_type.get(file_type, 0) + 1
            
            total_size += item.size_bytes
            total_chunks += item.chunk_count
        
        return {
            "total_files": len(items),
            "total_size_bytes": total_size,
            "total_chunks": total_chunks,
            "by_status": by_status,
            "by_type": by_type,
        }
