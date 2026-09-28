import React, { useRef, useState } from 'react';
import { UploadCloud, FileCheck, X, AlertCircle, FileText } from 'lucide-react';

export default function ResumeUploader({ file, setFile, error, setError }) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef(null);

  const validateAndSetFile = (selectedFile) => {
    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().endsWith('.pdf') && selectedFile.type !== 'application/pdf') {
      setError('Please upload a PDF file (.pdf only). Other formats are not supported.');
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File exceeds 10MB limit. Please upload a smaller PDF resume.');
      return;
    }

    setError(null);
    setFile(selectedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const removeFile = (e) => {
    e.stopPropagation();
    setFile(null);
    setError(null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes && bytes !== 0) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="card-box uploader-card">
      <div className="card-header">
        <div className="card-icon-badge">
          <FileText size={18} className="text-primary" />
        </div>
        <div>
          <h2 className="card-title">Upload Resume</h2>
          <p className="card-subtitle">Upload your current technical or professional resume in PDF</p>
        </div>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept=".pdf,application/pdf"
        onChange={handleFileChange}
        style={{ display: 'none' }}
        id="resume-file-input"
      />

      {!file ? (
        <div
          className={`dropzone ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => inputRef.current && inputRef.current.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && inputRef.current?.click()}
          id="resume-dropzone"
          aria-label="Upload resume dropzone"
        >
          <div className="dropzone-icon-wrapper">
            <UploadCloud className="dropzone-icon" size={32} />
          </div>
          <p className="dropzone-primary-text">Drag &amp; drop your PDF here</p>
          <p className="dropzone-hint">PDF &bull; Maximum 10 MB &bull; Ready for analysis</p>
          <button
            type="button"
            className="dropzone-btn"
            onClick={(e) => {
              e.stopPropagation();
              inputRef.current?.click();
            }}
          >
            Browse Files
          </button>
        </div>
      ) : (
        <div className="file-preview-card animate-fade-in">
          <div className="file-preview-icon">
            <FileCheck size={26} className="text-success" />
          </div>
          <div className="file-preview-info">
            <p className="file-name" title={file.name}>
              <span className="file-check-badge">✓</span> {file.name}
            </p>
            <p className="file-size">
              {formatFileSize(file.size)} &bull; PDF &bull; Ready to analyze
            </p>
          </div>
          <button
            type="button"
            className="file-remove-btn"
            onClick={removeFile}
            title="Remove uploaded resume"
            aria-label="Remove resume"
          >
            <X size={15} />
            <span>Remove</span>
          </button>
        </div>
      )}

      {error && (
        <div className="inline-error-banner animate-fade-in" role="alert">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
