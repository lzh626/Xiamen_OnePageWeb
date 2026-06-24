import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


DB_PATH = Path(os.getenv("DB_PATH", str(BASE_DIR / "xiamen_travel.db"))).resolve()
WEATHER_API_URL = os.getenv(
    "WEATHER_API_URL", "http://shanhe.kim/api/za/tianqi.php"
)
WEATHER_TIMEOUT_SECONDS = _get_int("WEATHER_TIMEOUT_SECONDS", 3)
WEATHER_RETRY_COUNT = _get_int("WEATHER_RETRY_COUNT", 2)
WEATHER_CACHE_TTL_SECONDS = _get_int("WEATHER_CACHE_TTL_SECONDS", 1800)
