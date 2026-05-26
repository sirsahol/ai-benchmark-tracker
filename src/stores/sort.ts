import { writable, derived } from 'svelte/store';
import { filteredModels } from './filters';

export const sortConfig = writable<{ column: string; direction: 1 | -1 }>({
  column: 'intelligence_index',
  direction: -1
});

export const sortedModels = derived(
  [filteredModels, sortConfig],
  ([$filteredModels, $sortConfig]) => {
    const models = [...$filteredModels];
    const { column, direction } = $sortConfig;

    models.sort((a: any, b: any) => {
      let aVal: any, bVal: any;
      if (column === 'intelligence_index') {
        aVal = a.scores?.intelligence_index?.value ?? 0;
        bVal = b.scores?.intelligence_index?.value ?? 0;
      } else if (column === 'price') {
        const getPrice = (m: any) => {
          const p = m.pricing;
          if (!p) return null;
          if (p.input_per_m != null && p.output_per_m != null)
            return (p.input_per_m + p.output_per_m) / 2;
          return null;
        };
        aVal = getPrice(a) ?? Infinity;
        bVal = getPrice(b) ?? Infinity;
      } else if (column === 'name') {
        aVal = a.name?.toLowerCase() || '';
        bVal = b.name?.toLowerCase() || '';
        return direction * aVal.localeCompare(bVal);
      } else {
        aVal = a[column] ?? 0;
        bVal = b[column] ?? 0;
      }
      return direction * ((aVal as number) - (bVal as number));
    });

    return models;
  }
);
