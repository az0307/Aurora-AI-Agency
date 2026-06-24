import { useApp } from '../context/AppContext';

export default function DraftBox({ jobId, draft }) {
  const { dispatch } = useApp();
  return (
    <div className="dw-sec">
      <div className="sec-h">The agent's draft — edit before sending</div>
      <textarea
        className="draft"
        defaultValue={draft}
        onChange={e => dispatch({ type: 'UPDATE_DRAFT', payload: { id: jobId, draft: e.target.value } })}
      />
    </div>
  );
}
