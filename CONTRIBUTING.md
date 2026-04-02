# Contributing to Frontier AI Benchmark Tracker

## Quick Guide

### Adding New Benchmark Scores

1. Find the provider YAML file in `data/models/<provider>.yaml`
2. Add or update scores under the relevant model's `scores:` section
3. Use the benchmark ID from `data/benchmarks/benchmarks.yaml`
4. If the score is self-reported and unverified, add a `verification:` section

### Adding a New Provider

1. Create `data/models/<provider>.yaml`
2. Follow the schema in README.md
3. Include provider metadata (name, brand_color, website)

### Adding a New Benchmark

1. Add the definition to `data/benchmarks/benchmarks.yaml` with:
   - Unique key (snake_case)
   - Display name
   - Category
   - Description
   - Unit (percent, elo, score, points)
   - Source URL
2. Add scores to all relevant models in `data/models/*.yaml`

### Creating a Snapshot

When there's a significant leaderboard change (new model release, major benchmark update):

1. Create `data/snapshots/YYYY-MM-DD.yaml`
2. Include the full leaderboard ranking and category winners at that date
3. Add notes explaining what changed

### Updating the Dashboard

The dashboard (`index.html`) reads data from embedded JSON. When updating YAML files, the dashboard JSON should be updated separately to match. Future versions will auto-compile YAML → JSON.

## Verification Status

All scores should have verification status:

- `verified` — Independently confirmed by third-party evaluators
- `unverified` — Self-reported by the model provider only
- `partially_verified` — Some scores verified, others pending

Always note the verification source and date.

## Commit Messages

Use this format:
```
[model-id] Add/Update <benchmark> scores
[snapshot] Add YYYY-MM-DD snapshot
[benchmark] Add <benchmark-name> definition
[dashboard] Update dashboard with new data
```
