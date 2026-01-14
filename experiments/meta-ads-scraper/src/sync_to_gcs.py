#!/usr/bin/env python3
"""
Sync Meta Ads data to GCS bucket.
Exports scraped ads to JSON and uploads to gs://metaadsscrapper/meta-ads/
"""

import json
import os
from datetime import datetime
from pathlib import Path

from google.cloud import storage

# Configuration
GCS_BUCKET = "metaadsscrapper"
GCS_PREFIX = "meta-ads"


def get_client():
    """Get GCS client."""
    return storage.Client()


def export_ads_from_db():
    """Export all ads from SQLite database to list of dicts."""
    import sqlite3
    
    db_path = Path(__file__).parent.parent / "data" / "ads.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM videos ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def sync_to_gcs():
    """Sync all ads data to GCS."""
    print("Exporting ads from database...")
    ads = export_ads_from_db()
    
    if not ads:
        print("No ads to sync!")
        return
    
    print(f"Found {len(ads)} ads to sync")
    
    # Create manifest
    manifest = {
        "version": "1.0",
        "synced_at": datetime.now().isoformat(),
        "total_ads": len(ads),
        "ads": []
    }
    
    # Process each ad
    for ad in ads:
        manifest["ads"].append({
            "id": ad["id"],
            "search_term": ad.get("search_term", ""),
            "advertiser_name": ad.get("advertiser_name", "Unknown"),
            "status": ad.get("status", "pending"),
            "platform": ad.get("platform", "facebook"),
            "country": ad.get("country", "US"),
            "snapshot_url": ad.get("ad_snapshot_url", ""),
            "gcs_path": ad.get("gcs_path", ""),
            "created_at": ad.get("created_at", ""),
            "downloaded_at": ad.get("downloaded_at", "")
        })
    
    # Upload manifest to GCS
    print("Uploading manifest to GCS...")
    client = get_client()
    bucket = client.bucket(GCS_BUCKET)
    
    # Upload main manifest
    manifest_blob = bucket.blob(f"{GCS_PREFIX}/manifest.json")
    manifest_blob.upload_from_string(
        json.dumps(manifest, indent=2),
        content_type="application/json"
    )
    print(f"✓ Uploaded manifest: gs://{GCS_BUCKET}/{GCS_PREFIX}/manifest.json")
    
    # Upload individual ad metadata files by search term
    by_search = {}
    for ad in manifest["ads"]:
        search = ad["search_term"] or "unknown"
        if search not in by_search:
            by_search[search] = []
        by_search[search].append(ad)
    
    for search_term, search_ads in by_search.items():
        safe_search = search_term.replace(" ", "_").lower()
        search_manifest = {
            "search_term": search_term,
            "synced_at": datetime.now().isoformat(),
            "total_ads": len(search_ads),
            "ads": search_ads
        }
        
        blob = bucket.blob(f"{GCS_PREFIX}/{safe_search}/ads.json")
        blob.upload_from_string(
            json.dumps(search_manifest, indent=2),
            content_type="application/json"
        )
        print(f"✓ Uploaded: gs://{GCS_BUCKET}/{GCS_PREFIX}/{safe_search}/ads.json ({len(search_ads)} ads)")
    
    print(f"\n✅ Sync complete! {len(ads)} ads synced to GCS")
    return manifest


if __name__ == "__main__":
    sync_to_gcs()
