# Verification Guide

This guide explains when and how to mark scores as verified, self-reported, or somewhere in between.

---

## The Problem

AI providers have strong incentives to publish favorable benchmark numbers. Self-reported scores:
- Often use non-standard or proprietary evaluation harnesses
- Are frequently cherry-picked from the best run or configuration
- Can't be independently audited without the exact methodology

This tracker distinguishes between independently verified and self-reported scores so you can make informed decisions about which numbers to trust.

---

## The Three Levels

### `verified`
**All key scores confirmed by independent third-party evaluators.**

The evaluator re-runs the benchmark themselves using a standard harness, with no provider involvement.

Qualifies as verified:
- [Artificial Analysis](https://artificialanalysis.ai) — Intelligence Index, pricing benchmarks
- [LM Council](https://lmcouncil.ai) — Multi-benchmark independent comparisons
- [ARC Prize](https://arcprize.org) — ARC-AGI-2 scores (they run verification themselves)
- [SWE-bench official leaderboard](https://www.swebench.com) — SWE-Bench Verified
- Official model cards (Google DeepMind, Anthropic) — where scores come from a published, reproducible methodology

Does **not** qualify:
- Provider blog posts or press releases
- Aggregator sites (LLMBase, SiliconFlow, BenchLM) that repost provider numbers
- Comparisons published by the model provider themselves

---

### `partially_verified`
**Mix of verified and self-reported scores.**

Use this when:
- Some scores (e.g. SWE-Bench, GPQA) are from verified sources
- Others (e.g. a custom coding eval, an internal RAG benchmark) are self-reported
- Scores come from aggregators whose primary source is the provider

---

### `unverified`
**All scores from provider announcement only.**

Use this for:
- Newly released models where independent evaluators haven't published yet
- Models where all published benchmarks use proprietary harnesses
- Self-reported scores on non-standard benchmarks (e.g. GLM-5.1's Claude Code eval)

**Unverified ≠ wrong.** It means "not yet independently confirmed." Update to `partially_verified` or `verified` as third-party results arrive.

---

## The `self_reported` Per-Score Flag

Even within a `partially_verified` model, individual scores can be flagged:

```yaml
scores:
  swe_bench_verified: 77.8          # independently verified — bare number is fine
  coding_eval_claude_code:
    value: 45.3
    self_reported: true             # ← this score is provider-only
    source: "https://z.ai/..."
    notes: "Non-standard Claude Code harness"
```

This gives **per-score transparency** — the dashboard renders an `SR` badge on self-reported cells.

### When to set `self_reported: true`

- The score appears only in the provider's own announcement or blog post
- The benchmark uses a custom/proprietary harness that others can't replicate
- The methodology hasn't been published

### Always include `source` when `self_reported: true`

The source URL is how anyone can trace the claim back to its origin. It's required — the CI validator will warn if it's missing.

---

## Updating Verification Status

When an independent evaluation is published for a previously unverified model:

1. Update `verification.status` in the model YAML
2. Update individual scores that are now verified — switch from rich object to bare number, or update `self_reported: false`
3. Add the source to `verification.notes`
4. Update `CHANGELOG.md`

Example:

```yaml
# Before (unverified)
verification:
  status: unverified
  notes: "Self-reported by Z.ai March 27"

# After (once Artificial Analysis publishes)
verification:
  status: partially_verified
  notes: "Intelligence Index verified by Artificial Analysis (April 2026). Coding eval (45.3) still pending independent verification."
```

---

## Reference: Trusted Third-Party Sources

| Source | What they measure | URL |
|--------|------------------|-----|
| Artificial Analysis | Intelligence Index, pricing, speed | artificialanalysis.ai |
| LM Council | Multi-benchmark, Epoch/Scale AI methodology | lmcouncil.ai |
| ARC Prize | ARC-AGI-2 only | arcprize.org |
| SWE-bench | SWE-Bench Verified, SWE-Bench Pro | swebench.com |
| Vellum AI | LiveCodeBench, IFEval, SWE-Bench | vellum.ai/llm-leaderboard |
| Onyx | Open-source leaderboards | onyx.app/llm-leaderboard |
| LM Arena (LMSYS) | Chatbot Arena Elo (human preference) | lmarena.ai |
