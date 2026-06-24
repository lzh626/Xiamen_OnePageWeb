from fastapi import APIRouter, HTTPException, Query
from db.database import get_db_connection

router = APIRouter()

VALID_SORT_FIELDS = frozenset({"id", "name", "popularity_score", "recommend_score", "comment_count", "favorite_count", "created_at"})
VALID_REGIONS = frozenset({"思明区", "湖里区", "集美区", "同安区", "翔安区", "海沧区"})

ATTRACTIONS_DETAIL_SQL = """
SELECT
    a.*,
    COALESCE(comment_stats.comment_count, 0) AS comment_count,
    COALESCE(favorite_stats.favorite_count, 0) AS favorite_count
FROM attractions AS a
LEFT JOIN (
    SELECT attraction_id, COUNT(*) AS comment_count
    FROM comments
    GROUP BY attraction_id
) AS comment_stats
    ON comment_stats.attraction_id = a.id
LEFT JOIN (
    SELECT attraction_id, COUNT(*) AS favorite_count
    FROM favorites
    GROUP BY attraction_id
) AS favorite_stats
    ON favorite_stats.attraction_id = a.id
"""


def _build_filter_clause(
    keyword: str | None,
    region: str | None,
    tag: str | None,
    suitable_weather: str | None,
    duration_max: float | None,
):
    clauses = []
    params: list = []

    if keyword:
        clauses.append("(a.name LIKE ? OR a.description LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    if region:
        if region not in VALID_REGIONS:
            raise HTTPException(status_code=400, detail=f"无效的区域参数，可选值: {', '.join(sorted(VALID_REGIONS))}")
        clauses.append("a.region = ?")
        params.append(region)

    if tag:
        clauses.append("a.id IN (SELECT at2.attraction_id FROM attraction_tags AS at2 JOIN tags AS t2 ON t2.id = at2.tag_id WHERE t2.name = ?)")
        params.append(tag)

    if suitable_weather:
        clauses.append("a.suitable_weather LIKE ?")
        params.append(f"%{suitable_weather}%")

    if duration_max is not None:
        if duration_max <= 0:
            raise HTTPException(status_code=400, detail="duration_max 必须大于 0")
        clauses.append("a.recommended_hours <= ?")
        params.append(duration_max)

    where_sql = " AND ".join(clauses) if clauses else "1=1"
    return where_sql, params


def _row_to_dict(row):
    return dict(row)


def _count_total(conn, where_sql: str, params: list) -> int:
    count_sql = f"""
        SELECT COUNT(*) AS total
        FROM attractions AS a
        LEFT JOIN (
            SELECT attraction_id, COUNT(*) AS comment_count
            FROM comments GROUP BY attraction_id
        ) AS comment_stats ON comment_stats.attraction_id = a.id
        LEFT JOIN (
            SELECT attraction_id, COUNT(*) AS favorite_count
            FROM favorites GROUP BY attraction_id
        ) AS favorite_stats ON favorite_stats.attraction_id = a.id
        WHERE {where_sql}
    """
    row = conn.execute(count_sql, params).fetchone()
    return int(row["total"])


@router.get("/api/attractions")
def get_attractions(
    keyword: str | None = Query(None, min_length=1, max_length=50),
    region: str | None = Query(None, min_length=1, max_length=10),
    tag: str | None = Query(None, min_length=1, max_length=20),
    suitable_weather: str | None = Query(None, min_length=1, max_length=20),
    duration_max: float | None = Query(None, gt=0),
    sort_by: str = Query("recommend_score", min_length=1, max_length=30),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
):
    if sort_by not in VALID_SORT_FIELDS:
        raise HTTPException(status_code=400, detail=f"无效的排序字段，可选值: {', '.join(sorted(VALID_SORT_FIELDS))}")

    direction = "DESC" if order == "desc" else "ASC"
    order_clause = f"{sort_by} {direction}"

    where_sql, params = _build_filter_clause(keyword, region, tag, suitable_weather, duration_max)

    conn = get_db_connection()
    try:
        total = _count_total(conn, where_sql, params)

        offset = (page - 1) * page_size
        query_sql = f"""
            {ATTRACTIONS_DETAIL_SQL}
            WHERE {where_sql}
            ORDER BY {order_clause}
            LIMIT ? OFFSET ?
        """
        rows = conn.execute(query_sql, params + [page_size, offset]).fetchall()
        items = [_row_to_dict(row) for row in rows]

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
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()


@router.get("/api/attractions/{attraction_id}")
def get_attraction_detail(attraction_id: int):
    conn = get_db_connection()
    try:
        row = conn.execute(
            f"{ATTRACTIONS_DETAIL_SQL} WHERE a.id = ?",
            (attraction_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="景点不存在")

        tags = conn.execute(
            """
            SELECT t.id, t.name
            FROM tags AS t
            JOIN attraction_tags AS at2 ON at2.tag_id = t.id
            WHERE at2.attraction_id = ?
            ORDER BY t.id
            """,
            (attraction_id,),
        ).fetchall()

        comments = conn.execute(
            """
            SELECT id, user_name, content, created_at
            FROM comments
            WHERE attraction_id = ?
            ORDER BY created_at DESC
            LIMIT 20
            """,
            (attraction_id,),
        ).fetchall()

        return {
            "code": 0,
            "msg": "success",
            "data": {
                "attraction": dict(row),
                "tags": [dict(t) for t in tags],
                "comments": [dict(c) for c in comments],
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()
