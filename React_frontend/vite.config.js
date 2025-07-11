// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

export default defineConfig({
  base: './', // 👈 This is the key line to fix the white screen!
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    strictPort: true,
    cors: true,
    allowedHosts: ['localhost', '127.0.0.1'],
  },
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
  assetsInclude: ['**/*.svg'],
});
