"""
Ad Search Service.

Reusable search service for both API and internal calls.

Usage:
    # Internal Python call
    from services.search_service import AdSearchService

    service = AdSearchService()
    results = service.search(
        query="Nike",
        country="IN",
        media_type="video",
        active_status="active"
    )

    # Download a video
    video = service.download(results["ads"][0]["video_urls"][0])
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class SearchFilters:
    """Search filter options matching Meta Ad Library UI."""
    language: Optional[str] = None  # "en", "hi", etc.
    advertiser: Optional[str] = None  # Page name filter
    platform: Optional[str] = None  # "facebook", "instagram", "messenger"
    media_type: Optional[str] = None  # "video", "image", "all"
    active_status: str = "active"  # "active", "inactive", "all"
    sort_by: str = "newest"  # "newest", "oldest"


class AdSearchService:
    """
    Unified search service for Meta Ad Library.

    Can be used:
    - Internally via Python calls
    - Via REST API
    - In background jobs
    """

    def __init__(self, firestore_client=None):
        from .ad_library_service import AdLibraryScraper
        from .video_downloader import VideoDownloader

        self.scraper = AdLibraryScraper()
        self.downloader = VideoDownloader()
        self.firestore = firestore_client
        self._init_firestore()

    def _init_firestore(self):
        """Initialize Firestore client."""
        if self.firestore is None:
            try:
                from google.cloud import firestore
                self.firestore = firestore.Client()
            except:
                self.firestore = None

    def search(
        self,
        query: str,
        country: str = "IN",
        limit: int = 30,
        language: Optional[str] = None,
        advertiser: Optional[str] = None,
        platform: Optional[str] = None,
        media_type: Optional[str] = None,
        active_status: str = "active",
        sort_by: str = "newest",
    ) -> Dict[str, Any]:
        """
        Search Meta Ad Library.

        Args:
            query: Search term (brand, keyword)
            country: Country code (default: IN)
            limit: Max results
            language: Filter by language
            advertiser: Filter by page/advertiser name
            platform: Filter by platform (facebook, instagram, messenger)
            media_type: Filter by media type (video, image, all)
            active_status: Filter by status (active, inactive, all)
            sort_by: Sort order (newest, oldest)

        Returns:
            Dict with ads and metadata
        """
        # Determine scraper media type
        scraper_media = "all"
        if media_type == "video":
            scraper_media = "video"
        elif media_type == "image":
            scraper_media = "image"

        # Scrape ads
        result = self.scraper.scrape(
            query=query,
            country=country,
            limit=limit * 2,  # Fetch more, filter later
            media_type=scraper_media,
        )

        if "error" in result:
            return {"error": result["error"], "ads": []}

        ads = result.get("ads", [])

        # Apply filters
        ads = self._apply_filters(
            ads=ads,
            media_type=media_type,
            active_status=active_status,
            platform=platform,
            advertiser=advertiser,
            language=language,
        )

        # Sort
        ads = self._sort_ads(ads, sort_by)

        # Apply limit
        ads = ads[:limit]

        return {
            "query": query,
            "country": country,
            "filters": {
                "language": language,
                "advertiser": advertiser,
                "platform": platform,
                "media_type": media_type,
                "active_status": active_status,
                "sort_by": sort_by,
            },
            "total": len(ads),
            "ads": ads,
            "scraped_at": datetime.utcnow().isoformat(),
        }

    def _apply_filters(
        self,
        ads: List[Dict],
        media_type: Optional[str],
        active_status: str,
        platform: Optional[str],
        advertiser: Optional[str],
        language: Optional[str],
    ) -> List[Dict]:
        """Apply all filters to ads list."""

        # Media type filter
        if media_type == "video":
            ads = [a for a in ads if a.get("has_video") or a.get("video_urls")]
        elif media_type == "image":
            ads = [a for a in ads if not a.get("has_video") and a.get("image_urls")]

        # Active status filter
        if active_status == "active":
            ads = [a for a in ads if a.get("status") == "active"]
        elif active_status == "inactive":
            ads = [a for a in ads if a.get("status") != "active"]

        # Platform filter
        if platform:
            platform_lower = platform.lower()
            ads = [a for a in ads if any(
                platform_lower in p.lower() for p in a.get("platforms", [])
            )]

        # Advertiser filter
        if advertiser:
            advertiser_lower = advertiser.lower()
            ads = [a for a in ads if advertiser_lower in (a.get("page_name") or "").lower()]

        # Language filter (if we have language data)
        if language:
            ads = [a for a in ads if language.lower() in str(a.get("languages", [])).lower()]

        return ads

    def _sort_ads(self, ads: List[Dict], sort_by: str) -> List[Dict]:
        """Sort ads list."""
        if sort_by == "newest":
            return sorted(ads, key=lambda x: x.get("start_date", ""), reverse=True)
        elif sort_by == "oldest":
            return sorted(ads, key=lambda x: x.get("start_date", ""))
        return ads

    def download(
        self,
        video_url: str,
        video_id: Optional[str] = None,
        project_id: str = "default",
        save_to_db: bool = True,
    ) -> Dict[str, Any]:
        """
        Download a video.

        Args:
            video_url: URL of the video
            video_id: Optional ID (generated if not provided)
            project_id: Project to associate with
            save_to_db: Save metadata to Firestore

        Returns:
            Download result with file path
        """
        result = self.downloader.download_video(
            video_url=video_url,
            video_id=video_id,
            project_id=project_id,
        )

        # Save to Firestore
        if save_to_db and self.firestore and result["status"] == "downloaded":
            doc = {
                "id": result["video_id"],
                "project_id": project_id,
                "video_url_original": video_url,
                "stored_url": result.get("stored_url"),
                "local_path": result.get("local_path"),
                "file_size": result.get("file_size"),
                "status": result["status"],
                "created_at": datetime.utcnow(),
            }
            self.firestore.collection("videos").document(result["video_id"]).set(doc)

        return result

    def search_and_download(
        self,
        query: str,
        project_id: str = "default",
        country: str = "IN",
        limit: int = 10,
        **filters,
    ) -> Dict[str, Any]:
        """
        Search and download videos in one call.

        Args:
            query: Search term
            project_id: Project ID
            country: Country code
            limit: Max videos to download
            **filters: Additional search filters

        Returns:
            Dict with search results and download status
        """
        # Search
        search_result = self.search(
            query=query,
            country=country,
            limit=limit,
            media_type="video",
            **filters,
        )

        if "error" in search_result:
            return search_result

        ads = search_result.get("ads", [])
        downloaded = []
        failed = []

        # Download each video
        for ad in ads:
            video_urls = ad.get("video_urls", [])
            if not video_urls:
                continue

            result = self.download(
                video_url=video_urls[0],
                project_id=project_id,
                save_to_db=True,
            )

            if result["status"] == "downloaded":
                downloaded.append({
                    "video_id": result["video_id"],
                    "page_name": ad.get("page_name"),
                    "file_path": result.get("local_path") or result.get("stored_url"),
                })
            else:
                failed.append({
                    "page_name": ad.get("page_name"),
                    "error": result.get("error"),
                })

        return {
            "query": query,
            "country": country,
            "videos_found": len(ads),
            "downloaded": len(downloaded),
            "failed": len(failed),
            "videos": downloaded,
            "errors": failed,
        }

    def get_videos(
        self,
        project_id: str = "default",
        limit: int = 50,
        media_type: Optional[str] = None,
    ) -> List[Dict]:
        """Get downloaded videos from database."""
        if not self.firestore:
            return []

        query = self.firestore.collection("videos").where("project_id", "==", project_id)

        if media_type:
            query = query.where("media_type", "==", media_type)

        docs = query.limit(limit).stream()
        return [doc.to_dict() for doc in docs]

    def get_video(self, video_id: str) -> Optional[Dict]:
        """Get single video by ID."""
        if not self.firestore:
            return None

        doc = self.firestore.collection("videos").document(video_id).get()
        return doc.to_dict() if doc.exists else None

    def delete_video(self, video_id: str) -> bool:
        """Delete video from database and disk."""
        import os

        if not self.firestore:
            return False

        doc = self.firestore.collection("videos").document(video_id).get()
        if not doc.exists:
            return False

        data = doc.to_dict()

        # Delete file
        local_path = data.get("local_path", "").replace("file://", "")
        if local_path and os.path.exists(local_path):
            os.remove(local_path)

        # Delete from Firestore
        self.firestore.collection("videos").document(video_id).delete()

        return True


# Convenience function for quick internal calls
def search_ads(query: str, country: str = "IN", **kwargs) -> Dict[str, Any]:
    """Quick search function for internal use."""
    service = AdSearchService()
    return service.search(query=query, country=country, **kwargs)


def download_video(video_url: str, project_id: str = "default") -> Dict[str, Any]:
    """Quick download function for internal use."""
    service = AdSearchService()
    return service.download(video_url=video_url, project_id=project_id)
