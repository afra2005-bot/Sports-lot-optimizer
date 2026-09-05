import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import ManagerDashboard from './components/ManagerDashboard';
import CustomerPortal from './components/CustomerPortal';
import SplitView from './components/SplitView';
import DemoGuide from './components/DemoGuide';
import { api } from './api';

export default function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [health, setHealth] = useState(null);
  
  // Data State
  const [slots, setSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [agentStats, setAgentStats] = useState(null);
  const [activities, setActivities] = useState([]);
  const [latestDecision, setLatestDecision] = useState(null);
  const [agentStatus, setAgentStatus] = useState('IDLE');

  // Customer State
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [notifications, setNotifications] = useState([]);

  // UI / Async State
  const [loading, setLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isBooking, setIsBooking] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [bookingSuccess, setBookingSuccess] = useState(null);

  // Clear messages after 5 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 6000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  // Initial Data Load
  const loadInitialData = useCallback(async () => {
    setLoading(true);
    try {
      // 1. Health check
      try {
        const h = await api.getHealth();
        setHealth(h);
      } catch (e) {
        console.warn('Backend health check failed:', e);
      }

      // 2. Load slots
      const slotsData = await api.getSlots();
      const loadedSlots = slotsData?.slots || [];
      setSlots(loadedSlots);

      // Select first vacant slot by default if none selected
      const firstVacant = loadedSlots.find((s) => s.status === 'VACANT') || loadedSlots[0];
      if (firstVacant && !selectedSlot) {
        setSelectedSlot(firstVacant);
      }

      // 3. Load customers
      const custList = await api.getCustomers();
      setCustomers(custList || []);

      // Select default demo student (Sneha George CUST0002 or first student)
      if (custList?.length > 0 && !selectedCustomer) {
        const student = custList.find((c) => c.segment === 'STUDENT') || custList[0];
        setSelectedCustomer(student);
      }
    } catch (err) {
      setError(`Failed to connect to backend: ${err.message}. Make sure FastAPI is running on port 8000.`);
    } finally {
      setLoading(false);
    }
  }, [selectedSlot, selectedCustomer]);

  useEffect(() => {
    loadInitialData();
  }, []);

  // Fetch slot-specific agent stats and activity when selectedSlot changes
  const loadSlotDetails = useCallback(async (slotId) => {
    if (!slotId) return;
    try {
      const [statsRes, actRes, statusRes] = await Promise.all([
        api.getSlotStats(slotId).catch(() => null),
        api.getAgentActivity(slotId).catch(() => []),
        api.getAgentStatus(slotId).catch(() => ({ agent_status: 'IDLE' })),
      ]);

      if (statsRes) setAgentStats(statsRes);
      if (actRes) setActivities(actRes);
      if (statusRes?.agent_status) setAgentStatus(statusRes.agent_status);

      // If there's recent activity with a decision, derive latest decision
      if (actRes?.length > 0) {
        const lastNotif = [...actRes].reverse().find((a) => 
          ['NOTIFY', 'DISCOUNT', 'REASSESS', 'STOP'].includes(a.action)
        );
        if (lastNotif && !latestDecision) {
          setLatestDecision({
            action: lastNotif.action === 'DISCOUNT' ? 'NOTIFY_WITH_DISCOUNT' : lastNotif.action,
            segment: lastNotif.target_segment,
            discount_percent: lastNotif.discount_percent || 0,
            wait_minutes: 30,
            reason: lastNotif.reason || '',
          });
        }
      }
    } catch (err) {
      console.error('Error loading slot details:', err);
    }
  }, [latestDecision]);

  useEffect(() => {
    if (selectedSlot?.id) {
      loadSlotDetails(selectedSlot.id);
    }
  }, [selectedSlot?.id, loadSlotDetails]);

  // Fetch customer notifications when selectedCustomer changes
  const loadCustomerNotifications = useCallback(async (customerId) => {
    if (!customerId) return;
    try {
      const notifs = await api.getCustomerNotifications(customerId);
      setNotifications(notifs || []);
    } catch (err) {
      console.error('Error loading customer notifications:', err);
    }
  }, []);

  useEffect(() => {
    if (selectedCustomer?.id) {
      loadCustomerNotifications(selectedCustomer.id);
    }
  }, [selectedCustomer?.id, loadCustomerNotifications]);

  // Handle slot selection
  const handleSelectSlot = (slot) => {
    setSelectedSlot(slot);
    setLatestDecision(null);
    loadSlotDetails(slot.id);
  };

  // Run AI Agent on selected slot
  const handleRunAgent = async (slotId) => {
    setIsProcessing(true);
    setError(null);
    setAgentStatus('ANALYSING');
    try {
      const res = await api.runAgent(slotId);
      if (res.success) {
        setLatestDecision(res.decision);
        setActivities(res.activity || []);
        if (res.segment_statistics) {
          setAgentStats((prev) => ({
            ...prev,
            segment_statistics: res.segment_statistics,
            revenue_metrics: res.revenue_metrics || prev?.revenue_metrics,
          }));
        }
        if (res.agent_status) setAgentStatus(res.agent_status);

        setSuccessMessage(`AI Agent executed ${res.decision?.action}: Notified ${res.decision?.segment || 'customers'}`);

        // Refresh slots and customer notifications
        const slotsData = await api.getSlots();
        setSlots(slotsData?.slots || []);
        const updatedSelected = slotsData?.slots?.find((s) => s.id === slotId);
        if (updatedSelected) setSelectedSlot(updatedSelected);

        if (selectedCustomer?.id) {
          loadCustomerNotifications(selectedCustomer.id);
        }
      } else {
        setError(res.message || 'Agent run failed');
        setAgentStatus('IDLE');
      }
    } catch (err) {
      setError(`Failed to run agent: ${err.message}`);
      setAgentStatus('IDLE');
    } finally {
      setIsProcessing(false);
    }
  };

  // Reassess Agent
  const handleReassessAgent = async (slotId) => {
    setIsProcessing(true);
    setError(null);
    setAgentStatus('REASSESSING');
    try {
      const res = await api.checkAgent(slotId);
      if (res.success) {
        setLatestDecision(res.decision);
        setActivities(res.activity || []);
        if (res.agent_status) setAgentStatus(res.agent_status);

        setSuccessMessage(`Agent reassessed slot ${slotId}: ${res.decision?.action}`);

        // Refresh slots and customer notifications
        const slotsData = await api.getSlots();
        setSlots(slotsData?.slots || []);
        const updatedSelected = slotsData?.slots?.find((s) => s.id === slotId);
        if (updatedSelected) setSelectedSlot(updatedSelected);

        if (selectedCustomer?.id) {
          loadCustomerNotifications(selectedCustomer.id);
        }
      } else {
        setError(res.message || 'Reassessment failed');
      }
    } catch (err) {
      setError(`Failed to reassess agent: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Book Slot from Customer Portal
  const handleBookSlot = async (customerId, slotId) => {
    setIsBooking(true);
    setError(null);
    setBookingSuccess(null);
    try {
      const res = await api.createBooking(customerId, slotId);
      setBookingSuccess(res);
      setSuccessMessage(`Booking confirmed! Booking ID: ${res.id}`);
      setAgentStatus('BOOKED');

      // Refresh slot list and current slot
      const slotsData = await api.getSlots();
      setSlots(slotsData?.slots || []);
      const updatedSelected = slotsData?.slots?.find((s) => s.id === slotId);
      if (updatedSelected) setSelectedSlot(updatedSelected);

      // Refresh customer notifications
      loadCustomerNotifications(customerId);
      // Refresh timeline
      loadSlotDetails(slotId);
    } catch (err) {
      setError(`Booking failed: ${err.message}`);
    } finally {
      setIsBooking(false);
    }
  };

  // Quick Demo Handlers
  const handleQuickSetupDemo = () => {
    // Find a vacant Badminton slot (e.g. SL0640, SL0641)
    const demoSlot = slots.find((s) => s.status === 'VACANT' && s.sport === 'Badminton') ||
                     slots.find((s) => s.status === 'VACANT') || slots[0];
    if (demoSlot) {
      handleSelectSlot(demoSlot);
    }
    // Select Student Sneha George
    const demoCust = customers.find((c) => c.segment === 'STUDENT') || customers[0];
    if (demoCust) {
      setSelectedCustomer(demoCust);
    }
    setSuccessMessage(`Selected Demo Slot ${demoSlot?.id} (${demoSlot?.sport}) & Student Persona`);
  };

  const handleRunDemoAgent = () => {
    if (selectedSlot?.id) {
      handleRunAgent(selectedSlot.id);
    } else {
      handleQuickSetupDemo();
    }
  };

  const handleReassessDemo = () => {
    if (selectedSlot?.id) {
      handleReassessAgent(selectedSlot.id);
    }
  };

  const handleBookDemoSlot = () => {
    if (selectedCustomer?.id && selectedSlot?.id) {
      handleBookSlot(selectedCustomer.id, selectedSlot.id);
    }
  };

  // Full Refresh
  const handleFullRefresh = () => {
    loadInitialData();
    if (selectedSlot?.id) loadSlotDetails(selectedSlot.id);
    if (selectedCustomer?.id) loadCustomerNotifications(selectedCustomer.id);
  };

  return (
    <div className="app-container">
      {/* Top Navigation */}
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        agentStatus={agentStatus}
        onRefresh={handleFullRefresh}
        loading={loading}
        health={health}
      />

      {/* Main Content Area */}
      <main className="main-content">
        {/* Interactive Demo Walkthrough Bar */}
        <DemoGuide
          onQuickSetupDemo={handleQuickSetupDemo}
          onRunDemoAgent={handleRunDemoAgent}
          onReassessDemo={handleReassessDemo}
          onBookDemoSlot={handleBookDemoSlot}
          isProcessing={isProcessing || isBooking}
        />

        {/* Tab 1: Turf Manager Dashboard */}
        {currentTab === 'dashboard' && (
          <ManagerDashboard
            slots={slots}
            selectedSlot={selectedSlot}
            onSelectSlot={handleSelectSlot}
            agentStats={agentStats}
            activities={activities}
            latestDecision={latestDecision}
            onRunAgent={handleRunAgent}
            onReassessAgent={handleReassessAgent}
            isProcessing={isProcessing}
            error={error}
            successMessage={successMessage}
          />
        )}

        {/* Tab 2: Customer In-App Portal */}
        {currentTab === 'customer' && (
          <CustomerPortal
            customers={customers}
            selectedCustomer={selectedCustomer}
            onSelectCustomer={setSelectedCustomer}
            notifications={notifications}
            onBookSlot={handleBookSlot}
            isBooking={isBooking}
            bookingSuccess={bookingSuccess}
            error={error}
          />
        )}

        {/* Tab 3: Split Live View */}
        {currentTab === 'split' && (
          <SplitView
            slots={slots}
            selectedSlot={selectedSlot}
            onSelectSlot={handleSelectSlot}
            agentStats={agentStats}
            activities={activities}
            latestDecision={latestDecision}
            onRunAgent={handleRunAgent}
            onReassessAgent={handleReassessAgent}
            customers={customers}
            selectedCustomer={selectedCustomer}
            onSelectCustomer={setSelectedCustomer}
            notifications={notifications}
            onBookSlot={handleBookSlot}
            isProcessing={isProcessing}
            isBooking={isBooking}
            bookingSuccess={bookingSuccess}
            error={error}
            successMessage={successMessage}
          />
        )}
      </main>
    </div>
  );
}
