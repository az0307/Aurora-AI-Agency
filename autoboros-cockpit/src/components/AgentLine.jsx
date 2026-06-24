export default function AgentLine({ text, time }) {
  return (
    <div className="agentline">
      <span className="ag">agent</span> · {text}
      <span className="ts">{time}</span>
    </div>
  );
}
