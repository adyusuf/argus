from fastapi import APIRouter, Request

from app.core.websocket import broadcast

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/broadcast")
async def broadcast_event(request: Request):
    body = await request.json()
    await broadcast(body.get("type", "unknown"), body.get("data", {}))
    return {"ok": True}
