import { useApp } from '../context/AppContext';
import LogLine from './LogLine';

export default function Feed() {
  const { state } = useApp();
  return (
    <aside className="feed">
      <h3><span className="live"></span> Agent activity</h3>
      <div>
        {state.activity.slice(0, 11).map((a, i) => (
          <LogLine key={i} type={a.type} text={a.t} time={a.ts} />
        ))}
      </div>
    </aside>
  );
}
