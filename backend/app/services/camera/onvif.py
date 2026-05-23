import logging

logger = logging.getLogger(__name__)


async def discover_cameras(subnet: str = "192.168.1.0/24") -> list[dict]:
    """ONVIF WS-Discovery — placeholder for full implementation."""
    logger.info("ONVIF discovery on %s (stub)", subnet)
    return []


async def get_camera_info(host: str, port: int, username: str, password: str) -> dict | None:
    """Retrieve camera details via ONVIF — placeholder for full implementation."""
    logger.info("ONVIF get_camera_info %s:%d (stub)", host, port)
    return None
