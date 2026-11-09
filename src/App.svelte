<script lang="ts">
  import { theme } from '$stores/theme';
  import { data } from '$stores/data';
  import Nav from './components/Nav.svelte';
  import Hero from './components/Hero.svelte';
  import KpiGrid from './components/KpiGrid.svelte';
  import TagFilterBar from './components/TagFilterBar.svelte';
  import LeaderboardTable from './components/LeaderboardTable.svelte';
  import RadarChart from './components/RadarChart.svelte';
  import BenchmarkDeepDive from './components/BenchmarkDeepDive.svelte';
  import PricePerformanceScatter from './components/PricePerformanceScatter.svelte';
  import Timeline from './components/Timeline.svelte';
  import ModelProfileCards from './components/ModelProfileCards.svelte';
  import Footer from './components/Footer.svelte';

  let dateSubtitle = $derived.by(() => {
    const builtAt = $data._build_metadata?.built_at;
    if (builtAt) {
      const d = new Date(builtAt);
      if (!isNaN(d.getTime())) {
        return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
      }
    }
    return new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  });
</script>

<div data-theme={$theme}>
  <Nav />
  <Hero />
  <KpiGrid />
  <section id="leaderboard" class="container">
    <div class="section-header">
      <h2 class="section-title">Intelligence Leaderboard</h2>
      <p class="section-subtitle">Artificial Analysis Intelligence Index &mdash; {dateSubtitle}</p>
    </div>
    <TagFilterBar />
    <LeaderboardTable />
  </section>
  <RadarChart />
  <BenchmarkDeepDive />
  <PricePerformanceScatter />
  <Timeline />
  <ModelProfileCards />
  <Footer />
</div>
