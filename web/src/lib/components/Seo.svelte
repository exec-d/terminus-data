<script lang="ts">
  import { page } from '$app/state';

  interface Props {
    title: string;
    description: string;
    path?: string; // override optionnel ; par défaut dérivé de la route courante
  }
  let { title, description, path }: Props = $props();

  // page.url.pathname reflète l'URL réellement servie (base incluse en prod),
  // donc on ne préfixe pas nous-mêmes le base path pour éviter un doublon.
  const ORIGIN = 'https://exec-d.github.io';
  const url = $derived(ORIGIN + (path ?? page.url.pathname));
</script>

<svelte:head>
  <title>{title}</title>
  <meta name="description" content={description} />
  <link rel="canonical" href={url} />
  <meta property="og:type" content="website" />
  <meta property="og:title" content={title} />
  <meta property="og:description" content={description} />
  <meta property="og:url" content={url} />
  <meta name="twitter:card" content="summary_large_image" />
</svelte:head>
