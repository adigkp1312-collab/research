#!/usr/bin/env python3
"""
Collect and download video ads from Meta Ad Library.

Usage:
    python collect_videos.py Nike Adidas --project-id my-project
    python collect_videos.py Nike --project-id my-project --countries US,GB,DE --max 50
    python collect_videos.py Nike --project-id my-project --no-download  # Metadata only
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.video_downloader import VideoCollectionService


def main():
    parser = argparse.ArgumentParser(description="Collect video ads from Meta Ad Library")
    parser.add_argument("keywords", nargs="+", help="Keywords/brands to search")
    parser.add_argument("--project-id", required=True, help="Project ID")
    parser.add_argument("--countries", default="US", help="Countries (comma-separated, default: US)")
    parser.add_argument("--max", type=int, default=30, help="Max videos per keyword (default: 30)")
    parser.add_argument("--no-download", action="store_true", help="Skip video download (metadata only)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    countries = [c.strip().upper() for c in args.countries.split(",")]

    print("=" * 60)
    print("VIDEO COLLECTION")
    print("=" * 60)
    print(f"Keywords: {', '.join(args.keywords)}")
    print(f"Countries: {', '.join(countries)}")
    print(f"Max per keyword: {args.max}")
    print(f"Download videos: {not args.no_download}")
    print(f"Project: {args.project_id}")
    print("=" * 60)
    print()

    service = VideoCollectionService()

    def on_progress(progress):
        print(f"Progress: {progress['completed_keywords']}/{progress['total_keywords']} keywords, "
              f"{progress['videos_found']} found, {progress['videos_downloaded']} downloaded")

    result = service.collect_videos(
        keywords=args.keywords,
        project_id=args.project_id,
        countries=countries,
        max_per_keyword=args.max,
        download=not args.no_download,
        on_progress=on_progress,
    )

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Job ID: {result['job_id']}")
        print(f"Videos found: {result['videos_found']}")
        print(f"Downloaded: {result['videos_downloaded']}")
        print(f"Failed: {result['videos_failed']}")
        print()

        if result.get('videos'):
            print("Sample videos:")
            for v in result['videos'][:5]:
                print(f"  - {v.get('page_name', 'Unknown')} ({v.get('status')})")
                if v.get('stored_url'):
                    print(f"    {v['stored_url']}")
                elif v.get('local_path'):
                    print(f"    {v['local_path']}")

        print("=" * 60)


if __name__ == "__main__":
    main()
