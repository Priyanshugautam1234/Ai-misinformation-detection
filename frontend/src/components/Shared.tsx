import React from 'react';
import { ShieldAlert, AlertTriangle, ShieldCheck, CheckCircle2, AlertCircle, TrendingUp } from 'lucide-react';

interface CircularTrustGaugeProps {
  score: number;
  size?: number;
  strokeWidth?: number;
}

export const CircularTrustGauge: React.FC<CircularTrustGaugeProps> = ({ 
  score, 
  size = 180, 
  strokeWidth = 14 
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;

  // Determine colors based on score
  let color = 'var(--accent-green)';
  let label = 'TRUSTWORTHY';
  let Icon = ShieldCheck;

  if (score < 40) {
    color = 'var(--accent-red)';
    label = 'CRITICAL RISK';
    Icon = ShieldAlert;
  } else if (score < 70) {
    color = 'var(--accent-amber)';
    label = 'SUSPICIOUS';
    Icon = AlertTriangle;
  }

  return (
    <div className="trust-radial-wrapper" style={{ position: 'relative' }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        {/* Background track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke="rgba(255, 255, 255, 0.03)"
          strokeWidth={strokeWidth}
        />
        {/* Glowing gauge line */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{
            transition: 'stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1)',
            filter: `drop-shadow(0 0 6px ${color})`
          }}
        />
      </svg>
      
      {/* Central Content */}
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        width: size - 32,
        height: size - 32,
        borderRadius: '50%',
        background: 'rgba(10, 15, 30, 0.6)'
      }}>
        <Icon size={24} style={{ color, marginBottom: '2px' }} />
        <span style={{
          fontSize: '2.5rem',
          fontWeight: 800,
          fontFamily: 'Outfit',
          color: '#fff',
          lineHeight: 1
        }}>
          {score}
        </span>
        <span style={{
          fontSize: '0.65rem',
          fontWeight: 700,
          color,
          letterSpacing: '0.1em',
          marginTop: '4px',
          textTransform: 'uppercase'
        }}>
          {label}
        </span>
      </div>
    </div>
  );
};

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  accentColor?: string;
  subtitle?: string;
}

export const StatCard: React.FC<StatCardProps> = ({ 
  title, 
  value, 
  icon, 
  accentColor = 'var(--accent-cyan)',
  subtitle 
}) => {
  return (
    <div className="glass-panel stat-card">
      <div className="stat-icon-wrapper" style={{ borderColor: `rgba(${accentColor}, 0.2)` }}>
        <span style={{ color: accentColor }}>
          {icon}
        </span>
      </div>
      <div className="stat-details">
        <h3>{title}</h3>
        <div className="stat-value">{value}</div>
        {subtitle && (
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <TrendingUp size={12} />
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
};

export interface Finding {
  type: 'positive' | 'warning' | 'negative';
  title: string;
  description: string;
}

interface FindingsWidgetProps {
  findings: Finding[];
}

export const FindingsWidget: React.FC<FindingsWidgetProps> = ({ findings }) => {
  if (!findings || findings.length === 0) return null;

  return (
    <div className="findings-container">
      <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#f1f5f9', marginBottom: '0.5rem' }}>Forensic Findings</h3>
      {findings.map((f, idx) => {
        let Icon = AlertCircle;
        if (f.type === 'positive') Icon = CheckCircle2;
        else if (f.type === 'warning') Icon = AlertTriangle;

        return (
          <div key={idx} className={`finding-card ${f.type}`}>
            <Icon size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontWeight: 600, marginBottom: '2px' }}>{f.title}</div>
              <div style={{ fontSize: '0.8rem', opacity: 0.85 }}>{f.description}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
