"""
Video Downloader Service.

Downloads video ads and stores them in Google Cloud Storage.
"""

import os
import uuid
import asyncio
import hashlib
import tempfile
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
import requests


class VideoDownloader:
    """Downloads videos from URLs and uploads to Cloud Storage."""

    def __init__(
        self,
        bucket_name: str = None,
        credentials_path: str = None,
        max_concurrent: int = 5,
    ):
        self.bucket_name = bucket_name or os.environ.get("GCS_BUCKET_NAME", "research-hub-videos")
        self.credentials_path = credentials_path or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        self.max_concurrent = max_concurrent
        self.storage_client = None
        self.bucket = None
        self._init_storage()

    def _init_storage(self):
        """Initialize Google Cloud Storage client."""
        try:
            from google.cloud import storage
            self.storage_client = storage.Client()
            # Try to get or create bucket
            try:
                self.bucket = self.storage_client.get_bucket(self.bucket_name)
            except Exception:
                # Bucket doesn't exist, will use local storage
                self.bucket = None
                print(f"⚠ GCS bucket '{self.bucket_name}' not found, using local storage")
        except Exception as e:
            print(f"⚠ Cloud Storage not available: {e}")
            self.storage_client = None
            self.bucket = None

    def download_video(
        self,
        video_url: str,
        video_id: str = None,
        project_id: str = "default",
        metadata: Dict = None,
    ) -> Dict[str, Any]:
        """
        Download a single video.

        Args:
            video_url: URL of the video to download
            video_id: Unique ID (generated if not provided)
            project_id: Project to associate video with
            metadata: Additional metadata to store

        Returns:
            Dict with download result
        """
        video_id = video_id or str(uuid.uuid4())
        result = {
            "video_id": video_id,
            "status": "pending",
            "original_url": video_url,
            "stored_url": None,
            "local_path": None,
            "file_size": 0,
            "error": None,
        }

        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                tmp_path = tmp.name

            # Download video
            print(f"Downloading {video_id}...")
            response = requests.get(video_url, stream=True, timeout=120)
            response.raise_for_status()

            with open(tmp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(tmp_path)
            result["file_size"] = file_size
            print(f"Downloaded {file_size / 1024 / 1024:.1f} MB")

            # Upload to Cloud Storage or save locally
            if self.bucket:
                blob_path = f"videos/{project_id}/{video_id}.mp4"
                blob = self.bucket.blob(blob_path)
                blob.upload_from_filename(tmp_path)
                result["stored_url"] = f"gs://{self.bucket_name}/{blob_path}"
                result["public_url"] = blob.public_url
                os.unlink(tmp_path)  # Clean up temp file
            else:
                # Local storage fallback
                local_dir = f"data/videos/{project_id}"
                os.makedirs(local_dir, exist_ok=True)
                local_path = f"{local_dir}/{video_id}.mp4"
                os.rename(tmp_path, local_path)
                result["local_path"] = local_path
                result["stored_url"] = f"file://{os.path.abspath(local_path)}"

            result["status"] = "downloaded"

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            # Clean up temp file if exists
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)

        return result

    def download_batch(
        self,
        videos: List[Dict],
        project_id: str = "default",
        on_progress: callable = None,
    ) -> Dict[str, Any]:
        """
        Download multiple videos.

        Args:
            videos: List of dicts with 'url' and optional 'id', 'metadata'
            project_id: Project ID
            on_progress: Callback function(completed, total, current_video)

        Returns:
            Dict with batch results
        """
        results = {
            "total": len(videos),
            "downloaded": 0,
            "failed": 0,
            "videos": [],
        }

        for i, video in enumerate(videos):
            url = video.get("url") or video.get("video_url")
            if not url:
                continue

            video_id = video.get("id") or video.get("video_id") or str(uuid.uuid4())

            result = self.download_video(
                video_url=url,
                video_id=video_id,
                project_id=project_id,
                metadata=video.get("metadata"),
            )

            results["videos"].append(result)

            if result["status"] == "downloaded":
                results["downloaded"] += 1
            else:
                results["failed"] += 1

            if on_progress:
                on_progress(i + 1, len(videos), result)

        return results

    async def download_batch_async(
        self,
        videos: List[Dict],
        project_id: str = "default",
    ) -> Dict[str, Any]:
        """Download videos concurrently."""
        loop = asyncio.get_event_loop()

        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            tasks = []
            for video in videos:
                url = video.get("url") or video.get("video_url")
                if not url:
                    continue

                video_id = video.get("id") or str(uuid.uuid4())

                task = loop.run_in_executor(
                    executor,
                    self.download_video,
                    url,
                    video_id,
                    project_id,
                    video.get("metadata"),
                )
                tasks.append(task)

            results_list = await asyncio.gather(*tasks, return_exceptions=True)

        results = {
            "total": len(videos),
            "downloaded": 0,
            "failed": 0,
            "videos": [],
        }

        for r in results_list:
            if isinstance(r, Exception):
                results["failed"] += 1
                results["videos"].append({"status": "failed", "error": str(r)})
            elif r.get("status") == "downloaded":
                results["downloaded"] += 1
                results["videos"].append(r)
            else:
                results["failed"] += 1
                results["videos"].append(r)

        return results


class VideoCollectionService:
    """
    High-level service for collecting and downloading video ads.
    """

    def __init__(self, firestore_client=None):
        from .ad_library_service import AdLibraryScraper
        self.scraper = AdLibraryScraper()
        self.downloader = VideoDownloader()
        self.firestore = firestore_client
        self._init_firestore()

    def _init_firestore(self):
        """Initialize Firestore."""
        if self.firestore is None:
            try:
                from google.cloud import firestore
                self.firestore = firestore.Client()
            except:
                self.firestore = None

    def collect_videos(
        self,
        keywords: List[str],
        project_id: str,
        countries: List[str] = None,
        max_per_keyword: int = 50,
        download: bool = True,
        on_progress: callable = None,
    ) -> Dict[str, Any]:
        """
        Collect video ads for multiple keywords.

        Args:
            keywords: List of search terms
            project_id: Project ID
            countries: List of country codes
            max_per_keyword: Max videos per keyword
            download: Whether to download video files
            on_progress: Progress callback

        Returns:
            Collection results
        """
        countries = countries or ["US"]

        job_id = str(uuid.uuid4())
        job = {
            "id": job_id,
            "project_id": project_id,
            "status": "running",
            "config": {
                "keywords": keywords,
                "countries": countries,
                "max_per_keyword": max_per_keyword,
                "download": download,
            },
            "progress": {
                "total_keywords": len(keywords),
                "completed_keywords": 0,
                "videos_found": 0,
                "videos_downloaded": 0,
                "videos_failed": 0,
            },
            "started_at": datetime.utcnow(),
        }

        # Save job to Firestore
        if self.firestore:
            self.firestore.collection("collection_jobs").document(job_id).set(job)

        all_videos = []

        for i, keyword in enumerate(keywords):
            print(f"\n[{i+1}/{len(keywords)}] Collecting videos for '{keyword}'...")

            for country in countries:
                # Scrape video ads
                result = self.scraper.scrape(
                    query=keyword,
                    country=country,
                    limit=max_per_keyword,
                    media_type="video",
                )

                if "error" in result:
                    print(f"  Error scraping {keyword}/{country}: {result['error']}")
                    continue

                ads = result.get("ads", [])
                video_ads = [a for a in ads if a.get("has_video") and a.get("video_urls")]

                print(f"  Found {len(video_ads)} video ads in {country}")

                for ad in video_ads:
                    video_urls = ad.get("video_urls", [])
                    if not video_urls:
                        continue

                    video_data = {
                        "id": str(uuid.uuid4()),
                        "project_id": project_id,
                        "keyword": keyword,
                        "country": country,
                        "page_name": ad.get("page_name"),
                        "body": ad.get("body"),
                        "start_date": ad.get("start_date"),
                        "platforms": ad.get("platforms", []),
                        "video_url_original": video_urls[0],
                        "status": "pending",
                        "created_at": datetime.utcnow(),
                    }

                    all_videos.append(video_data)
                    job["progress"]["videos_found"] += 1

            job["progress"]["completed_keywords"] += 1

            # Update job progress
            if self.firestore:
                self.firestore.collection("collection_jobs").document(job_id).update(job)

            if on_progress:
                on_progress(job["progress"])

        print(f"\nTotal videos found: {len(all_videos)}")

        # Download videos
        if download and all_videos:
            print(f"\nDownloading {len(all_videos)} videos...")

            for j, video in enumerate(all_videos):
                print(f"[{j+1}/{len(all_videos)}] {video.get('page_name', 'Unknown')}...")

                download_result = self.downloader.download_video(
                    video_url=video["video_url_original"],
                    video_id=video["id"],
                    project_id=project_id,
                )

                video["status"] = download_result["status"]
                video["stored_url"] = download_result.get("stored_url")
                video["local_path"] = download_result.get("local_path")
                video["file_size"] = download_result.get("file_size", 0)
                video["error"] = download_result.get("error")

                if download_result["status"] == "downloaded":
                    job["progress"]["videos_downloaded"] += 1
                else:
                    job["progress"]["videos_failed"] += 1

                # Save video to Firestore
                if self.firestore:
                    self.firestore.collection("videos").document(video["id"]).set(video)

                # Update job
                if self.firestore:
                    self.firestore.collection("collection_jobs").document(job_id).update(job)

        # Complete job
        job["status"] = "completed"
        job["completed_at"] = datetime.utcnow()

        if self.firestore:
            self.firestore.collection("collection_jobs").document(job_id).update(job)

        return {
            "job_id": job_id,
            "status": "completed",
            "videos_found": len(all_videos),
            "videos_downloaded": job["progress"]["videos_downloaded"],
            "videos_failed": job["progress"]["videos_failed"],
            "videos": all_videos,
        }


# CLI
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Collect video ads")
    parser.add_argument("keywords", nargs="+", help="Keywords to search")
    parser.add_argument("--project-id", required=True, help="Project ID")
    parser.add_argument("--countries", default="US", help="Countries (comma-separated)")
    parser.add_argument("--max", type=int, default=20, help="Max videos per keyword")
    parser.add_argument("--no-download", action="store_true", help="Skip downloading")
    parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    countries = [c.strip() for c in args.countries.split(",")]

    service = VideoCollectionService()

    result = service.collect_videos(
        keywords=args.keywords,
        project_id=args.project_id,
        countries=countries,
        max_per_keyword=args.max,
        download=not args.no_download,
    )

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print("\n" + "=" * 60)
        print("COLLECTION COMPLETE")
        print("=" * 60)
        print(f"Job ID: {result['job_id']}")
        print(f"Videos found: {result['videos_found']}")
        print(f"Downloaded: {result['videos_downloaded']}")
        print(f"Failed: {result['videos_failed']}")
