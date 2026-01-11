#!/usr/bin/env python3
"""
Test script for Meta Ads Library search.

Usage:
    export META_ACCESS_TOKEN="your_token"
    python scripts/test_meta_ads.py "Nike"
"""

import sys
import json
import os

# Add parent to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tools.meta_ads_tool import MetaAdsLibraryTool


def main():
    # Get search term from command line or use default
    search_term = sys.argv[1] if len(sys.argv) > 1 else "Nike"

    # Initialize tool
    tool = MetaAdsLibraryTool()

    # Check configuration
    print("=" * 60)
    print("META ADS LIBRARY TEST")
    print("=" * 60)
    print(f"Configured: {tool.is_configured}")

    if not tool.is_configured:
        print("\n❌ ERROR: Meta API not configured!")
        print("\nSet one of these environment variables:")
        print("  export META_ACCESS_TOKEN='your_token'")
        print("  OR")
        print("  export META_APP_ID='your_app_id'")
        print("  export META_APP_SECRET='your_app_secret'")
        return

    print(f"Search term: {search_term}")
    print("-" * 60)

    # Test 1: Basic search (single page, 25 ads max)
    print("\n📍 Test 1: Basic Search (25 ads)")
    result = tool.search_ads(
        search_terms=search_term,
        countries=["US"],
        ad_active_status="ACTIVE",
        limit=10,
    )

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        if "details" in result:
            print(f"   Details: {json.dumps(result['details'], indent=2)}")
        return

    print(f"✅ Found {result['count']} ads")
    print(f"   Has more pages: {result['has_more']}")

    # Show sample ads
    for i, ad in enumerate(result.get("ads", [])[:3]):
        print(f"\n   Ad {i+1}:")
        print(f"   - Page: {ad.get('page_name', 'N/A')}")
        print(f"   - Started: {ad.get('ad_delivery_start_time', 'N/A')}")
        print(f"   - Platforms: {ad.get('publisher_platforms', [])}")
        bodies = ad.get('ad_creative_bodies', [])
        if bodies:
            print(f"   - Body: {bodies[0][:100]}...")

    # Test 2: Paginated search (up to 50 ads)
    print("\n" + "-" * 60)
    print("\n📍 Test 2: Paginated Search (up to 50 ads)")

    result_all = tool.search_ads_all(
        search_terms=search_term,
        countries=["US"],
        ad_active_status="ACTIVE",
        max_ads=50,
    )

    if "error" in result_all:
        print(f"❌ Error: {result_all['error']}")
        return

    print(f"✅ Fetched {result_all['count']} ads total")

    # Analyze platforms
    platforms = {}
    for ad in result_all.get("ads", []):
        for platform in ad.get("publisher_platforms", []):
            platforms[platform] = platforms.get(platform, 0) + 1

    print(f"   Platform distribution: {platforms}")

    # Test 3: Competitor analysis
    print("\n" + "-" * 60)
    print("\n📍 Test 3: Competitor Analysis")

    competitor = tool.search_competitor_ads(
        competitor_name=search_term,
        countries=["US"],
        max_ads=50,
    )

    if "error" in competitor:
        print(f"❌ Error: {competitor['error']}")
        return

    print(f"✅ Competitor: {competitor['competitor']}")
    print(f"   Total ads: {competitor['total_ads_found']}")
    print(f"   Active ads: {competitor['active_ads']}")
    print(f"   Platforms: {competitor['platforms']}")

    if competitor.get("messaging_themes"):
        print(f"\n   Sample messaging themes:")
        for theme in competitor["messaging_themes"][:3]:
            print(f"   - {theme[:80]}...")

    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
