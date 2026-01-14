"""Database synchronization with GCS for stateless environments (Cloud Run)."""

import os
from pathlib import Path
from google.cloud import storage
from rich.console import Console

from .config import GCS_BUCKET, GCS_PREFIX, DATABASE_PATH

console = Console()

# The specific path for the database in GCS
GCS_DB_PATH = f"{GCS_PREFIX}/ads.db"

def download_db():
    """Download ads.db from GCS to local data directory."""
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS") and not os.getenv("K_SERVICE"):
        # Skip if not in cloud and no credentials provided
        return False
        
    try:
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(GCS_DB_PATH)
        
        if blob.exists():
            console.print(f"[blue]Cloud Sync:[/blue] Downloading database from gs://{GCS_BUCKET}/{GCS_DB_PATH}")
            DATABASE_PATH.parent.mkdir(exist_ok=True)
            blob.download_to_filename(str(DATABASE_PATH))
            return True
        else:
            console.print(f"[yellow]Cloud Sync:[/yellow] No existing database found in GCS.")
            return False
    except Exception as e:
        console.print(f"[red]Cloud Sync Error (Download):[/red] {e}")
        return False

def upload_db():
    """Upload local ads.db to GCS."""
    if not DATABASE_PATH.exists():
        return False
        
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS") and not os.getenv("K_SERVICE"):
        return False
        
    try:
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(GCS_DB_PATH)
        
        console.print(f"[blue]Cloud Sync:[/blue] Uploading database to gs://{GCS_BUCKET}/{GCS_DB_PATH}")
        blob.upload_from_filename(str(DATABASE_PATH))
        return True
    except Exception as e:
        console.print(f"[red]Cloud Sync Error (Upload):[/red] {e}")
        return False
