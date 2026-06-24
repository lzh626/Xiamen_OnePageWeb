DROP TABLE IF EXISTS weather_cache;
DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS attractions;

CREATE TABLE attractions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    cover_image TEXT NOT NULL,
    region TEXT NOT NULL,
    rec_time TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attraction_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    content TEXT NOT NULL,
    submission_token TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attraction_id) REFERENCES attractions (id) ON DELETE CASCADE
);

CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attraction_id INTEGER NOT NULL,
    device_id TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attraction_id) REFERENCES attractions (id) ON DELETE CASCADE,
    UNIQUE (attraction_id, device_id)
);

CREATE TABLE weather_cache (
    city TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    updated_at DATETIME NOT NULL
);

INSERT INTO attractions (name, description, cover_image, region, rec_time) VALUES
('鼓浪屿', '海上花园，万国建筑博览，适合漫步发呆。', '/images/gulangyu.svg', '思明区', '半天-1天'),
('厦门大学', '中国最美大学之一，依山傍海，人文气息浓厚。', '/images/xiada.svg', '思明区', '2-3小时'),
('环岛路', '最美马拉松赛道，骑行看海的最佳选择。', '/images/huandaolu.svg', '思明区', '1-2小时'),
('南普陀寺', '千年古刹，香火鼎盛，背倚五老峰，可俯瞰厦大。', '/images/nanputuo.svg', '思明区', '2小时'),
('曾厝垵', '中国最文艺渔村，特色小吃与文创小店聚集地。', '/images/zengcuoan.svg', '思明区', '2-3小时'),
('沙坡尾', '老厦门渔港文化与现代年轻潮流的碰撞地。', '/images/shapowei.svg', '思明区', '1-2小时');

INSERT INTO comments (attraction_id, user_name, content, submission_token) VALUES
(1, '小雨', '鼓浪屿适合慢慢逛，拍照很出片。', 'seed-comment-1'),
(2, '阿杰', '厦大附近步行就能连着去南普陀，很方便。', 'seed-comment-2');

INSERT INTO favorites (attraction_id, device_id) VALUES
(1, 'seed-device-a'),
(1, 'seed-device-b'),
(3, 'seed-device-c'),
(5, 'seed-device-d');
