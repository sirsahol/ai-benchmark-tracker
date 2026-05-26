<script lang="ts">
  import { data } from '$stores/data';
  import { activeTags } from '$stores/filters';

  let allTags = $derived.by(() => {
    const tags = new Set<string>();
    ($data.models || []).forEach((m: any) => (m.tags || []).forEach((t: string) => tags.add(t)));
    return [...tags].sort();
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
  {#each allTags as tag}
    <button
      class="tag-pill"
      class:active={$activeTags.has(tag)}
      onclick={() => handleClick(tag)}
    >{tag}</button>
  {/each}
</div>
