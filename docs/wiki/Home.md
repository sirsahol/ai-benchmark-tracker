# Frontier AI Benchmark Tracker — Wiki

A structured, version-controlled database of frontier AI model benchmark scores.
Maintained by [@sirsahol](https://github.com/sirsahol).

---

## Quick Links

| | |
|---|---|
| **GitHub Pages** | [sirsahol.github.io/ai-benchmark-tracker](https://sirsahol.github.io/ai-benchmark-tracker) |
| **GitHub Repo** | [github.com/sirsahol/ai-benchmark-tracker](https://github.com/sirsahol/ai-benchmark-tracker) |

---

## Wiki Pages

| Page | What it covers |
|------|----------------|
| [Schema Reference](./Schema-Reference.md) | Complete YAML field definitions for models, benchmarks |
| [Adding Models](./Adding-Models.md) | Step-by-step guide to adding a new model or provider |
| [Adding Benchmarks](./Adding-Benchmarks.md) | How to add a new benchmark definition and scores |
| [Verification Guide](./Verification-Guide.md) | When to mark a score as verified, unverified, or partially_verified |
| [Dashboard Guide](./Dashboard-Guide.md) | How the dashboard reads data and what each visualisation shows |
| [Contributing](./Contributing.md) | Commit conventions, PR workflow, CI checks |
| [Changelog](../../CHANGELOG.md) | Full history of updates |

---

## Architecture

Built with **Vite 6** + **Svelte 5** + **TypeScript** + **Chart.js**. Previously a monolithic 106K `index.html` (now retired to `legacy/`), the dashboard is now a proper component-based SPA.

**Data pipeline:** YAML files in `data/models/` are compiled by `build_json.py` into `data/dashboard.json`, which the Svelte app imports at build time.

**Auto-populate:** A weekly GitHub Actions cron fetches scores from free public APIs and opens a pull request for human review.

---

## Repo Structure

```
ai-benchmark-tracker/
├── index.html                        # Vite entry point (thin shell)
├── package.json                      # pnpm, Vite 6, Svelte 5, Chart.js
├── vite.config.ts                    # Build config, path aliases
├── svelte.config.js                  # Svelte compiler options
├── tsconfig.json                     # TypeScript config
├── src/
│   ├── main.ts                       # App bootstrap, CSS imports
│   ├── App.svelte                    # Root Svelte component
│   ├── lib/
│   │   └── constants.ts              # Shared constants
│   ├── stores/
│   │   ├── data.ts                   # Dashboard data store
│   │   ├── filters.ts                # Filter state
│   │   ├── radarSelection.ts         # Radar chart selection
│   │   ├── sort.ts                   # Sort state
│   │   └── theme.ts                  # Dark/light theme
│   └── styles/
│       ├── design-tokens.css         # CSS custom properties
│       ├── theme-dark.css            # Dark mode overrides
│       ├── theme-light.css           # Light mode overrides
│       ├── base.css                  # Reset and global styles
│       └── components.css            # Component-specific styles
├── data/
│   ├── dashboard.json                # Auto-generated — do not edit manually
│   ├── models/                       # One YAML per provider (11 files)
│   ├── benchmarks/
│   │   └── benchmarks.yaml           # Benchmark definitions (16 benchmarks)
│   └── versions/
│       └── YYYY-MM-DD.json           # Auto-generated versioned JSON
├── legacy/
│   └── index.html                    # Retired monolithic dashboard (106K)
├── docs/
│   ├── ADDING_MODELS.md
│   └── wiki/                         # This wiki
└── .github/
    ├── workflows/
    │   ├── validate-yaml.yml          # Validates YAML on every push/PR
    │   ├── build-json.yml             # Compiles YAML -> JSON on push to main
    │   ├── deploy-pages.yml           # OIDC deploy to GitHub Pages
    │   └── auto-populate-scores.yml   # Weekly cron fetches scores, opens PR
    └── scripts/
        ├── validate_yaml.py
        ├── build_json.py
        └── auto_populate_scores.py
```

---

## Design Principles

1. **Source of truth is YAML** — `data/dashboard.json` is always auto-generated from YAML. Never edit it manually.
2. **Per-score provenance** — every score optionally carries `source`, `benchmark_date`, and `notes`. This makes data auditable.
3. **Self-reported scores are flagged** — any score with `self_reported: true` gets an SR badge in the dashboard and cannot be treated as independently verified.
4. **Superseded models are preserved** — old model versions stay in the YAML with `superseded_by:` set. The dashboard can hide or grey them out; the data is never lost.
5. **Tags enable filtering** — models have `tags` like `[fast, coding, open-weight]` for capability-based filtering in the dashboard.
6. **No snapshots** — historical data is preserved via git history and the `data/versions/` directory. Point-in-time snapshots have been dropped.

---

## Current Models Tracked (May 2026)

32 models across 11 providers:

| Provider | Models |
|----------|--------|
| Anthropic | Claude Opus 4.6, Sonnet 4.6, Opus 4.5 |
| Google DeepMind | Gemini 3.1 Pro, Gemini 3 Pro, Gemini 3 Flash |
| OpenAI | GPT-5.4, GPT-5.3 Codex, GPT-5.2, GPT-5.1 |
| Z.ai | GLM-5.1, GLM-5, GLM-4.7 |
| xAI | Grok 4.20 Beta, Grok 4 |
| Meta | Llama 4 Scout, Llama 4 Maverick |
| MiniMax | MiniMax-M2.7, MiniMax-M2.5 |
| Moonshot AI | Kimi K2.5, Kimi K2 |
| DeepSeek | DeepSeek-R2 |
| Mistral | Mistral Large 3 |
| Xiaomi | MiMo |
