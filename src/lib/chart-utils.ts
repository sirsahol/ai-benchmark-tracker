import dashboard from '../../data/dashboard.json';

const DB_PROVIDERS: Record<string, { name: string; color: string }> = {};
Object.entries(dashboard.providers).forEach(([id, p]: [string, any]) => {
  DB_PROVIDERS[id] = { name: p.name, color: p.brand_color, website: p.website };
});

export function getCompositePrice(m: any): number | null {
  const p = m.pricing;
  if (!p) return null;
  if (p.composite_per_m) return p.composite_per_m;
  if (p.input_per_m != null && p.output_per_m != null)
    return (p.input_per_m + p.output_per_m) / 2;
  return null;
}

export function getSpeed(m: any): number | null {
  if (m.scores?.speed_tps?.value) return m.scores.speed_tps.value;
  const speedMap: Record<string, number | null> = {
    'gemini-3.1-pro': 109, 'gpt-5.4': 80, 'gpt-5.3-codex': 73,
    'claude-opus-4.6': 43, 'claude-sonnet-4.6': 68, 'gpt-5.2': 70,
    'glm-5': 68, 'claude-opus-4.5': 50, 'minimax-m2.7': 45,
    'grok-4.20-beta': 248, 'gemini-3-pro': 121, 'gemini-3-flash': 350,
  };
  return speedMap[m.id] ?? null;
}

export function getProviderColor(providerId: string): string {
  const isDark = typeof document !== 'undefined'
    && document.documentElement.getAttribute('data-theme') === 'dark';
  if (providerId === 'xai') return isDark ? '#C8C8C8' : '#666666';
  if (providerId === 'moonshot') return isDark ? '#4A7BC4' : '#0F3460';
  return DB_PROVIDERS[providerId]?.color || '#888';
}

export function getProviderName(providerId: string): string {
  return DB_PROVIDERS[providerId]?.name || providerId;
}

export function getChartColors(theme: string) {
  const isDark = theme === 'dark';
  return {
    grid: isDark ? 'rgba(48,54,61,0.6)' : 'rgba(208,215,222,0.6)',
    gridLight: isDark ? 'rgba(48,54,61,0.4)' : 'rgba(208,215,222,0.5)',
    label: isDark ? '#8B949E' : '#656D76',
    tooltip: {
      bg: isDark ? '#21262D' : '#fff',
      title: isDark ? '#E6EDF3' : '#1F2328',
      body: isDark ? '#8B949E' : '#656D76',
      border: isDark ? '#30363D' : '#D0D7DE',
    },
  };
}

export function srBadge(title?: string): string {
  return `<span class="badge-sr" title="${title || 'Self-reported by provider — not independently verified'}">SR</span>`;
}

export function getProviderRowClass(provider: string): string {
  return 'row-' + provider;
}

export function guessProvider(name: string): string {
  if (name.includes('Claude') || name.includes('Opus') || name.includes('Sonnet')) return 'anthropic';
  if (name.includes('Gemini')) return 'google';
  if (name.includes('GPT')) return 'openai';
  if (name.includes('GLM')) return 'zai';
  if (name.includes('Grok')) return 'xai';
  if (name.includes('Llama')) return 'meta';
  if (name.includes('MiniMax')) return 'minimax';
  if (name.includes('MiMo')) return 'xiaomi';
  if (name.includes('Kimi')) return 'moonshot';
  return 'openai';
}

export const EXTRA_BENCH_NAMES: Record<string, string> = {
  ifeval: 'IFEval',
  hle_no_tools: "Humanity's Last Exam (no tools)",
  math_500: 'MATH-500',
  livecode_bench: 'LiveCodeBench',
  aime_2025: 'AIME 2025',
  simple_qa: 'SimpleQA',
  mmlu: 'MMLU',
  mmlu_pro: 'MMLU-Pro',
  mmmlu: 'mMMLU',
  mmmu_pro: 'MMMU Pro',
  aime_2025_with_code: 'AIME 2025 (with code)',
  biglaw_bench: 'BigLaw Bench',
  apex_agents: 'Apex Agents',
  mcp_atlas: 'MCP Atlas',
  scicode: 'SciCode',
  swe_bench_pro: 'SWE-Bench Pro',
  weird_ml_v2: 'Weird ML v2',
  ifbench: 'IFBench',
  tau_bench_v2: 'TAU-Bench v2',
  pinch_bench: 'Pinch Bench',
  gdpval: 'GDPval',
};

export function getBenchName(key: string): string {
  const benchmarks: Record<string, any> = dashboard.benchmarks;
  return benchmarks[key]?.name || EXTRA_BENCH_NAMES[key] || key;
}
