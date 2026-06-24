import sqlite3

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from db.database import get_db_connection


router = APIRouter()


class CommentCreate(BaseModel):
    attraction_id: int = Field(gt=0)
    user_name: str = Field(min_length=1, max_length=20)
    content: str = Field(min_length=1, max_length=200)
    submission_token: str = Field(min_length=8, max_length=100)


class FavoriteCreate(BaseModel):
    attraction_id: int = Field(gt=0)
    device_id: str = Field(min_length=8, max_length=100)


def _attraction_exists(conn, attraction_id: int) -> bool:
    row = conn.execute(
        "SELECT id FROM attractions WHERE id = ?",
        (attraction_id,),
    ).fetchone()
    return row is not None


def _get_comment_count(conn, attraction_id: int) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS total FROM comments WHERE attraction_id = ?",
        (attraction_id,),
    ).fetchone()
    return int(row["total"])


def _get_favorite_count(conn, attraction_id: int) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS total FROM favorites WHERE attraction_id = ?",
        (attraction_id,),
    ).fetchone()
    return int(row["total"])


@router.post("/api/comments")
def create_comment(payload: CommentCreate):
    conn = get_db_connection()
    try:
        if not _attraction_exists(conn, payload.attraction_id):
            raise HTTPException(status_code=404, detail="景点不存在")

        cursor = conn.execute(
            """
            INSERT INTO comments (attraction_id, user_name, content, submission_token)
            VALUES (?, ?, ?, ?)
            """,
            (
                payload.attraction_id,
                payload.user_name.strip(),
                payload.content.strip(),
                payload.submission_token,
            ),
        )
        conn.commit()

        comment = conn.execute(
            """
            SELECT id, attraction_id, user_name, content, created_at
            FROM comments
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
        comment_count = _get_comment_count(conn, payload.attraction_id)
        return {
            "code": 0,
            "msg": "评论提交成功",
            "data": {
                "comment": dict(comment),
                "comment_count": comment_count,
            },
        }
    except sqlite3.IntegrityError as exc:
        if "submission_token" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="请勿重复提交评论",
            ) from exc
        raise
    finally:
        conn.close()


@router.post("/api/favorites")
def create_favorite(payload: FavoriteCreate):
    conn = get_db_connection()
    try:
        if not _attraction_exists(conn, payload.attraction_id):
            raise HTTPException(status_code=404, detail="景点不存在")

        duplicated = False
        try:
            conn.execute(
                """
                INSERT INTO favorites (attraction_id, device_id)
                VALUES (?, ?)
                """,
                (payload.attraction_id, payload.device_id),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            duplicated = True

        favorite_count = _get_favorite_count(conn, payload.attraction_id)
        return {
            "code": 0,
            "msg": "已收藏" if not duplicated else "你已收藏过该景点",
            "data": {
                "attraction_id": payload.attraction_id,
                "favorite_count": favorite_count,
                "duplicated": duplicated,
            },
        }
    finally:
        conn.close()
