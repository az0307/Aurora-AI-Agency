import { useEffect } from 'react';
import { useApp } from '../context/AppContext';

export function useKeyboard() {
  const { dispatch, state } = useApp();
  useEffect(() => {
    function onKey(e) {
      if (e.key === 'Escape') {
        if (state.drawerId) dispatch({ type: 'CLOSE_DRAWER' });
        else if (state.modal) dispatch({ type: 'CLOSE_MODAL' });
      }
      if (e.key === '/' && !state.drawerId && !state.modal) {
        e.preventDefault();
        document.getElementById('search-input')?.focus();
      }
      if ((e.key === 'n' || e.key === 'N') && !state.drawerId && !state.modal && !e.ctrlKey && !e.metaKey) {
        if (document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
          dispatch({ type: 'OPEN_MODAL', payload: { type: 'new' } });
        }
      }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [dispatch, state.drawerId, state.modal]);
}
