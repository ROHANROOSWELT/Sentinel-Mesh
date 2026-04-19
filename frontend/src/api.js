const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(endpoint, options = {}) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export const api = {
  chat: (body) => request('/chat', { method: 'POST', body: JSON.stringify(body) }),
  analyze: (body) => request('/analyze', { method: 'POST', body: JSON.stringify(body) }),
  stats: () => request('/stats'),
  log: (session_id = '', limit = 20) => request(`/log?${session_id ? `session_id=${session_id}&` : ''}limit=${limit}`),
  verifyChain: () => request('/log/verify'),
  benchmark: () => request('/benchmark'),
  health: () => request('/health'),
  reset: () => request('/reset', { method: 'POST' }),
};
