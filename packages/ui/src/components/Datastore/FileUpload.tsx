/**
 * File Upload Component
 * 
 * Drag-and-drop file upload with progress tracking.
 * 
 * Team: Frontend
 */

import React, { useState, useCallback } from 'react';
import { datastoreApi, FileMetadata } from '../../services/datastoreApi';

interface FileUploadProps {
  onUploadComplete?: (file: FileMetadata) => void;
  onError?: (error: Error) => void;
}

const ALLOWED_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
  'text/markdown',
  'text/html',
];

const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt', '.md', '.html', '.htm'];

export const FileUpload: React.FC<FileUploadProps> = ({
  onUploadComplete,
  onError,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [description, setDescription] = useState('');

  const validateFile = (file: File): boolean => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    return (
      ALLOWED_TYPES.includes(file.type) ||
      ALLOWED_EXTENSIONS.some((allowed) => ext === allowed)
    );
  };

  const handleUpload = useCallback(
    async (file: File) => {
      if (!validateFile(file)) {
        const error = new Error(
          `File type not supported. Allowed: ${ALLOWED_EXTENSIONS.join(', ')}`
        );
        onError?.(error);
        return;
      }

      setUploading(true);
      setProgress(0);

      try {
        const result = await datastoreApi.uploadFile(
          file,
          description || undefined,
          (prog) => setProgress(prog)
        );
        onUploadComplete?.(result);
        setDescription('');
        setProgress(0);
      } catch (error) {
        onError?.(error as Error);
      } finally {
        setUploading(false);
      }
    },
    [description, onUploadComplete, onError]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const file = e.dataTransfer.files[0];
      if (file) {
        handleUpload(file);
      }
    },
    [handleUpload]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        handleUpload(file);
      }
    },
    [handleUpload]
  );

  return (
    <div
      style={{
        border: `2px dashed ${isDragging ? '#4CAF50' : '#ccc'}`,
        borderRadius: '8px',
        padding: '40px',
        textAlign: 'center',
        backgroundColor: isDragging ? '#f0f8f0' : '#fafafa',
        transition: 'all 0.3s',
        marginBottom: '20px',
      }}
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      {uploading ? (
        <div>
          <div>Uploading... {Math.round(progress)}%</div>
          <div
            style={{
              width: '100%',
              height: '8px',
              backgroundColor: '#e0e0e0',
              borderRadius: '4px',
              marginTop: '10px',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                width: `${progress}%`,
                height: '100%',
                backgroundColor: '#4CAF50',
                transition: 'width 0.3s',
              }}
            />
          </div>
        </div>
      ) : (
        <>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📄</div>
          <div style={{ marginBottom: '16px' }}>
            <strong>Drag and drop a file here, or click to select</strong>
          </div>
          <input
            type="file"
            onChange={handleFileInput}
            accept={ALLOWED_EXTENSIONS.join(',')}
            style={{ display: 'none' }}
            id="file-upload-input"
          />
          <label
            htmlFor="file-upload-input"
            style={{
              display: 'inline-block',
              padding: '10px 20px',
              backgroundColor: '#2196F3',
              color: 'white',
              borderRadius: '4px',
              cursor: 'pointer',
              marginBottom: '16px',
            }}
          >
            Select File
          </label>
          <div style={{ marginTop: '16px' }}>
            <input
              type="text"
              placeholder="Optional description..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              style={{
                width: '100%',
                maxWidth: '400px',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #ccc',
              }}
            />
          </div>
          <div style={{ fontSize: '12px', color: '#666', marginTop: '8px' }}>
            Supported: PDF, DOCX, TXT, MD, HTML
          </div>
        </>
      )}
    </div>
  );
};

export default FileUpload;
