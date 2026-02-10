<script lang="ts">
  const currentYear = new Date().getFullYear();
</script>

<footer class="footer">
  <div class="container">
    <div class="footer-inner">
      <div class="footer-brand">
        <div class="footer-logo">
          <svg width="20" height="32" viewBox="0 0 47.581429 77.315781" xmlns="http://www.w3.org/2000/svg">
            <g transform="translate(351.30686,-158.54937)">
              <g transform="matrix(2.4307449,0,0,2.4307449,-363.74873,-127.07147)" style="fill:var(--accent)">
                <path d="m 12.3073,127.88684 v 11.22412 4.57854 a 5.6360459,5.6360459 0 0 0 5.251876,5.62136 V 138.08674 133.5082 A 5.6360459,5.6360459 0 0 0 12.3073,127.88684 Z" />
                <path d="m 5.1185506,117.50342 v 15.94993 a 5.4826112,5.4826112 0 0 0 5.2518754,5.4622 v -10.92491 -10.48722 z" />
                <path d="m 19.441507,128.02077 v 13.09636 a 6.7146358,6.7146358 0 0 0 5.251876,-6.2513 v -0.79324 a 6.7146358,6.7146358 0 0 0 -5.251876,-6.05182 z" />
              </g>
            </g>
          </svg>
          <span class="footer-name">HashPrep</span>
        </div>
        <p class="footer-tagline">Dataset Profiler & Debugger for Machine Learning</p>
      </div>

      <div class="footer-links">
        <div class="footer-col">
          <h4 class="footer-heading">Product</h4>
          <a href="/#features">Features</a>
          <a href="/#how-it-works">How It Works</a>
          <a href="https://pypi.org/project/hashprep/">PyPI</a>
        </div>
        <div class="footer-col">
          <h4 class="footer-heading">Resources</h4>
          <a href="/docs">Documentation</a>
          <a href="https://github.com/cachevector/hashprep">GitHub</a>
          <a href="https://github.com/cachevector/hashprep/blob/main/CONTRIBUTING.md">Contributing</a>
        </div>
        <div class="footer-col">
          <h4 class="footer-heading">Legal</h4>
          <a href="https://github.com/cachevector/hashprep/blob/main/LICENSE">MIT License</a>
        </div>
      </div>
    </div>

    <div class="footer-bottom">
      <p>&copy; {currentYear} HashPrep. Open source under MIT License.</p>
    </div>
  </div>
</footer>

<style>
  .footer {
    padding: 64px 0 32px;
    border-top: 1px solid var(--border-secondary);
  }

  .footer-inner {
    display: grid;
    grid-template-columns: 1.2fr 2fr;
    gap: 48px;
    margin-bottom: 48px;
  }

  .footer-logo {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
  }

  .footer-name {
    font-family: var(--font-mono);
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: -0.02em;
  }

  .footer-tagline {
    font-size: 0.85rem;
    color: var(--text-tertiary);
    line-height: 1.6;
    max-width: 280px;
  }

  .footer-links {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 32px;
  }

  .footer-col {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .footer-heading {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
  }

  .footer-col a {
    font-size: 0.85rem;
    color: var(--text-secondary);
    transition: color var(--transition-fast);
  }

  .footer-col a:hover {
    color: var(--accent);
  }

  .footer-bottom {
    padding-top: 24px;
    border-top: 1px solid var(--border-secondary);
  }

  .footer-bottom p {
    font-size: 0.8rem;
    color: var(--text-tertiary);
  }

  @media (max-width: 768px) {
    .footer-inner {
      grid-template-columns: 1fr;
      gap: 40px;
    }

    .footer-links {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  @media (max-width: 480px) {
    .footer {
      padding: 40px 0 20px;
    }

    .footer-inner {
      gap: 32px;
      margin-bottom: 32px;
    }

    .footer-links {
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }

    .footer-bottom p {
      font-size: 0.75rem;
    }
  }
</style>
