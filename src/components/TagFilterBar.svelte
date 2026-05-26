<script lang="ts">
  import { data } from '$stores/data';
  import { activeTags } from '$stores/filters';

  let tagEntries = $derived.by(() => {
    const count: Record<string, number> = {};
    ($data.models || []).forEach((m: any) => (m.tags || []).forEach((t: string) => { count[t] = (count[t] || 0) + 1; }));
    const MIN_TAG_MODELS = 3;
    return Object.entries(count)
      .filter(([, c]) => c >= MIN_TAG_MODELS)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([tag, count]) => ({ tag, count }));
  });

  function handleClick(tag: string) {
    if (tag === 'all') {
      $activeTags = new Set();
    } else {
      const next = new Set($activeTags);
      if (next.has(tag)) {
        next.delete(tag);
      } else {
        next.add(tag);
      }
      $activeTags = next;
    }
  }

  let isAllActive = $derived($activeTags.size === 0);
</script>

<div class="tag-filter-bar">
  <button
    class="tag-pill"
    class:active={isAllActive}
    onclick={() => handleClick('all')}
  >All</button>
  {#each tagEntries as { tag, count }}
    <button
      class="tag-pill"
      class:active={$activeTags.has(tag)}
      onclick={() => handleClick(tag)}
      title="{count} models"
    >{tag}</button>
  {/each}
</div>
