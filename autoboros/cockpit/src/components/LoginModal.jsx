import { useRef, useEffect, useState } from 'react';
import { useApp } from '../context/AppContext';

export default function LoginModal() {
  const { user, loading, login } = useApp();
  const ref = useRef(null);
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!user && !loading && ref.current) {
      ref.current.focus();
    }
  }, [user, loading]);

  if (user || loading) return null;

  async function submit(e) {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await login(password);
    } catch {
      setError('Wrong password');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="modal-scrim show">
      <div className="modal" ref={ref} tabIndex={-1} style={{maxWidth: 360}}>
        <h2 style={{marginBottom: 8}}>AutoBoros</h2>
        <p style={{color: 'var(--muted)', fontSize: 13, marginBottom: 18}}>Enter your cockpit password</p>
        <form onSubmit={submit}>
          <div className="form-row">
            <input
              ref={ref}
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Password"
              autoFocus
            />
          </div>
          {error && <div style={{color: 'var(--danger)', fontSize: 12, marginBottom: 12}}>{error}</div>}
          <div className="modal-actions" style={{justifyContent: 'stretch'}}>
            <button type="submit" className="btn btn-primary" style={{flex: 1}} disabled={submitting}>
              {submitting ? 'Checking…' : 'Enter cockpit'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
