import { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  LayoutDashboard, 
  FileText, 
  Image, 
  Globe, 
  Database, 
  Activity,
  Github
} from 'lucide-react';
import './App.css';
import { Dashboard } from './components/Dashboard';
import { TextAnalyzer } from './components/TextAnalyzer';
import { ImageDetector } from './components/ImageDetector';
import { UrlScanner } from './components/UrlScanner';
import { ReportSystem } from './components/ReportSystem';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [systemActive, setSystemActive] = useState(false);
  const [dbState, setDbState] = useState('offline');

  // Query heartbeat status of FastAPI backend
  const checkHeartbeat = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/status');
      const data = await res.json();
      if (data.status === "healthy") {
        setSystemActive(true);
        setDbState(data.database.status === "connected" ? "MongoDB Live" : "In-Memory DB");
      } else {
        setSystemActive(false);
        setDbState('offline');
      }
    } catch (err) {
      setSystemActive(false);
      setDbState('offline');
    }
  };

  useEffect(() => {
    checkHeartbeat();
    const interval = setInterval(checkHeartbeat, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      {/* Background neon elements */}
      <div className="bg-orb orb-cyan"></div>
      <div className="bg-orb orb-purple"></div>

      {/* Side navigation bar */}
      <aside className="sidebar">
        <div className="brand-section">
          <ShieldAlert className="brand-icon" size={28} />
          <span className="brand-title">Misinfo Shield</span>
        </div>

        <nav className="navigation-menu">
          <div 
            className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard className="nav-icon" size={18} />
            <span>Dashboard</span>
          </div>

          <div 
            className={`nav-link ${activeTab === 'text' ? 'active' : ''}`}
            onClick={() => setActiveTab('text')}
          >
            <FileText className="nav-icon" size={18} />
            <span>Text Claim NLP</span>
          </div>

          <div 
            className={`nav-link ${activeTab === 'image' ? 'active' : ''}`}
            onClick={() => setActiveTab('image')}
          >
            <Image className="nav-icon" size={18} />
            <span>Image Forensics</span>
          </div>

          <div 
            className={`nav-link ${activeTab === 'url' ? 'active' : ''}`}
            onClick={() => setActiveTab('url')}
          >
            <Globe className="nav-icon" size={18} />
            <span>URL Reputation</span>
          </div>

          <div 
            className={`nav-link ${activeTab === 'reports' ? 'active' : ''}`}
            onClick={() => setActiveTab('reports')}
          >
            <Database className="nav-icon" size={18} />
            <span>Active Registry</span>
          </div>
        </nav>

        {/* System Heartbeat indicators */}
        <div className="system-indicator">
          <div className="status-badge" style={{ marginBottom: '0.5rem' }}>
            <div className="status-dot" style={{ backgroundColor: systemActive ? 'var(--accent-green)' : 'var(--accent-red)', boxShadow: systemActive ? 'var(--glow-green)' : 'var(--glow-red)' }}></div>
            <span>System Heartbeat: {systemActive ? "ONLINE" : "OFFLINE"}</span>
          </div>
          <div className="status-badge" style={{ fontSize: '0.75rem', opacity: 0.8 }}>
            <Activity size={12} style={{ color: 'var(--accent-cyan)' }} />
            <span>Ledger: {dbState}</span>
          </div>
        </div>
      </aside>

      {/* Main rendering viewport */}
      <main className="main-content">
        {activeTab === 'dashboard' && <Dashboard onNavigate={setActiveTab} />}
        {activeTab === 'text' && <TextAnalyzer />}
        {activeTab === 'image' && <ImageDetector />}
        {activeTab === 'url' && <UrlScanner />}
        {activeTab === 'reports' && <ReportSystem />}

        <footer style={{ marginTop: '4rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem', display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#64748b' }}>
          <span>🛡️ AI Misinformation Shield Engine. Powered by FastAPI, React, and MongoDB.</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Github size={12} />
            Secure Sandbox
          </span>
        </footer>
      </main>
    </div>
  );
}

export default App;
