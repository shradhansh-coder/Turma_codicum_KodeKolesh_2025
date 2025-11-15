import React, { useState } from 'react';

export default function DocumentUpload({ onUpload, loading }) {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  return (
    <div className="upload-container">
      <div
        className={`upload-area ${dragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="upload-icon">📄</div>
        <h3>Drag & Drop Your Document</h3>
        <p>or</p>
        <label className="upload-button">
          Browse Files
          <input
            type="file"
            accept=".pdf,.txt,.docx"
            onChange={handleChange}
            disabled={loading}
            style={{ display: 'none' }}
          />
        </label>
        <p className="upload-hint">Supported: PDF, TXT, DOCX (Max 50MB)</p>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Processing document...</p>
        </div>
      )}
    </div>
  );
}
