from recommend.base import BaseRecommender


class RuleRecommender(BaseRecommender):

    def _score_attraction(self, attraction, preferences, weather):
        score = 0
        reasons = []

        if attraction["intensity_level"] == "low" and "低强度" in preferences:
            score += 20
            reasons.append("低强度友好，适合轻松游玩")

        intensity_bonus = {"low": 15, "medium": 10}
        score += intensity_bonus.get(attraction["intensity_level"], 5)
        score += min(attraction.get("recommend_score", 0) // 5, 20)
        score += min(attraction.get("popularity_score", 0) // 5, 20)

        current_w = weather.get("current_weather", "")
        suitable = attraction.get("suitable_weather", "")
        if current_w and suitable and current_w in suitable:
            score += 25
            reasons.append(f"当前天气{current_w}适合游玩")

        tourism = weather.get("tourism_index", "")
        if tourism in ("适宜", "较适宜"):
            score += 15
            reasons.append(f"旅游指数「{tourism}」")
        elif tourism == "不适宜":
            reasons.append(f"旅游指数「{tourism}」，建议优先考虑室内景点")

        tag_names = attraction.get("tag_names", [])
        for pref in preferences:
            if pref in tag_names:
                score += 15
                reasons.append(f"属于「{pref}」类景点")

        return score, reasons

    def recommend(self, preferences, duration, weather, attractions):
        tagged = []
        for attr in attractions:
            d = dict(attr)
            d.setdefault("tag_names", [])
            tagged.append(d)

        scored = []
        for attr in tagged:
            s, r = self._score_attraction(attr, preferences, weather)
            scored.append((s, r, attr))

        scored.sort(key=lambda x: x[0], reverse=True)

        max_hours = 2.5 if duration == "half_day" else 5.0
        selected = []
        total_hours = 0.0

        for _, reasons, attr in scored:
            hours = attr.get("recommended_hours", 1.5)
            if total_hours + hours > max_hours + 0.5:
                if total_hours >= max_hours:
                    continue
            selected.append({"attraction": attr, "reasons": reasons})
            total_hours += hours

        return {
            "route": selected,
            "estimated_duration": f"{total_hours:.1f}小时",
            "recommender": "rule",
        }
