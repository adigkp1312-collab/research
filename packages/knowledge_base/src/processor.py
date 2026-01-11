"""
File Processor

Handles file uploads, text extraction, chunking, and ingestion to Vertex AI Datastore.

Team: AI/ML
"""

import os
import uuid
import tempfile
from typing import Optional, List, Dict, Any
from pathlib import Path

from google.cloud import storage

# Import from core package
from packages.core.src import (
    GOOGLE_CLOUD_PROJECT,
    VERTEX_AI_LOCATION,
)
from packages.core.src import (
    GCS_BUCKET_NAME,
    GCS_UPLOAD_PREFIX,
    RAG_CHUNK_SIZE,
    RAG_CHUNK_OVERLAP,
)

# Import new models and managers
from .models import FileMetadata, FileStatus, FileType
from .metadata import MetadataStore
from .datastore import DatastoreManager

# File processing libraries
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import markdown
except ImportError:
    markdown = None


# =============================================================================
# UTILITY FUNCTIONS (Backward Compatible)
# =============================================================================

def extract_text(file_path: str, file_type: str) -> str:
    """
    Extract text from various file formats.
    
    Args:
        file_path: Path to the file
        file_type: File extension (pdf, docx, txt, md, html, etc.)
    
    Returns:
        Extracted text content
    """
    file_type_lower = file_type.lower().lstrip('.')
    
    try:
        if file_type_lower == 'pdf':
            if PyPDF2 is None:
                raise ImportError("PyPDF2 not installed. Install with: pip install pypdf2")
            
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        
        elif file_type_lower == 'docx':
            if Document is None:
                raise ImportError("python-docx not installed. Install with: pip install python-docx")
            
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        
        elif file_type_lower in ['txt', 'text']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif file_type_lower == 'md' or file_type_lower == 'markdown':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Convert markdown to plain text (optional: keep markdown)
                if markdown:
                    html = markdown.markdown(content)
                    if BeautifulSoup:
                        soup = BeautifulSoup(html, 'html.parser')
                        return soup.get_text()
                return content
        
        elif file_type_lower == 'html' or file_type_lower == 'htm':
            if BeautifulSoup is None:
                raise ImportError("beautifulsoup4 not installed. Install with: pip install beautifulsoup4")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                return soup.get_text()
        
        elif file_type_lower == 'csv':
            import csv
            text = ""
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    text += ", ".join(row) + "\n"
            return text
        
        elif file_type_lower == 'json':
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        
        else:
            # Try as plain text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    
    except Exception as e:
        raise ValueError(f"Failed to extract text from {file_type} file: {str(e)}")


def chunk_document(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """
    Split document into chunks with overlap.
    
    Args:
        text: Full text content
        chunk_size: Size of each chunk in characters (default: RAG_CHUNK_SIZE)
        overlap: Overlap between chunks in characters (default: RAG_CHUNK_OVERLAP)
    
    Returns:
        List of text chunks
    """
    chunk_size = chunk_size or RAG_CHUNK_SIZE
    overlap = overlap or RAG_CHUNK_OVERLAP
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings
            for punct in ['. ', '.\n', '! ', '!\n', '? ', '?\n']:
                last_punct = text.rfind(punct, start, end)
                if last_punct != -1:
                    end = last_punct + 2
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap
        if start < 0:
            start = 0
    
    return chunks


# =============================================================================
# FILE PROCESSOR CLASS (New Integrated Implementation)
# =============================================================================

class FileProcessor:
    """
    Processes files for knowledge base ingestion.
    
    Pipeline:
    1. Validate file type
    2. Extract text content
    3. Upload to GCS
    4. Trigger datastore import
    5. Track metadata
    
    Usage:
        processor = FileProcessor()
        result = processor.process_upload(file_content, "document.pdf")
    """
    
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        metadata_store: Optional[MetadataStore] = None,
        datastore_manager: Optional[DatastoreManager] = None,
    ):
        """
        Initialize file processor.
        
        Args:
            bucket_name: GCS bucket name (defaults to env var)
            metadata_store: MetadataStore instance (creates new if None)
            datastore_manager: DatastoreManager instance (creates new if None)
        """
        self.bucket_name = bucket_name or GCS_BUCKET_NAME
        self.metadata_store = metadata_store or MetadataStore()
        self.datastore_manager = datastore_manager or DatastoreManager()
        
        self._storage_client = None
    
    @property
    def storage_client(self) -> storage.Client:
        """Lazy-load storage client."""
        if self._storage_client is None:
            if not GOOGLE_CLOUD_PROJECT:
                raise ValueError("GOOGLE_CLOUD_PROJECT not configured")
            self._storage_client = storage.Client(project=GOOGLE_CLOUD_PROJECT)
        return self._storage_client
    
    def process_upload(
        self,
        content: bytes,
        filename: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> FileMetadata:
        """
        Process an uploaded file through the full pipeline.
        
        Args:
            content: File content as bytes
            filename: Original filename
            description: Optional description
            tags: Optional tags for filtering
        
        Returns:
            FileMetadata with processing status
        
        Raises:
            ValueError: If file type is unsupported
            RuntimeError: If processing fails
        """
        # Generate unique ID
        file_id = str(uuid.uuid4())
        
        # Determine file type
        ext = Path(filename).suffix.lstrip('.').lower()
        try:
            file_type = FileType(ext)
        except ValueError:
            # Try to map common extensions
            ext_mapping = {
                'htm': 'html',
                'text': 'txt',
                'markdown': 'md',
            }
            ext = ext_mapping.get(ext, ext)
            try:
                file_type = FileType(ext)
            except ValueError:
                # Default to text for unknown types
                file_type = FileType.TXT
        
        # Create metadata
        metadata = FileMetadata(
            id=file_id,
            filename=filename,
            file_type=file_type,
            size_bytes=len(content),
            description=description,
            tags=tags or [],
            status=FileStatus.PENDING,
        )
        
        self.metadata_store.save(metadata)
        
        try:
            # Update status to processing
            self.metadata_store.update_status(file_id, FileStatus.PROCESSING)
            
            # Save to temp file for processing
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=f".{ext}",
            ) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            try:
                # Extract text
                text = extract_text(tmp_path, ext)
                metadata.character_count = len(text)
                
                # Chunk document
                chunks = chunk_document(text)
                metadata.chunk_count = len(chunks)
                
                # Update metadata with processing info
                self.metadata_store.save(metadata)
                
                # Upload to GCS
                self.metadata_store.update_status(file_id, FileStatus.UPLOADING)
                gcs_uri = self._upload_to_gcs(tmp_path, file_id, filename)
                metadata.gcs_uri = gcs_uri
                self.metadata_store.save(metadata)
                
                # Trigger datastore import
                self.metadata_store.update_status(file_id, FileStatus.INDEXING)
                import_result = self.datastore_manager.import_documents(gcs_uri)
                
                if import_result.get("status") == "importing":
                    # Import started successfully
                    metadata.status = FileStatus.INDEXED
                    # Note: Actual indexing happens async, but we mark as indexed
                    # since the import operation was accepted
                else:
                    metadata.status = FileStatus.FAILED
                    metadata.error_message = import_result.get("error", "Import failed")
                
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            
            # Save final metadata
            self.metadata_store.save(metadata)
            return metadata
            
        except Exception as e:
            # Update status to failed
            self.metadata_store.update_status(
                file_id,
                FileStatus.FAILED,
                error_message=str(e),
            )
            raise RuntimeError(f"Failed to process file: {str(e)}") from e
    
    def _upload_to_gcs(
        self,
        file_path: str,
        file_id: str,
        filename: str,
    ) -> str:
        """
        Upload file to GCS.
        
        Args:
            file_path: Local file path
            file_id: Unique file identifier
            filename: Original filename
        
        Returns:
            GCS URI (gs://bucket/path)
        """
        if not self.bucket_name:
            raise ValueError("GCS_BUCKET_NAME not configured")
        
        bucket = self.storage_client.bucket(self.bucket_name)
        
        # Create blob name with prefix and file ID
        blob_name = f"{GCS_UPLOAD_PREFIX}/{file_id}/{filename}"
        blob = bucket.blob(blob_name)
        
        # Upload file
        blob.upload_from_filename(file_path)
        
        return f"gs://{self.bucket_name}/{blob_name}"


# =============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS
# =============================================================================

def upload_to_gcs(file_path: str, bucket_name: str = None, blob_name: str = None) -> str:
    """
    Upload file to Google Cloud Storage.
    
    Args:
        file_path: Local file path
        bucket_name: GCS bucket name (defaults to env var)
        blob_name: Name for the blob in GCS (defaults to filename)
    
    Returns:
        GCS URI (gs://bucket/blob)
    """
    bucket_name = bucket_name or GCS_BUCKET_NAME
    if not bucket_name:
        raise ValueError("GCS_BUCKET_NAME not configured")
    
    if not blob_name:
        blob_name = os.path.basename(file_path)
    
    try:
        storage_client = storage.Client(project=GOOGLE_CLOUD_PROJECT)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        blob.upload_from_filename(file_path)
        
        return f"gs://{bucket_name}/{blob_name}"
    
    except Exception as e:
        raise RuntimeError(f"Failed to upload to GCS: {str(e)}")


def ingest_to_datastore(gcs_uri: str, datastore_id: str = None) -> Dict[str, Any]:
    """
    Trigger ingestion of file from GCS to Vertex AI Datastore.
    
    Args:
        gcs_uri: GCS URI (gs://bucket/blob)
        datastore_id: Datastore ID (defaults to env var)
    
    Returns:
        Dictionary with ingestion status
    
    Note:
        This function is kept for backward compatibility.
        Use FileProcessor.process_upload() for new code.
    """
    manager = DatastoreManager(datastore_id=datastore_id)
    return manager.import_documents(gcs_uri)


def process_file(
    file_path: str,
    file_type: str,
    upload_to_storage: bool = True,
    ingest: bool = True,
) -> Dict[str, Any]:
    """
    Complete file processing pipeline: extract, chunk, upload, ingest.
    
    Args:
        file_path: Path to uploaded file
        file_type: File extension
        upload_to_storage: Whether to upload to GCS
        ingest: Whether to ingest to datastore
    
    Returns:
        Dictionary with processing results
    
    Note:
        This function is kept for backward compatibility.
        Use FileProcessor.process_upload() for new code.
    """
    results = {
        "file_path": file_path,
        "file_type": file_type,
        "chunks": [],
        "gcs_uri": None,
        "ingestion_status": None,
    }
    
    try:
        # Extract text
        text = extract_text(file_path, file_type)
        results["text_length"] = len(text)
        
        # Chunk document
        chunks = chunk_document(text)
        results["chunks"] = chunks
        results["num_chunks"] = len(chunks)
        
        # Upload to GCS if requested
        if upload_to_storage:
            gcs_uri = upload_to_gcs(file_path)
            results["gcs_uri"] = gcs_uri
        
        # Ingest to datastore if requested
        if ingest and results["gcs_uri"]:
            ingestion = ingest_to_datastore(results["gcs_uri"])
            results["ingestion_status"] = ingestion
        
        return results
    
    except Exception as e:
        results["error"] = str(e)
        return results
