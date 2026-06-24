import json
from datetime import datetime, timedelta

from fastapi import APIRouter

from config.settings import WEATHER_CACHE_TTL_SECONDS
from db.database import get_db_connection
from external.weather_client import (
    build_fallback_weather,
    fetch_weather_from_provider,
    normalize_weather,
)


router = APIRouter()


def _read_cache(city: str):
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT payload, updated_at FROM weather_cache WHERE city = ?",
            (city,),
        ).fetchone()
        if row is None:
            return None
        return {
            "payload": json.loads(row["payload"]),
            "updated_at": datetime.fromisoformat(row["updated_at"]),
        }
    finally:
        conn.close()


def _write_cache(city: str, payload: dict):
    conn = get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO weather_cache (city, payload, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(city) DO UPDATE SET
                payload = excluded.payload,
                updated_at = excluded.updated_at
            """,
            (city, json.dumps(payload, ensure_ascii=False), datetime.now().isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


@router.get("/api/weather/xiamen")
def get_xiamen_weather():
    city = "厦门"
    cached = _read_cache(city)
    now = datetime.now()

    if cached and now - cached["updated_at"] < timedelta(seconds=WEATHER_CACHE_TTL_SECONDS):
        return {
            "code": 0,
            "msg": "success",
            "data": {
                **cached["payload"],
                "source": "cache",
                "degraded": False,
            },
        }

    try:
        normalized = normalize_weather(fetch_weather_from_provider(city))
        _write_cache(city, normalized)
        return {
            "code": 0,
            "msg": "success",
            "data": {
                **normalized,
                "source": "live",
                "degraded": False,
            },
        }
    except RuntimeError as exc:
        if cached:
            return {
                "code": 0,
                "msg": "天气服务繁忙，已返回缓存数据",
                "data": {
                    **cached["payload"],
                    "source": "stale-cache",
                    "degraded": True,
                },
            }

        fallback = build_fallback_weather(city, str(exc))
        return {
            "code": 0,
            "msg": "天气服务降级",
            "data": {
                **fallback,
                "source": "fallback",
                "degraded": True,
            },
        }
