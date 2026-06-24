import Swatch from './Swatch';

export default function GroupLabel({ label, count, swatch }) {
  return (
    <div className="group-label">
      {swatch && <Swatch color={swatch} />}
      {label} <span className="gc">· {count}</span>
    </div>
  );
}
