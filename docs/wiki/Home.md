# Frontier AI Benchmark Tracker — Wiki

A structured, version-controlled database of frontier AI model benchmark scores.
Maintained by [@sirsahol](https://github.com/sirsahol).

---

## Quick Links

| | |
|---|---|
| **Live Dashboard** | [perplexity.ai/computer/a/frontier-ai-benchmark-tracker-HND2tHqjQrGSQ9_6w4CDsw](https://www.perplexity.ai/computer/a/frontier-ai-benchmark-tracker-HND2tHqjQrGSQ9_6w4CDsw) |
| **GitHub Pages** | [sirsahol.github.io/ai-benchmark-tracker](https://sirsahol.github.io/ai-benchmark-tracker) |
| **GitHub Repo** | [github.com/sirsahol/ai-benchmark-tracker](https://github.com/sirsahol/ai-benchmark-tracker) |

---

## Wiki Pages

| Page | What it covers |
|------|----------------|
| [Schema Reference](./Schema-Reference.md) | Complete YAML field definitions for models, benchmarks, snapshots |
| [Adding Models](./Adding-Models.md) | Step-by-step guide to adding a new model or provider |
| [Adding Benchmarks](./Adding-Benchmarks.md) | How to add a new benchmark definition and scores |
| [Verification Guide](./Verification-Guide.md) | When to mark a score as verified, unverified, or partially_verified |
| [Dashboard Guide](./Dashboard-Guide.md) | How the dashboard reads data and what each visualisation shows |
| [Contributing](./Contributing.md) | Commit conventions, PR workflow, CI checks |
| [Changelog](../../CHANGELOG.md) | Full history of updates |

---

## Repo Structure

```
ai-benchmark-tracker/
├── index.html                        # Interactive dashboard (self-contained)
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── data/
│   ├── dashboard.json                # Auto-generated — do not edit manually
│   ├── models/                       # One YAML per provider
│   │   ├── anthropic.yaml
│   │   ├── google.yaml
│   │   ├── openai.yaml
│   │   ├── zai.yaml
│   │   ├── xai.yaml
│   │   ├── meta.yaml
│   │   ├── minimax.yaml
│   │   └── moonshot.yaml
│   ├── benchmarks/
│   │   └── benchmarks.yaml           # Benchmark definitions
│   ├── snapshots/
│   │   └── YYYY-MM-DD.yaml           # Leaderboard snapshots
│   └── versions/
│       └── YYYY-MM-DD.json           # Auto-generated versioned JSON
├── docs/
│   └── wiki/                         # This wiki
└── .github/
    ├── workflows/
    │   ├── validate-yaml.yml         # Validates YAML on every push
    │   └── build-json.yml            # Compiles YAML → JSON on push to main
    └── scripts/
        ├── validate_yaml.py
        └── build_json.py
```

---

## Design Principles

1. **Source of truth is YAML** — `data/dashboard.json` is always auto-generated from YAML. Never edit it manually.
2. **Per-score provenance** — every score optionally carries `source`, `benchmark_date`, and `notes`. This makes data auditable.
3. **Self-reported scores are flagged** — any score with `self_reported: true` gets an SR badge in the dashboard and cannot be treated as independently verified.
4. **Superseded models are preserved** — old model versions stay in the YAML with `superseded_by:` set. The dashboard can hide or grey them out; the data is never lost.
5. **Tags enable filtering** — models have `tags` like `[fast, coding, open-weight]` for capability-based filtering in the dashboard.

---

## Current Models Tracked (April 2026)

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
