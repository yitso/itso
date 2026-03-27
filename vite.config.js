import { defineConfig } from 'vite'
import { resolve } from 'path'
import { viteStaticCopy } from 'vite-plugin-static-copy'

const viteBase = process.env.VITE_BASE || '/static/itso/dist/'
const normalizedViteBase = viteBase.endsWith('/') ? viteBase : `${viteBase}/`

export default defineConfig({
  root: '.',
  publicDir: false,
  base: normalizedViteBase,
  optimizeDeps: {
    include: ['mermaid']
  },
  build: {
    outDir: 'static/itso/dist',
    emptyOutDir: false,
    sourcemap: false,
    manifest: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'frontend/main.js')
      },
      output: {
        manualChunks: {
          mermaid: ['mermaid']
        }
      }
    }
  },
  plugins: [
    viteStaticCopy({
      targets: [
        // jQuery
        { src: 'node_modules/jquery/dist/jquery.min.js', dest: 'lib/jquery' },
        // Bootstrap
        { src: 'node_modules/bootstrap/dist/js/bootstrap.min.js', dest: 'lib/bootstrap' },
        { src: 'node_modules/bootstrap/dist/css/bootstrap.min.css', dest: 'lib/bootstrap' },
        // MathJax
        { src: 'node_modules/mathjax/MathJax.js', dest: 'lib/mathjax' },
        { src: 'node_modules/mathjax/config/**', dest: 'lib/mathjax/config' },
        { src: 'node_modules/mathjax/jax/**', dest: 'lib/mathjax/jax' },
        { src: 'node_modules/mathjax/extensions/**', dest: 'lib/mathjax/extensions' },
        { src: 'node_modules/mathjax/fonts/**', dest: 'lib/mathjax/fonts' },
      ]
    })
  ]
})