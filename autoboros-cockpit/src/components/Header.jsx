import { useClock } from '../hooks/useClock';

export default function Header() {
  const { day, time } = useClock();
  return (
    <header>
      <div>
        <div className="wordmark">AUTOBOROS <span>/ cockpit</span></div>
        <div className="stacktag">engine <b>Claude Agent SDK</b> · store <b>Notion</b> · hands <b>MCP + Activepieces</b> · brain <b>AutoBoros skills</b></div>
      </div>
      <div className="clock"><span className="day">{day}</span><br/><span>{time}</span> AEST</div>
    </header>
  );
}
