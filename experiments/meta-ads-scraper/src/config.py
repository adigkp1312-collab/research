"""Configuration management for Meta Ad Library Scraper."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
TEMP_DIR = BASE_DIR / "temp"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# GCS Configuration
GCS_BUCKET = os.getenv("GCS_BUCKET", "metaadsscrapper")
GCS_PROJECT = os.getenv("GCS_PROJECT", "artful-striker-483214-b0")
GCS_PREFIX = "meta-ads"

# Supabase Configuration (for auth)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Scraper settings
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "US")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "3"))
DOWNLOAD_DELAY = float(os.getenv("DOWNLOAD_DELAY", "2"))

# Database
DATABASE_PATH = DATA_DIR / "ads.db"

# Meta Ad Library URL
AD_LIBRARY_URL = "https://www.facebook.com/ads/library"
