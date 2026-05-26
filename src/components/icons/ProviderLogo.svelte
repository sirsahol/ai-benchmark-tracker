<script lang="ts">
  import { getProviderColor } from '$lib/chart-utils';

  let { provider, size = 20 }: { provider: string; size?: number } = $props();
  let color = $derived(getProviderColor(provider));
</script>

{#if provider === 'anthropic'}
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="9" stroke={color} stroke-width="2"/>
    <line x1="5" y1="12" x2="19" y2="12" stroke={color} stroke-width="2"/>
  </svg>
{:else if provider === 'google'}
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M12 2L14.5 9.5H22L16 14L18.5 22L12 17L5.5 22L8 14L2 9.5H9.5Z" fill={color} opacity="0.9"/>
  </svg>
{:else if provider === 'openai'}
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M12 2L17.5 5.5V12.5L12 16L6.5 12.5V5.5Z" stroke={color} stroke-width="1.8"/>
    <path d="M12 8L15 10V14L12 16L9 14V10Z" stroke={color} stroke-width="1.5"/>
  </svg>
{:else if provider === 'zai'}
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <rect x="3" y="3" width="18" height="18" rx="4" stroke={color} stroke-width="1.8"/>
    <path d="M7 8H17L7 16H17" stroke={color} stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
{:else if provider === 'xai'}
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M6 6L18 18M18 6L6 18" stroke={color} stroke-width="2.5" stroke-linecap="round"/>
  </svg>
{:else if provider === 'meta'}
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M4 12C4 7 8 4 12 8C16 12 16 12 16 12C16 12 16 12 20 8" stroke={color} stroke-width="2" stroke-linecap="round"/>
    <path d="M4 16C4 12 8 8 12 12C16 16 16 16 16 16C16 16 16 16 20 12" stroke={color} stroke-width="2" stroke-linecap="round"/>
  </svg>
{:else if provider === 'minimax'}
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M4 18V8L8 14L12 6L16 14L20 8V18" stroke={color} stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
{:else if provider === 'xiaomi'}
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="8" stroke={color} stroke-width="2"/>
    <circle cx="12" cy="12" r="3" fill={color}/>
  </svg>
{:else if provider === 'moonshot'}
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke={color} stroke-width="2" fill="none"/>
  </svg>
{:else if provider === 'mistral'}
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="8" stroke={color} stroke-width="2"/>
    <line x1="12" y1="4" x2="12" y2="20" stroke={color} stroke-width="1.5"/>
  </svg>
{:else if provider === 'deepseek'}
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="8" stroke={color} stroke-width="2"/>
    <path d="M8 8L16 16M16 8L8 16" stroke={color} stroke-width="1.5" stroke-linecap="round"/>
  </svg>
{:else}
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="8" stroke={color} stroke-width="2"/>
  </svg>
{/if}
