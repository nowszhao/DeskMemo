import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
// 提取服务器基础 URL（去掉 /api）
const SERVER_BASE_URL = API_BASE_URL.replace('/api', '');

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// 请求拦截器：添加认证 token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理 401 错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 只在非登录和认证检查接口时才跳转
      const url = error.config?.url || '';
      if (!url.includes('/auth/login') && !url.includes('/auth/check')) {
        // 清除 token
        localStorage.removeItem('auth_token');
        // 触发重新登录
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// 导出辅助函数：构建图片 URL
export const getImageUrl = (path) => {
  return `${SERVER_BASE_URL}${path}`;
};

export const authAPI = {
  checkAuth: () => api.get('/auth/check'),
  login: (password) => api.post('/auth/login', { password }),
  logout: () => api.post('/auth/logout'),
};

export const statsAPI = {
  getTodayStats: () => api.get('/stats/today'),
};

export const screenshotsAPI = {
  getScreenshots: (params) => api.get('/screenshots', { params }),
};

export const activitiesAPI = {
  getActivities: (params) => api.get('/activities', { params }),
};

export const reportsAPI = {
  getHourlyReports: (date) => api.get('/reports/hourly', { params: { date } }),
  getDailyReports: (limit) => api.get('/reports/daily', { params: { limit } }),
};

export const searchAPI = {
  search: (query, limit) => api.get('/search', { params: { q: query, limit } }),
};

export default api;
