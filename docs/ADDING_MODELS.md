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
    architecture:
      total_params: 744B             # optional
      architecture: MoE              # optional: MoE | Dense
      experts_total: 256             # optional, MoE only
      experts_active: 8              # optional, MoE only
      training_hardware: null        # optional, e.g. "NVIDIA H100" or "Huawei Ascend 910B"
      notes: ""                      # any notable architecture facts
    scores:
      # Use the benchmark keys from data/benchmarks/benchmarks.yaml
      # All values must be numbers or null — never strings
      intelligence_index: null
      arc_agi_2: null
      gpqa_diamond: null
      swe_bench_verified: null
      terminal_bench_2: null
      hle_with_tools: null
      frontier_math: null
      gdpval_aa_elo: null
      browsecomp: null
      livecode_bench_elo: null
      mrcr_v2_128k: null
    verification:
      status: unverified             # verified | unverified | partially_verified
      notes: "Source and date of any independent verification"
    sources:
      - https://example.com/model-card
```

**Required fields:** `id`, `name`, `released`, `type`, `context_window`
**Recommended fields:** `pricing`, `scores`

---

### 3. Set verification status correctly

| Status | When to use |
|--------|-------------|
| `verified` | Score confirmed by an independent third-party evaluator (Artificial Analysis, LM Council, SWE-bench official leaderboard, ARC Prize, etc.) |
| `partially_verified` | Some scores verified, others self-reported or from aggregators |
| `unverified` | Score is only from the provider's own announcement / blog post |

Always add a `notes` field explaining which scores are verified and by whom.

---

### 4. Update the benchmark definitions (if needed)

If you're adding scores for a benchmark not yet in `data/benchmarks/benchmarks.yaml`, add it there first. See [ADDING_BENCHMARKS.md](./ADDING_BENCHMARKS.md).

---

### 5. Add a snapshot

After a significant model addition or update, create a dated snapshot:

```bash
cp data/snapshots/2026-04-02.yaml data/snapshots/$(date +%Y-%m-%d).yaml
# Edit the new file — update the leaderboard and category_winners
```

---

### 6. Update CHANGELOG.md

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

3. Add the provider's brand color to `index.html` in the `PROVIDER_COLORS` object.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Score as a string: `"80.8%"` | Use a bare number: `80.8` |
| Missing `released` date | Use best-known date; if unknown use first day of known month |
| `type: open source` | Must be `open-source` (hyphenated) or `proprietary` |
| Omitting `verification.status` for new models | Always include it — default to `unverified` if unsure |
| Benchmark key typo | Check against `data/benchmarks/benchmarks.yaml` for exact keys |
