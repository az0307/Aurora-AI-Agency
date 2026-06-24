import { useApp } from '../context/AppContext';
import { useFocusTrap } from '../hooks/useFocusTrap';
import Scrim from './Scrim';
import Chip from './Chip';
import DwMean from './DwMean';
import DwSection from './DwSection';
import SkillTag from './SkillTag';
import StepsList from './StepsList';
import AskBox from './AskBox';
import DraftBox from './DraftBox';
import AgentLine from './AgentLine';
import ResultLink from './ResultLink';
import DwActions from './DwActions';

export default function Drawer() {
  const { state, dispatch, LADDER } = useApp();
  const j = state.jobs.find(x => x.id === state.drawerId);
  const ref = useFocusTrap(!!j);

  if (!j) return null;
  const L = LADDER[j.lvl];

  return (
    <>
      <Scrim show={!!state.drawerId} onClick={() => dispatch({ type: 'CLOSE_DRAWER' })} />
      <div
        className={`drawer ${state.drawerId ? 'show' : ''}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
        ref={ref}
      >
        <button className="dw-close" onClick={() => dispatch({ type: 'CLOSE_DRAWER' })} aria-label="Close drawer">✕</button>
        <div className="dw-client">{j.client} · {j.src}</div>
        <div className="dw-title" id="drawer-title">{j.t}</div>
        <div className="dw-chips">
          <Chip>{j.status}</Chip>
          <Chip color={L.color}>L{j.lvl} · {L.name}</Chip>
          <Chip>actor: {j.actor}</Chip>
          {j.esc && <Chip color="#fca5a5">escalation</Chip>}
        </div>
        <DwMean level={j.lvl} color={L.color} text={L.mean} />

        {(j.skill || (j.steps && j.steps.length)) && (
          <DwSection title="How it gets done">
            <SkillTag skill={j.skill} />
            <StepsList steps={j.steps} />
          </DwSection>
        )}

        {j.ask && (
          <DwSection title={j.actor === 'You' ? 'Your move' : 'For your awareness'}>
            <AskBox text={j.ask} />
          </DwSection>
        )}

        {j.lvl === 2 && j.draft !== undefined && <DraftBox jobId={j.id} draft={j.draft} />}

        <DwSection title="Last agent action">
          <AgentLine text={j.last.ag} time={j.last.ts} />
        </DwSection>

        {j.result && <ResultLink label={j.result.label} url={j.result.url} />}

        <DwActions job={j} />
      </div>
    </>
  );
}
