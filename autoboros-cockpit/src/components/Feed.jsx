import { useApp } from '../context/AppContext';
import LogLine from './LogLine';
import { formatRelative } from '../utils/formatTime';

export default function Feed() {
  const { state } = useApp();
  return (
    <aside className="feed">
      <h3><span className="live"></span> Agent activity</h3>
      <div>
        {state.activity.slice(0, 11).map((a, i) => (
          <LogLine key={a.id ?? i} type={a.type} text={a.t} time={formatRelative(a.ts)} />
        ))}
      </div>
    </aside>
  );
}
