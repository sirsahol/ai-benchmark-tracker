import { writable } from 'svelte/store';

export const radarSelection = writable<Set<string>>(new Set());
