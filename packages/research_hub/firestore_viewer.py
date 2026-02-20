"""
Premium Firestore Data Viewer for Research Hub & Meta Ads.
Features: Glassmorphism UI, Media Gallery, Advanced Filtering.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, date
from google.cloud import firestore
from google.oauth2 import service_account
from typing import Dict, Any, List, Optional

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Adiyogi Analytics Hub",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PREMIUM CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Glassmorphism Effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 20px;
        margin-bottom: 20px;
    }

    /* Gradient Header */
    .main-header {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }

    /* Metric Styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
        color: #6366f1;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        color: #4b5563;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #6366f1 !important;
        border-bottom: 2px solid #6366f1 !important;
    }
    
    /* Media Wrapper */
    .media-container {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE FIRESTORE ---
@st.cache_resource
def get_firestore_client():
    """Initialize Firestore client with credentials."""
    try:
        # 1. Try environment variable for credential path
        cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        
        # 2. Try local folder paths
        if not cred_path:
            possible_paths = [
                './credentials.json',
                '/Users/guptaaditya/Applications/langchain-poc/packages/research_hub/credentials.json',
                '/app/credentials.json'
            ]
            for p in possible_paths:
                if os.path.exists(p):
                    cred_path = p
                    break
        
        if cred_path:
            creds = service_account.Credentials.from_service_account_file(cred_path)
            return firestore.Client(credentials=creds, project='project-9881b278-0a45-47c1-9ed')
        else:
            # 3. Fallback to default credentials (works index-box in Cloud Run)
            return firestore.Client(project='project-9881b278-0a45-47c1-9ed')
    except Exception as e:
        st.error(f"Failed to connect to Firestore: {e}")
        return None

db = get_firestore_client()

# --- HELPER FUNCTIONS ---
def parse_date(val: Any) -> Optional[datetime]:
    if isinstance(val, datetime):
        return val
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val.replace('Z', '+00:00'))
        except:
            pass
    return None

@st.cache_data(ttl=300)
def fetch_collection_schema(collection_name: str) -> List[str]:
    """Get unique fields for filtering."""
    if not db: return []
    docs = list(db.collection(collection_name).limit(50).stream())
    fields = set()
    for doc in docs:
        fields.update(doc.to_dict().keys())
    return sorted(list(fields))

def render_media(data: Dict[str, Any]):
    """Render media if found in document data."""
    media_found = False
    
    # Check for direct video url
    video_url = data.get('video_url_original') or data.get('video_url')
    if not video_url and data.get('video_urls'):
        video_url = data['video_urls'][0] if isinstance(data['video_urls'], list) else data['video_urls']
        
    if video_url and isinstance(video_url, str) and video_url.startswith('http'):
        st.video(video_url)
        media_found = True
        
    # Check for images
    img_url = data.get('snapshot_url') or data.get('image_url')
    if not img_url and data.get('image_urls'):
        img_url = data['image_urls'][0] if isinstance(data['image_urls'], list) else data['image_urls']
        
    if img_url and isinstance(img_url, str) and img_url.startswith('http') and not media_found:
        st.image(img_url, use_container_width=True)
        media_found = True
        
    if not media_found:
        st.info("No preview available for this document.")

# --- SIDEBAR: NAVIGATION ---
st.sidebar.title("🔮 Adiyogi Hub")
st.sidebar.markdown("---")

if db:
    collections = [c.id for c in db.collections()]
    selected_col = st.sidebar.selectbox("📂 Select Collection", collections, index=collections.index('videos') if 'videos' in collections else 0)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("General Filters")
    sort_order = st.sidebar.radio("Sort by Created At", ["Newest First", "Oldest First"])
    limit = st.sidebar.slider("Records to Fetch", 10, 500, 100)
else:
    st.stop()

# --- DATA FETCHING ---
@st.cache_data(ttl=60)
def fetch_data(col_name: str, sort_desc: bool, row_limit: int) -> List[Dict[str, Any]]:
    ref = db.collection(col_name)
    # Note: Sorting requires index in Firestore. We'll fallback to client-side sort if needed.
    # For now, let's try client-side to avoid index creation errors.
    docs = list(ref.limit(row_limit * 5).stream()) # Fetch more for filtering/sorting
    data = []
    for d in docs:
        item = d.to_dict()
        item['_id'] = d.id
        data.append(item)
    
    # Dynamic sort by common date fields
    date_fields = ['created_at', 'updated_at', 'timestamp', 'start_date']
    def get_sort_key(x):
        for f in date_fields:
            if f in x:
                dt = parse_date(x[f])
                if dt: return dt
        return datetime.min
    
    data.sort(key=get_sort_key, reverse=sort_desc)
    return data[:row_limit]

all_data = fetch_data(selected_col, sort_order == "Newest First", limit)

# --- MAIN UI ---
st.markdown(f'<div class="main-header">{selected_col.replace("_", " ").title()} Explorer</div>', unsafe_allow_html=True)

tabs = st.tabs(["📊 Dashboard", "🔍 Grid View", "🖼️ Media Gallery", "🔎 Advance Search"])

# TAB 1: DASHBOARD
with tabs[0]:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Docs (Sampled)", len(all_data))
    with col2:
        projects = len(set([d.get('project_id', 'N/A') for d in all_data]))
        st.metric("Active Projects", projects)
    with col3:
        status_counts = pd.Series([d.get('status', 'unknown') for d in all_data]).value_counts()
        st.metric("Completed Ratio", f"{int(status_counts.get('downloaded', 0) / len(all_data) * 100 if all_data else 0)}%")
    with col4:
        st.metric("Available Fields", len(fetch_collection_schema(selected_col)))

    st.markdown("### Status Breakdown")
    st.bar_chart(status_counts)

# TAB 2: GRID VIEW
with tabs[1]:
    st.markdown("### Data Explorer")
    
    # Smart Search in Tab
    search_q = st.text_input("⚡ Quick Filter (Search any field)", "")
    
    display_data = all_data
    if search_q:
        search_q = search_q.lower()
        display_data = [d for d in all_data if any(search_q in str(v).lower() for v in d.values())]
    
    if display_data:
        df = pd.DataFrame(display_data).drop(columns=['_id'])
        # Reorder to keep important bits first
        cols = df.columns.tolist()
        important = ['id', 'page_name', 'status', 'created_at', 'keyword', 'country']
        cols = [c for c in important if c in cols] + [c for c in cols if c not in important]
        st.dataframe(df[cols], use_container_width=True)
        
        st.markdown("---")
        inspect_id = st.selectbox("Select Record to Inspect", [d['_id'] for d in display_data])
        item = next(d for d in display_data if d['_id'] == inspect_id)
        
        det_col1, det_col2 = st.columns([1, 1])
        with det_col1:
            st.json(item)
        with det_col2:
            st.markdown("#### Document Assets")
            render_media(item)
    else:
        st.warning("No data matching your search criteria.")

# TAB 3: MEDIA GALLERY
with tabs[2]:
    st.markdown("### Visual Archive")
    media_items = [d for d in all_data if any(k in d for k in ['video_url_original', 'video_urls', 'snapshot_url', 'image_urls'])]
    
    if not media_items:
        st.info("No media found in the current sample.")
    else:
        # 3-column grid for media
        cols_per_row = 3
        for i in range(0, len(media_items), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < len(media_items):
                    item = media_items[i+j]
                    with cols[j]:
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        st.caption(f"ID: {item['_id'][:10]}... | {item.get('page_name', 'N/A')}")
                        render_media(item)
                        if st.button("View JSON", key=f"btn_{item['_id']}"):
                            st.json(item)
                        st.markdown('</div>', unsafe_allow_html=True)

# TAB 4: ADVANCE SEARCH
with tabs[3]:
    st.markdown("### Search & Query")
    
    search_mode = st.radio("Search Mode", ["Fetch by Exact ID", "Filter by Date Range"], horizontal=True)
    
    if search_mode == "Fetch by Exact ID":
        id_input = st.text_input("Enter Document ID")
        if st.button("Retrieve"):
            doc = db.collection(selected_col).document(id_input).get()
            if doc.exists:
                st.success("Found document!")
                st.json(doc.to_dict())
                render_media(doc.to_dict())
            else:
                st.error("Document not found.")
    
    else:
        st.subheader("Time Warp")
        start_date = st.date_input("From", date(2025, 1, 1))
        end_date = st.date_input("To", date.today())
        
        if st.button("Apply Date Filter"):
            # Client-side date filter for simplicity
            range_data = []
            for d in all_data:
                dt = parse_date(d.get('created_at'))
                if dt and start_date <= dt.date() <= end_date:
                    range_data.append(d)
            
            if range_data:
                st.success(f"Found {len(range_data)} records in range.")
                st.dataframe(pd.DataFrame(range_data))
            else:
                st.info("No records in this date range.")

# --- FOOTER ---
st.markdown("---")
st.caption(f"Connected to Firestore: project-9881b278-0a45-47c1-9ed | Collection: {selected_col}")
