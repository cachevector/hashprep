<script lang="ts">
  const integrations = [
    { name: 'Python', icon: 'python' },
    { name: 'pandas', icon: 'pandas' },
    { name: 'scikit-learn', icon: 'sklearn' },
    { name: 'NumPy', icon: 'numpy' },
  ];
</script>

<section class="integrations">
  <div class="container">
    <p class="integrations-label">Works with your ML stack</p>
    <div class="integrations-grid">
      {#each integrations as item}
        <div class="integration-item">
          {#if item.icon === 'python'}
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M11.914 0C5.82 0 6.2 2.656 6.2 2.656l.007 2.752h5.814v.826H3.9S0 5.789 0 11.969c0 6.18 3.403 5.961 3.403 5.961h2.03v-2.867s-.109-3.42 3.35-3.42h5.766s3.24.053 3.24-3.148V3.202S18.28 0 11.914 0zM8.708 1.85a1.06 1.06 0 110 2.12 1.06 1.06 0 010-2.12z" fill="var(--text-tertiary)"/>
              <path d="M12.086 24c6.094 0 5.714-2.656 5.714-2.656l-.007-2.752H11.98v-.826h8.121S24 18.211 24 12.031c0-6.18-3.403-5.961-3.403-5.961h-2.03v2.867s.109 3.42-3.35 3.42H9.451s-3.24-.053-3.24 3.148v5.293S5.72 24 12.086 24zm3.206-1.85a1.06 1.06 0 110-2.12 1.06 1.06 0 010 2.12z" fill="var(--text-tertiary)"/>
            </svg>
          {:else if item.icon === 'pandas'}
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="1" width="4" height="8" rx="0.5" fill="var(--text-tertiary)"/>
              <rect x="3" y="11" width="4" height="4" rx="0.5" fill="var(--text-tertiary)"/>
              <rect x="3" y="17" width="4" height="6" rx="0.5" fill="var(--text-tertiary)"/>
              <rect x="10" y="6" width="4" height="3" rx="0.5" fill="var(--text-tertiary)"/>
              <rect x="17" y="1" width="4" height="6" rx="0.5" fill="var(--text-tertiary)"/>
              <rect x="17" y="9" width="4" height="4" rx="0.5" fill="var(--text-tertiary)"/>
              <rect x="17" y="15" width="4" height="8" rx="0.5" fill="var(--text-tertiary)"/>
            </svg>
          {:else if item.icon === 'sklearn'}
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="var(--text-tertiary)" stroke-width="1.5" fill="none"/>
              <circle cx="8" cy="9" r="2" fill="var(--text-tertiary)"/>
              <circle cx="15" cy="8" r="1.5" fill="var(--text-tertiary)"/>
              <circle cx="10" cy="15" r="2.5" fill="var(--text-tertiary)"/>
              <circle cx="16" cy="14" r="1.8" fill="var(--text-tertiary)"/>
            </svg>
          {:else if item.icon === 'numpy'}
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L2 7v10l10 5 10-5V7L12 2z" stroke="var(--text-tertiary)" stroke-width="1.5" fill="none"/>
              <path d="M2 7l10 5 10-5" stroke="var(--text-tertiary)" stroke-width="1.5"/>
              <path d="M12 22V12" stroke="var(--text-tertiary)" stroke-width="1.5"/>
            </svg>
          {/if}
          <span class="integration-name">{item.name}</span>
        </div>
      {/each}
    </div>
  </div>
</section>

<style>
  .integrations {
    padding: 40px 0;
    border-top: 1px solid var(--border-secondary);
    border-bottom: 1px solid var(--border-secondary);
  }

  .integrations-label {
    text-align: center;
    font-family: var(--font-mono);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-tertiary);
    margin-bottom: 24px;
    font-weight: 400;
  }

  .integrations-grid {
    display: flex;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
  }

  .integration-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border: 1px solid var(--border-secondary);
    border-radius: var(--radius-sm);
    transition: border-color var(--transition-fast);
  }

  .integration-item:hover {
    border-color: var(--border-primary);
  }

  .integration-name {
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--text-tertiary);
    white-space: nowrap;
  }

  @media (max-width: 640px) {
    .integrations {
      padding: 32px 0;
    }

    .integrations-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }

    .integration-item {
      justify-content: center;
      padding: 10px 12px;
    }
  }

  @media (max-width: 360px) {
    .integrations-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
