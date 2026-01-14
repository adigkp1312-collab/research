"""Test the scraper with a quick search."""

from src.scraper import collect_ads

print("=" * 60)
print("Testing Meta Ad Library Scraper")
print("=" * 60)

# Test with Nike ads in India
query = "nike"
country = "IN"
limit = 5

print(f"\nSearching for: {query}")
print(f"Country: {country}")
print(f"Limit: {limit} ads\n")

ads = collect_ads(query, country, limit, headless=True)

print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)

if ads:
    print(f"\n✓ Found {len(ads)} ads!\n")
    for i, ad in enumerate(ads, 1):
        print(f"{i}. Ad ID: {ad['id']}")
        print(f"   Advertiser: {ad['advertiser']}")
        print(f"   URL: {ad['snapshot_url']}")
        print()
else:
    print("\n✗ No ads found. The scraper may need additional debugging.\n")

print("=" * 60)
