"""Test Meta Ad Library API access (public endpoint)."""

import requests
import json

# Meta's public Ad Library search (no auth needed for basic search)
def test_api_search(query="foot patch", country="IN"):
    # This endpoint sometimes works without auth for read-only
    url = "https://graph.facebook.com/v21.0/ads_archive"
    
    params = {
        "search_terms": query,
        "ad_reached_countries": [country],
        "ad_type": "ALL",
        "media_type": "VIDEO",
        "fields": "id,ad_creative_bodies,ad_snapshot_url,page_name",
        "access_token": "YOUR_TOKEN_HERE",  # We'll try without first
    }
    
    print(f"Testing API for: {query}")
    response = requests.get(url, params=params)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nFound {len(data.get('data', []))} ads")
        return data
    else:
        print("\nAPI requires access token. We need to use browser scraping.")
        return None

if __name__ == "__main__":
    test_api_search()
