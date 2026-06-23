import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('ab_token');
    if (!token) { setLoading(false); return; }
    api.auth.me()
      .then(setUser)
      .catch(() => localStorage.removeItem('ab_token'))
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (password) => {
    const res = await api.auth.login(password);
    setUser(res.user);
    return res;
  }, []);

  const logout = useCallback(() => {
    api.auth.logout();
    setUser(null);
    window.location.reload();
  }, []);

  return { user, loading, login, logout, isAuthed: !!user };
}
