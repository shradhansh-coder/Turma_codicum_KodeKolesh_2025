import React from 'react';

export default function SummaryPanel({ document, summary, onClose }) {
  return (
    <div className="summary-panel">
      <div className="panel-header">
        <h3>{document.filename}</h3>
        <button className="btn-close" onClick={onClose}>✕</button>
      </div>

      <div className="summary-content">
        <div className="info-section">
          <h4>Document Info</h4>
          <p><strong>ID:</strong> {document.id}</p>
          <p><strong>Date:</strong> {new Date(document.created_at).toLocaleString()}</p>
          <p><strong>Size:</strong> {document.text_length.toLocaleString()} characters</p>
          <p><strong>Pages:</strong> {document.pages}</p>
        </div>

        <div className="summary-section">
          <h4>Summary</h4>
          <div className="summary-text">
            {summary}
          </div>
        </div>
      </div>
    </div>
  );
}
