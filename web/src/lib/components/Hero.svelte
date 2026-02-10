<script lang="ts">
</script>

<section class="hero">
  <div class="container hero-inner">
    <div class="hero-badge">
      <span class="badge">Beta v0.1.0</span>
    </div>

    <h1 class="hero-title">
      Dataset Profiler &amp; Debugger<br class="hero-br" />for Machine Learning.
    </h1>

    <p class="hero-subtitle">
      Catch critical dataset issues before they derail your ML pipeline.
      Profile, debug, and fix — all in one command.
    </p>

    <div class="hero-actions">
      <a href="/docs#installation" class="btn-hero btn-hero-primary">
        <svg width="12" height="20" viewBox="0 0 47.581429 77.315781" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <g transform="translate(351.30686,-158.54937)">
            <g transform="matrix(2.4307449,0,0,2.4307449,-363.74873,-127.07147)" style="fill:currentColor">
              <path d="m 12.3073,127.88684 v 11.22412 4.57854 a 5.6360459,5.6360459 0 0 0 5.251876,5.62136 V 138.08674 133.5082 A 5.6360459,5.6360459 0 0 0 12.3073,127.88684 Z" />
              <path d="m 5.1185506,117.50342 v 15.94993 a 5.4826112,5.4826112 0 0 0 5.2518754,5.4622 v -10.92491 -10.48722 z" />
              <path d="m 19.441507,128.02077 v 13.09636 a 6.7146358,6.7146358 0 0 0 5.251876,-6.2513 v -0.79324 a 6.7146358,6.7146358 0 0 0 -5.251876,-6.05182 z" />
            </g>
          </g>
        </svg>
        Get Started
      </a>
      <a href="https://github.com/cachevector/hashprep" class="btn-hero btn-hero-secondary">
        View on GitHub
      </a>
    </div>

    <div class="hero-terminal">
      <div class="terminal-chrome">
        <div class="terminal-dots">
          <span class="dot dot-red"></span>
          <span class="dot dot-yellow"></span>
          <span class="dot dot-green"></span>
        </div>
        <span class="terminal-title">terminal</span>
      </div>
      <div class="terminal-body">
        <pre><code><span class="term-prompt">$</span> <span class="term-cmd">pip install hashprep</span>
<span class="term-output">Successfully installed hashprep-0.1.0b1</span>

<span class="term-prompt">$</span> <span class="term-cmd">hashprep scan train.csv --target Survived</span>

<span class="term-output">  HashPrep Dataset Analysis</span>
<span class="term-output">  ────────────────────────────────────</span>
<span class="term-accent">  3 critical</span><span class="term-output"> issues found</span>
<span class="term-warn">  5 warnings</span><span class="term-output"> detected</span>
<span class="term-output">  ────────────────────────────────────</span>
<span class="term-accent">  ✗ high_missing_values</span><span class="term-output">  Cabin: 77.1% missing</span>
<span class="term-accent">  ✗ class_imbalance</span><span class="term-output">      Survived: ratio 1.58</span>
<span class="term-accent">  ✗ outliers</span><span class="term-output">             Fare: 116 outliers</span>
<span class="term-warn">  ⚠ high_cardinality</span><span class="term-output">    Ticket: 681 unique</span>
<span class="term-warn">  ⚠ feature_correlation</span><span class="term-output"> SibSp ↔ Parch: 0.41</span></code></pre>
      </div>
    </div>
  </div>
</section>

<style>
  .hero {
    padding-top: calc(var(--nav-height) + 72px);
    padding-bottom: 96px;
    background: var(--hero-gradient);
    text-align: center;
  }

  .hero-inner {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 40px;
    padding: 0 24px;
  }

  .badge {
    display: inline-block;
    padding: 4px 14px;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--accent);
    background: var(--accent-light);
    border: 1px solid var(--border-accent);
    border-radius: var(--radius-full);
    letter-spacing: 0.02em;
  }

  .hero-title {
    max-width: 640px;
    margin-bottom: 18px;
    padding: 0 8px;
  }

  .hero-subtitle {
    max-width: 520px;
    font-size: clamp(0.95rem, 1.5vw, 1.1rem);
    color: var(--text-secondary);
    margin-bottom: 28px;
    line-height: 1.7;
    padding: 0 12px;
  }

  .hero-actions {
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
    flex-wrap: wrap;
    justify-content: center;
  }

  .btn-hero {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 24px;
    font-size: 0.9rem;
    font-weight: 500;
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
    white-space: nowrap;
  }

  .btn-hero-primary {
    background: var(--accent);
    color: var(--text-inverse);
    box-shadow: var(--shadow-sm);
  }

  .btn-hero-primary:hover {
    background: var(--accent-hover);
    box-shadow: var(--shadow-md);
  }

  .btn-hero-secondary {
    color: var(--text-secondary);
    border: 1px solid var(--border-primary);
    background: var(--bg-primary);
  }

  .btn-hero-secondary:hover {
    color: var(--text-primary);
    border-color: var(--text-tertiary);
    background: var(--bg-tertiary);
  }

  /* Terminal */
  .hero-terminal {
    width: 100%;
    max-width: 640px;
    border-radius: 22px;
    overflow: hidden;
    border: 1px solid var(--border-primary);
    box-shadow: var(--shadow-lg);
    text-align: left;
  }

  .terminal-chrome {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    background: var(--bg-tertiary);
    border-bottom: 1px solid var(--border-primary);
  }

  .terminal-dots {
    display: flex;
    gap: 6px;
  }

  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }

  .dot-red { background: #ff5f57; }
  .dot-yellow { background: #febc2e; }
  .dot-green { background: #28c840; }

  .terminal-title {
    font-size: 0.75rem;
    color: var(--text-tertiary);
    font-weight: 400;
  }

  .terminal-body {
    padding: 20px;
    background: var(--bg-code);
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .terminal-body pre {
    margin: 0;
    font-size: 0.8rem;
    line-height: 1.6;
  }

  .terminal-body code {
    color: var(--text-secondary);
  }

  .term-prompt {
    color: var(--text-tertiary);
    user-select: none;
  }

  .term-cmd {
    color: var(--text-primary);
    font-weight: 500;
  }

  .term-output {
    color: var(--text-secondary);
  }

  .term-accent {
    color: var(--accent);
  }

  .term-warn {
    color: #d79921;
  }

  @media (max-width: 768px) {
    .hero {
      padding-top: calc(var(--nav-height) + 48px);
      padding-bottom: 72px;
    }

    .terminal-body {
      padding: 16px;
    }

    .terminal-body pre {
      font-size: 0.7rem;
    }

    .dot {
      width: 8px;
      height: 8px;
    }
  }

  @media (max-width: 480px) {
    .hero {
      padding-top: calc(var(--nav-height) + 40px);
      padding-bottom: 56px;
    }

    .hero-br {
      display: none;
    }

    .btn-hero {
      width: 100%;
      max-width: 240px;
      justify-content: center;
    }

    .terminal-body pre {
      font-size: 0.62rem;
    }

    .terminal-body {
      padding: 12px;
    }
  }
</style>
