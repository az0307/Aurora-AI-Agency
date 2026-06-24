import { useApp } from '../context/AppContext';
import { groupJobs } from '../utils/groupJobs';
import Card from './Card';
import SegmentedControl from './SegmentedControl';
import GroupLabel from './GroupLabel';
import EmptyState from './EmptyState';
import Eyebrow from './Eyebrow';

const SEGMENTS = [
  { value: 'status', label: 'Status' },
  { value: 'level', label: 'Autonomy' },
  { value: 'client', label: 'Client' },
];

export default function Board() {
  const { state, filteredJobs, LADDER, dispatch } = useApp();
  const groups = groupJobs(filteredJobs, state.groupBy, LADDER).filter(g => g.jobs.length);

  return (
    <div>
      <div className="board-head">
        <Eyebrow text="The board" showRule={false} />
        <SegmentedControl
          options={SEGMENTS}
          value={state.groupBy}
          onChange={v => dispatch({ type: 'SET_GROUP', payload: v })}
        />
      </div>
      <div>
        {groups.map(g => (
          <div className="group" key={g.key}>
            <GroupLabel label={g.label} count={g.jobs.length} swatch={g.swatch} />
            <div className="cards">
              {g.jobs.map(j => <Card key={j.id} job={j} />)}
            </div>
          </div>
        ))}
        {filteredJobs.length === 0 && <EmptyState />}
      </div>
    </div>
  );
}
