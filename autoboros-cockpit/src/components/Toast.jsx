import { useApp } from '../context/AppContext';

export default function Toast() {
  const { state } = useApp();
  return (
    <div className={`toast ${state.toast ? 'show' : ''}`}>
      <span className="tk"></span>
      <span>{state.toast}</span>
    </div>
  );
}
