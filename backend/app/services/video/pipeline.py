import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.services.ai.provider import AIProvider, Detection
from app.services.camera.rtsp import grab_frame

logger = logging.getLogger(__name__)

FRAMES_DIR = Path("/app/data/frames")
FRAMES_DIR.mkdir(parents=True, exist_ok=True)


def save_frame(frame_bytes: bytes, camera_id: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{camera_id}_{ts}_{uuid.uuid4().hex[:8]}.jpg"
    path = FRAMES_DIR / filename
    path.write_bytes(frame_bytes)
    return str(path)


async def process_camera(
    camera_id: str,
    rtsp_url: str,
    ai_provider: AIProvider,
) -> list[Detection]:
    frame = grab_frame(rtsp_url)
    if frame is None:
        logger.warning("No frame captured from camera %s", camera_id)
        return []

    detections = await ai_provider.detect(frame)
    if detections:
        save_frame(frame, camera_id)
        logger.info(
            "Camera %s: %d detections — %s",
            camera_id,
            len(detections),
            [d.label for d in detections],
        )
    return detections
