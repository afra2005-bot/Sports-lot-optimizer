import React from 'react';
import { 
  Activity, 
  LayoutDashboard, 
  User, 
  Columns, 
  Sparkles, 
  RefreshCw,
  Zap
} from 'lucide-react';

export default function Navbar({ 
  currentTab, 
  setCurrentTab, 
  agentStatus = 'IDLE',
  onRefresh,
  loading = false,
  health
}) {
  const getStatusClass = (status) => {
    switch (status?.toUpperCase()) {
      case 'ANALYSING': return 'analysing';
      case 'OUTREACH':
      case 'WAITING': return 'waiting';
      case 'REASSESSING': return 'reassessing';
      case 'BOOKED': return 'booked';
      case 'STOPPED': return 'stopped';
      case 'IDLE':
      default: return 'idle';
    }
  };

  return (
    <header className="navbar">
      <div className="nav-brand">
        <div className="nav-logo-icon">
          <Zap size={20} />
        </div>
        <div>
          <div className="nav-title">SportsLot Optimizer</div>
          <div className="nav-subtitle">AI Revenue Optimization Agent</div>
        </div>
      </div>

      <nav className="nav-tabs">
        <button 
          className={`nav-tab-btn ${currentTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setCurrentTab('dashboard')}
        >
          <LayoutDashboard size={16} />
          <span>Turf Manager</span>
        </button>
        <button 
          className={`nav-tab-btn ${currentTab === 'customer' ? 'active' : ''}`}
          onClick={() => setCurrentTab('customer')}
        >
          <User size={16} />
          <span>Customer Portal</span>
        </button>
        <button 
          className={`nav-tab-btn ${currentTab === 'split' ? 'active' : ''}`}
          onClick={() => setCurrentTab('split')}
        >
          <Columns size={16} />
          <span>Live Demo Split</span>
        </button>
      </nav>

      <div className="nav-actions">
        {/* Agent Status Pill */}
        <div className={`status-badge ${getStatusClass(agentStatus)}`}>
          <span className="pulse-dot"></span>
          <span>Agent: {agentStatus}</span>
        </div>

        {/* Mode Indicator */}
        {health?.ai_mode && (
          <div style={{
            fontSize: '0.72rem',
            color: 'var(--text-muted)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.3rem',
            background: 'var(--bg-primary)',
            padding: '0.25rem 0.5rem',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-color)'
          }}>
            <Sparkles size={12} color="var(--emerald-light)" />
            <span>Mode: {health.ai_mode.toUpperCase()}</span>
          </div>
        )}

        {/* Refresh Button */}
        <button 
          className="btn btn-secondary" 
          style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}
          onClick={onRefresh}
          disabled={loading}
          title="Refresh real-time data"
        >
          <RefreshCw size={14} className={loading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>
    </header>
  );
}
