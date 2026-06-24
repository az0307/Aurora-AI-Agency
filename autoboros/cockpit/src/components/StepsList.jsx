export default function StepsList({ steps }) {
  if (!steps || steps.length === 0) return null;
  return (
    <ol className="steps">
      {steps.map((s, i) => <li key={i}>{s}</li>)}
    </ol>
  );
}
