import React, { useState } from 'react';
import { 
  Play, 
  RotateCw, 
  Filter, 
  Calendar, 
  Clock, 
  Zap, 
  AlertCircle,
  CheckCircle2,
  Tag
} from 'lucide-react';
import SlotCard from './SlotCard';
import DecisionPanel from './DecisionPanel';
import SegmentAnalysis from './SegmentAnalysis';
import RevenuePanel from './RevenuePanel';
import ActivityTimeline from './ActivityTimeline';

export default function ManagerDashboard({
  slots = [],
  selectedSlot,
  onSelectSlot,
  agentStats,
  activities = [],
  latestDecision,
  onRunAgent,
  onReassessAgent,
  isProcessing = false,
  error = null,
  successMessage = null
}) {
  const [sportFilter, setSportFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('VACANT');

  const sports = Array.from(new Set(slots.map((s) => s.sport))).filter(Boolean);

  const filteredSlots = slots.filter((slot) => {
    if (sportFilter && slot.sport !== sportFilter) return false;
    if (statusFilter && slot.status !== statusFilter) return false;
    return true;
  });

  const isVacant = selectedSlot?.status === 'VACANT';
  const isBooked = selectedSlot?.status === 'BOOKED';

  return (
    <div>
      {/* Alert / Notification Banners */}
      {error && (
        <div style={{
          background: 'rgba(244, 63, 94, 0.15)',
          border: '1px solid rgba(244, 63, 94, 0.4)',
          borderRadius: 'var(--radius-md)',
          padding: '0.75rem 1rem',
          marginBottom: '1rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          color: '#fca5a5'
        }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {successMessage && (
        <div style={{
          background: 'rgba(16, 185, 129, 0.15)',
          border: '1px solid rgba(16, 185, 129, 0.4)',
          borderRadius: 'var(--radius-md)',
          padding: '0.75rem 1rem',
          marginBottom: '1rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          color: '#6ee7b7'
        }}>
          <CheckCircle2 size={18} />
          <span>{successMessage}</span>
        </div>
      )}

      <div className="grid-dashboard">
        {/* Left Column: Slot Selection List */}
        <div>
          <div className="card" style={{ marginBottom: '1rem' }}>
            <div className="card-header" style={{ marginBottom: '0.75rem' }}>
              <div className="card-title">
                <Filter size={16} color="var(--emerald-light)" />
                <span>Turf Slots ({filteredSlots.length})</span>
              </div>
            </div>

            {/* Filters */}
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <select 
                style={{
                  flex: 1,
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '0.4rem 0.5rem',
                  color: 'var(--text-primary)',
                  fontSize: '0.8rem'
                }}
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="">All Statuses</option>
                <option value="VACANT">Vacant Only</option>
                <option value="BOOKED">Booked</option>
              </select>

              <select 
                style={{
                  flex: 1,
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '0.4rem 0.5rem',
                  color: 'var(--text-primary)',
                  fontSize: '0.8rem'
                }}
                value={sportFilter}
                onChange={(e) => setSportFilter(e.target.value)}
              >
                <option value="">All Sports</option>
                {sports.map((sp) => (
                  <option key={sp} value={sp}>{sp}</option>
                ))}
              </select>
            </div>

            {/* List of Slot Cards */}
            <div className="slot-list">
              {filteredSlots.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  No slots match your filter.
                </div>
              ) : (
                filteredSlots.map((slot) => (
                  <SlotCard
                    key={slot.id}
                    slot={slot}
                    isSelected={selectedSlot?.id === slot.id}
                    onSelect={onSelectSlot}
                    onRunAgent={onRunAgent}
                    isProcessing={isProcessing}
                  />
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Active Slot Analysis, Decision, Segment Stats, Timeline */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {selectedSlot ? (
            <>
              {/* Selected Slot Header & Controls */}
              <div className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.25rem' }}>
                      <h2 style={{ fontSize: '1.35rem', fontWeight: 700 }}>
                        {selectedSlot.sport} Slot ({selectedSlot.id})
                      </h2>
                      <span className={`status-badge ${selectedSlot.status.toLowerCase()}`}>
                        {selectedSlot.status}
                      </span>
                      {selectedSlot.discount_percent > 0 && (
                        <span className="discount-pill">
                          <Tag size={12} /> {selectedSlot.discount_percent}% OFF
                        </span>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        <Calendar size={14} /> {selectedSlot.date}
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        <Clock size={14} /> {selectedSlot.start_time} - {selectedSlot.end_time}
                      </span>
                    </div>
                  </div>

                  {/* Agent Action Buttons */}
                  <div style={{ display: 'flex', gap: '0.6rem' }}>
                    {isVacant && (
                      <button 
                        className="btn btn-primary"
                        onClick={() => onRunAgent(selectedSlot.id)}
                        disabled={isProcessing}
                      >
                        <Play size={15} />
                        <span>{isProcessing ? 'Agent Thinking...' : 'Run AI Agent'}</span>
                      </button>
                    )}

                    {isVacant && activities.length > 0 && (
                      <button 
                        className="btn btn-secondary"
                        onClick={() => onReassessAgent(selectedSlot.id)}
                        disabled={isProcessing}
                        title="Reassess after waiting period"
                      >
                        <RotateCw size={15} />
                        <span>Reassess Slot</span>
                      </button>
                    )}

                    {isBooked && (
                      <div className="status-badge booked" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>
                        <CheckCircle2 size={16} /> Slot Booked — Agent Stopped
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* AI Decision Card (with Prominent WHY DID THE AGENT DO THIS?) */}
              <DecisionPanel
                decision={latestDecision}
                latestActivity={activities[activities.length - 1]}
                recipientsCount={latestDecision ? (agentStats?.revenue_metrics ? 126 : 0) : 0}
              />

              {/* Customer Segment Analysis */}
              <SegmentAnalysis
                segmentStats={agentStats?.segment_statistics || []}
                selectedSegment={latestDecision?.segment || activities[activities.length - 1]?.target_segment}
              />

              {/* Revenue Optimization Panel */}
              <RevenuePanel
                slot={selectedSlot}
                revenueMetrics={agentStats?.revenue_metrics}
              />

              {/* Agent Activity Timeline */}
              <ActivityTimeline activities={activities} />
            </>
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
              <Zap size={40} color="var(--emerald-light)" style={{ margin: '0 auto 1rem' }} />
              <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Select a Slot to Inspect</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', maxWidth: '400px', margin: '0 auto' }}>
                Pick any vacant sports turf slot from the left to view real-time behavioral analytics and trigger the AI Revenue Agent.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
