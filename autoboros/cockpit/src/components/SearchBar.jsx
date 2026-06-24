import { useApp } from '../context/AppContext';

export default function SearchBar() {
  const { state, dispatch } = useApp();
  return (
    <div className="toolbar">
      <div className="search-wrap">
        <input
          id="search-input"
          type="text"
          placeholder="Search jobs, clients, skills…"
          value={state.search}
          onChange={e => dispatch({ type: 'SET_SEARCH', payload: e.target.value })}
        />
      </div>
      <button className="btn btn-primary" onClick={() => dispatch({ type: 'OPEN_MODAL', payload: { type: 'new' } })}>
        + New job
      </button>
      <span className="kbd">/</span>
      <span className="kbd">n</span>
    </div>
  );
}
