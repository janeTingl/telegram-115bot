import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,                                   // ← 改这里！不能是 8000
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',             // ← 改这里！后端真实端口
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, '/api') // 可选保险
      },
      '/uploads': 'http://127.0.0.1:8000'         // 上传文件也代理
    }
  },
  build: {
    outDir: '../backend/dist',    // ← 这个你已经对了，保留！
    emptyOutDir: true,
  }
});