"""
Vertex AI Agent Builder (Discovery Engine) Datastore Manager.

Uses the correct production API: google.cloud.discoveryengine_v1

Team: AI/ML
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime

from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core import exceptions as google_exceptions
from google.protobuf import struct_pb2

from packages.core.src import GOOGLE_CLOUD_PROJECT, VERTEX_AI_LOCATION


# Configuration
DATASTORE_ID = os.environ.get('VERTEX_AI_DATASTORE_ID', '')
DATASTORE_LOCATION = os.environ.get('VERTEX_AI_DATASTORE_LOCATION', 'global')
DATASTORE_DISPLAY_NAME = os.environ.get('VERTEX_AI_DATASTORE_NAME', 'knowledge-base')


class DatastoreManager:
    """
    Manages Vertex AI Agent Builder datastores.
    
    Uses Discovery Engine API for:
    - Creating/managing datastores
    - Importing documents
    - Managing document lifecycle
    
    Usage:
        manager = DatastoreManager()
        manager.create_datastore("my-datastore", "My Knowledge Base")
        manager.import_documents("gs://bucket/documents/")
    """
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        datastore_id: Optional[str] = None,
    ):
        """
        Initialize datastore manager.
        
        Args:
            project_id: GCP project ID (defaults to env var)
            location: Datastore location (defaults to 'global')
            datastore_id: Existing datastore ID (defaults to env var)
        """
        self.project_id = project_id or GOOGLE_CLOUD_PROJECT
        self.location = location or DATASTORE_LOCATION
        self.datastore_id = datastore_id or DATASTORE_ID
        
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT not configured")
        
        # Initialize clients
        self._datastore_client = None
        self._document_client = None
    
    @property
    def datastore_client(self) -> discoveryengine.DataStoreServiceClient:
        """Lazy-load datastore client."""
        if self._datastore_client is None:
            self._datastore_client = discoveryengine.DataStoreServiceClient()
        return self._datastore_client
    
    @property
    def document_client(self) -> discoveryengine.DocumentServiceClient:
        """Lazy-load document client."""
        if self._document_client is None:
            self._document_client = discoveryengine.DocumentServiceClient()
        return self._document_client
    
    @property
    def parent(self) -> str:
        """Get parent resource path for collections."""
        return f"projects/{self.project_id}/locations/{self.location}/collections/default_collection"
    
    @property
    def datastore_path(self) -> str:
        """Get full datastore resource path."""
        if not self.datastore_id:
            raise ValueError("VERTEX_AI_DATASTORE_ID not configured")
        return f"{self.parent}/dataStores/{self.datastore_id}"
    
    def create_datastore(
        self,
        datastore_id: str,
        display_name: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new datastore.
        
        Args:
            datastore_id: Unique ID for the datastore
            display_name: Human-readable name
            description: Optional description
            
        Returns:
            Dictionary with datastore info
            
        Note:
            This is a long-running operation. The datastore may take
            a few minutes to become fully operational.
        """
        datastore = discoveryengine.DataStore(
            display_name=display_name,
            industry_vertical=discoveryengine.IndustryVertical.GENERIC,
            solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
            content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
        )
        
        try:
            operation = self.datastore_client.create_data_store(
                parent=self.parent,
                data_store=datastore,
                data_store_id=datastore_id,
            )
            
            # Wait for operation to complete
            result = operation.result(timeout=300)  # 5 minute timeout
            
            return {
                "datastore_id": datastore_id,
                "display_name": display_name,
                "status": "created",
                "resource_name": result.name,
            }
            
        except google_exceptions.AlreadyExists:
            return {
                "datastore_id": datastore_id,
                "display_name": display_name,
                "status": "already_exists",
            }
        except Exception as e:
            raise RuntimeError(f"Failed to create datastore: {str(e)}")
    
    def get_datastore_info(self) -> Dict[str, Any]:
        """
        Get information about the current datastore.
        
        Returns:
            Dictionary with datastore metadata
        """
        if not self.datastore_id:
            return {
                "configured": False,
                "message": "VERTEX_AI_DATASTORE_ID not set",
            }
        
        try:
            datastore = self.datastore_client.get_data_store(
                name=self.datastore_path
            )
            
            return {
                "configured": True,
                "datastore_id": self.datastore_id,
                "display_name": datastore.display_name,
                "project": self.project_id,
                "location": self.location,
                "resource_name": datastore.name,
                "create_time": datastore.create_time.isoformat() if datastore.create_time else None,
            }
            
        except google_exceptions.NotFound:
            return {
                "configured": True,
                "datastore_id": self.datastore_id,
                "status": "not_found",
                "message": f"Datastore '{self.datastore_id}' does not exist",
            }
        except Exception as e:
            return {
                "configured": True,
                "datastore_id": self.datastore_id,
                "status": "error",
                "message": str(e),
            }
    
    def list_datastores(self) -> List[Dict[str, Any]]:
        """
        List all datastores in the project.
        
        Returns:
            List of datastore info dictionaries
        """
        try:
            datastores = self.datastore_client.list_data_stores(
                parent=self.parent
            )
            
            return [
                {
                    "datastore_id": ds.name.split("/")[-1],
                    "display_name": ds.display_name,
                    "create_time": ds.create_time.isoformat() if ds.create_time else None,
                }
                for ds in datastores
            ]
            
        except Exception as e:
            print(f"Warning: Failed to list datastores: {e}")
            return []
    
    def import_documents(
        self,
        gcs_uri: str,
        reconciliation_mode: str = "INCREMENTAL",
    ) -> Dict[str, Any]:
        """
        Import documents from GCS to the datastore.
        
        Args:
            gcs_uri: GCS URI (gs://bucket/path/) or specific file
            reconciliation_mode: INCREMENTAL or FULL
            
        Returns:
            Import operation status
        """
        request = discoveryengine.ImportDocumentsRequest(
            parent=f"{self.datastore_path}/branches/default_branch",
            gcs_source=discoveryengine.GcsSource(
                input_uris=[gcs_uri],
                data_schema="content",
            ),
            reconciliation_mode=getattr(
                discoveryengine.ImportDocumentsRequest.ReconciliationMode,
                reconciliation_mode,
            ),
        )
        
        try:
            operation = self.document_client.import_documents(request=request)
            
            # Return immediately - import runs async
            return {
                "status": "importing",
                "operation_name": operation.operation.name,
                "gcs_uri": gcs_uri,
                "message": "Document import started. This may take several minutes.",
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "gcs_uri": gcs_uri,
            }
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the datastore.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if deleted successfully
        """
        document_name = f"{self.datastore_path}/branches/default_branch/documents/{document_id}"
        
        try:
            self.document_client.delete_document(name=document_name)
            return True
        except google_exceptions.NotFound:
            return False
        except Exception as e:
            raise RuntimeError(f"Failed to delete document: {str(e)}")


# Convenience functions for backward compatibility
def init_datastore() -> None:
    """Initialize datastore connection (deprecated - use DatastoreManager)."""
    manager = DatastoreManager()
    # Just verify connection works
    manager.get_datastore_info()


def get_datastore_info() -> Dict[str, Any]:
    """Get datastore info (convenience function)."""
    manager = DatastoreManager()
    return manager.get_datastore_info()


def list_datastores() -> List[Dict[str, Any]]:
    """List datastores (convenience function)."""
    manager = DatastoreManager()
    return manager.list_datastores()
