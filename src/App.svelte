<script lang="ts">
  import { theme } from '$stores/theme';
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
</script>

<div data-theme={$theme}>
  <Nav />
  <Hero />
  <KpiGrid />
  <section id="leaderboard" class="container">
    <div class="section-header">
      <h2 class="section-title">Intelligence Leaderboard</h2>
      <p class="section-subtitle">Artificial Analysis Intelligence Index &mdash; April 2026</p>
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
