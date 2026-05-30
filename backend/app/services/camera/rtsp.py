import io
import logging
from urllib.parse import urlparse

import av
from PIL import Image

logger = logging.getLogger(__name__)

_ALLOWED_SCHEMES = ("rtsp", "rtsps")


def _validate_url(rtsp_url: str) -> bool:
    parsed = urlparse(rtsp_url)
    return parsed.scheme in _ALLOWED_SCHEMES and bool(parsed.hostname)


def grab_frame(rtsp_url: str) -> bytes | None:
    if not _validate_url(rtsp_url):
        logger.error("Rejected non-RTSP URL: %s", rtsp_url.split("@")[-1])
        return None
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
        logger.exception("Failed to grab frame from %s", rtsp_url.split("@")[-1])
    return None


def check_stream(rtsp_url: str) -> bool:
    if not _validate_url(rtsp_url):
        return False
    try:
        container = av.open(rtsp_url, timeout=5)
        container.close()
        return True
    except Exception:
        return False
