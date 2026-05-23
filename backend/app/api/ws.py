from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.websocket import ws_connect, ws_disconnect

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws_connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await ws_disconnect(ws)
