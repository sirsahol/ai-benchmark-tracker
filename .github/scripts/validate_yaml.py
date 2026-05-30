#!/usr/bin/env python3
"""
YAML Schema Validator — ai-benchmark-tracker (schema v3)
Supports both bare-number and rich-object score formats.
Exits with code 1 on errors (blocks CI merge).

Enforces:
  - Trust tiers: verified (requires verified_by/at/source_url), auto_populated,
    unverified, estimated
  - Deprecation: no circular chains, no dangling superseded_by, data freeze on
    deprecated models, no reanimation
  - Score format and metadata validation
"""

import json, re, sys, yaml
from pathlib import Path

RED    = "\033[91m"; YELLOW = "\033[93m"; GREEN = "\033[92m"
CYAN   = "\033[96m"; RESET  = "\033[0m";  BOLD  = "\033[1m"

REPO_ROOT   = Path(__file__).resolve().parent.parent.parent
DATA_DIR    = REPO_ROOT / "data"
MODELS_DIR  = DATA_DIR / "models"
BENCH_FILE  = DATA_DIR / "benchmarks" / "benchmarks.yaml"
SNAP_DIR    = DATA_DIR / "snapshots"
DASH_JSON   = DATA_DIR / "dashboard.json"

VALID_TYPES        = {"proprietary", "open-source", "open_source"}
VALID_VERIF        = {"verified", "unverified", "partially_verified",
                      "auto_populated", "estimated"}
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

def load_json(p: Path):
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def is_date(s): return bool(DATE_RE.match(str(s)))

# ── Score normalisation (mirrors build_json.py) ───────────────────────────────
def validate_score_entry(loc, key, raw):
    if raw is None:
        return
    if isinstance(raw, (int, float)):
        return
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

# ── Trust tier validation ────────────────────────────────────────────────────
def validate_trust_tier(loc, model_id, verif):
    """Enforce trust tier requirements."""
    status = verif.get("status") if isinstance(verif, dict) else None
    if not status:
        return

    if status not in VALID_VERIF:
        err(loc, f"`verification.status` must be one of {VALID_VERIF}, got: {status!r}")
        return

    if status == "verified":
        vby = verif.get("verified_by")
        if not vby or not isinstance(vby, str):
            err(loc, "`verification.verified_by` (string) is required when status='verified'")
        vat = verif.get("verified_at")
        if not vat or not is_date(str(vat)):
            err(loc, "`verification.verified_at` (YYYY-MM-DD) is required when status='verified'")
        surl = verif.get("source_url")
        if not surl or not isinstance(surl, str):
            err(loc, "`verification.source_url` (string) is required when status='verified'")

# ── Model file ────────────────────────────────────────────────────────────────
def validate_model_file(path: Path, data: dict, all_model_ids: set[str],
                        prior_models: dict[str, dict] | None):
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

        model_id = m.get("id", "")

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

        tags = m.get("tags", [])
        if tags is not None and not isinstance(tags, list):
            err(loc, "`tags` must be a list")

        # superseded_by — basic type check (cross-file checks happen in phase 2)
        sup = m.get("superseded_by")
        if sup is not None and not isinstance(sup, str):
            err(loc, "`superseded_by` must be a model id string")
        if sup is not None and sup == model_id:
            err(loc, "`superseded_by` cannot point to itself")

        # scores
        scores = m.get("scores") or {}
        for k, v in scores.items():
            validate_score_entry(loc, k, v)

        # verification — trust tier
        verif = m.get("verification") or {}
        validate_trust_tier(loc, model_id, verif)

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

# ── Cross-file checks (phase 2) ─────────────────────────────────────────────
def resolve_superseded_chain(start_id: str, all_superseded: dict[str, str]) -> list[str]:
    """Follow the superseded_by chain from start_id. Returns the chain of IDs."""
    chain = [start_id]
    current = start_id
    visited = {current}
    while current in all_superseded:
        next_id = all_superseded[current]
        if next_id in visited:
            chain.append(next_id)
            return chain  # cycle detected
        visited.add(next_id)
        chain.append(next_id)
        current = next_id
    return chain

def cross_file_checks(all_models: list[dict]):
    """Run checks that require the full set of all models across all files."""
    # Build maps
    model_ids = set()
    superseded_map: dict[str, str] = {}
    deprecated_ids: set[str] = set()
    deprecated_scores: dict[str, dict] = {}
    verif_status: dict[str, str] = {}

    for m in all_models:
        mid = m.get("id", "")
        if not mid:
            continue
        model_ids.add(mid)
        scores = m.get("scores") or {}
        verif = m.get("verification") or {}
        verif_status[mid] = (verif.get("status", "") if isinstance(verif, dict) else "")

        sup = m.get("superseded_by")
        if sup and isinstance(sup, str):
            superseded_map[mid] = sup
            deprecated_ids.add(mid)
            deprecated_scores[mid] = scores

    # 1. No dangling superseded_by
    for dep_id, target in superseded_map.items():
        if target not in model_ids:
            err(f"{dep_id}", f"`superseded_by` points to '{target}' which does not exist in any model file")

    # 2. No circular deprecation chains
    for dep_id in superseded_map:
        chain = resolve_superseded_chain(dep_id, superseded_map)
        if len(chain) > 2 and chain[-1] == dep_id:
            path = " → ".join(chain)
            err(f"{dep_id}", f"Circular deprecation chain detected: {path}")

    # 3. Data freeze — deprecated models must not have new/changed scores
    prior = load_json(DASH_JSON)
    if prior and prior.get("models"):
        prior_map: dict[str, dict] = {}
        for pm in prior["models"]:
            prior_map[pm.get("id", "")] = pm

        for dep_id in deprecated_ids:
            # Check if model existed before (wasn't just added)
            prior_entry = prior_map.get(dep_id)
            if prior_entry:
                prior_sup = prior_entry.get("superseded_by")
                was_deprecated = bool(prior_sup)
                if was_deprecated:
                    # Model was already deprecated — scores must match exactly
                    prior_scr = prior_entry.get("scores") or {}
                    current_scr = deprecated_scores.get(dep_id) or {}
                    # Compare score keys and values
                    prior_keys = set(prior_scr.keys())
                    current_keys = set(current_scr.keys())
                    added = current_keys - prior_keys
                    removed = prior_keys - current_keys
                    changed = {k for k in prior_keys & current_keys
                               if _score_value(prior_scr[k]) != _score_value(current_scr[k])}
                    if added:
                        err(f"{dep_id}", f"Data freeze violation: deprecated model has new score(s): {', '.join(sorted(added))}")
                    if removed:
                        err(f"{dep_id}", f"Data freeze violation: deprecated model is missing score(s): {', '.join(sorted(removed))}")
                    if changed:
                        err(f"{dep_id}", f"Data freeze violation: deprecated model has modified score(s): {', '.join(sorted(changed))}")
            else:
                # New model that is already deprecated — can only have empty scores
                current_scr = deprecated_scores.get(dep_id) or {}
                non_null = {k for k, v in current_scr.items() if v is not None}
                if isinstance(list(current_scr.values())[0], dict) if current_scr else False:
                    non_null = {k for k, v in current_scr.items()
                                if isinstance(v, dict) and v.get("value") is not None}
                if non_null:
                    err(f"{dep_id}", f"New model cannot be immediately deprecated with scores — use an active state first")

    # 4. Reanimation check — model had superseded_by in prior JSON but not in current YAML
    if prior and prior.get("models"):
        for pm in prior["models"]:
            pid = pm.get("id", "")
            prior_sup = pm.get("superseded_by")
            if prior_sup and pid in model_ids:
                current_sup = None
                for m in all_models:
                    if m.get("id") == pid:
                        current_sup = m.get("superseded_by")
                        break
                if not current_sup:
                    err(f"{pid}", f"Reanimation: `superseded_by` was '{prior_sup}' but is now unset — reverting deprecation requires human review")


def _score_value(raw) -> float | None:
    """Extract the numeric value from a score entry (bare number or rich object)."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, dict):
        v = raw.get("value")
        return float(v) if v is not None else None
    return None

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{BOLD}{CYAN}ai-benchmark-tracker — YAML Validator (schema v3){RESET}\n")
    n = 0
    all_models: list[dict] = []

    for f in sorted(MODELS_DIR.glob("*.yaml")):
        print(f"  {CYAN}{f.relative_to(REPO_ROOT)}{RESET}")
        try:
            data = load(f)
            validate_model_file(f, data, set(), None)
            all_models.extend(data.get("models", []))
            n += 1
        except yaml.YAMLError as e:
            err(f.name, f"YAML parse error: {e}")

    if BENCH_FILE.exists():
        print(f"  {CYAN}{BENCH_FILE.relative_to(REPO_ROOT)}{RESET}")
        try:
            validate_benchmarks_file(BENCH_FILE, load(BENCH_FILE))
            n += 1
        except yaml.YAMLError as e:
            err(BENCH_FILE.name, f"YAML parse error: {e}")
    else:
        warn("data/benchmarks/benchmarks.yaml", "File not found")

    for f in sorted(SNAP_DIR.glob("*.yaml")):
        if f.name == ".gitkeep":
            continue
        print(f"  {CYAN}{f.relative_to(REPO_ROOT)}{RESET}")
        try:
            validate_snapshot_file(f, load(f))
            n += 1
        except yaml.YAMLError as e:
            err(f.name, f"YAML parse error: {e}")

    # Phase 2 — cross-file checks
    cross_file_checks(all_models)

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
