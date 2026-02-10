<script lang="ts">
  import '../app.css';
  import { theme } from '$lib/theme.svelte';
  import { onMount } from 'svelte';
  import type { Snippet } from 'svelte';

  let { children }: { children: Snippet } = $props();

  onMount(() => {
    theme.init();
  });
</script>

<svelte:head>
  <title>HashPrep — Dataset Profiler & Debugger for Machine Learning</title>
</svelte:head>

{@render children()}
