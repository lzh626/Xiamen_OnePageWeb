import os

base = 'g:/ai_angent_web'
dirs = ['config', 'db', 'api', 'external', 'recommend', 'frontend/css', 'frontend/js', 'tests']
for d in dirs:
    os.makedirs(os.path.join(base, d), exist_ok=True)

req_txt = '''fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.2
pytest==7.4.3
httpx==0.25.2
'''

env_example = '''# 第三方API配置 (山河天气)
WEATHER_API_URL=http://shanhe.kim/api/za/tianqi.php

# 数据库配置
DB_PATH=./xiamen_travel.db
'''

init_sql = '''DROP TABLE IF EXISTS attractions;
CREATE TABLE attractions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    cover_image TEXT NOT NULL,
    region TEXT NOT NULL,
    rec_time TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO attractions (name, description, cover_image, region, rec_time) VALUES
('鼓浪屿', '海上花园，万国建筑博览，适合漫步发呆。', 'https://images.unsplash.com/photo-1596484552993-9c869b329fc3?auto=format&fit=crop&w=400&q=80', '思明区', '半天-1天'),
('厦门大学', '中国最美大学之一，依山傍海，人文气息浓厚。', 'https://images.unsplash.com/photo-1582230182883-79d39c9b83b3?auto=format&fit=crop&w=400&q=80', '思明区', '2-3小时'),
('环岛路', '最美马拉松赛道，骑行看海的最佳选择。', 'https://images.unsplash.com/photo-1625026671046-e50b8eb49692?auto=format&fit=crop&w=400&q=80', '思明区', '1-2小时'),
('南普陀寺', '千年古刹，香火鼎盛，背倚五老峰，可俯瞰厦大。', 'https://images.unsplash.com/photo-1596484552834-8a58f4a0c841?auto=format&fit=crop&w=400&q=80', '思明区', '2小时'),
('曾厝垵', '中国最文艺渔村，特色小吃与文创小店聚集地。', 'https://images.unsplash.com/photo-1574256241285-115f530d95ea?auto=format&fit=crop&w=400&q=80', '思明区', '2-3小时'),
('沙坡尾', '老厦门渔港文化与现代年轻潮流的碰撞地。', 'https://images.unsplash.com/photo-1601662528567-526cd06f6582?auto=format&fit=crop&w=400&q=80', '思明区', '1-2小时');
'''

db_py = '''import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'xiamen_travel.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_PATH):
        conn = get_db_connection()
        with open(os.path.join(os.path.dirname(__file__), 'init.sql'), 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print("Database initialized successfully.")
'''

api_attr_py = '''from fastapi import APIRouter, HTTPException
from db.database import get_db_connection

router = APIRouter()

@router.get("/api/attractions")
def get_attractions():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attractions ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        return {"code": 0, "msg": "success", "data": [dict(row) for row in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''

main_py = '''import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from db.database import init_db
from api.attractions import router as attractions_router

# 启动时初始化数据库
init_db()

app = FastAPI(title="厦门旅游 Web API")

# 注册路由
app.include_router(attractions_router)

# 挂载前端静态文件
frontend_path = os.path.join(os.path.dirname(__file__), 'frontend')

@app.get("/")
def read_root():
    return FileResponse(os.path.join(frontend_path, 'index.html'))

app.mount("/", StaticFiles(directory=frontend_path), name="frontend")
'''

html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>厦门旅游 - 发现最美鹭岛</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <header class="header">
        <h1>探索厦门</h1>
        <p>海上花园，文艺鹭岛</p>
    </header>
    <main class="container">
        <section id="attractions-section">
            <h2 class="section-title">热门景点</h2>
            <div id="loading" class="state-msg">数据加载中...</div>
            <div id="error-msg" class="state-msg error hidden"></div>
            <div id="attractions-grid" class="grid hidden"></div>
        </section>
    </main>
    <script src="/js/api.js"></script>
    <script src="/js/main.js"></script>
</body>
</html>
'''

css_content = '''* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f5f7fa; color: #333; line-height: 1.6; }
.header { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; text-align: center; padding: 3rem 1rem; }
.header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
.container { max-width: 1200px; margin: 0 auto; padding: 2rem 1rem; }
.section-title { text-align: center; margin-bottom: 2rem; color: #2c3e50; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; }
.card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: transform 0.2s; }
.card:hover { transform: translateY(-5px); }
.card img { width: 100%; height: 200px; object-fit: cover; }
.card-content { padding: 1.5rem; }
.card-content h3 { margin-bottom: 0.5rem; color: #2c3e50; }
.meta { font-size: 0.875rem; color: #666; margin-bottom: 0.5rem; }
.desc { font-size: 0.95rem; color: #4a5568; }
.state-msg { text-align: center; padding: 2rem; color: #666; font-size: 1.1rem; }
.error { color: #e53e3e; }
.hidden { display: none !important; }
'''

js_api = '''const API = {
    async getAttractions() {
        try {
            const response = await fetch('/api/attractions');
            if (!response.ok) throw new Error('网络请求异常，状态码：' + response.status);
            const res = await response.json();
            if (res.code !== 0) throw new Error(res.msg || '后端返回错误');
            return res.data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
};
'''

js_main = '''document.addEventListener('DOMContentLoaded', () => {
    loadAttractions();
});

async function loadAttractions() {
    const loading = document.getElementById('loading');
    const errorMsg = document.getElementById('error-msg');
    const grid = document.getElementById('attractions-grid');

    try {
        const data = await API.getAttractions();
        loading.classList.add('hidden');
        
        if (!data || data.length === 0) {
            errorMsg.textContent = '暂无景点数据，请稍后再试。';
            errorMsg.classList.remove('hidden');
            return;
        }

        grid.innerHTML = data.map(item => `
            <div class="card">
                <img src="${item.cover_image}" alt="${item.name}" loading="lazy">
                <div class="card-content">
                    <h3>${item.name}</h3>
                    <p class="meta">📍 ${item.region} | ⏱ ${item.rec_time}</p>
                    <p class="desc">${item.description}</p>
                </div>
            </div>
        `).join('');
        grid.classList.remove('hidden');
    } catch (error) {
        loading.classList.add('hidden');
        errorMsg.textContent = '加载景点失败，请检查网络或后端服务。';
        errorMsg.classList.remove('hidden');
    }
}
'''

test_api = '''from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def test_get_attractions():
    response = client.get("/api/attractions")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "data" in data
    assert len(data["data"]) >= 5
    names = [item["name"] for item in data["data"]]
    assert "鼓浪屿" in names
    assert "厦门大学" in names
'''

files = {
    "requirements.txt": req_txt,
    ".env.example": env_example,
    "db/init.sql": init_sql,
    "db/database.py": db_py,
    "api/attractions.py": api_attr_py,
    "main.py": main_py,
    "frontend/index.html": html_content,
    "frontend/css/style.css": css_content,
    "frontend/js/api.js": js_api,
    "frontend/js/main.js": js_main,
    "tests/test_api.py": test_api
}

for f, content in files.items():
    with open(os.path.join(base, f), "w", encoding="utf-8") as out:
        out.write(content)

print("All Phase 1 files created successfully.")