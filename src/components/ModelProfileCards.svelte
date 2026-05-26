<script lang="ts">
  import { data } from '$stores/data';
  import { filteredModels } from '$stores/filters';
  import ModelCard from './ModelCard.svelte';

  let models = $derived($filteredModels);
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
