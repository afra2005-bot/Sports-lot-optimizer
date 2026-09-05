import React from 'react';
import { DollarSign, TrendingUp, CheckCircle } from 'lucide-react';

export default function RevenuePanel({ slot, revenueMetrics }) {
  if (!slot) return null;

  const originalPrice = slot.price || 0;
  const discountPercent = slot.discount_percent || 0;
  const finalPrice = slot.final_price || originalPrice;
  const isBooked = slot.status === 'BOOKED';

  const expNoDiscount = revenueMetrics?.expected_revenue_without_discount ?? Math.round(originalPrice * 0.4);
  const expWithDiscount = revenueMetrics?.expected_revenue_with_discount ?? Math.round(finalPrice * 0.7);
  const expectedGain = Math.round(expWithDiscount - expNoDiscount);

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <DollarSign size={16} color="var(--emerald-light)" />
          <span>Revenue Optimization Metrics</span>
        </div>
        {isBooked && (
          <span className="status-badge booked" style={{ fontSize: '0.7rem' }}>
            <CheckCircle size={12} /> Revenue Captured
          </span>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.75rem', marginBottom: '1rem' }}>
        <div className="decision-metric">
          <div className="metric-label">Original Price</div>
          <div className="metric-value">₹{originalPrice}</div>
        </div>

        <div className="decision-metric">
          <div className="metric-label">Active Discount</div>
          <div className="metric-value" style={{ color: discountPercent > 0 ? '#fb923c' : 'var(--text-secondary)' }}>
            {discountPercent}%
          </div>
        </div>

        <div className="decision-metric">
          <div className="metric-label">Final Price</div>
          <div className="metric-value" style={{ color: 'var(--emerald-light)' }}>
            ₹{finalPrice}
          </div>
        </div>

        <div className="decision-metric">
          <div className="metric-label">Status</div>
          <div className="metric-value" style={{ fontSize: '0.95rem', color: isBooked ? '#34d399' : '#93c5fd' }}>
            {isBooked ? '₹' + finalPrice + ' RECOVERED' : 'UNBOOKED'}
          </div>
        </div>
      </div>

      <div style={{
        background: 'rgba(17, 24, 39, 0.7)',
        border: '1px solid var(--border-light)',
        borderRadius: 'var(--radius-md)',
        padding: '0.9rem 1.1rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: '0.85rem'
      }}>
        <div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>
            Expected Revenue (Probability × Price)
          </div>
          <div style={{ display: 'flex', gap: '1.25rem', marginTop: '0.25rem' }}>
            <span>Without Discount: <strong>₹{expNoDiscount}</strong></span>
            <span>With Discount: <strong style={{ color: 'var(--emerald-light)' }}>₹{expWithDiscount}</strong></span>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>
            Expected Lift
          </div>
          <div style={{ color: expectedGain >= 0 ? '#34d399' : '#f87171', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <TrendingUp size={14} /> +₹{Math.max(0, expectedGain)}
          </div>
        </div>
      </div>
    </div>
  );
}
