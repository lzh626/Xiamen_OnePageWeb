const API = {
    async request(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...(options.headers || {})
                },
                ...options
            });

            const res = await response.json();
            if (!response.ok) {
                throw new Error(res.msg || ('网络请求异常，状态码：' + response.status));
            }
            if (res.code !== 0) {
                throw new Error(res.msg || '后端返回错误');
            }
            return res.data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    async getAttractions(params = {}) {
        const query = new URLSearchParams();
        Object.entries(params).forEach(([k, v]) => {
            if (v !== null && v !== undefined && v !== '') {
                if (Array.isArray(v)) {
                    v.forEach((val) => query.append(k, val));
                } else {
                    query.append(k, v);
                }
            }
        });
        const qs = query.toString();
        return this.request('/api/attractions' + (qs ? '?' + qs : ''));
    },

    async getAttractionDetail(id) {
        return this.request('/api/attractions/' + id);
    },

    async getWeather() {
        return this.request('/api/weather/xiamen');
    },

    async recommendRoute(preferences, duration) {
        const query = new URLSearchParams();
        (preferences || []).forEach((p) => query.append('preferences', p));
        query.append('duration', duration || 'half_day');
        return this.request('/api/routes/recommend?' + query.toString());
    },

    async saveCustomRoute(payload) {
        return this.request('/api/routes/custom', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async getSavedRoutes(page, pageSize) {
        return this.request('/api/routes?page=' + (page || 1) + '&page_size=' + (pageSize || 10));
    },

    async submitFavorite(payload) {
        return this.request('/api/favorites', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async submitComment(payload) {
        return this.request('/api/comments', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }
};
