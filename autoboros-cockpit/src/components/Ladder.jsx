import { useApp } from '../context/AppContext';
import Rung from './Rung';
import Eyebrow from './Eyebrow';

export default function Ladder() {
  const { LADDER } = useApp();
  return (
    <section className="legend">
      <Eyebrow text="The autonomy ladder" right="grey = you · green = the agent" />
      <div className="ladder">
        {Object.entries(LADDER).map(([l, d]) => (
          <Rung key={l} level={l} name={d.name} color={d.color} description={d.mean} />
        ))}
      </div>
    </section>
  );
}
