import os

base_dir = "g:/ai_angent_web"
img_dir = os.path.join(base_dir, "frontend", "images")
os.makedirs(img_dir, exist_ok=True)

# 使用 SVG 生成精美的本地测试图片（模拟真实旅游图片展示）
svg_template = """<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
    <defs>
        <linearGradient id="grad{id}" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{color1};stop-opacity:1" />
            <stop offset="100%" style="stop-color:{color2};stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#grad{id})" />
    <text x="50%" y="50%" font-family="sans-serif" font-size="48" font-weight="bold" fill="white" text-anchor="middle" dominant-baseline="middle">{name}</text>
    <text x="50%" y="60%" font-family="sans-serif" font-size="24" fill="rgba(255,255,255,0.8)" text-anchor="middle" dominant-baseline="middle">Xiamen Travel</text>
</svg>"""

attractions = {
    "gulangyu": {"name": "鼓浪屿 (Gulangyu)", "color1": "#4facfe", "color2": "#00f2fe"},
    "xiada": {"name": "厦门大学 (XMU)", "color1": "#43e97b", "color2": "#38f9d7"},
    "huandaolu": {"name": "环岛路 (Huandao Rd)", "color1": "#fa709a", "color2": "#fee140"},
    "nanputuo": {"name": "南普陀寺 (Nanputuo)", "color1": "#f83600", "color2": "#f9d423"},
    "zengcuoan": {"name": "曾厝垵 (Zengcuoan)", "color1": "#13547a", "color2": "#80d0c7"},
    "shapowei": {"name": "沙坡尾 (Shapowei)", "color1": "#ff0844", "color2": "#ffb199"}
}

image_paths = {}
for key, data in attractions.items():
    filepath = os.path.join(img_dir, f"{key}.svg")
    svg_content = svg_template.format(id=key, color1=data["color1"], color2=data["color2"], name=data["name"])
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_content)
    image_paths[key] = f"/images/{key}.svg"
    print(f"Generated local SVG for {key}")

# Rewrite init.sql with local SVG image paths
init_sql_path = os.path.join(base_dir, "db", "init.sql")
with open(init_sql_path, "w", encoding="utf-8") as f:
    f.write(f'''DROP TABLE IF EXISTS attractions;
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
('鼓浪屿', '海上花园，万国建筑博览，适合漫步发呆。', '{image_paths["gulangyu"]}', '思明区', '半天-1天'),
('厦门大学', '中国最美大学之一，依山傍海，人文气息浓厚。', '{image_paths["xiada"]}', '思明区', '2-3小时'),
('环岛路', '最美马拉松赛道，骑行看海的最佳选择。', '{image_paths["huandaolu"]}', '思明区', '1-2小时'),
('南普陀寺', '千年古刹，香火鼎盛，背倚五老峰，可俯瞰厦大。', '{image_paths["nanputuo"]}', '思明区', '2小时'),
('曾厝垵', '中国最文艺渔村，特色小吃与文创小店聚集地。', '{image_paths["zengcuoan"]}', '思明区', '2-3小时'),
('沙坡尾', '老厦门渔港文化与现代年轻潮流的碰撞地。', '{image_paths["shapowei"]}', '思明区', '1-2小时');
''')

# Remove existing db to force recreation on next run
db_path = os.path.join(base_dir, "xiamen_travel.db")
if os.path.exists(db_path):
    os.remove(db_path)
    print("Removed old database. It will be recreated on next startup.")
