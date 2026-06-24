import { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { filterJobs } from '../utils/filterJobs';
import { LADDER, STATUS_ORDER, CLIENT_ORDER, INITIAL_JOBS, INITIAL_ACTIVITY } from '../data/initialData';

const LS_JOBS = 'autoboros_jobs';
const LS_ACTIVITY = 'autoboros_activity';
const LS_GROUP = 'autoboros_groupBy';

function loadSaved() {
  try {
    const jobs = JSON.parse(localStorage.getItem(LS_JOBS));
    const activity = JSON.parse(localStorage.getItem(LS_ACTIVITY));
    const groupBy = localStorage.getItem(LS_GROUP) || 'status';
    return {
      jobs: jobs ?? INITIAL_JOBS,
      activity: activity ?? INITIAL_ACTIVITY,
      groupBy,
    };
  } catch {
    return { jobs: INITIAL_JOBS, activity: INITIAL_ACTIVITY, groupBy: 'status' };
  }
}

function init() {
  const saved = loadSaved();
  return {
    jobs: saved.jobs,
    activity: saved.activity,
    groupBy: saved.groupBy,
    search: '',
    drawerId: null,
    toast: null,
    modal: null,
  };
}

function reducer(state, action) {
  switch (action.type) {
    case 'SET_GROUP': return { ...state, groupBy: action.payload };
    case 'SET_SEARCH': return { ...state, search: action.payload };
    case 'OPEN_DRAWER': return { ...state, drawerId: action.payload };
    case 'CLOSE_DRAWER': return { ...state, drawerId: null };
    case 'SHOW_TOAST': return { ...state, toast: action.payload };
    case 'HIDE_TOAST': return { ...state, toast: null };
    case 'OPEN_MODAL': return { ...state, modal: action.payload };
    case 'CLOSE_MODAL': return { ...state, modal: null };
    case 'JOB_CREATED':
      return { ...state, jobs: [action.payload, ...state.jobs] };
    case 'JOB_UPDATED': {
      const jobs = state.jobs.map(j => j.id === action.payload.id ? action.payload : j);
      return { ...state, jobs };
    }
    case 'JOB_DELETED': {
      const jobs = state.jobs.filter(j => j.id !== action.payload.id);
      return { ...state, jobs };
    }
    case 'PUSH_ACTIVITY': {
      const activity = [action.payload, ...state.activity].slice(0, 50);
      return { ...state, activity };
    }
    case 'UPDATE_DRAFT': {
      const jobs = state.jobs.map(j =>
        j.id === action.payload.id ? { ...j, draft: action.payload.draft } : j
      );
      return { ...state, jobs };
    }
    default: return state;
  }
}

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, undefined, init);

  useEffect(() => {
    try { localStorage.setItem(LS_JOBS, JSON.stringify(state.jobs)); } catch {}
  }, [state.jobs]);

  useEffect(() => {
    try { localStorage.setItem(LS_ACTIVITY, JSON.stringify(state.activity)); } catch {}
  }, [state.activity]);

  useEffect(() => {
    try { localStorage.setItem(LS_GROUP, state.groupBy); } catch {}
  }, [state.groupBy]);

  const showToast = useCallback((msg) => {
    dispatch({ type: 'SHOW_TOAST', payload: msg });
    setTimeout(() => dispatch({ type: 'HIDE_TOAST' }), 2600);
  }, []);

  const pushActivity = useCallback((type, text) => {
    dispatch({
      type: 'PUSH_ACTIVITY',
      payload: { id: Date.now(), type, t: text, ts: new Date().toISOString() },
    });
  }, []);

  const act = useCallback((id, kind) => {
    const j = state.jobs.find(x => x.id === id);
    if (!j) return;
    const now = new Date().toISOString();
    const map = {
      approve: { upd: { status: 'Done', actor: 'Agent', esc: false, last: { ag: 'Sent after your approval', ts: now } }, toast: 'Approved & sent', at: 'you', atxt: `Approved "${j.t}" — sent` },
      reject:  { upd: { status: 'Done', actor: 'You', last: { ag: 'Draft rejected by you — closed', ts: now } }, toast: 'Rejected — closed', at: 'you', atxt: `Rejected "${j.t}"` },
      ok:      { upd: { last: { ag: 'You confirmed — agent continuing', ts: now } }, toast: 'Confirmed', at: 'you', atxt: `Confirmed "${j.t}"` },
      veto:    { upd: { status: 'Waiting on you', actor: 'You', last: { ag: 'Vetoed — handed to you', ts: now } }, toast: "Vetoed — it's yours now", at: 'warn', atxt: `Vetoed "${j.t}"` },
      done:    { upd: { status: 'Done', esc: false, last: { ag: 'Marked done by you', ts: now } }, toast: 'Marked done', at: 'ok', atxt: `"${j.t}" done` },
      flag:    { upd: { last: { ag: 'Flagged by you for review', ts: now } }, toast: 'Flagged for review', at: 'warn', atxt: `Flagged "${j.t}"` },
    };
    const a = map[kind];
    if (!a) return;
    dispatch({ type: 'JOB_UPDATED', payload: { ...j, ...a.upd } });
    pushActivity(a.at, a.atxt);
    showToast(a.toast);
    dispatch({ type: 'CLOSE_DRAWER' });
  }, [state.jobs, showToast, pushActivity]);

  const createJob = useCallback((jobData) => {
    const job = {
      ...jobData,
      id: Date.now(),
      esc: false,
      est: 0,
      last: { ag: 'Created by you', ts: new Date().toISOString() },
    };
    dispatch({ type: 'JOB_CREATED', payload: job });
    pushActivity('you', `New job: "${job.t}"`);
    showToast('Job created');
    return job;
  }, [showToast, pushActivity]);

  const deleteJob = useCallback((id) => {
    const j = state.jobs.find(x => x.id === id);
    dispatch({ type: 'JOB_DELETED', payload: { id } });
    if (j) pushActivity('info', `Deleted: "${j.t}"`);
    showToast('Job deleted');
  }, [state.jobs, showToast, pushActivity]);

  const filteredJobs = filterJobs(state.jobs, state.search);
  const needsYou = filteredJobs.filter(
    j => j.actor === 'You' && (j.status === 'Waiting on you' || j.status === 'In progress')
  );

  return (
    <AppContext.Provider value={{
      state, dispatch, showToast, act, createJob, deleteJob,
      filteredJobs, needsYou, LADDER, STATUS_ORDER, CLIENT_ORDER,
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be inside AppProvider');
  return ctx;
}
