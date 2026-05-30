import io
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.services.ai.provider import AIProvider, Detection
from app.services.camera.rtsp import grab_frame

logger = logging.getLogger(__name__)

FRAMES_DIR = Path("/app/data/frames")
FRAMES_DIR.mkdir(parents=True, exist_ok=True)

_LABEL_COLORS = {
    "person": "#ef4444",
    "car": "#3b82f6",
    "truck": "#3b82f6",
    "bus": "#3b82f6",
    "motorcycle": "#3b82f6",
    "bicycle": "#8b5cf6",
    "dog": "#f59e0b",
    "cat": "#f59e0b",
    "bird": "#f59e0b",
    "knife": "#dc2626",
    "scissors": "#dc2626",
    "backpack": "#22c55e",
    "suitcase": "#22c55e",
    "handbag": "#22c55e",
    "cell phone": "#6366f1",
    "laptop": "#6366f1",
}


def _draw_detections(frame_bytes: bytes, detections: list[Detection]) -> bytes:
    img = Image.open(io.BytesIO(frame_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except (OSError, IOError):
        font = ImageFont.load_default()

    for det in detections:
        if not det.bounding_box:
            continue
        bb = det.bounding_box
        x, y, w, h = bb["x"], bb["y"], bb["width"], bb["height"]
        color = _LABEL_COLORS.get(det.label, "#f59e0b")
        draw.rectangle([x, y, x + w, y + h], outline=color, width=2)

        label_text = f"{det.label} {det.confidence:.0%}"
        text_bbox = draw.textbbox((0, 0), label_text, font=font)
        tw, th = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        label_y = max(y - th - 6, 0)
        draw.rectangle([x, label_y, x + tw + 8, label_y + th + 6], fill=color)
        draw.text((x + 4, label_y + 2), label_text, fill="white", font=font)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


@dataclass
class PipelineResult:
    detections: list[Detection]
    frame_path: str | None


def save_frame(frame_bytes: bytes, camera_id: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{camera_id}_{ts}_{uuid.uuid4().hex[:8]}.jpg"
    path = FRAMES_DIR / filename
    path.write_bytes(frame_bytes)
    return filename


async def process_camera(
    camera_id: str,
    rtsp_url: str,
    ai_provider: AIProvider,
) -> PipelineResult | None:
    """Returns PipelineResult on success, None if stream is unreachable."""
    frame = grab_frame(rtsp_url)
    if frame is None:
        logger.warning("No frame captured from camera %s", camera_id)
        return None

    detections = await ai_provider.detect(frame)

    if detections:
        annotated = _draw_detections(frame, detections)
        frame_path = save_frame(annotated, camera_id)
        logger.info(
            "Camera %s: %d detections — %s",
            camera_id,
            len(detections),
            [d.label for d in detections],
        )
    else:
        frame_path = save_frame(frame, camera_id)

    return PipelineResult(detections=detections, frame_path=frame_path)
