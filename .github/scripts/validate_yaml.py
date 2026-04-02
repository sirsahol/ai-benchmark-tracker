#!/usr/bin/env python3
"""
YAML Schema Validator — ai-benchmark-tracker (schema v3)
Supports both bare-number and rich-object score formats.
Exits with code 1 on errors (blocks CI merge).
"""

import re, sys, yaml
from pathlib import Path

RED    = "\033[91m"; YELLOW = "\033[93m"; GREEN = "\033[92m"
CYAN   = "\033[96m"; RESET  = "\033[0m";  BOLD  = "\033[1m"

REPO_ROOT   = Path(__file__).resolve().parent.parent.parent
DATA_DIR    = REPO_ROOT / "data"
MODELS_DIR  = DATA_DIR / "models"
BENCH_FILE  = DATA_DIR / "benchmarks" / "benchmarks.yaml"
SNAP_DIR    = DATA_DIR / "snapshots"

VALID_TYPES        = {"proprietary", "open-source", "open_source"}
VALID_VERIF        = {"verified", "unverified", "partially_verified"}
VALID_BENCH_CATS   = {"reasoning","science","coding","math","knowledge_work",
                      "long_context","agentic","composite"}
DATE_RE            = re.compile(r"^\d{4}-\d{2}-\d{2}$")

errors   = []
warnings = []

def err(loc, msg):  errors.append(f"  {RED}✗ {loc}{RESET}  {msg}")
def warn(loc, msg): warnings.append(f"  {YELLOW}⚠ {loc}{RESET}  {msg}")

def load(p: Path):
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def is_date(s): return bool(DATE_RE.match(str(s)))

# ── Score normalisation (mirrors build_json.py) ───────────────────────────────
def validate_score_entry(loc, key, raw):
    if raw is None:
        return
    if isinstance(raw, (int, float)):
        return  # bare number — fine
    if isinstance(raw, dict):
        if "value" not in raw:
            err(loc, f"`scores.{key}` rich object is missing required `value` field")
        elif raw["value"] is not None and not isinstance(raw["value"], (int, float)):
            err(loc, f"`scores.{key}.value` must be a number or null, got: {raw['value']!r}")
        if "self_reported" in raw and not isinstance(raw["self_reported"], bool):
            err(loc, f"`scores.{key}.self_reported` must be true or false")
        if "benchmark_date" in raw and raw["benchmark_date"] and not is_date(raw["benchmark_date"]):
            err(loc, f"`scores.{key}.benchmark_date` must be YYYY-MM-DD, got: {raw['benchmark_date']!r}")
        if raw.get("self_reported") and not raw.get("source"):
            warn(loc, f"`scores.{key}` is self_reported but has no `source` URL")
        return
    err(loc, f"`scores.{key}` must be a number or a dict, got: {type(raw).__name__}")

# ── Model file ────────────────────────────────────────────────────────────────
def validate_model_file(path: Path, data: dict):
    b = path.name
    prov = data.get("provider", {})
    if not isinstance(prov, dict):
        err(b, "`provider` must be a dict"); return
    for k in ("name", "brand_color", "website"):
        if k not in prov: err(b, f"`provider.{k}` is required")
    bc = prov.get("brand_color", "")
    if bc and not (bc.startswith("#") and len(bc) in (4,7)):
        err(b, f"`provider.brand_color` must be hex (#RGB or #RRGGBB), got: {bc!r}")

    models = data.get("models", [])
    if not isinstance(models, list):
        err(b, "`models` must be a list"); return

    for i, m in enumerate(models):
        loc = f"{b} → models[{i}] ({m.get('id','?')})"
        if not isinstance(m, dict): err(loc, "Expected dict"); continue

        for f in ("id", "name", "released", "type", "context_window"):
            if f not in m: err(loc, f"Required field `{f}` missing")
        for f in ("pricing", "scores"):
            if f not in m: warn(loc, f"Recommended field `{f}` missing")

        released = m.get("released")
        if released and not is_date(str(released)):
            err(loc, f"`released` must be YYYY-MM-DD, got: {released!r}")

        mtype = m.get("type", "")
        if mtype and mtype not in VALID_TYPES:
            warn(loc, f"`type` {mtype!r} not in {VALID_TYPES}")

        # tags
        tags = m.get("tags", [])
        if tags is not None and not isinstance(tags, list):
            err(loc, "`tags` must be a list")

        # superseded_by
        sup = m.get("superseded_by")
        if sup and not isinstance(sup, str):
            err(loc, "`superseded_by` must be a model id string")

        # scores
        scores = m.get("scores") or {}
        for k, v in scores.items():
            validate_score_entry(loc, k, v)

        # verification
        verif = m.get("verification") or {}
        status = verif.get("status")
        if status and status not in VALID_VERIF:
            err(loc, f"`verification.status` must be one of {VALID_VERIF}, got: {status!r}")

# ── Benchmarks file ───────────────────────────────────────────────────────────
def validate_benchmarks_file(path: Path, data: dict):
    b = path.name
    benches = data.get("benchmarks", {})
    if not isinstance(benches, dict): err(b, "`benchmarks` must be a dict"); return
    for k, v in benches.items():
        loc = f"{b} → {k}"
        for f in ("name","category","description","unit","higher_is_better"):
            if f not in v: err(loc, f"Required field `{f}` missing")
        cat = v.get("category","")
        if cat and cat not in VALID_BENCH_CATS:
            err(loc, f"`category` {cat!r} not in {VALID_BENCH_CATS}")
        hib = v.get("higher_is_better")
        if hib is not None and not isinstance(hib, bool):
            err(loc, "`higher_is_better` must be true or false")

# ── Snapshot file ─────────────────────────────────────────────────────────────
def validate_snapshot_file(path: Path, data: dict):
    b = path.name
    sd = data.get("snapshot_date")
    if not sd: err(b, "`snapshot_date` missing")
    elif not is_date(str(sd)): err(b, f"`snapshot_date` must be YYYY-MM-DD, got: {sd!r}")
    lb = data.get("leaderboard", [])
    if not isinstance(lb, list): err(b, "`leaderboard` must be a list"); return
    if not lb: warn(b, "`leaderboard` is empty")
    for i, entry in enumerate(lb):
        for f in ("rank","model","provider"):
            if f not in entry: err(f"{b}[{i}]", f"Required field `{f}` missing")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{BOLD}{CYAN}ai-benchmark-tracker — YAML Validator (schema v3){RESET}\n")
    n = 0

    for f in sorted(MODELS_DIR.glob("*.yaml")):
        print(f"  {CYAN}{f.relative_to(REPO_ROOT)}{RESET}")
        try: validate_model_file(f, load(f)); n += 1
        except yaml.YAMLError as e: err(f.name, f"YAML parse error: {e}")

    if BENCH_FILE.exists():
        print(f"  {CYAN}{BENCH_FILE.relative_to(REPO_ROOT)}{RESET}")
        try: validate_benchmarks_file(BENCH_FILE, load(BENCH_FILE)); n += 1
        except yaml.YAMLError as e: err(BENCH_FILE.name, f"YAML parse error: {e}")
    else:
        warn("data/benchmarks/benchmarks.yaml", "File not found")

    for f in sorted(SNAP_DIR.glob("*.yaml")):
        print(f"  {CYAN}{f.relative_to(REPO_ROOT)}{RESET}")
        try: validate_snapshot_file(f, load(f)); n += 1
        except yaml.YAMLError as e: err(f.name, f"YAML parse error: {e}")

    print(f"\n{BOLD}── Results {'─'*40}{RESET}")
    print(f"  Files checked : {n}")
    print(f"  Errors        : {len(errors)}")
    print(f"  Warnings      : {len(warnings)}")

    if warnings:
        print(f"\n{YELLOW}Warnings:{RESET}")
        for w in warnings: print(w)
    if errors:
        print(f"\n{RED}Errors:{RESET}")
        for e in errors: print(e)
        print(f"\n{RED}{BOLD}Validation FAILED — fix errors before merging.{RESET}\n")
        sys.exit(1)
    else:
        print(f"\n{GREEN}{BOLD}All files passed ✓{RESET}\n")

if __name__ == "__main__": main()
