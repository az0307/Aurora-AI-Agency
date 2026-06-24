export default function Badge({ level, name }) {
  return (
    <span className={`badge b${level}`}>
      L{level} · {name}
    </span>
  );
}
