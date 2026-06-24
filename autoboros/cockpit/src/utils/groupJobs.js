import { STATUS_ORDER, CLIENT_ORDER } from '../data/initialData';

export function groupJobs(jobs, groupBy, LADDER) {
  if (groupBy === 'status') {
    return STATUS_ORDER.map(s => ({ key: s, label: s, swatch: null, jobs: jobs.filter(j => j.status === s) }));
  }
  if (groupBy === 'level') {
    return [4,3,2,1,0].map(l => ({ key: l, label: `L${l} · ${LADDER[l].name}`, swatch: LADDER[l].color, jobs: jobs.filter(j => j.lvl === l) }));
  }
  return CLIENT_ORDER.map(c => ({ key: c, label: c, swatch: null, jobs: jobs.filter(j => j.client === c) }));
}
