export default function LogLine({ type, text, time }) {
  return (
    <div className="logline">
      <span className={`logdot ld-${type}`}></span>
      <div className="logbody">
        <span className="lt">{text}</span>
        <span className="ts">{time}</span>
      </div>
    </div>
  );
}
