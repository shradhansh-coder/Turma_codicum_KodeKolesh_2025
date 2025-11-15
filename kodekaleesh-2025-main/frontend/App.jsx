import React, { useState, useEffect } from 'react';
import './App.css';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import SearchPanel from './components/SearchPanel';
import SummaryPanel from './components/SummaryPanel';

function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [summary, setSummary] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('upload');

  const API_BASE = 'http://localhost:5000/api';

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${API_BASE}/documents`);
      const data = await response.json();
      if (data.success) {
        setDocuments(data.documents);
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleUpload = async (file) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (data.success) {
        fetchDocuments();
        alert('Document uploaded successfully!');
        setActiveTab('documents');
      } else {
        alert('Error: ' + data.error);
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDocument = async (doc) => {
    setSelectedDoc(doc);
    setActiveTab('summary');
    
    try {
      const response = await fetch(`${API_BASE}/documents/${doc.id}/summary`);
      const data = await response.json();
      if (data.success) {
        setSummary(data.summary);
      }
    } catch (error) {
      console.error('Error fetching summary:', error);
    }
  };

  const handleSearch = async (query) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, limit: 10 }),
      });

      const data = await response.json();
      if (data.success) {
        setSearchResults(data.results);
        setActiveTab('search');
      }
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDocument = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/documents/${docId}`, {
        method: 'DELETE',
      });

      const data = await response.json();
      if (data.success) {
        fetchDocuments();
        setSelectedDoc(null);
        setSummary(null);
      }
    } catch (error) {
      console.error('Delete error:', error);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>⚖️ Legal Document Intelligence</h1>
        <p>AI-Powered Document Analysis & Search System</p>
      </header>

      <nav className="nav-tabs">
        <button
          className={`nav-tab ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          Upload
        </button>
        <button
          className={`nav-tab ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          Documents ({documents.length})
        </button>
        <button
          className={`nav-tab ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          Search
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'upload' && (
          <section className="panel">
            <h2>Upload Legal Document</h2>
            <DocumentUpload onUpload={handleUpload} loading={loading} />
          </section>
        )}

        {activeTab === 'documents' && (
          <section className="panel">
            <h2>Documents Library</h2>
            <DocumentList
              documents={documents}
              onSelect={handleSelectDocument}
              onDelete={handleDeleteDocument}
            />
          </section>
        )}

        {activeTab === 'search' && (
          <section className="panel">
            <h2>Search Documents</h2>
            <SearchPanel
              onSearch={handleSearch}
              results={searchResults}
              onSelectResult={handleSelectDocument}
              loading={loading}
            />
          </section>
        )}

        {selectedDoc && summary && (
          <aside className="sidebar">
            <SummaryPanel
              document={selectedDoc}
              summary={summary}
              onClose={() => {
                setSelectedDoc(null);
                setSummary(null);
              }}
            />
          </aside>
        )}
      </main>

      <footer className="app-footer">
        <p>Legal Document Intelligence MVP | Powered by AI</p>
      </footer>
    </div>
  );
}

export default App;
