import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import WindiCSS from "vite-plugin-windicss";
import AutoImport from "unplugin-auto-import/vite";
import Components from "unplugin-vue-components/vite";
import { ElementPlusResolver } from "unplugin-vue-components/resolvers";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    WindiCSS(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  build: {
    chunkSizeWarningLimit: 2000, // 设置更高的值
  },
  server: {
    host: "0.0.0.0",
    // port: 8080,
    proxy: {
      "/auth-api": {
        // target: "http://10.159.1.46:8000",
        target: "http://127.0.0.1:8053",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/auth-api/, ""),
      },
      "/sympton-api": {
        // target: "http://10.159.1.46:8000",
        target: "http://127.0.0.1:8050",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/sympton-api/, ""),
      },
      "/model-api": {
        // target: "http://10.159.1.46:8000",
        target: "http://127.0.0.1:8054",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/model-api/, ""),
      },
      "/minio-api": {
        // target: "http://10.159.1.46:8000",
        target: "http://127.0.0.1:9000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/minio-api/, ""),
      },
      "/csust-api": {
        // target: "http://10.159.1.46:8000",
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/csust-api/, ""),
      },
    },
  },
});
