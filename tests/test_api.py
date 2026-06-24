import json

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_get_attractions():
    response = client.get("/api/attractions")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "items" in data["data"]
    assert len(data["data"]["items"]) >= 5
    names = [item["name"] for item in data["data"]["items"]]
    assert "鼓浪屿" in names


def test_get_attractions_with_filter():
    response = client.get("/api/attractions?keyword=鼓浪屿")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    items = data["data"]["items"]
    assert len(items) >= 1
    names = [item["name"] for item in items]
    assert "鼓浪屿" in names


def test_get_attractions_with_region():
    response = client.get("/api/attractions?region=思明区")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    items = data["data"]["items"]
    assert len(items) >= 5


def test_get_attractions_with_tag():
    response = client.get("/api/attractions?tag=海边")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    items = data["data"]["items"]
    names = [item["name"] for item in items]
    assert any("鼓浪" in n or "环岛" in n for n in names)


def test_get_attractions_with_sort():
    response = client.get("/api/attractions?sort_by=popularity_score&order=desc")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    items = data["data"]["items"]
    assert len(items) >= 2
    assert items[0]["popularity_score"] >= items[-1]["popularity_score"]


def test_get_attractions_with_pagination():
    response = client.get("/api/attractions?page=1&page_size=3")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]["items"]) <= 3
    assert data["data"]["pagination"]["page"] == 1
    assert data["data"]["pagination"]["page_size"] == 3


def test_get_attractions_invalid_region():
    response = client.get("/api/attractions?region=不存在的区域")
    assert response.status_code == 400


def test_get_attractions_invalid_sort():
    response = client.get("/api/attractions?sort_by=invalid_field")
    assert response.status_code == 400


def test_get_attraction_detail():
    response = client.get("/api/attractions/1")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["attraction"]["name"] == "鼓浪屿"
    assert "tags" in data["data"]
    assert "comments" in data["data"]


def test_get_attraction_detail_not_found():
    response = client.get("/api/attractions/99999")
    assert response.status_code == 404


def test_create_comment():
    payload = {
        "attraction_id": 1,
        "user_name": "测试用户",
        "content": "很棒",
        "submission_token": "test-comment-unique-1"
    }
    response = client.post("/api/comments", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["comment_count"] >= 2


def test_duplicate_comment():
    payload = {
        "attraction_id": 1,
        "user_name": "重复用户",
        "content": "重复评论",
        "submission_token": "test-comment-dup-1"
    }
    response = client.post("/api/comments", json=payload)
    assert response.status_code == 200

    response2 = client.post("/api/comments", json=payload)
    assert response2.status_code == 409


def test_create_favorite():
    payload = {
        "attraction_id": 2,
        "device_id": "test-device-fav-1"
    }
    response = client.post("/api/favorites", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["duplicated"] is False


def test_duplicate_favorite():
    payload = {
        "attraction_id": 2,
        "device_id": "test-device-dup-fav-1"
    }
    response = client.post("/api/favorites", json=payload)
    assert response.status_code == 200

    response2 = client.post("/api/favorites", json=payload)
    assert response2.status_code == 200
    assert response2.json()["data"]["duplicated"] is True


def test_recommend_route():
    response = client.get("/api/routes/recommend?preferences=人文&preferences=摄影&duration=half_day")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    route = data["data"]["route"]
    assert len(route) >= 1


def test_recommend_route_one_day():
    response = client.get("/api/routes/recommend?preferences=亲子&preferences=美食&duration=one_day")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    route = data["data"]["route"]
    assert len(route) >= 1


def test_create_custom_route():
    payload = {
        "name": "测试自定义路线",
        "attraction_ids": [1, 3, 5],
        "preferences": ["人文", "海边"],
        "notes": "测试备注"
    }
    response = client.post("/api/routes/custom", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "route_id" in data["data"]


def test_create_custom_route_invalid_attraction():
    payload = {
        "name": "无效路线",
        "attraction_ids": [1, 99999],
        "preferences": ["人文"],
        "notes": ""
    }
    response = client.post("/api/routes/custom", json=payload)
    assert response.status_code == 404


def test_get_saved_routes():
    response = client.get("/api/routes")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]["items"]) >= 1


def test_get_route_detail():
    response = client.get("/api/routes/1")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]["attractions"]) >= 1
