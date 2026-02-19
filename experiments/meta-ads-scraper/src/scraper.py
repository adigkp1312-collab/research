"""Browser automation for Meta Ad Library scraping - FIXED VERSION."""

import re
import time
import random
import json
import hashlib
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page, Browser

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import AD_LIBRARY_URL, DEFAULT_COUNTRY, DOWNLOAD_DELAY
from . import database

console = Console()


class AdLibraryScraper:
    """Scraper for Meta Ad Library - Using video container extraction."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self._playwright = None
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self.stop()
    
    def start(self):
        """Start browser."""
        self._playwright = sync_playwright().start()

        # Browser args for containerized environments (Cloud Run, Docker)
        browser_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--single-process',
        ]

        # User agent to avoid bot detection
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        self.browser = self._playwright.chromium.launch(
            headless=self.headless,
            args=browser_args
        )
        self.context = self.browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1920, "height": 1080}
        )
        self.page = self.context.new_page()
    
    def stop(self):
        """Stop browser."""
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()
    
    def search(self, query: str, country: str = DEFAULT_COUNTRY, limit: int = None) -> List[Dict]:
        """
        Search for ads and collect video ad data.
        
        Args:
            query: Search term (keyword, product, company)
            country: Country code (US, IN, etc.)
            limit: Max number of ads to collect (None = all)
        
        Returns:
            List of ad info dicts with video URLs
        """
        console.print(f"[blue]Searching for:[/blue] {query}")
        console.print(f"[blue]Country:[/blue] {country}")
        
        # Build search URL - filtered for VIDEO ads
        search_url = (
            f"{AD_LIBRARY_URL}?"
            f"active_status=active"
            f"&ad_type=all"
            f"&country={country}"
            f"&media_type=video"
            f"&q={query}"
            f"&search_type=keyword_unordered"
        )
        
        console.print(f"[dim]Navigating to Ad Library...[/dim]")
        # Use load instead of networkidle which can hang indefinitely
        self.page.goto(search_url, wait_until="load", timeout=90000)
        
        # Wait for page to render
        time.sleep(5)
        
        # Accept cookies if prompted
        self._handle_cookie_dialog()
        
        ads = []
        seen_ids = set()
        last_count = 0
        no_new_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Collecting ads...", total=None)
            
            while True:
                # Extract visible ads using new method
                new_ads = self._extract_video_ads(query, country)
                
                for ad in new_ads:
                    if ad['id'] not in seen_ids:
                        seen_ids.add(ad['id'])
                        ads.append(ad)
                        # Add to database
                        database.add_video(
                            ad_id=ad['id'],
                            search_term=query,
                            advertiser_name=ad.get('advertiser'),
                            ad_snapshot_url=ad['snapshot_url'],
                            country=ad['country'],
                            platform=ad['platform'],
                            video_url=ad.get('video_url')
                        )
                
                progress.update(task, description=f"Collected {len(ads)} video ads")
                
                # Check if we've reached limit
                if limit and len(ads) >= limit:
                    console.print(f"[green]Reached limit of {limit} ads[/green]")
                    break
                
                # Check if we're getting new ads
                if len(ads) == last_count:
                    no_new_count += 1
                    if no_new_count >= 3:
                        console.print("[yellow]No more ads found[/yellow]")
                        break
                else:
                    no_new_count = 0
                    last_count = len(ads)
                
                # Scroll to load more
                self._scroll_page()
                # Added randomized delay to look more human
                time.sleep(DOWNLOAD_DELAY + random.uniform(2.0, 5.0))
        
        console.print(f"[green]✓ Collected {len(ads)} video ads[/green]")
        return ads[:limit] if limit else ads
    
    def _handle_cookie_dialog(self):
        """Handle cookie consent dialog if present."""
        try:
            for text in ["Accept All", "Allow All Cookies", "Accept", "Allow all cookies"]:
                button = self.page.locator(f"button:has-text('{text}')").first
                if button.is_visible(timeout=2000):
                    button.click()
                    time.sleep(1)
                    break
        except Exception:
            pass
    
    def _extract_video_ads(self, search_term: str, country: str) -> List[Dict]:
        """
        Extract ad information from video containers.
        Uses multiple strategies to find ads and their metadata.
        """
        ads = []

        # First, extract all ad IDs (collation_ids) from embedded script data
        ad_ids_from_scripts = self._extract_ad_ids_from_scripts()

        # Strategy 1: Use ad containers with data-testid
        ad_containers = self.page.locator('[data-testid="ad-library-dynamic-content-container"]').all()

        for idx, container in enumerate(ad_containers):
            try:
                # Get video in this container
                video = container.locator("video").first
                video_src = ""
                if video.count() > 0:
                    video_src = video.get_attribute("src") or ""
                    if not video_src or "fbcdn" not in video_src:
                        continue
                else:
                    continue

                # Extract advertiser name from the first Facebook page link
                advertiser = "Unknown"
                advertiser_url = ""
                links = container.locator("a[href*='facebook.com/']").all()
                for link in links[:3]:
                    href = link.get_attribute("href") or ""
                    # Skip non-page links (like l.facebook.com redirects)
                    if "l.facebook.com" in href or "/ads/library" in href:
                        continue
                    text = (link.text_content() or "").strip()
                    if text and len(text) > 1 and len(text) < 100:
                        advertiser = text
                        advertiser_url = href
                        break

                # Extract body text
                body_text = ""
                full_text = container.text_content() or ""
                # Remove the advertiser name and common UI text from body
                body_text = full_text.replace(advertiser, "").strip()
                # Clean up common UI elements
                for remove in ["प्रायोजित", "Sponsored", "Shop Now", "Learn More", "See ad details"]:
                    body_text = body_text.replace(remove, "")
                body_text = body_text[:500].strip()

                # Get ad ID - use from scripts if available, otherwise generate hash
                ad_id = hashlib.md5(video_src.encode()).hexdigest()[:16]
                if idx < len(ad_ids_from_scripts):
                    ad_id = ad_ids_from_scripts[idx]

                ads.append({
                    'id': ad_id,
                    'advertiser': advertiser[:100],
                    'advertiser_url': advertiser_url,
                    'body': body_text,
                    'video_url': video_src,
                    'snapshot_url': f"https://www.facebook.com/ads/library/?id={ad_id}",
                    'platform': 'facebook',
                    'search_term': search_term,
                    'country': country
                })

            except Exception as e:
                console.print(f"[dim red]Error extracting ad container: {e}[/dim red]")
                continue

        # Strategy 2: Fallback - extract from video elements directly
        if not ads:
            video_elements = self.page.locator("video").all()

            for idx, video in enumerate(video_elements):
                try:
                    video_src = video.get_attribute("src") or ""
                    if not video_src or "fbcdn" not in video_src:
                        continue

                    # Generate hash-based ID or use from scripts
                    ad_id = hashlib.md5(video_src.encode()).hexdigest()[:16]
                    if idx < len(ad_ids_from_scripts):
                        ad_id = ad_ids_from_scripts[idx]

                    # Try to get advertiser from parent elements
                    advertiser = "Unknown"
                    try:
                        parent_info = video.evaluate('''(el) => {
                            let node = el;
                            for (let i = 0; i < 15; i++) {
                                if (!node.parentElement) break;
                                node = node.parentElement;
                                const links = node.querySelectorAll('a[href*="facebook.com/"]');
                                for (const link of links) {
                                    const href = link.href || "";
                                    if (href.includes("l.facebook.com") || href.includes("/ads/library")) continue;
                                    const text = link.textContent?.trim() || "";
                                    if (text.length > 1 && text.length < 100) {
                                        return {advertiser: text, url: href};
                                    }
                                }
                            }
                            return {advertiser: "Unknown", url: ""};
                        }''')
                        advertiser = parent_info.get('advertiser', 'Unknown')
                    except:
                        pass

                    ads.append({
                        'id': ad_id,
                        'advertiser': advertiser[:100],
                        'body': '',
                        'video_url': video_src,
                        'snapshot_url': f"https://www.facebook.com/ads/library/?id={ad_id}",
                        'platform': 'facebook',
                        'search_term': search_term,
                        'country': country
                    })

                except Exception as e:
                    console.print(f"[dim red]Error extracting video: {e}[/dim red]")
                    continue

        return ads

    def _extract_ad_ids_from_scripts(self) -> List[str]:
        """Extract ad IDs (collation_ids) from embedded script data."""
        ad_ids = []
        try:
            scripts = self.page.locator("script").all()
            for script in scripts:
                content = script.text_content() or ""
                if 'collation_id' in content:
                    # Extract collation_ids which are the actual ad archive IDs
                    ids = re.findall(r'"collation_id":"(\d+)"', content)
                    ad_ids.extend(ids)
            # Remove duplicates while preserving order
            seen = set()
            unique_ids = []
            for id in ad_ids:
                if id not in seen:
                    seen.add(id)
                    unique_ids.append(id)
            return unique_ids
        except Exception as e:
            console.print(f"[dim red]Error extracting IDs from scripts: {e}[/dim red]")
            return []
    
    def _scroll_page(self):
        """Scroll down to load more ads."""
        # Scroll by a larger amount
        self.page.evaluate("window.scrollBy(0, 1500)")

        # Wait for new content to potentially load
        time.sleep(1)

        # Also try clicking "See More" buttons if present
        try:
            see_more_buttons = self.page.locator("button:has-text('See More'), a:has-text('See More')").all()
            for btn in see_more_buttons[:2]:
                if btn.is_visible(timeout=500):
                    btn.click()
                    time.sleep(0.5)
        except Exception:
            pass

        # Try scrolling to the bottom of the page
        try:
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        except Exception:
            pass


def collect_ads(query: str, country: str = DEFAULT_COUNTRY, limit: int = None, headless: bool = True) -> List[Dict]:
    """
    Convenience function to collect ads.
    
    Args:
        query: Search term
        country: Country code
        limit: Max ads to collect
        headless: Run browser in headless mode
    
    Returns:
        List of collected ad info
    """
    with AdLibraryScraper(headless=headless) as scraper:
        return scraper.search(query, country, limit)
