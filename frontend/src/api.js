/**
 * SportsLot Optimizer — API Client
 * Connects React frontend directly to FastAPI backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!res.ok) {
      let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
      try {
        const errorData = await res.json();
        if (errorData.detail) {
          errorDetail = typeof errorData.detail === 'string' 
            ? errorData.detail 
            : JSON.stringify(errorData.detail);
        }
      } catch {
        // Ignore json parse error
      }
      throw new Error(errorDetail);
    }

    return await res.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Health
  getHealth: () => fetchJson('/api/health'),

  // Slots
  getSlots: (status = '', sport = '') => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (sport) params.append('sport', sport);
    const query = params.toString() ? `?${params.toString()}` : '';
    return fetchJson(`/api/slots${query}`);
  },
  getSlot: (slotId) => fetchJson(`/api/slots/${slotId}`),

  // Customers
  getCustomers: () => fetchJson('/api/customers'),
  getCustomer: (customerId) => fetchJson(`/api/customers/${customerId}`),
  getCustomerNotifications: (customerId) => fetchJson(`/api/customers/${customerId}/notifications`),

  // Bookings
  createBooking: (customerId, slotId) =>
    fetchJson('/api/bookings', {
      method: 'POST',
      body: JSON.stringify({ customer_id: customerId, slot_id: slotId }),
    }),

  // Agent
  getAgentActivity: (slotId) => fetchJson(`/api/agent/activity/${slotId}`),
  getSlotStats: (slotId) => fetchJson(`/api/agent/stats/${slotId}`),
  getAgentStatus: (slotId) => fetchJson(`/api/agent/status/${slotId}`),
  runAgent: (slotId) =>
    fetchJson(`/api/agent/run/${slotId}`, {
      method: 'POST',
    }),
  checkAgent: (slotId) =>
    fetchJson(`/api/agent/check/${slotId}`, {
      method: 'POST',
    }),
};
