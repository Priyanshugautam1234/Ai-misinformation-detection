import React, { useState } from 'react';
import { Send, AlertTriangle, CheckSquare, ShieldCheck, ShieldAlert, AlertCircle, BarChart3, Database, FileText } from 'lucide-react';
import { CircularTrustGauge } from './Shared';

interface AnalysisResponse {
  success: boolean;
  message: string;
  prediction: string;
  prediction_label: string;
  is_scam: boolean;
  confidence: number;
  confidence_score: number;
  threat_level: string;
  suspicious_keywords: string[];
  probabilities: {
    safe: number;
    scam: number;
  };
}

export const TextAnalyzer: React.FC = () => {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reporting, setReporting] = useState(false);
  const [reportSuccess, setReportSuccess] = useState(false);

  // Dynamic Trust Score computation
  // If scam: Low trust score = (1 - confidence) * 100
  // If safe: High trust score = confidence * 100
  const getTrustScore = (res: AnalysisResponse) => {
    if (res.is_scam) {
      return Math.round((1 - res.confidence) * 100);
    } else {
      return Math.round(res.confidence * 100);
    }
  };

  // Safe keyword highlighter
  const highlightKeywords = (textStr: string, keywords: string[]) => {
    if (!keywords || keywords.length === 0) return textStr;
    
    // Sort keywords by length descending to match multi-word terms first (e.g. "click now" before "click")
    const sortedKeywords = [...keywords].sort((a, b) => b.length - a.length);
    const escapeRegExp = (str: string) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const pattern = new RegExp(`(${sortedKeywords.map(escapeRegExp).join('|')})`, 'gi');
    
    return textStr.replace(pattern, (match) => `<span class="keyword-highlight">${match}</span>`);
  };

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setReportSuccess(false);

    try {
      const res = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setResult(data);
      } else {
        setError(data.detail || "An error occurred during Machine Learning text analysis.");
      }
    } catch (err) {
      setError("Unable to reach the ML backend server. Please verify it is running on port 8000.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickReport = async () => {
    if (!result) return;
    setReporting(true);
    const trustScore = getTrustScore(result);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: `ML Scan: ${text.substring(0, 30)}...`,
          description: text,
          category: result.is_scam ? "Cybersecurity / Scam" : "Ham Message",
          source_type: "Text",
          source_reference: "ML Predictive Classifier Engine",
          threat_level: result.threat_level,
          trust_score: trustScore,
          notes: `Verdict: ${result.prediction.toUpperCase()}, Keywords: ${result.suspicious_keywords.join(', ') || 'none'}, Confidence: ${Math.round(result.confidence * 100)}%`
        })
      });
      if (res.ok) {
        setReportSuccess(true);
      }
    } catch (err) {
      console.error("Failed to submit quick report", err);
    } finally {
      setReporting(false);
    }
  };

  return (
    <div>
      <style>{`
        .keyword-highlight {
          background: rgba(239, 68, 68, 0.18);
          border-bottom: 2px solid var(--accent-red);
          color: #fca5a5;
          text-shadow: var(--glow-red);
          padding: 0 4px;
          border-radius: 4px;
          font-weight: 700;
        }
        .keyword-badge {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          padding: 0.35rem 0.65rem;
          border-radius: 6px;
          font-size: 0.72rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          background: rgba(239, 68, 68, 0.08);
          border: 1px solid rgba(239, 68, 68, 0.25);
          color: #fca5a5;
          box-shadow: 0 2px 8px rgba(0,0,0,0.2), 0 0 8px rgba(239, 68, 68, 0.05);
        }
      `}</style>

      <div className="page-title-section">
        <h1 className="page-title">AI Predictive Scam Diagnostic Console</h1>
        <p className="page-subtitle">Examine text claims, messages, or emails using pre-trained Logistic Regression & TF-IDF vectors</p>
      </div>

      <div className="console-grid">
        {/* Input panel */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="input-group" style={{ marginBottom: 0 }}>
            <label className="input-label">Claim Text / SMS Message / Phishing Email</label>
            <textarea
              className="text-area"
              placeholder="Paste suspicious text message, phishing email contents, or transactional claim here to run ML inference..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={loading}
            ></textarea>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
              {text.length} characters | {text.split(/\s+/).filter(Boolean).length} words
            </span>
            <button
              className="btn btn-primary"
              onClick={handleAnalyze}
              disabled={loading || !text.trim()}
            >
              <Send size={16} />
              {loading ? "Evaluating Inference..." : "Deploy ML Predictor"}
            </button>
          </div>

          {error && (
            <div style={{
              display: 'flex',
              gap: '0.75rem',
              padding: '1rem',
              borderRadius: '10px',
              background: 'rgba(239, 68, 68, 0.08)',
              border: '1px solid rgba(239, 68, 68, 0.2)',
              color: '#fca5a5',
              fontSize: '0.85rem'
            }}>
              <AlertCircle size={18} style={{ flexShrink: 0 }} />
              {error}
            </div>
          )}

          {/* Quick Examples */}
          <div style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
            <h4 style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.75rem', fontWeight: 600 }}>Try standard sample prompts:</h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              <button 
                className="btn btn-secondary" 
                style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem', borderRadius: '6px' }}
                onClick={() => setText("URGENT! Your mobile number was awarded 2,000,000 pounds. Call 09066368727 click now to claim your winner prize.")}
              >
                🚨 Cash Prize Scam
              </button>
              <button 
                className="btn btn-secondary" 
                style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem', borderRadius: '6px' }}
                onClick={() => setText("Dear customer, your bank card has been blocked. We sent an OTP to verify your identity. Please call us for a free unlock.")}
              >
                📞 Bank OTP Lock
              </button>
              <button 
                className="btn btn-secondary" 
                style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem', borderRadius: '6px' }}
                onClick={() => setText("Hey, are we still meeting today? Just wanted to catch up.")}
              >
                🛡️ Safe Work Text
              </button>
              <button 
                className="btn btn-secondary" 
                style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem', borderRadius: '6px' }}
                onClick={() => setText("Hey mom, just wanted to check if you got the groceries. Love you!")}
              >
                💬 Casual Greetings
              </button>
            </div>
          </div>
        </div>

        {/* Output Diagnostics Panel */}
        <div>
          {loading ? (
            <div className="glass-panel scanner-animation-panel">
              <div className="scanning-radar"></div>
              <div className="scanning-txt">COMPUTING ML MODEL INFERENCE...</div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Applying TF-IDF vector transform & evaluating class probabilities</div>
            </div>
          ) : result ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {/* Trust Score Radial Card */}
              <div className="glass-panel" style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center',
                borderWidth: '1px',
                borderStyle: 'solid',
                borderColor: result.is_scam ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)',
                background: result.is_scam ? 'rgba(239, 68, 68, 0.01)' : 'rgba(34, 197, 94, 0.01)',
              }}>
                <CircularTrustGauge score={getTrustScore(result)} />
                
                {/* Quick actions on results */}
                <div style={{ width: '100%', marginTop: '1.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem', display: 'flex', justifyContent: 'center' }}>
                  {reportSuccess ? (
                    <span style={{ fontSize: '0.85rem', color: 'var(--accent-green)', fontWeight: 600 }}>✓ Logged successfully to active registry!</span>
                  ) : (
                    <button 
                      className="btn btn-secondary" 
                      style={{ width: '100%', fontSize: '0.85rem', padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                      onClick={handleQuickReport}
                      disabled={reporting}
                    >
                      <Database size={14} />
                      {reporting ? "Logging to db..." : "Index in Global Misinfo Registry"}
                    </button>
                  )}
                </div>
              </div>

              {/* Explanatory Keyword Highlight view */}
              <div className="glass-panel">
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <FileText size={18} style={{ color: 'var(--accent-cyan)' }} />
                  Scam Diagnostics & Highlighted Text
                </h3>
                
                <div 
                  style={{
                    padding: '1.25rem',
                    background: 'rgba(10, 15, 30, 0.45)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '10px',
                    fontSize: '0.875rem',
                    lineHeight: '1.6',
                    color: '#e2e8f0',
                    whiteSpace: 'pre-wrap',
                    marginBottom: '1rem',
                    fontFamily: 'Outfit, sans-serif'
                  }} 
                  dangerouslySetInnerHTML={{ __html: highlightKeywords(result.message, result.suspicious_keywords) }} 
                />

                <div style={{ marginTop: '0.5rem' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', display: 'block', marginBottom: '0.5rem' }}>
                    Detected suspicious vocab terms:
                  </span>
                  
                  {result.suspicious_keywords.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                      {result.suspicious_keywords.map((kw, idx) => (
                        <span key={idx} className="keyword-badge">
                          ⚠️ {kw}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <div style={{ fontSize: '0.8rem', color: 'var(--accent-green)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <ShieldCheck size={14} />
                      Zero high-risk keywords detected.
                    </div>
                  )}
                </div>
              </div>

              {/* ML Verdict Breakdown Panel */}
              <div className="glass-panel" style={{
                borderColor: result.is_scam ? 'rgba(239, 68, 68, 0.15)' : 'rgba(34, 197, 94, 0.15)',
              }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <BarChart3 size={18} style={{ color: result.is_scam ? 'var(--accent-red)' : 'var(--accent-green)' }} />
                  Classifier Inference Metrics
                </h3>

                {/* Verdict Row */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.75rem 1rem',
                  background: 'rgba(255, 255, 255, 0.02)',
                  borderRadius: '8px',
                  marginBottom: '1rem',
                  border: '1px solid var(--border-color)'
                }}>
                  <span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>Model Verdict</span>
                  <span style={{
                    fontSize: '0.95rem',
                    fontWeight: 800,
                    letterSpacing: '0.05em',
                    color: result.is_scam ? 'var(--accent-red)' : 'var(--accent-green)',
                    textShadow: result.is_scam ? 'var(--glow-red)' : 'var(--glow-green)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem'
                  }}>
                    {result.is_scam ? <ShieldAlert size={16} /> : <ShieldCheck size={16} />}
                    {result.prediction.toUpperCase()}
                  </span>
                </div>

                {/* Threat Level Row */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.75rem 1rem',
                  background: 'rgba(255, 255, 255, 0.02)',
                  borderRadius: '8px',
                  marginBottom: '1rem',
                  border: '1px solid var(--border-color)'
                }}>
                  <span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>Computed Threat Severity</span>
                  <span style={{
                    fontSize: '0.9rem',
                    fontWeight: 700,
                    color: result.threat_level === 'Critical' ? 'var(--accent-red)' : (result.threat_level === 'Suspicious' ? 'var(--accent-amber)' : 'var(--accent-green)'),
                    textShadow: result.threat_level === 'Critical' ? 'var(--glow-red)' : (result.threat_level === 'Suspicious' ? 'var(--glow-amber)' : 'var(--glow-green)'),
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem'
                  }}>
                    <AlertTriangle size={15} />
                    {result.threat_level.toUpperCase()}
                  </span>
                </div>

                {/* Confidence Level Row */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.75rem 1rem',
                  background: 'rgba(255, 255, 255, 0.02)',
                  borderRadius: '8px',
                  marginBottom: '1.5rem',
                  border: '1px solid var(--border-color)'
                }}>
                  <span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>Classification Confidence</span>
                  <span style={{
                    fontSize: '0.95rem',
                    fontWeight: 700,
                    color: '#fff',
                    fontFamily: 'monospace'
                  }}>
                    {(result.confidence * 100).toFixed(2)}%
                  </span>
                </div>

                {/* Probability Distribution */}
                <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.05)', paddingTop: '1.25rem' }}>
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#94a3b8', marginBottom: '1rem' }}>Class Probability Distribution</h4>
                  
                  {/* Safe Bar */}
                  <div className="metric-row" style={{ marginBottom: '1rem' }}>
                    <span className="metric-label" style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>Legitimate (Safe) Score</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div className="metric-bar-bg">
                        <div className="metric-bar-fill" style={{
                          width: `${result.probabilities.safe * 100}%`,
                          backgroundColor: 'var(--accent-green)',
                          boxShadow: 'var(--glow-green)'
                        }}></div>
                      </div>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, width: '45px', textAlign: 'right', fontFamily: 'monospace' }}>
                        {(result.probabilities.safe * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  {/* Scam Bar */}
                  <div className="metric-row">
                    <span className="metric-label" style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>Scam (Fraudulent) Score</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div className="metric-bar-bg">
                        <div className="metric-bar-fill" style={{
                          width: `${result.probabilities.scam * 100}%`,
                          backgroundColor: 'var(--accent-red)',
                          boxShadow: 'var(--glow-red)'
                        }}></div>
                      </div>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, width: '45px', textAlign: 'right', fontFamily: 'monospace' }}>
                        {(result.probabilities.scam * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-panel" style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '300px',
              textAlign: 'center',
              color: '#64748b',
              gap: '1rem'
            }}>
              <CheckSquare size={48} style={{ strokeWidth: 1 }} />
              <div>
                <h3 style={{ color: '#cbd5e1', fontSize: '1.1rem', marginBottom: '0.25rem' }}>Awaiting Diagnostic Target</h3>
                <p style={{ fontSize: '0.85rem', maxWidth: '300px' }}>Input text messages or claim paragraphs to evaluate real ML models</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
