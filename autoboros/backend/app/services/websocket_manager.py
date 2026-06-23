import json
from typing import Set, Dict, Any
from fastapi import WebSocket
import structlog

logger = structlog.get_logger()

class ConnectionManager:
    def __init__(self):
        self._connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._connections.add(websocket)
        logger.info("websocket_connected", client=len(self._connections))

    def disconnect(self, websocket: WebSocket):
        self._connections.discard(websocket)
        logger.info("websocket_disconnected", client=len(self._connections))

    async def broadcast(self, event: str, data: Dict[str, Any]):
        """Broadcast a typed event to all connected clients."""
        payload = json.dumps({"event": event, "data": data})
        dead = set()
        for ws in self._connections:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._connections.discard(ws)
        if dead:
            logger.warning("websocket_pruned_dead", count=len(dead))

    async def send_personal(self, websocket: WebSocket, event: str, data: Dict[str, Any]):
        payload = json.dumps({"event": event, "data": data})
        await websocket.send_text(payload)

manager = ConnectionManager()
