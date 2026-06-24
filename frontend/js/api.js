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

    async getAttractions() {
        return this.request('/api/attractions');
    },

    async getWeather() {
        return this.request('/api/weather/xiamen');
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
