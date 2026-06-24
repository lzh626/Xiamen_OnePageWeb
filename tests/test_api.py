from fastapi.testclient import TestClient

from db.database import reset_db
from main import app


client = TestClient(app)


def setup_function():
    reset_db()


def test_get_attractions():
    response = client.get("/api/attractions")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]) >= 5
    assert data["data"][0]["favorite_count"] >= 0
    names = [item["name"] for item in data["data"]]
    assert "鼓浪屿" in names
    assert "厦门大学" in names


def test_submit_comment_success():
    response = client.post(
        "/api/comments",
        json={
            "attraction_id": 1,
            "user_name": "测试用户",
            "content": "很适合阶段二联调验证。",
            "submission_token": "unit-test-comment-1",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["comment"]["user_name"] == "测试用户"
    assert payload["data"]["comment_count"] >= 1


def test_submit_comment_duplicate_token():
    comment_payload = {
        "attraction_id": 1,
        "user_name": "测试用户",
        "content": "重复提交应被拦截。",
        "submission_token": "duplicate-comment-token",
    }
    first = client.post("/api/comments", json=comment_payload)
    second = client.post("/api/comments", json=comment_payload)

    assert first.status_code == 200
    assert second.status_code == 409
    assert second.json()["msg"] == "请勿重复提交评论"


def test_submit_favorite_idempotent():
    payload = {
        "attraction_id": 2,
        "device_id": "unit-test-device-1",
    }

    first = client.post("/api/favorites", json=payload)
    second = client.post("/api/favorites", json=payload)

    assert first.status_code == 200
    assert first.json()["data"]["duplicated"] is False
    assert second.status_code == 200
    assert second.json()["data"]["duplicated"] is True


def test_submit_comment_validation_error():
    response = client.post(
        "/api/comments",
        json={
            "attraction_id": 1,
            "user_name": "",
            "content": "",
            "submission_token": "short",
        },
    )

    assert response.status_code == 422
    assert response.json()["msg"] == "参数校验失败"
