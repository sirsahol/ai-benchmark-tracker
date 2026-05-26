<script lang="ts">
  import { data } from '$stores/data';
  import { filteredModels } from '$stores/filters';
  import ModelCard from './ModelCard.svelte';

  let models = $derived.by(() => {
    return [...$filteredModels].sort((a: any, b: any) => {
      const aS = !!a.superseded_by;
      const bS = !!b.superseded_by;
      if (aS !== bS) return aS ? 1 : -1;
      return new Date(b.released).getTime() - new Date(a.released).getTime();
    });
  });
</script>

<section id="model-profiles" class="container">
  <div class="section-header">
    <h2 class="section-title">Model Profiles</h2>
    <p class="section-subtitle">Click a card to expand full benchmark details</p>
  </div>
  <div class="model-cards-grid">
    {#each models as m (m.id)}
      <ModelCard model={m} />
    {/each}
  </div>
</section>
