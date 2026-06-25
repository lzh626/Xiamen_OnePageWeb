document.addEventListener('DOMContentLoaded', () => {
    loadWeather();
    loadAttractions();
    bindRouteEvents();
    bindFilterEvents();
});

function getDeviceId() {
    const cacheKey = 'xiamen-travel-device-id';
    let deviceId = localStorage.getItem(cacheKey);
    if (!deviceId) {
        deviceId = 'device-' + Date.now() + '-' + Math.random().toString(16).slice(2, 10);
        localStorage.setItem(cacheKey, deviceId);
    }
    return deviceId;
}

function getSelectedPreferences() {
    const chips = document.querySelectorAll('.pref-chip.active');
    return Array.from(chips).map(function (c) { return c.dataset.pref; });
}

function bindRouteEvents() {
    document.querySelectorAll('.pref-chip').forEach(function (chip) {
        chip.addEventListener('click', function () {
            chip.classList.toggle('active');
        });
    });

    document.getElementById('recommend-btn').addEventListener('click', handleRecommend);
    document.getElementById('reset-recommend-btn').addEventListener('click', function () {
        document.querySelectorAll('.pref-chip').forEach(function (c) { c.classList.remove('active'); });
        document.getElementById('route-result').classList.add('hidden');
        document.getElementById('route-error').classList.add('hidden');
    });
}

async function handleRecommend() {
    const routeLoading = document.getElementById('route-loading');
    const routeError = document.getElementById('route-error');
    const routeResult = document.getElementById('route-result');
    const duration = document.getElementById('route-duration').value;
    const prefs = getSelectedPreferences();

    routeResult.classList.add('hidden');
    routeError.classList.add('hidden');
    routeLoading.classList.remove('hidden');

    try {
        const data = await API.recommendRoute(prefs, duration);
        routeLoading.classList.add('hidden');
        renderRouteResult(data);
        routeResult.classList.remove('hidden');
    } catch (error) {
        routeLoading.classList.add('hidden');
        routeError.textContent = '路线推荐失败：' + error.message;
        routeError.classList.remove('hidden');
    }
}

function renderRouteResult(data) {
    var routeDiv = document.getElementById('route-result');
    var html = '<div class="route-summary">';
    html += '<span class="route-summary-item">预计时长：' + (data.estimated_duration || '--') + '</span>';
    html += '<span class="route-summary-item">天气：' + (data.matched_weather || '--') + '</span>';
    html += '<span class="route-summary-item">旅游建议：' + (data.weather_summary && data.weather_summary.tourism_tips ? data.weather_summary.tourism_tips : '--') + '</span>';
    html += '</div>';

    if (!data.route || data.route.length === 0) {
        html += '<p class="state-msg">当前偏好下暂无推荐景点，请调整偏好重试。</p>';
        routeDiv.innerHTML = html;
        return;
    }

    data.route.forEach(function (item, index) {
        html += '<div class="route-item">';
        html += '<div class="route-item-number">' + (index + 1) + '</div>';
        html += '<div class="route-item-content">';
        html += '<h4>' + item.attraction.name + '</h4>';
        html += '<p style="font-size:0.85rem;color:#718096;">区域：' + item.attraction.region + ' | 建议时长：' + item.attraction.recommended_hours + '小时</p>';
        if (item.reasons && item.reasons.length > 0) {
            html += '<ul class="route-reasons">';
            item.reasons.forEach(function (r) {
                html += '<li class="route-reason">' + r + '</li>';
            });
            html += '</ul>';
        }
        html += '</div></div>';
    });

    html += '<button class="action-btn route-save-btn" id="save-route-btn">保存这条路线</button>';
    routeDiv.innerHTML = html;

    var saveBtn = document.getElementById('save-route-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', function () {
            handleSaveRoute(data);
        });
    }
}

async function handleSaveRoute(data) {
    var routeName = prompt('请输入路线名称：', '我的推荐路线');
    if (!routeName) return;

    var attractionIds = data.route.map(function (item) { return item.attraction.id; });
    try {
        await API.saveCustomRoute({
            name: routeName,
            attraction_ids: attractionIds,
            preferences: getSelectedPreferences(),
            notes: '基于推荐路线保存'
        });
        alert('路线「' + routeName + '」保存成功！');
    } catch (error) {
        alert('路线保存失败：' + error.message);
    }
}

var currentFilter = {
    keyword: '',
    region: '',
    tag: '',
    sort_by: 'recommend_score',
    order: 'desc',
    page: 1,
    page_size: 12
};

function bindFilterEvents() {
    document.getElementById('apply-filter-btn').addEventListener('click', function () {
        currentFilter.keyword = document.getElementById('filter-keyword').value.trim();
        currentFilter.region = document.getElementById('filter-region').value;
        currentFilter.tag = document.getElementById('filter-tag').value;
        currentFilter.sort_by = document.getElementById('filter-sort').value;
        currentFilter.order = document.getElementById('filter-order').value;
        currentFilter.page = 1;
        loadAttractions(currentFilter);
    });

    document.getElementById('reset-filter-btn').addEventListener('click', function () {
        document.getElementById('filter-keyword').value = '';
        document.getElementById('filter-region').value = '';
        document.getElementById('filter-tag').value = '';
        document.getElementById('filter-sort').value = 'recommend_score';
        document.getElementById('filter-order').value = 'desc';
        currentFilter = { keyword: '', region: '', tag: '', sort_by: 'recommend_score', order: 'desc', page: 1, page_size: 12 };
        loadAttractions(currentFilter);
    });

    document.getElementById('prev-page').addEventListener('click', function () {
        if (currentFilter.page > 1) {
            currentFilter.page -= 1;
            loadAttractions(currentFilter);
        }
    });

    document.getElementById('next-page').addEventListener('click', function () {
        currentFilter.page += 1;
        loadAttractions(currentFilter);
    });

    document.getElementById('filter-keyword').addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            document.getElementById('apply-filter-btn').click();
        }
    });
}

async function loadWeather() {
    var loading = document.getElementById('weather-loading');
    var errorMsg = document.getElementById('weather-error');
    var card = document.getElementById('weather-card');

    try {
        var weather = await API.getWeather();
        loading.classList.add('hidden');
        errorMsg.classList.add('hidden');

        var degradeText = weather.degraded
            ? '<span>服务状态：已降级 (' + weather.source + ')</span>'
            : '<span>服务状态：正常 (' + weather.source + ')</span>';

        card.innerHTML =
            '<div class="weather-top">' +
                '<div>' +
                    '<h3>' + weather.city + ' · ' + weather.current_weather + '</h3>' +
                    '<p class="weather-temp">' + weather.current_temp + '°C</p>' +
                    '<p>' + weather.low_temp + '°C - ' + weather.high_temp + '°C | ' + (weather.observe_time || weather.update_time || '今日') + ' ' + weather.today_weather + '</p>' +
                '</div>' +
                '<div>' +
                    '<p>' + degradeText + '</p>' +
                    '<p>旅游指数：' + weather.tourism_index + '</p>' +
                '</div>' +
            '</div>' +
            '<div class="weather-meta">' +
                '<div class="weather-meta-item">湿度：' + weather.humidity + '</div>' +
                '<div class="weather-meta-item">空气质量：' + weather.air_quality + '</div>' +
                '<div class="weather-meta-item">城市：' + weather.city + '</div>' +
                '<div class="weather-meta-item">缓存来源：' + weather.source + '</div>' +
            '</div>' +
            '<p class="weather-tip">' + weather.tourism_tips + '</p>';
        card.classList.remove('hidden');
    } catch (error) {
        loading.classList.add('hidden');
        errorMsg.textContent = '天气加载失败：' + error.message;
        errorMsg.classList.remove('hidden');
    }
}

async function loadAttractions(filters) {
    var f = filters || currentFilter;
    var loading = document.getElementById('attractions-loading');
    var errorMsg = document.getElementById('attractions-error');
    var grid = document.getElementById('attractions-grid');
    var pagination = document.getElementById('pagination-bar');

    loading.classList.remove('hidden');
    errorMsg.classList.add('hidden');
    grid.classList.add('hidden');
    pagination.classList.add('hidden');

    try {
        var params = {
            keyword: f.keyword || undefined,
            region: f.region || undefined,
            tag: f.tag || undefined,
            sort_by: f.sort_by,
            order: f.order,
            page: f.page,
            page_size: f.page_size
        };
        var result = await API.getAttractions(params);
        loading.classList.add('hidden');

        var items = result.items || [];
        var pag = result.pagination || {};

        if (items.length === 0) {
            errorMsg.textContent = '没有找到匹配的景点，请调整筛选条件。';
            errorMsg.classList.remove('hidden');
            return;
        }

        grid.innerHTML = items.map(function (item) {
            var realPath = item.cover_image.replace('.svg', '.jpg').replace('/images/', '/images/real/');
            return '<article class="card" data-attraction-id="' + item.id + '">' +
                '<img src="' + realPath + '" alt="' + item.name + '" loading="lazy" onerror="this.onerror=null;this.src=\'' + item.cover_image + '\'">' +
                '<div class="card-content">' +
                    '<h3>' + item.name + '</h3>' +
                    '<p class="meta">区域：' + item.region + ' | 推荐时长：' + item.rec_time + '</p>' +
                    '<p class="desc">' + item.description + '</p>' +
                    '<div class="stats-row">' +
                        '<span>点赞 <strong data-like-count="' + item.id + '">' + (item.like_count || 0) + '</strong></span>' +
                        '<span>收藏 <strong data-favorite-count="' + item.id + '">' + (item.favorite_count || 0) + '</strong></span>' +
                        '<span>评论 <strong data-comment-count="' + item.id + '">' + (item.comment_count || 0) + '</strong></span>' +
                    '</div>' +
                    '<div class="action-buttons">' +
                        '<button class="action-btn like-btn" data-like-btn="' + item.id + '">点赞推荐</button>' +
                        '<button class="action-btn favorite-btn" data-favorite-btn="' + item.id + '">收藏这个景点</button>' +
                    '</div>' +
                    '<form class="comment-form" data-comment-form="' + item.id + '">' +
                        '<input name="user_name" type="text" maxlength="20" placeholder="你的昵称（最多20字）" required>' +
                        '<textarea name="content" maxlength="200" placeholder="写下你的游玩建议（最多200字）" required></textarea>' +
                        '<button class="action-btn comment-btn" type="submit">提交评论</button>' +
                        '<p class="inline-msg" data-form-message="' + item.id + '"></p>' +
                    '</form>' +
                '</div>' +
            '</article>';
        }).join('');
        bindCardEvents();
        grid.classList.remove('hidden');

        document.getElementById('page-info').textContent = '第 ' + pag.page + ' 页 / 共 ' + pag.total_pages + ' 页（' + pag.total + ' 条）';
        document.getElementById('prev-page').disabled = pag.page <= 1;
        document.getElementById('next-page').disabled = !pag.has_more;
        pagination.classList.remove('hidden');
    } catch (error) {
        loading.classList.add('hidden');
        errorMsg.textContent = '加载景点失败：' + error.message;
        errorMsg.classList.remove('hidden');
    }
}

function bindCardEvents() {
    document.querySelectorAll('[data-like-btn]').forEach(function (button) {
        button.addEventListener('click', handleLikeClick);
    });
    document.querySelectorAll('[data-favorite-btn]').forEach(function (button) {
        button.addEventListener('click', handleFavoriteClick);
    });
    document.querySelectorAll('[data-comment-form]').forEach(function (form) {
        form.addEventListener('submit', handleCommentSubmit);
    });
}

async function handleLikeClick(event) {
    var button = event.currentTarget;
    var attractionId = Number(button.dataset.likeBtn);
    button.disabled = true;
    button.textContent = '点赞中...';

    try {
        var result = await API.submitLike({
            attraction_id: attractionId,
            device_id: getDeviceId()
        });
        document.querySelector('[data-like-count="' + attractionId + '"]').textContent = result.like_count;
        button.textContent = result.duplicated ? '已点赞过' : '已点赞';
    } catch (error) {
        button.disabled = false;
        button.textContent = '点赞推荐';
        alert('点赞失败：' + error.message);
    }
}

async function handleFavoriteClick(event) {
    var button = event.currentTarget;
    var attractionId = Number(button.dataset.favoriteBtn);
    button.disabled = true;
    button.textContent = '收藏提交中...';

    try {
        var result = await API.submitFavorite({
            attraction_id: attractionId,
            device_id: getDeviceId()
        });
        document.querySelector('[data-favorite-count="' + attractionId + '"]').textContent = result.favorite_count;
        button.textContent = result.duplicated ? '已收藏过' : '收藏成功';
    } catch (error) {
        button.disabled = false;
        button.textContent = '收藏这个景点';
        alert('收藏失败：' + error.message);
    }
}

async function handleCommentSubmit(event) {
    event.preventDefault();
    var form = event.currentTarget;
    var attractionId = Number(form.dataset.commentForm);
    var button = form.querySelector('button[type="submit"]');
    var message = form.querySelector('[data-form-message="' + attractionId + '"]');
    var formData = new FormData(form);
    var userName = String(formData.get('user_name') || '').trim();
    var content = String(formData.get('content') || '').trim();

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
        var result = await API.submitComment({
            attraction_id: attractionId,
            user_name: userName,
            content: content,
            submission_token: 'comment-' + attractionId + '-' + Date.now() + '-' + Math.random().toString(16).slice(2, 8)
        });
        document.querySelector('[data-comment-count="' + attractionId + '"]').textContent = result.comment_count;
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
