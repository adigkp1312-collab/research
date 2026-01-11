"""Test Firestore connection and check for data."""

from google.cloud import firestore
from google.oauth2 import service_account

try:
    # Load credentials
    creds = service_account.Credentials.from_service_account_file(
        '/Users/guptaaditya/Applications/langchain-poc/packages/research_hub/credentials.json'
    )
    
    # Create client
    db = firestore.Client(credentials=creds, project='artful-striker-483214-b0')
    
    print("✓ Successfully connected to Firestore")
    print(f"  Project: artful-striker-483214-b0")
    
    # Check the collection
    collection_name = 'research_hub_entries'
    print(f"\n Checking collection: {collection_name}")
    
    entries_ref = db.collection(collection_name)
    docs = list(entries_ref.limit(10).stream())
    
    print(f"\n✓ Found {len(docs)} documents")
    
    if docs:
        print("\nFirst document:")
        first_doc = docs[0]
        print(f"  ID: {first_doc.id}")
        print(f"  Data: {first_doc.to_dict()}")
    else:
        print("\n⚠ No documents found in collection!")
        print("\nLet's check all collections:")
        collections = db.collections()
        for collection in collections:
            print(f"  - {collection.id}")
            
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
