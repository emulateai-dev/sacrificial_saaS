import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    allowedHosts: process.env.BASE_DOMAIN ? [process.env.BASE_DOMAIN, 'localhost', '127.0.0.1'] : ['localhost', '127.0.0.1', 'copen-labs.letscookmeth.fun'],
  },
})
