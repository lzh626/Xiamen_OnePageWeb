# 厦门旅游宣传单页 Web 应用



# 厦门旅游宣传单页 Web 应用

> **厦门大学谷雨大模型实验室 · AI Coding 面试测试题**  
> 技术栈：Python (FastAPI) + SQLite + 原生 HTML/CSS/JS  
> 开发周期：2026-06-24 ~ 2026-06-25，共 5 个阶段

---

## 目录

1. [项目概述](#项目概述)
2. [最终代码架构](#最终代码架构)
3. [阶段0：需求拆解与脚手架规划](#阶段0需求拆解与脚手架规划)
4. [阶段1：最小可运行闭环](#阶段1最小可运行闭环)
5. [阶段2：完善基础模块](#阶段2完善基础模块)
6. [阶段3：进阶业务能力](#阶段3进阶业务能力)
7. [阶段4：AI推荐适配层+工程化](#阶段4ai推荐适配层工程化)
8. [启动与部署](#启动与部署)
9. [AI工具使用说明](#ai工具使用说明)

---

## 项目概述

本项目是厦门大学谷雨大模型实验室 AI Coding 面试的完整交付项目。围绕"厦门旅游"主题，实现了一个前后端分离的单页 Web 应用，涵盖景点浏览、天气查询、路线推荐、评论收藏等核心功能。

**核心设计原则：**
- 所有数据通过后端接口动态获取，前端不写死任何业务数据
- 第三方 API（山河天气、大模型）由后端代理，前端零密钥暴露
- 所有外部依赖视为不稳定依赖，统一做超时、重试、缓存、降级处理
- 代码按 config / db / api / external / recommend / frontend / tests 七层模块化组织

---

## 最终代码架构

```
g:\ai_angent_web\
│
├── main.py                        # 后端入口：FastAPI 应用 + request_id 中间件 + 全局异常 + 静态文件挂载
├── requirements.txt               # Python 依赖清单
├── .env.example                   # 环境变量模板（天气/LLM/DB 全部配置项）
│
├── config/
│   └── settings.py                # 环境变量加载与类型转换
│
├── db/
│   ├── init.sql                   # 9 张表完整建表 DDL + 种子数据（景点/标签/路线/评论/收藏/点赞/天气缓存）
│   └── database.py                # SQLite 连接管理 + init_db / reset_db
│
├── api/
│   ├── attractions.py             # 景点列表（筛选/排序/分页）+ 景点详情
│   ├── interactions.py            # 评论写入 + 收藏写入（幂等 + 防重复提交）
│   ├── weather.py                 # 天气代理接口 + 缓存读写
│   └── recommend.py               # 路线推荐接口（接入适配层）+ 路线保存/列表/详情
│
├── external/
│   └── weather_client.py          # 山河天气 HTTP 客户端 + 温度清洗标准化 + 降级数据构建
│
├── recommend/
│   ├── __init__.py                # 包标记
│   ├── base.py                    # 推荐器抽象基类
│   ├── rule_recommender.py        # 规则引擎实现
│   └── llm_recommender.py         # LLM 推荐器（含 Mock 和自动降级）
│
├── frontend/
│   ├── index.html                 # 单页入口（天气卡片+路线推荐+筛选栏+景点网格+分页栏）
│   ├── css/style.css              # 全响应式布局（移动端适配 + 动画）
│   ├── js/api.js                  # 统一 Fetch 封装 + 异常处理
│   └── js/main.js                 # 全页面逻辑（天气/路线/筛选/分页/收藏/评论）
│   └── images/                    # 15 张景点 SVG 图片（本地自生成）
│
├── scripts/
│   └── fetch_images.py             # 百度图片爬取（icrawler）
├── tests/
│   ├── test_api.py                # 27 项 API 测试（覆盖正常+异常+降级+request_id）
│   └── test_weather.py            # 2 项天气降级测试
│
└── README.md                      # AICoding 交付说明（精简版）
```

### 数据库 ER 关系

```
attractions ──< attraction_tags >── tags
    │
    ├──< comments
    ├──< favorites
    ├──< likes
    ├──< route_items >── routes
    │
    └──  weather_cache（独立）
```

---

## 阶段0：需求拆解与脚手架规划

**日期：** 2026-06-24  
**Git 提交：** `阶段0-需求拆解与脚手架规划 | 对标AI面试文档-全需求分析`  
**状态：** 规划阶段，不产生代码

### 预期目标
- 解析《AI Coding 面试.txt》全部需求点
- 设计数据库表结构、RESTful 接口清单、前端状态覆盖矩阵
- 确定技术栈：Python FastAPI + SQLite + 原生 HTML/CSS/JS
- 输出完整架构规划文档

### 完成步骤
1. 阅读并拆解面试文档 5 大需求块（基础闭环 + 路线推荐 + 筛选排序 + 评论收藏 + 天气代理）
2. 设计 8 张数据库表（attractions / tags / attraction_tags / comments / favorites / weather_cache / routes / route_items）
3. 拟定 6 个 RESTful 接口清单（3 读取 + 3 写入）
4. 规划 7 层代码目录结构（config / db / api / external / recommend / frontend / tests）
5. 输出脚手架规划报告 + 面试参考问答

### 交付物
- 需求分析文档
- 数据库 ER 设计
- 接口清单
- 目录架构图

---

## 阶段1：最小可运行闭环

**日期：** 2026-06-24  
**Git 提交：** `阶段1-景点数据读取闭环与移动端展示 | 对标AI面试文档-宣传页面+真实前后端交互+SQLite初始化`

### 预期目标
- 实现"SQLite → 后端 → 前端"完整数据流
- 前端至少展示 5 个厦门景点
- 前端处理加载中/空数据/请求失败三种异常状态
- 移动端响应式适配

### 新增功能清单
| 功能 | 对应面试文档 |
|:---|:---|
| SQLite 建表 + 6 个景点种子数据 | 03 DB 本地数据库 |
| `GET /api/attractions` 全量读取 | 02 API 真实前后端交互 |
| 前端卡片网格展示 + CSS Grid 响应式 | 01 厦门旅游宣传页面 |
| 加载中/空数据/失败三态处理 | 前端状态要求 |
| 移动端 viewport 适配 | 移动端适配要求 |

### 代码架构变迁

| 操作 | 文件 | 说明 |
|:---|:---|:---|
| **新增** | `config/settings.py` | 环境变量加载：DB_PATH / WEATHER_API_URL 等 |
| **新增** | `db/init.sql` | attractions 表 DDL + 6 条种子数据 |
| **新增** | `db/database.py` | SQLite 连接 + init_db 自动初始化 |
| **新增** | `api/attractions.py` | `GET /api/attractions` 单接口 |
| **新增** | `main.py` | FastAPI 入口 + 静态文件挂载 |
| **新增** | `frontend/index.html` | 单页入口 |
| **新增** | `frontend/css/style.css` | 基础样式 |
| **新增** | `frontend/js/api.js` | Fetch 封装 |
| **新增** | `frontend/js/main.js` | 景点加载 + 异常状态 |
| **新增** | `frontend/images/*.svg` | 6 个景点 SVG 图片（本地自生成） |
| **新增** | `tests/test_api.py` | 景点列表基础测试 |
| **新增** | `requirements.txt` | fastapi/uvicorn/pydantic/pytest/httpx |
| **新增** | `.env.example` | 环境变量模板 |

### 阶段验证
- `pytest` 景点列表接口返回 ≥5 条数据 ✓
- 浏览器 F12 Network 确认数据为 Fetch 动态请求 ✓
- 关闭后端服务，页面显示红色错误提示 ✓
- 手机（同 Wi-Fi）可正常访问 ✓

---

## 阶段2：完善基础模块

**日期：** 2026-06-24  
**Git 提交：** `阶段2-评论收藏与天气代理缓存 | 对标AI面试文档-2个写入接口+天气代理缓存降级+前端基础交互`

### 预期目标
- 实现 2 个写入接口：评论提交 + 收藏
- 后端代理山河天气接口，前端不直连第三方
- 天气结果缓存 30 分钟，异常时降级

### 新增功能清单
| 功能 | 对应面试文档 |
|:---|:---|
| `POST /api/comments` 评论提交（字段校验+防重复） | 3. 评论、收藏与数据一致性 |
| `POST /api/favorites` 收藏（幂等控制） | 3. 评论、收藏与数据一致性 |
| `GET /api/weather/xiamen` 天气代理 | 4. 天气代理、缓存与降级 |
| 天气缓存表 weather_cache + TTL 机制 | 4. 天气代理、缓存与降级 |
| 响应 `{code, msg, data}` 统一 JSON 结构 | RESTful 约束 |
| 全局异常处理器（HTTP 4xx/422/500） | 可维护性 |

### 代码架构变迁

| 操作 | 文件 | 说明 |
|:---|:---|:---|
| **新增** | `api/interactions.py` | 评论/收藏写入接口 + Pydantic 校验 |
| **新增** | `api/weather.py` | 天气代理 + 缓存读写 + 降级策略 |
| **新增** | `external/weather_client.py` | 山河天气 HTTP 客户端（超时/重试/标准化） |
| **修改** | `db/init.sql` | 新增 comments / favorites / weather_cache 三张表 |
| **修改** | `db/database.py` | 数据库路径改由 settings.DB_PATH 控制，增加 reset_db() |
| **修改** | `api/attractions.py` | 列表查询 LEFT JOIN 聚合 comment_count/favorite_count |
| **修改** | `main.py` | 注册 interactions + weather 路由 + 全局异常处理器 |
| **修改** | `.env.example` | 新增 WEATHER_TIMEOUT/RETRY/CACHE_TTL 配置项 |
| **修改** | `frontend/js/api.js` | 新增通用 request() 方法 + submitFavorite/submitComment/getWeather |
| **修改** | `frontend/js/main.js` | 新增天气卡片渲染 + 收藏/评论表单事件绑定 |
| **修改** | `frontend/index.html` | 新增天气区域 |
| **修改** | `frontend/css/style.css` | 新增天气卡片/表单/消息提示样式 |
| **新增** | `tests/test_weather.py` | 天气降级 + 缓存 2 项测试 |
| **修改** | `tests/test_api.py` | 新增评论提交 + 重复/收藏 4 项测试 |

### 阶段验证
- `pytest` 7 passed ✓
- 浏览器可看到天气卡片（实时温度/湿度/旅游指数） ✓
- 点击收藏按钮 → 统计数即时更新 → 重复点击显示"已收藏过" ✓
- 提交评论 → 表单清空 → 显示"评论提交成功" → 评论数 +1 ✓

---

## 阶段3：进阶业务能力

**日期：** 2026-06-25  
**Git 提交：**  
- `阶段3-景点筛选分页排序与路线推荐 | 对标AI面试文档-搜索筛选排序+路线规划推荐+分页异常处理`
- `阶段3-bug修复-天气999温度过滤与观测时间显示 | 对标AI面试文档-天气代理缓存降级`
- `阶段3-bug修复-温度范围倒挂修正与README创建 | 对标AI面试文档-天气代理缓存降级+交付物清单`

### 预期目标
- 实现景点搜索/筛选/排序/分页全功能
- 基于偏好+天气的路线推荐算法
- 自定义路线保存

### 新增功能清单
| 功能 | 对应面试文档 |
|:---|:---|
| 关键词/区域/标签/天气适配/时长 5 维筛选 | 2. 搜索、筛选与排序 |
| 6 种排序 + 升/降序 | 2. 搜索、筛选与排序 |
| 分页（total/page/page_size/has_more） | 2. 搜索、筛选与排序 |
| `GET /api/attractions/:id` 景点详情（+标签+评论） | 推荐数据模型与接口 |
| `GET /api/routes/recommend` 路线推荐（三维评分） | 1. 路线规划与推荐逻辑 |
| `POST /api/routes/custom` 路线保存 | 写入接口要求 |
| `GET /api/routes` + `GET /api/routes/:id` 路线查询 | 推荐数据模型与接口 |
| 前端筛选面板 + 偏好标签 + 分页控件 | 前端状态要求 |
| 天气温度异常值过滤（999→None→推算） | 4. 天气代理、缓存与降级 |
| 温度高低倒挂自动交换 | 4. 天气代理、缓存与降级 |
| 观测时间替代硬编码"今日" | 4. 天气代理、缓存与降级 |

### 代码架构变迁

| 操作 | 文件 | 说明 |
|:---|:---|:---|
| **修改** | `db/init.sql` | 新增 tags / attraction_tags / routes / route_items 表；attractions 表新增 open_time/close_time/recommended_hours/suitable_weather/intensity_level/popularity_score/recommend_score/updated_at 字段 |
| **重写** | `api/attractions.py` | 从单一全量查询重构为：5 维筛选 + 排序白名单 + 分页 + 详情接口 |
| **新增** | `api/recommend.py` | 路线推荐接口（规则评分）+ 路线 CRUD 全套 |
| **修改** | `external/weather_client.py` | 新增 _sanitize_temp 过滤 999；normalize_weather 新增 observe_time/update_time；高低倒挂交换 |
| **重写** | `frontend/index.html` | 新增路线推荐面板 + 筛选栏 + 分页栏 |
| **修改** | `frontend/css/style.css` | 新增路线/筛选/分页全部样式 + 移动端响应式 |
| **修改** | `frontend/js/api.js` | 新增 getAttractions(params)/getAttractionDetail/recommendRoute/saveCustomRoute/getSavedRoutes |
| **重写** | `frontend/js/main.js` | 新增路线推荐/筛选/分页全逻辑；天气文案改为动态观测时间 |
| **修改** | `tests/test_api.py` | 新增 13 项测试（筛选/排序/分页/详情/路线推荐/路线CRUD） |
| **修改** | `build_fallback_weather` | 补 update_time/observe_time 字段 |

### 阶段验证
- `pytest` 22 passed ✓
- 搜索"鼓浪屿"只返回匹配结果 ✓
- 筛选"海边"标签 → 鼓浪屿+环岛路 ✓
- 按热度降序 → 鼓浪屿排第一 ✓
- 路线推荐（人文+摄影+半日游）→ 展示排名+每条推荐理由 ✓
- 温度显示 25°C - 26°C 而非 26°C - 25°C 或 28°C - 999°C ✓

---

## 阶段4：AI推荐适配层 + 工程化

**日期：** 2026-06-25  
**Git 提交：** `阶段4-AI推荐适配层与request_id日志工程化 | 对标AI面试文档-AI辅助推荐适配层+测试日志与可维护性`

### 预期目标
- 实现可替换的 AI 推荐适配层（规则/LLM/Mock 一键切换）
- LLM 调用失败自动降级到规则引擎
- request_id 全链路追踪 + 日志耗时记录
- LLM API Key 零泄露

### 新增功能清单
| 功能 | 对应面试文档 |
|:---|:---|
| 推荐器抽象基类 + 3 种实现 | 5. AI辅助推荐适配层 |
| `RECOMMENDER_TYPE` 环境变量切换推荐器 | 5. 可替换可降级 |
| LLM 调用失败自动回退规则引擎 | 5. AI辅助推荐适配层 |
| request_id 中间件（UUID + 耗时 + X-Request-ID 响应头） | 6. 测试、日志与可维护性 |
| 全异常日志分级（4xx WARNING / 5xx ERROR） | 6. 测试、日志与可维护性 |
| LLM 配置全环境变量（密钥不在代码中） | 5. API Key 保护 |

### 代码架构变迁

| 操作 | 文件 | 说明 |
|:---|:---|:---|
| **新增** | `recommend/__init__.py` | 包标记 |
| **新增** | `recommend/base.py` | 推荐器抽象基类 `BaseRecommender` |
| **新增** | `recommend/rule_recommender.py` | 规则引擎实现（从 api/recommend.py 抽取独立） |
| **新增** | `recommend/llm_recommender.py` | LLM 推荐器 + MockLLM 推荐器 + 自动降级逻辑 |
| **重写** | `api/recommend.py` | 移除内联评分函数，改用 `_get_recommender()` 工厂注入 |
| **重写** | `main.py` | 新增 request_id 中间件 + logging 初始化 + 异常日志 |
| **修改** | `config/settings.py` | 新增 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL / LLM_TIMEOUT_SECONDS / RECOMMENDER_TYPE |
| **修改** | `.env.example` | 新增 LLM 完整配置段 |
| **修改** | `tests/test_api.py` | 新增 request_id 头 2 项 + 推荐器类型标记断言 |
| **删除** | `fix_images.py` | 清理临时脚本 |
| **删除** | `setup_phase1.py` | 清理临时脚本 |

### 阶段验证
- `pytest` 24 passed ✓
- 响应头包含 `X-Request-ID` ✓
- 终端日志输出 `request_id=xxx | GET /api/attractions | 200 | 12.3ms` ✓
- 环境变量 `RECOMMENDER_TYPE=mock` → 路线推荐标记为 `mock-llm` ✓
- 环境变量 `RECOMMENDER_TYPE=llm` + 无效 API Key → 自动降级为 `rule-fallback` + 标记 `llm_error=True` ✓

---
## 阶段5 · 点赞推荐 + 数据扩充 + 真实图片

### 预计用时
1.5h ｜ 29 passed

### 新增功能
- **点赞推荐**：`POST /api/likes`，device_id 唯一约束（每用户每景点限一次），自动联动 `popularity_score`（like×4 + fav×2 + comment）
- **景点扩充**：15 个景点覆盖 4 行政区（思明区 8、集美区 2、湖里区 1、海沧区 2）
- **真实图片爬取**：`scripts/fetch_images.py` 百度图片搜索中文关键词 → 重命名保存 `frontend/images/real/`
- **图片加载兜底**：前端 `<img onerror>` SVG 自动降级

### 新增文件 / 变更

| 操作 | 文件 | 说明 |
|:---|:---|:---|
| **新增** | `scripts/fetch_images.py` | icrawler 百度图片爬取 |
| **新增** | `frontend/images/hulishan.svg` 等 9 张 | 新景点 SVG |
| **修改** | `db/init.sql` | likes 表 + 15 景点种子 + 点赞种子 |
| **修改** | `api/interactions.py` | POST /api/likes + 热度联动 UPDATE |
| **修改** | `api/attractions.py` | SQL 新增 like_count LEFT JOIN |
| **修改** | `frontend/js/main.js` | 点赞按钮事件 + 图片 onerror 降级 |
| **修改** | `frontend/css/style.css` | 点赞按钮红色样式 |
| **修改** | `requirements.txt` | 新增 icrawler |
| **修改** | `tests/test_api.py` | 点赞/重复点赞/区域筛选/29→27→29 项 |

### 阶段验证
- `pytest` 29 passed ✓
- 点赞点击即时更新统计 → 重复点击 "已点赞过" ✓
- 筛选"集美区" → 集美学村+园博苑 ✓
- SQL 查询验证 popularity_score 联动更新 ✓
- 前端 onerror 自动降级 SVG ✓

---
## 启动与部署

### 前置条件
- Python 3.10+
- pip

### 安装
```bash
git clone <仓库地址>
cd ai_angent_web
pip install -r requirements.txt
cp .env.example .env
```

### 数据库初始化
```bash
# 首次启动自动初始化；如需重建：
python -c "from db.database import reset_db; reset_db()"
```

### 启动服务
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 访问
- PC 浏览器：`http://127.0.0.1:8000/`
- 手机（同 Wi-Fi）：`http://<电脑局域网IP>:8000/`

### 运行测试
```bash
python -m pytest tests/ -v
# 预期：29 passed
```

### 环境变量说明
| 变量 | 默认值 | 说明 |
|:---|:---|:---|
| `WEATHER_API_URL` | `http://shanhe.kim/api/za/tianqi.php` | 山河天气接口 |
| `WEATHER_TIMEOUT_SECONDS` | `3` | 天气请求超时 |
| `WEATHER_RETRY_COUNT` | `2` | 天气请求重试次数 |
| `WEATHER_CACHE_TTL_SECONDS` | `1800` | 天气缓存有效期 |
| `DB_PATH` | `./xiamen_travel.db` | SQLite 文件路径 |
| `RECOMMENDER_TYPE` | `rule` | 推荐器类型：rule / mock / llm |
| `LLM_API_KEY` | (空) | 大模型 API Key |
| `LLM_BASE_URL` | `https://api.openai.com/v1` | LLM 服务地址 |
| `LLM_MODEL` | `gpt-3.5-turbo` | 模型名称 |
| `LLM_TIMEOUT_SECONDS` | `10` | LLM 请求超时 |

---

## AI工具使用说明

### 使用的 AI 工具
- **TRAE IDE（AI 编程助手）**：用于代码生成、结构设计、调试辅助

### AI 参与环节
| 环节 | AI 参与内容 | 人工校验方式 |
|:---|:---|:---|
| 数据库设计 | 生成 8 张表的 DDL 和种子数据 | 对照面试文档逐字段核验 |
| API 接口实现 | 生成 FastAPI 路由、Pydantic 校验 | 运行 pytest 全覆盖验证 |
| 天气客户端 | 生成 HTTP 重试、异常值过滤、降级逻辑 | 模拟 999 温度/超时/空数据场景测试 |
| 推荐算法 | 生成规则评分函数、贪心选择逻辑 | 手工构造偏好+天气组合验证排序合理性 |
| 前端页面 | 生成 HTML/CSS/JS 全部代码 | 浏览器真实交互 + 手机适配测试 |
| request_id 日志 | 生成中间件和异常处理器改造 | 终端观察日志输出格式和耗时 |
| README 文档 | 生成阶段总结和架构说明 | 逐阶段核验文件变更清单 |

### 关键提示词策略
- 分阶段迭代：每次只要求完成面试文档的一个需求块
- 测试驱动：代码生成后立即要求编写 pytest 并验证通过
- 异常优先：每次都要求"先考虑失败场景再写正常路径"

### AI 输出校验方法
1. 每个接口生成后立即用 `TestClient` 编写正向+异常测试
2. 前端代码生成后在浏览器 F12 Network/Console 验证请求和状态流转
3. 天气接口用真实山河 API 返回数据校验温度/时间字段
4. 统计字段在终端 SQL 查询验证与前端显示一致
