export const CATEGORIES: Record<string, { label: string; benchmarks: string[] }> = {
  reasoning_science: { label: 'Reasoning & Science', benchmarks: ['arc_agi_2', 'gpqa_diamond', 'hle_with_tools'] },
  coding: { label: 'Coding & Engineering', benchmarks: ['swe_bench_verified', 'terminal_bench_2', 'livecode_bench_elo', 'swe_bench_pro'] },
  math: { label: 'Mathematics', benchmarks: ['frontier_math'] },
  knowledge_work: { label: 'Knowledge Work', benchmarks: ['gdpval_aa_elo', 'browsecomp', 'biglaw_bench'] },
  long_context: { label: 'Long Context', benchmarks: ['mrcr_v2_128k'] },
  instruction_following: { label: 'Instruction Following', benchmarks: ['ifeval'] },
  composite: { label: 'Composite', benchmarks: ['intelligence_index', 'chatbot_arena_elo', 'aitnt_arena_elo'] },
  agentic: { label: 'Agentic', benchmarks: ['webarena'] },
};

export const RADAR_AXES = ['intelligence_index', 'swe_bench_verified', 'gpqa_diamond', 'arc_agi_2', 'frontier_math', 'browsecomp'];
