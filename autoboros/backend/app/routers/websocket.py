from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services import manager
from app.routers.auth import authenticate_token

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None),
):
    # B2.6 — auth is mandatory. No token (or a bad one) => reject the socket.
    if not token:
        await websocket.close(code=4001)
        return
    # S5 — authenticate_token also rejects revoked (logged-out) tokens.
    user_id = await authenticate_token(token)
    if not user_id:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal(websocket, "pong", {"received": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
