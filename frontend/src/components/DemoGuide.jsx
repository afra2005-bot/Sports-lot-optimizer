import React from 'react';
import { Sparkles, ArrowRight, Play, RotateCw, CheckCircle2, UserCheck, Bot } from 'lucide-react';

export default function DemoGuide({ 
  currentStep = 1, 
  onQuickSetupDemo, 
  onRunDemoAgent, 
  onReassessDemo, 
  onBookDemoSlot,
  isProcessing = false 
}) {
  return (
    <div className="demo-banner">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Sparkles size={16} color="#60a5fa" />
          <strong style={{ fontSize: '0.85rem' }}>Demo Walkthrough:</strong>
        </div>

        {/* Step 1: Setup Slot */}
        <button 
          className="btn btn-secondary"
          style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
          onClick={onQuickSetupDemo}
          disabled={isProcessing}
        >
          <span className="demo-step-badge">1</span>
          <span>Pick Demo Slot</span>
        </button>

        <ArrowRight size={14} color="var(--text-muted)" />

        {/* Step 2: Run Agent */}
        <button 
          className="btn btn-primary"
          style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
          onClick={onRunDemoAgent}
          disabled={isProcessing}
        >
          <span className="demo-step-badge" style={{ background: '#059669' }}>2</span>
          <Bot size={12} />
          <span>Run AI Agent</span>
        </button>

        <ArrowRight size={14} color="var(--text-muted)" />

        {/* Step 3: Reassess with Discount */}
        <button 
          className="btn btn-secondary"
          style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
          onClick={onReassessDemo}
          disabled={isProcessing}
        >
          <span className="demo-step-badge" style={{ background: '#d97706' }}>3</span>
          <RotateCw size={12} />
          <span>Reassess (Discount)</span>
        </button>

        <ArrowRight size={14} color="var(--text-muted)" />

        {/* Step 4: Customer Books */}
        <button 
          className="btn btn-accent"
          style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
          onClick={onBookDemoSlot}
          disabled={isProcessing}
        >
          <span className="demo-step-badge" style={{ background: '#7c3aed' }}>4</span>
          <UserCheck size={12} />
          <span>Simulate Booking</span>
        </button>
      </div>

      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'none' }}>
        Complete Hackathon Demonstration Mode
      </div>
    </div>
  );
}
