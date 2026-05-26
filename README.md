# Frontier AI Benchmark Tracker

Structured benchmark data for frontier AI models (April 2026+). Machine-readable YAML files, a Vite + Svelte interactive dashboard, and auto-populated scores for tracking model progression over time.

**Live Dashboard:** [sirsahol.github.io/ai-benchmark-tracker](https://sirsahol.github.io/ai-benchmark-tracker)

## Models Tracked

32 models across 11 providers:

| Provider | Models | Type |
|----------|--------|------|
| Google DeepMind | Gemini 3.1 Pro, Gemini 3 Pro, Gemini 3 Flash | Proprietary |
| OpenAI | GPT-5.4, GPT-5.3 Codex, GPT-5.2, GPT-5.1 | Proprietary |
| Anthropic | Claude Opus 4.6, Claude Sonnet 4.6, Claude Opus 4.5 | Proprietary |
| Z.ai | GLM-5.1, GLM-5, GLM-4.7 | Open-source (MIT) |
| xAI | Grok 4.20 Beta, Grok 4 | Proprietary |
| Meta | Llama 4 Scout, Llama 4 Maverick | Open-source |
| MiniMax | MiniMax-M2.7, MiniMax-M2.5 | Proprietary |
| Moonshot AI | Kimi K2.5, Kimi K2 | Open-source |
| DeepSeek | DeepSeek-R2 | Open-source |
| Mistral | Mistral Large 3 | Proprietary |
| Xiaomi | MiMo | Open-source |

## Benchmarks Covered

16 benchmarks across 8 categories:

| Category | Benchmarks |
|----------|------------|
| Reasoning | ARC-AGI-2, Humanity's Last Exam |
| Science | GPQA Diamond |
| Coding | SWE-Bench Verified, SWE-Bench Pro, Terminal-Bench 2.0, LiveCodeBench Pro |
| Mathematics | FrontierMath |
| Knowledge Work | GDPval-AA Elo, BrowseComp, BigLaw Bench |
| Long Context | MRCR v2 (8-needle 128k) |
| Agentic | WebArena |
| Composite | Artificial Analysis Intelligence Index, Chatbot Arena Elo, AiTNt Arena Elo |

## Architecture

Built with **Vite 6** + **Svelte 5** + **TypeScript** + **Chart.js**. The monolithic 106K `index.html` has been retired to `legacy/` and replaced by a component-based architecture.

### Data Pipeline

```
data/models/*.yaml  -->  build_json.py  -->  data/dashboard.json  -->  static import in Svelte
```

1. Benchmark scores and model metadata live in YAML files under `data/models/`
2. `build_json.py` compiles all YAML into a single `data/dashboard.json`
3. The Svelte app imports the JSON at build time and renders the dashboard

### Auto-Populate

A weekly GitHub Actions cron (`auto-populate-scores.yml`) fetches scores from free public APIs (HuggingFace Open LLM Leaderboard, Artificial Analysis) and opens a pull request with any changes. Human review required before merge.

## Repo Structure

```
ai-benchmark-tracker/
├── index.html                      # Vite entry point (thin shell)
├── package.json                    # pnpm, Vite 6, Svelte 5, Chart.js
├── vite.config.ts                  # Build config, path aliases
├── svelte.config.js                # Svelte compiler options
├── tsconfig.json                   # TypeScript config
├── src/
│   ├── main.ts                     # App bootstrap, CSS imports
│   ├── App.svelte                  # Root Svelte component
│   ├── lib/
│   │   └── constants.ts            # Shared constants
│   ├── stores/
│   │   ├── data.ts                 # Dashboard data store
│   │   ├── filters.ts              # Filter state
│   │   ├── radarSelection.ts       # Radar chart selection
│   │   ├── sort.ts                 # Sort state
│   │   └── theme.ts                # Dark/light theme
│   └── styles/
│       ├── design-tokens.css       # CSS custom properties
│       ├── theme-dark.css          # Dark mode overrides
│       ├── theme-light.css         # Light mode overrides
│       ├── base.css                # Reset and global styles
│       └── components.css          # Component-specific styles
├── data/
│   ├── dashboard.json              # Auto-generated — do not edit manually
│   ├── models/                     # One YAML file per provider
│   │   ├── anthropic.yaml
│   │   ├── google.yaml
│   │   ├── openai.yaml
│   │   ├── zai.yaml
│   │   ├── xai.yaml
│   │   ├── meta.yaml
│   │   ├── minimax.yaml
│   │   ├── moonshot.yaml
│   │   ├── deepseek.yaml
│   │   ├── mistral.yaml
│   │   └── xiaomi.yaml
│   ├── benchmarks/
│   │   └── benchmarks.yaml         # Benchmark definitions & metadata
│   └── versions/
│       └── YYYY-MM-DD.json         # Auto-generated versioned JSON
├── legacy/
│   └── index.html                  # Retired monolithic dashboard (106K)
├── docs/
│   ├── ADDING_MODELS.md
│   └── wiki/                       # Extended documentation
└── .github/
    ├── workflows/
    │   ├── validate-yaml.yml        # Validates YAML on every push/PR
    │   ├── build-json.yml           # Compiles YAML -> JSON on push to main
    │   ├── deploy-pages.yml         # OIDC deploy to GitHub Pages
    │   └── auto-populate-scores.yml # Weekly cron fetches scores, opens PR
    └── scripts/
        ├── validate_yaml.py
        ├── build_json.py
        └── auto_populate_scores.py
```

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) 20+
- [pnpm](https://pnpm.io/) (recommended) or npm
- Python 3.10+ (for YAML validation and JSON build scripts)

### Install & Run

```bash
pnpm install
pnpm dev          # Hot-reload dev server at localhost:5173
```

### Build for Production

```bash
pnpm build        # Outputs to dist/
pnpm preview      # Preview production build locally
```

### Data Workflow

```bash
# Validate YAML files
python .github/scripts/validate_yaml.py

# Rebuild dashboard.json from YAML
python .github/scripts/build_json.py          # full build
python .github/scripts/build_json.py --dry-run # preview changes
```

## Deployment

Deployed to **GitHub Pages** via OIDC-based `deploy-pages.yml`. On push to `master`/`main` that touches `src/`, `data/dashboard.json`, `public/`, or build config files, the workflow:

1. Checks out the repo
2. Installs dependencies with Bun
3. Runs `vite build`
4. Uploads the `dist/` artifact
5. Deploys to GitHub Pages

## How to Update

### Adding a new model version

1. Open the relevant `data/models/<provider>.yaml`
2. Add a new entry under `models:` with the model ID, release date, scores, and pricing
3. Run `python .github/scripts/validate_yaml.py` to check for errors
4. Run `python .github/scripts/build_json.py` to regenerate the dashboard data
5. Update `CHANGELOG.md` with a new date entry

### Adding a new benchmark

1. Add the benchmark definition to `data/benchmarks/benchmarks.yaml`
2. Add scores to each relevant model in `data/models/*.yaml`
3. If the benchmark should appear in the radar chart, update the axes config in `src/lib/constants.ts`
4. Document the addition in `CHANGELOG.md`

### Example: Adding a new model

```yaml
# In data/models/<provider>.yaml, add under models:
  - id: model-name-version
    name: Model Display Name
    released: 2026-05-XX
    type: proprietary
    context_window: 200k
    pricing:
      input_per_m: 5.00
      output_per_m: 25.00
      cache_per_m: 1.25
    scores:
      intelligence_index: XX
      swe_bench_verified: XX.X
      # ... other benchmark scores (bare number or rich object)
    verification:
      status: verified
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
      cache_per_m: number (USD per 1M cached input tokens)
    architecture:
      total_params: string
      # ... other arch details
    scores:
      <benchmark_id>: number | {value, self_reported, source, notes}
    verification:
      status: string (verified | unverified | partially_verified)
      notes: string
```

Composite pricing (`composite_per_m`) is no longer stored in YAML — it is derived in code from `input_per_m` and `output_per_m`.

## Sources

- [Artificial Analysis](https://artificialanalysis.ai) — Intelligence Index, pricing, speed benchmarks
- [Google DeepMind Model Card](https://deepmind.google/models/model-cards/gemini-3-1-pro/) — Gemini 3.1 Pro benchmarks
- [Anthropic](https://www.anthropic.com/news/claude-opus-4-6) — Claude Opus 4.6 official benchmarks
- [LM Council](https://lmcouncil.ai/benchmarks) — Independent multi-benchmark comparisons
- [Serenities AI](https://serenitiesai.com) — GLM-5.1 analysis
- [BenchLM](https://benchlm.ai) — Cross-model comparisons
- [HuggingFace Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard) — Auto-populate source

## License

Data is compiled from public sources. YAML files and dashboard code are MIT licensed.
