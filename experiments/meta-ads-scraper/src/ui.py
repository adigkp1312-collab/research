"""Streamlit UI for Meta Ad Library Scraper."""

import os
import time
import pandas as pd
import streamlit as st
from datetime import datetime
from pathlib import Path

from src import database, scraper, downloader, storage, config, cloud_sync
from supabase import create_client, Client

# Page config
st.set_page_config(
    page_title="Meta Ad Library Scraper",
    page_icon="🎥",
    layout="wide"
)

# Initialize cloud sync on startup
if 'db_synced' not in st.session_state:
    cloud_sync.download_db()
    st.session_state.db_synced = True

def run_auth_check():
    """Check if user is authenticated with Supabase."""
    # Local dev fallback if not configured
    if not config.SUPABASE_URL or not config.SUPABASE_ANON_KEY:
        # If we are in Cloud Run, this is an error
        if os.getenv("K_SERVICE"):
            st.error("Supabase configuration missing in Cloud environment.")
            st.stop()
        return True

    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if st.session_state['authenticated']:
        return True

    # Login UI
    st.container()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("# 🔐 Meta Scraper Login")
        st.info("Please enter your credentials to access the scraper.")
        email = st.text_input("Email", placeholder="admin@example.com")
        password = st.text_input("Password", type="password")
        
        if st.button("🚀 Login"):
            try:
                supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)
                supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state['authenticated'] = True
                st.success("Login successful!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {e}")
    
    st.stop()
    return False

# Enforce Auth
run_auth_check()

# Custom CSS for modern look
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .status-pending { color: #f39c12; }
    .status-downloaded { color: #27ae60; }
    .status-failed { color: #e74c3c; }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🎥 Meta Scraper")
st.sidebar.info("Search, collect, and download Meta Ad Library videos to GCS.")

# Stats in sidebar
stats = database.get_stats()
st.sidebar.divider()
st.sidebar.subheader("System Stats")
st.sidebar.metric("Total Ads", stats['total'])
st.sidebar.metric("Pending", stats['pending'])
st.sidebar.metric("Downloaded", stats['downloaded'])
st.sidebar.metric("Failed", stats['failed'])

# User Info & Logout
if st.session_state.get('authenticated'):
    st.sidebar.divider()
    if st.sidebar.button("🔓 Logout"):
        st.session_state['authenticated'] = False
        st.rerun()

# Cloud Sync Controls
st.sidebar.divider()
st.sidebar.subheader("Persistence")
is_cloud = os.getenv("K_SERVICE") is not None
st.sidebar.write(f"Mode: {'☁️ Cloud' if is_cloud else '💻 Local'}")

if st.sidebar.button("🔄 Sync with GCS"):
    with st.sidebar.status("Syncing DB...", expanded=False):
        cloud_sync.upload_db()
        st.success("Uploaded to GCS!")
        time.sleep(1)
        st.rerun()

# Main Tabs
tabs = st.tabs(["🔍 Search & Collect", "📥 Downloads", "📊 Dashboard"])

# TAB 1: SEARCH & COLLECT
with tabs[0]:
    st.header("Search Meta Ad Library")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Enter Search Term (Keyword, Brand, or URL)", placeholder="e.g. nike running shoes")
    with col2:
        country = st.selectbox("Country", ["US", "IN", "GB", "CA", "AU", "DE", "FR"], index=0)
    
    limit = st.number_input("Max Ads to Collect", min_value=1, max_value=500, value=50)
    
    if st.button("🚀 Start Collection", key="start_collection_btn"):
        if not query:
            st.error("Please enter a search term.")
        else:
            # Show immediate feedback that button was clicked
            status_container = st.container()
            with status_container:
                st.info("⏳ Button clicked - starting scraper...")

            try:
                st.write(f"🔍 Querying Meta for '{query}' in {country}...")
                st.write(f"📊 Limit: {limit} ads, Headless: True")

                # Import check
                st.write("✓ Imports OK")

                # Actually run the scraper
                ads = scraper.collect_ads(query, country, limit, headless=True)

                st.write(f"✅ Successfully collected {len(ads)} ads.")

                # Auto-sync to GCS after collection if in cloud
                if os.getenv("K_SERVICE"):
                    st.write("☁️ Syncing changes to cloud storage...")
                    cloud_sync.upload_db()

                st.success(f"🎉 Added {len(ads)} ads to the queue!")

            except Exception as e:
                import traceback
                st.error(f"❌ Scraper failed: {str(e)}")
                st.code(traceback.format_exc(), language="python")

# TAB 2: DOWNLOADS
with tabs[1]:
    st.header("Video Queue & GCS Sync")
    
    pending_count = stats['pending']
    
    if pending_count > 0:
        st.warning(f"You have {pending_count} videos pending download.")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            workers = st.slider("Parallel Workers", 1, 5, 2)
        with col_btn2:
            st.write("") # Padding
            if st.button("📥 Start GCS Download Process"):
                st.info("Starting background download task...")
                
                # We use a placeholder for progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Process videos
                results = downloader.download_videos(workers=workers, limit=None, headless=True)
                
                # Auto-sync to GCS after download
                if os.getenv("K_SERVICE"):
                    cloud_sync.upload_db()
                
                st.success(f"Finished! Success: {results['success']}, Failed: {results['failed']}")
                st.rerun()
    else:
        st.success("All videos in queue have been processed!")

    # Show Recent Data
    st.divider()
    st.subheader("Recent Ads")
    data = database.export_data()
    if data:
        df = pd.DataFrame(data)
        # Reorder and filter columns for display
        display_cols = ['id', 'search_term', 'advertiser_name', 'status', 'gcs_path', 'downloaded_at']
        st.dataframe(df[display_cols], use_container_width=True)
    else:
        st.info("No ads in database yet.")

# TAB 3: DASHBOARD
with tabs[2]:
    st.header("Archive Analytics")

    # Re-fetch data for dashboard
    dashboard_data = database.export_data()

    if dashboard_data and len(dashboard_data) > 0:
        df = pd.DataFrame(dashboard_data)

        # Row 1: Status Distribution
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Status Breakdown")
            if 'status' in df.columns and df['status'].notna().any():
                status_counts = df['status'].value_counts().reset_index()
                status_counts.columns = ['status', 'count']
                st.bar_chart(status_counts, x='status', y='count')
            else:
                st.info("No status data available yet.")

        with c2:
            st.subheader("Top Search Terms")
            if 'search_term' in df.columns and df['search_term'].notna().any():
                search_counts = df['search_term'].value_counts().reset_index()
                search_counts.columns = ['search_term', 'count']
                st.bar_chart(search_counts, x='search_term', y='count')
            else:
                st.info("No search data available yet.")

        # Row 2: File Size Info
        st.divider()
        st.subheader("Storage Info")
        if 'file_size_bytes' in df.columns and df['file_size_bytes'].notna().any():
            total_size_mb = df['file_size_bytes'].fillna(0).sum() / (1024 * 1024)
        else:
            total_size_mb = 0.0
        st.metric("Total GCS Storage Used", f"{total_size_mb:.2f} MB")

        # Export section - show data preview instead of download button (avoids Cloud Run 404 issues)
        st.divider()
        st.subheader("Export Data")
        st.text("Copy from table above or use CLI: python -m src.cli export --format csv")
    else:
        st.info("No data yet. Start a search in the 'Search & Collect' tab to see analytics.")

# Footer
st.divider()
st.caption(f"Meta Ad Library Scraper v1.0 | Dashboard Local Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
