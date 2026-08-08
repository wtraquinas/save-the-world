import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  root: '.',          // explicit — current dir is frontend/
  build: {
    outDir: 'dist',
  },
})