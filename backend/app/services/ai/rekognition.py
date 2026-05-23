import boto3

from app.core.config import settings
from app.services.ai.provider import AIProvider, Detection


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

    async def detect(self, frame_bytes: bytes) -> list[Detection]:
        response = self._client.detect_labels(
            Image={"Bytes": frame_bytes},
            MaxLabels=10,
            MinConfidence=70,
        )
        return [
            Detection(
                label=label["Name"],
                confidence=round(label["Confidence"], 2),
                bounding_box=(
                    label["Instances"][0]["BoundingBox"] if label.get("Instances") else None
                ),
            )
            for label in response.get("Labels", [])
        ]
