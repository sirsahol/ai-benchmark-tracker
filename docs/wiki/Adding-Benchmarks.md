# Adding Benchmarks

## When to Add a New Benchmark

Add a new entry to `data/benchmarks/benchmarks.yaml` when:
- A new evaluation appears on multiple leaderboards and is likely to persist
- You're adding model scores for it and need the key to exist
- The benchmark has a clear, public methodology

Do **not** add benchmarks that are:
- One-off internal evals with no public methodology
- Identical to an existing benchmark (check for aliases first)
- No longer maintained or widely cited

---

## Step-by-Step

### 1 — Add to `data/benchmarks/benchmarks.yaml`

```yaml
benchmarks:
  your_benchmark_key:           # snake_case, e.g. "arc_agi_3" or "swe_bench_pro"
    name: Your Benchmark Name   # REQUIRED — display name in the dashboard
    category: coding            # REQUIRED — see valid categories below
    description: >              # REQUIRED — one clear sentence
      What this benchmark tests and why it matters.
    unit: percent               # REQUIRED — percent | elo | score | points | tps
    higher_is_better: true      # REQUIRED — true | false
    source: Organization Name   # optional — who maintains it
    url: https://example.com    # optional — link to benchmark homepage
    notes: >                    # optional — harness differences, known issues
      Any caveats about how scores were collected or why comparisons may be tricky.
```

### Valid categories

| Category | Use for |
|----------|---------|
| `reasoning` | Abstract reasoning, logic, novel problem-solving (e.g. ARC-AGI-2, HLE) |
| `science` | Graduate-level scientific knowledge (e.g. GPQA Diamond) |
| `coding` | Software engineering, code generation (e.g. SWE-Bench, HumanEval) |
| `math` | Mathematical problem-solving (e.g. FrontierMath, AIME, MATH-500) |
| `knowledge_work` | Professional tasks, legal, financial, office work (e.g. GDPval-AA) |
| `long_context` | Retrieval and reasoning over long contexts (e.g. MRCR v2) |
| `agentic` | Autonomous multi-step task completion (e.g. APEX-Agents, τ-bench) |
| `composite` | Aggregated index scores (e.g. Artificial Analysis Intelligence Index) |

---

### 2 — Add scores to model files

Once the key exists in `benchmarks.yaml`, add scores to the relevant models in `data/models/*.yaml`:

```yaml
# Bare number (verified, no caveats)
your_benchmark_key: 82.5

# Rich object (self-reported or has notes)
your_benchmark_key:
  value: 82.5
  self_reported: false
  benchmark_date: 2026-04-15
  source: "https://example.com/leaderboard"
  notes: "Single-attempt, no tools"
```

---

### 3 — Add to dashboard (if it should appear in charts)

The dashboard reads benchmark categories from the data. To add the benchmark to the **radar chart axes**, edit `index.html` and find the `RADAR_AXES` array:

```javascript
const RADAR_AXES = [
  { key: 'arc_agi_2',         label: 'Reasoning',     max: 100 },
  { key: 'gpqa_diamond',      label: 'Science',        max: 100 },
  // ... existing axes ...
  { key: 'your_benchmark_key', label: 'Your Label',    max: 100 }  // add here
];
```

To add it to the **Benchmark Deep Dive** tabs, find the `BENCHMARK_TABS` config and add it to the appropriate category array.

---

### 4 — Update CHANGELOG.md

```markdown
## [YYYY-MM-DD] — Add <Benchmark Name>

### Added
- `<benchmark_key>` to `data/benchmarks/benchmarks.yaml`
  - Category: <category>
  - Scores added for: <list of models>
```

---

## Benchmark Key Naming Conventions

| Pattern | Example |
|---------|---------|
| Org name + version | `swe_bench_verified`, `swe_bench_pro` |
| Benchmark name + variant | `gpqa_diamond`, `mrcr_v2_128k` |
| Organisation abbreviation | `hle_with_tools`, `hle_no_tools` |
| Composite / index | `intelligence_index`, `coding_index` |

Use **snake_case** only. No hyphens, spaces, or capitals in keys.

---

## Benchmark Harness Caveats

Some benchmarks have multiple harnesses that produce incomparable scores. Always note this in the benchmark definition and in the individual model score:

```yaml
# In benchmarks.yaml
terminal_bench_2:
  notes: >
    Two harnesses in use: Terminus-2 (standard, used by Anthropic and Google)
    and Codex CLI (used by OpenAI for GPT-5.3 Codex — self-reported).
    Scores from different harnesses are NOT directly comparable.

# In model scores
terminal_bench_2:
  value: 77.3
  self_reported: true
  notes: "Codex CLI harness — not comparable to Terminus-2 results"
```
