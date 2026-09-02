import {defineConfig} from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, 'src')
        }
    },
    server: {
        host: true,
        port: 5173,
        proxy: {
            // 后端 API
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            // 关键修复: 代理 Channels WebSocket
            '/ws': {
                target: 'ws://127.0.0.1:8000',
                ws: true,
                changeOrigin: true
            }
        }
    }
});