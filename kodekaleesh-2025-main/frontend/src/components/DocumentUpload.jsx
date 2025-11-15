import React, { useState } from 'react';

export default function DocumentUpload({ onUpload, loading, progress }) {
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

    if (e.dataTransfer.files && e.dataTransfer.files.length) {
      onUpload(Array.from(e.dataTransfer.files));
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files.length) {
      onUpload(Array.from(e.target.files));
    }
  };

  return (
    <div className="upload-container" aria-live="polite">
      <div
        className={`upload-area ${dragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        role="button"
        aria-label="Upload area, drag and drop a file or browse"
      >
        <div className="upload-icon">📄</div>
        <h3>Drag & Drop Your Document or Image</h3>
        <p>or</p>
        <label className="upload-button">
          Browse Files
          <input
            type="file"
            multiple
            accept=".pdf,.txt,.docx,.jpg,.jpeg,.png,.bmp,.gif,.tiff"
            onChange={handleChange}
            disabled={loading}
            style={{ display: 'none' }}
          />
        </label>
        <p className="upload-hint">Supported: PDF, TXT, DOCX (text) | JPG, PNG, BMP, GIF, TIFF (with OCR)</p>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Processing document{progress?.total > 1 ? `s (${progress.done}/${progress.total})` : '...'} </p>
        </div>
      )}
    </div>
  );
}
