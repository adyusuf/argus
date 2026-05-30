from fastapi import APIRouter, Depends, Header, HTTPException, Request

from app.core.config import settings
from app.core.websocket import broadcast

router = APIRouter(prefix="/internal", tags=["internal"])


async def _verify_internal_token(
    x_internal_token: str = Header(...),
):
    if x_internal_token != settings.secret_key:
        raise HTTPException(status_code=403, detail="Invalid internal token")


@router.post("/broadcast", dependencies=[Depends(_verify_internal_token)])
async def broadcast_event(request: Request):
    body = await request.json()
    await broadcast(body.get("type", "unknown"), body.get("data", {}))
    return {"ok": True}
