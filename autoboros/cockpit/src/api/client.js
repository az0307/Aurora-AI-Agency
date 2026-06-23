const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

function getToken() {
  return localStorage.getItem('ab_token');
}

async function fetchJSON(path, opts = {}) {
  const url = `${API_BASE}${path}`;
  const headers = {
    'Content-Type': 'application/json',
    ...opts.headers,
  };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(url, { ...opts, headers });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`${res.status}: ${err}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  jobs: {
    list: () => fetchJSON('/jobs'),
    get: (id) => fetchJSON(`/jobs/${id}`),
    create: (data) => fetchJSON('/jobs', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => fetchJSON(`/jobs/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    action: (id, action, draftText) => fetchJSON(`/jobs/${id}/action`, {
      method: 'POST',
      body: JSON.stringify({ action, draft_text: draftText }),
    }),
    del: (id) => fetchJSON(`/jobs/${id}`, { method: 'DELETE' }),
  },
  activity: {
    list: (limit = 50) => fetchJSON(`/activity?limit=${limit}`),
  },
  auth: {
    login: async (password) => {
      const res = await fetchJSON('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ password }),
      });
      if (res.token) localStorage.setItem('ab_token', res.token);
      return res;
    },
    logout: () => localStorage.removeItem('ab_token'),
    me: () => fetchJSON('/auth/me'),
  },
};
