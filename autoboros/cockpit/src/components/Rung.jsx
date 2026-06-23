export default function Rung({ level, name, color, description }) {
  return (
    <div className="rung">
      <div className="r-top">
        <span className="r-bar" style={{ background: color }}></span>
        <span className="r-code">L{level}</span>
      </div>
      <div className="r-name">{name}</div>
      <div className="r-desc">{description}</div>
    </div>
  );
}
