import React from 'react';
import { BarChart3, CheckCircle2 } from 'lucide-react';

export default function SegmentAnalysis({ segmentStats = [], selectedSegment = null }) {
  if (!segmentStats || segmentStats.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <BarChart3 size={16} color="var(--emerald-light)" />
            <span>Customer Segment Behaviour</span>
          </div>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Select a slot to view historical segment conversion, fill rates, and booking times.
        </p>
      </div>
    );
  }

  const formatSegmentName = (seg) => {
    switch (seg) {
      case 'STUDENT': return 'Students (College Groups)';
      case 'WORKING_PROFESSIONAL': return 'Working Professionals (Corporate)';
      case 'NON_WORKING': return 'Non-Working / Casual';
      case 'OTHER': return 'Regular Weeknight / Teams';
      default: return seg;
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <BarChart3 size={16} color="var(--emerald-light)" />
          <span>Historical Segment Behaviour Analysis</span>
        </div>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Calculated from PostgreSQL Dataset
        </span>
      </div>

      <div className="segment-table-container">
        <table className="segment-table">
          <thead>
            <tr>
              <th>Customer Segment</th>
              <th>Historical Fill Rate</th>
              <th>Avg Time-to-Book</th>
              <th>Conversion Rate</th>
              <th>Bookings</th>
            </tr>
          </thead>
          <tbody>
            {segmentStats.map((stat) => {
              const isTargeted = selectedSegment && stat.segment === selectedSegment;
              const fillPercent = Math.round((stat.fill_rate || 0) * 100);
              const convPercent = Math.round((stat.conversion_rate || 0) * 100);

              return (
                <tr 
                  key={stat.segment} 
                  className={isTargeted ? 'selected-segment' : ''}
                >
                  <td style={{ fontWeight: isTargeted ? 700 : 500 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      {isTargeted && <CheckCircle2 size={14} color="var(--emerald-light)" />}
                      <span>{formatSegmentName(stat.segment)}</span>
                    </div>
                  </td>
                  <td style={{ minWidth: '130px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                      <span>{fillPercent}%</span>
                    </div>
                    <div className="progress-bar-bg">
                      <div 
                        className="progress-bar-fill" 
                        style={{ width: `${Math.min(100, fillPercent)}%` }}
                      ></div>
                    </div>
                  </td>
                  <td>
                    <span className="font-mono">{stat.avg_time_to_book} min</span>
                  </td>
                  <td>
                    <span 
                      style={{ 
                        fontWeight: 600, 
                        color: convPercent > 50 ? 'var(--emerald-light)' : 'var(--text-secondary)' 
                      }}
                    >
                      {convPercent}%
                    </span>
                  </td>
                  <td>
                    <span className="font-mono">{stat.num_bookings}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
