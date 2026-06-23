export function formatTimeSaved(mins) {
  if (mins === 0) return '0m';
  const hrs = Math.floor(mins / 60);
  const rem = mins % 60;
  return hrs > 0 ? `${hrs}h ${rem}m` : `${rem}m`;
}
