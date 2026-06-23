export function filterJobs(jobs, query) {
  if (!query) return jobs;
  const q = query.toLowerCase();
  return jobs.filter(j =>
    j.t.toLowerCase().includes(q) ||
    j.client.toLowerCase().includes(q) ||
    j.status.toLowerCase().includes(q) ||
    (j.skill && j.skill.toLowerCase().includes(q)) ||
    j.src.toLowerCase().includes(q)
  );
}
