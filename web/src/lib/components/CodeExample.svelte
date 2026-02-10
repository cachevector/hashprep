<script lang="ts">
  let activeTab = $state<'cli' | 'python'>('cli');
</script>

<section class="code-section">
  <div class="container">
    <div class="code-layout">
      <div class="code-info">
        <h2>Use it your way</h2>
        <p class="code-subtitle">
          Quick terminal scan or deep Python integration — HashPrep fits into any ML workflow.
        </p>

        <div class="check-list">
          <div class="check-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <span>13 built-in dataset checks</span>
          </div>
          <div class="check-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <span>HTML, PDF, Markdown, JSON reports</span>
          </div>
          <div class="check-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <span>Auto-generated fix scripts</span>
          </div>
          <div class="check-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <span>Drift detection between datasets</span>
          </div>
        </div>
      </div>

      <div class="code-panel">
        <div class="code-tabs">
          <button
            class="code-tab"
            class:active={activeTab === 'cli'}
            onclick={() => activeTab = 'cli'}
          >
            CLI
          </button>
          <button
            class="code-tab"
            class:active={activeTab === 'python'}
            onclick={() => activeTab = 'python'}
          >
            Python
          </button>
        </div>

        <div class="code-body">
          {#if activeTab === 'cli'}
            <pre><code><span class="c-comment"># Quick scan for critical issues</span>
<span class="c-prompt">$</span> hashprep scan train.csv --target Survived

<span class="c-comment"># Detailed analysis of all issues</span>
<span class="c-prompt">$</span> hashprep details train.csv --target Survived

<span class="c-comment"># Generate HTML report with fix scripts</span>
<span class="c-prompt">$</span> hashprep report train.csv \
    --format html \
    --theme minimal \
    --with-code

<span class="c-comment"># Compare datasets for drift</span>
<span class="c-prompt">$</span> hashprep report train.csv \
    --comparison test.csv \
    --format html</code></pre>
          {:else}
            <pre><code><span class="c-keyword">import</span> pandas <span class="c-keyword">as</span> pd
<span class="c-keyword">from</span> hashprep <span class="c-keyword">import</span> DatasetAnalyzer
<span class="c-keyword">from</span> hashprep.reports <span class="c-keyword">import</span> generate_report

<span class="c-comment"># Load and analyze</span>
df = pd.read_csv(<span class="c-string">"train.csv"</span>)
analyzer = DatasetAnalyzer(
    df,
    target_col=<span class="c-string">"Survived"</span>,
    include_plots=<span class="c-keyword">True</span>
)
summary = analyzer.analyze()

<span class="c-comment"># Check results</span>
<span class="c-builtin">print</span>(<span class="c-string">f"Critical: {'{'}</span>summary[<span class="c-string">'critical_count'</span>]<span class="c-string">{'}'}"</span>)

<span class="c-comment"># Generate report</span>
generate_report(
    summary,
    format=<span class="c-string">"html"</span>,
    theme=<span class="c-string">"minimal"</span>,
    output_file=<span class="c-string">"report.html"</span>
)</code></pre>
          {/if}
        </div>
      </div>
    </div>
  </div>
</section>

<style>
  .code-section {
    padding: 120px 0;
  }

  .code-layout {
    display: grid;
    grid-template-columns: 1fr 1.2fr;
    gap: 64px;
    align-items: center;
  }

  .code-info h2 {
    margin-bottom: 14px;
  }

  .code-subtitle {
    font-size: 1.05rem;
    color: var(--text-secondary);
    margin-bottom: 32px;
    line-height: 1.7;
  }

  .check-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .check-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.9rem;
    color: var(--text-secondary);
  }

  .code-panel {
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-md);
    overflow: hidden;
    box-shadow: var(--shadow-md);
  }

  .code-tabs {
    display: flex;
    border-bottom: 1px solid var(--border-primary);
    background: var(--bg-tertiary);
  }

  .code-tab {
    padding: 10px 20px;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-tertiary);
    border-bottom: 2px solid transparent;
    transition: all var(--transition-fast);
  }

  .code-tab:hover {
    color: var(--text-secondary);
  }

  .code-tab.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
  }

  .code-body {
    padding: 24px;
    background: var(--code-bg);
    overflow-x: auto;
  }

  .code-body pre {
    margin: 0;
    font-size: 0.8rem;
    line-height: 1.7;
  }

  .code-body code {
    color: var(--text-secondary);
  }

  .c-comment { color: var(--text-tertiary); }
  .c-prompt { color: var(--text-tertiary); user-select: none; }
  .c-keyword { color: var(--accent); }
  .c-string { color: #98971a; }
  .c-builtin { color: var(--text-primary); }

  :global([data-theme="dark"]) .c-string {
    color: #b8bb26;
  }

  @media (max-width: 1024px) {
    .code-layout {
      grid-template-columns: 1fr;
      gap: 32px;
    }

    .code-info {
      text-align: center;
    }

    .check-list {
      align-items: center;
    }
  }

  @media (max-width: 640px) {
    .code-section {
      padding: 64px 0;
    }

    .code-body {
      padding: 16px;
    }

    .code-body pre {
      font-size: 0.68rem;
    }

    .code-info {
      text-align: left;
    }

    .check-list {
      align-items: flex-start;
    }
  }
</style>
