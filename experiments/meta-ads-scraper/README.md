# Meta Ad Library Video Scraper

Search and download video ads from Meta (Facebook/Instagram) Ad Library, with automatic upload to Google Cloud Storage.

## Features

- 🔍 Search by keyword, product name, or company
- 📥 Bulk download video ads (handles 100s of videos)
- ☁️ Automatic upload to GCS
- 🔄 Resumable downloads
- 📊 SQLite metadata for analysis

## Setup

### 1. Install Dependencies

```bash
cd /Users/guptaaditya/Applications/meta-ad-library-scraper
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Set up GCS credentials

Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to your service account JSON.

## Usage

```bash
# Collect ad URLs from search
python -m src.cli collect "nike shoes" --country US

# Download and upload videos
python -m src.cli download --workers 3

# Resume interrupted downloads
python -m src.cli download --resume

# Export metadata
python -m src.cli export --format json
```

## Data Storage

- **Videos**: `gs://metaadsscrapper/meta-ads/{search_term}/{ad_id}.mp4`
- **Metadata**: `data/ads.db` (SQLite)
