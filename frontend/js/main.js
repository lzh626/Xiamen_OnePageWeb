document.addEventListener('DOMContentLoaded', () => {
    loadWeather();
    loadAttractions();
});

function getDeviceId() {
    const cacheKey = 'xiamen-travel-device-id';
    let deviceId = localStorage.getItem(cacheKey);
    if (!deviceId) {
        deviceId = `device-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`;
        localStorage.setItem(cacheKey, deviceId);
    }
    return deviceId;
}

async function loadWeather() {
    const loading = document.getElementById('weather-loading');
    const errorMsg = document.getElementById('weather-error');
    const card = document.getElementById('weather-card');

    try {
        const weather = await API.getWeather();
        loading.classList.add('hidden');
        errorMsg.classList.add('hidden');

        const degradeText = weather.degraded
            ? `<span>服务状态：已降级 (${weather.source})</span>`
            : `<span>服务状态：正常 (${weather.source})</span>`;

        card.innerHTML = `
            <div class="weather-top">
                <div>
                    <h3>${weather.city} · ${weather.current_weather}</h3>
                    <p class="weather-temp">${weather.current_temp}°C</p>
                    <p>${weather.low_temp}°C - ${weather.high_temp}°C | 今日 ${weather.today_weather}</p>
                </div>
                <div>
                    <p>${degradeText}</p>
                    <p>旅游指数：${weather.tourism_index}</p>
                </div>
            </div>
            <div class="weather-meta">
                <div class="weather-meta-item">湿度：${weather.humidity}</div>
                <div class="weather-meta-item">空气质量：${weather.air_quality}</div>
                <div class="weather-meta-item">城市：${weather.city}</div>
                <div class="weather-meta-item">缓存来源：${weather.source}</div>
            </div>
            <p class="weather-tip">${weather.tourism_tips}</p>
        `;
        card.classList.remove('hidden');
    } catch (error) {
        loading.classList.add('hidden');
        errorMsg.textContent = `天气加载失败：${error.message}`;
        errorMsg.classList.remove('hidden');
    }
}

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

        grid.innerHTML = data.map((item) => `
            <article class="card" data-attraction-id="${item.id}">
                <img src="${item.cover_image}" alt="${item.name}" loading="lazy">
                <div class="card-content">
                    <h3>${item.name}</h3>
                    <p class="meta">区域：${item.region} | 推荐时长：${item.rec_time}</p>
                    <p class="desc">${item.description}</p>
                    <div class="stats-row">
                        <span>收藏 <strong data-favorite-count="${item.id}">${item.favorite_count || 0}</strong></span>
                        <span>评论 <strong data-comment-count="${item.id}">${item.comment_count || 0}</strong></span>
                    </div>
                    <button class="action-btn favorite-btn" data-favorite-btn="${item.id}">收藏这个景点</button>
                    <form class="comment-form" data-comment-form="${item.id}">
                        <input name="user_name" type="text" maxlength="20" placeholder="你的昵称（最多20字）" required>
                        <textarea name="content" maxlength="200" placeholder="写下你的游玩建议（最多200字）" required></textarea>
                        <button class="action-btn comment-btn" type="submit">提交评论</button>
                        <p class="inline-msg" data-form-message="${item.id}"></p>
                    </form>
                </div>
            </article>
        `).join('');
        bindCardEvents();
        grid.classList.remove('hidden');
    } catch (error) {
        loading.classList.add('hidden');
        errorMsg.textContent = `加载景点失败：${error.message}`;
        errorMsg.classList.remove('hidden');
    }
}

function bindCardEvents() {
    document.querySelectorAll('[data-favorite-btn]').forEach((button) => {
        button.addEventListener('click', handleFavoriteClick);
    });
    document.querySelectorAll('[data-comment-form]').forEach((form) => {
        form.addEventListener('submit', handleCommentSubmit);
    });
}

async function handleFavoriteClick(event) {
    const button = event.currentTarget;
    const attractionId = Number(button.dataset.favoriteBtn);
    button.disabled = true;
    button.textContent = '收藏提交中...';

    try {
        const result = await API.submitFavorite({
            attraction_id: attractionId,
            device_id: getDeviceId()
        });
        document.querySelector(`[data-favorite-count="${attractionId}"]`).textContent = result.favorite_count;
        button.textContent = result.duplicated ? '已收藏过' : '收藏成功';
    } catch (error) {
        button.disabled = false;
        button.textContent = '收藏这个景点';
        alert(`收藏失败：${error.message}`);
    }
}

async function handleCommentSubmit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const attractionId = Number(form.dataset.commentForm);
    const button = form.querySelector('button[type="submit"]');
    const message = form.querySelector(`[data-form-message="${attractionId}"]`);
    const formData = new FormData(form);
    const userName = String(formData.get('user_name') || '').trim();
    const content = String(formData.get('content') || '').trim();

    message.className = 'inline-msg';
    message.textContent = '';

    if (!userName || !content) {
        message.classList.add('error');
        message.textContent = '昵称和评论内容不能为空。';
        return;
    }

    button.disabled = true;
    button.textContent = '评论提交中...';

    try {
        const result = await API.submitComment({
            attraction_id: attractionId,
            user_name: userName,
            content,
            submission_token: `comment-${attractionId}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`
        });
        document.querySelector(`[data-comment-count="${attractionId}"]`).textContent = result.comment_count;
        form.reset();
        message.classList.add('success');
        message.textContent = '评论提交成功，已更新统计。';
    } catch (error) {
        message.classList.add('error');
        message.textContent = error.message;
    } finally {
        button.disabled = false;
        button.textContent = '提交评论';
    }
}
