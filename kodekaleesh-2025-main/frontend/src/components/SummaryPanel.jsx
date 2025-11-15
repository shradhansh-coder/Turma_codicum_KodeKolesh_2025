import React from 'react';

export default function SummaryPanel({ document, summary, onClose }) {
  if (!document) {
    return null;
  }

  return (
    <div className="summary-panel">
      <div className="panel-header">
        <h3>{document.filename || 'Document'}</h3>
        <button className="btn-close" onClick={onClose}>✕</button>
      </div>

      <div className="summary-content">
        <div className="info-section">
          <h4>Document Info</h4>
          <p><strong>ID:</strong> {document.id || 'N/A'}</p>
          <p><strong>Date:</strong> {document.created_at ? new Date(document.created_at).toLocaleString() : 'N/A'}</p>
          <p><strong>Size:</strong> {document.text_length ? document.text_length.toLocaleString() : 0} characters</p>
          <p><strong>Pages:</strong> {document.pages || 0}</p>
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
