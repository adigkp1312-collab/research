#!/usr/bin/env python3
"""Test the AdSearchService with India region."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.search_service import AdSearchService, search_ads

def main():
    print("=" * 60)
    print("Testing AdSearchService - India Region")
    print("=" * 60)

    # Test 1: Using the service class
    print("\n1. Testing AdSearchService class...")
    service = AdSearchService()

    results = service.search(
        query="Nike",
        country="IN",
        limit=5,
        media_type="video",
        active_status="active",
    )

    if "error" in results:
        print(f"   Error: {results['error']}")
    else:
        print(f"   Query: {results['query']}")
        print(f"   Country: {results['country']}")
        print(f"   Total ads found: {results['total']}")
        print(f"   Filters applied: {results['filters']}")

        for i, ad in enumerate(results.get('ads', [])[:3]):
            print(f"\n   Ad {i+1}:")
            print(f"     Page: {ad.get('page_name')}")
            print(f"     Date: {ad.get('start_date')}")
            print(f"     Has video: {ad.get('has_video')}")
            print(f"     Video URLs: {len(ad.get('video_urls', []))}")

    # Test 2: Using convenience function
    print("\n" + "=" * 60)
    print("2. Testing search_ads() convenience function...")

    results2 = search_ads("Adidas", country="IN", limit=3, platform="instagram")

    if "error" in results2:
        print(f"   Error: {results2['error']}")
    else:
        print(f"   Found {results2['total']} ads for Adidas on Instagram (IN)")
        for ad in results2.get('ads', [])[:2]:
            print(f"   - {ad.get('page_name')}: {ad.get('start_date')}")

    print("\n" + "=" * 60)
    print("Tests complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
