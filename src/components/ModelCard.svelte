<script lang="ts">
  import { data } from '$stores/data';
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
  let verifStatus = $derived(model.verification?.status || 'unverified');
  let verifColor = $derived(verifStatus === 'verified' ? 'var(--color-success)' : verifStatus === 'unverified' ? 'var(--color-text-faint)' : 'var(--color-amber)');
  let verifIcon = $derived(verifStatus === 'verified' ? '\u2713' : verifStatus === 'unverified' ? '\u2717' : '~');

  let allModels = $derived($data.models || []);

  let lastUpdated = $derived.by(() => {
    const dates = Object.values(model.scores || {})
      .map((s: any) => s?.benchmark_date)
      .filter(Boolean)
      .sort();
    const latest = dates.length ? dates[dates.length - 1] : model.released;
    if (!latest) return null;
    return new Date(latest).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  });

  let benchScores = $derived.by(() => {
    const results: any[] = [];
    if (!model.scores) return results;
    Object.entries(model.scores).forEach(([key, obj]: [string, any]) => {
      if (key === 'speed_tps') return;
      if (obj?.value == null) return;
      results.push({ key, name: getBenchName(key), value: obj.value, unit: obj.unit || '', self_reported: obj.self_reported || false, source: obj.source || '', benchmark_date: obj.benchmark_date || '', notes: obj.notes || '' });
    });
    results.sort((a, b) => {
      if (a.key === 'intelligence_index') return -1;
      if (b.key === 'intelligence_index') return 1;
      return (b.value ?? 0) - (a.value ?? 0);
    });
    return results;
  });

  let benchMaxByKey = $derived.by(() => {
    const max: Record<string, number> = {};
    benchScores.forEach((b: any) => {
      const vals = allModels
        .map((m: any) => m.scores?.[b.key]?.value)
        .filter((v: any) => v != null && !isNaN(v));
      max[b.key] = vals.length ? Math.max(...vals) : b.value;
    });
    return max;
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
    <div style="flex:1">
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
    {#if lastUpdated}
      <span class="card-updated-badge" title="Most recent benchmark date recorded">Updated {lastUpdated}</span>
    {/if}
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
  <div class="model-card-expand">
    <!-- Details -->
    <div class="card-section-label">Details</div>
    <div class="card-row"><span class="cr-label">Released</span><span class="cr-val">{model.released || '—'}</span></div>
    <div class="card-row"><span class="cr-label">Type</span><span class="cr-val">{model.type || '—'}</span></div>
    {#if model.max_output}
      <div class="card-row"><span class="cr-label">Max output</span><span class="cr-val">{model.max_output}</span></div>
    {/if}
    {#if model.tags?.length}
      <div class="card-row"><span class="cr-label">Tags</span><span class="cr-val">{#each model.tags as tag}<span class="card-tag">{tag}</span>{/each}</span></div>
    {/if}
    {#if model.superseded_by}
      <div class="card-row"><span class="cr-label">Superseded by</span><span class="cr-val" style="color:var(--color-text-muted)">{model.superseded_by}</span></div>
    {/if}
    <!-- Pricing -->
    {#if model.pricing}
      {@const p = model.pricing}
      {@const hasPricing = (p.input_per_m != null && p.output_per_m != null) || p.composite_per_m != null || p.coding_plan_monthly_usd}
      {#if hasPricing}
        <div class="card-section-label" style="margin-top:var(--space-3)">Pricing</div>
        {#if p.input_per_m != null && p.output_per_m != null}
          <div class="card-row"><span class="cr-label">Per 1M tokens</span><span class="cr-val">${p.input_per_m} in / ${p.output_per_m} out</span></div>
        {:else if p.composite_per_m != null}
          <div class="card-row"><span class="cr-label">Per 1M tokens</span><span class="cr-val">~${p.composite_per_m}/1M (blended)</span></div>
        {/if}
        {#if p.cache_per_m != null}
          <div class="card-row"><span class="cr-label">Cached input</span><span class="cr-val">${p.cache_per_m}/1M</span></div>
        {/if}
        {#if p.notes}
          <div class="card-row"><span class="cr-label"></span><span class="cr-val" style="color:var(--color-text-muted);font-size:var(--text-xs)">{p.notes}</span></div>
        {/if}
      {/if}
    {/if}
    <!-- Architecture -->
    {#if model.architecture}
      {@const a = model.architecture}
      {@const hasArch = a.total_params || a.active_params || a.training_hardware || a.training_data_tokens || a.attention || a.thinking_levels || a.notes}
      {#if hasArch}
        <div class="card-section-label" style="margin-top:var(--space-3)">Architecture</div>
        {#if a.total_params}
          <div class="card-row"><span class="cr-label">Parameters</span><span class="cr-val">{a.total_params}{#if a.experts_total} MoE ({a.experts_total} experts, {a.experts_active} active){/if}</span></div>
        {/if}
        {#if a.active_params}
          <div class="card-row"><span class="cr-label">Active params</span><span class="cr-val">{a.active_params}</span></div>
        {/if}
        {#if a.training_hardware}
          <div class="card-row"><span class="cr-label">Hardware</span><span class="cr-val">{a.training_hardware}</span></div>
        {/if}
        {#if a.training_data_tokens}
          <div class="card-row"><span class="cr-label">Training data</span><span class="cr-val">{a.training_data_tokens} tokens</span></div>
        {/if}
        {#if a.attention}
          <div class="card-row"><span class="cr-label">Attention</span><span class="cr-val">{a.attention}</span></div>
        {/if}
        {#if a.thinking_levels}
          <div class="card-row"><span class="cr-label">Thinking levels</span><span class="cr-val">{a.thinking_levels.join(', ')}</span></div>
        {/if}
        {#if a.notes}
          <div class="card-row"><span class="cr-label">Notes</span><span class="cr-val" style="color:var(--color-text-muted);font-size:var(--text-xs)">{a.notes}</span></div>
        {/if}
      {/if}
    {/if}
    <!-- Verification -->
    <div class="card-section-label" style="margin-top:var(--space-3)">Verification</div>
    <div class="card-row">
      <span class="cr-label">Status</span>
      <span class="cr-val" style="color:{verifColor};font-weight:600">{verifIcon} {verifStatus}</span>
    </div>
    {#if model.verification?.notes}
      <div class="card-row"><span class="cr-label"></span><span class="cr-val" style="color:var(--color-text-muted);font-size:var(--text-xs)">{model.verification.notes}</span></div>
    {/if}
    <!-- Benchmark scores with bars -->
    {#if benchScores.length > 0}
      <div class="card-section-label" style="margin-top:var(--space-3)">Benchmark Scores</div>
      <div class="card-bench-list">
        {#each benchScores as b}
          {@const bMax = benchMaxByKey[b.key] || b.value}
          {@const pct = bMax > 0 ? Math.min(100, (b.value / bMax) * 100).toFixed(1) : 0}
          {@const unitLabel = b.unit === 'elo' ? ' Elo' : b.unit === 'points' ? ' pts' : (b.value <= 100 ? '%' : '')}
          {@const sourceTitle = [b.source ? b.source.replace(/https?:\/\/[^/]+/, '') : '', b.benchmark_date, b.notes].filter(Boolean).join(' \u00B7 ')}
          <div class="card-bench-row" title={sourceTitle}>
            <span class="cbr-name">{b.name}</span>
            <div class="cbr-track"><div class="cbr-fill" style="width:{pct}%;background:{color}"></div></div>
            <span class="cbr-val">{b.value}{unitLabel}{#if b.self_reported} <span class="badge-sr" title="Self-reported by provider">SR</span>{/if}</span>
          </div>
        {/each}
      </div>
    {:else}
      <div style="color:var(--color-text-muted);font-size:var(--text-xs);padding:var(--space-2) 0;margin-top:var(--space-3)">No benchmark scores on record yet.</div>
    {/if}
  </div>
</div>
