import { createContext, useContext, useReducer, useEffect, useCallback, useRef } from 'react';
import { api } from '../api/client';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAuth } from '../hooks/useAuth';
import { filterJobs } from '../utils/filterJobs';
import { LADDER, STATUS_ORDER, CLIENT_ORDER } from '../data/initialData';

const STORAGE_KEY = 'autoboros-cockpit-offline';

function loadOffline() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return null;
}

function saveOffline(state) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      jobs: state.jobs,
      activity: state.activity,
      groupBy: state.groupBy,
    }));
  } catch {}
}

const defaultState = {
  jobs: [],
  activity: [],
  groupBy: 'status',
  search: '',
  drawerId: null,
  toast: null,
  modal: null,
  initialized: false,
  syncError: null,
};

function init() {
  const offline = loadOffline();
  if (offline) {
    return { ...defaultState, ...offline, toast: null, modal: null, drawerId: null };
  }
  return defaultState;
}

function reducer(state, action) {
  switch (action.type) {
    case 'INIT_DATA':
      return { ...state, jobs: action.payload.jobs, activity: action.payload.activity, initialized: true, syncError: null };
    case 'SYNC_ERROR':
      return { ...state, syncError: action.payload };
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
      const jobs = state.jobs.map(j => j.id === action.payload.id ? { ...j, draft: action.payload.draft } : j);
      return { ...state, jobs };
    }
    default: return state;
  }
}

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, undefined, init);
  const { user, loading: authLoading } = useAuth();
  const initRef = useRef(false);

  // Load initial data from API
  useEffect(() => {
    if (authLoading || initRef.current) return;
    initRef.current = true;

    async function load() {
      try {
        const [jobs, activity] = await Promise.all([
          api.jobs.list(),
          api.activity.list(50),
        ]);
        dispatch({ type: 'INIT_DATA', payload: { jobs, activity } });
      } catch (e) {
        console.error('Failed to load data:', e);
        dispatch({ type: 'SYNC_ERROR', payload: e.message });
        // Fall back to offline cache if available
      }
    }
    load();
  }, [authLoading]);

  // Persist to offline cache
  useEffect(() => {
    if (state.initialized) {
      saveOffline(state);
    }
  }, [state.jobs, state.activity, state.groupBy]);

  // WebSocket handler
  const handleWS = useCallback((msg) => {
    switch (msg.event) {
      case 'job_created':
        dispatch({ type: 'JOB_CREATED', payload: msg.data });
        break;
      case 'job_updated':
        dispatch({ type: 'JOB_UPDATED', payload: msg.data });
        break;
      case 'job_deleted':
        dispatch({ type: 'JOB_DELETED', payload: msg.data });
        break;
      case 'activity_new':
        dispatch({ type: 'PUSH_ACTIVITY', payload: msg.data });
        break;
      case 'pong':
        break;
      default:
        console.log('[ws] unknown event:', msg.event);
    }
  }, []);

  const { send: wsSend } = useWebSocket(handleWS);

  const showToast = useCallback((msg) => {
    dispatch({ type: 'SHOW_TOAST', payload: msg });
    setTimeout(() => dispatch({ type: 'HIDE_TOAST' }), 2600);
  }, []);

  // Optimistic actions with API sync
  const act = useCallback(async (id, kind, draftText = null) => {
    const j = state.jobs.find(x => x.id === id);
    if (!j) return;

    // Optimistic update
    const optimistic = getOptimisticUpdate(j, kind, draftText);
    if (optimistic) {
      dispatch({ type: 'JOB_UPDATED', payload: { ...j, ...optimistic } });
    }

    try {
      const result = await api.jobs.action(id, kind, draftText);
      // Server is source of truth — it will broadcast via WS, but we also update directly
      dispatch({ type: 'JOB_UPDATED', payload: result });
      showToast(getToastMessage(kind));
    } catch (e) {
      console.error('Action failed:', e);
      showToast('Failed — check connection');
      // Revert would require snapshotting — for now, next WS sync or refresh fixes it
    }

    dispatch({ type: 'CLOSE_DRAWER' });
  }, [state.jobs, showToast]);

  const createJob = useCallback(async (jobData) => {
    try {
      const result = await api.jobs.create(jobData);
      dispatch({ type: 'JOB_CREATED', payload: result });
      showToast('Job created');
      return result;
    } catch (e) {
      showToast('Failed to create job');
      throw e;
    }
  }, [showToast]);

  const deleteJob = useCallback(async (id) => {
    try {
      await api.jobs.del(id);
      dispatch({ type: 'JOB_DELETED', payload: { id } });
      showToast('Job deleted');
    } catch (e) {
      showToast('Failed to delete');
    }
  }, [showToast]);

  const filteredJobs = filterJobs(state.jobs, state.search);
  const needsYou = filteredJobs.filter(j => j.actor === 'You' && (j.status === 'Waiting on you' || j.status === 'In progress'));

  return (
    <AppContext.Provider value={{
      state, dispatch, showToast, act, createJob, deleteJob,
      filteredJobs, needsYou, LADDER, STATUS_ORDER, CLIENT_ORDER,
      user, authLoading,
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

// --- helpers ---

function getOptimisticUpdate(job, kind, draftText) {
  switch (kind) {
    case 'approve': return { status: 'Done', actor: 'Agent', esc: false, last: { ag: 'Sent after your approval', ts: 'now' } };
    case 'reject': return { status: 'Done', actor: 'You', last: { ag: 'Draft rejected by you — closed', ts: 'now' } };
    case 'ok': return { last: { ag: 'You confirmed — agent continuing', ts: 'now' } };
    case 'veto': return { status: 'Waiting on you', actor: 'You', last: { ag: 'Vetoed — handed to you', ts: 'now' } };
    case 'done': return { status: 'Done', esc: false, last: { ag: 'Marked done by you', ts: 'now' } };
    case 'flag': return { last: { ag: 'Flagged by you for review', ts: 'now' } };
    default: return null;
  }
}

function getToastMessage(kind) {
  switch (kind) {
    case 'approve': return 'Approved & sent';
    case 'reject': return 'Rejected — closed';
    case 'ok': return 'Confirmed';
    case 'veto': return "Vetoed — it's yours now";
    case 'done': return 'Marked done';
    case 'flag': return 'Flagged for review';
    default: return 'Done';
  }
}
