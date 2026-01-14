"""Video download and GCS upload functionality."""

import re
import time
import random
import tempfile
import requests
from pathlib import Path
from typing import Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from playwright.sync_api import sync_playwright, Browser, Page

from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

from .config import MAX_WORKERS, DOWNLOAD_DELAY, TEMP_DIR
from . import database
from . import storage

console = Console()


class VideoDownloader:
    """Downloads videos from Meta Ad Library and uploads to GCS."""
    
    def __init__(self, workers: int = MAX_WORKERS, headless: bool = True):
        self.workers = workers
        self.headless = headless
    
    def download_pending(self, limit: int = None) -> Dict[str, int]:
        """
        Download all pending videos.
        
        Returns:
            Stats dict with success/fail counts
        """
        pending = database.get_pending_videos(limit or 1000)
        
        if not pending:
            console.print("[yellow]No pending videos to download[/yellow]")
            return {"success": 0, "failed": 0}
        
        console.print(f"[blue]Downloading {len(pending)} videos...[/blue]")
        
        success = 0
        failed = 0
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Downloading", total=len(pending))
            
            # Process one at a time to be respectful of rate limits
            for video in pending:
                try:
                    result = self._download_single(video)
                    if result:
                        success += 1
                    else:
                        failed += 1
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                    failed += 1
                
                progress.update(task, advance=1)
                
                # Rate limiting
                time.sleep(DOWNLOAD_DELAY + random.uniform(0, 1))
        
        console.print(f"[green]✓ Downloaded: {success}[/green] | [red]Failed: {failed}[/red]")
        return {"success": success, "failed": failed}
    
    def _download_single(self, video: Dict) -> bool:
        """
        Download a single video.
        
        Args:
            video: Video info dict from database
        
        Returns:
            True if successful
        """
        ad_id = video['id']
        search_term = video['search_term']
        snapshot_url = video['ad_snapshot_url']
        
        console.print(f"[dim]Processing: {ad_id}[/dim]")
        
        try:
            # Check if already exists in GCS
            if storage.check_exists(search_term, ad_id):
                gcs_path = f"gs://{storage.GCS_BUCKET}/{storage.GCS_PREFIX}/{search_term.replace(' ', '_').lower()}/{ad_id}.mp4"
                database.update_video_status(ad_id, 'downloaded', gcs_path=gcs_path)
                console.print(f"[dim]Already exists: {ad_id}[/dim]")
                return True
            
            # Try to get video URL - first from DB, then by extraction
            video_url = video.get('video_url')
            
            if not video_url:
                console.print(f"[dim]Extracting URL for: {ad_id}...[/dim]")
                video_url = self._extract_video_url(snapshot_url or f"https://www.facebook.com/ads/library/?id={ad_id}")
            
            if not video_url:
                database.update_video_status(ad_id, 'failed', error_message="Could not extract video URL")
                return False
            
            # Download to temp file
            temp_path = TEMP_DIR / f"{ad_id}.mp4"
            
            if not self._download_file(video_url, temp_path):
                database.update_video_status(ad_id, 'failed', error_message="Download failed")
                return False
            
            # Upload to GCS
            gcs_path = storage.upload_video(temp_path, search_term, ad_id)
            
            # Update database
            file_size = temp_path.stat().st_size
            database.update_video_status(
                ad_id, 
                'downloaded',
                gcs_path=gcs_path,
                video_url=video_url,
                file_size_bytes=file_size
            )
            
            # Cleanup temp file
            temp_path.unlink()
            
            console.print(f"[green]✓ {ad_id} → {gcs_path}[/green]")
            return True
            
        except Exception as e:
            database.update_video_status(ad_id, 'failed', error_message=str(e))
            console.print(f"[red]✗ {ad_id}: {e}[/red]")
            return False
    
    def _extract_video_url(self, snapshot_url: str) -> Optional[str]:
        """
        Extract direct video URL from ad preview page.
        
        Uses Playwright to render the page and find video source.
        """
        with sync_playwright() as p:
            # Browser args for containerized environments
            browser_args = [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--single-process',
            ]
            browser = p.chromium.launch(headless=self.headless, args=browser_args)
            page = browser.new_page()
            
            try:
                page.goto(snapshot_url, wait_until="networkidle", timeout=30000)
                time.sleep(3)
                
                # Try to find video element
                video_url = None
                
                # Method 1: Look for video elements
                videos = page.locator("video").all()
                for video in videos:
                    src = video.get_attribute("src")
                    if src and "blob:" not in src:
                        video_url = src
                        break
                    
                    # Check source children
                    sources = video.locator("source").all()
                    for source in sources:
                        src = source.get_attribute("src")
                        if src and "blob:" not in src:
                            video_url = src
                            break
                
                # Method 2: Look in network requests (check page content for video URLs)
                if not video_url:
                    content = page.content()
                    
                    # Look for video URLs in page content
                    patterns = [
                        r'(https://video[^"\']+\.mp4[^"\']*)',
                        r'(https://scontent[^"\']+video[^"\']*)',
                        r'"playable_url":"([^"]+)"',
                        r'"sd_src":"([^"]+)"',
                        r'"hd_src":"([^"]+)"',
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            video_url = matches[0].replace("\\u0025", "%").replace("\\/", "/")
                            break
                
                return video_url
                
            except Exception as e:
                console.print(f"[red]Error extracting video: {e}[/red]")
                return None
            finally:
                browser.close()
    
    def _download_file(self, url: str, dest: Path) -> bool:
        """Download file from URL to destination."""
        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(dest, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            console.print(f"[red]Download error: {e}[/red]")
            return False


def download_videos(workers: int = MAX_WORKERS, limit: int = None, headless: bool = True) -> Dict[str, int]:
    """
    Convenience function to download pending videos.
    
    Args:
        workers: Number of parallel workers
        limit: Max videos to download
        headless: Run browser in headless mode
    
    Returns:
        Stats dict
    """
    downloader = VideoDownloader(workers=workers, headless=headless)
    return downloader.download_pending(limit)
