import requests
import json
import os

# Configuration
GCS_MANAGER_URL = "https://gcs-manager-1083011801594.europe-west1.run.app"
BUCKET = "metaadsscrapper"
MANIFEST_PATH = "meta-ads/manifest.json"

def test_health():
    print("Testing /health...")
    response = requests.get(f"{GCS_MANAGER_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_read_manifest():
    print(f"\nTesting /read for {MANIFEST_PATH}...")
    url = f"{GCS_MANAGER_URL}/read?bucket={BUCKET}&name={MANIFEST_PATH}"
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        # gcs-manager wraps content in {name, content}
        content = data.get('content')
        if isinstance(content, str):
            manifest = json.loads(content)
        else:
            manifest = content
        
        ads = manifest.get('ads', [])
        print(f"Found {len(ads)} ads in manifest.")
        
        # Find the first downloaded ad
        downloaded_ads = [a for a in ads if a.get('status') == 'downloaded']
        if downloaded_ads:
            print(f"Found {len(downloaded_ads)} downloaded ads. Testing with the first one.")
            print(json.dumps(downloaded_ads[0], indent=2))
            return downloaded_ads[0]
        
        if ads:
            print("No downloaded ads found. Showing first ad summary:")
            print(json.dumps(ads[0], indent=2))
            return ads[0]
    else:
        print(f"Error: {response.text}")
    return None

def test_raw_stream(ad):
    if not ad:
        print("\nSkipping /raw test (no ad provided)")
        return
    
    # Construct relative path from gcs_path
    # Snapshot: gs://metaadsscrapper/meta-ads/nike/123.mp4
    gcs_path = ad.get('gcs_path', '')
    if not gcs_path:
        print("\nSkipping /raw test (no gcs_path in ad)")
        return
    
    relative_path = gcs_path.replace(f"gs://{BUCKET}/", "")
    print(f"\nTesting /raw for {relative_path}...")
    
    url = f"{GCS_MANAGER_URL}/raw?bucket={BUCKET}&name={relative_path}"
    # Use stream=True to check headers without downloading full content
    response = requests.get(url, stream=True)
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content-Length: {response.headers.get('Content-Length')} bytes")
    
    if response.status_code == 200:
        print("✓ Resource exists and is streamable.")
        # Just check the first 10 bytes to verify it's binary
        chunk = next(response.iter_content(chunk_size=10))
        print(f"First 10 bytes: {chunk.hex()}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    if test_health():
        ad = test_read_manifest()
        test_raw_stream(ad)
    else:
        print("Backend is not reachable.")
