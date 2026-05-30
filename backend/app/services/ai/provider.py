from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class Detection:
    label: str
    confidence: float
    bounding_box: dict | None = None


class AIProvider(ABC):
    @abstractmethod
    async def detect(self, frame_bytes: bytes) -> list[Detection]:
        ...

    @abstractmethod
    def provider_name(self) -> str:
        ...


def get_ai_provider() -> AIProvider:
    if settings.ai_provider == "rekognition":
        from app.services.ai.rekognition import RekognitionProvider
        return RekognitionProvider()
    if settings.ai_provider == "yolo":
        from app.services.ai.yolo import YoloProvider
        return YoloProvider()
    from app.services.ai.mock import MockProvider
    return MockProvider()
