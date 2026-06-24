import json
from collections import Counter
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from api.weather import _read_cache, get_xiamen_weather
from db.database import get_db_connection

router = APIRouter()

VALID_PREFERENCES = frozenset({"亲子", "摄影", "人文", "海边", "美食", "低强度"})
VALID_DURATIONS = frozenset({"half_day", "one_day"})


class CustomRouteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    attraction_ids: list[int] = Field(min_length=1, max_length=10)
    preferences: list[str] = Field(min_length=1, max_length=6)
    notes: str = Field(default="", max_length=200)


def _get_weather_for_recommend():
    try:
        response = get_xiamen_weather()
        return response["data"]
    except Exception:
        fallback = _read_cache("厦门")
        if fallback:
            return fallback["payload"]
        return {
            "city": "厦门",
            "current_weather": "未知",
            "today_weather": "未知",
            "tourism_index": "暂无",
            "tourism_tips": "天气数据不可用",
        }


def _score_attraction(attraction, preferences, weather):
    score = 0
    reasons = []

    if attraction["intensity_level"] == "low" and "低强度" in preferences:
        score += 20
        reasons.append("低强度友好，适合轻松游玩")

    intensity_bonus = {"low": 15, "medium": 10}
    score += intensity_bonus.get(attraction["intensity_level"], 5)
    score += min(attraction.get("recommend_score", 0) // 5, 20)
    score += min(attraction.get("popularity_score", 0) // 5, 20)

    current_w = weather.get("current_weather", "")
    suitable = attraction.get("suitable_weather", "")
    if current_w and suitable and current_w in suitable:
        score += 25
        reasons.append(f"当前天气{current_w}适合游玩")

    tourism = weather.get("tourism_index", "")
    if tourism in ("适宜", "较适宜"):
        score += 15
        reasons.append(f"旅游指数「{tourism}」")
    elif tourism == "不适宜":
        reasons.append(f"旅游指数「{tourism}」，建议优先考虑室内景点")

    tag_names = attraction.get("tag_names", [])
    for pref in preferences:
        if pref in tag_names:
            score += 15
            reasons.append(f"属于「{pref}」类景点")

    return score, reasons


@router.get("/api/routes/recommend")
def recommend_route(
    preferences: list[str] | None = Query(None),
    duration: str = Query("half_day", pattern="^(half_day|one_day)$"),
):
    selected_prefs = [p for p in (preferences or []) if p in VALID_PREFERENCES]
    if not selected_prefs:
        selected_prefs = list(VALID_PREFERENCES)

    weather = _get_weather_for_recommend()

    conn = get_db_connection()
    try:
        placeholders = ",".join("?" for _ in selected_prefs)
        rows = conn.execute(
            f"""
            SELECT DISTINCT a.*,
                COALESCE(cs.comment_count, 0) AS comment_count,
                COALESCE(fs.favorite_count, 0) AS favorite_count
            FROM attractions AS a
            JOIN attraction_tags AS at2 ON at2.attraction_id = a.id
            JOIN tags AS t ON t.id = at2.tag_id
            LEFT JOIN (SELECT attraction_id, COUNT(*) AS comment_count FROM comments GROUP BY attraction_id) AS cs
                ON cs.attraction_id = a.id
            LEFT JOIN (SELECT attraction_id, COUNT(*) AS favorite_count FROM favorites GROUP BY attraction_id) AS fs
                ON fs.attraction_id = a.id
            WHERE t.name IN ({placeholders})
            ORDER BY a.recommend_score DESC
            """,
            selected_prefs,
        ).fetchall()

        if not rows:
            return {
                "code": 0,
                "msg": "未找到匹配景点，返回全量推荐",
                "data": {"route": [], "reasons": ["当前偏好无匹配景点"], "weather_summary": weather, "matched_weather": weather.get("current_weather", "未知"), "estimated_duration": "0小时"},
            }

        tagged_rows = []
        for row in rows:
            d = dict(row)
            tag_rows = conn.execute(
                "SELECT t2.name FROM tags AS t2 JOIN attraction_tags AS at2 ON at2.tag_id = t2.id WHERE at2.attraction_id = ?",
                (d["id"],),
            ).fetchall()
            d["tag_names"] = [t["name"] for t in tag_rows]
            tagged_rows.append(d)

        scored = []
        for attr in tagged_rows:
            s, r = _score_attraction(attr, selected_prefs, weather)
            scored.append((s, r, attr))

        scored.sort(key=lambda x: x[0], reverse=True)

        max_hours = 2.5 if duration == "half_day" else 5.0
        selected = []
        total_hours = 0.0

        for _, reasons, attr in scored:
            hours = attr.get("recommended_hours", 1.5)
            if total_hours + hours > max_hours + 0.5:
                if total_hours >= max_hours:
                    continue
            selected.append({"attraction": attr, "reasons": reasons})
            total_hours += hours

        return {
            "code": 0,
            "msg": "路线推荐成功",
            "data": {
                "route": selected,
                "reasons": [],
                "weather_summary": weather,
                "matched_weather": weather.get("current_weather", "未知"),
                "estimated_duration": f"{total_hours:.1f}小时",
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()


@router.post("/api/routes/custom")
def create_custom_route(payload: CustomRouteCreate):
    valid_prefs = [p for p in payload.preferences if p in VALID_PREFERENCES]
    if not valid_prefs:
        valid_prefs = list(payload.preferences)

    conn = get_db_connection()
    try:
        placeholders = ",".join("?" for _ in payload.attraction_ids)
        existing = conn.execute(
            f"SELECT id FROM attractions WHERE id IN ({placeholders})",
            payload.attraction_ids,
        ).fetchall()
        existing_ids = {r["id"] for r in existing}

        for aid in payload.attraction_ids:
            if aid not in existing_ids:
                raise HTTPException(status_code=404, detail=f"景点ID {aid} 不存在")

        weather = _get_weather_for_recommend()
        weather_summary = weather.get("current_weather", "未知")

        conn.execute(
            """
            INSERT INTO routes (name, duration_type, preferences, reason_text, weather_summary)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload.name.strip(),
                "custom",
                json.dumps(valid_prefs, ensure_ascii=False),
                payload.notes.strip() or "用户自定义路线",
                weather_summary,
            ),
        )

        route_id = conn.execute("SELECT last_insert_rowid() AS rid").fetchone()["rid"]

        for idx, aid in enumerate(payload.attraction_ids):
            conn.execute(
                "INSERT INTO route_items (route_id, attraction_id, sort_order) VALUES (?, ?, ?)",
                (route_id, aid, idx + 1),
            )

        conn.commit()

        return {
            "code": 0,
            "msg": "路线保存成功",
            "data": {
                "route_id": route_id,
                "name": payload.name.strip(),
                "attraction_count": len(payload.attraction_ids),
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()


@router.get("/api/routes")
def get_saved_routes(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
):
    conn = get_db_connection()
    try:
        total_row = conn.execute("SELECT COUNT(*) AS total FROM routes").fetchone()
        total = int(total_row["total"])

        offset = (page - 1) * page_size
        route_rows = conn.execute(
            "SELECT * FROM routes ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (page_size, offset),
        ).fetchall()

        items = []
        for route in route_rows:
            items_rows = conn.execute(
                """
                SELECT ri.sort_order, a.id, a.name, a.region, a.cover_image
                FROM route_items AS ri
                JOIN attractions AS a ON a.id = ri.attraction_id
                WHERE ri.route_id = ?
                ORDER BY ri.sort_order
                """,
                (route["id"],),
            ).fetchall()
            items.append({
                **dict(route),
                "attractions": [dict(i) for i in items_rows],
            })

        return {
            "code": 0,
            "msg": "success",
            "data": {
                "items": items,
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": max(1, (total + page_size - 1) // page_size),
                    "has_more": offset + page_size < total,
                },
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()


@router.get("/api/routes/{route_id}")
def get_route_detail(route_id: int):
    conn = get_db_connection()
    try:
        route = conn.execute("SELECT * FROM routes WHERE id = ?", (route_id,)).fetchone()
        if route is None:
            raise HTTPException(status_code=404, detail="路线不存在")

        items_rows = conn.execute(
            """
            SELECT ri.sort_order, a.*,
                COALESCE(cs.comment_count, 0) AS comment_count,
                COALESCE(fs.favorite_count, 0) AS favorite_count
            FROM route_items AS ri
            JOIN attractions AS a ON a.id = ri.attraction_id
            LEFT JOIN (SELECT attraction_id, COUNT(*) AS comment_count FROM comments GROUP BY attraction_id) AS cs
                ON cs.attraction_id = a.id
            LEFT JOIN (SELECT attraction_id, COUNT(*) AS favorite_count FROM favorites GROUP BY attraction_id) AS fs
                ON fs.attraction_id = a.id
            WHERE ri.route_id = ?
            ORDER BY ri.sort_order
            """,
            (route_id,),
        ).fetchall()

        return {
            "code": 0,
            "msg": "success",
            "data": {
                **dict(route),
                "attractions": [dict(i) for i in items_rows],
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()
