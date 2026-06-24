import { useApp } from '../context/AppContext';
import { formatTimeSaved } from '../utils/formatTime';
import Stat from './Stat';

export default function Stats() {
  const { filteredJobs } = useApp();
  const doneAgent = filteredJobs.filter(j => j.status === 'Done' && j.actor === 'Agent');
  const awaiting = filteredJobs.filter(j => j.actor === 'You' && j.status === 'Waiting on you').length;
  const escs = filteredJobs.filter(j => j.esc).length;
  const mins = doneAgent.reduce((a, j) => a + (j.est || 0), 0);

  return (
    <section className="stats">
      <Stat value={doneAgent.length} label="done by the agent today" variant="green" />
      <Stat value={awaiting} label="awaiting you" variant="amber" />
      <Stat value={escs} label={`escalation${escs !== 1 ? 's' : ''}`} variant={escs ? 'red' : ''} />
      <Stat value={formatTimeSaved(mins)} label="time the agent saved you" />
    </section>
  );
}
