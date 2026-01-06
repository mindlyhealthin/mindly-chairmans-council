import { useState } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/council/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error('Failed to get council advice');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header>
          <h1>🎯 Mindly Chairman's Council</h1>
          <p>Multi-model AI advisory for healthcare decisions</p>
        </header>

        <form onSubmit={handleSubmit} className="query-form">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask your question to the council..."
            disabled={loading}
            rows="4"
          />
          <button type="submit" disabled={loading}>
            {loading ? '⏳ Getting Council Advice...' : '🚀 Get Council Advice'}
          </button>
        </form>

        {error && (
          <div className="error">
            <p>⚠️ Error: {error}</p>
          </div>
        )}

        {results && (
          <div className="results">
            <h2>Council Response</h2>
            <div className="session-info">
              <p><strong>Session ID:</strong> {results.session_id}</p>
              <p><strong>Status:</strong> {results.stage}</p>
            </div>

            <div className="opinions">
              <h3>Council Member Responses:</h3>
              {Object.entries(results.council_opinions).map(([id, opinion]) => (
                <div key={id} className="opinion-card">
                  <h4>{opinion.role}</h4>
                  <p className="model">Model: {opinion.model}</p>
                  {opinion.response && (
                    <p className="response">{opinion.response.substring(0, 300)}...</p>
                  )}
                  {opinion.error && (
                    <p className="error-msg">Error: {opinion.error}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
