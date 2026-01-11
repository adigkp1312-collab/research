#!/usr/bin/env python3
"""
Scrape and store Meta Ad Library ads.

Usage:
    python store_ads.py "Nike" --project-id my-project
    python store_ads.py "Nike" --project-id my-project --video-only
    python store_ads.py "Nike" --project-id my-project --limit 50
"""

import argparse
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.ad_library_service import AdLibraryService


def main():
    parser = argparse.ArgumentParser(description="Scrape and store Meta Ad Library ads")
    parser.add_argument("query", help="Brand/keyword to search")
    parser.add_argument("--project-id", required=True, help="Project ID to associate ads with")
    parser.add_argument("--country", default="US", help="Country code (default: US)")
    parser.add_argument("--limit", type=int, default=30, help="Max ads to fetch (default: 30)")
    parser.add_argument("--video-only", action="store_true", help="Only fetch video ads")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    media_type = "video" if args.video_only else "all"

    print(f"🔍 Searching Ad Library for '{args.query}'...")
    print(f"   Project: {args.project_id}")
    print(f"   Country: {args.country}")
    print(f"   Limit: {args.limit}")
    print(f"   Type: {media_type}")
    print()

    service = AdLibraryService()

    result = service.search_and_store(
        query=args.query,
        project_id=args.project_id,
        country=args.country,
        limit=args.limit,
        media_type=media_type,
    )

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Total scraped: {result.get('total_scraped', 0)}")
    print(f"Stored in DB:  {result.get('stored', 0)}")
    print(f"Video ads:     {result.get('video_ads', 0)}")
    print(f"Image ads:     {result.get('image_ads', 0)}")
    print(f"Scraped at:    {result.get('scraped_at', 'N/A')}")
    print()

    if result.get('ad_ids'):
        print(f"Stored {len(result['ad_ids'])} ads in Firestore collection 'ad_library'")
        print("Sample IDs:", result['ad_ids'][:5])

    print("=" * 60)


if __name__ == "__main__":
    main()
