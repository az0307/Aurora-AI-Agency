import { useApp } from '../context/AppContext';
import Badge from './Badge';

export default function Card({ job }) {
  const { LADDER, dispatch } = useApp();
  const you = job.actor === 'You';
  return (
    <div className={`card acc-${job.lvl}`} onClick={() => dispatch({ type: 'OPEN_DRAWER', payload: job.id })}>
      <div className="c-top">
        <Badge level={job.lvl} name={LADDER[job.lvl].name} />
        {you && <span className="youtag"><span className="dot"></span>you</span>}
      </div>
      <div className="c-title">{job.t}</div>
      <div className="c-meta">
        <span className="src"><span className="cl">{job.client}</span> · {job.src}</span>
      </div>
      <div className="c-last"><span className="ag">agent:</span> {job.last.ag} <span style={{color:'var(--faint)'}}>· {job.last.ts}</span></div>
    </div>
  );
}
