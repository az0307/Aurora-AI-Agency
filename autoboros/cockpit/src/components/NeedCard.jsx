import { useApp } from '../context/AppContext';

export default function NeedCard({ job }) {
  const { LADDER, dispatch } = useApp();
  return (
    <div
      className={`need-card ${job.esc ? 'esc' : ''}`}
      style={{ borderLeftColor: LADDER[job.lvl].color }}
      onClick={() => dispatch({ type: 'OPEN_DRAWER', payload: job.id })}
    >
      <div className="nc-client">
        <span>{job.client}</span>
        {job.esc
          ? <span className="esc-pill">escalation</span>
          : <span className={`badge b${job.lvl}`}>L{job.lvl} · {LADDER[job.lvl].name}</span>
        }
      </div>
      <div className="nc-title">{job.t}</div>
      <div className="nc-ask">{job.ask}</div>
      <div className="nc-cta">
        {job.lvl === 2 ? 'Review & approve' : job.lvl === 0 ? 'Handle this' : 'Open'} →
      </div>
    </div>
  );
}
