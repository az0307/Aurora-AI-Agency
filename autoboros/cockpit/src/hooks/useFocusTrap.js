import { useEffect, useRef } from 'react';

const FOCUSABLE = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

export function useFocusTrap(active) {
  const containerRef = useRef(null);
  const prevFocus = useRef(null);

  useEffect(() => {
    if (!active) return;
    prevFocus.current = document.activeElement;
    const container = containerRef.current;
    if (!container) return;

    const focusables = Array.from(container.querySelectorAll(FOCUSABLE));
    const first = focusables[0];
    const last = focusables[focusables.length - 1];

    function onKey(e) {
      if (e.key !== 'Tab') return;
      if (focusables.length === 0) { e.preventDefault(); return; }
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }

    container.addEventListener('keydown', onKey);
    first?.focus();
    return () => {
      container.removeEventListener('keydown', onKey);
      prevFocus.current?.focus?.();
    };
  }, [active]);

  return containerRef;
}
