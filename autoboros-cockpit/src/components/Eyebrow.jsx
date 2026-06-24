export default function Eyebrow({ text, count, showRule = true, right }) {
  return (
    <div className="eyebrow">
      {showRule && <span className="rule" style={{width:0}}></span>}
      <span>{text}</span>
      {count !== undefined && <span className="count">{count}</span>}
      {showRule && <span className="rule"></span>}
      {right && <span style={{textTransform:'none',letterSpacing:0,color:'var(--faint)'}}>{right}</span>}
    </div>
  );
}
