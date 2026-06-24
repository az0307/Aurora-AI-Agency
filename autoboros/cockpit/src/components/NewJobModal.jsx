import { useRef, useEffect, useState } from 'react';
import { useApp } from '../context/AppContext';
import { LADDER, STATUS_ORDER, CLIENT_ORDER } from '../data/initialData';

export default function NewJobModal() {
  const { state, dispatch, createJob } = useApp();
  const ref = useRef(null);
  const isOpen = state.modal?.type === 'new';

  const [form, setForm] = useState({
    t: '', client: CLIENT_ORDER[0], status: 'Inbox', lvl: 2, actor: 'Agent', src: 'Manual',
    skill: '', steps: '', ask: '', draft: ''
  });

  useEffect(() => {
    if (isOpen && ref.current) ref.current.focus();
  }, [isOpen]);

  if (!isOpen) return null;

  async function submit(e) {
    e.preventDefault();
    if (!form.t.trim()) return;
    const steps = form.steps.split('\n').filter(Boolean);
    const job = {
      t: form.t.trim(),
      client: form.client,
      status: form.status,
      lvl: parseInt(form.lvl),
      actor: form.actor,
      src: form.src,
      skill: form.skill.trim() || null,
      steps: steps.length ? steps : [],
      ask: form.ask.trim() || '',
      draft: form.draft.trim() || undefined,
      esc: false,
      est: 0,
    };
    try {
      await createJob(job);
      dispatch({ type: 'CLOSE_MODAL' });
      setForm({ t: '', client: CLIENT_ORDER[0], status: 'Inbox', lvl: 2, actor: 'Agent', src: 'Manual', skill: '', steps: '', ask: '', draft: '' });
    } catch {
      // toast shown by createJob
    }
  }

  const input = (label, key, type = 'text', placeholder = '') => (
    <div className="form-row">
      <label>{label}</label>
      {type === 'textarea' ? (
        <textarea value={form[key]} onChange={e => setForm(f => ({...f, [key]: e.target.value}))} placeholder={placeholder} />
      ) : (
        <input type={type} value={form[key]} onChange={e => setForm(f => ({...f, [key]: e.target.value}))} placeholder={placeholder} />
      )}
    </div>
  );

  const select = (label, key, options) => (
    <div className="form-row">
      <label>{label}</label>
      <select value={form[key]} onChange={e => setForm(f => ({...f, [key]: e.target.value}))}>
        {options.map(o => typeof o === 'string' ? <option key={o} value={o}>{o}</option> : <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  );

  return (
    <div className="modal-scrim show" onClick={e => { if (e.target === e.currentTarget) dispatch({ type: 'CLOSE_MODAL' }); }}>
      <div className="modal" ref={ref} tabIndex={-1} role="dialog" aria-modal="true" aria-labelledby="newjob-title">
        <h2 id="newjob-title">New job</h2>
        <form onSubmit={submit}>
          {input('Title *', 't', 'text', 'What needs doing?')}
          <div className="form-row" style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:12}}>
            {select('Client', 'client', CLIENT_ORDER)}
            {select('Status', 'status', STATUS_ORDER)}
          </div>
          <div className="form-row" style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:12}}>
            {select('Autonomy level', 'lvl', Object.entries(LADDER).map(([l, d]) => ({ value: l, label: `L${l} · ${d.name}` })))}
            {select('Actor', 'actor', [{value:'Agent',label:'Agent'},{value:'You',label:'You'},{value:'External',label:'External'}])}
          </div>
          {input('Source', 'src', 'text', 'Email, Slack, ManyChat…')}
          {input('Skill tag (optional)', 'skill', 'text', 'e.g. quote-responder')}
          {input('Steps (one per line)', 'steps', 'textarea', '1. Do this\n2. Then that')}
          {input('Ask / human action', 'ask', 'textarea', 'What does the human need to do?')}
          {input('Draft content (optional)', 'draft', 'textarea', 'Pre-written draft for L2 jobs')}
          <div className="modal-actions">
            <button type="button" className="btn btn-ghost" onClick={() => dispatch({ type: 'CLOSE_MODAL' })}>Cancel</button>
            <button type="submit" className="btn btn-primary">Create job</button>
          </div>
        </form>
      </div>
    </div>
  );
}
