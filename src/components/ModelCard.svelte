<script lang="ts">
  import { getCompositePrice, getSpeed, getProviderColor, getBenchName } from '$lib/chart-utils';
  import ProviderLogo from './icons/ProviderLogo.svelte';

  let { model }: { model: any } = $props();
  let expanded = $state(false);

  let color = $derived(getProviderColor(model.provider_id));
  let ii = $derived(model.scores?.intelligence_index?.value ?? null);
  let price = $derived(getCompositePrice(model));
  let speed = $derived(getSpeed(model));
  let isSuperseded = $derived(!!model.superseded_by);
  let isUnverified = $derived(model.verification?.status === 'unverified');

  let benchScores = $derived.by(() => {
    const results: { key: string; name: string; value: number; unit: string; self_reported: boolean; source: string; notes: string }[] = [];
    if (!model.scores) return results;
    Object.entries(model.scores).forEach(([key, obj]: [string, any]) => {
      if (key === 'intelligence_index' || key === 'speed_tps') return;
      results.push({
        key,
        name: getBenchName(key),
        value: obj.value,
        unit: obj.unit || '',
        self_reported: obj.self_reported || false,
        source: obj.source || '',
        notes: obj.notes || '',
      });
    });
    return results;
  });
</script>

<div
  class="model-card"
  class:expanded
  role="button"
  tabindex="0"
  onclick={() => expanded = !expanded}
  onkeydown={(e: KeyboardEvent) => { if (e.key === 'Enter' || e.key === ' ') expanded = !expanded; }}
>
  <div style="position:absolute;top:0;left:0;right:0;height:3px;background:{color};opacity:0.7;border-radius:var(--radius-lg) var(--radius-lg) 0 0;"></div>
  <div class="model-card-head">
    <span class="provider-logo">
      <ProviderLogo provider={model.provider_id} size={28} />
    </span>
    <div>
      <h3>{model.name}
        {#if isSuperseded}
          <span class="badge badge-superseded">Superseded</span>
        {/if}
        {#if isUnverified}
          <span class="badge badge-unverified" style="font-size:9px">&#9888;</span>
        {/if}
      </h3>
      <span class="provider-name">{model.provider_name}</span>
    </div>
  </div>
  <div class="model-card-stats">
    <div class="model-card-stat">
      <div class="mc-value" style="color:{color}">{ii ?? '—'}</div>
      <div class="mc-label">Intelligence</div>
    </div>
    <div class="model-card-stat">
      <div class="mc-value">{price != null ? '$' + price.toFixed(2) : '—'}</div>
      <div class="mc-label">$/M Tokens</div>
    </div>
    <div class="model-card-stat">
      <div class="mc-value">{speed ?? '—'}</div>
      <div class="mc-label">Speed (t/s)</div>
    </div>
    <div class="model-card-stat">
      <div class="mc-value">{model.context_window || '—'}</div>
      <div class="mc-label">Context</div>
    </div>
  </div>
  {#if benchScores.length > 0}
    <div class="model-card-expand">
      <div style="font-size:var(--text-xs);font-weight:600;margin-bottom:var(--space-2);color:var(--color-text-muted)">Benchmark Scores</div>
      {#each benchScores as b}
        {@const unitLabel = b.unit === 'elo' ? ' Elo' : ''}
        {@const tooltipContent = [
          b.source ? b.source.replace(/https?:\/\//, '').substring(0, 40) + '...' : '',
          b.notes || '',
        ].filter(Boolean).join(' — ')}
        <div class="benchmark-mini">
          <span class="bm-name">{b.name}</span>
          <span class="bm-score">{b.value}{unitLabel}
            {#if b.self_reported}
              <span class="badge-sr" title="Self-reported by provider">SR</span>
            {/if}
          </span>
          {#if tooltipContent}
            <span class="bm-info" title="Source info">i
              <span class="bm-info-tooltip">{tooltipContent}</span>
            </span>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>
