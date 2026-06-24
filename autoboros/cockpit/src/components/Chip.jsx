export default function Chip({ children, color }) {
  return (
    <span className="chip" style={color ? { color } : undefined}>
      {children}
    </span>
  );
}
