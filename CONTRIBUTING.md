# Contributing to Frontier AI Benchmark Tracker

## Quick Guide

### Adding New Benchmark Scores

1. Find the provider YAML file in `data/models/<provider>.yaml`
2. Add or update scores under the relevant model's `scores:` section
3. Use the benchmark ID from `data/benchmarks/benchmarks.yaml`
4. If the score is self-reported and unverified, add a `verification:` section

### Adding a New Provider

1. Create `data/models/<provider>.yaml`
2. Follow the schema in `docs/wiki/Schema-Reference.md`
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

### Updating the Dashboard

The dashboard is built with Vite 6 + Svelte 5. The data pipeline:

```
data/models/*.yaml  -->  build_json.py  -->  data/dashboard.json  -->  static import in Svelte
```

Edit YAML files, run `build_json.py`, then the Svelte components pick up the new data automatically.

## Verification Status

All scores should have verification status:

- `verified` — Independently confirmed by third-party evaluators
- `unverified` — Self-reported by the model provider only
- `partially_verified` — Some scores verified, others pending

Always note the verification source and date.

## Local Development

### Prerequisites

- [Node.js](https://nodejs.org/) 20+
- [pnpm](https://pnpm.io/) (recommended) or npm
- Python 3.10+ (for data scripts)

### Install & Run

```bash
pnpm install
pnpm dev              # Hot-reload dev server at localhost:5173
```

### Validate YAML

```bash
python .github/scripts/validate_yaml.py
```

Checks all `data/models/*.yaml` and `data/benchmarks/benchmarks.yaml` for schema compliance. Exits 1 on errors.

### Build JSON

```bash
# Dry run — prints what would be written
python .github/scripts/build_json.py --dry-run

# Full build
python .github/scripts/build_json.py
```

Writes `data/dashboard.json` and `data/versions/YYYY-MM-DD.json`.

### Build for Production

```bash
pnpm build            # Outputs to dist/
pnpm preview          # Preview production build locally
```

## Data Changes

When changing data (scores, models, benchmarks):

1. Edit the relevant YAML file(s) in `data/models/` or `data/benchmarks/`
2. Run `python .github/scripts/validate_yaml.py` to check for errors
3. Run `python .github/scripts/build_json.py` to regenerate `data/dashboard.json`
4. Test locally with `pnpm dev`
5. Commit — CI will re-validate and rebuild JSON automatically

## Component Changes

When editing the dashboard UI:

1. Edit Svelte components in `src/` (App.svelte, stores, styles)
2. Run `pnpm dev` for hot-reload during development
3. Run `pnpm build` to verify the production build passes
4. Commit — CI will deploy to GitHub Pages on merge to `master`/`main`

## CI Checks

Four GitHub Actions workflows:

| Workflow | File | Triggers on |
|----------|------|-------------|
| **Validate YAML** | `.github/workflows/validate-yaml.yml` | Push/PR touching `data/**/*.yaml` |
| **Build JSON** | `.github/workflows/build-json.yml` | Push to `main`/`master` touching `data/**/*.yaml` |
| **Deploy Pages** | `.github/workflows/deploy-pages.yml` | Push to `main`/`master` touching `src/`, `data/dashboard.json`, build config |
| **Auto-Populate** | `.github/workflows/auto-populate-scores.yml` | Weekly cron (Monday 03:00 UTC) + manual |

The validate workflow **blocks merges** on errors. The build workflow auto-commits the regenerated JSON. The deploy workflow builds the Vite app and deploys to GitHub Pages via OIDC.

If the build workflow commits back to `main`, it uses `[skip ci]` in the commit message to prevent infinite loops.

## Data Integrity Rules

1. **Never edit `data/dashboard.json` manually** — it's auto-generated
2. **Never delete model entries** — use `superseded_by` to mark old models
3. **Always include `source` for self-reported scores** — `self_reported: true` without `source` fails validation
4. **Scores are numbers, not strings** — `80.8` not `"80.8%"`
5. **Dates are YYYY-MM-DD** — `2026-02-19` not `Feb 19, 2026`
6. **Keep benchmark keys consistent** — check `data/benchmarks/benchmarks.yaml` before adding new score keys to model files
7. **Pricing uses input_per_m / output_per_m / cache_per_m** — `composite_per_m` is derived in code, not stored

## PR Checklist

Before opening a PR:

- [ ] `python .github/scripts/validate_yaml.py` passes with no errors
- [ ] `python .github/scripts/build_json.py --dry-run` shows expected output
- [ ] `data/dashboard.json` rebuilt locally (or CI will do it)
- [ ] `pnpm build` succeeds with no errors
- [ ] `CHANGELOG.md` updated
- [ ] Commit message follows the format below

## Commit Messages

Use this format:
```
[model-id] Add/Update <benchmark> scores
[benchmark] Add <benchmark-name> definition
[dashboard] Description of dashboard change
[ci] Description of CI/tooling change
[docs] Description of documentation change
[fix] Description of data fix
[auto] Automated score update from public APIs
```
