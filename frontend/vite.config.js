import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // 如果部署到 GitHub Pages 子路径，把 base 改为仓库名
  // 例如：base: '/ai-paper-tracker/'
  base: './',
})
