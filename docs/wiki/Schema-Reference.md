# Schema Reference

Schema version: **3** (introduced April 2, 2026)

---

## Model File (`data/models/<provider>.yaml`)

### Provider block

```yaml
provider:
  name: string            # REQUIRED — display name, e.g. "Google DeepMind"
  brand_color: string     # REQUIRED — hex color (#RGB or #RRGGBB), used for charts
  website: string         # REQUIRED — canonical URL
  notes: string           # optional — any provider-level context
```

### Model entry

```yaml
models:
  - id: string                  # REQUIRED — kebab-case unique ID, e.g. "claude-opus-4.6"
    name: string                # REQUIRED — display name
    released: YYYY-MM-DD        # REQUIRED — ISO 8601 release date
    type: string                # REQUIRED — "proprietary" | "open-source"
    context_window: string      # REQUIRED — e.g. "1M", "200k", "128k", "10M"
    max_output: string          # optional — output token ceiling, e.g. "128k"
    superseded_by: string       # optional — id of the newer model that replaces this one
    tags: [string]              # optional — capability tags, see Tags Reference below
    pricing:
      input_per_m: number       # USD per 1M input tokens
      output_per_m: number      # USD per 1M output tokens
      cache_per_m: number       # USD per 1M cached input tokens
      notes: string             # optional — pricing caveats
    architecture:
      total_params: string      # optional — e.g. "744B"
      architecture: string      # optional — "MoE" | "Dense"
      experts_total: number     # optional — MoE only
      experts_active: number    # optional — MoE only
      active_params: string     # optional — active params per token, e.g. "~40–44B"
      training_hardware: string # optional — e.g. "NVIDIA H100" or "Huawei Ascend 910B"
      training_data_tokens: string # optional — e.g. "28.5T"
      attention: string         # optional — attention mechanism notes
      notes: string             # optional — architecture summary
    scores:
      <benchmark_id>: <score>   # see Score Format below
    verification:
      status: string            # "verified" | "unverified" | "partially_verified"
      notes: string             # explain what is/isn't verified and by whom
    sources:
      - string                  # optional list of URLs for this model's data
```

**Note on pricing:** The `composite_per_m` field is no longer stored in YAML. It is derived in code as a weighted blend of `input_per_m` and `output_per_m`. Only `input_per_m`, `output_per_m`, and `cache_per_m` are stored.

---

## Score Format

Scores support two formats. **Both are valid** and the build script handles both.

### Format 1 — Bare number (concise, for fully-verified scores)

```yaml
scores:
  gpqa_diamond: 94.3
  swe_bench_verified: 80.6
```

### Format 2 — Rich object (full provenance)

```yaml
scores:
  gpqa_diamond:
    value: 94.3                     # REQUIRED — the numeric score (or null)
    self_reported: false            # optional, default false
    benchmark_date: 2026-02-19      # optional — YYYY-MM-DD when the score was recorded
    source: "https://..."           # optional — URL to the source
    notes: "Thinking High mode"     # optional — harness/methodology caveats
```

### When to use each format

| Use bare number when | Use rich object when |
|---|---|
| Score is independently verified | Score is self-reported (`self_reported: true`) |
| Source is obvious (official model card) | Harness differs from standard (e.g. Codex CLI vs Terminus-2) |
| No methodology caveats | Score was recorded on a specific date worth tracking |
| Adding a quick update | Source URL is not obvious |

**Rule:** Any `self_reported: true` score **must** include a `source` URL.

---

## Benchmark File (`data/benchmarks/benchmarks.yaml`)

```yaml
benchmarks:
  <benchmark_id>:               # snake_case key, e.g. "swe_bench_verified"
    name: string                # REQUIRED — display name, e.g. "SWE-Bench Verified"
    category: string            # REQUIRED — see valid categories below
    description: string         # REQUIRED — one-sentence description
    unit: string                # REQUIRED — "percent" | "elo" | "score" | "points" | "tps"
    higher_is_better: boolean   # REQUIRED — true | false
    source: string              # optional — benchmark maintainer
    url: string                 # optional — link to benchmark page
    notes: string               # optional — known caveats (harness differences, etc.)
```

### Valid categories

`reasoning` · `science` · `coding` · `math` · `knowledge_work` · `long_context` · `agentic` · `composite`

### Current benchmarks (16)

| Key | Name | Category | Unit |
|-----|------|----------|------|
| `arc_agi_2` | ARC-AGI-2 | reasoning | percent |
| `hle_with_tools` | Humanity's Last Exam (with tools) | reasoning | percent |
| `gpqa_diamond` | GPQA Diamond | science | percent |
| `swe_bench_verified` | SWE-Bench Verified | coding | percent |
| `swe_bench_pro` | SWE-Bench Pro | coding | percent |
| `terminal_bench_2` | Terminal-Bench 2.0 | coding | percent |
| `livecode_bench_elo` | LiveCodeBench Pro | coding | elo |
| `frontier_math` | FrontierMath | math | percent |
| `gdpval_aa_elo` | GDPval-AA Elo | knowledge_work | elo |
| `browsecomp` | BrowseComp | knowledge_work | percent |
| `biglaw_bench` | BigLaw Bench | knowledge_work | percent |
| `mrcr_v2_128k` | MRCR v2 (8-needle 128k) | long_context | percent |
| `webarena` | WebArena | agentic | percent |
| `intelligence_index` | Artificial Analysis Intelligence Index | composite | score |
| `chatbot_arena_elo` | Chatbot Arena Elo | composite | elo |
| `aitnt_arena_elo` | AiTNt Arena Elo | composite | elo |

### Dropped benchmarks

| Key | Reason |
|-----|--------|
| `coding_eval_claude_code` | Replaced by more general coding benchmarks |

---

## Tags Reference

Tags are free-form lowercase strings on model entries. Common ones:

| Tag | Meaning |
|-----|---------|
| `flagship` | Provider's current top-tier model |
| `coding` | Optimised for or particularly strong at coding tasks |
| `agentic` | Strong at multi-step autonomous task completion |
| `fast` | Notably high tokens/second |
| `efficient` | High performance relative to cost |
| `long-context` | 1M+ token context support |
| `open-weight` | Weights publicly available |
| `reasoning` | Particularly strong on abstract/scientific reasoning |
| `multimodal` | Handles image/video/audio input |
| `math` | Strong on mathematical benchmarks |
| `knowledge-work` | Strong on GDPval-AA / professional tasks |
| `self-improving` | Autonomously updates its own capabilities |

---

## Verification Status Reference

| Status | Definition | Dashboard display |
|--------|------------|-------------------|
| `verified` | All key scores confirmed by an independent third-party evaluator | Green dot |
| `partially_verified` | Some scores independently confirmed; others self-reported or from aggregators | Amber dot |
| `unverified` | All scores from provider's own announcement only | Red dot + badge |

**Third-party evaluators that qualify as "verified":**
- [Artificial Analysis](https://artificialanalysis.ai) — Intelligence Index, pricing, speed
- [LM Council](https://lmcouncil.ai) — Multiple benchmarks with methodology docs
- [ARC Prize](https://arcprize.org) — ARC-AGI-2
- [SWE-bench official leaderboard](https://www.swebench.com)
- [Google DeepMind Model Card](https://deepmind.google/models/model-cards/) — for Gemini models
- [Anthropic official releases](https://www.anthropic.com/news)

Aggregator sites (LLMBase, SiliconFlow, BenchLM) are **not** independent evaluators — use `partially_verified` when relying on them.
