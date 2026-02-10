<script lang="ts">
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
</script>

<Navbar />

<main class="docs">
  <section class="docs-hero">
    <div class="container docs-hero-inner">
      <div class="docs-kicker">Documentation</div>
      <h1>Learn HashPrep in minutes, not hours.</h1>
      <p>
        A focused guide to installing, running, and integrating HashPrep into your ML workflows. Built to match the
        minimal, calm UI of the rest of the site.
      </p>
    </div>
  </section>

  <section class="docs-body">
    <div class="container docs-layout">
      <aside class="docs-nav" aria-label="Documentation sections">
        <div class="docs-nav-group">
          <div class="docs-nav-label">Getting started</div>
          <a href="#overview">Overview</a>
          <a href="#installation">Installation</a>
          <a href="#quickstart-cli">Quickstart (CLI)</a>
          <a href="#quickstart-python">Quickstart (Python)</a>
        </div>
        <div class="docs-nav-group">
          <div class="docs-nav-label">Deep dive</div>
          <a href="#reports">Reports</a>
          <a href="#cli-reference">CLI reference</a>
          <a href="#python-api">Python API</a>
          <a href="#checks">Available checks</a>
          <a href="#contributing">Contributing</a>
        </div>
      </aside>

      <article class="docs-content">
        <section id="overview">
          <h2>Overview</h2>
          <p>
            HashPrep is a dataset profiler and debugger for machine learning. Think of it as
            <strong>&ldquo;Pandas Profiling + a linter for datasets&rdquo;</strong> that runs before you train.
          </p>
          <p>
            It scans your data, surfaces critical issues, explains why they matter for modeling, and suggests (or
            generates) concrete fixes. You can use it as a single CLI command or as a Python library inside your
            pipelines.
          </p>
        </section>

        <section id="installation">
          <h2>Installation</h2>
          <div class="docs-card">
            <h3>Using pip</h3>
            <pre data-lang="bash"><code><span class="hl-command">pip</span> <span class="hl-arg">install</span> <span class="hl-value">hashprep</span></code></pre>
          </div>

          <div class="docs-card">
            <h3>Using uv (recommended)</h3>
            <pre data-lang="bash"><code><span class="hl-comment"># Install uv (if needed)</span>
<span class="hl-command">curl</span> <span class="hl-flag">-LsSf</span> <span class="hl-value">https://astral.sh/uv/install.sh</span> <span class="hl-operator">|</span> <span class="hl-command">sh</span>

<span class="hl-comment"># Install HashPrep</span>
<span class="hl-command">uv</span> <span class="hl-command">pip</span> <span class="hl-arg">install</span> <span class="hl-value">hashprep</span>

<span class="hl-comment"># Or from source</span>
<span class="hl-command">git</span> <span class="hl-arg">clone</span> <span class="hl-value">https://github.com/cachevector/hashprep.git</span>
<span class="hl-command">cd</span> <span class="hl-value">hashprep</span>
<span class="hl-command">uv</span> <span class="hl-arg">sync</span></code></pre>
          </div>

          <p class="docs-note">
            After installation, the <code>hashprep</code> command is available directly in your terminal.
          </p>
        </section>

        <section id="quickstart-cli">
          <h2>Quickstart &mdash; CLI</h2>
          <div class="docs-card">
            <h3>1. Run a quick scan</h3>
            <p>Get a concise summary of dataset issues in your terminal.</p>
            <pre data-lang="bash"><code><span class="hl-command">hashprep</span> <span class="hl-arg">scan</span> <span class="hl-value">dataset.csv</span></code></pre>
          </div>

          <div class="docs-grid-2">
            <div class="docs-card">
              <h3>Common options</h3>
              <ul>
                <li><code>--target COLUMN</code> &mdash; target column for ML-specific checks</li>
                <li><code>--checks outliers,high_missing_values</code> &mdash; run only selected checks</li>
                <li><code>--json</code> &mdash; JSON output for automation</li>
                <li><code>--sample-size N</code> &mdash; restrict analysis to N rows</li>
              </ul>
            </div>
            <div class="docs-card">
              <h3>Example</h3>
              <pre data-lang="bash"><code><span class="hl-command">hashprep</span> <span class="hl-arg">scan</span> <span class="hl-value">train.csv</span> <span class="hl-operator">\</span>
  <span class="hl-flag">--target</span> <span class="hl-value">Survived</span> <span class="hl-operator">\</span>
  <span class="hl-flag">--checks</span> <span class="hl-value">outliers,high_missing_values,class_imbalance</span></code></pre>
            </div>
          </div>

          <div class="docs-card">
            <h3>2. Detailed analysis</h3>
            <p>Drill into every issue HashPrep found.</p>
            <pre data-lang="bash"><code><span class="hl-command">hashprep</span> <span class="hl-arg">details</span> <span class="hl-value">train.csv</span> <span class="hl-flag">--target</span> <span class="hl-value">Survived</span></code></pre>
          </div>
        </section>

        <section id="quickstart-python">
          <h2>Quickstart &mdash; Python</h2>

          <div class="docs-card">
            <h3>Basic analysis</h3>
            <pre data-lang="python"><code><span class="hl-keyword">import</span> pandas <span class="hl-keyword">as</span> pd
<span class="hl-keyword">from</span> hashprep <span class="hl-keyword">import</span> DatasetAnalyzer

df = pd.read_csv(<span class="hl-string">"dataset.csv"</span>)

analyzer = DatasetAnalyzer(df)
summary = analyzer.analyze()

print(<span class="hl-string">"Critical issues:"</span>, summary[<span class="hl-string">"critical_count"</span>])
print(<span class="hl-string">"Warnings:"</span>, summary[<span class="hl-string">"warning_count"</span>])</code></pre>
          </div>

          <div class="docs-grid-2">
            <div class="docs-card">
              <h3>With a target column</h3>
              <pre data-lang="python"><code>analyzer = DatasetAnalyzer(
    df,
    target_col=<span class="hl-string">"target"</span>,
)
summary = analyzer.analyze()</code></pre>
            </div>

            <div class="docs-card">
              <h3>Run specific checks</h3>
              <pre data-lang="python"><code>analyzer = DatasetAnalyzer(
    df,
    selected_checks=[<span class="hl-string">"outliers"</span>, <span class="hl-string">"high_missing_values"</span>, <span class="hl-string">"class_imbalance"</span>],
)
summary = analyzer.analyze()</code></pre>
            </div>
          </div>
        </section>

        <section id="reports">
          <h2>Reports</h2>

          <div class="docs-card">
            <h3>Generate a report from the CLI</h3>
            <pre data-lang="bash"><code><span class="hl-command">hashprep</span> <span class="hl-arg">report</span> <span class="hl-value">dataset.csv</span> <span class="hl-flag">--format</span> <span class="hl-value">html</span> <span class="hl-flag">--theme</span> <span class="hl-value">minimal</span></code></pre>
            <p>
              Reports can be exported as <code>md</code>, <code>json</code>, <code>html</code>, or
              <code>pdf</code>, using the <code>--format</code> flag. Use <code>--with-code</code> to generate
              companion Python scripts with cleaning logic and pipelines.
            </p>
          </div>

          <div class="docs-card">
            <h3>Generate reports from Python</h3>
            <pre data-lang="python"><code><span class="hl-keyword">from</span> hashprep <span class="hl-keyword">import</span> DatasetAnalyzer
<span class="hl-keyword">from</span> hashprep.reports <span class="hl-keyword">import</span> generate_report

analyzer = DatasetAnalyzer(df, include_plots=<span class="hl-builtin">True</span>)
summary = analyzer.analyze()

generate_report(
    summary,
    format=<span class="hl-string">"html"</span>,
    full=<span class="hl-builtin">True</span>,
    output_file=<span class="hl-string">"dataset_hashprep_report.html"</span>,
    theme=<span class="hl-string">"minimal"</span>,
)</code></pre>
          </div>
        </section>

        <section id="cli-reference">
          <h2>CLI reference</h2>

          <div class="docs-card">
            <h3><code>hashprep scan</code></h3>
            <p>
              Run a quick scan and print a compact summary of issues to the terminal. Ideal for a fast health check
              during development.
            </p>
            <pre data-lang="bash"><code><span class="hl-command">hashprep</span> <span class="hl-arg">scan</span> <span class="hl-value">dataset.csv</span> <span class="hl-flag">--target</span> <span class="hl-value">Survived</span></code></pre>
            <ul>
              <li><code>--target COLUMN</code> &mdash; target column for ML checks (class imbalance, leakage, etc.)</li>
              <li><code>--checks LIST</code> &mdash; comma-separated list of checks to run</li>
              <li><code>--critical-only</code> &mdash; hide warnings and show only critical issues</li>
              <li><code>--json</code> &mdash; emit JSON instead of human-readable text</li>
              <li><code>--quiet</code> &mdash; minimal output, useful in CI</li>
            </ul>
          </div>

          <div class="docs-card">
            <h3><code>hashprep details</code></h3>
            <p>
              Produce a verbose, line-by-line description of each issue in the dataset, with statistics and
              recommendations.
            </p>
            <pre data-lang="bash"><code><span class="hl-command">hashprep</span> <span class="hl-arg">details</span> <span class="hl-value">dataset.csv</span> <span class="hl-flag">--target</span> <span class="hl-value">Survived</span></code></pre>
            <p>
              Accepts the same options as <code>scan</code> and is best used when you are actively debugging a dataset
              or deciding which columns to drop or transform.
            </p>
          </div>

          <div class="docs-card">
            <h3><code>hashprep report</code></h3>
            <p>
              Generate a full report in HTML, PDF, Markdown, or JSON. Reports contain summaries, plots, and (optionally)
              auto-generated Python code.
            </p>
            <pre data-lang="bash"><code><span class="hl-command">hashprep</span> <span class="hl-arg">report</span> <span class="hl-value">dataset.csv</span> <span class="hl-flag">--format</span> <span class="hl-value">html</span> <span class="hl-flag">--theme</span> <span class="hl-value">minimal</span> <span class="hl-flag">--with-code</span></code></pre>
            <ul>
              <li><code>--format &#123;md,json,html,pdf&#125;</code> &mdash; output format (Markdown is the default)</li>
              <li><code>--theme &#123;minimal,neubrutalism&#125;</code> &mdash; HTML theme</li>
              <li><code>--with-code</code> &mdash; write companion <code>_fixes.py</code> and <code>_pipeline.py</code> files</li>
              <li><code>--comparison FILE</code> &mdash; compare two datasets for drift (train vs test, etc.)</li>
              <li><code>--sample-size N</code> / <code>--no-sample</code> &mdash; control automatic sampling</li>
            </ul>
          </div>

          <div class="docs-card">
            <h3>Exit codes</h3>
            <p>
              HashPrep is CI-friendly: non-zero exit codes indicate that critical issues were detected or an internal
              error occurred. You can wire this into pre-commit hooks or data-quality checks in your pipeline.
            </p>
          </div>
        </section>

        <section id="python-api">
          <h2>Python API</h2>

          <div class="docs-card">
            <h3><code>DatasetAnalyzer</code></h3>
            <p>
              The core entry point for programmatic usage. It accepts a pandas <code>DataFrame</code> and optional
              configuration for targets, sampling, comparison datasets, and which checks to run.
            </p>
            <pre data-lang="python"><code><span class="hl-keyword">from</span> hashprep <span class="hl-keyword">import</span> DatasetAnalyzer

analyzer = DatasetAnalyzer(
    df,
    target_col=<span class="hl-string">"target"</span>,
    selected_checks=[<span class="hl-string">"outliers"</span>, <span class="hl-string">"high_missing_values"</span>],
    include_plots=<span class="hl-builtin">True</span>,
)
summary = analyzer.analyze()</code></pre>
            <p>The returned <code>summary</code> is a JSON-serializable dictionary with keys such as:</p>
            <ul>
              <li><code>critical_count</code> / <code>warning_count</code></li>
              <li><code>issues</code> &mdash; list of individual issues with severity, column, check name, and message</li>
              <li><code>summaries</code> &mdash; per-column statistics and optional plots</li>
              <li><code>sampling_info</code> &mdash; information about any sampling that was applied</li>
            </ul>
          </div>

          <div class="docs-card">
            <h3>Sampling large datasets</h3>
            <p>
              For very large tables, you can control how many rows HashPrep inspects using a sampling configuration.
              This keeps runtimes predictable in production.
            </p>
            <pre data-lang="python"><code><span class="hl-keyword">from</span> hashprep.utils.sampling <span class="hl-keyword">import</span> SamplingConfig

sampling = SamplingConfig(max_rows=<span class="hl-value">10000</span>)

analyzer = DatasetAnalyzer(
    df,
    sampling_config=sampling,
    auto_sample=<span class="hl-builtin">True</span>,
)
summary = analyzer.analyze()</code></pre>
            <p>
              When sampling is applied, <code>summary["sampling_info"]</code> contains details such as fractions and
              original row counts.
            </p>
          </div>

          <div class="docs-card">
            <h3>Generating fix scripts and pipelines</h3>
            <p>
              Beyond reports, HashPrep can emit executable Python code that encodes suggested fixes and ML pipelines.
            </p>
            <pre data-lang="python"><code><span class="hl-keyword">from</span> hashprep.checks.core <span class="hl-keyword">import</span> Issue
<span class="hl-keyword">from</span> hashprep.preparers.codegen <span class="hl-keyword">import</span> CodeGenerator
<span class="hl-keyword">from</span> hashprep.preparers.pipeline_builder <span class="hl-keyword">import</span> PipelineBuilder
<span class="hl-keyword">from</span> hashprep.preparers.suggestions <span class="hl-keyword">import</span> SuggestionProvider

issues = [Issue(<span class="hl-arg">**i</span>) <span class="hl-keyword">for</span> i <span class="hl-keyword">in</span> summary[<span class="hl-string">"issues"</span>]]
column_types = summary.get(<span class="hl-string">"column_types"</span>, <span class="hl-builtin">dict</span>())

provider = SuggestionProvider(
    issues=issues,
    column_types=column_types,
    target_col=<span class="hl-string">"target"</span>,
)
suggestions = provider.get_suggestions()

codegen = CodeGenerator(suggestions)
fixes_code = codegen.generate_pandas_script()

builder = PipelineBuilder(suggestions)
pipeline_code = builder.generate_pipeline_code()</code></pre>
            <p>
              You can write these strings to disk (for example, <code>fixes.py</code> and <code>pipeline.py</code>) or
              load them dynamically in your tooling.
            </p>
          </div>

          <div class="docs-card">
            <h3>Drift detection</h3>
            <p>
              To compare training and serving data, construct a <code>DatasetAnalyzer</code> with both a primary and
              comparison dataset and enable the <code>dataset_drift</code> check.
            </p>
            <pre data-lang="python"><code>analyzer = DatasetAnalyzer(
    train_df,
    comparison_df=test_df,
    selected_checks=[<span class="hl-string">"dataset_drift"</span>],
)
summary = analyzer.analyze()</code></pre>
          </div>
        </section>

        <section id="checks">
          <h2>Available checks</h2>

          <div class="docs-card docs-checks">
            <div>
              <h3>Data quality</h3>
              <ul>
                <li><code>missing_values</code> &mdash; overall missingness patterns</li>
                <li><code>high_missing_values</code> &mdash; columns with heavy missingness</li>
                <li><code>duplicates</code> &mdash; duplicate rows</li>
                <li><code>single_value_columns</code> &mdash; near-constant features</li>
              </ul>
            </div>
            <div>
              <h3>Distribution</h3>
              <ul>
                <li><code>outliers</code> &mdash; IQR-based outlier detection</li>
                <li><code>high_cardinality</code> &mdash; categorical columns with too many uniques</li>
                <li><code>uniform_distribution</code> &mdash; uniformly distributed numeric columns</li>
                <li><code>many_zeros</code> &mdash; features dominated by zeros</li>
              </ul>
            </div>
            <div>
              <h3>ML-specific</h3>
              <ul>
                <li><code>class_imbalance</code> &mdash; target imbalance (requires <code>--target</code>)</li>
                <li><code>feature_correlation</code> &mdash; highly correlated features</li>
                <li><code>target_leakage</code> &mdash; features leaking target information</li>
                <li><code>dataset_drift</code> &mdash; drift between train / test datasets</li>
              </ul>
            </div>
          </div>
        </section>

        <section id="contributing">
          <h2>Contributing</h2>
          <p>
            HashPrep is open source and welcomes contributions. If you want to fix a bug, add a check, or improve the
            reports:
          </p>
          <ul>
            <li>Read the <a href="https://github.com/cachevector/hashprep/blob/main/CONTRIBUTING.md">contribution guide</a></li>
            <li>Open an issue describing the change you&rsquo;d like to make</li>
            <li>Create a pull request with clear motivation and tests where appropriate</li>
          </ul>
        </section>
      </article>
    </div>
  </section>
</main>

<Footer />

<style>
  .docs {
    padding-top: var(--nav-height);
    overflow-x: hidden;
    max-width: 100vw;
  }

  .docs-hero {
    padding: 72px 0 40px;
    background: var(--hero-gradient);
  }

  .docs-hero-inner {
    text-align: center;
  }

  .docs-hero-inner h1 {
    font-size: clamp(2.1rem, 4vw, 3rem);
    font-weight: 300;
    letter-spacing: -0.05em;
    margin-bottom: 14px;
  }

  .docs-hero-inner p {
    font-size: 0.95rem;
    color: var(--text-secondary);
  }

  .docs-kicker {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 4px 12px;
    margin-bottom: 20px;
    border-radius: 999px;
    border: 1px solid var(--border-secondary);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--text-tertiary);
  }

  .docs-body {
    padding: 48px 0 96px;
  }

  .docs-layout {
    display: grid;
    grid-template-columns: minmax(0, 220px) minmax(0, 1fr);
    gap: 64px;
    align-items: flex-start;
    width: 100%;
    box-sizing: border-box;
  }

  .docs-nav {
    position: sticky;
    top: calc(var(--nav-height) + 24px);
    align-self: flex-start;
    padding-right: 8px;
    border-right: 1px solid var(--border-secondary);
    display: flex;
    flex-direction: column;
    gap: 20px;
    font-size: 0.8rem;
  }

  .docs-nav-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .docs-nav-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: var(--text-tertiary);
    margin-bottom: 4px;
  }

  .docs-nav a {
    padding: 4px 0;
    color: var(--text-secondary);
    text-decoration: none;
    border-radius: 4px;
    transition: color var(--transition-fast);
  }

  .docs-nav a:hover {
    color: var(--text-primary);
  }

  .docs-content {
    display: flex;
    flex-direction: column;
    gap: 64px;
    font-size: 0.9rem;
    max-width: 100%;
    min-width: 0;
  }

  .docs-content section + section {
    margin-top: 0;
  }

  .docs-content h2 {
    font-size: 1.1rem;
    letter-spacing: -0.04em;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-secondary);
  }

  .docs-content h3 {
    font-size: 0.9rem;
    font-weight: 600;
    text-transform: none;
    letter-spacing: -0.02em;
    color: var(--text-primary);
    margin-bottom: 12px;
  }

  .docs-content p {
    margin-bottom: 16px;
  }

  /* Ensure paragraphs after headings have proper spacing */
  .docs-content h3 + p {
    margin-top: 0;
  }

  /* Ensure lists after paragraphs have spacing */
  .docs-content p + ul {
    margin-top: 12px;
  }

  .docs-content ul {
    margin: 0;
    padding-left: 18px;
  }

  .docs-content li + li {
    margin-top: 4px;
  }

  .docs-card {
    border: 1px solid var(--border-secondary);
    border-radius: 0px;
    padding: 28px 32px;
    background: transparent;
    transition: border-color var(--transition-fast);
  }

  .docs-card h3 {
    margin-top: 0;
  }

  .docs-card h3 + p {
    margin-top: 8px;
  }

  .docs-card p:first-child {
    margin-top: 0;
  }

  .docs-card ul:first-child {
    margin-top: 0;
  }

  .docs-card:hover {
    border-color: var(--border-accent);
  }

  .docs-card + .docs-card {
    margin-top: 24px;
  }

  .docs-grid-2 {
    display: grid;
    grid-template-columns: repeat(2, minmax(280px, 1fr));
    gap: 40px;
    margin-top: 24px;
    margin-bottom: 32px;
  }

  .docs-grid-2 .docs-card {
    margin-top: 0;
    min-width: 0;
  }

  /* Code blocks in grid should wrap and be readable */
  .docs-grid-2 pre {
    white-space: pre-wrap;
    word-break: break-word;
    overflow-wrap: break-word;
    font-size: 0.75rem;
    line-height: 1.6;
    max-width: 100%;
  }

  .docs-grid-2 code {
    white-space: pre-wrap;
    word-break: break-word;
    display: block;
  }

  /* Ensure code blocks don't overflow */
  .docs-grid-2 .docs-card {
    overflow: hidden;
  }

  .docs-note {
    font-size: 0.8rem;
    color: var(--text-tertiary);
  }

  .docs-checks {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
  }

  pre {
    margin: 0;
    margin-top: 12px;
    margin-bottom: 20px;
    padding: 16px 20px;
    border-radius: 0px;
    border: 1px solid var(--border-secondary);
    background: var(--bg-code);
    font-size: 0.8rem;
    overflow-x: auto;
    overflow-y: hidden;
    position: relative;
    white-space: pre;
  }

  /* Allow wrapping for long commands when needed */
  pre code {
    white-space: pre;
    display: block;
  }

  /* Spacing after code blocks - works everywhere */
  pre + p,
  .docs-card pre + p {
    margin-top: 20px;
    margin-bottom: 16px;
  }

  pre + ul,
  .docs-card pre + ul {
    margin-top: 20px;
  }

  /* Ensure code blocks have bottom margin */
  .docs-card pre {
    margin-bottom: 20px;
  }

  code {
    font-family: var(--font-mono);
  }

  pre::before {
    position: absolute;
    inset-block-start: 6px;
    inset-inline-end: 10px;
    padding: 2px 8px;
    border-radius: 999px;
    border: 1px solid rgba(148, 163, 184, 0.4);
    font-size: 0.65rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--text-tertiary);
    background: rgba(15, 23, 42, 0.02);
  }

  pre[data-lang="bash"]::before {
    content: 'Bash';
  }

  pre[data-lang="python"]::before {
    content: 'Python';
  }

  /* Syntax highlighting */
  .hl-comment {
    color: #64748b;
  }

  .hl-command {
    color: var(--accent);
  }

  .hl-arg,
  .hl-flag {
    color: #22c55e;
  }

  .hl-operator {
    color: #e5e7eb;
  }

  .hl-value {
    color: #eab308;
  }

  .hl-keyword {
    color: #a855f7;
  }

  .hl-string {
    color: #f97316;
  }

  .hl-builtin {
    color: #0ea5e9;
  }

  @media (max-width: 960px) {
    .docs-layout {
      grid-template-columns: minmax(0, 1fr);
      gap: 32px;
    }

    .docs-nav {
      position: static;
      border-right: none;
      border-bottom: 1px solid var(--border-secondary);
      padding-bottom: 12px;
      flex-direction: row;
      flex-wrap: wrap;
      gap: 16px;
    }

    .docs-nav-group {
      min-width: 160px;
    }

    .docs-checks {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 640px) {
    .docs-hero {
      padding-top: 56px;
      padding-bottom: 32px;
    }

    .docs-hero-inner {
      padding: 0 16px;
    }

    .docs-grid-2 {
      grid-template-columns: minmax(0, 1fr);
    }

    .docs-checks {
      grid-template-columns: minmax(0, 1fr);
    }

    .docs-card {
      padding: 20px 16px;
    }

    pre {
      padding: 12px 16px;
      font-size: 0.7rem;
    }
  }
</style>

