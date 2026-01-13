# Beat-Sync Service: Independent Microservice Launch Plan

> **Version**: 1.0
> **Status**: Ready for Implementation
> **Last Updated**: January 2026
> **Service Name**: `beat-sync-service`
> **GCP Project**: `artful-striker-483214-b0`
> **Target Region**: `asia-southeast1`

---

## Executive Summary

This document outlines the complete plan to launch Beat-Sync as an independent microservice within the Adiyogi platform. The service will handle CPU/GPU-intensive audio analysis and video composition tasks, isolated from the main application to ensure scalability and reliability.

### Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Runtime | Cloud Run | Serverless, auto-scaling, cost-efficient |
| Storage | Cloud Storage (GCS) | Large video files, CDN integration |
| Queue | Cloud Tasks | Long-running jobs, retries |
| Database | Firestore | Job metadata, user data |
| Container | Python 3.11 + FFmpeg | ML libraries compatibility |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT APPLICATIONS                             │
│                    (Adiyogi Web App, Mobile App, API)                       │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY / LOAD BALANCER                        │
│                        (Cloud Run Default Endpoint)                          │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│  MAIN ADIYOGI   │    │  BEAT-SYNC SERVICE  │    │  RESEARCH HUB   │
│     SERVICE     │    │   (Cloud Run)       │    │    SERVICE      │
│   (Cloud Run)   │    │                     │    │  (Cloud Run)    │
│                 │    │  • Beat Detection   │    │                 │
│  • Chat/AI      │    │  • Video Sync       │    │  • Research     │
│  • Sessions     │    │  • Job Processing   │    │  • Analysis     │
└────────┬────────┘    └──────────┬──────────┘    └─────────────────┘
         │                        │
         │                        │
         ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SHARED INFRASTRUCTURE                               │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐ │
│  │   Firestore   │  │ Cloud Storage │  │  Cloud Tasks  │  │  Pub/Sub     │ │
│  │   (Metadata)  │  │   (Videos)    │  │   (Jobs)      │  │  (Events)    │ │
│  └───────────────┘  └───────────────┘  └───────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Service Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BEAT-SYNC SERVICE (Cloud Run)                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         FastAPI Application                          │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │    │
│  │  │ /analyze     │  │ /create      │  │ /jobs        │  │ /health │ │    │
│  │  │ Beat Analysis│  │ Video Create │  │ Job Status   │  │ Status  │ │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────────┘ │    │
│  │         │                 │                 │                       │    │
│  │         ▼                 ▼                 ▼                       │    │
│  │  ┌────────────────────────────────────────────────────────────────┐│    │
│  │  │                    Processing Engine                           ││    │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐││    │
│  │  │  │ Beat        │  │ Video       │  │ Job                     │││    │
│  │  │  │ Detector    │  │ Composer    │  │ Manager                 │││    │
│  │  │  │ (librosa/   │  │ (moviepy/   │  │ (Cloud Tasks)           │││    │
│  │  │  │  madmom)    │  │  ffmpeg)    │  │                         │││    │
│  │  │  └─────────────┘  └─────────────┘  └─────────────────────────┘││    │
│  │  └────────────────────────────────────────────────────────────────┘│    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         Storage Layer                                   │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────────────────┐  │ │
│  │  │ Audio Cache    │  │ Video Cache    │  │ Output Storage           │  │ │
│  │  │ (/tmp/audio)   │  │ (/tmp/video)   │  │ (GCS: beat-sync-output)  │  │ │
│  │  └────────────────┘  └────────────────┘  └──────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
/home/user/research/
├── packages/
│   └── beat_sync/                    # Core library package
│       ├── README.md
│       ├── pyproject.toml
│       ├── requirements.txt
│       ├── src/
│       │   ├── __init__.py
│       │   ├── models.py             # Data models (BeatMap, SyncConfig, etc.)
│       │   ├── config.py             # Configuration and presets
│       │   ├── beat_detector.py      # librosa + madmom beat detection
│       │   ├── beat_analyzer.py      # Advanced analysis (sections, drops)
│       │   ├── video_composer.py     # MoviePy video composition
│       │   ├── clip_selector.py      # Intelligent clip selection
│       │   ├── transitions.py        # Transition effects library
│       │   ├── storage.py            # GCS storage abstraction
│       │   ├── processor.py          # Main orchestrator
│       │   └── job_manager.py        # Cloud Tasks integration
│       └── tests/
│           ├── __init__.py
│           ├── conftest.py
│           ├── test_beat_detector.py
│           ├── test_video_composer.py
│           └── test_processor.py
│
├── apps/
│   └── beat-sync-service/            # Deployable service
│       ├── main.py                   # FastAPI application
│       ├── requirements.txt          # Service-specific deps
│       ├── Dockerfile                # Container definition
│       └── cloudbuild.yaml           # CI/CD pipeline
│
└── docs/
    └── plans/
        ├── BEAT_SYNC_VIDEO_SERVICE.md
        └── BEAT_SYNC_SERVICE_LAUNCH.md  # This document
```

---

## API Design

### Base URL
```
Production: https://beat-sync-service-{hash}.asia-southeast1.run.app
Internal:   https://beat-sync-service (via Cloud Run service-to-service)
```

### API Versioning
```
/api/v1/beat-sync/*
```

### Endpoints

#### Health & Status

```yaml
GET /
  Description: Basic health check
  Response:
    status: "ok" | "degraded"
    service: "beat-sync"
    version: "1.0.0"

GET /health
  Description: Detailed health with dependencies
  Response:
    status: "healthy" | "degraded" | "unhealthy"
    checks:
      storage: "ok" | "error"
      ffmpeg: "ok" | "error"
      librosa: "ok" | "error"
```

#### Beat Analysis

```yaml
POST /api/v1/beat-sync/analyze
  Description: Analyze audio and extract beat map
  Request:
    audio_url: string (required)     # URL to audio file
    audio_file: binary (optional)    # Direct file upload
    method: "librosa" | "madmom" | "hybrid" (default: "librosa")
    fps: integer (default: 30)       # Target video frame rate
  Response:
    job_id: string                   # For async tracking
    status: "processing" | "completed"
    beat_map:                        # If completed synchronously
      tempo: number                  # BPM
      duration: number               # Seconds
      total_beats: integer
      beats: array<BeatInfo>
      sections: array<Section>       # Verse, chorus, drop detection

GET /api/v1/beat-sync/analyze/{job_id}
  Description: Get beat analysis result
  Response:
    job_id: string
    status: "pending" | "processing" | "completed" | "failed"
    progress: number (0-100)
    beat_map: BeatMap | null
    error: string | null
```

#### Video Creation

```yaml
POST /api/v1/beat-sync/create
  Description: Create beat-synced video (async)
  Request:
    audio_url: string (required)
    video_urls: array<string> (required, min 1)
    config:
      sync_mode: "every_beat" | "every_other" | "strong_beats" | "downbeats"
      strength_threshold: number (0-1, default: 0.5)
      transition_style: "cut" | "fade" | "zoom" | "flash" | "glitch"
      transition_duration: number (seconds, default: 0.1)
      output_resolution: [width, height] (default: [1920, 1080])
      output_fps: integer (default: 30)
      output_format: "mp4" | "webm" (default: "mp4")
    preview_only: boolean (default: false)
    preview_duration: number (seconds, default: 30)
    webhook_url: string (optional)   # Callback on completion
  Response:
    job_id: string
    status: "queued"
    estimated_duration: number (seconds)
    queue_position: integer

GET /api/v1/beat-sync/create/{job_id}
  Description: Get video creation job status
  Response:
    job_id: string
    status: "queued" | "processing" | "completed" | "failed"
    progress: number (0-100)
    current_step: string             # "downloading" | "analyzing" | "composing"
    result:
      output_url: string             # GCS signed URL
      duration: number
      file_size: integer
      total_cuts: integer
      processing_time: number
    error: string | null

DELETE /api/v1/beat-sync/create/{job_id}
  Description: Cancel a pending/processing job
  Response:
    success: boolean
    message: string
```

#### Job Management

```yaml
GET /api/v1/beat-sync/jobs
  Description: List user's jobs
  Query Params:
    status: string (optional)
    limit: integer (default: 20, max: 100)
    offset: integer (default: 0)
  Response:
    jobs: array<JobSummary>
    total: integer
    has_more: boolean

GET /api/v1/beat-sync/jobs/{job_id}/logs
  Description: Get processing logs for debugging
  Response:
    logs: array<LogEntry>
```

#### Presets & Configuration

```yaml
GET /api/v1/beat-sync/presets
  Description: List available configuration presets
  Response:
    presets:
      - name: "music_video"
        description: "Cuts on every strong beat with fade transitions"
        config: {...}
      - name: "fast_cuts"
        description: "Quick cuts on every beat"
        config: {...}
      - name: "cinematic"
        description: "Slower cuts on downbeats with zoom transitions"
        config: {...}

GET /api/v1/beat-sync/transitions
  Description: List available transition effects
  Response:
    transitions:
      - name: "cut"
        description: "Hard cut between clips"
        supports_duration: false
      - name: "fade"
        description: "Crossfade between clips"
        supports_duration: true
        min_duration: 0.1
        max_duration: 2.0
```

---

## Data Models

### Request/Response Models

```python
# packages/beat_sync/src/api_models.py

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal
from enum import Enum
from datetime import datetime


class SyncMode(str, Enum):
    EVERY_BEAT = "every_beat"
    EVERY_OTHER = "every_other"
    STRONG_BEATS = "strong_beats"
    DOWNBEATS = "downbeats"


class TransitionStyle(str, Enum):
    CUT = "cut"
    FADE = "fade"
    ZOOM = "zoom"
    FLASH = "flash"
    GLITCH = "glitch"
    SLIDE = "slide"


class DetectionMethod(str, Enum):
    LIBROSA = "librosa"
    MADMOM = "madmom"
    HYBRID = "hybrid"


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================================
# Beat Analysis
# ============================================================================

class AnalyzeRequest(BaseModel):
    """Request to analyze audio for beats."""
    audio_url: HttpUrl
    method: DetectionMethod = DetectionMethod.LIBROSA
    fps: int = Field(default=30, ge=15, le=60)


class BeatInfo(BaseModel):
    """Single beat information."""
    index: int
    time: float          # Seconds
    frame: int           # Video frame number
    strength: float      # 0.0 to 1.0
    is_downbeat: bool = False


class Section(BaseModel):
    """Detected audio section."""
    name: str            # "intro", "verse", "chorus", "drop", "outro"
    start_time: float
    end_time: float
    energy: float        # Average energy level


class BeatMapResponse(BaseModel):
    """Complete beat analysis result."""
    tempo: float
    duration: float
    total_beats: int
    beats: List[BeatInfo]
    sections: List[Section] = []
    detection_method: DetectionMethod
    processing_time_ms: int


# ============================================================================
# Video Creation
# ============================================================================

class VideoConfig(BaseModel):
    """Configuration for video creation."""
    sync_mode: SyncMode = SyncMode.EVERY_BEAT
    strength_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    transition_style: TransitionStyle = TransitionStyle.CUT
    transition_duration: float = Field(default=0.1, ge=0.0, le=2.0)
    output_resolution: tuple[int, int] = (1920, 1080)
    output_fps: int = Field(default=30, ge=15, le=60)
    output_format: Literal["mp4", "webm"] = "mp4"


class CreateVideoRequest(BaseModel):
    """Request to create beat-synced video."""
    audio_url: HttpUrl
    video_urls: List[HttpUrl] = Field(..., min_length=1, max_length=20)
    config: Optional[VideoConfig] = None
    preset: Optional[str] = None
    preview_only: bool = False
    preview_duration: float = Field(default=30, ge=5, le=120)
    webhook_url: Optional[HttpUrl] = None


class JobResponse(BaseModel):
    """Job creation/status response."""
    job_id: str
    status: JobStatus
    progress: float = 0.0
    current_step: Optional[str] = None
    estimated_duration: Optional[float] = None
    queue_position: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class VideoResultResponse(BaseModel):
    """Completed video result."""
    job_id: str
    status: JobStatus = JobStatus.COMPLETED
    output_url: str              # Signed GCS URL
    duration: float
    file_size: int
    total_cuts: int
    beat_map: BeatMapResponse
    processing_time_seconds: float
    created_at: datetime
    expires_at: datetime         # URL expiration


# ============================================================================
# Job Management
# ============================================================================

class JobSummary(BaseModel):
    """Summary of a job for listing."""
    job_id: str
    status: JobStatus
    progress: float
    audio_url: str
    video_count: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    output_url: Optional[str] = None


class JobListResponse(BaseModel):
    """List of jobs response."""
    jobs: List[JobSummary]
    total: int
    has_more: bool
```

---

## Firestore Schema

### Collections

```
beat_sync_jobs/
├── {job_id}/
│   ├── id: string
│   ├── user_id: string
│   ├── project_id: string
│   ├── type: "analyze" | "create"
│   ├── status: "queued" | "processing" | "completed" | "failed"
│   ├── progress: number
│   ├── current_step: string
│   │
│   ├── input:
│   │   ├── audio_url: string
│   │   ├── video_urls: array<string>
│   │   ├── config: object
│   │   └── preset: string
│   │
│   ├── output:
│   │   ├── beat_map: object
│   │   ├── output_path: string (GCS path)
│   │   ├── output_url: string (signed URL)
│   │   ├── duration: number
│   │   ├── file_size: number
│   │   └── total_cuts: number
│   │
│   ├── error:
│   │   ├── message: string
│   │   ├── code: string
│   │   └── stack: string
│   │
│   ├── metrics:
│   │   ├── processing_time_ms: number
│   │   ├── download_time_ms: number
│   │   ├── analysis_time_ms: number
│   │   └── composition_time_ms: number
│   │
│   ├── created_at: timestamp
│   ├── updated_at: timestamp
│   ├── started_at: timestamp
│   └── completed_at: timestamp
│
beat_sync_analytics/
├── daily_stats/
│   └── {date}/
│       ├── total_jobs: number
│       ├── completed_jobs: number
│       ├── failed_jobs: number
│       ├── total_processing_seconds: number
│       └── total_output_bytes: number
```

---

## Cloud Storage Structure

```
gs://adiyogi-beat-sync/
├── inputs/
│   ├── audio/
│   │   └── {job_id}/
│   │       └── audio.{ext}
│   └── video/
│       └── {job_id}/
│           ├── clip_0.mp4
│           ├── clip_1.mp4
│           └── ...
│
├── outputs/
│   └── {job_id}/
│       ├── output.mp4
│       ├── preview.mp4
│       ├── beat_map.json
│       └── thumbnail.jpg
│
├── cache/
│   └── beat_maps/
│       └── {audio_hash}.json    # Cached beat analysis
│
└── temp/
    └── {job_id}/                # Temporary processing files
```

### Lifecycle Policies

```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 7,
          "matchesPrefix": ["temp/"]
        }
      },
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 30,
          "matchesPrefix": ["inputs/"]
        }
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {
          "age": 7,
          "matchesPrefix": ["outputs/"]
        }
      }
    ]
  }
}
```

---

## Service Implementation

### FastAPI Application

```python
# apps/beat-sync-service/main.py

"""
Beat-Sync Service - FastAPI Application.

Independent microservice for beat detection and video synchronization.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add project root for package imports
root = Path(__file__).parent.parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from packages.beat_sync.src.config import (
    validate_config,
    get_config_summary,
    CORS_ORIGINS,
)
from packages.beat_sync.src.api_models import (
    AnalyzeRequest,
    CreateVideoRequest,
    JobResponse,
    VideoResultResponse,
    JobListResponse,
    BeatMapResponse,
    JobStatus,
)
from packages.beat_sync.src.processor import BeatSyncProcessor
from packages.beat_sync.src.job_manager import JobManager
from packages.beat_sync.src.storage import StorageManager


# =============================================================================
# APPLICATION SETUP
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    config_status = validate_config()
    print(f"Beat-Sync Service starting...")
    print(f"Configuration: {get_config_summary()}")

    # Verify FFmpeg
    import subprocess
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        print(f"FFmpeg: OK")
    except Exception as e:
        print(f"FFmpeg: ERROR - {e}")

    # Verify librosa
    try:
        import librosa
        print(f"librosa: OK (v{librosa.__version__})")
    except Exception as e:
        print(f"librosa: ERROR - {e}")

    if config_status["warnings"]:
        for warning in config_status["warnings"]:
            print(f"Warning: {warning}")

    yield

    # Shutdown
    print("Beat-Sync Service shutting down...")


app = FastAPI(
    title="Beat-Sync Service API",
    description="Beat detection and video synchronization microservice",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# DEPENDENCIES
# =============================================================================

def get_processor() -> BeatSyncProcessor:
    """Get beat sync processor instance."""
    return BeatSyncProcessor()


def get_job_manager() -> JobManager:
    """Get job manager instance."""
    return JobManager()


def get_storage() -> StorageManager:
    """Get storage manager instance."""
    return StorageManager()


# =============================================================================
# HEALTH ENDPOINTS
# =============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    config_status = validate_config()
    return {
        "status": "ok" if config_status["ready"] else "degraded",
        "service": "beat-sync",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health():
    """Detailed health check."""
    import subprocess

    checks = {
        "config": "ok",
        "ffmpeg": "ok",
        "librosa": "ok",
        "storage": "ok",
    }

    # Check FFmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except Exception:
        checks["ffmpeg"] = "error"

    # Check librosa
    try:
        import librosa
        import numpy as np
        # Quick test
        y = np.zeros(22050)
        librosa.beat.beat_track(y=y, sr=22050)
    except Exception:
        checks["librosa"] = "error"

    # Check storage
    try:
        storage = get_storage()
        if not storage.is_configured:
            checks["storage"] = "not_configured"
    except Exception:
        checks["storage"] = "error"

    # Overall status
    all_ok = all(v == "ok" for v in checks.values())

    return {
        "status": "healthy" if all_ok else "degraded",
        "service": "beat-sync",
        "version": "1.0.0",
        "checks": checks,
    }


# =============================================================================
# BEAT ANALYSIS ENDPOINTS
# =============================================================================

@app.post("/api/v1/beat-sync/analyze", tags=["Analysis"])
async def analyze_audio(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
):
    """
    Analyze audio and extract beat map.

    For short audio (<60s), returns result synchronously.
    For longer audio, returns job_id for async tracking.
    """
    processor = get_processor()
    job_manager = get_job_manager()

    # Create job
    job_id = str(uuid.uuid4())
    job = await job_manager.create_job(
        job_id=job_id,
        job_type="analyze",
        input_data={
            "audio_url": str(request.audio_url),
            "method": request.method.value,
            "fps": request.fps,
        },
    )

    # For short audio, try synchronous processing
    async def process_analysis():
        try:
            await job_manager.update_status(job_id, JobStatus.PROCESSING)

            beat_map = await processor.analyze_audio(
                audio_url=str(request.audio_url),
                method=request.method,
                fps=request.fps,
            )

            await job_manager.complete_job(
                job_id=job_id,
                output_data=beat_map.dict(),
            )

        except Exception as e:
            await job_manager.fail_job(job_id, str(e))

    background_tasks.add_task(process_analysis)

    return JobResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@app.get("/api/v1/beat-sync/analyze/{job_id}", tags=["Analysis"])
async def get_analysis_result(job_id: str):
    """Get beat analysis result."""
    job_manager = get_job_manager()
    job = await job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = {
        "job_id": job_id,
        "status": job.status,
        "progress": job.progress,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }

    if job.status == JobStatus.COMPLETED:
        response["beat_map"] = job.output_data
    elif job.status == JobStatus.FAILED:
        response["error"] = job.error_message

    return response


# =============================================================================
# VIDEO CREATION ENDPOINTS
# =============================================================================

@app.post("/api/v1/beat-sync/create", tags=["Video"])
async def create_video(
    request: CreateVideoRequest,
    background_tasks: BackgroundTasks,
):
    """
    Create beat-synced video.

    Always runs asynchronously due to processing time.
    Use webhook_url for completion notification.
    """
    processor = get_processor()
    job_manager = get_job_manager()

    # Validate video count
    if len(request.video_urls) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 video sources allowed"
        )

    # Create job
    job_id = str(uuid.uuid4())
    job = await job_manager.create_job(
        job_id=job_id,
        job_type="create",
        input_data={
            "audio_url": str(request.audio_url),
            "video_urls": [str(url) for url in request.video_urls],
            "config": request.config.dict() if request.config else None,
            "preset": request.preset,
            "preview_only": request.preview_only,
            "preview_duration": request.preview_duration,
            "webhook_url": str(request.webhook_url) if request.webhook_url else None,
        },
    )

    # Estimate duration (rough: 1 min processing per 10s video)
    estimated_duration = request.preview_duration * 6 if request.preview_only else 300

    # Queue processing
    async def process_video():
        try:
            await job_manager.update_status(
                job_id,
                JobStatus.PROCESSING,
                current_step="downloading"
            )

            result = await processor.create_video(
                audio_url=str(request.audio_url),
                video_urls=[str(url) for url in request.video_urls],
                config=request.config,
                preview_only=request.preview_only,
                preview_duration=request.preview_duration,
                progress_callback=lambda p, s: job_manager.update_progress(job_id, p, s),
            )

            await job_manager.complete_job(
                job_id=job_id,
                output_data=result.dict(),
            )

            # Webhook notification
            if request.webhook_url:
                await notify_webhook(str(request.webhook_url), job_id, "completed", result)

        except Exception as e:
            await job_manager.fail_job(job_id, str(e))

            if request.webhook_url:
                await notify_webhook(str(request.webhook_url), job_id, "failed", {"error": str(e)})

    background_tasks.add_task(process_video)

    # Get queue position
    queue_position = await job_manager.get_queue_position(job_id)

    return JobResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        estimated_duration=estimated_duration,
        queue_position=queue_position,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@app.get("/api/v1/beat-sync/create/{job_id}", tags=["Video"])
async def get_video_result(job_id: str):
    """Get video creation job status and result."""
    job_manager = get_job_manager()
    job = await job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = JobResponse(
        job_id=job_id,
        status=job.status,
        progress=job.progress,
        current_step=job.current_step,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )

    if job.status == JobStatus.COMPLETED:
        # Generate signed URL for output
        storage = get_storage()
        output_url = await storage.get_signed_url(
            job.output_data.get("output_path"),
            expiration_hours=24,
        )

        return VideoResultResponse(
            job_id=job_id,
            output_url=output_url,
            duration=job.output_data.get("duration"),
            file_size=job.output_data.get("file_size"),
            total_cuts=job.output_data.get("total_cuts"),
            beat_map=job.output_data.get("beat_map"),
            processing_time_seconds=job.metrics.get("processing_time_ms", 0) / 1000,
            created_at=job.created_at,
            expires_at=job.created_at,  # TODO: Add 24 hours
        )

    elif job.status == JobStatus.FAILED:
        response_dict = response.dict()
        response_dict["error"] = job.error_message
        return response_dict

    return response


@app.delete("/api/v1/beat-sync/create/{job_id}", tags=["Video"])
async def cancel_video_job(job_id: str):
    """Cancel a pending or processing video job."""
    job_manager = get_job_manager()

    success = await job_manager.cancel_job(job_id)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Job cannot be cancelled (already completed or not found)"
        )

    return {"success": True, "message": "Job cancelled"}


# =============================================================================
# JOB MANAGEMENT ENDPOINTS
# =============================================================================

@app.get("/api/v1/beat-sync/jobs", tags=["Jobs"])
async def list_jobs(
    status: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
):
    """List jobs with optional filters."""
    job_manager = get_job_manager()

    status_filter = JobStatus(status) if status else None

    jobs = await job_manager.list_jobs(
        status=status_filter,
        job_type=job_type,
        limit=limit,
        offset=offset,
    )

    total = await job_manager.count_jobs(status=status_filter, job_type=job_type)

    return JobListResponse(
        jobs=jobs,
        total=total,
        has_more=(offset + limit) < total,
    )


@app.get("/api/v1/beat-sync/jobs/{job_id}/logs", tags=["Jobs"])
async def get_job_logs(job_id: str):
    """Get processing logs for a job."""
    job_manager = get_job_manager()
    logs = await job_manager.get_job_logs(job_id)

    if not logs:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"job_id": job_id, "logs": logs}


# =============================================================================
# PRESETS & CONFIGURATION ENDPOINTS
# =============================================================================

@app.get("/api/v1/beat-sync/presets", tags=["Configuration"])
async def list_presets():
    """List available configuration presets."""
    from packages.beat_sync.src.config import PRESETS

    return {
        "presets": [
            {
                "name": name,
                "description": preset.description,
                "config": preset.to_dict(),
            }
            for name, preset in PRESETS.items()
        ]
    }


@app.get("/api/v1/beat-sync/transitions", tags=["Configuration"])
async def list_transitions():
    """List available transition effects."""
    from packages.beat_sync.src.transitions import TRANSITIONS

    return {
        "transitions": [
            {
                "name": name,
                "description": transition.description,
                "supports_duration": transition.supports_duration,
                "min_duration": transition.min_duration,
                "max_duration": transition.max_duration,
            }
            for name, transition in TRANSITIONS.items()
        ]
    }


# =============================================================================
# INTERNAL ENDPOINTS (Service-to-Service)
# =============================================================================

@app.post("/internal/process-task", tags=["Internal"], include_in_schema=False)
async def process_cloud_task(task_data: dict):
    """
    Process a Cloud Task.

    Called by Cloud Tasks for deferred job processing.
    """
    job_id = task_data.get("job_id")
    job_type = task_data.get("job_type")

    job_manager = get_job_manager()
    processor = get_processor()

    job = await job_manager.get_job(job_id)

    if not job:
        return {"error": "Job not found"}

    if job_type == "analyze":
        beat_map = await processor.analyze_audio(
            audio_url=job.input_data["audio_url"],
            method=job.input_data["method"],
            fps=job.input_data["fps"],
        )
        await job_manager.complete_job(job_id, beat_map.dict())

    elif job_type == "create":
        result = await processor.create_video(
            audio_url=job.input_data["audio_url"],
            video_urls=job.input_data["video_urls"],
            config=job.input_data.get("config"),
            preview_only=job.input_data.get("preview_only", False),
        )
        await job_manager.complete_job(job_id, result.dict())

    return {"success": True}


# =============================================================================
# WEBHOOK HELPER
# =============================================================================

async def notify_webhook(webhook_url: str, job_id: str, status: str, data: dict):
    """Send webhook notification."""
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                webhook_url,
                json={
                    "event": "beat_sync.job." + status,
                    "job_id": job_id,
                    "status": status,
                    "data": data,
                },
                timeout=10.0,
            )
    except Exception as e:
        print(f"Webhook notification failed: {e}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )
```

---

## Dockerfile

```dockerfile
# apps/beat-sync-service/Dockerfile

# Beat-Sync Service Dockerfile
# Optimized for Google Cloud Run with FFmpeg and ML libraries

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # FFmpeg for video/audio processing
    ffmpeg \
    # Audio libraries
    libsndfile1 \
    libsndfile1-dev \
    # Build tools (for some ML packages)
    gcc \
    g++ \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY apps/beat-sync-service/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project (needed for package imports)
COPY . /app

# Set Python path
ENV PYTHONPATH=/app

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Create temp directories
RUN mkdir -p /tmp/beat-sync/audio /tmp/beat-sync/video /tmp/beat-sync/output

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run with gunicorn for production
CMD exec gunicorn \
    --bind :$PORT \
    --workers 2 \
    --threads 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 300 \
    --graceful-timeout 30 \
    apps.beat-sync-service.main:app
```

---

## Requirements

```txt
# apps/beat-sync-service/requirements.txt

# =============================================================================
# CORE FRAMEWORK
# =============================================================================
fastapi>=0.109.0
uvicorn>=0.27.0
gunicorn>=21.0.0

# =============================================================================
# BEAT DETECTION
# =============================================================================
librosa>=0.10.0
madmom>=0.16.1
numpy>=1.24.0
scipy>=1.11.0
soundfile>=0.12.0

# =============================================================================
# VIDEO PROCESSING
# =============================================================================
moviepy>=1.0.3
imageio>=2.31.0
imageio-ffmpeg>=0.4.8
Pillow>=10.0.0

# =============================================================================
# GOOGLE CLOUD
# =============================================================================
google-cloud-storage>=2.18.0
google-cloud-firestore>=2.11.0
google-cloud-tasks>=2.14.0

# =============================================================================
# HTTP & ASYNC
# =============================================================================
httpx>=0.25.0
aiohttp>=3.9.0
aiofiles>=23.0.0

# =============================================================================
# DATA VALIDATION
# =============================================================================
pydantic>=2.0.0

# =============================================================================
# UTILITIES
# =============================================================================
tenacity>=8.2.0
python-multipart>=0.0.6
```

---

## Cloud Build Configuration

```yaml
# apps/beat-sync-service/cloudbuild.yaml

steps:
  # Build the Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - '${_REGION}-docker.pkg.dev/$PROJECT_ID/beat-sync/api:$COMMIT_SHA'
      - '-t'
      - '${_REGION}-docker.pkg.dev/$PROJECT_ID/beat-sync/api:latest'
      - '-f'
      - 'apps/beat-sync-service/Dockerfile'
      - '.'

  # Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - '--all-tags'
      - '${_REGION}-docker.pkg.dev/$PROJECT_ID/beat-sync/api'

  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'beat-sync-service'
      - '--image'
      - '${_REGION}-docker.pkg.dev/$PROJECT_ID/beat-sync/api:$COMMIT_SHA'
      - '--region'
      - '${_REGION}'
      - '--platform'
      - 'managed'
      # Resources (CPU-intensive workload)
      - '--memory'
      - '8Gi'
      - '--cpu'
      - '4'
      - '--timeout'
      - '900'          # 15 minutes for long videos
      - '--concurrency'
      - '4'            # Low concurrency due to CPU load
      - '--min-instances'
      - '0'
      - '--max-instances'
      - '10'
      # Authentication
      - '--allow-unauthenticated'
      # Environment variables
      - '--set-env-vars'
      - 'GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GCS_BUCKET=adiyogi-beat-sync,FIRESTORE_COLLECTION=beat_sync_jobs'

substitutions:
  _REGION: asia-southeast1

options:
  logging: CLOUD_LOGGING_ONLY
  machineType: 'E2_HIGHCPU_8'  # Faster builds for large image
```

---

## Cloud Run Service Configuration

```yaml
# Service: beat-sync-service
# Region: asia-southeast1

apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: beat-sync-service
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/execution-environment: gen2
spec:
  template:
    metadata:
      annotations:
        # Scaling
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"  # Always-on CPU
        run.googleapis.com/startup-cpu-boost: "true"
    spec:
      containerConcurrency: 4
      timeoutSeconds: 900
      containers:
        - image: asia-southeast1-docker.pkg.dev/PROJECT_ID/beat-sync/api:latest
          ports:
            - containerPort: 8080
          resources:
            limits:
              cpu: "4"
              memory: "8Gi"
          env:
            - name: GOOGLE_CLOUD_PROJECT
              value: "artful-striker-483214-b0"
            - name: GCS_BUCKET
              value: "adiyogi-beat-sync"
            - name: FIRESTORE_COLLECTION
              value: "beat_sync_jobs"
            - name: MAX_PROCESSING_TIME
              value: "600"
            - name: TEMP_DIR
              value: "/tmp/beat-sync"
          startupProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 10
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /
              port: 8080
            periodSeconds: 30
```

---

## Infrastructure Setup

### 1. Create GCS Bucket

```bash
# Create bucket
gsutil mb -l asia-southeast1 gs://adiyogi-beat-sync

# Set lifecycle policy
cat > /tmp/lifecycle.json << 'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 7, "matchesPrefix": ["temp/"]}
      },
      {
        "action": {"type": "Delete"},
        "condition": {"age": 30, "matchesPrefix": ["inputs/"]}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 7, "matchesPrefix": ["outputs/"]}
      }
    ]
  }
}
EOF

gsutil lifecycle set /tmp/lifecycle.json gs://adiyogi-beat-sync

# Set CORS for browser uploads
cat > /tmp/cors.json << 'EOF'
[
  {
    "origin": ["*"],
    "method": ["GET", "PUT", "POST"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
EOF

gsutil cors set /tmp/cors.json gs://adiyogi-beat-sync
```

### 2. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create beat-sync \
    --repository-format=docker \
    --location=asia-southeast1 \
    --description="Beat-Sync Service Docker images"
```

### 3. Create Cloud Tasks Queue

```bash
gcloud tasks queues create beat-sync-jobs \
    --location=asia-southeast1 \
    --max-concurrent-dispatches=10 \
    --max-dispatches-per-second=1 \
    --max-attempts=3 \
    --min-backoff=10s \
    --max-backoff=300s
```

### 4. Set Up Service Account

```bash
# Create service account
gcloud iam service-accounts create beat-sync-service \
    --display-name="Beat-Sync Service Account"

# Grant permissions
PROJECT_ID=$(gcloud config get-value project)
SA_EMAIL="beat-sync-service@${PROJECT_ID}.iam.gserviceaccount.com"

# Storage access
gsutil iam ch serviceAccount:${SA_EMAIL}:objectAdmin gs://adiyogi-beat-sync

# Firestore access
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/datastore.user"

# Cloud Tasks access
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/cloudtasks.enqueuer"
```

---

## Integration with Main Application

### Option 1: Direct HTTP Calls

```python
# In main Adiyogi app
import httpx

BEAT_SYNC_SERVICE_URL = os.environ.get(
    "BEAT_SYNC_SERVICE_URL",
    "https://beat-sync-service-xxx.asia-southeast1.run.app"
)

async def create_beat_synced_video(
    audio_url: str,
    video_urls: list[str],
    config: dict = None,
) -> dict:
    """
    Create beat-synced video via Beat-Sync Service.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BEAT_SYNC_SERVICE_URL}/api/v1/beat-sync/create",
            json={
                "audio_url": audio_url,
                "video_urls": video_urls,
                "config": config,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


async def check_video_status(job_id: str) -> dict:
    """
    Check beat-sync job status.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BEAT_SYNC_SERVICE_URL}/api/v1/beat-sync/create/{job_id}",
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()
```

### Option 2: Service-to-Service Authentication (Recommended)

```python
# In main Adiyogi app
import google.auth.transport.requests
import google.oauth2.id_token

BEAT_SYNC_SERVICE_URL = "https://beat-sync-service-xxx.asia-southeast1.run.app"

async def get_id_token():
    """Get ID token for service-to-service auth."""
    auth_req = google.auth.transport.requests.Request()
    token = google.oauth2.id_token.fetch_id_token(auth_req, BEAT_SYNC_SERVICE_URL)
    return token


async def create_beat_synced_video(audio_url: str, video_urls: list[str]) -> dict:
    """Create beat-synced video with authenticated request."""
    token = await get_id_token()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BEAT_SYNC_SERVICE_URL}/api/v1/beat-sync/create",
            json={
                "audio_url": audio_url,
                "video_urls": video_urls,
            },
            headers={
                "Authorization": f"Bearer {token}",
            },
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
```

### Option 3: Pub/Sub Event-Driven

```python
# Publisher (Main App)
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, "beat-sync-requests")

def request_beat_sync(audio_url: str, video_urls: list[str], callback_topic: str):
    """Publish beat-sync request to Pub/Sub."""
    message = {
        "audio_url": audio_url,
        "video_urls": video_urls,
        "callback_topic": callback_topic,
    }

    future = publisher.publish(
        topic_path,
        json.dumps(message).encode("utf-8"),
    )
    return future.result()


# Subscriber (Beat-Sync Service)
# Add Pub/Sub push endpoint in main.py

@app.post("/pubsub/push", include_in_schema=False)
async def handle_pubsub_push(request: dict, background_tasks: BackgroundTasks):
    """Handle Pub/Sub push messages."""
    import base64
    import json

    message_data = base64.b64decode(request["message"]["data"]).decode("utf-8")
    payload = json.loads(message_data)

    # Process the request
    background_tasks.add_task(
        process_beat_sync_request,
        payload["audio_url"],
        payload["video_urls"],
        payload.get("callback_topic"),
    )

    return {"status": "ok"}
```

---

## Monitoring & Observability

### Cloud Monitoring Dashboard

```yaml
# monitoring/beat-sync-dashboard.yaml
displayName: Beat-Sync Service Dashboard
gridLayout:
  columns: 2
  widgets:
    # Request Rate
    - title: Request Rate
      xyChart:
        dataSets:
          - timeSeriesQuery:
              timeSeriesFilter:
                filter: metric.type="run.googleapis.com/request_count" resource.type="cloud_run_revision" resource.label.service_name="beat-sync-service"

    # Latency
    - title: Request Latency (p50, p95, p99)
      xyChart:
        dataSets:
          - timeSeriesQuery:
              timeSeriesFilter:
                filter: metric.type="run.googleapis.com/request_latencies" resource.type="cloud_run_revision" resource.label.service_name="beat-sync-service"

    # Instance Count
    - title: Active Instances
      xyChart:
        dataSets:
          - timeSeriesQuery:
              timeSeriesFilter:
                filter: metric.type="run.googleapis.com/container/instance_count" resource.type="cloud_run_revision" resource.label.service_name="beat-sync-service"

    # Memory Usage
    - title: Memory Utilization
      xyChart:
        dataSets:
          - timeSeriesQuery:
              timeSeriesFilter:
                filter: metric.type="run.googleapis.com/container/memory/utilizations" resource.type="cloud_run_revision" resource.label.service_name="beat-sync-service"

    # CPU Usage
    - title: CPU Utilization
      xyChart:
        dataSets:
          - timeSeriesQuery:
              timeSeriesFilter:
                filter: metric.type="run.googleapis.com/container/cpu/utilizations" resource.type="cloud_run_revision" resource.label.service_name="beat-sync-service"

    # Error Rate
    - title: Error Rate
      xyChart:
        dataSets:
          - timeSeriesQuery:
              timeSeriesFilter:
                filter: metric.type="run.googleapis.com/request_count" resource.type="cloud_run_revision" resource.label.service_name="beat-sync-service" metric.label.response_code_class!="2xx"
```

### Custom Metrics

```python
# packages/beat_sync/src/metrics.py

from google.cloud import monitoring_v3
import time

class MetricsCollector:
    """Custom metrics for beat-sync service."""

    def __init__(self, project_id: str):
        self.client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"

    def record_job_duration(self, job_type: str, duration_seconds: float):
        """Record job processing duration."""
        series = monitoring_v3.TimeSeries()
        series.metric.type = "custom.googleapis.com/beat_sync/job_duration"
        series.metric.labels["job_type"] = job_type

        point = monitoring_v3.Point()
        point.value.double_value = duration_seconds
        point.interval.end_time.seconds = int(time.time())

        series.points = [point]

        self.client.create_time_series(
            name=self.project_name,
            time_series=[series],
        )

    def record_job_status(self, job_type: str, status: str):
        """Record job completion status."""
        series = monitoring_v3.TimeSeries()
        series.metric.type = "custom.googleapis.com/beat_sync/job_count"
        series.metric.labels["job_type"] = job_type
        series.metric.labels["status"] = status

        point = monitoring_v3.Point()
        point.value.int64_value = 1
        point.interval.end_time.seconds = int(time.time())

        series.points = [point]

        self.client.create_time_series(
            name=self.project_name,
            time_series=[series],
        )
```

### Alerting Policies

```yaml
# Error Rate Alert
- displayName: Beat-Sync High Error Rate
  conditions:
    - displayName: Error rate > 5%
      conditionThreshold:
        filter: metric.type="run.googleapis.com/request_count" resource.type="cloud_run_revision" resource.label.service_name="beat-sync-service" metric.label.response_code_class!="2xx"
        comparison: COMPARISON_GT
        thresholdValue: 0.05
        duration: 300s
  notificationChannels:
    - projects/PROJECT_ID/notificationChannels/CHANNEL_ID

# Latency Alert
- displayName: Beat-Sync High Latency
  conditions:
    - displayName: p95 latency > 30s
      conditionThreshold:
        filter: metric.type="run.googleapis.com/request_latencies" resource.type="cloud_run_revision" resource.label.service_name="beat-sync-service"
        aggregations:
          - alignmentPeriod: 300s
            perSeriesAligner: ALIGN_PERCENTILE_95
        comparison: COMPARISON_GT
        thresholdValue: 30000  # 30 seconds in ms
        duration: 300s
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Create GCS bucket `adiyogi-beat-sync`
- [ ] Create Artifact Registry repository `beat-sync`
- [ ] Create Cloud Tasks queue `beat-sync-jobs`
- [ ] Create service account with required permissions
- [ ] Set up Firestore collection `beat_sync_jobs`
- [ ] Configure environment variables in Secret Manager

### Deployment

- [ ] Build and push Docker image
- [ ] Deploy to Cloud Run
- [ ] Verify health endpoint responds
- [ ] Test beat analysis endpoint
- [ ] Test video creation endpoint
- [ ] Verify GCS uploads work
- [ ] Verify Firestore writes work

### Post-Deployment

- [ ] Set up monitoring dashboard
- [ ] Configure alerting policies
- [ ] Update main app with service URL
- [ ] Test end-to-end integration
- [ ] Document API for team
- [ ] Set up CI/CD trigger

---

## Cost Estimation

### Cloud Run

| Resource | Spec | Cost/Month |
|----------|------|------------|
| vCPU | 4 vCPU | ~$0.024/vCPU-hour |
| Memory | 8 GB | ~$0.0025/GB-hour |
| Requests | ~10,000/month | ~$0.40 |

**Estimated**: $50-150/month (depends on usage)

### Cloud Storage

| Storage Class | Size | Cost/Month |
|---------------|------|------------|
| Standard | 100 GB | ~$2.30 |
| Operations | 100,000 | ~$0.50 |

**Estimated**: $5-20/month

### Total Estimated Cost

- Low usage: ~$60/month
- Medium usage: ~$150/month
- High usage: ~$300/month

---

## Security Considerations

1. **Authentication**: Use Cloud Run IAM for service-to-service auth
2. **Input Validation**: Validate all URLs, file sizes, durations
3. **Rate Limiting**: Implement per-user rate limits
4. **File Scanning**: Scan uploaded files for malware (optional)
5. **URL Allowlisting**: Only allow specific domains for video sources
6. **Signed URLs**: Use time-limited signed URLs for outputs
7. **Audit Logging**: Log all job creation and access

---

## Next Steps

1. **Review & Approve** this plan
2. **Create Package** - Set up `packages/beat_sync` structure
3. **Implement Core** - Beat detector and video composer
4. **Create Service** - FastAPI app in `apps/beat-sync-service`
5. **Deploy Infrastructure** - GCS, Firestore, Cloud Tasks
6. **Deploy Service** - Cloud Run deployment
7. **Integrate** - Connect main app to service
8. **Monitor** - Set up dashboards and alerts
