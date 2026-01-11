"""
Ad Library Service.

Scrapes Meta Ad Library and stores results in Firestore.
Handles both image and video ads.
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode
import hashlib


class AdLibraryScraper:
    """Scrapes Meta Ad Library using Playwright."""

    def __init__(self):
        self.playwright = None
        self.browser = None

    def _get_url(self, query: str, country: str = "US", media_type: str = "all") -> str:
        """Generate Ad Library URL."""
        params = {
            "active_status": "active",
            "ad_type": "all",
            "country": country,
            "q": query,
            "media_type": media_type,  # "all", "image", "video"
        }
        return f"https://www.facebook.com/ads/library/?{urlencode(params)}"

    def scrape(
        self,
        query: str,
        country: str = "US",
        limit: int = 50,
        media_type: str = "all",
    ) -> Dict[str, Any]:
        """
        Scrape ads from Meta Ad Library.

        Args:
            query: Brand/keyword to search
            country: Country code
            limit: Max ads to fetch
            media_type: "all", "image", or "video"

        Returns:
            Dict with ads and metadata
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {"error": "Playwright not installed"}

        url = self._get_url(query, country, media_type)

        with sync_playwright() as p:
            # Use headless=False for better success with Meta's bot detection
            # Set HEADLESS=1 env var to run headless (may have lower success rate)
            import os
            headless = os.environ.get("HEADLESS", "0") == "1"

            browser = p.chromium.launch(
                headless=headless,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"]
            )

            context = browser.new_context(
                viewport={"width": 1400, "height": 900},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            )

            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """)

            page = context.new_page()

            try:
                page.goto(url, wait_until="networkidle", timeout=45000)
                time.sleep(5)

                # Scroll to load more ads (aggressive scrolling for large collections)
                scroll_count = min(limit // 2 + 5, 30)  # More scrolling
                for i in range(scroll_count):
                    page.evaluate("window.scrollBy(0, 1200)")
                    time.sleep(1.5)
                    # Extra wait every 5 scrolls for content to load
                    if i % 5 == 4:
                        time.sleep(2)

                # Extract ads
                ads = page.evaluate("""
                    () => {
                        const results = [];
                        const seen = new Set();
                        const allElements = document.querySelectorAll('*');

                        for (const el of allElements) {
                            const text = el.innerText || '';
                            if (!text.match(/Started running|\\d+ Jan \\d{4}|\\d+ Dec \\d{4}/)) continue;
                            if (text.length < 50 || text.length > 5000) continue;

                            const sig = text.slice(0, 150);
                            if (seen.has(sig)) continue;
                            seen.add(sig);

                            const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);

                            // Page name
                            let pageName = '';
                            const links = el.querySelectorAll('a[href*="/ads/library/"]');
                            for (const link of links) {
                                const lt = link.innerText.trim();
                                if (lt && lt.length > 2 && lt.length < 80 && !lt.includes('See ad details')) {
                                    pageName = lt;
                                    break;
                                }
                            }
                            if (!pageName) {
                                for (const line of lines.slice(0, 5)) {
                                    if (line.length > 2 && line.length < 60 &&
                                        !line.includes('Active') && !line.includes('Started') && !line.match(/^\\d/)) {
                                        pageName = line;
                                        break;
                                    }
                                }
                            }

                            // Date
                            let startDate = '';
                            const dateMatch = text.match(/(\\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \\d{4})/i);
                            if (dateMatch) startDate = dateMatch[1];

                            // Platforms
                            const platforms = [];
                            const tl = text.toLowerCase();
                            if (tl.includes('facebook')) platforms.push('facebook');
                            if (tl.includes('instagram')) platforms.push('instagram');
                            if (tl.includes('messenger')) platforms.push('messenger');

                            // Ad body
                            let body = '';
                            for (const line of lines) {
                                if (line.length > body.length && line.length > 30 &&
                                    !line.includes('Started running') && !line.includes('Active') &&
                                    !line.includes('See ad details')) {
                                    body = line;
                                }
                            }

                            // Check for video
                            const hasVideo = el.querySelector('video') !== null ||
                                           text.toLowerCase().includes('video') ||
                                           el.querySelector('[aria-label*="video"]') !== null;

                            // Snapshot URL
                            let snapshotUrl = '';
                            const allLinks = el.querySelectorAll('a');
                            for (const link of allLinks) {
                                if (link.href && link.href.includes('render_ad')) {
                                    snapshotUrl = link.href;
                                    break;
                                }
                            }

                            // Image URLs
                            const images = [];
                            const imgElements = el.querySelectorAll('img');
                            for (const img of imgElements) {
                                if (img.src && img.src.includes('facebook') && img.width > 100) {
                                    images.push(img.src);
                                }
                            }

                            // Video URLs
                            const videos = [];
                            const videoElements = el.querySelectorAll('video');
                            for (const vid of videoElements) {
                                if (vid.src) videos.push(vid.src);
                                const source = vid.querySelector('source');
                                if (source && source.src) videos.push(source.src);
                            }

                            if (startDate || pageName) {
                                results.push({
                                    page_name: pageName || 'Unknown',
                                    start_date: startDate,
                                    platforms: platforms,
                                    body: body.slice(0, 500),
                                    status: text.includes('Active') ? 'active' : 'inactive',
                                    has_video: hasVideo || videos.length > 0,
                                    snapshot_url: snapshotUrl,
                                    image_urls: images.slice(0, 3),
                                    video_urls: videos.slice(0, 2),
                                });
                            }

                            if (results.length >= 50) break;
                        }

                        return results;
                    }
                """)

                browser.close()

                return {
                    "query": query,
                    "country": country,
                    "media_type": media_type,
                    "url": url,
                    "total": len(ads),
                    "ads": ads[:limit],
                    "scraped_at": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                browser.close()
                return {"error": str(e), "url": url}


class AdLibraryService:
    """
    Service for scraping and storing Meta Ad Library data.
    """

    def __init__(self, firestore_client=None):
        self.scraper = AdLibraryScraper()
        self.firestore = firestore_client
        self._init_firestore()

    def _init_firestore(self):
        """Initialize Firestore client if not provided."""
        if self.firestore is None:
            try:
                from google.cloud import firestore
                self.firestore = firestore.Client()
                print("✓ Connected to Firestore")
            except Exception as e:
                print(f"⚠ Firestore not available ({e}), using local JSON storage")
                self.firestore = None
                self.local_storage_path = "data/ad_library.json"

    def _generate_ad_id(self, ad: Dict) -> str:
        """Generate unique ID for an ad."""
        unique_str = f"{ad.get('page_name', '')}{ad.get('start_date', '')}{ad.get('body', '')[:100]}"
        return hashlib.md5(unique_str.encode()).hexdigest()

    def _store_local(self, doc: Dict):
        """Store ad in local JSON file."""
        import os
        os.makedirs("data", exist_ok=True)

        # Load existing data
        data = []
        if os.path.exists(self.local_storage_path):
            try:
                with open(self.local_storage_path, "r") as f:
                    data = json.load(f)
            except:
                data = []

        # Convert datetime to string
        doc_copy = doc.copy()
        for key in ["created_at", "updated_at"]:
            if key in doc_copy and hasattr(doc_copy[key], "isoformat"):
                doc_copy[key] = doc_copy[key].isoformat()

        # Check if already exists
        existing_ids = {d.get("id") for d in data}
        if doc_copy.get("id") not in existing_ids:
            data.append(doc_copy)

        # Save
        with open(self.local_storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load_local(self) -> List[Dict]:
        """Load ads from local JSON file."""
        import os
        if not os.path.exists(self.local_storage_path):
            return []
        try:
            with open(self.local_storage_path, "r") as f:
                return json.load(f)
        except:
            return []

    def search_and_store(
        self,
        query: str,
        project_id: str,
        country: str = "US",
        limit: int = 50,
        media_type: str = "all",
    ) -> Dict[str, Any]:
        """
        Search Ad Library and store results in Firestore.

        Args:
            query: Search term
            project_id: Project ID to associate ads with
            country: Country code
            limit: Max ads
            media_type: "all", "image", "video"

        Returns:
            Dict with stored ads count and IDs
        """
        # Scrape ads
        result = self.scraper.scrape(
            query=query,
            country=country,
            limit=limit,
            media_type=media_type,
        )

        if "error" in result:
            return result

        ads = result.get("ads", [])
        if not ads:
            return {"stored": 0, "message": "No ads found"}

        # Store in Firestore
        stored_ids = []
        video_ads = []
        image_ads = []

        for ad in ads:
            ad_id = self._generate_ad_id(ad)

            # Prepare document
            doc = {
                "id": ad_id,
                "project_id": project_id,
                "query": query,
                "page_name": ad.get("page_name"),
                "start_date": ad.get("start_date"),
                "platforms": ad.get("platforms", []),
                "body": ad.get("body"),
                "status": ad.get("status"),
                "has_video": ad.get("has_video", False),
                "snapshot_url": ad.get("snapshot_url"),
                "image_urls": ad.get("image_urls", []),
                "video_urls": ad.get("video_urls", []),
                "country": country,
                "media_type": "video" if ad.get("has_video") else "image",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            # Store in Firestore or local JSON
            if self.firestore:
                try:
                    self.firestore.collection("ad_library").document(ad_id).set(doc)
                    stored_ids.append(ad_id)
                except Exception as e:
                    print(f"Failed to store ad {ad_id}: {e}")
            else:
                # Local JSON storage fallback
                stored_ids.append(ad_id)
                self._store_local(doc)

            # Categorize
            if ad.get("has_video"):
                video_ads.append(doc)
            else:
                image_ads.append(doc)

        return {
            "query": query,
            "project_id": project_id,
            "total_scraped": len(ads),
            "stored": len(stored_ids),
            "video_ads": len(video_ads),
            "image_ads": len(image_ads),
            "ad_ids": stored_ids,
            "scraped_at": result.get("scraped_at"),
        }

    def get_ads_by_project(
        self,
        project_id: str,
        media_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Get stored ads for a project."""
        if self.firestore:
            query = self.firestore.collection("ad_library").where("project_id", "==", project_id)

            if media_type:
                query = query.where("media_type", "==", media_type)

            query = query.order_by("created_at", direction="DESCENDING").limit(limit)

            docs = query.stream()
            return [doc.to_dict() for doc in docs]
        else:
            # Local storage fallback
            data = self._load_local()
            results = [d for d in data if d.get("project_id") == project_id]

            if media_type:
                results = [d for d in results if d.get("media_type") == media_type]

            # Sort by created_at descending
            results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return results[:limit]

    def get_video_ads(self, project_id: str, limit: int = 50) -> List[Dict]:
        """Get only video ads for a project."""
        return self.get_ads_by_project(project_id, media_type="video", limit=limit)

    def get_image_ads(self, project_id: str, limit: int = 50) -> List[Dict]:
        """Get only image ads for a project."""
        return self.get_ads_by_project(project_id, media_type="image", limit=limit)

    def search_stored_ads(
        self,
        query: str,
        project_id: Optional[str] = None,
    ) -> List[Dict]:
        """Search stored ads by text."""
        if not self.firestore:
            return []

        # Firestore doesn't support full-text search, so we fetch and filter
        collection = self.firestore.collection("ad_library")

        if project_id:
            docs = collection.where("project_id", "==", project_id).stream()
        else:
            docs = collection.limit(500).stream()

        results = []
        query_lower = query.lower()

        for doc in docs:
            data = doc.to_dict()
            # Search in page_name and body
            if query_lower in (data.get("page_name", "") or "").lower() or \
               query_lower in (data.get("body", "") or "").lower():
                results.append(data)

        return results


# CLI for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ad Library Service")
    parser.add_argument("query", help="Search term")
    parser.add_argument("--project-id", default="test-project", help="Project ID")
    parser.add_argument("--country", default="US", help="Country code")
    parser.add_argument("--limit", type=int, default=20, help="Max ads")
    parser.add_argument("--video-only", action="store_true", help="Only video ads")

    args = parser.parse_args()

    service = AdLibraryService()

    media_type = "video" if args.video_only else "all"

    print(f"Searching for '{args.query}'...")
    result = service.search_and_store(
        query=args.query,
        project_id=args.project_id,
        country=args.country,
        limit=args.limit,
        media_type=media_type,
    )

    print(json.dumps(result, indent=2, default=str))
