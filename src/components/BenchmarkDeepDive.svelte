<script lang="ts">
  import { data } from '$stores/data';
  import { CATEGORIES } from '$lib/constants';
  import { getBenchName } from '$lib/chart-utils';
  import BenchmarkBarChart from './BenchmarkBarChart.svelte';

  let activeTab = $state(Object.keys(CATEGORIES)[0]);
  let categoryKeys = $derived(Object.keys(CATEGORIES));

  let tabData = $derived.by(() => {
    const benchmarks: Record<string, any> = $data.benchmarks || {};
    return categoryKeys.map((key: string) => {
      const cat = CATEGORIES[key];
      const benchItems = cat.benchmarks.map((bk: string) => {
        const meta = benchmarks[bk];
        return {
          key: bk,
          name: getBenchName(bk),
          description: meta?.description || '',
          notes: meta?.notes || '',
          hasNote: !!meta?.notes,
        };
      }).filter((b: any) => {
        const models: any[] = $data.models || [];
        return models.some((m: any) => m.scores?.[b.key]?.value != null);
      });
      return { key, label: cat.label, benchmarks: benchItems };
    }).filter((c: any) => c.benchmarks.length > 0);
  });
</script>

<section id="benchmarks" class="container">
  <div class="section-header">
    <h2 class="section-title">Benchmark Deep Dive</h2>
    <p class="section-subtitle">Detailed scores by category</p>
  </div>
  <div class="tab-bar">
    {#each tabData as cat}
      <button
        class="tab-btn"
        class:active={activeTab === cat.key}
        onclick={() => activeTab = cat.key}
      >{cat.label}</button>
    {/each}
  </div>
  {#each tabData as cat}
    <div class="tab-panel" class:active={activeTab === cat.key}>
      {#each cat.benchmarks as bench}
        <div class="benchmark-chart-group">
          <h3>{bench.name}
            {#if bench.hasNote}
              <span class="badge badge-unverified" style="font-size:9px;vertical-align:middle">&#9888; Note</span>
            {/if}
          </h3>
          <p class="bench-desc">{bench.description}{bench.hasNote ? ' — ' + bench.notes : ''}</p>
          <BenchmarkBarChart benchmarkKey={bench.key} models={$data.models || []} />
        </div>
      {/each}
    </div>
  {/each}
</section>
