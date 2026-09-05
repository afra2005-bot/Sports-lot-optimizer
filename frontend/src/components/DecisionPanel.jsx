import React from 'react';
import { Sparkles, Users, Percent, Clock, Send, HelpCircle, Bot } from 'lucide-react';

export default function DecisionPanel({ decision, latestActivity, recipientsCount = 0 }) {
  if (!decision && !latestActivity) {
    return (
      <div className="decision-card" style={{ textAlign: 'center', padding: '2rem 1rem' }}>
        <Bot size={36} color="var(--text-muted)" style={{ margin: '0 auto 0.75rem' }} />
        <h4 style={{ color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>AI Decision Pending</h4>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Select a vacant slot and click <strong>RUN AI AGENT</strong> to trigger autonomous analysis and targeted outreach.
        </p>
      </div>
    );
  }

  const action = decision?.action || latestActivity?.action || 'ANALYSIS';
  const segment = decision?.segment || latestActivity?.target_segment || 'N/A';
  const discount = decision?.discount_percent ?? latestActivity?.discount_percent ?? 0;
  const waitMinutes = decision?.wait_minutes ?? 30;
  const reason = decision?.reason || latestActivity?.reason || 'Agent analyzed customer behavior statistics and current slot urgency.';
  const recipients = decision ? recipientsCount : (latestActivity?.recipients_count || recipientsCount);

  const getActionColor = (act) => {
    switch (act) {
      case 'NOTIFY': return 'var(--emerald-light)';
      case 'NOTIFY_WITH_DISCOUNT': return 'var(--amber-primary)';
      case 'STOP': return 'var(--rose-primary)';
      case 'REASSESS': return 'var(--purple-primary)';
      default: return 'var(--blue-primary)';
    }
  };

  return (
    <div className="decision-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={18} color="var(--emerald-light)" />
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff' }}>
            AI AGENT DECISION
          </h3>
        </div>
        <span 
          className="status-badge"
          style={{ 
            background: 'rgba(0,0,0,0.4)', 
            color: getActionColor(action),
            border: `1px solid ${getActionColor(action)}`
          }}
        >
          {action}
        </span>
      </div>

      <div className="decision-grid">
        <div className="decision-metric">
          <div className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Users size={12} /> Target Segment
          </div>
          <div className="metric-value" style={{ color: 'var(--emerald-light)' }}>
            {segment.replace('_', ' ')}
          </div>
        </div>

        <div className="decision-metric">
          <div className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Percent size={12} /> Discount
          </div>
          <div className="metric-value" style={{ color: discount > 0 ? '#fb923c' : 'var(--text-primary)' }}>
            {discount}%
          </div>
        </div>

        <div className="decision-metric">
          <div className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Clock size={12} /> Wait Period
          </div>
          <div className="metric-value">
            {waitMinutes} <span style={{ fontSize: '0.75rem', fontWeight: 400 }}>min</span>
          </div>
        </div>

        <div className="decision-metric">
          <div className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Send size={12} /> Outreach
          </div>
          <div className="metric-value" style={{ color: '#60a5fa' }}>
            {recipients} <span style={{ fontSize: '0.75rem', fontWeight: 400 }}>notified</span>
          </div>
        </div>
      </div>

      {/* WHY DID THE AGENT DO THIS? */}
      <div className="reasoning-box">
        <div className="reasoning-title">
          <HelpCircle size={14} />
          <span>Why did the agent do this?</span>
        </div>
        <p>{reason}</p>
      </div>
    </div>
  );
}
