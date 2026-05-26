<script lang="ts">
  import { data } from '$stores/data';
  import { sortedModels, sortConfig } from '$stores/sort';
  import { providerFilter, showSuperseded } from '$stores/filters';
  import { getCompositePrice, getSpeed, getProviderColor, getProviderName, getProviderRowClass } from '$lib/chart-utils';
  import ProviderLogo from './icons/ProviderLogo.svelte';

  let providerList = $derived.by(() => {
    const ids = [...new Set(($data.models || []).map((m: any) => m.provider_id))];
    return ids.map((pid: string) => ({ id: pid, name: getProviderName(pid) }));
  });

  function handleSort(col: string) {
    if (col === 'rank') {
      $sortConfig = { column: 'intelligence_index', direction: -1 };
    } else if ($sortConfig.column === col) {
      $sortConfig = { ...$sortConfig, direction: ($sortConfig.direction * -1) as 1 | -1 };
    } else {
      const dir = (col === 'name' || col === 'released') ? 1 : -1;
      $sortConfig = { column: col, direction: dir as 1 | -1 };
    }
  }

  function getSortArrow(col: string): string {
    if ($sortConfig.column !== col) return '▲';
    return $sortConfig.direction === 1 ? '▲' : '▼';
  }

  function isSorted(col: string): boolean {
    return $sortConfig.column === col;
  }

  function getII(m: any): number | null {
    return m.scores?.intelligence_index?.value ?? null;
  }

  function parseContext(v: string | undefined): number {
    if (!v) return 0;
    const n = parseFloat(v);
    return v.includes('M') ? n * 1000 : n;
  }

  let enriched = $derived.by(() => {
    const models = $sortedModels;
    return models.map((m: any) => ({
      ...m,
      _ii: getII(m),
      _price: getCompositePrice(m),
      _speed: getSpeed(m),
      _provider_id: m.provider_id,
      _superseded: !!m.superseded_by,
    }));
  });

  let highlights = $derived.by(() => {
    const active = enriched.filter((m: any) => !m._superseded);
    const scores = active.map((m: any) => m._ii).filter((v: any): v is number => v !== null);
    const maxScore = scores.length > 0 ? Math.max(...scores) : 0;
    const prices = active.map((m: any) => m._price).filter((v: any): v is number => v !== null);
    const minPrice = prices.length > 0 ? Math.min(...prices) : 0;
    const speeds = active.map((m: any) => m._speed).filter((v: any): v is number => v !== null);
    const maxSpeed = speeds.length > 0 ? Math.max(...speeds) : 0;
    return { maxScore, minPrice, maxSpeed };
  });

  let displayModels = $derived.by(() => {
    if (!$showSuperseded) {
      return enriched.filter((m: any) => !m._superseded);
    }
    const active = enriched.filter((m: any) => !m._superseded);
    const superseded = enriched.filter((m: any) => m._superseded);
    return [...active, ...superseded];
  });

  let rankCounter = $derived.by(() => {
    let rank = 0;
    return displayModels.map((m: any) => {
      if (!m._superseded) rank++;
      return m._superseded ? '—' : rank;
    });
  });
</script>

<div class="table-controls">
  <select bind:value={$providerFilter}>
    <option value={""}>All Providers</option>
    {#each providerList as p}
      <option value={p.id}>{p.name}</option>
    {/each}
  </select>
  <label>
    <input type="checkbox" bind:checked={$showSuperseded} />
    Show superseded models
  </label>
</div>

<div class="leaderboard-wrap">
  <table class="leaderboard">
    <thead>
      <tr>
        <th class:sorted={isSorted('rank')} onclick={() => handleSort('rank')}>
          # <span class="sort-arrow">{getSortArrow('rank')}</span>
        </th>
        <th class:sorted={isSorted('name')} onclick={() => handleSort('name')}>
          Model <span class="sort-arrow">{getSortArrow('name')}</span>
        </th>
        <th class:sorted={isSorted('intelligence_index')} onclick={() => handleSort('intelligence_index')}>
          Intelligence <span class="sort-arrow">{getSortArrow('intelligence_index')}</span>
        </th>
        <th class:sorted={isSorted('price')} onclick={() => handleSort('price')}>
          $/M Tokens <span class="sort-arrow">{getSortArrow('price')}</span>
        </th>
        <th class:sorted={isSorted('speed')} onclick={() => handleSort('speed')}>
          Speed (t/s) <span class="sort-arrow">{getSortArrow('speed')}</span>
        </th>
        <th class:sorted={isSorted('context_window')} onclick={() => handleSort('context_window')}>
          Context <span class="sort-arrow">{getSortArrow('context_window')}</span>
        </th>
        <th class:sorted={isSorted('released')} onclick={() => handleSort('released')}>
          Released <span class="sort-arrow">{getSortArrow('released')}</span>
        </th>
      </tr>
    </thead>
    <tbody>
      {#each displayModels as m, i (m.id)}
        {@const isSuperseded = m._superseded}
        {@const isUnverified = m.verification?.status === 'unverified'}
        {@const isTopScore = m._ii === highlights.maxScore && m._ii !== null}
        {@const isCheapest = m._price === highlights.minPrice && m._price != null}
        {@const isFastest = m._speed === highlights.maxSpeed && m._speed != null}
        <tr class="{getProviderRowClass(m._provider_id)}{isSuperseded ? ' row-superseded' : ''}">
          <td style="color:var(--color-text-muted);font-size:var(--text-xs)">{rankCounter[i]}</td>
          <td>
            <div class="model-cell">
              <span class="provider-logo">
                <ProviderLogo provider={m._provider_id} size={20} />
              </span>
              <div>
                <div class="model-name">
                  {m.name}
                  {#if isTopScore}
                    <span class="badge badge-gold">&#x1F947; #1</span>
                  {/if}
                  {#if isSuperseded}
                    <span class="badge badge-superseded">Superseded</span>
                  {/if}
                </div>
                <div class="model-provider">{getProviderName(m._provider_id)}</div>
              </div>
            </div>
          </td>
          <td style="font-weight:600;{isTopScore ? 'color:var(--color-gold)' : ''}">
            {#if m._ii !== null}
              {m._ii}
              {#if isUnverified}
                <span class="badge-sr" title="Self-reported by provider — not independently verified">SR</span>
              {/if}
            {:else}
              &mdash;
            {/if}
          </td>
          <td style="{isCheapest ? 'color:var(--color-success);font-weight:600' : ''}">
            {m._price != null ? '$' + m._price.toFixed(2) : '—'}
          </td>
          <td style="{isFastest ? 'color:var(--color-accent);font-weight:600' : ''}">
            {m._speed ?? '—'}
          </td>
          <td>{m.context_window || '—'}</td>
          <td style="font-size:var(--text-xs);color:var(--color-text-muted)">
            {new Date(m.released).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
