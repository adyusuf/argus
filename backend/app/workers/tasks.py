import asyncio
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=2)
def process_camera_task(self, camera_id: str, rtsp_url: str):
    from app.services.ai import get_ai_provider
    from app.services.video.pipeline import process_camera

    async def _run():
        provider = get_ai_provider()
        detections = await process_camera(camera_id, rtsp_url, provider)
        if detections:
            from app.core.database import async_session
            from app.models.event import Event

            async with async_session() as session:
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
        return len(detections)

    return _run_async(_run())


@celery_app.task
def scan_all_cameras():
    from app.core.database import async_session
    from app.models.camera import Camera

    from sqlalchemy import select

    async def _run():
        async with async_session() as session:
            result = await session.execute(
                select(Camera).where(Camera.is_active.is_(True))
            )
            cameras = result.scalars().all()

        for cam in cameras:
            process_camera_task.delay(str(cam.id), cam.rtsp_url)

        logger.info("Queued %d cameras for processing", len(cameras))

    _run_async(_run())
