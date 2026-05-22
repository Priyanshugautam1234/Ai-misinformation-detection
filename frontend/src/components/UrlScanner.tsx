import React, { useState } from 'react';
import { Globe, Link2, AlertCircle, ShieldAlert, ShieldCheck, Shield, ChevronRight, Terminal, RefreshCw, Cpu, Database } from 'lucide-react';
import { CircularTrustGauge, FindingsWidget, Finding } from './Shared';

interface SecurityDetails {
  is_https: boolean;
  status: string;
}

interface RedirectDetails {
  count: number;
  history: string[];
  has_domain_change: boolean;
}

interface SuspiciousKeywords {
  detected: string[];
  count: number;
}

interface WhoisDetails {
  domain_age_years: number;
  created_date: string;
  registrar: string;
  status: string;
  is_heuristic: boolean;
}

interface PageDetails {
  title: string;
  description: string;
  snippet: string;
}

interface Metrics {
  clickbait_score: number;
  domain_reputation_score: number;
}

interface UrlResponse {
  success: boolean;
  url: string;
  domain: string;
  security: SecurityDetails;
  redirects: RedirectDetails;
  suspicious_keywords: SuspiciousKeywords;
  whois: WhoisDetails;
  trust_score: number;
  threat_level: string;
  scrape_success: boolean;
  page_details: PageDetails;
  metrics: Metrics;
  findings: Finding[];
}

export const UrlScanner: React.FC = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<UrlResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reporting, setReporting] = useState(false);
  const [reportSuccess, setReportSuccess] = useState(false);

  const handleScan = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setReportSuccess(false);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/analyze/url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setResult(data);
      } else {
        setError(data.detail || "An error occurred during domain credibility scraping.");
      }
    } catch (err) {
      setError("Web crawler backend is offline. Verify FastAPI is online on port 8000.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickReport = async () => {
    if (!result) return;
    setReporting(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: `URL Credibility: ${result.domain}`,
          description: `Scanner resolved target host '${result.domain}' with a threat level of '${result.threat_level}'. Domain age: ${result.whois.domain_age_years} years. Registrar: ${result.whois.registrar}.`,
          category: result.trust_score < 50 ? "Cybersecurity / Scam" : "General Media",
          source_type: "URL",
          source_reference: result.url,
          threat_level: result.trust_score < 50 ? "Critical" : (result.trust_score < 80 ? "Suspicious" : "Safe"),
          trust_score: result.trust_score,
          notes: `Transport: ${result.security.status}, Hops: ${result.redirects.count}, Phish Terms: ${result.suspicious_keywords.detected.join(', ') || 'none'}, Age: ${result.whois.domain_age_years} yrs`
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

  const loadExample = (exUrl: string) => {
    setUrl(exUrl);
    setResult(null);
    setError(null);
    setReportSuccess(false);
  };

  return (
    <div>
      <style>{`
        .threat-alert-card {
          border-radius: 12px;
          padding: 1.25rem;
          border: 1px solid rgba(255,255,255,0.06);
          margin-bottom: 1.5rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          transition: all 0.3s ease;
        }
        .threat-alert-card.critical {
          background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.02) 100%);
          border-color: rgba(239, 68, 68, 0.3);
          box-shadow: 0 4px 20px rgba(239, 68, 68, 0.05);
        }
        .threat-alert-card.suspicious {
          background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(245, 158, 11, 0.02) 100%);
          border-color: rgba(245, 158, 11, 0.3);
          box-shadow: 0 4px 20px rgba(245, 158, 11, 0.05);
        }
        .threat-alert-card.safe {
          background: linear-gradient(135deg, rgba(34, 197, 94, 0.12) 0%, rgba(34, 197, 94, 0.02) 100%);
          border-color: rgba(34, 197, 94, 0.25);
          box-shadow: 0 4px 20px rgba(34, 197, 94, 0.03);
        }
        .whois-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
          gap: 1rem;
          margin-top: 1rem;
        }
        .whois-subcard {
          background: rgba(255, 255, 255, 0.01);
          border: 1px solid var(--border-color);
          border-radius: 10px;
          padding: 0.85rem;
          text-align: center;
          transition: all 0.3s ease;
        }
        .whois-subcard:hover {
          background: rgba(255, 255, 255, 0.03);
          border-color: rgba(255, 255, 255, 0.1);
          transform: translateY(-2px);
        }
        .terminal-block {
          background: rgba(8, 10, 18, 0.7);
          border: 1px solid rgba(255, 255, 255, 0.05);
          border-radius: 12px;
          padding: 1.25rem;
          font-family: 'Consolas', 'Courier New', monospace;
          color: #94a3b8;
          font-size: 0.8rem;
          line-height: 1.6;
          box-shadow: inset 0 2px 8px rgba(0,0,0,0.5);
        }
        .terminal-row {
          display: flex;
          align-items: flex-start;
          gap: 0.5rem;
          margin-bottom: 0.75rem;
        }
        .terminal-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          margin-top: 5px;
          flex-shrink: 0;
        }
        .terminal-dot.green {
          background-color: var(--accent-green);
          box-shadow: var(--glow-green);
        }
        .terminal-dot.red {
          background-color: var(--accent-red);
          box-shadow: var(--glow-red);
        }
        .terminal-dot.amber {
          background-color: var(--accent-amber);
          box-shadow: var(--glow-amber);
        }
        .terminal-dot.cyan {
          background-color: var(--accent-cyan);
          box-shadow: var(--glow-cyan);
        }
        .hop-tag {
          display: inline-flex;
          align-items: center;
          background: rgba(255, 255, 255, 0.04);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 4px;
          padding: 0.15rem 0.45rem;
          font-size: 0.75rem;
          color: #fff;
          word-break: break-all;
        }
      `}</style>

      <div className="page-title-section">
        <h1 className="page-title">Real URL Credibility Scanner</h1>
        <p className="page-subtitle">Inspect digital certificates, follow redirection hops, query WHOIS records, and scan for phishing terms</p>
      </div>

      <div className="console-grid">
        {/* Input parameters panel */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="input-group" style={{ marginBottom: 0 }}>
            <label className="input-label">Suspect Domain / Target URL</label>
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                className="text-input"
                placeholder="Enter URL to crawl (e.g. apnews.com, netflix-signin-security.xyz)..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={loading}
                style={{ paddingLeft: '2.5rem' }}
              />
              <Link2 size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
            </div>
          </div>

          <button
            className="btn btn-primary"
            onClick={handleScan}
            disabled={loading || !url.trim()}
            style={{ width: '100%' }}
          >
            {loading ? <RefreshCw size={16} className="spin" /> : <Globe size={16} />}
            {loading ? "Running Forensic Scans..." : "Scan Domain Credibility"}
          </button>

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
          <div style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.25rem' }}>
            <h4 style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.75rem', fontWeight: 600 }}>Crawl Forensic Profiles:</h4>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.50rem' }}>
              <button 
                className="btn btn-secondary" 
                style={{ justifyContent: 'flex-start', fontSize: '0.8rem', padding: '0.5rem 0.85rem', gap: '0.5rem' }}
                onClick={() => loadExample("apnews.com")}
              >
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--accent-green)', boxShadow: 'var(--glow-green)' }}></div>
                AP News (Mature Trust Site)
              </button>
              <button 
                className="btn btn-secondary" 
                style={{ justifyContent: 'flex-start', fontSize: '0.8rem', padding: '0.5rem 0.85rem', gap: '0.5rem' }}
                onClick={() => loadExample("theonion.com")}
              >
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--accent-amber)', boxShadow: 'var(--glow-amber)' }}></div>
                The Onion (Satire Broadcast)
              </button>
              <button 
                className="btn btn-secondary" 
                style={{ justifyContent: 'flex-start', fontSize: '0.8rem', padding: '0.5rem 0.85rem', gap: '0.5rem' }}
                onClick={() => loadExample("http://netflix-signin-secure-billing.cc/login")}
              >
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--accent-red)', boxShadow: 'var(--glow-red)' }}></div>
                Netflix Phishing Alert (Insecure Protocol)
              </button>
            </div>
          </div>
        </div>

        {/* Diagnostics & Verification Reports */}
        <div>
          {loading ? (
            <div className="glass-panel scanner-animation-panel">
              <div className="scanning-radar" style={{ borderColor: 'var(--accent-cyan)' }}></div>
              <div className="scanning-txt" style={{ color: 'var(--accent-cyan)' }}>DEPLOYING NETWORK PROBES...</div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Checking redirects history, requesting RDAP registry records, evaluating SSL certificate details</div>
            </div>
          ) : result ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              
              {/* Trust Score Radial Card */}
              <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <CircularTrustGauge score={result.trust_score} />
                
                {/* Actions */}
                <div style={{ width: '100%', marginTop: '1.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem', display: 'flex', justifyContent: 'center' }}>
                  {reportSuccess ? (
                    <span style={{ fontSize: '0.85rem', color: 'var(--accent-green)', fontWeight: 600 }}>✓ Registered successfully in active misinfo ledger!</span>
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

              {/* Threat classification Verdict banner */}
              <div className={`threat-alert-card ${
                result.threat_level === 'Safe' ? 'safe' : (result.threat_level === 'Suspicious' ? 'suspicious' : 'critical')
              }`}>
                {result.threat_level === 'Safe' ? (
                  <ShieldCheck size={36} style={{ color: 'var(--accent-green)', filter: 'drop-shadow(0 0 4px var(--accent-green))', flexShrink: 0 }} />
                ) : result.threat_level === 'Suspicious' ? (
                  <Shield size={36} style={{ color: 'var(--accent-amber)', filter: 'drop-shadow(0 0 4px var(--accent-amber))', flexShrink: 0 }} />
                ) : (
                  <ShieldAlert size={36} style={{ color: 'var(--accent-red)', filter: 'drop-shadow(0 0 4px var(--accent-red))', flexShrink: 0 }} />
                )}
                <div>
                  <h3 style={{ 
                    fontSize: '1rem', 
                    fontWeight: 800, 
                    margin: 0,
                    textTransform: 'uppercase',
                    color: result.threat_level === 'Safe' ? 'var(--accent-green)' : (result.threat_level === 'Suspicious' ? 'var(--accent-amber)' : 'var(--accent-red)')
                  }}>
                    Threat Level: {result.threat_level}
                  </h3>
                  <p style={{ fontSize: '0.8rem', color: '#94a3b8', margin: '4px 0 0 0', lineHeight: 1.3 }}>
                    {result.threat_level === 'Safe' 
                      ? "Domain is classified as highly reputable with robust transport security, mature registration history, and secure resolution paths." 
                      : result.threat_level === 'Suspicious' 
                      ? "Domain exhibits marginal trust indicators. Registered metadata shows recent origin or minor path redirects. Proceed with standard caution." 
                      : "CRITICAL PHISHING HAZARD. URL employs aggressive redirection, unsecure data transfer, or phishing keywords matching popular spoof platforms."}
                  </p>
                </div>
              </div>

              {/* WHOIS Domain Registration Details */}
              <div className="glass-panel">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff', margin: 0 }}>WHOIS Domain Metadata</h3>
                  <span style={{ 
                    fontSize: '0.65rem', 
                    fontWeight: 700, 
                    padding: '0.2rem 0.5rem', 
                    borderRadius: '4px', 
                    background: result.whois.is_heuristic ? 'rgba(168, 85, 247, 0.1)' : 'rgba(34, 197, 94, 0.1)', 
                    border: result.whois.is_heuristic ? '1px solid rgba(168, 85, 247, 0.25)' : '1px solid rgba(34, 197, 94, 0.2)',
                    color: result.whois.is_heuristic ? '#d8b4fe' : '#a7f3d0',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.25rem'
                  }}>
                    <Cpu size={10} />
                    {result.whois.is_heuristic ? "CALIBRATED PREDICTION" : "LIVE RDAP MATCH"}
                  </span>
                </div>
                <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '1rem' }}>Domain ownership metrics resolved from global root registry systems</p>

                <div className="whois-grid">
                  <div className="whois-subcard">
                    <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block', fontWeight: 600 }}>DOMAIN AGE</span>
                    <span style={{ fontSize: '1.1rem', fontWeight: 800, color: result.whois.domain_age_years < 1.0 ? 'var(--accent-red)' : 'var(--accent-green)', fontFamily: 'monospace', display: 'block', marginTop: '0.25rem' }}>
                      {result.whois.domain_age_years} Yrs
                    </span>
                  </div>
                  <div className="whois-subcard">
                    <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block', fontWeight: 600 }}>REGISTRATION DATE</span>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#e2e8f0', display: 'block', marginTop: '0.45rem', fontFamily: 'monospace' }}>
                      {result.whois.created_date.substring(0, 10)}
                    </span>
                  </div>
                  <div className="whois-subcard" style={{ gridColumn: 'span 2' }}>
                    <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block', fontWeight: 600 }}>DOMAIN REGISTRAR</span>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#e2e8f0', display: 'block', marginTop: '0.45rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {result.whois.registrar}
                    </span>
                  </div>
                </div>
              </div>

              {/* Dynamic Real-time inspection logs */}
              <div className="glass-panel">
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Terminal size={18} style={{ color: 'var(--accent-cyan)' }} />
                  Real-time Forensic Diagnostic Stream
                </h3>

                <div className="terminal-block">
                  {/* Step 1: Protocol */}
                  <div className="terminal-row">
                    <div className={`terminal-dot ${result.security.is_https ? 'green' : 'red'}`}></div>
                    <div>
                      <span style={{ color: '#fff', fontWeight: 700 }}>[TRANSPORT SECURITY]</span> Resolving transport encryption protocol...
                      <div style={{ marginTop: '0.25rem' }}>
                        Result: <span style={{ color: result.security.is_https ? 'var(--accent-green)' : 'var(--accent-red)', fontWeight: 700 }}>{result.security.status}</span>
                      </div>
                    </div>
                  </div>

                  {/* Step 2: Redirections */}
                  <div className="terminal-row">
                    <div className={`terminal-dot ${result.redirects.count > 0 ? (result.redirects.has_domain_change ? 'red' : 'amber') : 'green'}`}></div>
                    <div>
                      <span style={{ color: '#fff', fontWeight: 700 }}>[REDIRECT MONITOR]</span> Intercepting HTTP redirect pathway...
                      <div style={{ marginTop: '0.25rem' }}>
                        Redirect Hops: <span style={{ color: '#fff', fontWeight: 700 }}>{result.redirects.count}</span>
                        {result.redirects.count > 0 && (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', marginTop: '0.45rem' }}>
                            <span style={{ color: '#cbd5e1', fontSize: '0.75rem' }}>Redirection history path:</span>
                            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.35rem' }}>
                              {result.redirects.history.map((hop, idx) => (
                                <React.Fragment key={idx}>
                                  {idx > 0 && <ChevronRight size={12} style={{ color: '#475569' }} />}
                                  <span className="hop-tag">{hop}</span>
                                </React.Fragment>
                              ))}
                            </div>
                            {result.redirects.has_domain_change && (
                              <span style={{ color: 'var(--accent-red)', fontSize: '0.72rem', fontWeight: 700 }}>
                                ⚠️ Alert: Redirection hopped across different domain hosts!
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Step 3: Phishing Keyword detection */}
                  <div className="terminal-row">
                    <div className={`terminal-dot ${result.suspicious_keywords.count > 0 ? 'red' : 'green'}`}></div>
                    <div>
                      <span style={{ color: '#fff', fontWeight: 700 }}>[LEXICON AUDIT]</span> Scanning URL for phishing vocabulary...
                      <div style={{ marginTop: '0.25rem' }}>
                        Matches found: <span style={{ color: result.suspicious_keywords.count > 0 ? 'var(--accent-red)' : 'var(--accent-green)', fontWeight: 700 }}>{result.suspicious_keywords.count}</span>
                        {result.suspicious_keywords.count > 0 && (
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginTop: '0.35rem' }}>
                            {result.suspicious_keywords.detected.map((kw, idx) => (
                              <span key={idx} style={{ 
                                padding: '0.1rem 0.4rem', 
                                borderRadius: '3px', 
                                background: 'rgba(239, 68, 68, 0.15)', 
                                border: '1px solid rgba(239, 68, 68, 0.3)',
                                color: '#fca5a5',
                                fontSize: '0.7rem',
                                fontWeight: 700
                              }}>
                                ⚠️ {kw}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Step 4: Web Crawl details */}
                  <div className="terminal-row" style={{ marginBottom: 0 }}>
                    <div className="terminal-dot cyan"></div>
                    <div>
                      <span style={{ color: '#fff', fontWeight: 700 }}>[HTML SCRAPE]</span> Parsing page crawler metadata...
                      <div style={{ 
                        marginTop: '0.45rem', 
                        padding: '0.6rem', 
                        background: 'rgba(255,255,255,0.02)', 
                        border: '1px solid rgba(255,255,255,0.05)',
                        borderRadius: '6px',
                        color: '#cbd5e1'
                      }}>
                        <div style={{ fontWeight: 600, color: '#fff', marginBottom: '0.25rem' }}>Resolved Page Title:</div>
                        <div style={{ fontStyle: 'italic', marginBottom: '0.5rem' }}>"{result.page_details.title}"</div>
                        <div style={{ fontWeight: 600, color: '#fff', marginBottom: '0.25rem' }}>Meta Description:</div>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{result.page_details.description}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Curated Metrics */}
              <div className="glass-panel">
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginBottom: '1.25rem' }}>Scoring Index Metrics</h3>
                
                <div className="metric-row">
                  <span className="metric-label">Domain Reputation Index</span>
                  <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>{result.metrics.domain_reputation_score}/100</span>
                </div>
                
                <div className="metric-row">
                  <span className="metric-label">Title Clickbait Index</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div className="metric-bar-bg">
                      <div className="metric-bar-fill" style={{
                        width: `${result.metrics.clickbait_score}%`,
                        backgroundColor: result.metrics.clickbait_score > 50 ? 'var(--accent-red)' : (result.metrics.clickbait_score > 20 ? 'var(--accent-amber)' : 'var(--accent-green)'),
                        boxShadow: result.metrics.clickbait_score > 50 ? 'var(--glow-red)' : (result.metrics.clickbait_score > 20 ? 'var(--glow-amber)' : 'var(--glow-green)')
                      }}></div>
                    </div>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, width: '35px', textAlign: 'right' }}>{result.metrics.clickbait_score}%</span>
                  </div>
                </div>
              </div>

              {/* Forensic Findings List */}
              {result.findings.length > 0 && (
                <div className="glass-panel">
                  <FindingsWidget findings={result.findings} />
                </div>
              )}
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
              <Globe size={48} style={{ strokeWidth: 1 }} />
              <div>
                <h3 style={{ color: '#cbd5e1', fontSize: '1.1rem', marginBottom: '0.25rem' }}>Awaiting Scanner Target</h3>
                <p style={{ fontSize: '0.85rem', maxWidth: '300px' }}>Enter a URL or host target in the inspection console to deploy scanning probes</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
