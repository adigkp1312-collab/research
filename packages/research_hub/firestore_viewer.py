"""Streamlit UI for Research Hub Firestore Data Viewer."""

import streamlit as st
import pandas as pd
from datetime import datetime
from google.cloud import firestore
from google.oauth2 import service_account
import json

# Page config
st.set_page_config(
    page_title="Research Hub Data Viewer",
    page_icon="🔬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Firestore
@st.cache_resource
def get_firestore_client():
    """Initialize Firestore client with credentials."""
    try:
        # Use service account from credentials.json
        creds = service_account.Credentials.from_service_account_file(
            '/Users/guptaaditya/Applications/langchain-poc/packages/research_hub/credentials.json'
        )
        return firestore.Client(credentials=creds, project='artful-striker-483214-b0')
    except Exception as e:
        st.error(f"Failed to connect to Firestore: {e}")
        return None

db = get_firestore_client()

# Sidebar
st.sidebar.title("🔬 Research Hub")
st.sidebar.info("View and explore your research data from Firestore")

# Main UI
st.title("Firestore Data Viewer")

if db is None:
    st.error("Cannot connect to Firestore. Check your credentials.")
    st.stop()

# Discover all collections
@st.cache_data(ttl=60)
def get_all_collections():
    """Get all collection names from Firestore."""
    collections = list(db.collections())
    return [c.id for c in collections]

collection_names = get_all_collections()

# Collection selector
st.sidebar.divider()
st.sidebar.subheader("Collections")
selected_collection = st.sidebar.selectbox(
    "Select Collection",
    collection_names if collection_names else ["No collections found"]
)

if not collection_names:
    st.warning("No collections found in Firestore database")
    st.stop()

# Tabs
tabs = st.tabs(["📊 Dashboard", "🔍 Entries", "� Search", "�📈 Analytics"])

# TAB 1: DASHBOARD
with tabs[0]:
    st.header(f"Overview: {selected_collection}")
    
    # Get stats
    try:
        entries_ref = db.collection(selected_collection)
        all_entries = list(entries_ref.stream())
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Documents", len(all_entries))
        
        with col2:
            # Count unique fields
            all_keys = set()
            for entry in all_entries:
                all_keys.update(entry.to_dict().keys())
            st.metric("Unique Fields", len(all_keys))
        
        with col3:
            # Average doc size
            if all_entries:
                avg_size = sum(len(str(e.to_dict())) for e in all_entries) / len(all_entries)
                st.metric("Avg Doc Size", f"{int(avg_size)} chars")
        
        # Recent activity
        st.divider()
        st.subheader("Recent Documents")
        
        recent = all_entries[:10] if len(all_entries) <= 10 else all_entries[-10:]
        
        for entry in recent:
            data = entry.to_dict()
            with st.expander(f"{entry.id[:20]}..."):
                st.json(data)
                
    except Exception as e:
        st.error(f"Error loading data: {e}")

# TAB 2: ENTRIES
with tabs[1]:
    st.header(f"All Documents: {selected_collection}")
    
    if not all_entries:
        st.info("No documents in this collection")
    else:
        # Quick filters
        st.subheader("Filters")
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            search_text = st.text_input("🔍 Search in documents", placeholder="Type to filter...")
        
        with col_f2:
            limit_docs = st.slider("Max documents to show", 10, 500, 100)
        
        # Apply search filter
        filtered_entries = all_entries[:limit_docs]
        
        if search_text:
            search_lower = search_text.lower()
            filtered_entries = [
                e for e in filtered_entries 
                if search_lower in json.dumps(e.to_dict(), default=str).lower()
            ]
        
        st.info(f"Showing {len(filtered_entries)} of {len(all_entries)} documents")
        
        # Display table
        df_data = []
        for entry in filtered_entries:
            data = entry.to_dict()
            row = {'ID': entry.id[:15] + '...'}
            # Add first 3 fields as preview
            for i, (key, val) in enumerate(list(data.items())[:3]):
                row[key] = str(val)[:30] + '...' if len(str(val)) > 30 else str(val)
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
        
        # Detail view
        st.divider()
        selected_idx = st.number_input("View entry details (row number)", min_value=0, max_value=len(filtered_entries)-1, value=0)
        
        if 0 <= selected_idx < len(filtered_entries):
            st.subheader("Entry Details")
            entry_data = filtered_entries[selected_idx].to_dict()
            st.json(entry_data)
            
            # Download button
            json_str = json.dumps(entry_data, indent=2, default=str)
            st.download_button(
                "💾 Download as JSON",
                json_str,
                file_name=f"{selected_collection}_{filtered_entries[selected_idx].id}.json",
                mime="application/json"
            )

# TAB 3: SEARCH
with tabs[2]:
    st.header("Advanced Search & Fetch")
    
    search_mode = st.radio("Search Mode", ["Fetch by ID", "Query by Field"])
    
    if search_mode == "Fetch by ID":
        st.subheader("Fetch Document by ID")
        doc_id = st.text_input("Enter Document ID", placeholder="e.g., 12345abcdef")
        
        if st.button("🔍 Fetch Document"):
            if doc_id:
                try:
                    doc_ref = db.collection(selected_collection).document(doc_id)
                    doc = doc_ref.get()
                    
                    if doc.exists:
                        st.success(f"✓ Found document: {doc_id}")
                        st.json(doc.to_dict())
                        
                        # Download option
                        json_str = json.dumps(doc.to_dict(), indent=2, default=str)
                        st.download_button(
                            "💾 Download",
                            json_str,
                            file_name=f"{selected_collection}_{doc_id}.json",
                            mime="application/json"
                        )
                    else:
                        st.warning(f"Document '{doc_id}' not found in collection '{selected_collection}'")
                except Exception as e:
                    st.error(f"Error fetching document: {e}")
            else:
                st.warning("Please enter a document ID")
    
    else:  # Query by Field
        st.subheader("Query by Field Value")
        
        # Get all field names from collection
        if all_entries:
            all_fields = set()
            for entry in all_entries:
                all_fields.update(entry.to_dict().keys())
            all_fields = sorted(list(all_fields))
            
            col_q1, col_q2 = st.columns(2)
            
            with col_q1:
                field_name = st.selectbox("Select Field", all_fields)
            
            with col_q2:
                field_value = st.text_input("Field Value")
            
            if st.button("🔎 Search"):
                if field_name and field_value:
                    try:
                        # Query Firestore
                        query = db.collection(selected_collection).where(field_name, "==", field_value)
                        results = list(query.stream())
                        
                        if results:
                            st.success(f"✓ Found {len(results)} matching document(s)")
                            
                            for i, doc in enumerate(results):
                                with st.expander(f"Result {i+1}: {doc.id}"):
                                    st.json(doc.to_dict())
                                    
                                    # Download option
                                    json_str = json.dumps(doc.to_dict(), indent=2, default=str)
                                    st.download_button(
                                        "💾 Download",
                                        json_str,
                                        file_name=f"{selected_collection}_{doc.id}.json",
                                        mime="application/json",
                                        key=f"download_{i}"
                                    )
                        else:
                            st.warning(f"No documents found where {field_name} = {field_value}")
                    except Exception as e:
                        st.error(f"Query error: {e}")
                else:
                    st.warning("Please select a field and enter a value")
        else:
            st.info("No documents in collection to query")

# TAB 3: ANALYTICS
with tabs[2]:
    st.header("Analytics")
    
    # Research type distribution
    st.subheader("Research Type Distribution")
    type_counts = pd.DataFrame(list(types.items()), columns=['Type', 'Count'])
    st.bar_chart(type_counts.set_index('Type'))
    
    # Timeline
    st.subheader("Research Timeline")
    timeline_data = []
    for entry in all_entries:
        data = entry.to_dict()
        created = data.get('created_at')
        if created:
            timeline_data.append({
                'Date': created.date() if hasattr(created, 'date') else created,
                'Count': 1
            })
    
    if timeline_data:
        timeline_df = pd.DataFrame(timeline_data).groupby('Date').sum().reset_index()
        st.line_chart(timeline_df.set_index('Date'))

# Footer
st.divider()
st.caption(f"Research Hub Data Viewer | Connected to Firestore | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
