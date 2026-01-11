# Video Collection System - Technical Plan

## Overview

System for collecting, downloading, and storing large numbers of video ads from Meta Ad Library.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              UI (Next.js)                                │
│  - Search interface                                                      │
│  - Video gallery                                                         │
│  - Download queue status                                                 │
│  - Analytics dashboard                                                   │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │ REST API
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend                                  │
│  POST /api/v1/videos/collect     - Start collection job                 │
│  GET  /api/v1/videos             - List videos                          │
│  GET  /api/v1/videos/{id}        - Get video details                    │
│  GET  /api/v1/jobs               - List collection jobs                 │
│  GET  /api/v1/jobs/{id}/status   - Job status                          │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Ad Library   │    │    Video      │    │    Cloud      │
│   Scraper     │    │  Downloader   │    │   Storage     │
│               │    │               │    │               │
│ - Playwright  │    │ - yt-dlp      │    │ - GCS Bucket  │
│ - Multi-keyword│   │ - ffmpeg      │    │ - CDN URLs    │
│ - Multi-country│   │ - Batch queue │    │               │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    ┌───────────────┐
                    │   Firestore   │
                    │               │
                    │ - Video meta  │
                    │ - Job status  │
                    │ - Analytics   │
                    └───────────────┘
```

---

## Data Models

### Video Document (Firestore: `videos`)

```json
{
  "id": "uuid",
  "project_id": "string",
  "source": "meta_ad_library",

  "page_name": "Nike",
  "ad_body": "Ad text content...",
  "platforms": ["facebook", "instagram"],
  "start_date": "2026-01-10",
  "country": "US",

  "video_url_original": "https://video.facebook.com/...",
  "video_url_stored": "gs://bucket/videos/uuid.mp4",
  "video_url_cdn": "https://cdn.example.com/videos/uuid.mp4",

  "thumbnail_url": "gs://bucket/thumbnails/uuid.jpg",
  "duration_seconds": 30,
  "resolution": "1080x1920",
  "file_size_bytes": 5242880,

  "status": "downloaded",  // pending, downloading, downloaded, failed
  "download_attempts": 1,
  "error_message": null,

  "tags": ["sports", "shoes"],
  "ai_analysis": {
    "transcript": "...",
    "detected_objects": [],
    "sentiment": "positive"
  },

  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Collection Job (Firestore: `collection_jobs`)

```json
{
  "id": "uuid",
  "project_id": "string",
  "status": "running",  // pending, running, completed, failed

  "config": {
    "keywords": ["Nike", "Nike Running"],
    "countries": ["US", "GB"],
    "max_videos_per_keyword": 50,
    "video_only": true
  },

  "progress": {
    "total_keywords": 2,
    "completed_keywords": 1,
    "videos_found": 45,
    "videos_downloaded": 30,
    "videos_failed": 2
  },

  "created_at": "timestamp",
  "started_at": "timestamp",
  "completed_at": null
}
```

---

## API Endpoints

### Start Video Collection

```
POST /api/v1/videos/collect
```

Request:
```json
{
  "project_id": "my-project",
  "keywords": ["Nike", "Adidas", "Puma"],
  "countries": ["US", "GB", "DE"],
  "max_per_keyword": 50,
  "download_videos": true
}
```

Response:
```json
{
  "job_id": "abc123",
  "status": "started",
  "estimated_videos": 450
}
```

### List Videos

```
GET /api/v1/videos?project_id=xxx&page=1&limit=20&status=downloaded
```

Response:
```json
{
  "videos": [...],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

### Get Job Status

```
GET /api/v1/jobs/{job_id}/status
```

Response:
```json
{
  "job_id": "abc123",
  "status": "running",
  "progress": {
    "videos_found": 120,
    "videos_downloaded": 85,
    "percentage": 71
  }
}
```

---

## UI Requirements

### Pages

1. **Dashboard**
   - Total videos collected
   - Videos by brand/keyword
   - Recent collection jobs
   - Storage usage

2. **Collection Page**
   - Form to start new collection
   - Keyword input (comma-separated or chips)
   - Country selector (multi-select)
   - Max videos slider
   - Start button

3. **Video Gallery**
   - Grid view of videos
   - Filters: brand, country, date, status
   - Search bar
   - Pagination
   - Click to view details

4. **Video Detail Page**
   - Video player
   - Metadata display
   - Download button
   - AI analysis (if available)
   - Related videos

5. **Jobs Page**
   - List of collection jobs
   - Status indicators
   - Progress bars
   - Cancel/retry buttons

### Components Needed

```
components/
├── VideoCard.tsx           # Video thumbnail + meta
├── VideoPlayer.tsx         # Video playback
├── VideoGallery.tsx        # Grid of VideoCards
├── CollectionForm.tsx      # Start new collection
├── JobProgress.tsx         # Progress indicator
├── KeywordInput.tsx        # Chip-style keyword entry
├── CountrySelector.tsx     # Multi-select countries
├── FilterBar.tsx           # Gallery filters
└── StatsCard.tsx           # Dashboard metrics
```

---

## Cloud Storage Setup

### Bucket Structure

```
gs://research-hub-videos/
├── videos/
│   ├── {project_id}/
│   │   ├── {video_id}.mp4
│   │   └── ...
├── thumbnails/
│   ├── {project_id}/
│   │   ├── {video_id}.jpg
│   │   └── ...
└── exports/
    └── {project_id}/
        └── export_{date}.zip
```

### Required Permissions

- `storage.objects.create`
- `storage.objects.get`
- `storage.objects.delete`
- `storage.buckets.get`

---

## Implementation Files

```
packages/research_hub/
├── src/
│   ├── services/
│   │   ├── ad_library_service.py     # Existing scraper
│   │   ├── video_downloader.py       # NEW: Download videos
│   │   ├── video_collection.py       # NEW: Batch collection
│   │   └── cloud_storage.py          # NEW: GCS integration
│   └── api/
│       ├── routes/
│       │   ├── videos.py             # Video endpoints
│       │   └── jobs.py               # Job endpoints
│       └── main.py                   # FastAPI app
└── scripts/
    ├── store_ads.py                  # Existing
    ├── collect_videos.py             # NEW: CLI for collection
    └── download_videos.py            # NEW: CLI for downloads
```

---

## Environment Variables

```bash
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_CLOUD_PROJECT=artful-striker-483214-b0

# Storage
GCS_BUCKET_NAME=research-hub-videos
GCS_VIDEO_PREFIX=videos
GCS_THUMBNAIL_PREFIX=thumbnails

# Collection Settings
MAX_CONCURRENT_DOWNLOADS=5
DOWNLOAD_TIMEOUT_SECONDS=300
RETRY_ATTEMPTS=3
```

---

## Next Steps

1. [ ] Create video downloader service
2. [ ] Set up GCS bucket
3. [ ] Build batch collection pipeline
4. [ ] Create FastAPI endpoints
5. [ ] UI agent builds frontend using this spec
