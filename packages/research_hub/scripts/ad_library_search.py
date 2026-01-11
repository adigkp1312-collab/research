#!/usr/bin/env python3
"""
Meta Ad Library Search - Scraper Version.

Searches Facebook Ad Library without API access.

Usage:
    python ad_library_search.py "Nike"
    python ad_library_search.py "Nike" --country US --limit 20
"""

import argparse
import json
import os
import re
import time
from urllib.parse import urlencode, quote
from typing import Dict, Any, List


def get_library_url(query: str, country: str = "US") -> str:
    """Generate Ad Library search URL."""
    params = {
        "active_status": "active",
        "ad_type": "all",
        "country": country,
        "q": query,
        "media_type": "all",
    }
    return f"https://www.facebook.com/ads/library/?{urlencode(params)}"


def search_with_playwright(query: str, country: str = "US", limit: int = 20, debug: bool = False) -> Dict[str, Any]:
    """Search using Playwright with anti-detection measures."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"error": "Run: pip install playwright && python -m playwright install chromium"}

    url = get_library_url(query, country)

    with sync_playwright() as p:
        # Launch with anti-detection flags
        browser = p.chromium.launch(
            headless=False,  # Use visible browser to avoid detection
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )

        context = browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            locale="en-US",
        )

        # Remove webdriver detection
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
        """)

        page = context.new_page()

        try:
            print("Opening Ad Library...")
            page.goto(url, wait_until="networkidle", timeout=45000)

            print("Waiting for ads to load...")
            time.sleep(5)

            # Scroll to load more ads
            scroll_count = min(limit // 3 + 2, 10)  # More scrolls for more ads
            for i in range(scroll_count):
                page.evaluate("window.scrollBy(0, 1000)")
                time.sleep(2)
                print(f"Loading more ads... ({i+1}/{scroll_count})")

            # Take screenshot for debugging
            if debug:
                page.screenshot(path="/tmp/ad_library_debug.png")
                print("Screenshot saved to /tmp/ad_library_debug.png")

            # Extract ads
            print("Extracting ad data...")
            ads = page.evaluate("""
                () => {
                    const results = [];
                    const seen = new Set();

                    // Find all ad cards by looking for elements with "Started running"
                    const allElements = document.querySelectorAll('*');

                    for (const el of allElements) {
                        const text = el.innerText || '';

                        // Must contain date pattern and be reasonable size
                        if (!text.match(/Started running|\\d+ Jan \\d{4}|\\d+ Dec \\d{4}/)) continue;
                        if (text.length < 50 || text.length > 5000) continue;

                        // Skip if we've seen similar content
                        const sig = text.slice(0, 150);
                        if (seen.has(sig)) continue;
                        seen.add(sig);

                        // Parse the text
                        const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);

                        // Find page name - look for link text or first substantial line
                        let pageName = '';
                        const links = el.querySelectorAll('a[href*="/ads/library/"]');
                        for (const link of links) {
                            const linkText = link.innerText.trim();
                            if (linkText && linkText.length > 2 && linkText.length < 80 && !linkText.includes('See ad details')) {
                                pageName = linkText;
                                break;
                            }
                        }

                        // Fallback: first line that looks like a name
                        if (!pageName) {
                            for (const line of lines.slice(0, 5)) {
                                if (line.length > 2 && line.length < 60 &&
                                    !line.includes('Active') &&
                                    !line.includes('Started') &&
                                    !line.includes('platforms') &&
                                    !line.match(/^\\d/)) {
                                    pageName = line;
                                    break;
                                }
                            }
                        }

                        // Find date - more flexible pattern
                        let startDate = '';
                        const dateMatch = text.match(/(\\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \\d{4})/i);
                        if (dateMatch) startDate = dateMatch[1];

                        // Alternative: "Started running on X"
                        const altDateMatch = text.match(/Started running on ([^\\n]+)/);
                        if (!startDate && altDateMatch) startDate = altDateMatch[1].trim();

                        // Find platforms
                        const platforms = [];
                        const textLower = text.toLowerCase();
                        if (textLower.includes('facebook')) platforms.push('Facebook');
                        if (textLower.includes('instagram')) platforms.push('Instagram');
                        if (textLower.includes('messenger')) platforms.push('Messenger');

                        // Find ad body - longest meaningful text
                        let body = '';
                        for (const line of lines) {
                            if (line.length > body.length &&
                                line.length > 30 &&
                                !line.includes('Started running') &&
                                !line.includes('Active') &&
                                !line.includes('See ad details') &&
                                !line.includes('platforms') &&
                                !line.match(/^\\d+ (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)/i)) {
                                body = line;
                            }
                        }

                        // Find snapshot URL
                        let snapshotUrl = '';
                        const allLinks = el.querySelectorAll('a');
                        for (const link of allLinks) {
                            if (link.href && (link.href.includes('render_ad') || link.href.includes('ad_snapshot'))) {
                                snapshotUrl = link.href;
                                break;
                            }
                        }

                        // Status
                        const status = text.includes('Active') ? 'Active' : 'Inactive';

                        // Only add if we have meaningful data
                        if (startDate || pageName) {
                            results.push({
                                page_name: pageName || 'Unknown',
                                start_date: startDate,
                                platforms: platforms,
                                body: body.slice(0, 400),
                                status: status,
                                snapshot_url: snapshotUrl,
                                raw_preview: text.slice(0, 200)
                            });
                        }

                        // Limit results
                        if (results.length >= 50) break;
                    }

                    // Deduplicate by page_name + start_date
                    const unique = [];
                    const keys = new Set();
                    for (const ad of results) {
                        const key = ad.page_name + ad.start_date;
                        if (!keys.has(key)) {
                            keys.add(key);
                            unique.push(ad);
                        }
                    }

                    return unique;
                }
            """)

            # Check for login wall
            page_content = page.content()
            if "Log Into Facebook" in page_content or "Create new account" in page_content:
                browser.close()
                return {
                    "error": "Facebook login wall detected",
                    "url": url,
                    "tip": "Try opening the URL in your browser first, then run this script again",
                }

            # Save screenshot regardless
            page.screenshot(path="/tmp/ad_library_result.png")
            print(f"Found {len(ads)} ads - screenshot saved to /tmp/ad_library_result.png")

            browser.close()

            return {
                "query": query,
                "country": country,
                "url": url,
                "total": len(ads),
                "ads": ads[:limit],
            }

        except Exception as e:
            if debug:
                page.screenshot(path="/tmp/ad_library_error.png")
            browser.close()
            return {"error": str(e), "url": url}


def display_results(result: Dict[str, Any]):
    """Display search results."""
    print("\n" + "=" * 70)
    print("META AD LIBRARY RESULTS")
    print("=" * 70)

    if "error" in result:
        print(f"\n❌ Error: {result['error']}")
        if "tip" in result:
            print(f"   Tip: {result['tip']}")
        if "url" in result:
            print(f"\n   Open manually: {result['url']}")
        return

    print(f"\nQuery: {result['query']}")
    print(f"Country: {result['country']}")
    print(f"Found: {result['total']} ads")
    print(f"\nURL: {result['url']}")

    ads = result.get("ads", [])
    if not ads:
        print("\nNo ads found. Try a different search term.")
        return

    print("\n" + "-" * 70)

    for i, ad in enumerate(ads, 1):
        print(f"\n[{i}] {ad.get('page_name', 'Unknown')}")
        print(f"    Status: {ad.get('status', '?')}")
        print(f"    Started: {ad.get('start_date', 'N/A')}")

        if ad.get('platforms'):
            print(f"    Platforms: {', '.join(ad['platforms'])}")

        if ad.get('body'):
            body = ad['body'][:150].replace('\n', ' ')
            print(f"    Ad text: {body}")

        if ad.get('snapshot_url'):
            print(f"    Preview: {ad['snapshot_url'][:80]}...")

        # Show raw preview for debugging
        if ad.get('raw_preview'):
            raw = ad['raw_preview'][:100].replace('\n', ' | ')
            print(f"    [Raw: {raw}...]")

    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Search Meta Ad Library")
    parser.add_argument("query", help="Brand or keyword to search")
    parser.add_argument("--country", default="US", help="Country code (default: US)")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--debug", action="store_true", help="Save debug screenshots")

    args = parser.parse_args()

    print(f"🔍 Searching Ad Library for '{args.query}'...")

    result = search_with_playwright(
        query=args.query,
        country=args.country,
        limit=args.limit,
        debug=args.debug,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        display_results(result)


if __name__ == "__main__":
    main()
