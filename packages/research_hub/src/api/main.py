"""
Research Hub API - Simple video search and download.

Run:
    uvicorn src.api.main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.ad_library_service import AdLibraryScraper
from services.video_downloader import VideoDownloader, VideoCollectionService
from services.search_service import AdSearchService

app = FastAPI(
    title="Research Hub API",
    description="Search and download video ads from Meta Ad Library",
    version="1.0.0",
)

# CORS for UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
scraper = AdLibraryScraper()
downloader = VideoDownloader()
search_service = AdSearchService()
collection_service = None

def get_collection_service():
    global collection_service
    if collection_service is None:
        collection_service = VideoCollectionService()
    return collection_service


# Request/Response models
class SearchRequest(BaseModel):
    query: str
    country: str = "IN"  # Default to India
    limit: int = 30

    # Filters matching Meta Ad Library UI
    language: Optional[str] = None  # "en", "hi", etc. or None for all
    advertiser: Optional[str] = None  # Specific page name or None for all
    platform: Optional[str] = None  # "facebook", "instagram", "messenger", "audience_network" or None for all
    media_type: Optional[str] = None  # "video", "image", "meme" or None for all
    active_status: str = "active"  # "active", "inactive", "all"

    sort_by: str = "newest"  # newest, oldest


class DownloadRequest(BaseModel):
    video_url: str
    video_id: Optional[str] = None
    project_id: str = "default"


class CollectRequest(BaseModel):
    keywords: List[str]
    project_id: str = "default"
    country: str = "IN"
    max_per_keyword: int = 30
    download: bool = True


# Endpoints
@app.get("/")
def root():
    return {"status": "ok", "service": "Research Hub API"}


@app.post("/api/search")
def search_ads_endpoint(req: SearchRequest):
    """
    Search Meta Ad Library for ads.

    Filters (matching Meta Ad Library UI):
    - language: "en", "hi", etc. or null for all
    - advertiser: Specific page/brand name or null for all
    - platform: "facebook", "instagram", "messenger", "audience_network" or null for all
    - media_type: "video", "image", "meme" or null for all
    - active_status: "active", "inactive", "all"
    - sort_by: "newest" or "oldest"
    """
    result = search_service.search(
        query=req.query,
        country=req.country,
        limit=req.limit,
        language=req.language,
        advertiser=req.advertiser,
        platform=req.platform,
        media_type=req.media_type,
        active_status=req.active_status,
        sort_by=req.sort_by,
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@app.post("/api/download")
def download_video(req: DownloadRequest):
    """
    Download a single video by URL.

    Returns download status and file location.
    """
    result = downloader.download_video(
        video_url=req.video_url,
        video_id=req.video_id,
        project_id=req.project_id,
    )

    if result["status"] == "failed":
        raise HTTPException(status_code=500, detail=result.get("error", "Download failed"))

    return result


@app.post("/api/collect")
def collect_videos(req: CollectRequest, background_tasks: BackgroundTasks):
    """
    Collect and download videos for keywords.

    Runs in background, returns job ID.
    """
    service = get_collection_service()

    # Run in background for large collections
    if len(req.keywords) > 1 or req.max_per_keyword > 20:
        # For now, run synchronously (can add background later)
        pass

    result = service.collect_videos(
        keywords=req.keywords,
        project_id=req.project_id,
        countries=[req.country],
        max_per_keyword=req.max_per_keyword,
        download=req.download,
    )

    return {
        "job_id": result["job_id"],
        "status": "completed",
        "videos_found": result["videos_found"],
        "videos_downloaded": result["videos_downloaded"],
        "videos_failed": result["videos_failed"],
    }


@app.get("/api/videos")
def list_videos(project_id: str = "default", limit: int = 50):
    """
    List downloaded videos from Firestore.
    """
    service = get_collection_service()

    if service.firestore:
        docs = service.firestore.collection("videos").where(
            "project_id", "==", project_id
        ).limit(limit).stream()

        videos = []
        for doc in docs:
            d = doc.to_dict()
            videos.append({
                "id": d.get("id"),
                "page_name": d.get("page_name"),
                "keyword": d.get("keyword"),
                "status": d.get("status"),
                "file_path": d.get("local_path") or d.get("stored_url"),
                "file_size": d.get("file_size"),
                "created_at": str(d.get("created_at")),
            })

        return {"total": len(videos), "videos": videos}

    return {"total": 0, "videos": [], "error": "Firestore not configured"}


@app.get("/api/videos/{video_id}")
def get_video(video_id: str):
    """
    Get video details by ID.
    """
    service = get_collection_service()

    if service.firestore:
        doc = service.firestore.collection("videos").document(video_id).get()
        if doc.exists:
            return doc.to_dict()

    raise HTTPException(status_code=404, detail="Video not found")


@app.delete("/api/videos/{video_id}")
def delete_video(video_id: str):
    """
    Delete a video (from Firestore and disk).
    """
    service = get_collection_service()

    if service.firestore:
        doc = service.firestore.collection("videos").document(video_id).get()
        if doc.exists:
            data = doc.to_dict()

            # Delete file
            local_path = data.get("local_path")
            if local_path and os.path.exists(local_path.replace("file://", "")):
                os.remove(local_path.replace("file://", ""))

            # Delete from Firestore
            service.firestore.collection("videos").document(video_id).delete()

            return {"status": "deleted", "video_id": video_id}

    raise HTTPException(status_code=404, detail="Video not found")


# Health check
@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
