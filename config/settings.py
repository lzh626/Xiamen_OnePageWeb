import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


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

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
LLM_TIMEOUT_SECONDS = _get_int("LLM_TIMEOUT_SECONDS", 10)
RECOMMENDER_TYPE = os.getenv("RECOMMENDER_TYPE", "rule")
