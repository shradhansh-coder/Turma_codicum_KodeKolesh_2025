import React, { useEffect, useRef, useState } from 'react';
import './App.css';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import SearchPanel from './components/SearchPanel';
import SummaryPanel from './components/SummaryPanel';
import toast from 'react-hot-toast';
import useLocalStorage from './hooks/useLocalStorage';
import Modal from './components/Modal';
import ThemeToggle from './components/ThemeToggle';
import AuthPanel from './components/AuthPanel';
import { getContractReadonly, getContractWritable, hexFromSha256, diagnoseEth, anchorOnChain } from './eth/eth';

function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [summary, setSummary] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useLocalStorage('activeTab', 'upload');
  const [theme, setTheme] = useLocalStorage('theme', 'light');
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);
  const [uploadProgress, setUploadProgress] = useState({ total: 0, done: 0 });
  const searchInputRef = useRef(null);
  const [auth, setAuth] = useLocalStorage('auth', null);

  const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:5000/api';
  const authHeader = auth?.token ? { Authorization: `Bearer ${auth.token}` } : {};

  useEffect(() => {
    fetchDocuments();
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Quick ETH diagnostics on mount
  useEffect(() => {
    (async () => {
      try {
        const diag = await diagnoseEth();
        // Log to console for debugging and show a helpful toast if misconfigured
        // eslint-disable-next-line no-console
        console.log('ETH Diagnose:', diag);
        if (!diag.ok) {
          if (diag.reason === 'no_code') {
            toast.error('ETH: Config address is not a contract on current network');
          } else if (diag.reason === 'wrong_chain') {
            toast.error('ETH: Wrong chain in wallet. Please switch to Sepolia');
          }
        }
      } catch (_) { /* ignore */ }
    })();
  }, []);

  // Keyboard shortcuts: / focuses search, u/d/s switch tabs
  useEffect(() => {
    const onKey = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === '/') {
        e.preventDefault();
        searchInputRef.current?.focus();
      } else if (e.key.toLowerCase() === 'u') {
        setActiveTab('upload');
      } else if (e.key.toLowerCase() === 'd') {
        setActiveTab('documents');
      } else if (e.key.toLowerCase() === 's') {
        setActiveTab('search');
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [setActiveTab]);

  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${API_BASE}/documents`, { headers: { ...authHeader } });
      if (!response.ok) {
        const msg = await response.text();
        throw new Error(msg || `Failed to fetch documents (${response.status})`);
      }
      const data = await response.json();
      if (data.success) {
        setDocuments(data.documents);
      } else {
        throw new Error(data.error || 'Unknown error');
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
      toast.error(`Load failed: ${error.message}`);
    }
  };

  const handleUpload = async (fileOrFiles) => {
    setLoading(true);
    try {
      const files = Array.isArray(fileOrFiles) ? fileOrFiles : (fileOrFiles instanceof FileList ? Array.from(fileOrFiles) : [fileOrFiles]);
      setUploadProgress({ total: files.length, done: 0 });
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(`${API_BASE}/upload`, { method: 'POST', body: formData, headers: { ...authHeader } });
        if (!response.ok) {
          const msg = await response.text();
          throw new Error(msg || `Upload failed for ${file.name} (${response.status})`);
        }
        const data = await response.json();
        if (data.success) {
          setUploadProgress((p) => ({ total: p.total, done: p.done + 1 }));
        } else {
          throw new Error(data.error || `Upload failed for ${file.name}`);
        }
      }
      await fetchDocuments();
      toast.success(`Uploaded ${files.length} file${files.length > 1 ? 's' : ''}`);
      setActiveTab('documents');
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Upload failed: ' + error.message);
    } finally {
      setLoading(false);
      setUploadProgress({ total: 0, done: 0 });
    }
  };

  const handleSelectDocument = async (doc) => {
    setSelectedDoc(doc);
    setActiveTab('summary');
    
    try {
      const response = await fetch(`${API_BASE}/documents/${doc.id}/summary`, { headers: { ...authHeader } });
      if (!response.ok) {
        const msg = await response.text();
        throw new Error(msg || `Failed to fetch summary (${response.status})`);
      }
      const data = await response.json();
      if (data.success) {
        setSummary(data.summary);
      } else {
        throw new Error(data.error || 'Unknown summary error');
      }
    } catch (error) {
      console.error('Error fetching summary:', error);
      toast.error(`Summary failed: ${error.message}`);
    }
  };

  const handleSearch = async (query) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeader,
        },
        body: JSON.stringify({ query, limit: 10 }),
      });

      if (!response.ok) {
        const msg = await response.text();
        throw new Error(msg || `Search failed (${response.status})`);
      }
      const data = await response.json();
      if (data.success) {
        setSearchResults(data.results);
        setActiveTab('search');
        if (data.results.length === 0) {
          toast('No results found', { icon: '🔎' });
        }
      } else {
        throw new Error(data.error || 'Unknown search error');
      }
    } catch (error) {
      console.error('Search error:', error);
      toast.error('Search error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDocument = async (docId) => {
    try {
      const response = await fetch(`${API_BASE}/documents/${docId}`, {
        method: 'DELETE',
        headers: { ...authHeader },
      });

      if (!response.ok) {
        const msg = await response.text();
        throw new Error(msg || `Delete failed (${response.status})`);
      }
      const data = await response.json();
      if (data.success) {
        await fetchDocuments();
        setSelectedDoc(null);
        setSummary(null);
        toast.success('Document deleted');
      } else {
        throw new Error(data.error || 'Delete failed');
      }
    } catch (error) {
      console.error('Delete error:', error);
      toast.error('Delete failed: ' + error.message);
    }
  };

  const fetchDocHash = async (docId) => {
    const resp = await fetch(`${API_BASE}/proof/hash/${docId}`, { headers: { ...authHeader } });
    if (!resp.ok) {
      const msg = await resp.text();
      throw new Error(msg || 'Failed to get hash');
    }
    const data = await resp.json();
    if (!data.success) throw new Error(data.error || 'Failed to get hash');
    return data.sha256;
  };

  const handleAnchorEth = async (doc) => {
    try {
      const sha = await fetchDocHash(doc.id);
      // Prefer explicit tx path to ensure 'to' is set
      const tx = await anchorOnChain(hexFromSha256(sha), doc.id);
      toast('Transaction sent. Waiting for confirmation...', { icon: '⛓️' });
      await tx.wait();
      toast.success('Anchored on Ethereum');
    } catch (e) {
      console.error(e);
      toast.error(e.message || 'Anchor failed');
    }
  };

  const handleVerifyEth = async (doc) => {
    try {
      const sha = await fetchDocHash(doc.id);
      const contract = await getContractReadonly();
      const anchored = await contract.isAnchored(hexFromSha256(sha));
      if (anchored) {
        toast.success('Document is anchored on Ethereum');
      } else {
        toast('No anchor found for this document', { icon: '🔎' });
      }
    } catch (e) {
      console.error(e);
      toast.error(e.message || 'Verify failed');
    }
  };

  const onRequestDelete = (docId) => setConfirmDeleteId(docId);
  const onConfirmDelete = async () => {
    const id = confirmDeleteId;
    setConfirmDeleteId(null);
    if (id) await handleDeleteDocument(id);
  };

  const toggleTheme = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'));

  return (
    <div className="App">
      <header className="app-header">
        <h1>⚖️ Legal Document Intelligence</h1>
        <p>AI-Powered Document Analysis & Search System</p>
        <ThemeToggle theme={theme} onToggle={toggleTheme} />
        {auth?.user ? (
          <div style={{ position: 'absolute', top: '1rem', left: '1rem' }}>
            <span style={{ color: 'white', marginRight: '.5rem' }}>{auth.user.email}</span>
            <button className="btn-secondary" onClick={() => setAuth(null)}>Logout</button>
          </div>
        ) : null}
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
        {!auth?.token ? (
          <AuthPanel onAuthenticated={(a) => setAuth(a)} apiBase={API_BASE} />
        ) : (
        <>
        {activeTab === 'upload' && (
          <section className="panel">
            <h2>Upload Legal Document</h2>
            <DocumentUpload onUpload={handleUpload} loading={loading} progress={uploadProgress} />
          </section>
        )}

        {activeTab === 'documents' && (
          <section className="panel">
            <h2>Documents Library</h2>
            <DocumentList
              documents={documents}
              onSelect={handleSelectDocument}
              onDelete={onRequestDelete}
              onAnchorEth={handleAnchorEth}
              onVerifyEth={handleVerifyEth}
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
              inputRef={searchInputRef}
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
        </>
        )}
      </main>

      <footer className="app-footer">
        <p>Legal Document Intelligence MVP | Powered by AI</p>
      </footer>

      <Modal
        open={!!confirmDeleteId}
        title="Delete document?"
        confirmText="Delete"
        onConfirm={onConfirmDelete}
        onClose={() => setConfirmDeleteId(null)}
      >
        This action cannot be undone.
      </Modal>
    </div>
  );
}

export default App;
