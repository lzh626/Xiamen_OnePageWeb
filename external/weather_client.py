import time

import httpx

from config.settings import (
    WEATHER_API_URL,
    WEATHER_RETRY_COUNT,
    WEATHER_TIMEOUT_SECONDS,
)


def fetch_weather_from_provider(city: str):
    last_error = None
    params = {"city": city, "type": "json"}

    for _ in range(WEATHER_RETRY_COUNT):
        try:
            response = httpx.get(
                WEATHER_API_URL,
                params=params,
                timeout=WEATHER_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            payload = response.json()
            if payload.get("code") != 1 or "data" not in payload:
                raise ValueError("天气接口返回空数据")
            return payload
        except (httpx.HTTPError, ValueError) as exc:
            last_error = exc
            time.sleep(0.2)

    raise RuntimeError(f"天气接口请求失败: {last_error}")


def normalize_weather(payload: dict):
    data = payload.get("data", {})
    current = data.get("current", {})
    living = data.get("living", [])

    tourism_index = "暂无"
    tourism_tips = "天气服务暂不可用，请灵活安排行程。"
    for item in living:
        if "旅游" in item.get("name", ""):
            tourism_index = item.get("index", tourism_index)
            tourism_tips = item.get("tips", tourism_tips)
            break

    return {
        "city": data.get("city", "厦门"),
        "today_weather": data.get("weather", "未知"),
        "high_temp": data.get("temp", "--"),
        "low_temp": data.get("tempn", "--"),
        "current_temp": current.get("temp", "--"),
        "current_weather": current.get("weather", data.get("weather", "未知")),
        "humidity": current.get("humidity", "--"),
        "air_quality": current.get("air", "--"),
        "tourism_index": tourism_index,
        "tourism_tips": tourism_tips,
    }


def build_fallback_weather(city: str, reason: str):
    return {
        "city": city,
        "today_weather": "天气待确认",
        "high_temp": "--",
        "low_temp": "--",
        "current_temp": "--",
        "current_weather": "服务降级中",
        "humidity": "--",
        "air_quality": "--",
        "tourism_index": "谨慎安排",
        "tourism_tips": f"天气接口暂不可用，建议以现场天气为准。原因: {reason}",
    }
