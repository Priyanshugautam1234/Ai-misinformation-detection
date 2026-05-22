import React, { useState } from 'react';
import { Upload, FileImage, ShieldAlert, AlertCircle, AlertTriangle, CheckCircle, Database, Sparkles, Activity } from 'lucide-react';
import { CircularTrustGauge } from './Shared';

interface MetadataTag {
  tag: string;
  description: string;
  value?: string;
}

interface MetadataState {
  software: string;
  camera: string;
  date: string;
  gps_present: boolean;
  raw_headers_count: number;
  present_metadata: MetadataTag[];
  missing_metadata: MetadataTag[];
}

interface ForensicsState {
  deepfake_probability: number;
  ela_anomaly_rating: number;
  noise_variance: number;
  avg_diff: number;
  max_diff: number;
  std_dev_diff: number;
  splicing_detected: boolean;
  suspicious_patches_count: number;
}

interface ImageResponse {
  success: boolean;
  filename: string;
  format: string;
  resolution: string;
  size_kb: number;
  mode: string;
  trust_score: number;
  final_trust_score: number;
  threat_level: string;
  ela_image_base64?: string;
  metadata_integrity_score: number;
  anomaly_percentage: number;
  forensic_confidence_score: number;
  ai_fake_probability: number;
  ai_real_probability: number;
  ai_prediction: string;
  ai_confidence: number;
  metadata: MetadataState;
  forensics: ForensicsState;
  risk_factors: string[];
}

export const ImageDetector: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ImageResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [reporting, setReporting] = useState(false);
  const [reportSuccess, setReportSuccess] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      processFile(file);
    }
  };

  const processFile = (file: File) => {
    setSelectedFile(file);
    setError(null);
    setResult(null);
    setReportSuccess(false);

    // Create local preview URL
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Auto-trigger analysis immediately on select/drop
    uploadAndAnalyze(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      processFile(file);
    }
  };

  const uploadAndAnalyze = async (fileToUpload: File) => {
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", fileToUpload);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/analyze/image', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setResult(data);
      } else {
        setError(data.detail || "Failed to process target image forensics.");
      }
    } catch (err) {
      setError("Digital forensics backend is unreachable. Verify FastAPI is online on port 8000.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFile) {
      uploadAndAnalyze(selectedFile);
    }
  };

  // Quick automated heuristics trigger for demos
  const triggerDemoScan = async (demoType: 'deepfake' | 'original') => {
    setLoading(true);
    setError(null);
    setResult(null);
    setReportSuccess(false);

    // Dynamic generated placeholders for visualization while loading
    if (demoType === 'deepfake') {
      setImagePreview("data:image/svg+xml;charset=utf-8,%3Csvg xmlns%3D'http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg' width%3D'400' height%3D'300' viewBox%3D'0 0 400 300'%3E%3Crect width%3D'100%25' height%3D'100%25' fill%3D'%23151025'%2F%3E%3Ctext x%3D'50%25' y%3D'50%25' fill%3D'%23a855f7' font-size%3D'20' text-anchor%3D'middle' font-family%3D'sans-serif'%3E🤖 deepfake_politician_speech.jpg%3C%2Ftext%3E%3C%2Fsvg%3E");
    } else {
      setImagePreview("data:image/svg+xml;charset=utf-8,%3Csvg xmlns%3D'http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg' width%3D'400' height%3D'300' viewBox%3D'0 0 400 300'%3E%3Crect width%3D'100%25' height%3D'100%25' fill%3D'%23051b15'%2F%3E%3Ctext x%3D'50%25' y%3D'50%25' fill%3D'%2310b981' font-size%3D'20' text-anchor%3D'middle' font-family%3D'sans-serif'%3E📷 dsc_4921_raw_camera.jpg%3C%2Ftext%3E%3C%2Fsvg%3E");
    }

    try {
      const mockCanvas = document.createElement("canvas");
      mockCanvas.width = 300;
      mockCanvas.height = 200;
      const ctx = mockCanvas.getContext("2d");
      if (ctx) {
        // Draw some texture so we have actual pixel variance
        if (demoType === 'deepfake') {
          // Deepfake = extremely flat smooth gray skin block
          ctx.fillStyle = "#808080";
          ctx.fillRect(0, 0, 300, 200);
          ctx.fillStyle = "#ffffff";
          ctx.font = "14px monospace";
          ctx.fillText("Fake Face Area (Flat)", 80, 100);
        } else {
          // Camera Photo = high texture variance noise
          ctx.fillStyle = "#22c55e";
          ctx.fillRect(0, 0, 300, 200);
          for (let i = 0; i < 2000; i++) {
            ctx.fillStyle = `rgb(${Math.random()*150}, ${Math.random()*255}, ${Math.random()*150})`;
            ctx.fillRect(Math.random()*300, Math.random()*200, 2, 2);
          }
        }
      }
      
      mockCanvas.toBlob(async (blob) => {
        if (blob) {
          const fakeFileName = demoType === 'deepfake' 
            ? 'synthetic_politician_deepfake.jpg' 
            : 'camera_original_metadata.jpg';
          const file = new File([blob], fakeFileName, { type: 'image/jpeg' });
          uploadAndAnalyze(file);
        }
      }, 'image/jpeg');
    } catch (err) {
      setError("Demo trigger failed.");
      setLoading(false);
    }
  };

  const handleReportImage = async () => {
    if (!result) return;
    setReporting(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: `Image Forensics: ${result.filename}`,
          description: `Uploaded digital photo metadata and noise variance diagnostics completed. Risk Factors tagged: ${result.risk_factors.join(", ") || "None"}`,
          category: result.forensics.deepfake_probability > 50 ? "Deepfakes / Synthetics" : "General Media",
          source_type: "Image",
          source_reference: result.filename,
          threat_level: result.trust_score < 40 ? "Critical" : (result.trust_score < 70 ? "Suspicious" : "Safe"),
          trust_score: result.trust_score,
          notes: `Deepfake rating: ${result.forensics.deepfake_probability}%, ELA check: ${result.forensics.ela_anomaly_rating}%, Software: ${result.metadata.software}`
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

  // Alert Banner colors based on computed threat level
  const getVerdictStyles = (threat: string) => {
    if (threat.includes("Trustworthy") || threat.includes("Safe")) {
      return {
        bg: 'rgba(16, 185, 129, 0.08)',
        border: '1px solid rgba(16, 185, 129, 0.25)',
        color: 'var(--accent-green)',
        glow: 'var(--glow-green)',
        icon: CheckCircle,
        verdict: 'VERIFIED MEDIA SOURCE',
        desc: 'Image checks confirm intact metadata and high-fidelity compression integrity.'
      };
    } else if (threat.includes("Suspicious")) {
      return {
        bg: 'rgba(245, 158, 11, 0.08)',
        border: '1px solid rgba(245, 158, 11, 0.25)',
        color: 'var(--accent-amber)',
        glow: 'var(--glow-amber)',
        icon: AlertTriangle,
        verdict: 'SUSPICIOUS SIGNAL DETECTED',
        desc: 'Image exhibits metadata omissions or minor JPEG compression anomalies. Proceed with caution.'
      };
    } else {
      return {
        bg: 'rgba(239, 68, 68, 0.08)',
        border: '1px solid rgba(239, 68, 68, 0.25)',
        color: 'var(--accent-red)',
        glow: 'var(--glow-red)',
        icon: ShieldAlert,
        verdict: 'CRITICAL TAMPERING EXPOSED',
        desc: 'Forensics indicate active pixel splicing, software editing traces, or synthetic AI deepfake signatures.'
      };
    }
  };

  const verdict = result ? getVerdictStyles(result.threat_level) : null;
  const VerdictIcon = verdict ? verdict.icon : null;

  return (
    <div>
      <div className="page-title-section">
        <h1 className="page-title">Digital Image Forensics Workspace</h1>
        <p className="page-subtitle">Verify source credentials, camera EXIF headers, and compression level integrity</p>
      </div>

      <div className="console-grid" style={{ gridTemplateColumns: result ? '1fr 1fr' : '1.5fr 1fr' }}>
        {/* Workspace dropzone upload */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <form onSubmit={handleFormSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div className="input-group" style={{ marginBottom: 0 }}>
              <label className="input-label">Suspect Digital Image Target (JPEG, PNG supported)</label>
              
              <label 
                className="dropzone"
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                style={{
                  border: isDragging ? '2px dashed var(--accent-cyan)' : '2px dashed rgba(255, 255, 255, 0.12)',
                  backgroundColor: isDragging ? 'rgba(6, 182, 212, 0.05)' : 'rgba(15, 23, 42, 0.2)',
                  boxShadow: isDragging ? 'var(--glow-cyan)' : 'none',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  padding: '4rem 2rem'
                }}
              >
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                  disabled={loading}
                />
                <Upload size={42} className="dropzone-icon" style={{ strokeWidth: 1.5 }} />
                <div>
                  <p style={{ fontWeight: 600, color: '#fff', fontSize: '1rem' }}>
                    {selectedFile ? selectedFile.name : "Select or drag suspect image here"}
                  </p>
                  <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.4rem', maxWidth: '320px', marginInline: 'auto' }}>
                    Drag & drop file directly. Analysis triggers automatically extracting metadata and ELA maps.
                  </p>
                </div>
              </label>
            </div>

            {selectedFile && (
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
                style={{ width: '100%' }}
              >
                🔍 Analyze Uploaded Media
              </button>
            )}
          </form>

          {/* Local preview if exists (Only displayed when there is no analysis result, or alongside) */}
          {!result && imagePreview && (
            <div style={{
              marginTop: '1rem',
              borderRadius: '12px',
              overflow: 'hidden',
              border: '1px solid var(--border-color)',
              maxHeight: '260px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: '#04080e',
              padding: '8px'
            }}>
              <img src={imagePreview} alt="Target Preview" style={{ maxWidth: '100%', maxHeight: '240px', objectFit: 'contain', borderRadius: '8px' }} />
            </div>
          )}

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

          {/* Quick Demo Dials */}
          <div style={{ marginTop: '1rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.25rem' }}>
            <h4 style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.75rem', fontWeight: 600 }}>Deploy Quick Heuristic Demos:</h4>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button
                className="btn btn-secondary"
                style={{ flex: 1, fontSize: '0.8rem', padding: '0.6rem 0.75rem' }}
                onClick={() => triggerDemoScan('deepfake')}
                disabled={loading}
              >
                🤖 Deepfake Politician speech
              </button>
              <button
                className="btn btn-secondary"
                style={{ flex: 1, fontSize: '0.8rem', padding: '0.6rem 0.75rem' }}
                onClick={() => triggerDemoScan('original')}
                disabled={loading}
              >
                📷 Raw Camera Photo (EXIF intact)
              </button>
            </div>
          </div>
        </div>

        {/* Forensics Output Panel */}
        <div>
          {loading ? (
            <div className="glass-panel scanner-animation-panel" style={{ height: '100%', minHeight: '400px' }}>
              <div className="scanning-radar" style={{ borderColor: 'var(--accent-purple)' }}></div>
              <div className="scanning-txt" style={{ color: 'var(--accent-purple)' }}>RUNNING FORENSICS...</div>
              <div style={{ fontSize: '0.85rem', color: '#64748b', textAlign: 'center', maxWidth: '280px' }}>
                Inspecting EXIF structures, computing pixel error level maps, measuring grid-based splicing ratios
              </div>
            </div>
          ) : result && verdict && VerdictIcon ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              
              {/* Dynamic Threat Verdict Banner */}
              <div style={{
                background: verdict.bg,
                border: verdict.border,
                borderRadius: '16px',
                padding: '1.5rem',
                display: 'flex',
                gap: '1rem',
                alignItems: 'center',
                boxShadow: verdict.glow,
                animation: 'pulseGlow 4s ease-in-out infinite'
              }}>
                <div style={{
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid rgba(255,255,255,0.05)',
                  borderRadius: '12px',
                  width: '48px',
                  height: '48px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <VerdictIcon size={24} style={{ color: verdict.color }} />
                </div>
                <div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#fff', letterSpacing: '0.05em', marginBottom: '0.15rem' }}>{verdict.verdict}</h3>
                  <p style={{ fontSize: '0.825rem', color: '#cbd5e1', lineHeight: 1.4 }}>{verdict.desc}</p>
                </div>
              </div>

              {/* Trust Score Radial gauge card with Diagnostics Grid */}
              <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '1.5rem', alignItems: 'center' }}>
                  <div style={{ display: 'flex', justifyContent: 'center' }}>
                    <CircularTrustGauge score={result.trust_score} />
                  </div>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    <h4 style={{ fontSize: '0.85rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Forensic Metrics</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                      <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}><strong>Format:</strong> {result.format}</div>
                      <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}><strong>Resolution:</strong> {result.resolution}</div>
                      <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}><strong>Size:</strong> {result.size_kb} KB</div>
                    </div>
                    
                    <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem', marginTop: '0.25rem' }}>
                      {reportSuccess ? (
                        <span style={{ fontSize: '0.85rem', color: 'var(--accent-green)', fontWeight: 600, display: 'block', textAlign: 'center' }}>
                          ✓ Logged to Global Registry!
                        </span>
                      ) : (
                        <button 
                          className="btn btn-secondary" 
                          style={{ width: '100%', fontSize: '0.8rem', padding: '0.5rem 1rem' }}
                          onClick={handleReportImage}
                          disabled={reporting}
                        >
                          🛡️ {reporting ? "Logging to db..." : "Index in Global Registry"}
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                {/* 3-Column Diagnostics Sub-grid */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(3, 1fr)',
                  gap: '1rem',
                  borderTop: '1px solid var(--border-color)',
                  paddingTop: '1.25rem'
                }}>
                  {/* Metadata Integrity Score Card */}
                  <div style={{
                    background: 'rgba(15, 23, 42, 0.4)',
                    border: `1px solid ${
                      result.metadata_integrity_score > 70 
                        ? 'rgba(16, 185, 129, 0.25)' 
                        : result.metadata_integrity_score > 30 
                          ? 'rgba(245, 158, 11, 0.25)' 
                          : 'rgba(239, 68, 68, 0.25)'
                    }`,
                    boxShadow: result.metadata_integrity_score > 70 
                      ? '0 0 10px rgba(16, 185, 129, 0.05)' 
                      : result.metadata_integrity_score > 30 
                        ? '0 0 10px rgba(245, 158, 11, 0.05)' 
                        : '0 0 10px rgba(239, 68, 68, 0.05)',
                    borderRadius: '12px',
                    padding: '0.85rem',
                    textAlign: 'center',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    gap: '0.25rem',
                    transition: 'all 0.3s ease'
                  }}>
                    <span style={{ fontSize: '0.65rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Metadata Integrity</span>
                    <span style={{ 
                      fontSize: '1.25rem', 
                      fontWeight: 800, 
                      color: result.metadata_integrity_score > 70 
                        ? 'var(--accent-green)' 
                        : result.metadata_integrity_score > 30 
                          ? 'var(--accent-amber)' 
                          : 'var(--accent-red)',
                      textShadow: result.metadata_integrity_score > 70 
                        ? '0 0 10px rgba(16, 185, 129, 0.3)' 
                        : result.metadata_integrity_score > 30 
                          ? '0 0 10px rgba(245, 158, 11, 0.3)' 
                          : '0 0 10px rgba(239, 68, 68, 0.3)'
                    }}>
                      {result.metadata_integrity_score}%
                    </span>
                  </div>

                  {/* Anomaly Density Card */}
                  <div style={{
                    background: 'rgba(15, 23, 42, 0.4)',
                    border: `1px solid ${result.anomaly_percentage > 20 ? 'rgba(239, 68, 68, 0.25)' : 'rgba(16, 185, 129, 0.25)'}`,
                    boxShadow: result.anomaly_percentage > 20 
                      ? '0 0 10px rgba(239, 68, 68, 0.05)' 
                      : '0 0 10px rgba(16, 185, 129, 0.05)',
                    borderRadius: '12px',
                    padding: '0.85rem',
                    textAlign: 'center',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    gap: '0.25rem',
                    transition: 'all 0.3s ease'
                  }}>
                    <span style={{ fontSize: '0.65rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Anomaly Density</span>
                    <span style={{ 
                      fontSize: '1.25rem', 
                      fontWeight: 800, 
                      color: result.anomaly_percentage > 20 ? 'var(--accent-red)' : 'var(--accent-green)',
                      textShadow: result.anomaly_percentage > 20 
                        ? '0 0 10px rgba(239, 68, 68, 0.3)' 
                        : '0 0 10px rgba(16, 185, 129, 0.3)'
                    }}>
                      {result.anomaly_percentage}%
                    </span>
                  </div>

                  {/* Scan Confidence Card */}
                  <div style={{
                    background: 'rgba(15, 23, 42, 0.4)',
                    border: '1px solid rgba(6, 182, 212, 0.25)',
                    boxShadow: '0 0 10px rgba(6, 182, 212, 0.05)',
                    borderRadius: '12px',
                    padding: '0.85rem',
                    textAlign: 'center',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    gap: '0.25rem',
                    transition: 'all 0.3s ease'
                  }}>
                    <span style={{ fontSize: '0.65rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Scan Confidence</span>
                    <span style={{ 
                      fontSize: '1.25rem', 
                      fontWeight: 800, 
                      color: 'var(--accent-cyan)',
                      textShadow: '0 0 10px rgba(6, 182, 212, 0.3)'
                    }}>
                      {result.forensic_confidence_score}%
                    </span>
                  </div>
                </div>
              </div>

              {/* PyTorch Neural Classifier & Combined Synthesis */}
              <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                  <Sparkles size={18} style={{ color: 'var(--accent-cyan)' }} />
                  Neural AI Classifier & Synthesis
                </h3>

                <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '1.5rem', alignItems: 'center' }}>
                  {/* Separate Scores Comparison */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <h4 style={{ fontSize: '0.85rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Forensic Score Synthesis</h4>
                    
                    {/* Heuristics Score progress bar */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.825rem' }}>
                        <span style={{ color: '#cbd5e1', fontWeight: 500 }}>Structural Heuristics Score:</span>
                        <span style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>
                          {Math.max(5, Math.min(99, Math.round(2 * result.trust_score - result.ai_real_probability * 100)))}/100
                        </span>
                      </div>
                      <div className="metric-bar-bg" style={{ width: '100%', height: '8px' }}>
                        <div className="metric-bar-fill" style={{
                          width: `${Math.max(5, Math.min(99, Math.round(2 * result.trust_score - result.ai_real_probability * 100)))}%`,
                          height: '100%',
                          backgroundColor: 'var(--accent-cyan)',
                          boxShadow: 'var(--glow-cyan)',
                          borderRadius: '4px'
                        }}></div>
                      </div>
                      <span style={{ fontSize: '0.675rem', color: '#64748b' }}>Calculated from EXIF metadata and ELA recompression maps</span>
                    </div>

                    {/* AI Neural Score progress bar */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.825rem' }}>
                        <span style={{ color: '#cbd5e1', fontWeight: 500 }}>ResNet-18 Texture Score:</span>
                        <span style={{ color: 'var(--accent-purple)', fontWeight: 700 }}>
                          {Math.round(result.ai_real_probability * 100)}/100
                        </span>
                      </div>
                      <div className="metric-bar-bg" style={{ width: '100%', height: '8px' }}>
                        <div className="metric-bar-fill" style={{
                          width: `${Math.round(result.ai_real_probability * 100)}%`,
                          height: '100%',
                          backgroundColor: 'var(--accent-purple)',
                          boxShadow: 'var(--glow-purple)',
                          borderRadius: '4px'
                        }}></div>
                      </div>
                      <span style={{ fontSize: '0.675rem', color: '#64748b' }}>Calculated from convolutional texture variance layers</span>
                    </div>
                  </div>

                  {/* AI Confidence Meter Card */}
                  <div style={{
                    background: 'rgba(15, 23, 42, 0.45)',
                    border: `1px solid ${
                      result.ai_prediction === 'REAL' 
                        ? 'rgba(16, 185, 129, 0.25)' 
                        : result.ai_prediction === 'SUSPICIOUS'
                          ? 'rgba(245, 158, 11, 0.25)'
                          : 'rgba(239, 68, 68, 0.25)'
                    }`,
                    boxShadow: result.ai_prediction === 'REAL' 
                      ? 'var(--glow-green)' 
                      : result.ai_prediction === 'SUSPICIOUS'
                        ? 'var(--glow-amber)'
                        : 'var(--glow-red)',
                    borderRadius: '16px',
                    padding: '1.25rem',
                    textAlign: 'center',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '0.65rem',
                    transition: 'all 0.3s ease'
                  }}>
                    <span style={{ fontSize: '0.7rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 700 }}>
                      AI Neural Classification
                    </span>
                    
                    <span style={{
                      fontSize: '1.8rem',
                      fontWeight: 900,
                      letterSpacing: '0.02em',
                      color: result.ai_prediction === 'REAL' 
                        ? 'var(--accent-green)' 
                        : result.ai_prediction === 'SUSPICIOUS'
                          ? 'var(--accent-amber)'
                          : 'var(--accent-red)',
                      textShadow: result.ai_prediction === 'REAL' 
                        ? '0 0 12px rgba(16, 185, 129, 0.4)' 
                        : result.ai_prediction === 'SUSPICIOUS'
                          ? '0 0 12px rgba(245, 158, 11, 0.4)'
                          : '0 0 12px rgba(239, 68, 68, 0.4)'
                    }}>
                      {result.ai_prediction}
                    </span>

                    <div style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#cbd5e1', marginBottom: '0.2rem' }}>
                        <span>Confidence:</span>
                        <strong>{Math.round(result.ai_confidence * 100)}%</strong>
                      </div>
                      <div className="metric-bar-bg" style={{ width: '100%', height: '6px' }}>
                        <div className="metric-bar-fill" style={{
                          width: `${result.ai_confidence * 100}%`,
                          height: '100%',
                          backgroundColor: result.ai_prediction === 'REAL' 
                            ? 'var(--accent-green)' 
                            : result.ai_prediction === 'SUSPICIOUS'
                              ? 'var(--accent-amber)'
                              : 'var(--accent-red)',
                          borderRadius: '3px'
                        }}></div>
                      </div>
                    </div>

                    <div style={{ display: 'flex', gap: '0.5rem', width: '100%', justifyContent: 'space-between', fontSize: '0.65rem', color: '#64748b', marginTop: '0.1rem' }}>
                      <span>Real: {Math.round(result.ai_real_probability * 100)}%</span>
                      <span>Fake: {Math.round(result.ai_fake_probability * 100)}%</span>
                    </div>
                  </div>
                </div>

                {/* Combined Synthesis Breakdown explanation */}
                <div style={{
                  fontSize: '0.8rem',
                  color: '#cbd5e1',
                  background: 'rgba(255, 255, 255, 0.01)',
                  padding: '1rem',
                  borderRadius: '10px',
                  borderLeft: '4px solid var(--accent-cyan)',
                  lineHeight: 1.4,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.35rem'
                }}>
                  <strong>Combined Forensic Diagnostics:</strong>
                  <p style={{ margin: 0, color: '#94a3b8' }}>
                    The unified media score of <strong>{Math.round(result.trust_score)}%</strong> synthesizes structural EXIF metadata indicators and error level pixel maps with neural ResNet-18 texture analysis. 
                    {result.ai_prediction === 'FAKE' ? (
                      <span style={{ color: '#fca5a5' }}> The deep neural classifier flags highly anomalous generative patterns (Fake probability: {Math.round(result.ai_fake_probability * 100)}%).</span>
                    ) : result.ai_prediction === 'SUSPICIOUS' ? (
                      <span style={{ color: 'var(--accent-amber)' }}> The deep neural classifier indicates moderate generative anomalies (Fake probability: {Math.round(result.ai_fake_probability * 100)}%).</span>
                    ) : (
                      <span style={{ color: '#a7f3d0' }}> The deep neural classifier confirms natural camera sensor noise patterns (Real probability: {Math.round(result.ai_real_probability * 100)}%).</span>
                    )}
                  </p>
                </div>
              </div>

              {/* Side-by-Side original-vs-ELA Comparative Viewer */}
              <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Sparkles size={18} style={{ color: 'var(--accent-purple)' }} />
                  Comparative Forensic Mapping
                </h3>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Original Source</span>
                    <div style={{
                      border: '1px solid var(--border-color)',
                      borderRadius: '10px',
                      overflow: 'hidden',
                      background: '#030712',
                      aspectRatio: '4/3',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      padding: '4px'
                    }}>
                      <img src={imagePreview || ""} alt="Original Preview" style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', borderRadius: '6px' }} />
                    </div>
                  </div>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--accent-purple)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Error Level Map</span>
                    <div style={{
                      border: '1px solid rgba(168, 85, 247, 0.25)',
                      boxShadow: '0 0 15px rgba(168, 85, 247, 0.04)',
                      borderRadius: '10px',
                      overflow: 'hidden',
                      background: '#030712',
                      aspectRatio: '4/3',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      padding: '4px'
                    }}>
                      {result.ela_image_base64 ? (
                        <img src={result.ela_image_base64} alt="ELA Forensic Map" style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', borderRadius: '6px' }} />
                      ) : (
                        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>No ELA generated</span>
                      )}
                    </div>
                  </div>
                </div>
                
                <div style={{
                  fontSize: '0.75rem',
                  color: '#94a3b8',
                  background: 'rgba(255, 255, 255, 0.01)',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  borderLeft: '3px solid var(--accent-purple)',
                  lineHeight: 1.4
                }}>
                  <strong>ELA Diagnostics:</strong> Edited sectors (like splicing) produce distinct, high-brightness hotspots in the map, while unedited sectors compression rates are uniform and dark.
                </div>
              </div>

              {/* EXIF Metadata Tag Validator (Present vs Missing) */}
              <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Database size={18} style={{ color: 'var(--accent-cyan)' }} />
                  EXIF Metadata Tag Inspector
                </h3>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
                  {/* Present list */}
                  <div>
                    <h4 style={{ fontSize: '0.85rem', color: 'var(--accent-green)', fontWeight: 700, marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <CheckCircle size={14} /> Present Headers ({result.metadata.present_metadata.length})
                    </h4>
                    
                    {result.metadata.present_metadata.length > 0 ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', maxHeight: '200px', overflowY: 'auto', paddingRight: '4px' }}>
                        {result.metadata.present_metadata.map((meta, i) => (
                          <div key={i} style={{
                            background: 'rgba(16, 185, 129, 0.03)',
                            border: '1px solid rgba(16, 185, 129, 0.08)',
                            padding: '0.5rem 0.75rem',
                            borderRadius: '8px',
                            fontSize: '0.8rem'
                          }}>
                            <div style={{ fontWeight: 700, color: '#fff', fontSize: '0.75rem' }}>{meta.tag}</div>
                            <div style={{ fontSize: '0.7rem', color: '#64748b', fontStyle: 'italic', marginBottom: '0.15rem' }}>{meta.description}</div>
                            <div style={{ fontFamily: 'monospace', color: '#cbd5e1', wordBreak: 'break-all' }}>{meta.value}</div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div style={{ padding: '1rem', border: '1px dashed rgba(255,255,255,0.06)', borderRadius: '8px', textAlign: 'center', fontSize: '0.75rem', color: '#64748b' }}>
                        No camera headers found.
                      </div>
                    )}
                  </div>

                  {/* Missing list */}
                  <div>
                    <h4 style={{ fontSize: '0.85rem', color: 'var(--accent-amber)', fontWeight: 700, marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <AlertTriangle size={14} /> Missing Headers ({result.metadata.missing_metadata.length})
                    </h4>
                    
                    {result.metadata.missing_metadata.length > 0 ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', maxHeight: '200px', overflowY: 'auto', paddingRight: '4px' }}>
                        {result.metadata.missing_metadata.map((meta, i) => (
                          <div key={i} style={{
                            background: 'rgba(245, 158, 11, 0.03)',
                            border: '1px solid rgba(245, 158, 11, 0.08)',
                            padding: '0.5rem 0.75rem',
                            borderRadius: '8px',
                            fontSize: '0.8rem'
                          }}>
                            <div style={{ fontWeight: 700, color: '#cbd5e1', fontSize: '0.75rem' }}>{meta.tag}</div>
                            <div style={{ fontSize: '0.7rem', color: '#64748b' }}>{meta.description}</div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div style={{ padding: '1rem', border: '1px dashed rgba(16,185,129,0.2)', background: 'rgba(16,185,129,0.03)', borderRadius: '8px', textAlign: 'center', fontSize: '0.75rem', color: 'var(--accent-green)', fontWeight: 600 }}>
                        All standard tags verified!
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Forensic Signal Breakdown */}
              <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Activity size={18} style={{ color: 'var(--accent-cyan)' }} />
                  Forensic Signal Indicators
                </h3>
                
                {/* Deepfake */}
                <div className="metric-row">
                  <div>
                    <span className="metric-label" style={{ display: 'block', fontWeight: 600, color: '#f1f5f9' }}>AI Generation / Deepfake probability</span>
                    <span style={{ fontSize: '0.7rem', color: '#64748b' }}>Evaluates center patch frequency and noise variance</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div className="metric-bar-bg" style={{ width: '120px' }}>
                      <div className="metric-bar-fill" style={{
                        width: `${result.forensics.deepfake_probability}%`,
                        backgroundColor: result.forensics.deepfake_probability > 60 ? 'var(--accent-red)' : (result.forensics.deepfake_probability > 30 ? 'var(--accent-amber)' : 'var(--accent-green)'),
                        boxShadow: result.forensics.deepfake_probability > 60 ? 'var(--glow-red)' : (result.forensics.deepfake_probability > 30 ? 'var(--glow-amber)' : 'var(--glow-green)')
                      }}></div>
                    </div>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, width: '35px', textAlign: 'right' }}>{result.forensics.deepfake_probability}%</span>
                  </div>
                </div>

                {/* ELA */}
                <div className="metric-row">
                  <div>
                    <span className="metric-label" style={{ display: 'block', fontWeight: 600, color: '#f1f5f9' }}>Compression Discrepancy (ELA)</span>
                    <span style={{ fontSize: '0.7rem', color: '#64748b' }}>Anomalous pixel variation upon 95% JPEG quality resave</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div className="metric-bar-bg" style={{ width: '120px' }}>
                      <div className="metric-bar-fill" style={{
                        width: `${result.forensics.ela_anomaly_rating}%`,
                        backgroundColor: result.forensics.ela_anomaly_rating > 60 ? 'var(--accent-red)' : (result.forensics.ela_anomaly_rating > 30 ? 'var(--accent-amber)' : 'var(--accent-green)'),
                        boxShadow: result.forensics.ela_anomaly_rating > 60 ? 'var(--glow-red)' : (result.forensics.ela_anomaly_rating > 30 ? 'var(--glow-amber)' : 'var(--glow-green)')
                      }}></div>
                    </div>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, width: '35px', textAlign: 'right' }}>{result.forensics.ela_anomaly_rating}%</span>
                  </div>
                </div>

                {/* Noise Variance / Texture */}
                <div className="metric-row" style={{ borderBottom: 'none', marginBottom: 0, paddingBottom: 0 }}>
                  <div>
                    <span className="metric-label" style={{ display: 'block', fontWeight: 600, color: '#f1f5f9' }}>Local Noise Texture Variance</span>
                    <span style={{ fontSize: '0.7rem', color: '#64748b' }}>Smoothness value below 5.0 indicates synthetic AI generation</span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.2rem' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: result.forensics.noise_variance < 5.0 && result.filename.toLowerCase().endsWith('.jpg') ? 'var(--accent-red)' : 'var(--accent-green)' }}>
                      {result.forensics.noise_variance}
                    </span>
                    <span style={{ fontSize: '0.65rem', color: '#64748b' }}>
                      {result.forensics.noise_variance < 5.0 ? "Flat / Smooth" : "Textured"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Splicing & Splicing Grid Metrics */}
              <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Activity size={16} style={{ color: 'var(--accent-purple)' }} />
                  Localized Splicing Diagnostics
                </h3>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: '#cbd5e1' }}>
                  <span>Splicing Detected:</span>
                  <span style={{ fontWeight: 700, color: result.forensics.splicing_detected ? 'var(--accent-red)' : 'var(--accent-green)' }}>
                    {result.forensics.splicing_detected ? "YES (HIGH RISK)" : "NO (LOW RISK)"}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: '#cbd5e1' }}>
                  <span>Suspicious Grid Sectors:</span>
                  <span style={{ fontWeight: 700 }}>{result.forensics.suspicious_patches_count} / 64 patches</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: '#cbd5e1' }}>
                  <span>ELA Standard Deviation:</span>
                  <span style={{ fontWeight: 700, fontFamily: 'monospace' }}>{result.forensics.std_dev_diff}</span>
                </div>
              </div>

              {/* Integrity Alerts warnings */}
              {result.risk_factors.length > 0 && (
                <div className="glass-panel" style={{ borderColor: 'rgba(239, 68, 68, 0.25)' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--accent-red)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                    <ShieldAlert size={18} />
                    Integrity Alerts Found
                  </h3>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                    {result.risk_factors.map((risk, idx) => (
                      <div key={idx} style={{
                        display: 'flex',
                        gap: '0.5rem',
                        padding: '0.75rem 1rem',
                        background: 'rgba(239,68,68,0.06)',
                        borderLeft: '3px solid var(--accent-red)',
                        borderRadius: '6px',
                        fontSize: '0.85rem',
                        color: '#fecaca'
                      }}>
                        <span>⚠️</span>
                        <span>{risk}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="glass-panel" style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              minHeight: '400px',
              textAlign: 'center',
              color: '#64748b',
              gap: '1.25rem'
            }}>
              <FileImage size={56} style={{ strokeWidth: 1 }} />
              <div>
                <h3 style={{ color: '#cbd5e1', fontSize: '1.2rem', marginBottom: '0.4rem' }}>Awaiting Forensic Media</h3>
                <p style={{ fontSize: '0.875rem', maxWidth: '320px', marginInline: 'auto', lineHeight: 1.4 }}>
                  Select or drag a suspect file in the workspace container on the left to run mathematical ELA and EXIF credentials tests
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
