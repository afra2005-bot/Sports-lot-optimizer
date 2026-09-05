import React from 'react';
import ManagerDashboard from './ManagerDashboard';
import CustomerPortal from './CustomerPortal';

export default function SplitView({
  slots,
  selectedSlot,
  onSelectSlot,
  agentStats,
  activities,
  latestDecision,
  onRunAgent,
  onReassessAgent,
  customers,
  selectedCustomer,
  onSelectCustomer,
  notifications,
  onBookSlot,
  isProcessing,
  isBooking,
  bookingSuccess,
  error,
  successMessage
}) {
  return (
    <div className="split-view-container">
      {/* Left Column: Manager Dashboard */}
      <div>
        <div style={{
          background: 'rgba(17, 24, 39, 0.9)',
          padding: '0.6rem 1rem',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-color)',
          marginBottom: '1rem',
          fontSize: '0.85rem',
          fontWeight: 700,
          color: 'var(--emerald-light)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <span>🏢 TURF MANAGER LIVE VIEW</span>
        </div>

        <ManagerDashboard
          slots={slots}
          selectedSlot={selectedSlot}
          onSelectSlot={onSelectSlot}
          agentStats={agentStats}
          activities={activities}
          latestDecision={latestDecision}
          onRunAgent={onRunAgent}
          onReassessAgent={onReassessAgent}
          isProcessing={isProcessing}
          error={error}
          successMessage={successMessage}
        />
      </div>

      {/* Right Column: Customer Mobile Portal */}
      <div>
        <div style={{
          background: 'rgba(17, 24, 39, 0.9)',
          padding: '0.6rem 1rem',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-color)',
          marginBottom: '1rem',
          fontSize: '0.85rem',
          fontWeight: 700,
          color: '#60a5fa',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <span>📱 CUSTOMER MOBILE IN-APP VIEW</span>
        </div>

        <CustomerPortal
          customers={customers}
          selectedCustomer={selectedCustomer}
          onSelectCustomer={onSelectCustomer}
          notifications={notifications}
          onBookSlot={onBookSlot}
          isBooking={isBooking}
          bookingSuccess={bookingSuccess}
          error={error}
        />
      </div>
    </div>
  );
}
