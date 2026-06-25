# 厦门旅游宣传单页 Web 应用

厦门大学谷雨大模型实验室 · AI Coding 面试测试题  
技术栈：Python (FastAPI) + SQLite + 原生 HTML/CSS/JS

---

## 版本记录

| 版本 | 提交描述 | 日期 |
|:---|:---|:---|
| 阶段0 | 需求拆解与脚手架规划 | 2026-06-24 |
| 阶段1 | 景点数据读取闭环与移动端展示 | 2026-06-24 |
| 阶段2 | 评论收藏与天气代理缓存 | 2026-06-24 |
| 阶段3 | 景点筛选排序与路线推荐 | 2026-06-25 |
| 阶段4 | AI推荐适配层与工程化 | 2026-06-25 |

---

## 依赖安装

```bash
pip install -r requirements.txt
cp .env.example .env
```

---

## 数据库初始化

```bash
python -c "from db.database import reset_db; reset_db()"
```

初始化脚本：[db/init.sql](db/init.sql)，包含 8 张表的 DDL 和种子数据。

---

## 启动服务

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

- PC 浏览器：`http://127.0.0.1:8000/`
- 手机访问：需同 Wi-Fi，访问 `http://<电脑IP>:8000/`（必须用 `--host 0.0.0.0`）

---

## 运行测试

```bash
python -m pytest tests/ -v
# 预期：24 passed
```

---

## 环境变量

| 变量 | 默认值 | 说明 |
|:---|:---|:---|
| `WEATHER_API_URL` | `http://shanhe.kim/api/za/tianqi.php` | 山河天气接口 |
| `WEATHER_TIMEOUT_SECONDS` | `3` | 超时秒数 |
| `WEATHER_RETRY_COUNT` | `2` | 重试次数 |
| `WEATHER_CACHE_TTL_SECONDS` | `1800` | 缓存秒数（30min） |
| `DB_PATH` | `./xiamen_travel.db` | SQLite 文件路径 |
| `RECOMMENDER_TYPE` | `rule` | 推荐器：`rule`/`mock`/`llm` |
| `LLM_API_KEY` | (空) | 大模型 API Key |
| `LLM_BASE_URL` | `https://api.openai.com/v1` | LLM 服务地址 |
| `LLM_MODEL` | `gpt-3.5-turbo` | 模型名称 |
| `LLM_TIMEOUT_SECONDS` | `10` | LLM 超时 |

---

## 项目结构

```
├── main.py                  # FastAPI 入口 + request_id 中间件 + 异常处理
├── config/settings.py        # 环境变量加载
├── db/
│   ├── init.sql              # 8 表 DDL + 种子数据
│   └── database.py           # SQLite 连接管理
├── api/
│   ├── attractions.py        # 景点列表（筛选/排序/分页）+ 详情
│   ├── interactions.py       # 评论写入 + 收藏写入
│   ├── weather.py            # 天气代理 + 缓存降级
│   └── recommend.py          # 路线推荐 + 路线 CRUD
├── external/
│   └── weather_client.py     # 山河天气客户端
├── recommend/
│   ├── base.py               # 推荐器抽象基类
│   ├── rule_recommender.py   # 规则引擎
│   └── llm_recommender.py    # LLM/Mock 推荐器
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   ├── js/api.js
│   ├── js/main.js
│   └── images/               # 6 张景点 SVG
└── tests/
    ├── test_api.py            # 22 项 API 测试
    └── test_weather.py        # 2 项天气降级测试
```

---

## 接口清单

| 方法 | 路径 | 说明 |
|:---|:---|:---|
| GET | `/api/attractions` | 景点列表（支持 keyword/region/tag/sort/page） |
| GET | `/api/attractions/{id}` | 景点详情（+标签+评论） |
| GET | `/api/weather/xiamen` | 厦门实时天气（缓存30min，失败降级） |
| GET | `/api/routes/recommend` | 路线推荐（偏好+天气+时长） |
| GET | `/api/routes` | 已保存路线列表 |
| GET | `/api/routes/{id}` | 路线详情 |
| POST | `/api/comments` | 提交评论（防重复提交） |
| POST | `/api/favorites` | 收藏景点（幂等） |
| POST | `/api/routes/custom` | 保存自定义路线 |

---

## 已完成的功能及对应需求

| 面试文档需求 | 实现 |
|:---|:---|
| 宣传页面（≥5个景点，信息层级，移动端适配） | 6 个景点卡片 + CSS Grid 响应式 + viewport meta |
| 3 个读取接口 + 2 个写入接口 | 6 个读取 + 3 个写入，统一 JSON 错误结构 |
| SQLite 本地数据库 + 建表脚本 + 样例数据 | 8 张表 + `db/init.sql` + `reset_db()` |
| 天气后端代理 + 缓存 + 降级 | `_sanitize_temp` 过滤异常值 + 缓存 30min + 过期缓存回退 + fallback |
| 路线推荐（偏好/天气/时长/推荐理由） | 三维评分规则引擎 + 贪心选择 |
| 筛选/排序/分页 + 非法参数/空结果处理 | 5 维筛选 + 6 种排序 + 白名单校验 + 分页元信息 |
| 评论收藏 + 字段校验 + 防重复 + 幂等 | submission_token UNIQUE + device_id 联合唯一 |
| AI 推荐适配层（可替换/可降级/密钥保护） | RECOMMENDER_TYPE 切换 + LLM 失败降级规则引擎 + .env 存储密钥 |
| request_id + 日志 + 测试 | UUID 中间件 + 耗时日志 + 24 项 pytest |

---

## 异常处理覆盖

| 异常场景 | 处理方式 |
|:---|:---|
| 天气接口超时/不可达 | 过期缓存 → fallback，页面不白屏 |
| 天气温度占位值 999 | `_sanitize_temp` 过滤 → 用当前温推算 |
| 温度高低倒挂 | 自动交换 |
| 重复提交评论 | 409 Conflict |
| 重复收藏 | 幂等返回 duplicated=true |
| 非法筛选参数 | 400 + 可选值提示 |
| 景点不存在 | 404 |
| 搜索结果为空 | "没有找到匹配的景点" |
| LLM 调用失败 | 自动降级规则引擎 + 标记 llm_error |
| 前端加载失败 | try-catch + 红色错误提示 |

---

## 演示流程建议

1. 启动服务，打开 `http://127.0.0.1:8000/`
2. 天气卡片：展示实时温度 + 观测时间 + 旅游指数 + 服务状态（live/cache/fallback）
3. 路线推荐：勾选偏好标签 → 生成推荐路线 → 查看推荐理由 → 保存路线
4. 景点筛选：搜索关键词/切换区域/标签/排序 → 翻页
5. 收藏评论：点击收藏 → 统计即时更新 → 提交评论 → 评论数变化
6. 终端验证：执行 SQL 查询展示数据写入 + `grep request_id` 展示日志追踪
