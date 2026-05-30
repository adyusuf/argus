import asyncio
import io
from functools import lru_cache

from PIL import Image

from app.services.ai.provider import AIProvider, Detection

_SECURITY_LABELS = {
    "person", "bicycle", "car", "motorcycle", "bus", "truck",
    "cat", "dog", "bird", "backpack", "umbrella", "handbag",
    "suitcase", "knife", "scissors", "cell phone", "laptop",
}


@lru_cache(maxsize=1)
def _load_model():
    from ultralytics import YOLO
    return YOLO("yolov8n.pt")


class YoloProvider(AIProvider):
    def provider_name(self) -> str:
        return "yolo"

    async def detect(self, frame_bytes: bytes) -> list[Detection]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._detect_sync, frame_bytes)

    def _detect_sync(self, frame_bytes: bytes) -> list[Detection]:
        model = _load_model()
        img = Image.open(io.BytesIO(frame_bytes))
        results = model(img, verbose=False, conf=0.35)

        detections: list[Detection] = []
        for r in results:
            for box in r.boxes:
                label = r.names[int(box.cls[0])]
                if label not in _SECURITY_LABELS:
                    continue
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append(Detection(
                    label=label,
                    confidence=round(float(box.conf[0]), 2),
                    bounding_box={
                        "x": int(x1), "y": int(y1),
                        "width": int(x2 - x1), "height": int(y2 - y1),
                    },
                ))
        return detections
