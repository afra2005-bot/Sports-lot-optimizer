import React from 'react';
import { 
  ListOrdered, 
  Search, 
  BrainCircuit, 
  Send, 
  Tag, 
  RotateCw, 
  CheckCircle2, 
  StopCircle,
  AlertTriangle
} from 'lucide-react';

export default function ActivityTimeline({ activities = [] }) {
  if (!activities || activities.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <ListOrdered size={16} color="var(--emerald-light)" />
            <span>Agent Activity Timeline</span>
          </div>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          No agent activity recorded for this slot yet. Run the agent to start tracking.
        </p>
      </div>
    );
  }

  const getActionIcon = (action) => {
    switch (action) {
      case 'SLOT_DETECTED': return <Search size={14} color="#60a5fa" />;
      case 'ANALYSIS': return <BrainCircuit size={14} color="#a78bfa" />;
      case 'NOTIFY': return <Send size={14} color="#34d399" />;
      case 'DISCOUNT': return <Tag size={14} color="#fb923c" />;
      case 'REASSESS': return <RotateCw size={14} color="#facc15" />;
      case 'BOOKED': return <CheckCircle2 size={14} color="#10b981" />;
      case 'STOP': return <StopCircle size={14} color="#f43f5e" />;
      case 'AI_FALLBACK': return <AlertTriangle size={14} color="#fbbf24" />;
      default: return <ListOrdered size={14} color="var(--text-muted)" />;
    }
  };

  const formatTime = (isoString) => {
    if (!isoString) return '';
    try {
      const d = new Date(isoString);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <ListOrdered size={16} color="var(--emerald-light)" />
          <span>Agent Activity Timeline</span>
        </div>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          {activities.length} events logged in PostgreSQL
        </span>
      </div>

      <div className="timeline">
        {activities.map((item, idx) => (
          <div className="timeline-item" key={item.id || idx}>
            <div className="timeline-node"></div>
            <div className="timeline-time">{formatTime(item.created_at)}</div>
            <div className="timeline-action">
              {getActionIcon(item.action)}
              <span>{item.action}</span>
              {item.target_segment && (
                <span className="status-badge" style={{ fontSize: '0.68rem', padding: '0.1rem 0.4rem' }}>
                  {item.target_segment}
                </span>
              )}
              {item.recipients_count > 0 && (
                <span style={{ fontSize: '0.75rem', color: '#60a5fa' }}>
                  ({item.recipients_count} sent)
                </span>
              )}
              {item.discount_percent > 0 && (
                <span className="discount-pill" style={{ fontSize: '0.68rem', padding: '0.1rem 0.35rem' }}>
                  {item.discount_percent}% OFF
                </span>
              )}
            </div>
            {item.reason && (
              <div className="timeline-reason">
                {item.reason}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
