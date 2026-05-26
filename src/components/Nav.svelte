<script lang="ts">
  import ThemeToggle from './icons/ThemeToggle.svelte';
  import { theme } from '$stores/theme';

  let sections = [
    { id: 'leaderboard', label: 'Leaderboard' },
    { id: 'radar', label: 'Compare' },
    { id: 'benchmarks', label: 'Benchmarks' },
    { id: 'scatter', label: 'Value' },
    { id: 'timeline', label: 'Timeline' },
    { id: 'model-profiles', label: 'Models' },
  ];

  let activeSection = $state('leaderboard');

  function scrollTo(id: string) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  }

  $effect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            activeSection = entry.target.id;
          }
        });
      },
      { rootMargin: '-20% 0px -70% 0px' }
    );

    sections.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  });

  let updatedLabel = $derived.by(() => {
    const d = new Date('2026-04-02');
    return `Updated ${d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
  });
</script>

<nav class="nav" id="nav">
  <div class="nav-inner">
    <div class="nav-brand">
      <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="Frontier AI Benchmark Tracker">
        <rect x="2" y="6" width="28" height="20" rx="3" stroke="currentColor" stroke-width="1.5"/>
        <line x1="8" y1="22" x2="8" y2="14" stroke="var(--color-accent)" stroke-width="2.5" stroke-linecap="round"/>
        <line x1="14" y1="22" x2="14" y2="10" stroke="var(--color-accent)" stroke-width="2.5" stroke-linecap="round"/>
        <line x1="20" y1="22" x2="20" y2="12" stroke="var(--color-accent)" stroke-width="2.5" stroke-linecap="round"/>
        <line x1="26" y1="22" x2="26" y2="8" stroke="var(--color-accent)" stroke-width="2.5" stroke-linecap="round"/>
        <circle cx="14" cy="10" r="2" fill="var(--color-accent)"/>
        <circle cx="26" cy="8" r="2" fill="var(--color-accent)"/>
      </svg>
      <span>Frontier AI Benchmarks</span>
    </div>
    <div class="nav-links">
      {#each sections as s}
        <button
          class="nav-link"
          class:active={activeSection === s.id}
          onclick={() => scrollTo(s.id)}
        >
          {s.label}
        </button>
      {/each}
    </div>
    <div class="nav-actions">
      <span class="badge-updated">{updatedLabel}</span>
      <a href="https://github.com/sirsahol/ai-benchmark-tracker" target="_blank" rel="noopener" class="icon-btn" title="View on GitHub" aria-label="View on GitHub">
        <svg width="18" height="18" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" fill="currentColor"/></svg>
      </a>
      <ThemeToggle />
    </div>
  </div>
</nav>
