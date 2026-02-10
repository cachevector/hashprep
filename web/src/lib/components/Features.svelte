<script lang="ts">
  const features = [
    {
      title: 'Intelligent Profiling',
      description: 'Detect missing values, skewed distributions, outliers, and data type inconsistencies across your entire dataset.',
      icon: 'scan'
    },
    {
      title: 'ML-Specific Checks',
      description: 'Identify data leakage, dataset drift, class imbalance, and high-cardinality features before training.',
      icon: 'shield'
    },
    {
      title: 'Automated Preparation',
      description: 'Get context-aware suggestions for encoding, imputation, scaling, and transformations — with auto-apply options.',
      icon: 'wand'
    },
    {
      title: 'Rich Reporting',
      description: 'Generate statistical summaries and exportable reports in HTML, PDF, Markdown, or JSON with embedded visualizations.',
      icon: 'report'
    },
    {
      title: 'Production Pipelines',
      description: 'Output reproducible cleaning code and sklearn pipelines that integrate seamlessly into ML workflows.',
      icon: 'code'
    },
    {
      title: 'CLI & Library',
      description: 'Use as a command-line tool for quick scans or as a Python library for deep integration into your codebase.',
      icon: 'terminal'
    }
  ];
</script>

<section id="features" class="features">
  <div class="container">
    <div class="section-header">
      <h2>Profile, debug, and fix<br />your datasets in seconds</h2>
      <p class="section-subtitle">
        HashPrep catches critical issues before they derail your ML pipeline,
        explains the problems, and suggests context-aware fixes.
      </p>
    </div>

    <div class="features-grid">
      {#each features as feature}
        <div class="feature-card">
          <div class="feature-icon">
            {#if feature.icon === 'scan'}
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
              </svg>
            {:else if feature.icon === 'shield'}
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            {:else if feature.icon === 'wand'}
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="m15 4-1 1 4 4 1-1a2.83 2.83 0 0 0-4-4z"/><path d="m13 6-8.5 8.5a2.12 2.12 0 1 0 3 3L16 9"/><path d="m8 16 1.5-1.5"/>
              </svg>
            {:else if feature.icon === 'report'}
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>
              </svg>
            {:else if feature.icon === 'code'}
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>
              </svg>
            {:else if feature.icon === 'terminal'}
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>
              </svg>
            {/if}
          </div>
          <h3 class="feature-title">{feature.title}</h3>
          <p class="feature-description">{feature.description}</p>
        </div>
      {/each}
    </div>
  </div>
</section>

<style>
  .features {
    padding: 120px 0;
  }

  .section-header {
    text-align: center;
    margin-bottom: 80px;
  }

  .section-subtitle {
    max-width: 480px;
    margin: 16px auto 0;
    font-size: 1.05rem;
    padding: 0 16px;
  }

  .features-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 32px;
  }

  .feature-card {
    padding: 28px;
    border: 1px solid var(--border-secondary);
    border-radius: var(--radius-md);
    transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  }

  .feature-card:hover {
    border-color: var(--border-accent);
    box-shadow: var(--shadow-sm);
  }

  .feature-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: var(--radius-sm);
    background: var(--accent-light);
    color: var(--accent);
    margin-bottom: 16px;
  }

  .feature-title {
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 8px;
  }

  .feature-description {
    font-size: 0.875rem;
    line-height: 1.65;
    color: var(--text-secondary);
  }

  @media (max-width: 1024px) {
    .features-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (max-width: 640px) {
    .features {
      padding: 64px 0;
    }

    .features-grid {
      grid-template-columns: 1fr;
      gap: 16px;
    }

    .section-header {
      margin-bottom: 40px;
    }
  }
</style>
