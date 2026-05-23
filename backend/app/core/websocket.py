import asyncio
import json
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)

_connections: set[WebSocket] = set()
_lock = asyncio.Lock()


async def ws_connect(ws: WebSocket):
    await ws.accept()
    async with _lock:
        _connections.add(ws)
    logger.info("WebSocket client connected (%d total)", len(_connections))


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
