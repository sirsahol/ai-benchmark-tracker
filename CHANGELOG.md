# Changelog

All notable updates to the AI Benchmark Tracker are documented here.

Format: `[date] — Summary`

---

## [2026-04-02] — Initial Release

### Added
- **12 models tracked** across 7 providers (Anthropic, Google, OpenAI, Z.ai, xAI, Meta, MiniMax)
- **11 benchmarks** across 6 categories (reasoning, science, coding, math, knowledge work, long context)
- YAML data files for all providers: `data/models/*.yaml`
- Benchmark definitions: `data/benchmarks/benchmarks.yaml`
- First snapshot: `data/snapshots/2026-04-02.yaml`
- Interactive dashboard with leaderboard, radar chart, benchmark deep dives, price-performance scatter, timeline, model profiles
- GLM-5.1 spotlight card with unverified status tracking

### Sources
- Artificial Analysis Intelligence Index (artificialanalysis.ai)
- Google DeepMind Model Card for Gemini 3.1 Pro
- Anthropic official release for Claude Opus 4.6
- LM Council benchmarks (lmcouncil.ai)
- Z.ai / Serenities AI for GLM-5.1 coding claims
- Design for Online comparative analysis
- DataCamp model reviews

### Notes
- GLM-5.1 coding score (45.3 on Claude Code harness, 94.6% of Opus 4.6) is self-reported by Z.ai. Not independently verified as of this date.
- Gemini 3.1 Pro is still in "Preview" — not yet GA.
- GPT-5.4 benchmark coverage on BenchLM is still incomplete.
