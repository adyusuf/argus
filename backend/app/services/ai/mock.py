import random

from app.services.ai.provider import AIProvider, Detection

_MOCK_LABELS = ["person", "vehicle", "animal", "package", "unknown"]


class MockProvider(AIProvider):
    def provider_name(self) -> str:
        return "mock"

    async def detect(self, frame_bytes: bytes) -> list[Detection]:
        if random.random() < 0.3:
            return [
                Detection(
                    label=random.choice(_MOCK_LABELS),
                    confidence=round(random.uniform(0.7, 0.99), 2),
                    bounding_box={"x": 100, "y": 100, "width": 200, "height": 300},
                )
            ]
        return []
