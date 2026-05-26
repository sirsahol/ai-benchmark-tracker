<script lang="ts">
  import { data } from '$stores/data';
  import { getCompositePrice, getSpeed } from '$lib/chart-utils';

  let kpis = $derived.by(() => {
    const models: any[] = $data.models || [];
    const validModels = models.filter((m: any) => m.scores?.intelligence_index?.value != null);
    const topModel = [...validModels].sort((a: any, b: any) =>
      (b.scores?.intelligence_index?.value ?? 0) - (a.scores?.intelligence_index?.value ?? 0)
    )[0];

    const priced = models
      .map((m: any) => ({ ...m, _price: getCompositePrice(m) }))
      .filter((m: any) => m._price != null);
    const cheapest = priced.length > 0
      ? priced.reduce((a: any, b: any) => a._price < b._price ? a : b)
      : null;

    const speeded = models
      .map((m: any) => ({ ...m, _speed: getSpeed(m) }))
      .filter((m: any) => m._speed != null);
    const fastest = speeded.length > 0
      ? speeded.reduce((a: any, b: any) => a._speed > b._speed ? a : b)
      : null;

    const latest = [...models].sort((a: any, b: any) =>
      new Date(b.released).getTime() - new Date(a.released).getTime()
    )[0];

    return [
      {
        value: topModel ? String(topModel.scores.intelligence_index.value) : '--',
        label: topModel ? `Top Score — ${topModel.name}` : 'Top Score',
        color: 'var(--color-gold)',
      },
      {
        value: cheapest ? `$${cheapest._price}` : '--',
        label: cheapest ? `Best Price — ${cheapest.name}` : 'Best Price',
        color: 'var(--color-success)',
      },
      {
        value: fastest ? `${fastest._speed} t/s` : '--',
        label: fastest ? `Fastest — ${fastest.name}` : 'Fastest',
        color: 'var(--color-accent)',
      },
      {
        value: String(models.length),
        label: 'Models Tracked',
        color: 'var(--color-text)',
      },
    ];
  });
</script>

<div class="container">
  <div class="kpi-grid">
    {#each kpis as kpi}
      <div class="kpi-card">
        <div class="kpi-value" style="color:{kpi.color}">{kpi.value}</div>
        <div class="kpi-label">{kpi.label}</div>
      </div>
    {/each}
  </div>
</div>
