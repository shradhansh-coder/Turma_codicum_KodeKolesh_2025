import React, { useState } from 'react';

export default function AuthPanel({ onAuthenticated, apiBase }) {
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const endpoint = mode === 'login' ? '/auth/login' : '/auth/register';
      const res = await fetch(`${apiBase}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Authentication failed');
      }
      onAuthenticated({ token: data.token, user: data.user });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel" style={{ maxWidth: 480, margin: '2rem auto' }}>
      <h2>{mode === 'login' ? 'Sign In' : 'Create Account'}</h2>
      <form onSubmit={submit} style={{ marginTop: '1rem', display: 'grid', gap: '.75rem' }}>
        {error && <div className="snippets" style={{ borderLeftColor: 'var(--danger)' }}>{error}</div>}
        <input
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="search-input"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="search-input"
          required
          minLength={6}
        />
        <button className="btn-primary" type="submit" disabled={loading}>
          {loading ? 'Please wait...' : (mode === 'login' ? 'Sign In' : 'Create Account')}
        </button>
      </form>
      <div style={{ marginTop: '.75rem', color: 'var(--muted)' }}>
        {mode === 'login' ? (
          <button className="btn-secondary" onClick={() => setMode('register')}>Need an account? Register</button>
        ) : (
          <button className="btn-secondary" onClick={() => setMode('login')}>Have an account? Sign in</button>
        )}
      </div>
    </div>
  );
}
