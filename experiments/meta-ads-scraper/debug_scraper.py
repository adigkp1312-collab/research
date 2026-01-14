"""Debug script to inspect Meta Ad Library page structure."""

from playwright.sync_api import sync_playwright
import time

def debug_ad_library():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Non-headless to see what's happening
        page = browser.new_page()
        
        # Go to Ad Library
        url = "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=IN&media_type=video&q=foot%20patch&search_type=keyword_unordered"
        print(f"Navigating to: {url}")
        page.goto(url, wait_until="networkidle")
        
        # Wait for page to settle
        time.sleep(5)
        
        # Try to handle cookies
        try:
            accept_btn = page.locator("button:has-text('Accept')").first
            if accept_btn.is_visible(timeout=2000):
                accept_btn.click()
                time.sleep(2)
        except:
            pass
        
        # Save page content for inspection
        html = page.content()
        with open("/Users/guptaaditya/Applications/meta-ad-library-scraper/page_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        # Take screenshot
        page.screenshot(path="/Users/guptaaditya/Applications/meta-ad-library-scraper/page_debug.png")
        
        print("\nPage title:", page.title())
        print("\nLooking for ad elements...")
        
        # Try different selectors
        selectors_to_try = [
            "div[role='article']",
            "div[data-testid]",
            "[class*='x1lliihq']",
            "a[href*='id=']",
            "div[class*='ad']",
        ]
        
        for selector in selectors_to_try:
            elements = page.locator(selector).count()
            print(f"  {selector}: {elements} elements found")
        
        print(f"\nSaved HTML to: page_debug.html")
        print(f"Saved screenshot to: page_debug.png")
        print("\nPress Enter to close browser...")
        input()
        
        browser.close()

if __name__ == "__main__":
    debug_ad_library()
