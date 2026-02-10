<script lang="ts">
  import Navbar from '$lib/components/Navbar.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import Integrations from '$lib/components/Integrations.svelte';
  import Features from '$lib/components/Features.svelte';
  import HowItWorks from '$lib/components/HowItWorks.svelte';
  import CodeExample from '$lib/components/CodeExample.svelte';
  import Checks from '$lib/components/Checks.svelte';
  import Themes from '$lib/components/Themes.svelte';
  import CTA from '$lib/components/CTA.svelte';
  import Footer from '$lib/components/Footer.svelte';
</script>

<Navbar />
<main>
  <Hero />
  <Integrations />
  <Features />
  <HowItWorks />
  <CodeExample />
  <Checks />
  <Themes />
  <CTA />
</main>
<Footer />
