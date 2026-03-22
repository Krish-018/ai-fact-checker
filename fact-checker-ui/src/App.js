import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  const API_URL = 'http://localhost:8000/verify';

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!inputText.trim()) {
      alert('Please enter some text to check');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(API_URL, {
        text: inputText
      });
      
      setResult(response.data);
      
    } catch (err) {
      alert('Error: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (result) {
      const text = `${result.extracted_claim}\n\nTruth: ${result.label}\nConfidence: ${result.confidence_percentage}%\nSimilarity: ${result.similarity_score}\nExplanation: ${result.explanation}`;
      navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.body.classList.toggle('dark-mode');
  };

  return (
    <div className={`app ${darkMode ? 'dark' : 'light'}`}>
      {/* Header with Dark Mode Toggle */}
      <header className="header">
        <div className="header-content">
          <h1>🔍 AI Fact Checker</h1>
          <button className="theme-toggle" onClick={toggleDarkMode}>
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
        <p className="subtitle">Verify news claims instantly with AI</p>
      </header>

      {/* Main Content */}
      <main className="main">
        {/* Input Form */}
        <div className="form-card">
          <form onSubmit={handleSubmit}>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Paste any news claim, headline, or social media post..."
              rows="4"
            />
            <button type="submit" disabled={loading} className="check-btn">
              {loading ? <div className="loading-spinner" /> : 'Check Fact'}
            </button>
          </form>
        </div>

        {/* Result Section */}
        {result && (
          <div className={`result-card ${result.label.toLowerCase()}`}>
            {/* Result Header */}
            <div className="result-header">
              <div className={`verified-badge ${result.label.toLowerCase()}`}>
                {result.label === 'True' ? '✓ Verified True' : '✗ Verified False'}
              </div>
              
              <div className="action-buttons">
                <button 
                  className="action-btn" 
                  onClick={copyToClipboard}
                  title="Copy to clipboard"
                >
                  {copied ? '✓' : '📋'}
                </button>
                <button className="action-btn" title="Share">
                  📤
                </button>
              </div>
            </div>

            {/* Extracted Claim */}
            <div className="result-section">
              <div className="section-title">Extracted Claim</div>
              <div className="section-content">
                {result.extracted_claim}
              </div>
            </div>

            {/* Matched Fact */}
            <div className="result-section">
              <div className="section-title">Matched Fact</div>
              <div className="section-content">
                {result.matched_claim}
              </div>
            </div>

            {/* Confidence Score */}
            <div className="result-section">
              <div className="section-title">Confidence Score</div>
              <div className="confidence-container">
                <div className="confidence-bar-container">
                  <div 
                    className="confidence-bar-fill"
                    style={{ width: `${result.confidence_percentage}%` }}
                  />
                </div>
                <div className="confidence-stats">
                  <span>Similarity Score</span>
                  <span className="confidence-score">
                    {result.similarity_score.toFixed(4)}
                  </span>
                </div>
              </div>
            </div>

            {/* AI Explanation */}
            <div className="result-section">
              <div className="section-title">AI Explanation</div>
              <div className="explanation">
                <p>{result.explanation}</p>
              </div>
            </div>

            {/* PERFORMANCE METRICS SECTION */}
            {result.metrics && (
              <div className="metrics-section">
                <div className="section-title">⚡ PERFORMANCE METRICS</div>
                
                <div className="metrics-grid">
                  {/* Total Time */}
                  <div className="metric-card">
                    <div className="metric-label">Total Time</div>
                    <div className="metric-value">{result.metrics.total_time_ms}ms</div>
                  </div>

                  {/* Token Savings */}
                  <div className="metric-card">
                    <div className="metric-label">Token Savings</div>
                    <div className="metric-value text-success">
                      {result.metrics.token_reduction || 
                       result.metrics.explanation?.compression?.savings_percentage || 
                       0}%
                    </div>
                  </div>

                  {/* Extraction Time */}
                  <div className="metric-card">
                    <div className="metric-label">Extraction</div>
                    <div className="metric-value">{result.metrics.extraction_time_ms || 0}ms</div>
                  </div>

                  {/* Search Time */}
                  <div className="metric-card">
                    <div className="metric-label">Search</div>
                    <div className="metric-value">
                      {result.metrics.similarity_search?.total_time_ms || 
                       result.metrics.similarity_search?.search_time_ms || 
                       0}ms
                    </div>
                  </div>
                </div>

                {/* Detailed Metrics */}
                <div className="metrics-details">
                  {/* Compression Details */}
                  {result.metrics.explanation?.compression && (
                    <div className="metrics-detail-card">
                      <h4>📦 Compression Details</h4>
                      <div className="detail-grid">
                        <span>Original Tokens:</span>
                        <span>{result.metrics.explanation.compression.original_tokens}</span>
                        <span>Compressed Tokens:</span>
                        <span>{result.metrics.explanation.compression.compressed_tokens}</span>
                        <span>Tokens Saved:</span>
                        <span className="text-success">{result.metrics.explanation.compression.tokens_saved}</span>
                        <span>Savings:</span>
                        <span className="text-success">{result.metrics.explanation.compression.savings_percentage}%</span>
                        <span>Compression Latency:</span>
                        <span>{result.metrics.explanation.compression.latency_ms}ms</span>
                      </div>
                    </div>
                  )}

                  {/* Search Details */}
                  {result.metrics.similarity_search && (
                    <div className="metrics-detail-card">
                      <h4>🔍 Search Details</h4>
                      <div className="detail-grid">
                        <span>Embedding Time:</span>
                        <span>{result.metrics.similarity_search.embedding_time_ms || 0}ms</span>
                        <span>Search Time:</span>
                        <span>{result.metrics.similarity_search.search_time_ms || 0}ms</span>
                        <span>Threshold:</span>
                        <span>{result.metrics.similarity_search.threshold || 0.6}</span>
                      </div>
                    </div>
                  )}

                  {/* Explanation Details */}
                  {result.metrics.explanation?.gemini_latency_ms && (
                    <div className="metrics-detail-card">
                      <h4>🤖 AI Details</h4>
                      <div className="detail-grid">
                        <span>Gemini Latency:</span>
                        <span>{result.metrics.explanation.gemini_latency_ms}ms</span>
                        <span>Model:</span>
                        <span>{result.metrics.explanation.model || 'gemini-1.5-flash'}</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Optimization Summary */}
                {(result.metrics.token_reduction > 0 || 
                  result.metrics.explanation?.compression?.savings_percentage > 0) && (
                  <div className="optimization-badge">
                    🚀 <strong>Pipeline Optimization:</strong> Saved{' '}
                    {result.metrics.token_reduction || 
                     result.metrics.explanation?.compression?.savings_percentage || 
                     0}% tokens using ScaleDown compression!
                  </div>
                )}

                {/* Cost Savings Estimate */}
                {result.metrics.explanation?.compression?.savings_percentage > 0 && (
                  <div className="cost-savings">
                    <span>💰 Estimated Cost Reduction: </span>
                    <strong className="text-success">
                      {result.metrics.explanation.compression.savings_percentage}% cheaper
                    </strong>
                    <span className="cost-note"> (vs. uncompressed)</span>
                  </div>
                )}
              </div>
            )}

            {/* Stats Grid */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-label">Confidence</div>
                <div className="stat-value">
                  {result.confidence_percentage}%
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Match</div>
                <div className="stat-value">
                  {result.similarity_score === 1 ? 'Exact' : 
                   result.similarity_score > 0.8 ? 'Very Similar' : 'Similar'}
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Status</div>
                <div className={`stat-value ${result.label.toLowerCase()}`}>
                  {result.label}
                </div>
              </div>
            </div>

            {/* Database Info */}
            {result.metrics?.similarity_search?.matched_index !== undefined && (
              <div className="database-note">
                📚 Matched with fact #{result.metrics.similarity_search.matched_index + 1} in database
              </div>
            )}
          </div>
        )}

        {/* No Result Placeholder */}
        {!result && !loading && (
          <div className="welcome-message">
            <p>Enter a news claim above to verify it with AI</p>
            <p className="examples-title">Try examples:</p>
            <div className="examples-grid">
              <button 
                className="example-btn"
                onClick={() => setInputText("The earth revolves around the sun")}
              >
                🌍 Earth revolves around sun
              </button>
              <button 
                className="example-btn"
                onClick={() => setInputText("Drinking hot water cures COVID")}
              >
                💧 Hot water cures COVID
              </button>
              <button 
                className="example-btn"
                onClick={() => setInputText("Vaccines cause autism")}
              >
                💉 Vaccines cause autism
              </button>
              <button 
                className="example-btn"
                onClick={() => setInputText("Melting ice sheets redistribute Earth's mass")}
              >
                ❄️ Ice sheets redistribute mass
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;