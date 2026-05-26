<script lang="ts">
  import { onMount } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  import { data } from '$stores/data';
  import { theme } from '$stores/theme';
  import { getCompositePrice, getSpeed, getProviderColor, getProviderName, getChartColors } from '$lib/chart-utils';

  Chart.register(...registerables);

  let canvas: HTMLCanvasElement;
  let chart: Chart | null = null;

  function renderChart() {
    if (!canvas) return;
    if (chart) chart.destroy();

    const models: any[] = $data.models || [];
    const colors = getChartColors($theme);

    const dataPoints = models
      .map((m: any) => ({
        score: m.scores?.intelligence_index?.value ?? null,
        price: getCompositePrice(m),
        speed: getSpeed(m),
        label: m.name,
        provider: m.provider_id,
      }))
      .filter((d: any) => d.score != null && d.price != null);

    const byProvider: Record<string, any[]> = {};
    dataPoints.forEach((d: any) => {
      if (!byProvider[d.provider]) byProvider[d.provider] = [];
      byProvider[d.provider].push(d);
    });

    const datasets = Object.entries(byProvider).map(([prov, points]: [string, any[]]) => ({
      label: getProviderName(prov),
      data: points.map((p: any) => ({
        x: p.score,
        y: p.price,
        r: p.speed ? Math.max(6, Math.min(30, p.speed / 8)) : 6,
      })),
      backgroundColor: getProviderColor(prov) + '80',
      borderColor: getProviderColor(prov),
      borderWidth: 2,
      hoverBorderWidth: 3,
      _meta: points,
    }));

    const sorted = [...dataPoints].sort((a: any, b: any) => a.score - b.score);
    const frontier: any[] = [];
    let bestPrice = Infinity;
    for (let i = sorted.length - 1; i >= 0; i--) {
      if (sorted[i].price <= bestPrice) {
        bestPrice = sorted[i].price;
        frontier.unshift(sorted[i]);
      }
    }

    if (frontier.length > 1) {
      datasets.push({
        type: 'line' as const,
        label: 'Value Frontier',
        data: frontier.map((f: any) => ({ x: f.score, y: f.price })),
        borderColor: $theme === 'dark' ? 'rgba(79,152,163,0.4)' : 'rgba(14,122,134,0.4)',
        borderDash: [6, 4],
        borderWidth: 2,
        pointRadius: 0,
        fill: false,
        tension: 0.3,
      } as any);
    }

    const scores = dataPoints.map((d: any) => d.score);
    const minScore = Math.max(Math.min(...scores) - 2, 0);
    const maxScoreVal = Math.max(...scores) + 2;

    chart = new Chart(canvas, {
      type: 'bubble',
      data: { datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: { display: true, text: 'Intelligence Index', color: colors.label, font: { size: 12, family: "'Inter', sans-serif" } },
            grid: { color: colors.gridLight },
            ticks: { color: colors.label, font: { size: 11 } },
            min: minScore,
            max: maxScoreVal,
          },
          y: {
            title: { display: true, text: 'Price ($/M tokens)', color: colors.label, font: { size: 12, family: "'Inter', sans-serif" } },
            grid: { color: colors.gridLight },
            ticks: { color: colors.label, font: { size: 11 }, callback: (v: any) => '$' + v },
            reverse: true,
          },
        },
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: colors.label,
              usePointStyle: true,
              font: { size: 11, family: "'Inter', sans-serif" },
              padding: 12,
              filter: (item: any) => item.text !== 'Value Frontier',
            },
          },
          tooltip: {
            backgroundColor: colors.tooltip.bg,
            titleColor: colors.tooltip.title,
            bodyColor: colors.tooltip.body,
            borderColor: colors.tooltip.border,
            borderWidth: 1,
            padding: 12,
            titleFont: { family: "'Inter', sans-serif", weight: '600' },
            bodyFont: { family: "'Inter', sans-serif" },
            callbacks: {
              title: (ctx: any) => {
                const ds = ctx[0].dataset;
                if (ds._meta) return ds._meta[ctx[0].dataIndex]?.label || ds.label;
                return ds.label;
              },
              label: (ctx: any) => {
                const ds = ctx.dataset;
                if (!ds._meta) return '';
                const meta = ds._meta[ctx.dataIndex];
                return [
                  `Score: ${ctx.raw.x}`,
                  `Price: $${ctx.raw.y.toFixed(2)}/M`,
                  `Speed: ${meta?.speed ?? 'N/A'} t/s`,
                ];
              },
            },
          },
        },
      },
    });
  }

  $effect(() => {
    if ($data) renderChart();
  });

  $effect(() => {
    if ($theme) renderChart();
  });

  onMount(() => {
    renderChart();
  });
</script>

<section id="scatter" class="container">
  <div class="section-header">
    <h2 class="section-title">Price&ndash;Performance</h2>
    <p class="section-subtitle">Intelligence score vs. cost &mdash; bubble size = speed</p>
  </div>
  <div class="card">
    <div class="scatter-container">
      <canvas bind:this={canvas}></canvas>
    </div>
  </div>
</section>
