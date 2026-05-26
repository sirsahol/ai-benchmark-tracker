<script lang="ts">
  import { onMount } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  import { data } from '$stores/data';
  import { theme } from '$stores/theme';
  import { radarSelection } from '$stores/radarSelection';
  import { getProviderColor, getChartColors } from '$lib/chart-utils';
  import { RADAR_AXES } from '$lib/constants';
  import ProviderLogo from './icons/ProviderLogo.svelte';

  Chart.register(...registerables);

  let canvas: HTMLCanvasElement;
  let chart: Chart | null = null;

  let radarModels = $derived.by(() => {
    return ($data.models || [])
      .filter((m: any) => m.scores?.intelligence_index?.value != null)
      .map((m: any) => m.name);
  });

  let axes = $derived(RADAR_AXES.map((key: string) => {
    const benchmarks: Record<string, any> = $data.benchmarks || {};
    const meta = benchmarks[key];
    return { key, label: (meta?.name || key).replace(/([^(]+)/, '$1') };
  }));

  function normalizeScore(benchKey: string, modelName: string): number | null {
    const benchmarks: Record<string, any> = $data.benchmarks || {};
    const models: any[] = $data.models || [];
    const values: number[] = [];
    let modelScore: number | null = null;

    models.forEach((m: any) => {
      if (m.scores?.[benchKey]?.value != null) {
        values.push(m.scores[benchKey].value);
        if (m.name === modelName) modelScore = m.scores[benchKey].value;
      }
    });

    if (modelScore === null || values.length === 0) return null;
    const maxV = Math.max(...values);
    const minV = Math.min(...values);
    if (maxV === minV) return 50;
    return ((modelScore - minV) / (maxV - minV)) * 100;
  }

  function renderChart() {
    if (!canvas) return;
    if (chart) chart.destroy();

    const colors = getChartColors($theme);
    const benchmarks: Record<string, any> = $data.benchmarks || {};
    const models: any[] = $data.models || [];

    const datasets = Array.from($radarSelection).map((name: string) => {
      const m = models.find((mo: any) => mo.name === name);
      const provider = m ? m.provider_id : 'openai';
      const color = getProviderColor(provider);
      return {
        label: name,
        data: axes.map((a: any) => normalizeScore(a.key, name) ?? 0),
        borderColor: color,
        backgroundColor: color + '20',
        pointBackgroundColor: color,
        pointBorderColor: color,
        pointRadius: 4,
        borderWidth: 2,
      };
    });

    chart = new Chart(canvas, {
      type: 'radar',
      data: {
        labels: axes.map((a: any) => a.label),
        datasets,
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
          r: {
            beginAtZero: true,
            max: 100,
            ticks: { display: false, stepSize: 25 },
            grid: { color: colors.grid },
            angleLines: { color: colors.grid },
            pointLabels: {
              font: { size: 11, family: "'Inter', sans-serif" },
              color: colors.label,
            },
          },
        },
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              font: { size: 12, family: "'Inter', sans-serif" },
              color: colors.label,
              usePointStyle: true,
              pointStyle: 'circle',
              padding: 16,
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
              label: (ctx: any) => {
                const benchKey = axes[ctx.dataIndex]?.key;
                const models: any[] = ($data as any).models || [];
                const modelName = ctx.dataset.label;
                const m = models.find((mo: any) => mo.name === modelName);
                const raw = m?.scores?.[benchKey]?.value;
                const benchmarks: Record<string, any> = ($data as any).benchmarks || {};
                const unit = benchmarks[benchKey]?.unit;
                return `${modelName}: ${raw ?? 'N/A'}${unit === 'elo' ? ' Elo' : ''}`;
              },
            },
          },
        },
      },
    });
  }

  function toggleModel(name: string) {
    const next = new Set($radarSelection);
    if (next.has(name)) {
      if (next.size <= 2) return;
      next.delete(name);
    } else {
      if (next.size >= 4) return;
      next.add(name);
    }
    $radarSelection = next;
  }

  $effect(() => {
    if ($radarSelection) renderChart();
  });

  $effect(() => {
    if ($theme) renderChart();
  });

  onMount(() => {
    const initial = new Set(['Claude Opus 4.6', 'Gemini 3.1 Pro', 'GPT-5.2']);
    const available = radarModels.filter((n: string) => initial.has(n));
    $radarSelection = new Set(available.length > 0 ? available : radarModels.slice(0, 3));
  });
</script>

<section id="radar" class="container radar-section">
  <div class="section-header">
    <h2 class="section-title">Model Comparison Radar</h2>
    <p class="section-subtitle">Select 2&ndash;4 models to compare across benchmarks</p>
  </div>
  <div class="controls">
    {#each radarModels as name}
      {@const m = ($data.models || []).find((mo: any) => mo.name === name)}
      {@const provider = m ? m.provider_id : 'openai'}
      <label class="model-check">
        <input
          type="checkbox"
          checked={$radarSelection.has(name)}
          onchange={() => toggleModel(name)}
        />
        <ProviderLogo provider={provider} size={16} />
        {name}
      </label>
    {/each}
  </div>
  <div class="chart-container">
    <canvas bind:this={canvas}></canvas>
  </div>
</section>
