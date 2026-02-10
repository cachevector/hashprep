<script lang="ts">
  let { size = 32, showText = true }: { size?: number; showText?: boolean } = $props();
</script>

<a href="/" class="logo" aria-label="HashPrep home">
  <img
    src="https://raw.githubusercontent.com/cachevector/hashprep/refs/heads/main/docs/assets/hashprep-wobg.svg"
    alt="HashPrep logo"
    width={size}
    height={size}
    loading="lazy"
  />
  {#if showText}
    <span class="logo-text">HashPrep</span>
  {/if}
</a>

<style>
  .logo {
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
  }

  .logo-text {
    font-family: var(--font-mono);
    font-size: 1rem;
    font-weight: 500;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    text-transform: uppercase;
  }
</style>
