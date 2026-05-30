import asyncio
import json
import logging
from fastapi import WebSocket

from app.core.config import settings

logger = logging.getLogger(__name__)

_connections: set[WebSocket] = set()
_lock = asyncio.Lock()


async def ws_connect(ws: WebSocket) -> bool:
    async with _lock:
        if len(_connections) >= settings.max_ws_connections:
            await ws.close(code=1013, reason="Too many connections")
            return False
        await ws.accept()
        _connections.add(ws)
    logger.info("WebSocket client connected (%d total)", len(_connections))
    return True


async def ws_disconnect(ws: WebSocket):
    async with _lock:
        _connections.discard(ws)
    logger.info("WebSocket client disconnected (%d total)", len(_connections))


async def broadcast(event_type: str, data: dict):
    message = json.dumps({"type": event_type, "data": data})
    async with _lock:
        dead: list[WebSocket] = []
        for ws in _connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            _connections.discard(ws)
