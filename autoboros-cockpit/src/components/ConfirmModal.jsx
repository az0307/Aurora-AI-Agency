import { useRef, useEffect } from 'react';
import { useApp } from '../context/AppContext';

export default function ConfirmModal() {
  const { state, dispatch, deleteJob } = useApp();
  const ref = useRef(null);
  const j = state.modal?.type === 'confirm' ? state.jobs.find(x => x.id === state.modal.id) : null;

  useEffect(() => {
    if (j && ref.current) ref.current.focus();
  }, [j]);

  if (!j) return null;

  async function handleDelete() {
    await deleteJob(j.id);
    dispatch({ type: 'CLOSE_MODAL' });
  }

  return (
    <div className="modal-scrim show" onClick={e => { if (e.target === e.currentTarget) dispatch({ type: 'CLOSE_MODAL' }); }}>
      <div className="modal" ref={ref} tabIndex={-1} role="dialog" aria-modal="true" aria-labelledby="confirm-title">
        <h2 id="confirm-title">Delete job?</h2>
        <div className="confirm-body">
          This will permanently remove <strong style={{color:'var(--white)'}}>&#34;{j.t}&#34;</strong> from the board.
          This action cannot be undone.
        </div>
        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={() => dispatch({ type: 'CLOSE_MODAL' })}>Cancel</button>
          <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
        </div>
      </div>
    </div>
  );
}
