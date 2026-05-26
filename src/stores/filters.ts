import { writable, derived } from 'svelte/store';
import { data } from './data';

export const providerFilter = writable<string | null>(null);
export const activeTags = writable<Set<string>>(new Set());
export const showSuperseded = writable<boolean>(false);

export const filteredModels = derived(
  [data, providerFilter, activeTags, showSuperseded],
  ([$data, $providerFilter, $activeTags, $showSuperseded]) => {
    let models = $data.models || [];
    if (!$showSuperseded) {
      models = models.filter((m: any) => !m.superseded_by);
    }
    if ($providerFilter) {
      models = models.filter((m: any) => m.provider_id === $providerFilter);
    }
    if ($activeTags.size > 0) {
      models = models.filter((m: any) =>
        (m.tags || []).some((t: string) => $activeTags.has(t))
      );
    }
    return models;
  }
);
