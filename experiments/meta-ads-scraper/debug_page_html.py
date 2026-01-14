"""Debug script to save page HTML and find correct selector."""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Navigate to search
    url = "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=IN&media_type=video&q=nike&search_type=keyword_unordered"
    print(f"Loading: {url}")
    page.goto(url, wait_until="networkidle")
    
    # Wait for content
    time.sleep(5)
    
    # Try to accept cookies
    try:
        accept = page.locator("button:has-text('Accept')").first
        if accept.is_visible(timeout=2000):
            accept.click()
            time.sleep(2)
    except:
        pass
    
    # Count various selectors
    print("\nChecking selectors:")
    print(f"  Spans with 'Library ID:': {page.locator(\"span:has-text('Library ID:')\").count()}")
    print(f"  Text containing '2073772573398602': {page.locator('text=2073772573398602').count()}")
    print(f"  All spans: {page.locator('span').count()}")
    
    # Save HTML
    html = page.content()
    with open("/Users/guptaaditya/Applications/meta-ad-library-scraper/page_source.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"\nSaved HTML to page_source.html ({len(html)} chars)")
    
    # Search for Library ID in the HTML
    if "Library ID:" in html:
        print("✓ Found 'Library ID:' in HTML")
        # Count how many times it appears
        count = html.count("Library ID:")
        print(f"  Appears {count} times")
    else:
        print("✗ 'Library ID:' NOT found in HTML")
    
    browser.close()
