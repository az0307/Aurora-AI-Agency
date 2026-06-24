export default function EmptyState({ title = 'No matches', subtitle = 'Try a different search term or clear the filter.' }) {
  return (
    <div className="empty">
      <b>{title}</b>
      {subtitle}
    </div>
  );
}
