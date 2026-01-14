"""Google Cloud Storage operations."""

from pathlib import Path
from typing import Optional
from google.cloud import storage

from .config import GCS_BUCKET, GCS_PROJECT, GCS_PREFIX


_client: Optional[storage.Client] = None
_bucket: Optional[storage.Bucket] = None


def get_client() -> storage.Client:
    """Get or create GCS client."""
    global _client
    if _client is None:
        _client = storage.Client(project=GCS_PROJECT)
    return _client


def get_bucket() -> storage.Bucket:
    """Get or create bucket reference."""
    global _bucket
    if _bucket is None:
        _bucket = get_client().bucket(GCS_BUCKET)
    return _bucket


def upload_video(local_path: Path, search_term: str, ad_id: str) -> str:
    """
    Upload video to GCS.
    
    Returns:
        GCS path (gs://bucket/path)
    """
    # Clean search term for path
    safe_search = search_term.replace(" ", "_").lower()
    gcs_path = f"{GCS_PREFIX}/{safe_search}/{ad_id}.mp4"
    
    bucket = get_bucket()
    blob = bucket.blob(gcs_path)
    
    # Upload with content type
    blob.upload_from_filename(
        str(local_path),
        content_type="video/mp4"
    )
    
    return f"gs://{GCS_BUCKET}/{gcs_path}"


def check_exists(search_term: str, ad_id: str) -> bool:
    """Check if video already exists in GCS."""
    safe_search = search_term.replace(" ", "_").lower()
    gcs_path = f"{GCS_PREFIX}/{safe_search}/{ad_id}.mp4"
    
    bucket = get_bucket()
    blob = bucket.blob(gcs_path)
    
    return blob.exists()


def list_videos(search_term: str = None) -> list:
    """List all videos in bucket, optionally filtered by search term."""
    bucket = get_bucket()
    
    prefix = GCS_PREFIX
    if search_term:
        safe_search = search_term.replace(" ", "_").lower()
        prefix = f"{GCS_PREFIX}/{safe_search}/"
    
    blobs = bucket.list_blobs(prefix=prefix)
    return [f"gs://{GCS_BUCKET}/{blob.name}" for blob in blobs]
