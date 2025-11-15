import React from 'react';

export default function DocumentList({ documents, onSelect, onDelete }) {
  if (documents.length === 0) {
    return (
      <div className="empty-state">
        <p>No documents yet. Upload one to get started!</p>
      </div>
    );
  }

  return (
    <div className="document-list">
      <table className="documents-table">
        <thead>
          <tr>
            <th>Filename</th>
            <th>Date Uploaded</th>
            <th>Size (chars)</th>
            <th>Pages</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id} className="doc-row">
              <td className="doc-name">{doc.filename}</td>
              <td>{new Date(doc.created_at).toLocaleDateString()}</td>
              <td>{doc.text_length.toLocaleString()}</td>
              <td>{doc.pages}</td>
              <td className="doc-actions">
                <button
                  className="btn-primary"
                  onClick={() => onSelect(doc)}
                >
                  View
                </button>
                <button
                  className="btn-danger"
                  onClick={() => onDelete(doc.id)}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
