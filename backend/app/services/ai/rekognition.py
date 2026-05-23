import asyncio
import logging
from functools import partial

import boto3

from app.core.config import settings
from app.services.ai.provider import AIProvider, Detection

logger = logging.getLogger(__name__)


class RekognitionProvider(AIProvider):
    def __init__(self):
        self._client = boto3.client(
            "rekognition",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    def provider_name(self) -> str:
        return "rekognition"

    def _detect_sync(self, frame_bytes: bytes) -> list[Detection]:
        response = self._client.detect_labels(
            Image={"Bytes": frame_bytes},
            MaxLabels=10,
            MinConfidence=70,
            Features=["GENERAL_LABELS"],
        )
        detections = []
        for label in response.get("Labels", []):
            bbox = None
            if label.get("Instances"):
                raw = label["Instances"][0]["BoundingBox"]
                bbox = {
                    "left": raw["Left"],
                    "top": raw["Top"],
                    "width": raw["Width"],
                    "height": raw["Height"],
                }
            detections.append(
                Detection(
                    label=label["Name"],
                    confidence=round(label["Confidence"], 2),
                    bounding_box=bbox,
                )
            )
        return detections

    async def detect(self, frame_bytes: bytes) -> list[Detection]:
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(
                None, partial(self._detect_sync, frame_bytes)
            )
        except Exception:
            logger.exception("Rekognition API call failed")
            return []
