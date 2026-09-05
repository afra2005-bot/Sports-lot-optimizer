import React from 'react';
import { Calendar, Clock, Tag, Play } from 'lucide-react';

export default function SlotCard({ slot, isSelected, onSelect, onRunAgent, isProcessing }) {
  const isVacant = slot.status === 'VACANT';
  const hasDiscount = slot.discount_percent > 0;

  const getSportEmoji = (sport) => {
    switch (sport) {
      case 'Badminton': return '🏸';
      case 'Tennis': return '🎾';
      case 'Football (5-a-side)':
      case 'Football (7-a-side)': return '⚽';
      case 'Futsal': return '🥅';
      case 'Box Cricket': return '🏏';
      default: return '🏆';
    }
  };

  return (
    <div 
      className={`slot-item ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect(slot)}
    >
      <div className="slot-item-header">
        <div className="slot-sport-title">
          <span>{getSportEmoji(slot.sport)}</span>
          <span>{slot.sport}</span>
        </div>
        <span className={`status-badge ${slot.status.toLowerCase()}`}>
          {slot.status}
        </span>
      </div>

      <div className="slot-time">
        <Calendar size={13} />
        <span>{slot.date}</span>
        <span style={{ margin: '0 0.25rem' }}>•</span>
        <Clock size={13} />
        <span>{slot.start_time} - {slot.end_time}</span>
      </div>

      <div className="slot-price-row">
        <div className="price-box">
          {hasDiscount && (
            <span className="price-original">₹{slot.price}</span>
          )}
          <span className="price-current">₹{slot.final_price}</span>
          {hasDiscount && (
            <span className="discount-pill" style={{ padding: '0.1rem 0.4rem', fontSize: '0.68rem' }}>
              <Tag size={10} /> {slot.discount_percent}% OFF
            </span>
          )}
        </div>

        {isVacant && (
          <button 
            className="btn btn-primary"
            style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
            onClick={(e) => {
              e.stopPropagation();
              onRunAgent(slot.id);
            }}
            disabled={isProcessing}
          >
            <Play size={12} />
            <span>RUN AI</span>
          </button>
        )}
      </div>
    </div>
  );
}
