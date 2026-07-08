<script lang="ts">
  import Seo from '$lib/components/Seo.svelte';
</script>

<Seo
  title="TERMinus — ligne 32 TER Bourg-en-Bresse ⇄ Lyon"
  description="Application non officielle de suivi de la ligne 32 TER : ponctualité, horaires et données ouvertes."
/>

<section class="hero">
  <h1><span class="w-ter">TER</span><span class="w-minus">Minus</span></h1>
  <p class="muted">Le suivi honnête de la ligne 32 — Bourg-en-Bresse ⇄ Lyon.</p>
</section>

<style>
  .hero {
    padding-block: var(--space-6) var(--space-5);
  }
  h1 {
    font-family: var(--font-mono);
    font-size: clamp(2.5rem, 8vw, 4rem);
    margin: 0;
  }
  .w-ter {
    color: var(--accent);
  }
  .w-minus {
    color: var(--fg);
  }
</style>
