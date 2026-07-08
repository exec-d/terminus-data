import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

// En dev, base vide ; en build (prod Pages), sous /terminus-32.
const dev = process.argv.includes('dev');

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: null,
      precompress: false,
      strict: true
    }),
    paths: { base: dev ? '' : '/terminus-32', relative: false },
    prerender: {
      // Le Hero lie "#pourquoi" (ancre vers la section "Pourquoi", ajoutée par
      // un composant ultérieur du portage) : ne pas casser le build tant que
      // la cible n'existe pas encore sur la page.
      handleMissingId: 'warn'
    }
  }
};

export default config;
