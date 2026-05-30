import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import delete, func, select, update
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
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://backend:8000/api/internal/broadcast",
                json=event_data,
                headers={"X-Internal-Token": settings.secret_key},
                timeout=2,
            )
    except Exception:
        logger.warning("Failed to broadcast event", exc_info=True)


@celery_app.task(bind=True, max_retries=2)
def process_camera_task(self, camera_id: str, rtsp_url: str):
    from app.services.ai import get_ai_provider
    from app.services.video.pipeline import process_camera
    from app.models.camera import Camera
    from app.models.event import Event

    async def _run():
        provider = get_ai_provider()
        session_factory = _make_session()

        result = await process_camera(camera_id, rtsp_url, provider)
        stream_ok = result is not None

        async with session_factory() as session:
            update_values = {
                "status": "online" if stream_ok else "offline",
                "last_seen": datetime.now(timezone.utc) if stream_ok else None,
            }
            if result and result.frame_path:
                update_values["last_frame"] = result.frame_path

            await session.execute(
                update(Camera).where(Camera.id == camera_id).values(**update_values)
            )

            if result and result.detections:
                for d in result.detections:
                    event = Event(
                        camera_id=camera_id,
                        event_type=d.label,
                        confidence=d.confidence,
                        details=d.bounding_box,
                        frame_path=result.frame_path,
                        ai_provider=provider.provider_name(),
                    )
                    session.add(event)

            await session.commit()

        if result and result.detections:
            for d in result.detections:
                await _notify_event({
                    "type": "new_event",
                    "data": {
                        "camera_id": camera_id,
                        "event_type": d.label,
                        "confidence": d.confidence,
                        "ai_provider": provider.provider_name(),
                        "frame_path": result.frame_path,
                    },
                })

        await _notify_event({
            "type": "camera_status",
            "data": {
                "camera_id": camera_id,
                "status": "online" if stream_ok else "offline",
                "last_frame": result.frame_path if result else None,
            },
        })

        return len(result.detections) if result else 0

    return _run_async(_run())


@celery_app.task
def scan_all_cameras():
    import redis as redis_lib
    from app.models.camera import Camera

    r = redis_lib.from_url(settings.redis_url)
    started_at = r.get("demo:started_at")
    if not started_at:
        return

    elapsed = datetime.now(timezone.utc).timestamp() - float(started_at)
    if elapsed > settings.demo_duration_seconds:
        r.delete("demo:started_at")
        logger.info("Demo expired after %d seconds, stopping", int(elapsed))
        return

    async def _run():
        from app.models.event import Event as EventModel

        session_factory = _make_session()
        async with session_factory() as session:
            result = await session.execute(
                select(Camera).where(Camera.is_active.is_(True))
            )
            cameras = result.scalars().all()

        for cam in cameras:
            process_camera_task.delay(str(cam.id), cam.rtsp_url)

        async with session_factory() as session:
            count_result = await session.execute(
                select(func.count(EventModel.id))
            )
            total = count_result.scalar() or 0
            if total > 1000:
                oldest = await session.execute(
                    select(EventModel.id)
                    .order_by(EventModel.created_at.desc())
                    .offset(1000)
                )
                ids_to_delete = [row[0] for row in oldest.fetchall()]
                if ids_to_delete:
                    await session.execute(
                        delete(EventModel).where(EventModel.id.in_(ids_to_delete))
                    )
                    await session.commit()
                    logger.info("Pruned %d old events (kept latest 1000)", len(ids_to_delete))

        logger.info("Queued %d cameras for processing (demo: %ds remaining)",
                     len(cameras), int(settings.demo_duration_seconds - elapsed))

    _run_async(_run())
