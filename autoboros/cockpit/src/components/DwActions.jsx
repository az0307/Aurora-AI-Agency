import { useApp } from '../context/AppContext';

export default function DwActions({ job }) {
  const { act, dispatch, deleteJob } = useApp();

  if (job.lvl === 2) return (
    <div className="dw-actions">
      <button className="btn btn-ok" onClick={() => act(job.id, 'approve')}>Approve & send</button>
      <button className="btn btn-danger" onClick={() => act(job.id, 'reject')}>Reject</button>
      <button className="btn btn-ghost" onClick={() => dispatch({ type: 'OPEN_MODAL', payload: { type: 'confirm', id: job.id } })}>Delete</button>
    </div>
  );
  if (job.lvl === 3) return (
    <div className="dw-actions">
      <button className="btn btn-ok" onClick={() => act(job.id, 'ok')}>Looks good</button>
      <button className="btn btn-danger" onClick={() => act(job.id, 'veto')}>Veto & take over</button>
      <button className="btn btn-ghost" onClick={() => dispatch({ type: 'OPEN_MODAL', payload: { type: 'confirm', id: job.id } })}>Delete</button>
    </div>
  );
  if (job.lvl === 1 || job.lvl === 0) return (
    <div className="dw-actions">
      <button className="btn btn-primary" onClick={() => act(job.id, 'done')}>Mark done</button>
      <button className="btn btn-ghost" onClick={() => act(job.id, 'notion')}>Open in Notion</button>
      <button className="btn btn-ghost" onClick={() => dispatch({ type: 'OPEN_MODAL', payload: { type: 'confirm', id: job.id } })}>Delete</button>
    </div>
  );
  return (
    <div className="dw-actions">
      <button className="btn btn-ghost" onClick={() => act(job.id, 'flag')}>Flag for review</button>
      {job.result && <button className="btn btn-ghost" onClick={() => act(job.id, 'notion')}>Open result</button>}
      <button className="btn btn-ghost" onClick={() => dispatch({ type: 'OPEN_MODAL', payload: { type: 'confirm', id: job.id } })}>Delete</button>
    </div>
  );
}
