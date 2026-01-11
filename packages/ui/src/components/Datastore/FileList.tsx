/**
 * File List Component
 * 
 * Displays list of uploaded files with metadata and actions.
 * 
 * Team: Frontend
 */

import React, { useState, useEffect } from 'react';
import { datastoreApi, FileMetadata } from '../../services/datastoreApi';

interface FileListProps {
  onFileSelect?: (file: FileMetadata) => void;
  onFileDelete?: (fileId: string) => void;
}

export const FileList: React.FC<FileListProps> = ({
  onFileSelect,
  onFileDelete,
}) => {
  const [files, setFiles] = useState<FileMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('');

  const loadFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const fileList = await datastoreApi.listFiles();
      setFiles(fileList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load files');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  const handleDelete = async (fileId: string) => {
    if (!confirm('Are you sure you want to delete this file?')) {
      return;
    }

    try {
      await datastoreApi.deleteFile(fileId);
      setFiles(files.filter((f) => f.id !== fileId));
      onFileDelete?.(fileId);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete file');
    }
  };

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString();
  };

  const filteredFiles = filter
    ? files.filter(
        (f) =>
          f.name.toLowerCase().includes(filter.toLowerCase()) ||
          f.type.toLowerCase().includes(filter.toLowerCase())
      )
    : files;

  if (loading) {
    return <div>Loading files...</div>;
  }

  if (error) {
    return <div style={{ color: 'red' }}>Error: {error}</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: '16px' }}>
        <input
          type="text"
          placeholder="Search files..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            borderRadius: '4px',
            border: '1px solid #ccc',
          }}
        />
      </div>

      {filteredFiles.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          {filter ? 'No files match your search' : 'No files uploaded yet'}
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '12px' }}>
          {filteredFiles.map((file) => (
            <div
              key={file.id}
              style={{
                border: '1px solid #ddd',
                borderRadius: '8px',
                padding: '16px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                backgroundColor: '#fff',
              }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                  {file.name}
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>
                  {file.type.toUpperCase()} • {formatSize(file.size)} •{' '}
                  {file.chunks} chunks • {formatDate(file.uploaded_at)}
                </div>
                {file.description && (
                  <div style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
                    {file.description}
                  </div>
                )}
              </div>
              <div>
                <button
                  onClick={() => onFileSelect?.(file)}
                  style={{
                    padding: '6px 12px',
                    marginRight: '8px',
                    backgroundColor: '#2196F3',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  View
                </button>
                <button
                  onClick={() => handleDelete(file.id)}
                  style={{
                    padding: '6px 12px',
                    backgroundColor: '#f44336',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileList;
