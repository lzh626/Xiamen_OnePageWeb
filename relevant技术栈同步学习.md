# 厦门旅游项目 · 技术栈同步学习手册

> **对应项目：** 厦门旅游前后端 Web + AI 推荐  
> **AI Coding 面试完整知识点 + 项目实现对照**  
> **更新日期：** 2026-06-25 ｜ 状态：阶段0→5 全部完成，29 项测试通过

---

## 总说明

本文档将通用的技术知识点与"厦门旅游"项目的**实际实现代码**一一对应。每个模块包含：

- **知识要点**：面试需要掌握的理论
- **项目实现对照**：本项目在哪段代码体现了这个知识点
- **面试高频考点**：面试官可能怎么问
- **学习导航**：推荐的学习资料链接

---

## 模块 1：Python 基础与工程环境

### 1.1 虚拟环境 venv

**知识要点：**
- 创建：`python -m venv venv_name`
- 激活：Windows `.\venv_name\Scripts\activate` / Mac `source venv_name/bin/activate`
- 依赖导出：`pip freeze > requirements.txt`
- 依赖安装：`pip install -r requirements.txt`

**项目实现对照：**
- 本项目的虚拟环境：`ven_of_XmWeatherWeb/`
- `requirements.txt` 包含 7 个依赖：fastapi / uvicorn / pydantic / pytest / httpx / icrawler / python-dotenv
- 激活命令：`.\ven_of_XmWeatherWeb\Scripts\activate`
- `.gitignore` 第 7 行排除 `ven_of_XmWeatherWeb/`，防止将虚拟环境提交到 Git

**面试高频考点：**
- 为什么必须使用虚拟环境？→ 依赖隔离，避免全局 Python 包冲突；不同项目可共存不同版本
- requirements.txt 和 pip freeze 的区别？→ `freeze` 输出当前环境所有包（含依赖链），`requirements.txt` 应只列直接依赖

### 1.2 环境变量 .env

**知识要点：**
- `python-dotenv` 的 `load_dotenv()` 加载 `.env` 文件
- 密钥 / API Key 只能放在 `.env`，不能出现在代码中
- `.env` 必须加入 `.gitignore` 防止泄露
- `.env.example` 用于提交 Git，展示配置项但不含真实密钥

**项目实现对照：**
- [config/settings.py](config/settings.py): 第 7 行 `load_dotenv(BASE_DIR / ".env")`
- `.env.example` 提交远程：展示 WEATHER_API_URL / RECOMMENDER_TYPE / LLM_API_KEY 等模板
- `.gitignore` 第 9 行排除 `.env`
- 核心配置项：
  ```python
  WEATHER_API_URL = os.getenv("WEATHER_API_URL", "http://shanhe.kim/api/za/tianqi.php")
  RECOMMENDER_TYPE = os.getenv("RECOMMENDER_TYPE", "rule")
  LLM_API_KEY = os.getenv("LLM_API_KEY", "")
  ```

**面试高频考点：**
- 密钥为什么不能写死代码？→ 泄漏风险，多人协作时密钥共享，Git 历史无法清除
- .env.example 的作用？→ 告诉队友需要配置什么变量，方便部署

### 1.3 模块化分层

**知识要点：**
- 按功能拆分目录：config / db / api / external / recommend / frontend / tests
- 包标记：`__init__.py`
- 绝对导入 vs 相对导入

**项目实现对照：**
```
config/settings.py      # 环境变量（配置层）
db/database.py          # SQLite 连接管理（持久层）
api/                    # 路由（接口层）
external/              # 第三方客户端（外部依赖层）
recommend/             # 推荐器（业务逻辑层）
frontend/              # 前端静态资源（展示层）
tests/                 # 测试
```

### 1.4 异步基础 async/await

**知识要点：**
- ASGI 与 WSGI 区别
- uvicorn 运行原理
- httpx 异步请求

**项目实现对照：**
- [main.py](main.py): FastAPI 的请求中间件使用 `async def` + `await call_next(request)`
- [api/weather.py](api/weather.py): 天气请求使用 httpx 同步调用（默认通过 uvicorn 工作线程）
- uvicorn 启动命令：`uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

**面试高频考点：**
- `--host 0.0.0.0` 和 `127.0.0.1` 区别？→ `0.0.0.0` 绑定所有网络接口，手机同 Wi-Fi 可访问；`127.0.0.1` 仅本机访问
- Windows/Mac 虚拟环境激活命令差异：Windows `.bat` / `.ps1`，Mac `source bin/activate`

---

## 模块 2：FastAPI 后端核心

### 2.1 框架基础

**知识要点：**
- 路由装饰器：`@app.get()` / `@router.post()`
- 路径参数：`/api/attractions/{attraction_id}`
- 查询参数：`Query(min_length=1, max_length=50)`
- 请求体校验：Pydantic `BaseModel`
- 静态资源挂载：`StaticFiles(directory=...)`
- 自动文档：`/docs` + `/redoc`

**项目实现对照：**

```python
# 路径参数示例 — attractions.py:147
@router.get("/api/attractions/{attraction_id}")
def get_attraction_detail(attraction_id: int):
    ...

# 查询参数示例 — attractions.py:92
def get_attractions(
    keyword: str | None = Query(None, min_length=1, max_length=50),
    region: str | None = Query(None, min_length=1, max_length=10),
    page: int = Query(1, ge=1),
    ...
):
    ...

# 请求体校验 — interactions.py:12-22
class CommentCreate(BaseModel):
    attraction_id: int = Field(gt=0)
    user_name: str = Field(min_length=1, max_length=20)
    content: str = Field(min_length=1, max_length=200)
    submission_token: str = Field(min_length=8, max_length=100)

# 全局路由注册 — main.py:26
app.include_router(attractions_router)
app.include_router(interactions_router)
app.include_router(weather_router)
app.include_router(recommend_router)

# 静态文件挂载 — main.py:88
app.mount("/", StaticFiles(directory=frontend_path), name="frontend")

# 自动文档
# http://127.0.0.1:8000/docs → Swagger UI
# http://127.0.0.1:8000/redoc → ReDoc
```

### 2.2 进阶工程能力

**知识要点：**
- 分页、筛选、排序接口实现
- 全局统一返回格式 `{code, msg, data}`
- 全局异常处理器（HTTP 4xx、422、500）
- Request-ID 链路日志 + 接口耗时
- 重复提交防抖、参数非法拦截、空数据兜底

**项目实现对照：**

```python
# 统一返回格式 — 所有接口都返回 {code, msg, data}
return {
    "code": 0,
    "msg": "success",
    "data": {"items": items, "pagination": {...}},
}

# 全局异常处理器 — main.py:52-78
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "msg": exc.detail, "data": None},
    )

# 分页返回结构 — attractions.py:133-139
"pagination": {
    "total": total,
    "page": page,
    "page_size": page_size,
    "total_pages": max(1, (total + page_size - 1) // page_size),
    "has_more": offset + page_size < total,
}

# Request-ID + 耗时日志 — main.py:31-50
@app.middleware("http")
async def add_request_id_and_log(request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info("request_id=%s | %s %s | %d | %.1fms",
        request_id, request.method, request.url.path,
        response.status_code, elapsed_ms)
    response.headers["X-Request-ID"] = request_id

# 非法参数拦截 — attractions.py:6 (白名单校验)
VALID_REGIONS = frozenset({"思明区", "湖里区", "集美区", "同安区", "翔安区", "海沧区"})
if region not in VALID_REGIONS:
    raise HTTPException(status_code=400, detail=f"无效的区域参数")

# 重复提交防抖 — interactions.py:86-91
try:
    conn.execute("INSERT INTO comments (...) VALUES (?,?,?,?)", ...)
except sqlite3.IntegrityError:
    raise HTTPException(status_code=409, detail="该评论已提交，请勿重复操作")
```

**面试高频考点：**
- FastAPI 相比 Flask/Django 优势？→ 原生 Pydantic 校验、自动 OpenAPI、async/await、高性能
- 分页接口如何处理超大游标、空列表？→ `page_size` 上限 50（`le=50`），空列表正常返回 `items: []`
- 跨域产生原因？→ 浏览器同源策略；前端 `http://localhost:8000` 请求后端 `http://127.0.0.1:8000` 不同源（端口号不同）
- 统一错误响应怎么设计？→ `{code: int, msg: str, data: any}`，区分参数错误 400 / 数据库错误 500 / 第三方接口失败 502

---

## 模块 3：SQLite 数据库设计

### 3.1 9 张数据表

**知识要点：**
- 主键、外键、创建/更新时间戳
- 多对多关系：需要中间桥接表
- 建表 SQL 脚本 + 种子数据
- 多表联查：LEFT JOIN + GROUP BY + COUNT

**项目实现对照：**

```
9 张表 ER 关系：
attractions ──< attraction_tags >── tags
    ├──< comments
    ├──< favorites
    ├──< likes
    ├──< route_items >── routes
    └──  weather_cache（独立）
```

**attractions 表核心字段：**
```sql
id, name, description, cover_image, region, rec_time,
open_time, close_time, recommended_hours, suitable_weather,
intensity_level, popularity_score, recommend_score,
created_at, updated_at
```

**多对多关系实现 — [db/init.sql](db/init.sql):**
```sql
CREATE TABLE attraction_tags (
    attraction_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (attraction_id, tag_id),
    FOREIGN KEY (attraction_id) REFERENCES attractions(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
```

**多表联查统计 — [api/attractions.py](api/attractions.py):**
```python
LEFT JOIN (
    SELECT attraction_id, COUNT(*) AS like_count
    FROM likes GROUP BY attraction_id
) AS like_stats ON like_stats.attraction_id = a.id
```

**种子数据 — [db/init.sql](db/init.sql):**
- 15 个景点覆盖思明/集美/湖里/海沧 4 区
- 6 种标签：亲子/摄影/人文/海边/美食/低强度
- 5 条种子评论、7 条收藏、7 条点赞

### 3.2 数据一致性

**知识要点：**
- 事务：写入失败自动回滚
- 唯一约束防重复（submission_token UNIQUE / device_id+attraction_id UNIQUE）
- 统计实时聚合 LEFT JOIN COUNT，不自增计数字段防止并发错乱
- `popularity_score` 联动公式：`like×4 + fav×2 + comment`

**项目实现对照：**

```python
# 事务保证 — interactions.py:83-84
conn.execute("INSERT INTO comments (...) VALUES (?,?,?,?)", ...)
conn.commit()  # 提交事务，失败自动回滚

# 防重复评论 — db/init.sql
submission_token TEXT NOT NULL UNIQUE  →  409 Conflict

# 防重复收藏 — db/init.sql
UNIQUE (attraction_id, device_id)  →  幂等返回 duplicated=true

# 收藏/点赞后同步更新 popularity_score — interactions.py:137-146
conn.execute("""
    UPDATE attractions SET popularity_score = (
        SELECT COALESCE(lk.c,0)*4 + COALESCE(fv.c,0)*2 + COALESCE(cm.c,0)
        FROM (SELECT COUNT(*) AS c FROM likes WHERE attraction_id=?) AS lk,
             (SELECT COUNT(*) AS c FROM favorites WHERE attraction_id=?) AS fv,
             (SELECT COUNT(*) AS c FROM comments WHERE attraction_id=?) AS cm
    ) WHERE id = ?
""", (aid, aid, aid, aid))
```

### 3.3 天气缓存表设计

**知识要点：**
- 缓存表：city 为主键，存储 JSON payload + 更新时间
- TTL 策略：读取时比较 `updated_at` 与当前时间

**项目实现对照：**

```sql
CREATE TABLE weather_cache (
    city TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    updated_at DATETIME NOT NULL
);
```

[api/weather.py](api/weather.py) 中的三级缓存降级：
```python
# 1. 读取缓存，检查 TTL（1800 秒可配）
# 2. 缓存有效 → 直接返回
# 3. 缓存过期 → 先返回旧数据（stale cache），异步请求新数据
# 4. 无缓存 → 请求实时接口
# 5. 接口失败 → 返回过期缓存（如果有）→ fallback 固定文案
```

**面试高频考点：**
- 景点与标签多对多怎么设计三张表？→ 中间桥接表 `attraction_tags` 存 `(attraction_id, tag_id)`，避免逗号分隔的数组字段，便于 SQL JOIN 查询和索引优化
- 收藏统计如何保证实时一致？→ 不维护计数器字段，每次 `LEFT JOIN COUNT` 实时聚合；点赞/收藏/评论写入后在同一个事务中通过 `UPDATE ... FROM (SELECT COUNT FROM likes WHERE ...)` 更新 `popularity_score`
- SQLite 优缺点？→ 优点：零配置、文件级、适合单机小项目；缺点：无高并发、无用户权限、无存储过程
- weather_cache 为什么不用内存缓存？→ SQLite 是文件数据库，重启服务缓存不丢失；内存缓存重启后必须重新请求第三方接口

---

## 模块 4：前端页面基础

### 4.1 原生 HTML/CSS/JS

**知识要点：**
- 单页应用：一个 `index.html` 入口
- CSS Grid / Flexbox 布局
- `@media (max-width: 640px)` 移动端断点
- `viewport` meta 标签
- `fetch()` 异步请求

**项目实现对照：**

index.html — 结构顺序：
```
header（标题区）
→ weather-section（天气卡片）
→ route-section（路线推荐面板）
→ attractions-section（筛选栏 + 景点网格 + 分页栏）
```

CSS Grid 响应式布局 — [style.css](frontend/css/style.css):
```css
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
}

@media (max-width: 640px) {
    .grid { grid-template-columns: 1fr; }
}
```

### 4.2 前端多状态处理

**知识要点：**
- 加载中 / 空数据 / 接口失败 / 提交中 / 提交成功 / 重复点击保护
- 分别写独立 DOM 元素控制 `classList.remove('hidden')`

**项目实现对照 — [main.js](frontend/js/main.js):**

```javascript
// 加载/空数据/失败三态 — loadAttractions()
loading.classList.remove('hidden');    // 显示加载中
errorMsg.classList.add('hidden');       // 隐藏错误
grid.classList.add('hidden');           // 隐藏已有数据

// ...请求完成后
loading.classList.add('hidden');         // 隐藏加载中
if (items.length === 0) {
    errorMsg.textContent = '没有找到匹配的景点';  // 空结果
    errorMsg.classList.remove('hidden');
    return;
}
grid.innerHTML = ...;                    // 渲染数据
grid.classList.remove('hidden');
```

**面试高频考点：**
- 前端为什么不能直接请求山河天气接口？→ 跨域（HTTP 请求 HTTPS 页面） + 混合内容（HTTPS 页面加载 HTTP 接口被浏览器拦截）；必须后端代理
- 电脑开 VPN 后手机无法访问？→ VPN 修改了主机的网络路由表，局域网 IP 不再可达；关闭 VPN 或改用手机热点

---

## 模块 5：第三方天气接口 · 缓存与降级

### 5.1 山河 API 调用规范

**知识要点：**
- API 地址：`http://shanhe.kim/api/za/tianqi.php?city=厦门&type=json`
- 返回 JSON 结构：`{code, text, data: {temp, tempn, weather, time, current, living}}`
- 注意事项：仅 HTTP、无 HTTPS、无 API Key

**项目实现对照 — [external/weather_client.py](external/weather_client.py):**

```python
# 标准化输出
def normalize_weather(payload):
    ...
    return {
        "city": data["city"],
        "today_weather": data["weather"],
        "high_temp": high_temp,          # 经过 _sanitize_temp 过滤的合理值
        "low_temp": low_temp,
        "current_temp": current_temp,
        "current_weather": current["weather"],
        "humidity": current.get("humidity", ""),
        "air_quality": air_quality,
        "tourism_index": tourism["index"],
        "tourism_tips": tourism["tips"],
        "observe_time": observe_time,    # 实际观测时间
        "update_time": data.get("time", ""),
        "source": "live",
    }
```

### 5.2 四级降级策略

**知识要点（必背）：**
1. 实时数据 → 正常返回
2. 缓存未过期 → 直接返回缓存
3. 缓存已过期 → 先返回旧数据（stale cache），后台请求更新
4. 接口全部不可用 → fallback 固定文案

**项目实现对照 — [api/weather.py](api/weather.py):**

```python
# 降级链路
try:
    response = get_xiamen_weather()       # 1. 尝试实时
except:
    cache = _read_cache("厦门")            # 2. fallback 缓存
    if cache:
        return cache
    return build_fallback_weather(...)     # 3. fallback 文案
```

**异常值过滤 — [external/weather_client.py](external/weather_client.py):**
```python
def _sanitize_temp(raw_value):
    try:
        val = float(raw_value)
    except (TypeError, ValueError):
        return None
    if val > 100 or val < -60:       # 过滤 999 占位值
        return None
    return val

# 低 > 高自动交换
if raw_low > raw_high:
    raw_high, raw_low = raw_low, raw_high
```

**面试高频考点：**
- 全套异常场景：网络超时 / 接口 503 / 返回非 JSON / 空数据 / 温度占位值 999 / 温度高低倒挂
- 为什么不用内存缓存？→ SQLite 持久化，重启不丢失；可跨服务共享
- 如何利用旅游指数生成个性化路线？→ `tourism_index` 在 [recommend/rule_recommender.py](recommend/rule_recommender.py) 中参与三维评分（"适宜"+15 分，"不适宜"→推荐室内景点）

---

## 模块 6：AI 推荐 Agent 适配层

### 6.1 三层降级推荐架构

**知识要点（硬性要求）：**
- 第一层：大模型 AI 推荐（`LLMRecommender`）
- 第二层：规则推荐（`RuleRecommender`）
- 第三层：Mock 兜底（`MockLLMRecommender`）
- 可替换：通过环境变量 `RECOMMENDER_TYPE` 一键切换

**项目实现对照：**

```python
# 抽象基类 — recommend/base.py
class BaseRecommender(ABC):
    @abstractmethod
    def recommend(self, preferences, duration, weather, attractions):
        raise NotImplementedError

# 工厂函数 — api/recommend.py:18-23
def _get_recommender():
    if RECOMMENDER_TYPE == "llm":   return LLMRecommender()
    if RECOMMENDER_TYPE == "mock":  return MockLLMRecommender()
    return RuleRecommender()
```

### 6.2 规则推荐引擎

**知识要点：**
- 三维评分：偏好匹配（15 分/项） + 天气适配（25 分） + 热度指数（5-20 分）
- 贪心选择：按评分降序排列，累计时长不超过半日/一日限制
- 推荐理由生成：每条推荐回传原因

**项目实现对照 — [recommend/rule_recommender.py](recommend/rule_recommender.py):**

```python
def _score_attraction(self, attraction, preferences, weather):
    score = 0
    reasons = []
    # 低强度偏好 +20
    if attraction["intensity_level"] == "low" and "低强度" in preferences:
        score += 20; reasons.append("低强度友好")
    # 天气适配 +25
    if current_w in suitable:
        score += 25; reasons.append(f"当前天气{current_w}适合游玩")
    # 偏好匹配 +15/项
    for pref in preferences:
        if pref in tag_names:
            score += 15; reasons.append(f"属于「{pref}」类景点")
    return score, reasons
```

### 6.3 LLM 推荐器

**知识要点：**
- 调用 OpenAI 兼容 API（Chat Completions）
- Prompt 工程：约束返回 JSON 格式，限制不生成幻觉
- 密钥安全：仅后端 `.env` 读取
- 失败自动降级：捕获 RuntimeError → 回退 RuleRecommender

**项目实现对照 — [recommend/llm_recommender.py](recommend/llm_recommender.py):**

```python
# LLM 调用失败降级 — 第 80-86 行
try:
    llm_result = self._call_llm(prompt)
except RuntimeError:
    fallback = self._fallback.recommend(...)
    fallback["recommender"] = "rule-fallback"
    fallback["llm_error"] = True
    return fallback

# Prompt 约束 — 第 27-39 行
"""请返回仅含 JSON 的回复，格式严格如下：
{"route": [{"name": "景点名", "reason": "推荐理由（20字内）"}], ...}
要求：根据用户偏好和天气筛选，推荐理由需结合天气和偏好，按优先级排序"""
```

### 6.4 Vibe Coding / Agentic 开发模式

**知识要点：**
- 分阶段迭代：每次只完成一个需求块
- 测试驱动：代码生成后立即编写 pytest 并验证通过
- 异常优先：先考虑失败场景再写正常路径
- AI 校验方法：每个接口用 TestClient 测试 + 浏览器 F12 验证 + SQL 查询核对

**本项目 AI 工具使用说明：**
- 所有代码由 TRAE IDE 辅助生成
- 数据库设计 → AI 生成 DDL → 人工对照面试文档逐字段核验
- API 接口 → AI 生成 FastAPI 路由 → pytest 全覆盖
- 天气客户端 → AI 生成重试/降级 → 模拟 999/超时场景测试
- 推荐算法 → AI 生成评分函数 → 手工构造组合验证排序
- 前端 → AI 生成 HTML/CSS/JS → 浏览器真实交互 + 手机适配测试

### 6.5 关于"自然语言出行需求理解"

**澄清：** 面试文档原文是"如果使用大模型，需要做成可替换、可降级的模块"——强调的是**架构可替换性**，不是自然语言理解。所谓的"理解人的出行需求、给出生动答复"属于《实验7 综合实践》中「Agent 拓展加分项」（如 LangChain SQL Agent），不是 AI Coding 面试的硬性要求。

当前项目的推荐适配层已经完整覆盖面试文档第 5 条的三点要求：
1. ✅ 封装统一推荐接口，可接多种实现（BaseRecommender）
2. ✅ 可降级（LLM 失败 → 规则引擎）
3. ✅ API Key 仅在后端环境变量

---

## 模块 7：工程化 · 测试 · 文档 · 答辩

### 7.1 Git 版本管理

**项目实现对照：**

```bash
# 分阶段提交规范
git commit -m "阶段X-功能简述 | 对标AI面试文档-需求点"

# 实际提交记录
阶段0 → "阶段0-需求拆解与脚手架规划 | 对标AI面试文档-全需求分析"
阶段1 → "阶段1-景点数据读取闭环与移动端展示 | 对标AI面试文档-宣传页面+真实前后端交互+SQLite初始化"
阶段2 → "阶段2-评论收藏与天气代理缓存 | 对标AI面试文档-2个写入接口+天气代理缓存降级+前端基础交互"
阶段3 → "阶段3-景点筛选分页排序与路线推荐 | 对标AI面试文档-搜索筛选排序+路线规划推荐+分页异常处理"
阶段4 → "阶段4-AI推荐适配层与request_id日志工程化 | 对标AI面试文档-AI辅助推荐适配层+测试日志与可维护性"
阶段5 → "阶段5-点赞推荐联动热度+15景点多区域扩充+真实图片爬取 | 对标AI面试文档-数据扩充+排序筛选+推荐算法数据联动"

# .gitignore 排除项
venv/, __pycache__/, *.db, .env, .vscode/, README_LOCAL.md
```

### 7.2 单元测试

**项目实现对照：**

```python
# 29 项测试覆盖：
# 景点类（10项）：全量/关键词/区域/标签/集美区/排序/like_count排序/分页/非法区域/非法排序
# 详情类（3项）：正常/新景点/404
# 交互类（7项）：点赞/重复点赞/评论/重复评论409/收藏/重复收藏/幂等
# 路线类（5项）：推荐半日/推荐一日/自定义保存/无效景点/路线详情
# 日志类（2项）：request_id 正常头/404头
# 天气类（2项）：fallback/缓存
```

### 7.3 交付文档

**项目交付文件：**

| 文件 | 用途 | 推送 |
|:---|:---|:---|
| README.md | GitHub 展示（完整架构+逐阶段+AI说明） | ✅ |
| README_LOCAL.md | AICoding 面试精简版（不推送） | ❌ |
| 面试与演示.md | 需求逐条对照+演示流程+问答预案 | ✅ |
| 面试问题记录.md | 面试过程问题记录 | ✅ |
| relevant技术栈同步学习.md | 本文档 | ✅ |

### 7.4 面试答辩能力

**面试官常见提问顺序：**
1. 项目整体介绍（技术栈、目标、分阶段思路）
2. 数据库表结构讲解（9 张表关联、缓存表设计）
3. 后端接口讲解（读取/写入、分页筛选、天气代理缓存降级）
4. AI 推荐模块（三层降级、偏好路线生成、大模型安全封装）
5. 前端移动端适配、异常状态、手机局域网访问
6. 工程化（虚拟环境、Git 版本、日志、单元测试、README）
7. AI 开发工具提问（TRAE 辅助、Vibe Coding、Prompt 约束）
8. 附加拓展（LangChain SQLAgent、自然语言数据分析）

**核心回答技巧：**
- 面试官问"你怎么实现XX" → 先讲思路，再指代码位置
- 面试官问"遇到什么问题" → 先说问题场景，再说解决方案，最后说"现在还存在的问题"
- 面试官问"为什么选这个方案" → 列出至少 2 个替代方案 + 选择理由

---

## 附录：项目核心数字

| 指标 | 数值 |
|:---|:---|
| 数据库表 | 9 张 |
| 景点 | 15 个（4 个行政区） |
| 接口 | 10 个（6 读 + 4 写） |
| 测试 | 29 项 |
| Python 源文件 | 14 个（按 7 层模块化） |
| 前端文件 | 5 个 |
| 开发阶段 | 6 个（阶段0→5） |
| 外部依赖 | 3 个（山河天气、大模型、图片源） |
| 推荐器实现 | 3 种（规则/Mock/LLM） |
| 天气降级层级 | 4 级（实时→新鲜缓存→过期缓存→静态fallback） |
