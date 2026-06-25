# 厦门旅游宣传单页 Web 应用

厦门大学谷雨大模型实验室 · AI Coding 面试测试题
技术栈：Python (FastAPI) + SQLite + 原生 HTML/CSS/JS

---

## 一、版本迭代记录

| 阶段 | 提交描述 | 日期 |
|:---|:---|:---|
| 阶段0 | 阶段0-需求拆解与脚手架规划 | 对标AI面试文档-全需求分析 | 2026-06-24 |
| 阶段1 | 阶段1-景点数据读取闭环与移动端展示 | 对标AI面试文档-宣传页面+真实前后端交互+SQLite初始化 | 2026-06-24 |
| 阶段2 | 阶段2-评论收藏与天气代理缓存 | 对标AI面试文档-2个写入接口+天气代理缓存降级+前端基础交互 | 2026-06-24 |
| 阶段3 | 阶段3-景点筛选分页排序与路线推荐 | 对标AI面试文档-搜索筛选排序+路线规划推荐+分页异常处理 | 2026-06-25 |
| Bug修复 | 阶段3-bug修复-天气999温度过滤与观测时间显示 | 对标AI面试文档-天气代理缓存降级 | 2026-06-25 |
| Bug修复 | 阶段3-bug修复-温度范围倒挂修正 | 对标AI面试文档-天气代理缓存降级 | 2026-06-25 |

---

## 二、新增功能清单（逐条对应面试文档需求点）

### 01 厦门旅游宣传页面
- 图文介绍 6 个厦门景点：鼓浪屿、厦门大学、环岛路、南普陀寺、曾厝垵、沙坡尾
- 清晰的信息层级（头图→天气卡片→路线推荐→景点列表）
- 移动端响应式适配（CSS Grid + viewport meta）

### 02 API 真实前后端交互
- **3+ 个读取接口**：`GET /api/attractions`（筛选/排序/分页）、`GET /api/attractions/:id`（详情+标签+评论）、`GET /api/weather/xiamen`（天气代理）、`GET /api/routes/recommend`（路线推荐）
- **3 个写入接口**：`POST /api/comments`、`POST /api/favorites`、`POST /api/routes/custom`
- 所有数据通过接口动态获取，前端不写死

### 03 DB 本地数据库
- SQLite 数据库，8 张表：`attractions`、`tags`、`attraction_tags`、`comments`、`favorites`、`weather_cache`、`routes`、`route_items`
- 提供 `db/init.sql` 完整建表与种子数据
- 提供 `reset_db()` 重置函数

### 04 WX 厦门实时天气
- 后端代理调用山河天气 API
- 展示：实时温度、天气状况、湿度、空气质量、旅游指数、观测时间
- 异常值过滤：自动过滤 >100 或 <-60 的温度占位值（如 999），用当前温估推算
- 温度范围修正：当 API 返回高温 < 低温时自动交换

### 进阶能力
- **路线推荐**：基于偏好标签 + 天气三维评分（偏好匹配 + 天气适配 + 热度指数）
- **筛选排序**：关键词/区域/标签/天气适配/时长过滤 + 6 种排序 + 分页
- **评论收藏**：submission_token 防重复 + device_id 幂等 + 统计实时聚合
- **天气降级**：缓存 30min → 过期缓存回退 → fallback 固定文案

---

## 三、环境与启动更新

### 依赖安装
```bash
pip install -r requirements.txt
```

### 环境变量
复制 `.env.example` 为 `.env`，按需修改：
- `WEATHER_API_URL` — 山河天气接口地址
- `WEATHER_TIMEOUT_SECONDS` — 超时秒数（默认 3）
- `WEATHER_RETRY_COUNT` — 重试次数（默认 2）
- `WEATHER_CACHE_TTL_SECONDS` — 缓存秒数（默认 1800）
- `DB_PATH` — SQLite 文件路径（默认 `./xiamen_travel.db`）

### 数据库初始化
```bash
python -c "from db.database import reset_db; reset_db()"
```

### 启动服务
```bash
.\ven_of_XmWeatherWeb\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 运行测试
```bash
python -m pytest tests/ -v
```

---

## 四、现场演示 & 异常测试补充

### 推荐演示流程
1. 启动服务，打开 `http://127.0.0.1:8000/`
2. 天气卡片：观察实时温度、观测时间、旅游指数
3. 路线推荐：勾选偏好标签 → 生成推荐路线 → 查看推荐理由 → 保存路线
4. 景点筛选：搜索关键词/切换区域/标签/排序 → 翻页
5. 收藏评论：点击收藏 → 统计即时更新 → 提交评论 → 评论数更新
6. 终端验证：SQL 查询展示数据实时写入

### 已覆盖异常场景
| 场景 | 处理 |
|:---|:---|
| 天气接口超时/不可达 | 过期缓存 → fallback |
| 温度占位值 999 | `_sanitize_temp` 过滤 + current_temp 推算 |
| 温度高低倒挂 | 自动交换 high/low |
| 重复提交评论 | 409 Conflict |
| 重复收藏 | 幂等返回 duplicated=true |
| 非法筛选参数 | 400 Bad Request |
| 景点不存在 | 404 Not Found |
| 搜索结果为空 | "没有找到匹配的景点" |
| 前端请求失败 | try-catch 红色错误提示 |

### 移动端访问排坑
- 必须用 `--host 0.0.0.0`，不能用 `127.0.0.1`
- 校园网可能有客户端隔离 → 改用手机热点
- ERR_ADDRESS_UNREACHABLE → 检查 Windows 防火墙放行 8000 端口
