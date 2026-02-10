import { browser } from '$app/environment';

type Theme = 'light' | 'dark';

function getSystemTheme(): Theme {
  if (!browser) return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function getStoredPreference(): 'light' | 'dark' | 'system' {
  if (!browser) return 'system';
  return (localStorage.getItem('hashprep-theme') as 'light' | 'dark' | 'system') || 'system';
}

let preference = $state<'light' | 'dark' | 'system'>(getStoredPreference());
let resolved = $derived<Theme>(preference === 'system' ? getSystemTheme() : preference);

function apply(t: Theme) {
  if (!browser) return;
  document.documentElement.setAttribute('data-theme', t);
}

function setPreference(pref: 'light' | 'dark' | 'system') {
  preference = pref;
  if (browser) {
    localStorage.setItem('hashprep-theme', pref);
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
