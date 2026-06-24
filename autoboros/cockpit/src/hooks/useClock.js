import { useState, useEffect } from 'react';

export function useClock() {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 30000);
    return () => clearInterval(t);
  }, []);
  const days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  return {
    day: days[now.getDay()],
    time: now.toLocaleTimeString('en-AU', { hour: '2-digit', minute: '2-digit', hour12: false })
  };
}
