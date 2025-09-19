import {defineConfig} from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': path.resolve(new URL('.', import.meta.url).pathname, 'src') // 替代 __dirname
        }
    },
    server: {
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
                // rewrite: path => path.replace(/^\/api/, '') // 仅在后端无 /api 前缀时使用
            }
        }
    }
});
