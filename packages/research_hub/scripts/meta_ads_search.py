#!/usr/bin/env python3
"""
Raw Meta Ads Library Search.

Usage:
    export META_ACCESS_TOKEN="your_token"
    python meta_ads_search.py "Nike"
    python meta_ads_search.py "Nike" --country US --limit 50
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime


class MetaAdsSearch:
    """Simple Meta Ads Library API client."""

    BASE_URL = "https://graph.facebook.com/v21.0/ads_archive"

    def __init__(self, access_token: str = None):
        self.access_token = access_token or os.environ.get("META_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("META_ACCESS_TOKEN not set")

    def search(
        self,
        search_terms: str,
        country: str = "US",
        limit: int = 25,
        active_only: bool = False,
    ) -> dict:
        """Search for ads."""
        params = {
            "access_token": self.access_token,
            "search_terms": search_terms,
            "ad_reached_countries": [country],
            "ad_active_status": "ACTIVE" if active_only else "ALL",
            "ad_type": "ALL",
            "limit": min(limit, 25),
            "fields": ",".join([
                "id",
                "page_name",
                "page_id",
                "ad_snapshot_url",
                "ad_creative_bodies",
                "ad_creative_link_titles",
                "ad_creative_link_captions",
                "ad_delivery_start_time",
                "ad_delivery_stop_time",
                "publisher_platforms",
                "languages",
            ]),
        }

        response = requests.get(self.BASE_URL, params=params, timeout=30)
        return response.json()

    def search_all(
        self,
        search_terms: str,
        country: str = "US",
        max_ads: int = 100,
        active_only: bool = False,
    ) -> list:
        """Search with automatic pagination."""
        all_ads = []
        after_cursor = None

        while len(all_ads) < max_ads:
            params = {
                "access_token": self.access_token,
                "search_terms": search_terms,
                "ad_reached_countries": [country],
                "ad_active_status": "ACTIVE" if active_only else "ALL",
                "ad_type": "ALL",
                "limit": 25,
                "fields": ",".join([
                    "id",
                    "page_name",
                    "page_id",
                    "ad_snapshot_url",
                    "ad_creative_bodies",
                    "ad_creative_link_titles",
                    "ad_creative_link_captions",
                    "ad_delivery_start_time",
                    "ad_delivery_stop_time",
                    "publisher_platforms",
                ]),
            }

            if after_cursor:
                params["after"] = after_cursor

            response = requests.get(self.BASE_URL, params=params, timeout=30)
            data = response.json()

            if "error" in data:
                print(f"API Error: {data['error']}")
                break

            ads = data.get("data", [])
            if not ads:
                break

            all_ads.extend(ads)

            # Check for next page
            paging = data.get("paging", {})
            after_cursor = paging.get("cursors", {}).get("after")

            if not after_cursor or "next" not in paging:
                break

        return all_ads[:max_ads]


def display_results(ads: list, output_format: str = "table"):
    """Display search results."""

    if output_format == "json":
        print(json.dumps(ads, indent=2))
        return

    # Table format
    print(f"\n{'='*80}")
    print(f"FOUND {len(ads)} ADS")
    print(f"{'='*80}\n")

    # Summary stats
    platforms = {}
    pages = {}
    active_count = 0

    for ad in ads:
        # Count platforms
        for p in ad.get("publisher_platforms", []):
            platforms[p] = platforms.get(p, 0) + 1

        # Count pages
        page = ad.get("page_name", "Unknown")
        pages[page] = pages.get(page, 0) + 1

        # Count active
        if not ad.get("ad_delivery_stop_time"):
            active_count += 1

    print("SUMMARY")
    print("-" * 40)
    print(f"Total ads:  {len(ads)}")
    print(f"Active:     {active_count}")
    print(f"Platforms:  {platforms}")
    print(f"Top pages:  {dict(sorted(pages.items(), key=lambda x: -x[1])[:5])}")

    # Individual ads
    print(f"\n{'='*80}")
    print("AD DETAILS")
    print(f"{'='*80}\n")

    for i, ad in enumerate(ads[:20], 1):  # Show first 20
        print(f"[{i}] {ad.get('page_name', 'Unknown')}")
        print(f"    Started: {ad.get('ad_delivery_start_time', 'N/A')}")
        print(f"    Status:  {'Active' if not ad.get('ad_delivery_stop_time') else 'Ended'}")
        print(f"    Platforms: {', '.join(ad.get('publisher_platforms', []))}")

        # Headlines
        titles = ad.get("ad_creative_link_titles", [])
        if titles:
            print(f"    Headline: {titles[0][:60]}...")

        # Body
        bodies = ad.get("ad_creative_bodies", [])
        if bodies:
            body = bodies[0][:100].replace('\n', ' ')
            print(f"    Body: {body}...")

        # Link
        print(f"    Preview: {ad.get('ad_snapshot_url', 'N/A')}")
        print()

    if len(ads) > 20:
        print(f"... and {len(ads) - 20} more ads")


def main():
    parser = argparse.ArgumentParser(description="Search Meta Ads Library")
    parser.add_argument("query", help="Search term (brand/keyword)")
    parser.add_argument("--country", default="US", help="Country code (default: US)")
    parser.add_argument("--limit", type=int, default=50, help="Max ads to fetch (default: 50)")
    parser.add_argument("--active", action="store_true", help="Only active ads")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Check token
    if not os.environ.get("META_ACCESS_TOKEN"):
        print("ERROR: META_ACCESS_TOKEN environment variable not set")
        print("\nTo get a token:")
        print("1. Go to https://developers.facebook.com/")
        print("2. Create an app with Ad Library API access")
        print("3. Generate an access token")
        print("\nThen run:")
        print('  export META_ACCESS_TOKEN="your_token_here"')
        sys.exit(1)

    print(f"Searching for: {args.query}")
    print(f"Country: {args.country}, Limit: {args.limit}")

    try:
        client = MetaAdsSearch()
        ads = client.search_all(
            search_terms=args.query,
            country=args.country,
            max_ads=args.limit,
            active_only=args.active,
        )

        display_results(ads, "json" if args.json else "table")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
