# Contributing

## Types of Contributions

| Type | What to do |
|------|------------|
| Add a new model | See [Adding Models](./Adding-Models.md) |
| Add a new benchmark | See [Adding Benchmarks](./Adding-Benchmarks.md) |
| Update an existing score | Edit the score in the model YAML, update CHANGELOG |
| Update verification status | Edit `verification.status` + `notes` in model YAML |
| Fix a typo or data error | Direct commit to `main` is fine for trivial fixes |
| Dashboard UI change | Edit `index.html`, test locally, open PR |
| Add a new CI check | Edit `.github/scripts/validate_yaml.py` |

---

## Commit Message Format

```
[model-id] Action description

[snapshot] Add YYYY-MM-DD snapshot
[benchmark] Add benchmark-name definition
[dashboard] Description of dashboard change
[ci] Description of CI/tooling change
[docs] Description of documentation change
[fix] Description of data fix
```

Examples:
```
[gemini-3.1-pro] Add APEX-Agents and MCP Atlas scores
[snapshot] Add 2026-04-15 snapshot after GPT-5.5 release
[benchmark] Add apex_agents benchmark definition
[dashboard] Add SR badge tooltip to leaderboard table
[ci] Fix date validation regex in validate_yaml.py
[fix] Correct Kimi K2.5 SWE-Bench score (72.4 → 73.1)
```

---

## Local Development

### Prerequisites

```bash
pip install pyyaml
```

No other dependencies — the dashboard is vanilla HTML/CSS/JS.

### Validate YAML

```bash
python .github/scripts/validate_yaml.py
```

Checks all `data/models/*.yaml`, `data/benchmarks/benchmarks.yaml`, and `data/snapshots/*.yaml` for schema compliance. Exits 1 on errors.

### Build JSON

```bash
# Dry run — prints what would be written
python .github/scripts/build_json.py --dry-run

# Full build
python .github/scripts/build_json.py
```

Writes `data/dashboard.json` and `data/versions/YYYY-MM-DD.json`.

### View the dashboard locally

```bash
open index.html
# or
python -m http.server 8080  # then visit localhost:8080
```

No build step. All data is embedded or loaded from `data/dashboard.json` relative to `index.html`.

---

## CI Checks

Two GitHub Actions workflows run on every push:

| Workflow | File | Triggers on |
|----------|------|-------------|
| **Validate YAML** | `.github/workflows/validate-yaml.yml` | Push/PR touching `data/**/*.yaml` |
| **Build JSON** | `.github/workflows/build-json.yml` | Push to `main`/`master` touching `data/**/*.yaml` |

The validate workflow **blocks merges** on errors. The build workflow auto-commits the regenerated JSON.

If the build workflow commits back to `main`, it uses `[skip ci]` in the commit message to prevent infinite loops.

---

## Data Integrity Rules

1. **Never edit `data/dashboard.json` manually** — it's auto-generated
2. **Never delete model entries** — use `superseded_by` to mark old models
3. **Always include `source` for self-reported scores** — `self_reported: true` without `source` fails validation
4. **Scores are numbers, not strings** — `80.8` not `"80.8%"`
5. **Dates are YYYY-MM-DD** — `2026-02-19` not `Feb 19, 2026`
6. **Keep benchmark keys consistent** — check `data/benchmarks/benchmarks.yaml` before adding new score keys to model files

---

## PR Checklist

Before opening a PR:

- [ ] `python .github/scripts/validate_yaml.py` passes with no errors
- [ ] `python .github/scripts/build_json.py --dry-run` shows expected output
- [ ] `data/dashboard.json` rebuilt locally (or CI will do it)
- [ ] `CHANGELOG.md` updated
- [ ] Snapshot updated if leaderboard changed materially
- [ ] Commit message follows the format above
