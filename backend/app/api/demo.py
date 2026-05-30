from datetime import datetime, timezone

import redis
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/demo", tags=["demo"])

_redis = redis.from_url(settings.redis_url)


@router.post("/start")
async def start_demo():
    now = datetime.now(timezone.utc).timestamp()
    _redis.set("demo:started_at", str(now))
    return {
        "status": "running",
        "duration_seconds": settings.demo_duration_seconds,
        "started_at": now,
    }


@router.post("/stop")
async def stop_demo():
    _redis.delete("demo:started_at")
    return {"status": "stopped"}


@router.get("/status")
async def demo_status():
    started_at = _redis.get("demo:started_at")
    if not started_at:
        return {"status": "stopped", "remaining_seconds": 0}

    elapsed = datetime.now(timezone.utc).timestamp() - float(started_at)
    remaining = max(0, settings.demo_duration_seconds - elapsed)

    if remaining == 0:
        _redis.delete("demo:started_at")
        return {"status": "stopped", "remaining_seconds": 0}

    return {
        "status": "running",
        "remaining_seconds": int(remaining),
        "elapsed_seconds": int(elapsed),
    }
