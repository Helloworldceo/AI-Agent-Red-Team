import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  // GitHub Pages serves a project repo from /<repo-name>/, not the domain root.
  base: process.env.GITHUB_PAGES ? '/AI-Agent-Red-Team/' : '/',
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
  },
})
