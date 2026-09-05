import React, { useState } from 'react';
import { 
  User, 
  Bell, 
  Calendar, 
  Clock, 
  Tag, 
  CheckCircle, 
  Sparkles, 
  AlertCircle,
  PartyPopper,
  Zap
} from 'lucide-react';

export default function CustomerPortal({
  customers = [],
  selectedCustomer,
  onSelectCustomer,
  notifications = [],
  onBookSlot,
  isBooking = false,
  bookingSuccess = null,
  error = null
}) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredCustomers = customers.filter((c) => {
    if (!searchQuery) return true;
    return (
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.segment.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.id.toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  // Recommended demo customers
  const demoPresets = [
    { id: 'CUST0002', label: 'Sneha George (Student)' },
    { id: 'CUST0008', label: 'Divya Rao (Corporate)' },
    { id: 'CUST0009', label: 'Aravind Basheer (Casual)' },
    { id: 'CUST0004', label: 'Meera Iyer (Student - Badminton)' },
  ];

  return (
    <div className="customer-portal-container">
      {/* Success Popup / Banner */}
      {bookingSuccess && (
        <div style={{
          background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(59, 130, 246, 0.2))',
          border: '1px solid var(--emerald-primary)',
          borderRadius: 'var(--radius-lg)',
          padding: '1.25rem',
          marginBottom: '1.5rem',
          boxShadow: '0 0 20px var(--emerald-glow)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <PartyPopper size={24} color="var(--emerald-light)" />
            <h3 style={{ fontSize: '1.15rem', color: '#fff' }}>Booking Confirmed!</h3>
          </div>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            Booking ID: <strong className="font-mono" style={{ color: '#fff' }}>{bookingSuccess.id}</strong>
          </div>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            Final Paid Price: <strong style={{ color: 'var(--emerald-light)' }}>₹{bookingSuccess.final_price}</strong> ({bookingSuccess.discount_percent}% off)
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            ✓ Slot status updated to BOOKED in PostgreSQL • Agent outreach stopped
          </div>
        </div>
      )}

      {error && (
        <div style={{
          background: 'rgba(244, 63, 94, 0.15)',
          border: '1px solid rgba(244, 63, 94, 0.4)',
          borderRadius: 'var(--radius-md)',
          padding: '0.75rem 1rem',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          color: '#fca5a5'
        }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Customer Selector Card */}
      <div className="card customer-selector-card">
        <div className="card-header">
          <div className="card-title">
            <User size={16} color="var(--emerald-light)" />
            <span>Select Active Customer Persona</span>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            150 Customers from Database
          </span>
        </div>

        {/* Quick Demo Persona Chips */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '1rem' }}>
          {demoPresets.map((preset) => (
            <button
              key={preset.id}
              className={`btn ${selectedCustomer?.id === preset.id ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
              onClick={() => {
                const found = customers.find((c) => c.id === preset.id);
                if (found) onSelectCustomer(found);
              }}
            >
              <Zap size={11} />
              <span>{preset.label}</span>
            </button>
          ))}
        </div>

        {/* Customer Select Dropdown */}
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <select
            style={{
              flex: 1,
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '0.6rem 0.8rem',
              color: 'var(--text-primary)',
              fontSize: '0.9rem'
            }}
            value={selectedCustomer?.id || ''}
            onChange={(e) => {
              const found = customers.find((c) => c.id === e.target.value);
              if (found) onSelectCustomer(found);
            }}
          >
            <option value="" disabled>-- Select a customer --</option>
            {customers.map((c) => (
              <option key={c.id} value={c.id}>
                {c.id} — {c.name} ({c.segment}) {c.sport ? `• ${c.sport}` : ''}
              </option>
            ))}
          </select>
        </div>

        {selectedCustomer && (
          <div style={{
            marginTop: '1rem',
            padding: '0.75rem',
            background: 'var(--bg-secondary)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-light)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div>
              <div style={{ fontWeight: 700, fontSize: '1rem' }}>{selectedCustomer.name}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                Preferred Sport: {selectedCustomer.sport || 'Any'}
              </div>
            </div>
            <span className="status-badge" style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--emerald-light)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
              {selectedCustomer.segment}
            </span>
          </div>
        )}
      </div>

      {/* In-App Notifications Feed */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <Bell size={16} color="var(--emerald-light)" />
            <span>In-App Notifications ({notifications.length})</span>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Real-time notifications sent by AI Agent
          </span>
        </div>

        {notifications.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--text-muted)' }}>
            <Bell size={32} style={{ margin: '0 auto 0.5rem', opacity: 0.5 }} />
            <div style={{ fontSize: '0.95rem', fontWeight: 600 }}>No Notifications Yet</div>
            <p style={{ fontSize: '0.8rem', maxWidth: '340px', margin: '0.25rem auto 0' }}>
              When the Turf Manager triggers the AI agent for this customer's segment, personalized alerts and discounts will appear here.
            </p>
          </div>
        ) : (
          <div className="notifications-container">
            {notifications.map((notif) => {
              const isBooked = notif.status === 'BOOKED';
              const hasDiscount = notif.discount_percent > 0;

              return (
                <div 
                  key={notif.id} 
                  className={`notification-card ${isBooked ? 'booked' : 'unread'}`}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <span style={{ fontSize: '1.1rem' }}>
                        {hasDiscount ? '🔥' : '🔔'}
                      </span>
                      <strong style={{ fontSize: '0.95rem' }}>
                        {hasDiscount ? 'Exclusive Slot Discount!' : 'New Slot Available!'}
                      </strong>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      {hasDiscount && (
                        <span className="discount-pill">
                          <Tag size={10} /> {notif.discount_percent}% OFF
                        </span>
                      )}
                      <span className={`status-badge ${isBooked ? 'booked' : 'vacant'}`}>
                        {notif.status}
                      </span>
                    </div>
                  </div>

                  <p style={{ fontSize: '0.88rem', color: 'var(--text-primary)', marginBottom: '0.9rem', lineHeight: 1.5 }}>
                    {notif.message}
                  </p>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.5rem', borderTop: '1px solid var(--border-light)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Slot: <strong className="font-mono" style={{ color: 'var(--text-secondary)' }}>{notif.slot_id}</strong>
                    </span>

                    {!isBooked ? (
                      <button
                        className="btn btn-primary"
                        onClick={() => onBookSlot(selectedCustomer.id, notif.slot_id)}
                        disabled={isBooking}
                        style={{ padding: '0.45rem 1rem' }}
                      >
                        <CheckCircle size={14} />
                        <span>{isBooking ? 'Booking...' : 'Book Now'}</span>
                      </button>
                    ) : (
                      <span style={{ fontSize: '0.8rem', color: 'var(--emerald-light)', fontWeight: 600 }}>
                        ✓ Slot Booked
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
