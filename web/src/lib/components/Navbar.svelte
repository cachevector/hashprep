<script lang="ts">
  import Logo from './Logo.svelte';
  import ThemeToggle from './ThemeToggle.svelte';

  let mobileOpen = $state(false);

  const navLinks = [
    { label: 'Features', href: '/#features' },
    { label: 'How It Works', href: '/#how-it-works' },
    { label: 'Docs', href: '/docs' },
    { label: 'GitHub', href: 'https://github.com/cachevector/hashprep' }
  ];

  function closeMobile() {
    mobileOpen = false;
  }
</script>

<nav class="navbar">
  <div class="navbar-inner container">
    <Logo size={20} />

    <div class="nav-links desktop-only">
      {#each navLinks as link}
        <a href={link.href} class="nav-link">{link.label}</a>
      {/each}
    </div>

    <div class="nav-actions">
      <ThemeToggle />
    <a href="/docs#installation" class="btn btn-primary desktop-only">
        Get Started
      </a>

      <button
        class="mobile-toggle mobile-only"
        onclick={() => mobileOpen = !mobileOpen}
        aria-label="Toggle menu"
        aria-expanded={mobileOpen}
      >
        {#if mobileOpen}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        {:else}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
            <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        {/if}
      </button>
    </div>
  </div>

  {#if mobileOpen}
    <div class="mobile-menu mobile-only">
      <div class="mobile-menu-inner">
        {#each navLinks as link}
          <a href={link.href} class="mobile-link" onclick={closeMobile}>{link.label}</a>
        {/each}
        <hr />
        <a href="/docs#installation" class="btn btn-primary mobile-cta">
          Get Started
        </a>
      </div>
    </div>
  {/if}
</nav>

<style>
  .navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
    background: var(--nav-bg);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--nav-border);
    height: var(--nav-height);
  }

  .navbar-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 100%;
  }

  .nav-links {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .nav-link {
    padding: 6px 14px;
    font-size: 0.85rem;
    font-weight: 400;
    color: var(--text-secondary);
    border-radius: var(--radius-sm);
    transition: color var(--transition-fast), background-color var(--transition-fast);
  }

  .nav-link:hover {
    color: var(--text-primary);
    background: var(--bg-tertiary);
  }

  .nav-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 16px;
    font-size: 0.85rem;
    font-weight: 500;
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
    white-space: nowrap;
  }

  .btn-primary {
    background: var(--accent);
    color: var(--text-inverse);
  }

  .btn-primary:hover {
    background: var(--accent-hover);
  }

  .mobile-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    color: var(--text-secondary);
    border-radius: var(--radius-sm);
  }

  .mobile-toggle:hover {
    background: var(--bg-tertiary);
  }

  .mobile-menu {
    position: fixed;
    top: var(--nav-height);
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--bg-primary);
    z-index: 99;
    overflow-y: auto;
  }

  .mobile-menu-inner {
    display: flex;
    flex-direction: column;
    padding: 16px;
    gap: 4px;
  }

  .mobile-link {
    padding: 12px 16px;
    font-size: 1rem;
    font-weight: 400;
    color: var(--text-secondary);
    border-radius: var(--radius-sm);
    transition: background var(--transition-fast);
  }

  .mobile-link:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }

  .mobile-menu hr {
    border: none;
    border-top: 1px solid var(--border-secondary);
    margin: 8px 0;
  }

  .mobile-cta {
    margin-top: 8px;
    justify-content: center;
    padding: 12px;
  }

  .desktop-only {
    display: flex;
  }

  .mobile-only {
    display: none;
  }

  @media (max-width: 768px) {
    .desktop-only {
      display: none !important;
    }

    .mobile-only {
      display: flex;
    }
  }
</style>
