DROP TABLE IF EXISTS weather_cache;
DROP TABLE IF EXISTS route_items;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS likes;
DROP TABLE IF EXISTS attraction_tags;
DROP TABLE IF EXISTS tags;
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
    open_time TEXT NOT NULL,
    close_time TEXT NOT NULL,
    recommended_hours REAL NOT NULL,
    suitable_weather TEXT NOT NULL,
    intensity_level TEXT NOT NULL,
    popularity_score INTEGER NOT NULL DEFAULT 0,
    recommend_score INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attraction_tags (
    attraction_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (attraction_id, tag_id),
    FOREIGN KEY (attraction_id) REFERENCES attractions (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
);

CREATE TABLE likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attraction_id INTEGER NOT NULL,
    device_id TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attraction_id) REFERENCES attractions (id) ON DELETE CASCADE,
    UNIQUE (attraction_id, device_id)
);

CREATE TABLE routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    duration_type TEXT NOT NULL,
    preferences TEXT NOT NULL,
    reason_text TEXT NOT NULL,
    weather_summary TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE route_items (
    route_id INTEGER NOT NULL,
    attraction_id INTEGER NOT NULL,
    sort_order INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (route_id, attraction_id),
    FOREIGN KEY (route_id) REFERENCES routes (id) ON DELETE CASCADE,
    FOREIGN KEY (attraction_id) REFERENCES attractions (id) ON DELETE CASCADE
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attraction_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    content TEXT NOT NULL,
    submission_token TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attraction_id) REFERENCES attractions (id) ON DELETE CASCADE
);

CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attraction_id INTEGER NOT NULL,
    device_id TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attraction_id) REFERENCES attractions (id) ON DELETE CASCADE,
    UNIQUE (attraction_id, device_id)
);

CREATE TABLE weather_cache (
    city TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    updated_at DATETIME NOT NULL
);

INSERT INTO attractions (
    name, description, cover_image, region, rec_time, open_time, close_time,
    recommended_hours, suitable_weather, intensity_level, popularity_score,
    recommend_score
) VALUES
('鼓浪屿', '海上花园，万国建筑博览，适合漫步发呆。', '/images/gulangyu.svg', '思明区', '半天-1天', '08:00', '18:00', 5.5, 'sunny,cloudy', 'medium', 98, 97),
('厦门大学', '中国最美大学之一，依山傍海，人文气息浓厚。', '/images/xiada.svg', '思明区', '2-3小时', '08:30', '17:30', 2.5, 'cloudy,sunny', 'low', 95, 94),
('环岛路', '最美马拉松赛道，骑行看海的最佳选择。', '/images/huandaolu.svg', '思明区', '1-2小时', '06:00', '22:00', 2.0, 'sunny,cloudy', 'medium', 90, 96),
('南普陀寺', '千年古刹，香火鼎盛，背倚五老峰，可俯瞰厦大。', '/images/nanputuo.svg', '思明区', '2小时', '08:00', '17:00', 2.0, 'cloudy,rainy,sunny', 'low', 88, 92),
('曾厝垵', '中国最文艺渔村，特色小吃与文创小店聚集地。', '/images/zengcuoan.svg', '思明区', '2-3小时', '10:00', '22:30', 2.5, 'cloudy,sunny,rainy', 'low', 92, 91),
('沙坡尾', '老厦门渔港文化与现代年轻潮流的碰撞地。', '/images/shapowei.svg', '思明区', '1-2小时', '10:00', '21:30', 1.5, 'cloudy,sunny', 'low', 89, 90),
('中山路步行街', '百年商业老街，南洋骑楼建筑群，厦门美食集中地。', '/images/zhongshanlu.svg', '思明区', '1-2小时', '10:00', '22:30', 1.5, 'sunny,cloudy,rainy', 'low', 93, 88),
('胡里山炮台', '清代海防要塞，世界现存最大海岸古炮，海景壮观。', '/images/hulishan.svg', '思明区', '1.5小时', '07:30', '18:00', 1.5, 'sunny,cloudy', 'low', 87, 85),
('集美学村', '陈嘉庚先生创办，中西合璧建筑群，感受嘉庚精神。', '/images/jimeixuecun.svg', '集美区', '半天', '08:30', '17:30', 3.0, 'sunny,cloudy,rainy', 'medium', 91, 93),
('园博苑', '水上园林博览，汇集各地园林精华，适合亲子出游。', '/images/yuanboyuan.svg', '集美区', '2-3小时', '09:00', '18:00', 2.5, 'sunny,cloudy', 'low', 86, 84),
('五缘湾湿地公园', '厦门最大生态公园，黑天鹅栖息地，亲子自然课堂。', '/images/wuyuanwan.svg', '湖里区', '2-3小时', '06:00', '21:00', 2.0, 'sunny,cloudy', 'low', 88, 87),
('铁路文化公园', '废弃铁路改造的文艺公园，三角梅隧道网红打卡地。', '/images/tielugongyuan.svg', '思明区', '1小时', '06:00', '22:00', 1.0, 'cloudy,sunny', 'low', 85, 82),
('东坪山', '厦门岛内最高峰，山海健康步道，俯瞰全城视野。', '/images/dongpingshan.svg', '思明区', '3小时', '06:00', '20:00', 3.0, 'sunny,cloudy', 'medium', 89, 90),
('海沧大桥', '跨海大桥地标，桥下游览区可远眺鼓浪屿和厦门港。', '/images/haicangdaqiao.svg', '海沧区', '1小时', '全天', '全天', 1.0, 'sunny,cloudy', 'low', 82, 83),
('海沧湾公园', '海沧最美海岸线，红树林栈道，观鸟与亲子野餐好去处。', '/images/haicangwan.svg', '海沧区', '1.5小时', '06:00', '22:00', 1.5, 'sunny,cloudy', 'low', 84, 83);

INSERT INTO tags (name) VALUES
('亲子'),
('摄影'),
('人文'),
('海边'),
('美食'),
('低强度');

INSERT INTO attraction_tags (attraction_id, tag_id) VALUES
(1, 2), (1, 3), (1, 4),
(2, 3), (2, 6),
(3, 2), (3, 4),
(4, 3), (4, 6),
(5, 2), (5, 5), (5, 6),
(6, 2), (6, 5), (6, 6),
(7, 5), (7, 3),
(8, 3), (8, 2),
(9, 3), (9, 1),
(10, 1), (10, 2),
(11, 1), (11, 4), (11, 6),
(12, 2), (12, 6),
(13, 1), (13, 2), (13, 5),
(14, 2), (14, 4),
(15, 1), (15, 4), (15, 6);

INSERT INTO comments (attraction_id, user_name, content, submission_token) VALUES
(1, '小雨', '鼓浪屿适合慢慢逛，拍照很出片。', 'seed-comment-1'),
(2, '阿杰', '厦大附近步行就能连着去南普陀，很方便。', 'seed-comment-2'),
(5, '吃货小分队', '曾厝垵的沙茶面和海蛎煎必吃！', 'seed-comment-3'),
(7, '老厦门人', '中山路晚上灯火通明，逛街吃小吃一绝。', 'seed-comment-4'),
(13, '登山爱好者', '东坪山健康步道视野绝佳，建议傍晚去。', 'seed-comment-5');

INSERT INTO favorites (attraction_id, device_id) VALUES
(1, 'seed-device-a'),
(1, 'seed-device-b'),
(3, 'seed-device-c'),
(5, 'seed-device-d'),
(7, 'seed-device-e'),
(9, 'seed-device-f'),
(13, 'seed-device-g');

INSERT INTO likes (attraction_id, device_id) VALUES
(1, 'seed-device-a'),
(1, 'seed-device-b'),
(1, 'seed-device-h'),
(3, 'seed-device-i'),
(7, 'seed-device-j'),
(13, 'seed-device-k'),
(14, 'seed-device-l');

INSERT INTO routes (name, duration_type, preferences, reason_text, weather_summary) VALUES
('人文慢游示例路线', 'half_day', '["人文","低强度"]', '示例路线，便于验证路线写入与展示。', '多云');

INSERT INTO route_items (route_id, attraction_id, sort_order) VALUES
(1, 2, 1),
(1, 4, 2),
(1, 6, 3);
