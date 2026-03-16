import { browser } from '$app/environment';

type Theme = 'light' | 'dark';

// Must match --bg-primary in app.css for each theme.
// Safari doesn't repaint body.backgroundColor when CSS vars change on html,
// so we set it directly in JS with the known values.
const BG: Record<Theme, string> = {
  light: '#fdfbff',
  dark:  '#0f1117',
};

function safeLocalStorage(action: 'get' | 'set', key: string, value?: string): string | null {
  try {
    if (action === 'get') return localStorage.getItem(key);
    localStorage.setItem(key, value!);
    return null;
  } catch {
    return null;
  }
}

function getSystemTheme(): Theme {
  if (!browser) return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function getStoredPreference(): 'light' | 'dark' | 'system' {
  if (!browser) return 'system';
  return (safeLocalStorage('get', 'hashprep-theme') as 'light' | 'dark' | 'system') || 'system';
}

let preference = $state<'light' | 'dark' | 'system'>(getStoredPreference());
let resolved = $derived<Theme>(preference === 'system' ? getSystemTheme() : preference);

function apply(t: Theme) {
  if (!browser) return;
  document.documentElement.setAttribute('data-theme', t);
  document.documentElement.style.colorScheme = t;
  // Safari bug: body's background-color using var(--bg-primary) is not repainted
  // when the CSS variable changes via a [data-theme] attribute selector on <html>.
  // The CSS transition on background-color also fights inline style updates in
  // Safari, so we removed that transition and set the value directly here.
  document.body.style.backgroundColor = BG[t];
}

function setPreference(pref: 'light' | 'dark' | 'system') {
  preference = pref;
  if (browser) {
    safeLocalStorage('set', 'hashprep-theme', pref);
  }
  apply(pref === 'system' ? getSystemTheme() : pref);
}

function init() {
  if (!browser) return;
  apply(resolved);

  const mq = window.matchMedia('(prefers-color-scheme: dark)');
  mq.addEventListener('change', () => {
    if (preference === 'system') {
      apply(getSystemTheme());
    }
  });
}

export const theme = {
  get preference() { return preference; },
  get resolved() { return resolved; },
  set: setPreference,
  toggle() {
    setPreference(resolved === 'light' ? 'dark' : 'light');
  },
  init
};
