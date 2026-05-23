from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health_returns_200(client):
    with patch("app.api.health.get_db") as mock_db:
        session = AsyncMock()
        mock_db.return_value = session
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
