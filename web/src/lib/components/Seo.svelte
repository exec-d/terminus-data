<script lang="ts">
  interface Props {
    title: string;
    description: string;
    path?: string;
  }
  let { title, description, path = '/' }: Props = $props();

  const SITE = 'https://exec-d.github.io/terminus-32';
  const url = $derived(`${SITE}${path}`);
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
