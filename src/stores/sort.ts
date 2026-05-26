import { writable, derived } from 'svelte/store';
import { filteredModels } from './filters';

export const sortConfig = writable({ column: 'intelligence_index', direction: -1 as 1 | -1 });

function nullBottom<T>(av: T | null | undefined, bv: T | null | undefined, dir: number): number | null {
  if (av == null || av === '' || (typeof av === 'number' && isNaN(av))) return 1;
  if (bv == null || bv === '' || (typeof bv === 'number' && isNaN(bv))) return -1;
  return null;
}

export const sortedModels = derived(
  [filteredModels, sortConfig],
  ([$filteredModels, $sortConfig]) => {
    const { column, direction } = $sortConfig;
    return [...$filteredModels].sort((a: any, b: any) => {
      if (column === 'intelligence_index') {
        const av = a.scores?.intelligence_index?.value ?? null;
        const bv = b.scores?.intelligence_index?.value ?? null;
        const nb = nullBottom(av, bv, direction);
        if (nb !== null) return nb;
        return direction * (av - bv);
      }
      if (column === 'price') {
        const getPrice = (m: any) => {
          const p = m.pricing;
          if (!p) return null;
          if (p.composite_per_m) return p.composite_per_m;
          if (p.input_per_m != null && p.output_per_m != null)
            return (p.input_per_m + p.output_per_m) / 2;
          return null;
        };
        const av = getPrice(a);
        const bv = getPrice(b);
        const nb = nullBottom(av, bv, direction);
        if (nb !== null) return nb;
        return direction * (av - bv);
      }
      if (column === 'name') {
        const av = (a.name?.toLowerCase() || '');
        const bv = (b.name?.toLowerCase() || '');
        return direction * av.localeCompare(bv);
      }
      if (column === 'context_window') {
        const parse = (v: string) => { if (!v) return -1; const n = parseFloat(v); return v.toUpperCase().includes('M') ? n * 1000 : n; };
        const av = parse(a[column]);
        const bv = parse(b[column]);
        const nb = nullBottom(av, bv, direction);
        if (nb !== null) return nb;
        return direction * (av - bv);
      }
      if (column === 'released') {
        const av = a[column] ? new Date(a[column]).getTime() : null;
        const bv = b[column] ? new Date(b[column]).getTime() : null;
        const nb = nullBottom(av, bv, direction);
        if (nb !== null) return nb;
        return direction * ((av as number) - (bv as number));
      }
      const av = a[column] ?? null;
      const bv = b[column] ?? null;
      const nb = nullBottom(av, bv, direction);
      if (nb !== null) return nb;
      return direction * (Number(av) - Number(bv));
    });
  }
);
