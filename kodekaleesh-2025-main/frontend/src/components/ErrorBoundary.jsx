import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    // Optionally log to monitoring service
    // console.error('UI Error:', error, info);
  }

  handleReload = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div role="alert" style={{ padding: '2rem', textAlign: 'center' }}>
          <h2 style={{ marginBottom: '0.5rem' }}>Something went wrong.</h2>
          <p style={{ color: '#666', marginBottom: '1rem' }}>
            An unexpected error occurred in the UI.
          </p>
          <button className="btn-primary" onClick={this.handleReload}>
            Reload Page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
