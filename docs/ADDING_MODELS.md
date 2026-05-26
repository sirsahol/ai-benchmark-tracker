# Adding Models

## Quickstart

1. Open (or create) `data/models/<provider>.yaml`
2. Add a new entry under `models:`
3. Run the validator locally: `python .github/scripts/validate_yaml.py`
4. Run the builder locally: `python .github/scripts/build_json.py`
5. Commit — CI will re-validate and rebuild JSON automatically

---

## Step-by-Step

### 1. Find the right provider file

| Provider | File |
|----------|------|
| Anthropic | `data/models/anthropic.yaml` |
| Google DeepMind | `data/models/google.yaml` |
| OpenAI | `data/models/openai.yaml` |
| Z.ai (GLM) | `data/models/zai.yaml` |
| xAI (Grok) | `data/models/xai.yaml` |
| Meta (Llama) | `data/models/meta.yaml` |
| MiniMax | `data/models/minimax.yaml` |
| Moonshot (Kimi) | `data/models/moonshot.yaml` |
| DeepSeek | `data/models/deepseek.yaml` |
| Mistral | `data/models/mistral.yaml` |
| Xiaomi | `data/models/xiaomi.yaml` |

If the provider doesn't exist yet, see [Adding a Provider](#adding-a-new-provider).

---

### 2. Add the model entry

Copy this template and fill in what you know. Leave unknown fields as `null` — don't omit required fields.

```yaml
  - id: <provider>-<version>          # e.g. claude-opus-4.7, gemini-3.2-pro
    name: <Display Name>              # e.g. Claude Opus 4.7
    released: YYYY-MM-DD             # ISO 8601 date
    type: proprietary                 # proprietary | open-source
    context_window: 200k             # e.g. 1M, 200k, 128k, 10M
    max_output: 128k                 # optional, output token ceiling
    pricing:
      input_per_m: 5.00              # USD per 1M input tokens (null if unknown)
      output_per_m: 25.00            # USD per 1M output tokens
      cache_per_m: 1.25              # USD per 1M cached input tokens (null if N/A)
    architecture:
      total_params: 744B             # optional
      architecture: MoE              # optional: MoE | Dense
      experts_total: 256             # optional, MoE only
      experts_active: 8              # optional, MoE only
      training_hardware: null        # optional, e.g. "NVIDIA H100" or "Huawei Ascend 910B"
      notes: ""                      # any notable architecture facts
    scores:
      # Use the benchmark keys from data/benchmarks/benchmarks.yaml
      # Values can be bare numbers or rich objects — see Score Format below
      intelligence_index: null
      arc_agi_2: null
      gpqa_diamond: null
      swe_bench_verified: null
      swe_bench_pro: null
      terminal_bench_2: null
      hle_with_tools: null
      frontier_math: null
      gdpval_aa_elo: null
      browsecomp: null
      livecode_bench_elo: null
      mrcr_v2_128k: null
      chatbot_arena_elo: null
      webarena: null
      aitnt_arena_elo: null
      biglaw_bench: null
    verification:
      status: unverified             # verified | unverified | partially_verified
      notes: "Source and date of any independent verification"
    sources:
      - https://example.com/model-card
```

**Required fields:** `id`, `name`, `released`, `type`, `context_window`
**Recommended fields:** `pricing`, `scores`

---

### 3. Score Format

Scores support two formats. **Both are valid** and the build script handles both.

**Bare number** (concise, for verified scores with no caveats):

```yaml
scores:
  gpqa_diamond: 94.3
  swe_bench_verified: 80.6
```

**Rich object** (for self-reported scores or scores with provenance):

```yaml
scores:
  gpqa_diamond:
    value: 94.3                     # REQUIRED — the numeric score (or null)
    self_reported: false            # optional, default false
    benchmark_date: 2026-02-19      # optional — when the score was recorded
    source: "https://..."           # optional — URL to the source
    notes: "Thinking High mode"     # optional — harness/methodology caveats
```

**Rule:** Any `self_reported: true` score **must** include a `source` URL.

---

### 4. Set verification status correctly

| Status | When to use |
|--------|-------------|
| `verified` | Score confirmed by an independent third-party evaluator (Artificial Analysis, LM Council, SWE-bench official leaderboard, ARC Prize, etc.) |
| `partially_verified` | Some scores verified, others self-reported or from aggregators |
| `unverified` | Score is only from the provider's own announcement / blog post |

Always add a `notes` field explaining which scores are verified and by whom.

---

### 5. Update the benchmark definitions (if needed)

If you're adding scores for a benchmark not yet in `data/benchmarks/benchmarks.yaml`, add it there first. See [ADDING_BENCHMARKS.md](./ADDING_BENCHMARKS.md).

---

### 6. Rebuild and test

```bash
python .github/scripts/validate_yaml.py    # Validate
python .github/scripts/build_json.py        # Rebuild dashboard.json
pnpm dev                                    # Test locally at localhost:5173
```

---

### 7. Update CHANGELOG.md

```markdown
## [YYYY-MM-DD] — Add <Model Name>

### Added
- <Model Name> to `data/models/<provider>.yaml`
  - Intelligence Index: XX
  - Notable: <one key fact>

### Sources
- <link to model card or announcement>
```

---

## Adding a New Provider

1. Create `data/models/<provider-slug>.yaml`
2. Use this header:

```yaml
provider:
  name: Provider Display Name
  brand_color: "#RRGGBB"   # hex, used for chart colors and row tinting
  website: https://example.com

models: []
```

3. The `brand_color` and `website` fields are **required** for new providers — the dashboard uses them for chart coloring and provider links.

---

## Pricing Notes

- Pricing uses three fields: `input_per_m`, `output_per_m`, and `cache_per_m`
- `composite_per_m` is **no longer stored** in YAML — it is derived in code as a weighted blend of input and output pricing
- If cache pricing is not available, set `cache_per_m: null` or omit it
- All values are in USD per 1M tokens

---

## Dropped Benchmarks

The following benchmarks have been removed and should not be used in new model entries:

- `coding_eval_claude_code` — dropped (replaced by more general coding benchmarks)

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Score as a string: `"80.8%"` | Use a bare number: `80.8` |
| Missing `released` date | Use best-known date; if unknown use first day of known month |
| `type: open source` | Must be `open-source` (hyphenated) or `proprietary` |
| Omitting `verification.status` for new models | Always include it — default to `unverified` if unsure |
| Benchmark key typo | Check against `data/benchmarks/benchmarks.yaml` for exact keys |
| Including `composite_per_m` in pricing | Remove it — it's derived in code, not stored in YAML |
| Adding `coding_eval_claude_code` scores | This benchmark has been dropped — use `swe_bench_verified` or `terminal_bench_2` instead |
