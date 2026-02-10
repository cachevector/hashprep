<script lang="ts">
</script>

<section class="cta-section">
  <div class="container">
    <div class="cta-card">
      <div class="cta-content">
        <h2>Stop debugging datasets manually.</h2>
        <p class="cta-subtitle">
          Install HashPrep and get your first dataset audit in under a minute.
        </p>
        <div class="cta-install">
          <code>pip install hashprep</code>
        </div>
        <div class="cta-actions">
          <a href="/docs#installation" class="cta-btn cta-btn-primary">
            Get Started
          </a>
          <a href="https://github.com/cachevector/hashprep" class="cta-btn cta-btn-secondary">
            View on GitHub
          </a>
        </div>
      </div>
    </div>
  </div>
</section>

<style>
  .cta-section {
    padding: 120px 0;
    background: var(--section-alt-bg);
  }

  .cta-card {
    text-align: center;
    padding: 64px 32px;
    border: 1px solid var(--border-secondary);
    border-radius: var(--radius-lg);
    background: var(--bg-primary);
  }

  .cta-content {
    max-width: 480px;
    margin: 0 auto;
  }

  .cta-content h2 {
    margin-bottom: 14px;
  }

  .cta-subtitle {
    font-size: 1.05rem;
    color: var(--text-secondary);
    margin-bottom: 28px;
    line-height: 1.7;
  }

  .cta-install {
    display: inline-flex;
    padding: 10px 24px;
    background: var(--code-bg);
    border: 1px solid var(--code-border);
    border-radius: var(--radius-sm);
    margin-bottom: 28px;
  }

  .cta-install code {
    font-size: 0.8rem;
    color: var(--code-text);
    font-weight: 400;
  }

  .cta-actions {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .cta-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 24px;
    font-size: 0.925rem;
    font-weight: 500;
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
  }

  .cta-btn-primary {
    background: var(--accent);
    color: var(--text-inverse);
  }

  .cta-btn-primary:hover {
    background: var(--accent-hover);
  }

  .cta-btn-secondary {
    color: var(--text-secondary);
    border: 1px solid var(--border-primary);
  }

  .cta-btn-secondary:hover {
    color: var(--text-primary);
    border-color: var(--text-tertiary);
    background: var(--bg-tertiary);
  }

  @media (max-width: 640px) {
    .cta-section {
      padding: 64px 0;
    }

    .cta-card {
      padding: 40px 20px;
    }

    .cta-actions {
      flex-direction: column;
      align-items: center;
    }

    .cta-btn {
      width: 100%;
      max-width: 240px;
      justify-content: center;
    }
  }
</style>
