import { writable, derived } from 'svelte/store';
import dashboard from '../../data/dashboard.json';

export const data = writable(dashboard);
export const providers = derived(data, $d => $d.providers);
export const benchmarks = derived(data, $d => $d.benchmarks);
export const models = derived(data, $d => $d.models);
