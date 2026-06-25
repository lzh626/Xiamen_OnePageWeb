import json
import time

import httpx

from config.settings import (
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_TIMEOUT_SECONDS,
)
from recommend.base import BaseRecommender
from recommend.rule_recommender import RuleRecommender


class LLMRecommender(BaseRecommender):

    def __init__(self):
        self._fallback = RuleRecommender()

    def _build_prompt(self, preferences, duration, weather, attractions):
        names = [a["name"] for a in attractions]
        current_weather = weather.get("current_weather", "未知")
        tourism_index = weather.get("tourism_index", "暂无")
        duration_label = "半日游" if duration == "half_day" else "一日游"

        return f"""你是厦门旅游推荐助手。请根据以下信息推荐一条{duration_label}路线。

用户偏好：{', '.join(preferences)}
当前天气：{current_weather}，旅游指数：{tourism_index}
可选景点：{json.dumps(names, ensure_ascii=False)}

请返回仅含 JSON 的回复，格式严格如下：
{{"route": [{{"name": "景点名", "reason": "推荐理由（20字内）"}}], "summary": "一句话总结（30字内）"}}

要求：
1. 根据用户偏好和天气筛选3-5个最合适的景点
2. 推荐理由需结合天气和偏好
3. 按推荐优先级排序"""

    def _call_llm(self, prompt):
        if not LLM_API_KEY or not LLM_BASE_URL:
            raise RuntimeError("LLM not configured")

        for attempt in range(2):
            try:
                resp = httpx.post(
                    f"{LLM_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {LLM_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": LLM_MODEL,
                        "messages": [
                            {"role": "system", "content": "你只返回合法JSON，不输出其他内容。"},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.7,
                        "max_tokens": 600,
                    },
                    timeout=LLM_TIMEOUT_SECONDS,
                )
                resp.raise_for_status()
                body = resp.json()
                content = body["choices"][0]["message"]["content"].strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[-1]
                    content = content.rsplit("```", 1)[0]
                return json.loads(content)
            except (httpx.HTTPError, json.JSONDecodeError, KeyError, IndexError) as exc:
                if attempt == 1:
                    raise RuntimeError(f"LLM call failed: {exc}") from exc
                time.sleep(0.5)

    def recommend(self, preferences, duration, weather, attractions):
        try:
            prompt = self._build_prompt(preferences, duration, weather, attractions)
            llm_result = self._call_llm(prompt)
        except RuntimeError:
            fallback_result = self._fallback.recommend(
                preferences, duration, weather, attractions
            )
            fallback_result["recommender"] = "rule-fallback"
            fallback_result["llm_error"] = True
            return fallback_result

        name_map = {a["name"]: a for a in attractions}
        selected = []
        for item in llm_result.get("route", []):
            name = item.get("name", "")
            reason = item.get("reason", "")
            attr = name_map.get(name)
            if attr:
                selected.append({
                    "attraction": dict(attr),
                    "reasons": [reason] if reason else [],
                })

        total_hours = sum(a["attraction"].get("recommended_hours", 1.5) for a in selected)

        return {
            "route": selected,
            "estimated_duration": f"{total_hours:.1f}小时",
            "recommender": "llm",
            "llm_summary": llm_result.get("summary", ""),
            "llm_error": False,
        }


class MockLLMRecommender(BaseRecommender):

    def recommend(self, preferences, duration, weather, attractions):
        max_hours = 2.5 if duration == "half_day" else 5.0
        selected = []
        total_hours = 0.0

        for attr in attractions:
            hours = attr.get("recommended_hours", 1.5)
            if total_hours + hours > max_hours + 0.5:
                if total_hours >= max_hours:
                    continue
            pref_text = f"AI模型推荐：匹配偏好「{preferences[0] if preferences else '综合'}」"
            selected.append({
                "attraction": dict(attr),
                "reasons": [pref_text],
            })
            total_hours += hours
            if len(selected) >= 4:
                break

        return {
            "route": selected,
            "estimated_duration": f"{total_hours:.1f}小时",
            "recommender": "mock-llm",
            "llm_summary": "基于AI模型（模拟）生成的推荐路线，实际部署时替换为真实大模型。",
            "llm_error": False,
        }
