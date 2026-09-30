import { useEffect, useRef, useCallback } from 'react';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws';
const RECONNECT_DELAY = 3000;
const MAX_RECONNECTS = 10;

export function useWebSocket(onMessage) {
  const wsRef = useRef(null);
  const reconnectCount = useRef(0);
  const reconnectTimer = useRef(null);
  const disposed = useRef(false);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const connect = useCallback(() => {
    if (disposed.current || wsRef.current?.readyState === WebSocket.OPEN) return;

    const token = localStorage.getItem('ab_token');
    if (!token) {
      // B5 — WS auth is mandatory; don't open a tokenless socket (server closes 4001).
      // No retry timer: the caller calls connect() again once a user logs in.
      return;
    }
    const url = `${WS_URL}?token=${encodeURIComponent(token)}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      reconnectCount.current = 0;
      console.log('[ws] connected');
    };

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        onMessageRef.current?.(msg);
      } catch (err) {
        console.error('[ws] parse error', err);
      }
    };

    ws.onclose = () => {
      console.log('[ws] closed');
      if (disposed.current || wsRef.current !== ws) return;
      if (reconnectCount.current < MAX_RECONNECTS) {
        reconnectCount.current++;
        reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY);
      }
    };

    ws.onerror = (err) => {
      console.error('[ws] error', err);
      ws.close();
    };
  }, []);

  useEffect(() => {
    disposed.current = false;
    connect();
    return () => {
      disposed.current = true;
      clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  return { send, connect };
}
