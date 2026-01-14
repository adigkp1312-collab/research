"""SQLite database for tracking ads and videos."""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from .config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Videos table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
            search_term TEXT,
            advertiser_name TEXT,
            advertiser_page_url TEXT,
            ad_snapshot_url TEXT,
            video_url TEXT,
            gcs_path TEXT,
            duration_seconds INTEGER,
            file_size_bytes INTEGER,
            country TEXT,
            platform TEXT,
            start_date TEXT,
            end_date TEXT,
            is_active INTEGER DEFAULT 1,
            status TEXT DEFAULT 'pending',
            error_message TEXT,
            created_at TEXT,
            downloaded_at TEXT,
            analysis_status TEXT DEFAULT 'not_analyzed',
            analysis_json TEXT
        )
    """)
    
    # Search sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_term TEXT,
            country TEXT,
            total_ads_found INTEGER DEFAULT 0,
            videos_downloaded INTEGER DEFAULT 0,
            started_at TEXT,
            completed_at TEXT
        )
    """)
    
    # Indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_search ON videos(search_term)")
    
    conn.commit()
    conn.close()


def create_search(search_term: str, country: str) -> int:
    """Create a new search session."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO searches (search_term, country, started_at) VALUES (?, ?, ?)",
        (search_term, country, datetime.now().isoformat())
    )
    search_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return search_id


def add_video(
    ad_id: str,
    search_term: str,
    advertiser_name: str = None,
    ad_snapshot_url: str = None,
    country: str = None,
    platform: str = None,
    video_url: str = None
) -> bool:
    """Add a video to the queue. Returns False if already exists."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO videos (id, search_term, advertiser_name, ad_snapshot_url, 
                              country, platform, video_url, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (ad_id, search_term, advertiser_name, ad_snapshot_url, 
              country, platform, video_url, datetime.now().isoformat()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_pending_videos(limit: int = 100) -> List[Dict[str, Any]]:
    """Get pending videos to download."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM videos WHERE status = 'pending' LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_video_status(
    ad_id: str,
    status: str,
    gcs_path: str = None,
    video_url: str = None,
    file_size_bytes: int = None,
    error_message: str = None
):
    """Update video download status."""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = ["status = ?"]
    values = [status]
    
    if gcs_path:
        updates.append("gcs_path = ?")
        values.append(gcs_path)
    if video_url:
        updates.append("video_url = ?")
        values.append(video_url)
    if file_size_bytes:
        updates.append("file_size_bytes = ?")
        values.append(file_size_bytes)
    if error_message:
        updates.append("error_message = ?")
        values.append(error_message)
    if status == 'downloaded':
        updates.append("downloaded_at = ?")
        values.append(datetime.now().isoformat())
    
    values.append(ad_id)
    
    cursor.execute(
        f"UPDATE videos SET {', '.join(updates)} WHERE id = ?",
        values
    )
    conn.commit()
    conn.close()


def get_stats() -> Dict[str, int]:
    """Get download statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM videos")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM videos WHERE status = 'pending'")
    pending = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM videos WHERE status = 'downloaded'")
    downloaded = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM videos WHERE status = 'failed'")
    failed = cursor.fetchone()[0]
    
    conn.close()
    return {
        "total": total,
        "pending": pending,
        "downloaded": downloaded,
        "failed": failed
    }


def export_data(format: str = 'json') -> List[Dict[str, Any]]:
    """Export all video data."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Initialize database on import
init_database()
