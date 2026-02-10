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
    document.body.style.overflow = '';
  }

  function toggleMobile() {
    mobileOpen = !mobileOpen;
    document.body.style.overflow = mobileOpen ? 'hidden' : '';
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
        onclick={toggleMobile}
        aria-label="Toggle menu"
        aria-expanded={mobileOpen}
        type="button"
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
</nav>

{#if mobileOpen}
  <div class="mobile-menu">
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
    width: 100%;
    max-width: 100vw;
    overflow: visible;
  }

  .navbar-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 100%;
    width: 100%;
    max-width: 100%;
    overflow: hidden;
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
    flex-shrink: 0;
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
    min-width: 36px;
    color: var(--text-secondary);
    border-radius: var(--radius-sm);
    flex-shrink: 0;
    cursor: pointer;
  }

  .mobile-toggle:hover {
    background: var(--bg-tertiary);
  }

  .mobile-menu {
    position: fixed !important;
    top: var(--nav-height) !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    background: var(--bg-primary) !important;
    z-index: 999 !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    width: 100vw !important;
    max-width: 100vw !important;
    -webkit-overflow-scrolling: touch;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  /* Hide on desktop */
  @media (min-width: 769px) {
    .mobile-menu {
      display: none !important;
    }
  }

  .mobile-menu-inner {
    display: flex !important;
    flex-direction: column !important;
    padding: 16px !important;
    gap: 4px !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    min-height: 200px !important;
  }

  .mobile-link {
    padding: 12px 16px;
    font-size: 1rem;
    font-weight: 400;
    color: var(--text-secondary);
    border-radius: var(--radius-sm);
    transition: background var(--transition-fast);
    display: block;
    text-decoration: none;
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
    .navbar-inner {
      padding: 0 12px;
    }

    .desktop-only {
      display: none !important;
    }

    .mobile-only {
      display: flex;
    }

    .mobile-menu {
      display: block !important;
    }

    .nav-actions {
      gap: 4px;
    }
  }
</style>
