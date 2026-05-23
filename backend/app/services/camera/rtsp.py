import io
import logging

import av
from PIL import Image

logger = logging.getLogger(__name__)


def grab_frame(rtsp_url: str) -> bytes | None:
    try:
        container = av.open(rtsp_url, timeout=10)
        for frame in container.decode(video=0):
            img = frame.to_image()
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            container.close()
            return buf.getvalue()
        container.close()
    except Exception:
        logger.exception("Failed to grab frame from %s", rtsp_url)
    return None


def check_stream(rtsp_url: str) -> bool:
    try:
        container = av.open(rtsp_url, timeout=5)
        container.close()
        return True
    except Exception:
        return False
