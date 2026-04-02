# Adding Models

## TL;DR Checklist

- [ ] Find or create `data/models/<provider>.yaml`
- [ ] Add model entry with all required fields
- [ ] Use rich score format for self-reported scores (`self_reported: true`)
- [ ] Set `verification.status` correctly
- [ ] Set `superseded_by` on any model this replaces
- [ ] Run `python .github/scripts/validate_yaml.py` locally
- [ ] Run `python .github/scripts/build_json.py --dry-run` locally
- [ ] Create or update `data/snapshots/YYYY-MM-DD.yaml`
- [ ] Update `CHANGELOG.md`
- [ ] Commit with `[model-id] Add/Update <model>` message

---

## Step 1 — Find the right file

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

New provider? See [New Provider](#adding-a-new-provider) below.

---

## Step 2 — Add the model entry

Minimum required fields:

```yaml
  - id: provider-model-version      # e.g. claude-opus-4.7, gemini-3.2-pro
    name: Display Name              # e.g. Claude Opus 4.7
    released: YYYY-MM-DD
    type: proprietary               # or open-source
    context_window: 200k            # e.g. 1M, 128k, 10M
    verification:
      status: unverified            # always start here until confirmed
      notes: "Self-reported. Source: <url>"
```

Full template with all fields:

```yaml
  - id: <provider>-<model>-<version>
    name: <Display Name>
    released: YYYY-MM-DD
    type: proprietary               # or open-source
    context_window: 200k
    max_output: 128k                # optional
    superseded_by: <model-id>       # only if this model replaces another
    tags: [flagship, coding, agentic]
    pricing:
      input_per_m: 5.00
      output_per_m: 25.00
      notes: ""
    architecture:
      total_params: 744B
      architecture: MoE
      experts_total: 256
      experts_active: 8
      training_hardware: "NVIDIA H100"
      notes: ""
    scores:
      # Bare number — fully verified, no caveats
      gpqa_diamond: 94.3
      # Rich object — self-reported or has methodology notes
      terminal_bench_2:
        value: 68.5
        self_reported: false
        benchmark_date: 2026-02-19
        source: "https://deepmind.google/models/model-cards/gemini-3-1-pro/"
        notes: "Terminus-2 harness"
      coding_eval_custom:
        value: 45.3
        self_reported: true
        benchmark_date: 2026-03-27
        source: "https://provider.com/announcement"
        notes: "Non-standard harness — not comparable to SWE-Bench"
    verification:
      status: unverified            # verified | unverified | partially_verified
      notes: "All scores self-reported. Independent evaluation pending."
    sources:
      - https://provider.com/model-card
```

---

## Step 3 — Choosing score format

Use **bare number** when:
- The score is independently verified
- No harness or methodology caveats
- Source is obvious (official model card from a trusted evaluator)

Use **rich object** when:
- `self_reported: true` — required in this case
- The benchmark used a non-standard harness (e.g. Codex CLI vs Terminus-2)
- The score was recorded on a specific date you want to track
- You have a specific source URL

**Never omit `source` when `self_reported: true`.**

---

## Step 4 — Set verification status

| Status | Use when |
|--------|----------|
| `verified` | All key scores confirmed by Artificial Analysis, LM Council, ARC Prize, or official leaderboards |
| `partially_verified` | Mix of verified + self-reported/aggregator scores |
| `unverified` | Only provider announcement — no third-party confirmation yet |

New models should almost always start as `unverified`. Update to `partially_verified` or `verified` once third-party results land.

---

## Step 5 — Mark superseded models

If the new model replaces an existing one, add `superseded_by` to the **old** model:

```yaml
  - id: claude-opus-4.5
    name: Claude Opus 4.5
    superseded_by: claude-opus-4.6   # ← add this
    ...
```

Do **not** delete old model entries. History is preserved.

---

## Step 6 — Run checks locally

```bash
# Validate all YAML files
python .github/scripts/validate_yaml.py

# Dry-run the JSON build (see what would be written)
python .github/scripts/build_json.py --dry-run

# Full build (writes data/dashboard.json and data/versions/YYYY-MM-DD.json)
python .github/scripts/build_json.py
```

Requires: `pip install pyyaml`

---

## Step 7 — Create a snapshot

When the leaderboard changes materially (new model in top 10, category winner changes):

```bash
cp data/snapshots/2026-04-02.yaml data/snapshots/$(date +%Y-%m-%d).yaml
# Edit to reflect current leaderboard and category_winners
```

---

## Step 8 — Update CHANGELOG.md

```markdown
## [YYYY-MM-DD] — Add <Model Name>

### Added
- `<model-id>` to `data/models/<provider>.yaml`
  - Intelligence Index: XX (verified/unverified)
  - Key scores: SWE-Bench XX%, GPQA XX%
  - Notable: <one-liner about what makes this model different>

### Sources
- [Official model card](<url>)
```

---

## Adding a New Provider

1. Create `data/models/<slug>.yaml` where `<slug>` is lowercase-hyphenated, e.g. `mistral.yaml`

2. Add the provider header:
```yaml
provider:
  name: Mistral AI
  brand_color: "#FF7000"   # brand hex — check official brand guidelines
  website: https://mistral.ai

models: []
```

3. Add the provider color to `index.html` in the `PROVIDER_COLORS` object:
```javascript
const PROVIDER_COLORS = {
  // ... existing entries ...
  mistral: { primary: '#FF7000', light: '#FF700022' }
};
```

4. Add a simple SVG icon to the `PROVIDER_LOGOS` object in `index.html`.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Score as string: `"80.8%"` | Use bare number: `80.8` |
| `self_reported: true` without `source` | Always include `source` URL |
| `type: open source` | Must be `open-source` (hyphenated) |
| Hardcoding composite price as `input_per_m` | Use `composite_per_m` when input/output aren't split |
| Deleting old model entries | Use `superseded_by` instead — never delete |
| Forgetting to run validator | CI will catch it, but run locally first to save a CI round-trip |
