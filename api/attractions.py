from fastapi import APIRouter, HTTPException

from db.database import get_db_connection

router = APIRouter()


ATTRACTIONS_LIST_SQL = """
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
ORDER BY a.id ASC
"""


@router.get("/api/attractions")
def get_attractions():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(ATTRACTIONS_LIST_SQL)
        rows = cursor.fetchall()
        conn.close()
        return {"code": 0, "msg": "success", "data": [dict(row) for row in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
