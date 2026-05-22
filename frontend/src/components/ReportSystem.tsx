import React, { useEffect, useState } from 'react';
import { ShieldAlert, Plus, Search, Filter, Trash2, Eye, X, BookOpen } from 'lucide-react';


interface Report {
  id: string;
  _id: string;
  title: string;
  description: string;
  category: string;
  source_type: string;
  source_reference: string;
  threat_level: string;
  trust_score: number;
  status: string;
  timestamp: string;
  notes: string;
}

export const ReportSystem: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [sourceFilter, setSourceFilter] = useState('All');
  
  // Form State
  const [showAddForm, setShowAddForm] = useState(false);
  const [formTitle, setFormTitle] = useState('');
  const [formDesc, setFormDesc] = useState('');
  const [formCategory, setFormCategory] = useState('Health & Medical');
  const [formSourceType, setFormSourceType] = useState('Text');
  const [formSourceRef, setFormSourceRef] = useState('');
  const [formThreat, setFormThreat] = useState('Suspicious');
  const [formScore, setFormScore] = useState(50);
  const [formNotes, setFormNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Drawer State for reviewing a report details
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [drawerNotes, setDrawerNotes] = useState('');

  const fetchReports = async () => {
    setLoading(true);
    try {
      const url = new URL('http://127.0.0.1:8000/api/reports');
      url.searchParams.append("category", categoryFilter);
      url.searchParams.append("source_type", sourceFilter);
      if (search.trim()) {
        url.searchParams.append("search", search);
      }

      const res = await fetch(url.toString());
      const data = await res.json();
      if (data.success) {
        setReports(data.reports);
      }
    } catch (err) {
      console.error("Failed to load reports from database", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [categoryFilter, sourceFilter, search]);

  const handleAddReport = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: formTitle,
          description: formDesc,
          category: formCategory,
          source_type: formSourceType,
          source_reference: formSourceRef,
          threat_level: formThreat,
          trust_score: Number(formScore),
          notes: formNotes
        })
      });
      if (res.ok) {
        // Reset form & fetch
        setFormTitle('');
        setFormDesc('');
        setFormSourceRef('');
        setFormNotes('');
        setFormScore(50);
        setShowAddForm(false);
        fetchReports();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (reportId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to permanently delete this misinformation log?")) return;
    
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/reports/${reportId}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        if (selectedReport?.id === reportId || selectedReport?._id === reportId) {
          setSelectedReport(null);
        }
        fetchReports();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdateStatus = async (status: string) => {
    if (!selectedReport) return;
    const reportId = selectedReport.id || selectedReport._id;
    setUpdatingStatus(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/reports/${reportId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status,
          notes: drawerNotes
        })
      });
      if (res.ok) {
        // update local review copy
        setSelectedReport({
          ...selectedReport,
          status,
          notes: drawerNotes
        });
        fetchReports();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setUpdatingStatus(false);
    }
  };

  const openReviewDrawer = (report: Report) => {
    setSelectedReport(report);
    setDrawerNotes(report.notes || '');
  };

  return (
    <div style={{ position: 'relative' }}>
      <div className="page-title-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 className="page-title">Intercept Ledger Database</h1>
            <p className="page-subtitle">Inspect historical reports, audit logs, and status queues in MongoDB</p>
          </div>
          <button 
            className="btn btn-primary"
            onClick={() => setShowAddForm(!showAddForm)}
          >
            <Plus size={16} />
            {showAddForm ? "View Active Registry" : "Log Intercept"}
          </button>
        </div>
      </div>

      {showAddForm ? (
        /* Form Panel */
        <div className="glass-panel float-item" style={{ maxWidth: '800px', margin: '0 auto' }}>
          <h2 style={{ fontSize: '1.25rem', color: '#fff', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldAlert size={20} style={{ color: 'var(--accent-cyan)' }} />
            Manual Misinformation Registry Logging
          </h2>

          <form onSubmit={handleAddReport} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div className="input-group">
              <label className="input-label">Report Incident / Headline</label>
              <input
                type="text"
                className="text-input"
                required
                placeholder="e.g. Fictional statement claiming bank closures this Friday..."
                value={formTitle}
                onChange={(e) => setFormTitle(e.target.value)}
              />
            </div>

            <div className="input-group">
              <label className="input-label">Claim Content & Evidence Details</label>
              <textarea
                className="text-area"
                required
                placeholder="Describe the claim, where it was shared, and the core debunk details..."
                value={formDesc}
                onChange={(e) => setFormDesc(e.target.value)}
              ></textarea>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="input-group">
                <label className="input-label">Core Category</label>
                <select
                  className="select-input"
                  value={formCategory}
                  onChange={(e) => setFormCategory(e.target.value)}
                >
                  <option value="Health & Medical">Health & Medical</option>
                  <option value="Global Politics">Global Politics</option>
                  <option value="Finance / Crypto">Finance / Crypto</option>
                  <option value="Climate / Science">Climate / Science</option>
                  <option value="General News">General News</option>
                </select>
              </div>

              <div className="input-group">
                <label className="input-label">Source Format</label>
                <select
                  className="select-input"
                  value={formSourceType}
                  onChange={(e) => setFormSourceType(e.target.value)}
                >
                  <option value="Text">Text paragraph / claim</option>
                  <option value="Image">Image / deepfake photo</option>
                  <option value="URL">URL / website domain</option>
                </select>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="input-group">
                <label className="input-label">Source Reference Location</label>
                <input
                  type="text"
                  className="text-input"
                  placeholder="e.g. WhatsApp, Facebook link, deepfake.jpg..."
                  value={formSourceRef}
                  onChange={(e) => setFormSourceRef(e.target.value)}
                />
              </div>

              <div className="input-group">
                <label className="input-label">Threat Level Matrix</label>
                <select
                  className="select-input"
                  value={formThreat}
                  onChange={(e) => setFormThreat(e.target.value)}
                >
                  <option value="Safe">Safe / Verified factual</option>
                  <option value="Suspicious">Suspicious / Unverified</option>
                  <option value="Critical">Critical Misinformation</option>
                </select>
              </div>
            </div>

            <div className="input-group">
              <label className="input-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Simulated Trust Rating</span>
                <span style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>{formScore}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                className="select-input"
                style={{ height: 'auto', padding: 0 }}
                value={formScore}
                onChange={(e) => setFormScore(Number(e.target.value))}
              />
            </div>

            <div className="input-group">
              <label className="input-label">Moderator / Fact-Check Notes</label>
              <input
                type="text"
                className="text-input"
                placeholder="Include verification details or notes for other team moderators..."
                value={formNotes}
                onChange={(e) => setFormNotes(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={submitting}
                style={{ flex: 1 }}
              >
                Log Registry Ledger
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowAddForm(false)}
                style={{ flex: 1 }}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      ) : (
        /* Registry View */
        <div className="glass-panel">
          {/* Filtering bar */}
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '1rem',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid var(--border-color)',
            paddingBottom: '1.5rem',
            marginBottom: '1rem'
          }}>
            {/* Search */}
            <div style={{ position: 'relative', flexGrow: 1, minWidth: '240px', maxWidth: '400px' }}>
              <input
                type="text"
                className="text-input"
                style={{ paddingLeft: '2.5rem' }}
                placeholder="Search database title, details..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <Search size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
            </div>

            {/* Filters */}
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Filter size={14} style={{ color: '#64748b' }} />
                <select
                  className="select-input"
                  style={{ padding: '0.5rem 2rem 0.5rem 1rem', fontSize: '0.85rem' }}
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                >
                  <option value="All">All Categories</option>
                  <option value="Health & Medical">Health & Medical</option>
                  <option value="Global Politics">Global Politics</option>
                  <option value="Finance / Crypto">Finance / Crypto</option>
                  <option value="Climate / Science">Climate / Science</option>
                </select>
              </div>

              <select
                className="select-input"
                style={{ padding: '0.5rem 2rem 0.5rem 1rem', fontSize: '0.85rem' }}
                value={sourceFilter}
                onChange={(e) => setSourceFilter(e.target.value)}
              >
                <option value="All">All Source Formats</option>
                <option value="Text">Text Claim</option>
                <option value="Image">Image File</option>
                <option value="URL">URL Link</option>
              </select>
            </div>
          </div>

          {loading ? (
            <div className="scanner-animation-panel" style={{ height: '200px' }}>
              <div className="scanning-radar" style={{ width: '50px', height: '50px' }}></div>
              <span className="scanning-txt" style={{ fontSize: '0.9rem' }}>LOADING LEDGER...</span>
            </div>
          ) : reports.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '4rem 2rem', color: '#64748b' }}>
              <BookOpen size={48} style={{ strokeWidth: 1, margin: '0 auto 1rem' }} />
              <h3>No Intercepts Found</h3>
              <p style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>Adjust search queries or log a manual report in the registry.</p>
            </div>
          ) : (
            <div className="reports-table-wrapper">
              <table className="reports-table">
                <thead>
                  <tr>
                    <th>Title & Incident</th>
                    <th>Source Format</th>
                    <th>Category</th>
                    <th>Threat Level</th>
                    <th>Trust Score</th>
                    <th>Queue Status</th>
                    <th style={{ textAlign: 'center' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {reports.map((report) => {
                    const rId = report.id || report._id;
                    const score = report.trust_score;
                    const scoreClass = score > 70 ? "trust-high" : (score > 40 ? "trust-medium" : "trust-low");
                    
                    let formatIcon = "📄";
                    if (report.source_type === "Image") formatIcon = "🖼️";
                    else if (report.source_type === "URL") formatIcon = "🔗";

                    return (
                      <tr key={rId} style={{ cursor: 'pointer' }} onClick={() => openReviewDrawer(report)}>
                        <td>
                          <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.9rem' }}>{report.title}</div>
                          <div style={{ fontSize: '0.75rem', color: '#64748b', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden', maxWidth: '280px' }}>
                            Ref: {report.source_reference}
                          </div>
                        </td>
                        <td>
                          <span style={{ fontSize: '0.85rem' }}>
                            {formatIcon} {report.source_type}
                          </span>
                        </td>
                        <td>
                          <span style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>{report.category}</span>
                        </td>
                        <td>
                          <span className={`badge badge-${report.threat_level?.toLowerCase()}`}>
                            {report.threat_level}
                          </span>
                        </td>
                        <td>
                          <span className={scoreClass} style={{ fontWeight: 800 }}>
                            {score}%
                          </span>
                        </td>
                        <td>
                          <span style={{
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            color: report.status === "Resolved" ? 'var(--accent-green)' : (report.status === "Investigated" ? 'var(--accent-cyan)' : 'var(--accent-amber)')
                          }}>
                            ● {report.status}
                          </span>
                        </td>
                        <td>
                          <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                            <button
                              className="btn btn-secondary"
                              style={{ padding: '0.35rem 0.5rem', borderRadius: '6px' }}
                              onClick={(e) => { e.stopPropagation(); openReviewDrawer(report); }}
                              title="Review Details"
                            >
                              <Eye size={12} />
                            </button>
                            <button
                              className="btn btn-secondary"
                              style={{ padding: '0.35rem 0.5rem', borderRadius: '6px', borderColor: 'rgba(239,68,68,0.2)' }}
                              onClick={(e) => handleDelete(rId, e)}
                              title="Delete Record"
                            >
                              <Trash2 size={12} style={{ color: 'var(--accent-red)' }} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Review Sliding Side Drawer Details */}
      <div className={`mini-drawer ${selectedReport ? "open" : ""}`}>
        {selectedReport && (
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
              <div>
                <span className={`badge badge-${selectedReport.threat_level?.toLowerCase()}`} style={{ marginBottom: '0.5rem' }}>
                  {selectedReport.threat_level} Threat Profile
                </span>
                <h3 style={{ fontSize: '1.25rem', color: '#fff', fontWeight: 700 }}>{selectedReport.title}</h3>
              </div>
              <button
                className="btn btn-secondary"
                style={{ padding: '0.35rem', borderRadius: '50%' }}
                onClick={() => setSelectedReport(null)}
              >
                <X size={16} />
              </button>
            </div>

            {/* Content Body */}
            <div style={{ flexGrow: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.25rem', paddingRight: '0.5rem' }}>
              <div>
                <h4 style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Incident Evidence Description</h4>
                <p style={{ fontSize: '0.9rem', color: '#f1f5f9', lineHeight: 1.5, background: 'rgba(255,255,255,0.02)', padding: '1rem', border: '1px solid var(--border-color)', borderRadius: '10px' }}>
                  {selectedReport.description}
                </p>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <h4 style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Source Format</h4>
                  <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{selectedReport.source_type}</span>
                </div>
                <div>
                  <h4 style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Category</h4>
                  <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{selectedReport.category}</span>
                </div>
              </div>

              <div>
                <h4 style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Source Reference Location</h4>
                <span style={{ fontSize: '0.85rem', fontFamily: 'monospace', wordBreak: 'break-all', color: 'var(--accent-cyan)' }}>
                  {selectedReport.source_reference}
                </span>
              </div>

              <div>
                <h4 style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Calculated Trust Score</h4>
                <span className={selectedReport.trust_score > 70 ? "trust-high" : (selectedReport.trust_score > 40 ? "trust-medium" : "trust-low")} style={{ fontWeight: 800, fontSize: '1.5rem' }}>
                  {selectedReport.trust_score}%
                </span>
              </div>

              {/* Status Update / Notes */}
              <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.25rem', marginTop: '1rem' }}>
                <h4 style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Moderator Fact-checking Verdict</h4>
                <textarea
                  className="text-area"
                  style={{ minHeight: '100px', fontSize: '0.85rem', marginBottom: '1rem' }}
                  placeholder="Record fact check verification conclusions or notes here..."
                  value={drawerNotes}
                  onChange={(e) => setDrawerNotes(e.target.value)}
                ></textarea>
                
                <h4 style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Queue Status Verification</h4>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    className="btn btn-secondary"
                    style={{ flex: 1, fontSize: '0.75rem', padding: '0.5rem', borderColor: selectedReport.status === 'Pending Review' ? 'var(--accent-amber)' : 'var(--border-color)' }}
                    onClick={() => handleUpdateStatus('Pending Review')}
                    disabled={updatingStatus}
                  >
                    ⏳ Queue
                  </button>
                  <button
                    className="btn btn-secondary"
                    style={{ flex: 1, fontSize: '0.75rem', padding: '0.5rem', borderColor: selectedReport.status === 'Investigated' ? 'var(--accent-cyan)' : 'var(--border-color)' }}
                    onClick={() => handleUpdateStatus('Investigated')}
                    disabled={updatingStatus}
                  >
                    🔍 Investigate
                  </button>
                  <button
                    className="btn btn-secondary"
                    style={{ flex: 1, fontSize: '0.75rem', padding: '0.5rem', borderColor: selectedReport.status === 'Resolved' ? 'var(--accent-green)' : 'var(--border-color)' }}
                    onClick={() => handleUpdateStatus('Resolved')}
                    disabled={updatingStatus}
                  >
                    ✓ Resolve
                  </button>
                </div>
              </div>
            </div>

            {/* Bottom Actions */}
            <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.25rem', marginTop: '1.5rem', display: 'flex', gap: '0.75rem' }}>
              <button
                className="btn btn-secondary"
                style={{ flex: 1, fontSize: '0.85rem', borderColor: 'rgba(239, 68, 68, 0.2)' }}
                onClick={(e) => handleDelete(selectedReport.id || selectedReport._id, e)}
              >
                <Trash2 size={14} style={{ color: 'var(--accent-red)', marginRight: '4px' }} />
                Delete Incident Log
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
