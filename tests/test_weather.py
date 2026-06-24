from fastapi.testclient import TestClient

from db.database import reset_db
from main import app


client = TestClient(app)


def setup_function():
    reset_db()


def test_weather_fallback_when_provider_unavailable(monkeypatch):
    def fake_fetch(_city):
        raise RuntimeError("provider down")

    monkeypatch.setattr("api.weather.fetch_weather_from_provider", fake_fetch)

    response = client.get("/api/weather/xiamen")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["degraded"] is True
    assert payload["data"]["source"] == "fallback"


def test_weather_uses_cache_when_provider_recovers(monkeypatch):
    def fake_fetch(_city):
        return {
            "code": 1,
            "data": {
                "city": "厦门",
                "weather": "多云",
                "temp": "31",
                "tempn": "26",
                "current": {
                    "temp": "29.8",
                    "humidity": "76%",
                    "weather": "多云",
                    "air": "50",
                },
                "living": [
                    {
                        "name": "旅游指数",
                        "index": "较适宜",
                        "tips": "可以安排轻量行程。",
                    }
                ],
            },
        }

    monkeypatch.setattr("api.weather.fetch_weather_from_provider", fake_fetch)

    first = client.get("/api/weather/xiamen")
    second = client.get("/api/weather/xiamen")

    assert first.status_code == 200
    assert first.json()["data"]["source"] == "live"
    assert second.status_code == 200
    assert second.json()["data"]["source"] == "cache"
