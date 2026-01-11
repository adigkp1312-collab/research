/**
 * Datastore API Service
 * 
 * Backend API communication for datastore management.
 * 
 * Team: Frontend
 */

import { CONFIG } from '../config';

export interface FileMetadata {
  id: string;
  name: string;
  type: string;
  size: number;
  gcs_uri?: string;
  chunks: number;
  uploaded_at: string;
  description?: string;
  status: string;
}

export interface DatastoreInfo {
  datastore_id: string;
  display_name: string;
  description: string;
  project: string;
  location: string;
  configured: boolean;
}

export interface SearchRequest {
  query: string;
  top_k?: number;
  filters?: Record<string, any>;
}

export interface SearchResponse {
  results: Array<Record<string, any>>;
  query: string;
  top_k: number;
}

export interface DatastoreStats {
  file_count: number;
  total_size: number;
  datastore_info: DatastoreInfo;
}

export const datastoreApi = {
  /**
   * Get datastore information.
   */
  async getDatastoreInfo(): Promise<DatastoreInfo> {
    const response = await fetch(`${CONFIG.API_URL}/datastore`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return response.json();
  },

  /**
   * List all uploaded files.
   */
  async listFiles(limit = 100, offset = 0, fileType?: string): Promise<FileMetadata[]> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    if (fileType) {
      params.append('file_type', fileType);
    }
    
    const response = await fetch(`${CONFIG.API_URL}/datastore/files?${params}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return response.json();
  },

  /**
   * Upload a file.
   */
  async uploadFile(
    file: File,
    description?: string,
    onProgress?: (progress: number) => void
  ): Promise<FileMetadata> {
    const formData = new FormData();
    formData.append('file', file);
    if (description) {
      formData.append('description', description);
    }

    const xhr = new XMLHttpRequest();
    
    return new Promise((resolve, reject) => {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          const progress = (e.loaded / e.total) * 100;
          onProgress(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(JSON.parse(xhr.responseText));
        } else {
          reject(new Error(`Upload failed: ${xhr.status}`));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Upload failed'));
      });

      xhr.open('POST', `${CONFIG.API_URL}/datastore/files`);
      xhr.send(formData);
    });
  },

  /**
   * Get file metadata by ID.
   */
  async getFile(fileId: string): Promise<FileMetadata> {
    const response = await fetch(`${CONFIG.API_URL}/datastore/files/${fileId}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return response.json();
  },

  /**
   * Preview file content.
   */
  async previewFile(fileId: string, maxLength = 1000): Promise<{ preview: string }> {
    const response = await fetch(
      `${CONFIG.API_URL}/datastore/files/${fileId}/preview?max_length=${maxLength}`
    );
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return response.json();
  },

  /**
   * Delete a file.
   */
  async deleteFile(fileId: string): Promise<void> {
    const response = await fetch(`${CONFIG.API_URL}/datastore/files/${fileId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
  },

  /**
   * Search the datastore.
   */
  async searchDatastore(request: SearchRequest): Promise<SearchResponse> {
    const response = await fetch(`${CONFIG.API_URL}/datastore/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return response.json();
  },

  /**
   * Get datastore statistics.
   */
  async getStats(): Promise<DatastoreStats> {
    const response = await fetch(`${CONFIG.API_URL}/datastore/stats`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return response.json();
  },
};

export default datastoreApi;
