import { writable } from 'svelte/store';

type Theme = 'dark' | 'light';

function createThemeStore() {
  const stored = typeof localStorage !== 'undefined' ? localStorage.getItem('theme') as Theme : null;
  const initial: Theme = stored || 'dark';

  if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('data-theme', initial);
  }

  const { subscribe, set, update } = writable<Theme>(initial);

  return {
    subscribe,
    toggle: () => update(t => {
      const next = t === 'dark' ? 'light' : 'dark';
      if (typeof document !== 'undefined') {
        document.documentElement.setAttribute('data-theme', next);
      }
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('theme', next);
      }
      return next;
    }),
    set: (v: Theme) => {
      if (typeof document !== 'undefined') {
        document.documentElement.setAttribute('data-theme', v);
      }
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('theme', v);
      }
      set(v);
    }
  };
}

export const theme = createThemeStore();
