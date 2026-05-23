import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _make_session() -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(settings.database_url)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def _notify_event(event_data: dict):
    """Best-effort WebSocket broadcast via HTTP to the backend."""
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://backend:8000/api/internal/broadcast",
                json=event_data,
                timeout=2,
            )
    except Exception:
        pass


@celery_app.task(bind=True, max_retries=2)
def process_camera_task(self, camera_id: str, rtsp_url: str):
    from app.services.ai import get_ai_provider
    from app.services.video.pipeline import process_camera
    from app.models.camera import Camera
    from app.models.event import Event

    async def _run():
        provider = get_ai_provider()
        session_factory = _make_session()

        detections = await process_camera(camera_id, rtsp_url, provider)
        stream_ok = detections is not None

        async with session_factory() as session:
            await session.execute(
                update(Camera)
                .where(Camera.id == camera_id)
                .values(
                    status="online" if stream_ok else "offline",
                    last_seen=datetime.now(timezone.utc) if stream_ok else None,
                )
            )

            if detections:
                for d in detections:
                    event = Event(
                        camera_id=camera_id,
                        event_type=d.label,
                        confidence=d.confidence,
                        details=d.bounding_box,
                        ai_provider=provider.provider_name(),
                    )
                    session.add(event)

            await session.commit()

        if detections:
            for d in detections:
                await _notify_event({
                    "type": "new_event",
                    "data": {
                        "camera_id": camera_id,
                        "event_type": d.label,
                        "confidence": d.confidence,
                        "ai_provider": provider.provider_name(),
                    },
                })

        await _notify_event({
            "type": "camera_status",
            "data": {
                "camera_id": camera_id,
                "status": "online" if stream_ok else "offline",
            },
        })

        return len(detections) if detections else 0

    return _run_async(_run())


@celery_app.task
def scan_all_cameras():
    from app.models.camera import Camera

    async def _run():
        session_factory = _make_session()
        async with session_factory() as session:
            result = await session.execute(
                select(Camera).where(Camera.is_active.is_(True))
            )
            cameras = result.scalars().all()

        for cam in cameras:
            process_camera_task.delay(str(cam.id), cam.rtsp_url)

        logger.info("Queued %d cameras for processing", len(cameras))

    _run_async(_run())
