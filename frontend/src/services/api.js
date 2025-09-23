import axios from 'axios';

const base = (import.meta.env.VITE_API_BASE || '/api').replace(/\/+$/, '/'); // 规范化末尾斜杠
const api = axios.create({
    baseURL: base,
    timeout: 10000
});

// 需要的拦截器/导出自行保留
export default api;