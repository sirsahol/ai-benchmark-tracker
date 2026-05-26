# Contributing

## Types of Contributions

| Type | What to do |
|------|------------|
| Add a new model | See [Adding Models](./Adding-Models.md) |
| Add a new benchmark | See [Adding Benchmarks](./Adding-Benchmarks.md) |
| Update an existing score | Edit the score in the model YAML, update CHANGELOG |
| Update verification status | Edit `verification.status` + `notes` in model YAML |
| Fix a typo or data error | Direct commit to `master` is fine for trivial fixes |
| Dashboard UI change | Edit files in `src/`, test with `pnpm dev`, open PR |
| Add a new CI check | Edit `.github/scripts/validate_yaml.py` |

---

## Commit Message Format

```
[model-id] Action description

[benchmark] Add benchmark-name definition
[dashboard] Description of dashboard change
[ci] Description of CI/tooling change
[docs] Description of documentation change
[fix] Description of data fix
[auto] Automated score update from public APIs
```

Examples:
```
[gemini-3.1-pro] Add SWE-Bench Pro and WebArena scores
[benchmark] Add swe_bench_pro benchmark definition
[dashboard] Add agentic benchmark category to radar chart
[ci] Fix date validation regex in validate_yaml.py
[fix] Correct DeepSeek-R2 SWE-Bench score (72.4 → 73.1)
[auto] Weekly score update from HuggingFace and Artificial Analysis
```

---

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

Checks all `data/models/*.yaml`, `data/benchmarks/benchmarks.yaml` for schema compliance. Exits 1 on errors.

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

---

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

---

## Data Integrity Rules

1. **Never edit `data/dashboard.json` manually** — it's auto-generated
2. **Never delete model entries** — use `superseded_by` to mark old models
3. **Always include `source` for self-reported scores** — `self_reported: true` without `source` fails validation
4. **Scores are numbers, not strings** — `80.8` not `"80.8%"`
5. **Dates are YYYY-MM-DD** — `2026-02-19` not `Feb 19, 2026`
6. **Keep benchmark keys consistent** — check `data/benchmarks/benchmarks.yaml` before adding new score keys to model files
7. **Pricing uses input_per_m / output_per_m / cache_per_m** — `composite_per_m` is derived in code, not stored

---

## PR Checklist

Before opening a PR:

- [ ] `python .github/scripts/validate_yaml.py` passes with no errors
- [ ] `python .github/scripts/build_json.py --dry-run` shows expected output
- [ ] `data/dashboard.json` rebuilt locally (or CI will do it)
- [ ] `pnpm build` succeeds with no errors
- [ ] `CHANGELOG.md` updated
- [ ] Commit message follows the format above
