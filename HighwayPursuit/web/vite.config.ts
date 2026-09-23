import { defineConfig } from "vite";

// base relativo para GitHub Pages (funciona em raiz ou subpasta)
export default defineConfig({
  base: "./",
  server: {
    host: true,
    port: 5173,
  },
});
