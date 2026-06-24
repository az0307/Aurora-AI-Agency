import { useApp } from '../context/AppContext';
import NeedCard from './NeedCard';

export default function Hero() {
  const { needsYou } = useApp();
  if (!needsYou.length) {
    return (
      <section className="hero">
        <div className="hero-head"><div className="hero-title">What needs you</div></div>
        <div className="hero-clear"><div className="big">You're clear.</div><div className="sml">The agent has everything else. ✌️</div></div>
      </section>
    );
  }
  return (
    <section className="hero">
      <div className="hero-head">
        <div className="hero-title">What needs you</div>
        <div className="hero-sub">{needsYou.length} thing{needsYou.length>1?'s':''} the agent can't finish without you</div>
      </div>
      <div className="hero-row">
        {needsYou.map(j => <NeedCard key={j.id} job={j} />)}
      </div>
    </section>
  );
}
