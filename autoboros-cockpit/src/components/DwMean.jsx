export default function DwMean({ level, color, text }) {
  return (
    <div className="dw-mean">
      <div className="mlabel" style={{ color }}>
        <span className="mbar" style={{ background: color }}></span>
        What "L{level}" means here
      </div>
      {text}
    </div>
  );
}
