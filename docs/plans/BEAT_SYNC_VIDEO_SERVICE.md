# Beat-Sync Video Service Implementation Plan

> **Version**: 1.0
> **Status**: Research & Planning
> **Last Updated**: January 2026
> **Target Package**: `packages/video_processing` or new `packages/beat_sync`
> **Prerequisites**: VIDEO_PROCESSING_SERVICE_v2 (audio extraction with yt-dlp)

---

## Overview

Build a Beat-Sync Video Service that automatically synchronizes video clips, cuts, and transitions to the beats of a music track. This enables automated creation of music videos, promotional content, and rhythmic video montages.

### Goals

1. **Beat Detection** - Extract beat timestamps from audio tracks with high accuracy
2. **Video Sync** - Create automated cuts and transitions aligned to beats
3. **Flexible Editing** - Support multiple video sources, transition styles, and sync modes
4. **Integration** - Seamlessly integrate with existing Adiyogi video processing pipeline

---

## Research Summary: Open Source Beat Detection Tools

### Tier 1: Production-Ready Libraries

| Library | Language | Type | Accuracy | Use Case |
|---------|----------|------|----------|----------|
| **librosa** | Python | Offline | Good | General-purpose, well-documented |
| **madmom** | Python | Offline | Excellent | Best accuracy, neural network-based |
| **Essentia** | C++/Python | Both | Excellent | Comprehensive, production-ready |
| **aubio** | C/Python | Real-time | Good | Low latency, embedded systems |

### Tier 2: Specialized Tools

| Library | Language | Type | Use Case |
|---------|----------|------|----------|
| **BeatNet** | Python | Real-time | Live performances, neural network |
| **BEAST** | Python | Real-time | Bayesian networks, live shows |
| **web-audio-beat-detector** | JavaScript | Browser | Web applications |

### Recommendation for Adiyogi

**Primary: librosa + madmom combo**
- `librosa` for quick beat tracking and audio analysis
- `madmom` for high-accuracy beat detection when needed
- Both integrate naturally with Python ecosystem

**Video Editing: moviepy**
- Pure Python video editing
- Easy integration with beat timestamps
- FFmpeg backend for reliability

---

## Architecture

```mermaid
flowchart TB
    subgraph Input["Input Sources"]
        AudioFile[Audio File]
        VideoSource[Video Source(s)]
        YouTubeURL[YouTube URL]
    end

    subgraph BeatDetection["Beat Detection Engine"]
        AudioExtractor[Audio Extractor<br/>yt-dlp / ffmpeg]
        BeatAnalyzer[Beat Analyzer<br/>librosa / madmom]
        BeatMap[Beat Map<br/>timestamps + intensity]
    end

    subgraph VideoEngine["Video Editing Engine"]
        ClipSelector[Clip Selector]
        TransitionEngine[Transition Engine]
        VideoComposer[Video Composer<br/>moviepy]
    end

    subgraph Output["Output"]
        SyncedVideo[Synchronized Video]
        BeatData[Beat Data JSON]
        Preview[Preview Clips]
    end

    Input --> BeatDetection
    AudioFile --> BeatAnalyzer
    VideoSource --> ClipSelector

    BeatAnalyzer --> BeatMap
    BeatMap --> ClipSelector
    BeatMap --> TransitionEngine

    ClipSelector --> VideoComposer
    TransitionEngine --> VideoComposer

    VideoComposer --> Output
```

---

## Core Algorithms

### Beat Detection with librosa

```python
"""
Beat detection using librosa - the standard approach.
"""
import librosa
import numpy as np

def detect_beats_librosa(audio_path: str, fps: int = 30) -> dict:
    """
    Detect beats in an audio file using librosa.

    Args:
        audio_path: Path to audio file (mp3, wav, m4a)
        fps: Target video frame rate

    Returns:
        Dictionary with beat times, frames, tempo, and intensity
    """
    # Load audio file
    y, sr = librosa.load(audio_path, sr=22050)

    # Detect beats and tempo
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    # Convert frames to timestamps
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    # Convert to video frames
    video_frames = (beat_times * fps).astype(int)

    # Calculate beat strength/intensity using onset envelope
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    beat_strength = onset_env[beat_frames]

    # Normalize strength to 0-1
    if beat_strength.max() > 0:
        beat_strength = beat_strength / beat_strength.max()

    return {
        "tempo": float(tempo),
        "beat_times": beat_times.tolist(),
        "beat_frames": video_frames.tolist(),
        "beat_strength": beat_strength.tolist(),
        "total_beats": len(beat_times),
        "duration": float(librosa.get_duration(y=y, sr=sr)),
    }
```

### High-Accuracy Beat Detection with madmom

```python
"""
Beat detection using madmom - more accurate, neural network-based.
"""
import madmom

def detect_beats_madmom(audio_path: str, fps: int = 30) -> dict:
    """
    Detect beats using madmom's neural network approach.

    More accurate than librosa, especially for complex rhythms.
    """
    # Create beat tracking processor
    proc = madmom.features.beats.DBNBeatTrackingProcessor(fps=100)

    # Run RNN beat processor
    act = madmom.features.beats.RNNBeatProcessor()(audio_path)

    # Get beat times
    beat_times = proc(act)

    # Convert to video frames
    video_frames = (beat_times * fps).astype(int)

    # Calculate intervals for tempo estimation
    if len(beat_times) > 1:
        intervals = np.diff(beat_times)
        avg_interval = np.mean(intervals)
        tempo = 60.0 / avg_interval
    else:
        tempo = 120.0  # Default

    return {
        "tempo": float(tempo),
        "beat_times": beat_times.tolist(),
        "beat_frames": video_frames.tolist(),
        "total_beats": len(beat_times),
    }
```

### Video Sync with MoviePy

```python
"""
Video synchronization to beats using MoviePy.
"""
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeVideoClip
)
import random

def create_beat_synced_video(
    video_clips: list[str],
    audio_path: str,
    beat_times: list[float],
    output_path: str,
    transition_type: str = "cut",
) -> str:
    """
    Create a video that cuts on beats.

    Args:
        video_clips: List of video file paths
        audio_path: Path to music file
        beat_times: List of beat timestamps in seconds
        output_path: Output video path
        transition_type: "cut", "fade", "zoom", "flash"

    Returns:
        Path to output video
    """
    # Load audio
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    # Load all source videos
    sources = [VideoFileClip(clip) for clip in video_clips]

    # Calculate clip durations based on beat intervals
    clips = []
    for i, beat_time in enumerate(beat_times[:-1]):
        # Duration until next beat
        duration = beat_times[i + 1] - beat_time

        # Select random source video
        source = random.choice(sources)

        # Extract random segment from source
        max_start = max(0, source.duration - duration)
        start_time = random.uniform(0, max_start)

        # Create clip
        clip = source.subclip(start_time, start_time + duration)

        # Apply transition effect
        if transition_type == "fade":
            clip = clip.crossfadein(0.1)
        elif transition_type == "zoom":
            # Slight zoom in effect
            clip = clip.resize(lambda t: 1 + 0.02 * t)
        elif transition_type == "flash":
            # Quick brightness flash at start
            clip = clip.fx(vfx.colorx, 1.5).set_duration(0.05).crossfadeout(0.05)

        clips.append(clip)

    # Concatenate all clips
    final_video = concatenate_videoclips(clips, method="compose")

    # Add audio
    final_video = final_video.set_audio(audio)

    # Trim to audio duration
    final_video = final_video.set_duration(min(final_video.duration, total_duration))

    # Write output
    final_video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
    )

    # Cleanup
    for source in sources:
        source.close()
    audio.close()
    final_video.close()

    return output_path
```

---

## Package Structure

```
packages/beat_sync/
├── README.md
├── requirements.txt
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── models.py           # Data models (BeatMap, SyncConfig, etc.)
│   ├── config.py           # Processing presets and settings
│   ├── audio_extractor.py  # Extract audio from video/YouTube
│   ├── beat_detector.py    # Beat detection (librosa + madmom)
│   ├── beat_analyzer.py    # Advanced analysis (sections, drops, etc.)
│   ├── clip_selector.py    # Intelligent clip selection
│   ├── transitions.py      # Transition effects library
│   ├── video_composer.py   # MoviePy-based video composition
│   ├── processor.py        # Main orchestrator
│   └── api.py              # FastAPI routes
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_beat_detector.py
    ├── test_video_composer.py
    └── test_processor.py
```

---

## Data Models

### `packages/beat_sync/src/models.py`

```python
"""
Data models for beat-sync video processing.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class BeatDetectionMethod(Enum):
    """Beat detection algorithm to use."""
    LIBROSA = "librosa"           # Fast, good accuracy
    MADMOM = "madmom"             # Best accuracy, slower
    ESSENTIA = "essentia"         # Comprehensive
    HYBRID = "hybrid"             # librosa + madmom verification


class TransitionStyle(Enum):
    """Video transition styles."""
    CUT = "cut"                   # Hard cut
    FADE = "fade"                 # Crossfade
    ZOOM = "zoom"                 # Zoom in/out
    FLASH = "flash"               # Quick white flash
    GLITCH = "glitch"             # Glitch effect
    SLIDE = "slide"               # Slide transition
    SPIN = "spin"                 # Rotation
    SHAKE = "shake"               # Camera shake


class SyncMode(Enum):
    """How to sync video to beats."""
    EVERY_BEAT = "every_beat"           # Cut on every beat
    EVERY_OTHER = "every_other"         # Every 2nd beat
    STRONG_BEATS = "strong_beats"       # Only strong beats (>threshold)
    DOWNBEATS = "downbeats"             # Only on bar starts (1, 5, 9...)
    CUSTOM = "custom"                   # Custom beat selection


@dataclass
class BeatInfo:
    """Information about a single beat."""
    index: int
    time: float              # Seconds
    frame: int               # Video frame number
    strength: float          # 0.0 to 1.0
    is_downbeat: bool = False


@dataclass
class BeatMap:
    """Complete beat analysis of an audio track."""
    audio_path: str
    duration: float          # Total duration in seconds
    tempo: float             # BPM
    beats: List[BeatInfo]

    # Analysis metadata
    detection_method: BeatDetectionMethod = BeatDetectionMethod.LIBROSA
    sample_rate: int = 22050
    fps: int = 30

    # Sections (verse, chorus, drop, etc.)
    sections: List[Dict[str, Any]] = field(default_factory=list)

    def get_beat_times(self) -> List[float]:
        """Get all beat timestamps."""
        return [b.time for b in self.beats]

    def get_strong_beats(self, threshold: float = 0.5) -> List[BeatInfo]:
        """Get only beats above strength threshold."""
        return [b for b in self.beats if b.strength >= threshold]

    def get_downbeats(self) -> List[BeatInfo]:
        """Get only downbeats (first beat of each bar)."""
        return [b for b in self.beats if b.is_downbeat]

    def filter_by_mode(self, mode: SyncMode, **kwargs) -> List[BeatInfo]:
        """Filter beats based on sync mode."""
        if mode == SyncMode.EVERY_BEAT:
            return self.beats
        elif mode == SyncMode.EVERY_OTHER:
            return self.beats[::2]
        elif mode == SyncMode.STRONG_BEATS:
            threshold = kwargs.get("threshold", 0.5)
            return self.get_strong_beats(threshold)
        elif mode == SyncMode.DOWNBEATS:
            return self.get_downbeats()
        else:
            return self.beats


@dataclass
class VideoClip:
    """A video source clip."""
    path: str
    duration: float
    width: int
    height: int
    fps: float

    # Optional metadata
    tags: List[str] = field(default_factory=list)
    weight: float = 1.0      # Selection probability weight


@dataclass
class SyncConfig:
    """Configuration for beat-sync video creation."""

    # Beat detection
    detection_method: BeatDetectionMethod = BeatDetectionMethod.LIBROSA
    sync_mode: SyncMode = SyncMode.EVERY_BEAT
    strength_threshold: float = 0.5

    # Video output
    output_fps: int = 30
    output_resolution: tuple = (1920, 1080)
    output_format: str = "mp4"

    # Transitions
    transition_style: TransitionStyle = TransitionStyle.CUT
    transition_duration: float = 0.1  # Seconds

    # Clip selection
    min_clip_duration: float = 0.3    # Minimum seconds per clip
    max_clip_duration: float = 5.0    # Maximum seconds per clip
    avoid_repetition: bool = True     # Avoid repeating same clip consecutively

    # Audio
    keep_original_audio: bool = True
    audio_fade_in: float = 0.0
    audio_fade_out: float = 0.0

    # Processing
    preview_only: bool = False        # Generate preview instead of full video
    preview_duration: float = 30.0    # Preview duration in seconds


@dataclass
class SyncResult:
    """Result of beat-sync video processing."""

    # Output
    output_path: str
    duration: float

    # Beat info
    beat_map: BeatMap
    total_beats_used: int
    total_cuts: int

    # Clips used
    clips_used: List[Dict[str, Any]]

    # Processing info
    processing_time: float
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Status
    success: bool = True
    error_message: Optional[str] = None
```

---

## Implementation Phases

### Phase 1: Beat Detection Core (Week 1)

**Tasks:**
- [ ] Set up `packages/beat_sync` package structure
- [ ] Implement `audio_extractor.py` (reuse from video_processing)
- [ ] Implement `beat_detector.py` with librosa
- [ ] Add madmom support for high-accuracy mode
- [ ] Create `BeatMap` data model
- [ ] Add unit tests for beat detection
- [ ] Test with various music genres

**Deliverable:** Working beat detection that outputs timestamps

### Phase 2: Video Composition (Week 2)

**Tasks:**
- [ ] Implement `video_composer.py` with MoviePy
- [ ] Create basic cut-on-beat functionality
- [ ] Add transition effects (fade, zoom, flash)
- [ ] Implement clip selection logic
- [ ] Add audio mixing capabilities
- [ ] Handle various video input formats
- [ ] Add output quality presets

**Deliverable:** Create basic beat-synced videos

### Phase 3: Advanced Features (Week 3)

**Tasks:**
- [ ] Implement `beat_analyzer.py` for section detection
- [ ] Add intelligent clip selection based on energy
- [ ] Create more transition effects (glitch, shake)
- [ ] Add text/overlay sync to beats
- [ ] Implement preview generation
- [ ] Add batch processing support
- [ ] Optimize for large video files

**Deliverable:** Production-ready beat sync engine

### Phase 4: API Integration (Week 4)

**Tasks:**
- [ ] Create FastAPI routes in `api.py`
- [ ] Add background job processing
- [ ] Integrate with existing Adiyogi API
- [ ] Add progress tracking
- [ ] Create OpenAPI documentation
- [ ] Add rate limiting
- [ ] Deploy to Cloud Run

**Deliverable:** REST API for beat sync processing

---

## API Endpoints

```python
# POST /beat-sync/analyze
# Analyze audio and return beat map
{
    "audio_url": "https://...",
    "method": "librosa",  # or "madmom", "hybrid"
    "fps": 30
}

# POST /beat-sync/create
# Create beat-synced video
{
    "audio_url": "https://...",
    "video_urls": ["https://...", "https://..."],
    "config": {
        "sync_mode": "every_beat",
        "transition_style": "cut",
        "output_resolution": [1920, 1080]
    }
}

# GET /beat-sync/jobs/{job_id}
# Get job status and progress

# GET /beat-sync/result/{video_id}
# Get processed video
```

---

## Dependencies

### Required

```txt
# Beat Detection
librosa>=0.10.0
madmom>=0.16.1

# Video Editing
moviepy>=1.0.3
imageio>=2.31.0
imageio-ffmpeg>=0.4.8

# Audio Processing
numpy>=1.24.0
scipy>=1.11.0
soundfile>=0.12.0

# Utilities
pydantic>=2.0.0
tenacity>=8.2.0
```

### System Dependencies

```bash
# Ubuntu/Debian
apt-get install ffmpeg libsndfile1

# macOS
brew install ffmpeg libsndfile

# Already available in Cloud Run via static-ffmpeg
```

---

## Integration with Existing Video Processing

The beat sync service integrates with the existing `packages/video_processing` service:

```python
# In packages/video_processing/src/processor.py

from packages.beat_sync.src.processor import BeatSyncProcessor
from packages.beat_sync.src.models import SyncConfig, SyncMode

class VideoProcessor:
    # ... existing code ...

    def create_beat_synced_video(
        self,
        audio_url: str,
        video_urls: list[str],
        config: Optional[SyncConfig] = None,
    ) -> SyncResult:
        """
        Create a beat-synced video from multiple sources.

        Integrates with the beat sync service.
        """
        sync_processor = BeatSyncProcessor(config=config)

        # Download videos using existing downloader
        local_videos = []
        for url in video_urls:
            path = self.download_video(url)  # Existing method
            local_videos.append(path)

        # Download audio
        local_audio = self.download_audio(audio_url)

        # Process
        result = sync_processor.process(
            audio_path=local_audio,
            video_paths=local_videos,
        )

        return result
```

---

## Usage Examples

### Basic Beat Detection

```python
from packages.beat_sync.src.beat_detector import BeatDetector

detector = BeatDetector(method="librosa")
beat_map = detector.detect("song.mp3", fps=30)

print(f"Tempo: {beat_map.tempo} BPM")
print(f"Total beats: {len(beat_map.beats)}")
print(f"First 10 beats: {beat_map.get_beat_times()[:10]}")
```

### Create Beat-Synced Video

```python
from packages.beat_sync.src.processor import BeatSyncProcessor
from packages.beat_sync.src.models import SyncConfig, SyncMode, TransitionStyle

config = SyncConfig(
    sync_mode=SyncMode.STRONG_BEATS,
    strength_threshold=0.6,
    transition_style=TransitionStyle.FADE,
)

processor = BeatSyncProcessor(config=config)
result = processor.process(
    audio_path="music.mp3",
    video_paths=["clip1.mp4", "clip2.mp4", "clip3.mp4"],
    output_path="output.mp4",
)

print(f"Created video with {result.total_cuts} cuts")
print(f"Processing time: {result.processing_time:.2f}s")
```

### API Usage

```bash
# Analyze beats
curl -X POST http://localhost:8000/beat-sync/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://example.com/song.mp3",
    "method": "librosa",
    "fps": 30
  }'

# Create beat-synced video
curl -X POST http://localhost:8000/beat-sync/create \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://example.com/song.mp3",
    "video_urls": [
      "https://example.com/clip1.mp4",
      "https://example.com/clip2.mp4"
    ],
    "config": {
      "sync_mode": "every_beat",
      "transition_style": "cut"
    }
  }'
```

---

## Performance Considerations

### Beat Detection

| Method | Speed | Accuracy | Memory |
|--------|-------|----------|--------|
| librosa | ~2-3x realtime | Good | Low |
| madmom | ~0.5-1x realtime | Excellent | Medium |
| hybrid | ~0.3x realtime | Best | Medium |

### Video Processing

- **MoviePy** processes at roughly 10-30 fps depending on resolution
- Use `preview_only=True` for quick iterations
- Pre-transcode source videos to consistent format
- Consider GPU acceleration with NVENC on Cloud GPU instances

### Recommended Cloud Run Specs

```yaml
# For production workloads
resources:
  limits:
    memory: "8Gi"
    cpu: "4"

# Timeout for long videos
timeout: 3600  # 1 hour

# Concurrency (CPU-bound work)
containerConcurrency: 1
```

---

## References

### Libraries
- [librosa Documentation](https://librosa.org/doc/0.11.0/tutorial.html)
- [madmom Documentation](https://madmom.readthedocs.io/)
- [MoviePy Documentation](https://zulko.github.io/moviepy/)
- [Essentia Documentation](https://essentia.upf.edu/)
- [aubio Documentation](https://aubio.org/)

### Tutorials & Articles
- [Beat Detection Models Comparison](https://biff.ai/a-rundown-of-open-source-beat-detection-models/)
- [Automated Video Editing with Python](https://medium.com/@jordy.bonnet_67692/automated-video-editing-based-on-music-rhythm-with-python-76420dac2e6f)
- [Audio Offline Analysis for Video Sync](https://github.com/kessoning/Audio-Offline-Analysis)
- [MoviePy GitHub](https://github.com/Zulko/moviepy)

### Related Projects
- [youtube-to-docs](https://github.com/DoIT-Artificial-Intelligence/youtube-to-docs) - Inspiration for video processing
- [automatic_video_editing](https://github.com/Winston-503/automatic_video_editing) - Python video automation

---

## Next Steps

1. **Approve Plan** - Review and approve this implementation plan
2. **Create Package** - Set up `packages/beat_sync` structure
3. **Prototype** - Build minimal beat detection + video cut demo
4. **Iterate** - Add features based on testing feedback
5. **Deploy** - Integrate with Adiyogi API and deploy to Cloud Run
