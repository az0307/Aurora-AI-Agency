export default function Stat({ value, label, variant }) {
  return (
    <div className="stat">
      <div className={`v ${variant || ''}`}>{value}</div>
      <div className="l">{label}</div>
    </div>
  );
}
