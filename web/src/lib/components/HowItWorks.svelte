<script lang="ts">
  const steps = [
    {
      step: '01',
      title: 'Scan',
      command: 'hashprep scan dataset.csv',
      description: 'Run a quick scan to get a summary of critical issues in your terminal. Add --target to enable ML-specific checks.',
    },
    {
      step: '02',
      title: 'Analyze',
      command: 'hashprep details dataset.csv --target Survived',
      description: 'Get comprehensive details about all detected issues including outliers, missing values, class imbalance, and data leakage.',
    },
    {
      step: '03',
      title: 'Report & Fix',
      command: 'hashprep report dataset.csv --format html --with-code',
      description: 'Generate rich HTML/PDF reports with visualizations and auto-generated Python fix scripts and sklearn pipelines.',
    },
  ];
</script>

<section id="how-it-works" class="how-it-works">
  <div class="container">
    <div class="section-header">
      <h2>Three commands.<br />Zero guesswork.</h2>
      <p class="section-subtitle">
        No need to change your workflow — bring your own tools,
        frameworks, and datasets.
      </p>
    </div>

    <div class="steps-grid">
      {#each steps as step}
        <div class="step-card">
          <div class="step-top">
            <div class="step-number">{step.step}</div>
            <h3 class="step-title">{step.title}</h3>
            <div class="step-command">
              <code>{step.command}</code>
            </div>
          </div>
          <p class="step-description">{step.description}</p>
        </div>
      {/each}
    </div>
  </div>
</section>

<style>
  .how-it-works {
    padding: 120px 0;
    background: var(--section-alt-bg);
  }

  .section-header {
    text-align: center;
    margin-bottom: 80px;
  }

  .section-subtitle {
    max-width: 440px;
    margin: 16px auto 0;
    font-size: 1.05rem;
  }

  .steps-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 32px;
  }

  .step-card {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 28px;
    background: var(--bg-primary);
    border: 1px solid var(--border-secondary);
    border-radius: var(--radius-md);
    transition: border-color var(--transition-fast);
  }

  .step-card:hover {
    border-color: var(--border-accent);
  }

  .step-top {
    margin-bottom: 14px;
  }

  .step-number {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--accent);
    letter-spacing: 0.05em;
    margin-bottom: 12px;
  }

  .step-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 12px;
  }

  .step-command {
    padding: 8px 12px;
    background: var(--code-bg);
    border: 1px solid var(--code-border);
    border-radius: var(--radius-sm);
    overflow-x: auto;
  }

  .step-command code {
    font-size: 0.78rem;
    color: var(--code-text);
    white-space: nowrap;
  }

  .step-description {
    font-size: 0.875rem;
    line-height: 1.65;
    color: var(--text-secondary);
  }

  @media (max-width: 1024px) {
    .steps-grid {
      grid-template-columns: 1fr;
      gap: 16px;
      max-width: 520px;
      margin: 0 auto;
    }
  }

  @media (max-width: 640px) {
    .how-it-works {
      padding: 64px 0;
    }

    .section-header {
      margin-bottom: 40px;
    }

    .step-card {
      padding: 22px;
    }
  }
</style>
