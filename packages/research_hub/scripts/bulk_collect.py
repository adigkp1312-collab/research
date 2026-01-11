#!/usr/bin/env python3
"""
Bulk Video Collection Script.

Collects large numbers of video ads across multiple brands and countries.

Usage:
    python bulk_collect.py --project-id my-project --config brands.json
    python bulk_collect.py --project-id my-project --preset sportswear
    python bulk_collect.py --project-id my-project --brands "Nike,Adidas,Puma" --countries "US,GB,DE"
"""

import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.video_downloader import VideoCollectionService

# Preset brand collections
PRESETS = {
    "sportswear": [
        "Nike", "Adidas", "Puma", "Under Armour", "Reebok",
        "New Balance", "ASICS", "Fila", "Converse", "Vans"
    ],
    "tech": [
        "Apple", "Samsung", "Google", "Microsoft", "Sony",
        "Dell", "HP", "Lenovo", "ASUS", "LG"
    ],
    "food_beverage": [
        "Coca Cola", "Pepsi", "McDonald's", "Starbucks", "Red Bull",
        "Nestle", "Burger King", "KFC", "Subway", "Dunkin"
    ],
    "automotive": [
        "Toyota", "BMW", "Mercedes", "Ford", "Tesla",
        "Honda", "Audi", "Volkswagen", "Hyundai", "Chevrolet"
    ],
    "fashion": [
        "Zara", "H&M", "Gucci", "Louis Vuitton", "Nike",
        "Levi's", "Calvin Klein", "Ralph Lauren", "Uniqlo", "GAP"
    ],
    "ecommerce": [
        "Amazon", "eBay", "Shopify", "Alibaba", "Walmart",
        "Target", "Best Buy", "Etsy", "Wayfair", "IKEA"
    ],
}

COUNTRIES = {
    "tier1": ["US", "GB", "CA", "AU", "DE"],
    "tier2": ["FR", "IT", "ES", "NL", "JP"],
    "asia": ["IN", "SG", "MY", "PH", "ID"],
    "all": ["US", "GB", "CA", "AU", "DE", "FR", "IT", "ES", "IN", "BR"],
}


def estimate_collection(brands: list, countries: list, max_per: int) -> dict:
    """Estimate collection size."""
    total_searches = len(brands) * len(countries)
    estimated_videos = total_searches * (max_per * 0.3)  # ~30% are video ads
    estimated_size_gb = estimated_videos * 5 / 1024  # ~5MB average per video
    estimated_time_mins = total_searches * 2  # ~2 min per search

    return {
        "brands": len(brands),
        "countries": len(countries),
        "total_searches": total_searches,
        "estimated_videos": int(estimated_videos),
        "estimated_size_gb": round(estimated_size_gb, 1),
        "estimated_time_mins": estimated_time_mins,
    }


def main():
    parser = argparse.ArgumentParser(description="Bulk collect video ads")
    parser.add_argument("--project-id", required=True, help="Project ID")

    # Brand selection
    brand_group = parser.add_mutually_exclusive_group(required=True)
    brand_group.add_argument("--brands", help="Comma-separated brand names")
    brand_group.add_argument("--preset", choices=list(PRESETS.keys()), help="Use preset brand list")
    brand_group.add_argument("--config", help="JSON config file")

    # Country selection
    parser.add_argument("--countries", default="US", help="Comma-separated countries or preset (tier1, tier2, all)")

    # Options
    parser.add_argument("--max", type=int, default=30, help="Max videos per brand/country (default: 30)")
    parser.add_argument("--no-download", action="store_true", help="Metadata only")
    parser.add_argument("--estimate", action="store_true", help="Show estimate only, don't run")
    parser.add_argument("--output", help="Output results to JSON file")

    args = parser.parse_args()

    # Get brands
    if args.brands:
        brands = [b.strip() for b in args.brands.split(",")]
    elif args.preset:
        brands = PRESETS[args.preset]
    elif args.config:
        with open(args.config) as f:
            config = json.load(f)
            brands = config.get("brands", [])

    # Get countries
    if args.countries in COUNTRIES:
        countries = COUNTRIES[args.countries]
    else:
        countries = [c.strip().upper() for c in args.countries.split(",")]

    # Show estimate
    estimate = estimate_collection(brands, countries, args.max)

    print("=" * 60)
    print("BULK VIDEO COLLECTION")
    print("=" * 60)
    print(f"Project: {args.project_id}")
    print(f"Brands: {len(brands)} - {', '.join(brands[:5])}{'...' if len(brands) > 5 else ''}")
    print(f"Countries: {len(countries)} - {', '.join(countries)}")
    print(f"Max per search: {args.max}")
    print(f"Download: {not args.no_download}")
    print()
    print("ESTIMATE:")
    print(f"  Total searches: {estimate['total_searches']}")
    print(f"  Expected videos: ~{estimate['estimated_videos']}")
    print(f"  Expected size: ~{estimate['estimated_size_gb']} GB")
    print(f"  Expected time: ~{estimate['estimated_time_mins']} minutes")
    print("=" * 60)

    if args.estimate:
        return

    # Confirm
    response = input("\nProceed? [y/N]: ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    # Run collection
    print("\nStarting collection...")

    service = VideoCollectionService()

    all_results = {
        "project_id": args.project_id,
        "started_at": datetime.utcnow().isoformat(),
        "config": {
            "brands": brands,
            "countries": countries,
            "max_per_search": args.max,
        },
        "jobs": [],
        "total_videos": 0,
        "total_downloaded": 0,
    }

    for brand in brands:
        print(f"\n>>> Collecting: {brand}")

        result = service.collect_videos(
            keywords=[brand],
            project_id=args.project_id,
            countries=countries,
            max_per_keyword=args.max,
            download=not args.no_download,
        )

        all_results["jobs"].append({
            "brand": brand,
            "job_id": result["job_id"],
            "videos_found": result["videos_found"],
            "videos_downloaded": result["videos_downloaded"],
        })

        all_results["total_videos"] += result["videos_found"]
        all_results["total_downloaded"] += result["videos_downloaded"]

        print(f"    Found: {result['videos_found']}, Downloaded: {result['videos_downloaded']}")

    all_results["completed_at"] = datetime.utcnow().isoformat()

    # Summary
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"Total videos found: {all_results['total_videos']}")
    print(f"Total downloaded: {all_results['total_downloaded']}")

    # Save results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"Results saved to: {args.output}")


if __name__ == "__main__":
    main()
