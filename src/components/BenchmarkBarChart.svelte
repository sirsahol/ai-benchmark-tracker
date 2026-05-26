<script lang="ts">
  import { getProviderColor, guessProvider } from '$lib/chart-utils';

  let { benchmarkKey, models = [] }: { benchmarkKey: string; models: any[] } = $props();

  let entries = $derived.by(() => {
    const scores: Record<string, { value: number; self_reported: boolean }> = {};
    models.forEach((m: any) => {
      if (!m.scores) return;
      const s = m.scores[benchmarkKey];
      if (s) scores[m.name] = { value: s.value, self_reported: s.self_reported };
    });
    return Object.entries(scores)
      .map(([name, obj]) => ({ name, value: obj.value, self_reported: obj.self_reported }))
      .sort((a, b) => b.value - a.value);
  });

  let maxVal = $derived(entries.length > 0 ? entries[0].value : 1);
</script>

{#if entries.length > 0}
  <div class="bar-chart">
    {#each entries as entry}
      {@const m = models.find((mo: any) => mo.name === entry.name)}
      {@const provider = m ? m.provider_id || m.provider : guessProvider(entry.name)}
      {@const color = getProviderColor(provider)}
      {@const pct = maxVal > 0 ? (entry.value / maxVal * 100).toFixed(1) : '0'}
      {@const isWinner = entry.value === maxVal}
      <div class="bar-row">
        <span class="bar-label" title={entry.name}>{entry.name}</span>
        <div class="bar-track">
          <div
            class="bar-fill"
            class:winner={isWinner}
            style="width:{pct}%;background:{color}"
          ></div>
        </div>
        <span class="bar-value" style="color:{isWinner ? 'var(--color-gold)' : ''}">
          {entry.value}
          {#if entry.self_reported}
            <span class="badge-sr" title="Self-reported by provider">SR</span>
          {/if}
        </span>
      </div>
    {/each}
  </div>
{/if}
