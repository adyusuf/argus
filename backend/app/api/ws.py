from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.websocket import ws_connect, ws_disconnect

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    accepted = await ws_connect(ws)
    if not accepted:
        return
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await ws_disconnect(ws)
