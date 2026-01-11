"""
Datastore Management API Routes.

Provides endpoints for:
- File upload and management
- Datastore info and statistics
- Search/test functionality

Team: Backend
"""

import os
from typing import Optional, List

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

router = APIRouter()


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class DatastoreInfoResponse(BaseModel):
    """Datastore status and metadata."""
    configured: bool
    datastore_id: Optional[str] = None
    display_name: Optional[str] = None
    project: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None


class FileUploadResponse(BaseModel):
    """Response after file upload."""
    file_id: str
    filename: str
    file_type: str
    size_bytes: int
    status: str
    chunk_count: int
    message: str


class FileMetadataResponse(BaseModel):
    """File metadata."""
    id: str
    filename: str
    file_type: str
    size_bytes: int
    status: str
    chunk_count: int
    character_count: int
    created_at: str
    updated_at: str
    gcs_uri: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = []
    error_message: Optional[str] = None


class FileListResponse(BaseModel):
    """Paginated file list."""
    files: List[FileMetadataResponse]
    total: int
    limit: int
    offset: int


class SearchRequest(BaseModel):
    """Search request."""
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResultItem(BaseModel):
    """Single search result."""
    document_id: str
    content: str
    source: str
    relevance_score: float


class SearchResponse(BaseModel):
    """Search response."""
    query: str
    results: List[SearchResultItem]
    total: int


class StatsResponse(BaseModel):
    """Datastore statistics."""
    total_files: int
    total_size_bytes: int
    total_chunks: int
    by_status: dict
    by_type: dict


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("", response_model=DatastoreInfoResponse)
async def get_datastore_info():
    """
    Get datastore configuration and status.
    
    Returns information about the configured Vertex AI Agent Builder datastore.
    """
    from packages.knowledge_base.src import DatastoreManager
    
    try:
        manager = DatastoreManager()
        info = manager.get_datastore_info()
        return DatastoreInfoResponse(**info)
    except ValueError as e:
        return DatastoreInfoResponse(
            configured=False,
            message=str(e),
        )


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get statistics about uploaded files.
    
    Returns counts by status, file type, and totals.
    """
    from packages.knowledge_base.src import MetadataStore
    
    store = MetadataStore()
    stats = store.get_stats()
    return StatsResponse(**stats)


@router.post("/files", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(..., description="File to upload"),
    description: Optional[str] = Form(None, description="File description"),
    tags: Optional[str] = Form(None, description="Comma-separated tags"),
):
    """
    Upload a file to the knowledge base.
    
    Supported formats: PDF, DOCX, TXT, MD, HTML, CSV, JSON
    
    The file will be:
    1. Validated and text extracted
    2. Uploaded to Google Cloud Storage
    3. Indexed in Vertex AI Agent Builder
    
    Note: Indexing is asynchronous and may take a few minutes.
    """
    from packages.knowledge_base.src import FileProcessor
    
    # Validate file type
    allowed_extensions = {'pdf', 'docx', 'txt', 'md', 'html', 'htm', 'csv', 'json'}
    ext = file.filename.split('.')[-1].lower() if file.filename else ''
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {allowed_extensions}",
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size (max 50MB)
    max_size = 50 * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {max_size // (1024*1024)}MB",
        )
    
    # Parse tags
    tag_list = [t.strip() for t in tags.split(',')] if tags else []
    
    try:
        processor = FileProcessor()
        metadata = processor.process_upload(
            content=content,
            filename=file.filename,
            description=description,
            tags=tag_list,
        )
        
        return FileUploadResponse(
            file_id=metadata.id,
            filename=metadata.filename,
            file_type=metadata.file_type.value,
            size_bytes=metadata.size_bytes,
            status=metadata.status.value,
            chunk_count=metadata.chunk_count,
            message="File uploaded and indexing started",
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files", response_model=FileListResponse)
async def list_files(
    status: Optional[str] = Query(None, description="Filter by status"),
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List uploaded files with optional filtering.
    
    Supports pagination and filtering by status or file type.
    """
    from packages.knowledge_base.src import MetadataStore, FileStatus
    
    store = MetadataStore()
    
    # Convert status string to enum if provided
    status_enum = None
    if status:
        try:
            status_enum = FileStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status: {status}",
            )
    
    files = store.list_all(
        status=status_enum,
        file_type=file_type,
        limit=limit,
        offset=offset,
    )
    
    # Get total count
    all_files = store.list_all(status=status_enum, file_type=file_type, limit=10000)
    
    return FileListResponse(
        files=[
            FileMetadataResponse(
                id=f.id,
                filename=f.filename,
                file_type=f.file_type.value,
                size_bytes=f.size_bytes,
                status=f.status.value,
                chunk_count=f.chunk_count,
                character_count=f.character_count,
                created_at=f.created_at.isoformat(),
                updated_at=f.updated_at.isoformat(),
                gcs_uri=f.gcs_uri,
                description=f.description,
                tags=f.tags,
                error_message=f.error_message,
            )
            for f in files
        ],
        total=len(all_files),
        limit=limit,
        offset=offset,
    )


@router.get("/files/{file_id}", response_model=FileMetadataResponse)
async def get_file(file_id: str):
    """Get metadata for a specific file."""
    from packages.knowledge_base.src import MetadataStore
    
    store = MetadataStore()
    metadata = store.get(file_id)
    
    if not metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileMetadataResponse(
        id=metadata.id,
        filename=metadata.filename,
        file_type=metadata.file_type.value,
        size_bytes=metadata.size_bytes,
        status=metadata.status.value,
        chunk_count=metadata.chunk_count,
        character_count=metadata.character_count,
        created_at=metadata.created_at.isoformat(),
        updated_at=metadata.updated_at.isoformat(),
        gcs_uri=metadata.gcs_uri,
        description=metadata.description,
        tags=metadata.tags,
        error_message=metadata.error_message,
    )


@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """
    Delete a file from the knowledge base.
    
    Note: This removes the metadata. The document may still exist in the datastore
    until the next full reconciliation.
    """
    from packages.knowledge_base.src import MetadataStore
    
    store = MetadataStore()
    deleted = store.delete(file_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {"status": "deleted", "file_id": file_id}


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search the knowledge base.
    
    Performs semantic search over all indexed documents and returns
    the most relevant results.
    """
    from packages.knowledge_base.src import RAGRetriever
    from packages.core.src import GOOGLE_CLOUD_PROJECT
    
    retriever = RAGRetriever()
    
    if not retriever.is_configured:
        raise HTTPException(
            status_code=503,
            detail="Datastore not configured. Set VERTEX_AI_DATASTORE_ID.",
        )
    
    results = retriever.retrieve(request.query, top_k=request.top_k)
    
    return SearchResponse(
        query=request.query,
        results=[
            SearchResultItem(
                document_id=r.document_id,
                content=r.content,
                source=r.source,
                relevance_score=r.relevance_score,
            )
            for r in results
        ],
        total=len(results),
    )
