import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  root: '.', // Set root to current directory
  build: {
    rollupOptions: {
      input: './index.html' // Point to your index.html
    }
  }
})