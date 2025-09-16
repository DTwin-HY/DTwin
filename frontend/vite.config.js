import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import autoprefixer from "autoprefixer";
// https://vite.dev/config/
//export default defineConfig({
//  plugins: [react(), tailwindcss()],
//})
//import { defineConfig, loadEnv } from "vite";
//import react from "@vitejs/plugin-react";
//import tailwindcss from "tailwindcss";

// https://vite.dev/config/

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd());
  return {
    define: {
      "process.env": env,
    },
    plugins: [react(),tailwindcss()],
    server: {
      proxy: {
        "/api/": process.env.VITE_BACKEND_URL,
      },
    },
    css: {
      postcss: {
        plugins: [tailwindcss, autoprefixer],
      },
    },
  };
});