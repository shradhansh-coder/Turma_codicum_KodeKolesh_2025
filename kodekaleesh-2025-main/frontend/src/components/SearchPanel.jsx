import React, { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react';

function highlight(text, query) {
  if (!query) return text;
  const q = query.trim();
  if (!q) return text;
  const parts = text.split(new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'));
  return parts.map((part, i) => (
    part.toLowerCase() === q.toLowerCase() ? <mark key={i}>{part}</mark> : <span key={i}>{part}</span>
  ));
}

const SearchPanel = forwardRef(function SearchPanel({ onSearch, results, onSelectResult, loading, inputRef }, ref) {
  const [query, setQuery] = useState('');
  const localInputRef = useRef(null);

  useImperativeHandle(ref, () => ({
    focus: () => localInputRef.current?.focus(),
  }));

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim().length >= 2) {
      onSearch(query);
    }
  };

  return (
    <div className="search-panel">
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search across documents (e.g., 'plaintiff', 'contract terms', 'appeal')..."
          className="search-input"
          aria-label="Search documents"
          ref={(el) => {
            localInputRef.current = el;
            if (inputRef) inputRef.current = el;
          }}
        />
        <button type="submit" className="btn-primary" disabled={loading || query.trim().length < 2} aria-disabled={loading || query.trim().length < 2}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {results.length > 0 && (
        <div className="search-results">
          <h3>Search Results ({results.length})</h3>
          {results.map((result) => (
            <div key={result.document_id} className="search-result" role="article" aria-label={`Search result for ${result.filename}`}>
              <div className="result-header">
                <h4>{result.filename}</h4>
                <span className="relevance">Relevance: {result.relevance_score}</span>
              </div>
              <div className="result-metadata">
                <span>Matches: {result.match_count}</span>
                <span>Date: {new Date(result.created_at).toLocaleDateString()}</span>
              </div>
              {result.snippets.length > 0 && (
                <div className="snippets">
                  <p className="snippets-title">Context:</p>
                  {result.snippets.map((snippet, idx) => (
                    <p key={idx} className="snippet">{highlight(snippet, query)}</p>
                  ))}
                </div>
              )}
              <button
                className="btn-secondary"
                onClick={() => onSelectResult({ id: result.document_id, filename: result.filename })}
              >
                View Document
              </button>
            </div>
          ))}
        </div>
      )}

      {!loading && results.length === 0 && query && (
        <div className="no-results">
          <p>No results found for "{query}"</p>
        </div>
      )}
    </div>
  );
});

export default SearchPanel;
