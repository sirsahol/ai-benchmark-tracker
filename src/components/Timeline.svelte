<script lang="ts">
  import { data } from '$stores/data';
  import { getProviderColor } from '$lib/chart-utils';

  let sorted = $derived.by(() => {
    const models: any[] = $data.models || [];
    return [...models].sort((a: any, b: any) =>
      new Date(a.released).getTime() - new Date(b.released).getTime()
    );
  });
</script>

<section id="timeline" class="container">
  <div class="section-header">
    <h2 class="section-title">Release Timeline</h2>
    <p class="section-subtitle">Model releases &mdash; April 2025 to March 2026</p>
  </div>
  <div class="card">
    <div class="timeline-track">
      <div class="timeline-line"></div>
      <div class="timeline-items">
        {#each sorted as m}
          {@const color = getProviderColor(m.provider_id)}
          {@const date = new Date(m.released)}
          {@const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          <div class="timeline-item">
            <div class="timeline-date">{dateStr}</div>
            <div
              class="timeline-dot"
              style="background:{color};box-shadow:0 0 0 2px var(--color-bg), 0 0 0 4px {color}40"
            ></div>
            <div class="timeline-model" style="color:{color}">{m.name}</div>
          </div>
        {/each}
      </div>
    </div>
  </div>
</section>
