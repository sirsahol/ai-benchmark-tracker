# Frontier AI Benchmark Tracker

Structured benchmark data for frontier AI models (April 2026+). Machine-readable YAML files, an interactive dashboard, and historical snapshots for tracking model progression over time.

**Live Dashboard:** [Deployed here](https://www.perplexity.ai/computer/a/frontier-ai-benchmark-tracker-HND2tHqjQrGSQ9_6w4CDsw)

## Models Tracked

| Provider | Models | Type |
|----------|--------|------|
| Google DeepMind | Gemini 3.1 Pro, Gemini 3 Pro | Proprietary |
| OpenAI | GPT-5.4, GPT-5.3 Codex, GPT-5.2, GPT-5.1 | Proprietary |
| Anthropic | Claude Opus 4.6, Claude Sonnet 4.6, Claude Opus 4.5 | Proprietary |
| Z.ai | GLM-5.1, GLM-5, GLM-4.7 | Open-source (MIT) |
| xAI | Grok 4.20 Beta, Grok 4 | Proprietary |
| Meta | Llama 4 Scout, Llama 4 Maverick | Open-source |
| MiniMax | MiniMax-M2.7 | Proprietary |

## Benchmarks Covered

| Category | Benchmarks |
|----------|------------|
| Reasoning | ARC-AGI-2, Humanity's Last Exam |
| Science | GPQA Diamond |
| Coding | SWE-Bench Verified, Terminal-Bench 2.0, LiveCodeBench Pro |
| Mathematics | FrontierMath |
| Knowledge Work | GDPval-AA Elo, BrowseComp |
| Long Context | MRCR v2 (8-needle 128k) |
| Composite | Artificial Analysis Intelligence Index |

## Repo Structure

```
ai-benchmark-tracker/
├── index.html                     # Interactive dashboard (self-contained)
├── README.md                      # This file
├── CHANGELOG.md                   # Update log
├── CONTRIBUTING.md                # How to add new models/benchmarks
├── data/
│   ├── models/                    # One YAML file per provider
│   │   ├── anthropic.yaml
│   │   ├── google.yaml
│   │   ├── openai.yaml
│   │   ├── zai.yaml
│   │   ├── xai.yaml
│   │   ├── meta.yaml
│   │   └── minimax.yaml
│   ├── benchmarks/
│   │   └── benchmarks.yaml        # Benchmark definitions & metadata
│   └── snapshots/
│       └── 2026-04-02.yaml        # Point-in-time leaderboard snapshots
```

## How to Update

### Adding a new model version

1. Open the relevant `data/models/<provider>.yaml`
2. Add a new entry under `models:` with the model ID, release date, scores, and pricing
3. Update `CHANGELOG.md` with a new date entry
4. Create a new snapshot in `data/snapshots/YYYY-MM-DD.yaml`

### Adding a new benchmark

1. Add the benchmark definition to `data/benchmarks/benchmarks.yaml`
2. Add scores to each relevant model in `data/models/*.yaml`
3. Document the addition in `CHANGELOG.md`

### Example: Adding GLM-5.2

```yaml
# In data/models/zai.yaml, add under models:
  - id: glm-5.2
    name: GLM-5.2
    released: 2026-05-XX
    type: open-source (MIT)
    context_window: 200k
    scores:
      intelligence_index: XX
      swe_bench_verified: XX.X
      # ... other benchmark scores
    verification:
      status: verified  # or unverified
      notes: "Independently validated by [source]"
```

## Data Format

### Model YAML Schema

```yaml
provider:
  name: string
  brand_color: string (hex)
  website: string (url)

models:
  - id: string (kebab-case unique ID)
    name: string (display name)
    released: date (YYYY-MM-DD)
    type: string (proprietary | open-source)
    context_window: string (e.g., "1M", "200k")
    max_output: string (e.g., "128k")
    pricing:
      input_per_m: number (USD per 1M tokens)
      output_per_m: number (USD per 1M tokens)
    architecture:
      total_params: string
      # ... other arch details
    scores:
      <benchmark_id>: number
    verification:
      status: string (verified | unverified | partially_verified)
      notes: string
```

### Snapshot YAML Schema

```yaml
snapshot_date: date
notes: string
leaderboard:
  - rank: number
    model: string
    provider: string
    intelligence_index: number
category_winners:
  <category>: string (model name)
```

## Sources

- [Artificial Analysis](https://artificialanalysis.ai) — Intelligence Index, pricing, speed benchmarks
- [Google DeepMind Model Card](https://deepmind.google/models/model-cards/gemini-3-1-pro/) — Gemini 3.1 Pro benchmarks
- [Anthropic](https://www.anthropic.com/news/claude-opus-4-6) — Claude Opus 4.6 official benchmarks
- [LM Council](https://lmcouncil.ai/benchmarks) — Independent multi-benchmark comparisons
- [Serenities AI](https://serenitiesai.com) — GLM-5.1 analysis
- [BenchLM](https://benchlm.ai) — Cross-model comparisons

## License

Data is compiled from public sources. YAML files and dashboard code are MIT licensed.
