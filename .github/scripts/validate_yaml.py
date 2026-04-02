#!/usr/bin/env python3
"""
YAML Schema Validator for ai-benchmark-tracker
Validates all data files against required field schemas.
Exits with code 1 if any errors are found (fails the CI check).
"""

import os
import sys
import yaml
from pathlib import Path

# ── ANSI colours ──────────────────────────────────────────────────────────────
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

# ── Required field schemas ─────────────────────────────────────────────────────

MODEL_FILE_REQUIRED = {
    "provider": {
        "_type": dict,
        "required_keys": ["name", "brand_color", "website"],
    },
    "models": {
        "_type": list,
    },
}

MODEL_ENTRY_REQUIRED = ["id", "name", "released", "type", "context_window"]
MODEL_ENTRY_RECOMMENDED = ["pricing", "scores"]

BENCHMARK_FILE_REQUIRED = {
    "benchmarks": {"_type": dict},
}

BENCHMARK_ENTRY_REQUIRED = ["name", "category", "description", "unit", "higher_is_better"]
VALID_BENCHMARK_CATEGORIES = {
    "reasoning", "science", "coding", "math",
    "knowledge_work", "long_context", "agentic", "composite",
}

SNAPSHOT_FILE_REQUIRED = {
    "snapshot_date": {"_type": str},
    "leaderboard": {"_type": list},
}

SNAPSHOT_ENTRY_REQUIRED = ["rank", "model", "provider"]

VALID_VERIFICATION_STATUSES = {"verified", "unverified", "partially_verified"}

# ── Helpers ────────────────────────────────────────────────────────────────────

errors   = []
warnings = []

def err(path: str, msg: str):
    errors.append(f"  {RED}✗ {path}{RESET}  {msg}")

def warn(path: str, msg: str):
    warnings.append(f"  {YELLOW}⚠ {path}{RESET}  {msg}")

def load_yaml(filepath: Path):
    with open(filepath) as f:
        return yaml.safe_load(f)

# ── Validators ─────────────────────────────────────────────────────────────────

def validate_model_file(filepath: Path, data: dict):
    base = filepath.name

    # Top-level structure
    for key, spec in MODEL_FILE_REQUIRED.items():
        if key not in data:
            err(base, f"Missing top-level key: `{key}`")
            continue
        if "_type" in spec and not isinstance(data[key], spec["_type"]):
            err(base, f"`{key}` must be a {spec['_type'].__name__}")
            continue
        if "required_keys" in spec:
            for rk in spec["required_keys"]:
                if rk not in data[key]:
                    err(base, f"`provider.{rk}` is required but missing")

    # Validate provider brand_color format
    if "provider" in data and "brand_color" in data.get("provider", {}):
        bc = data["provider"]["brand_color"]
        if not (isinstance(bc, str) and bc.startswith("#") and len(bc) in (4, 7)):
            err(base, f"`provider.brand_color` must be a hex color (e.g. #FF0000), got: {bc!r}")

    # Validate each model entry
    models = data.get("models", [])
    if not isinstance(models, list):
        return
    for i, model in enumerate(models):
        ref = f"{base} → models[{i}]"
        if not isinstance(model, dict):
            err(ref, "Expected a dict, got something else")
            continue

        for field in MODEL_ENTRY_REQUIRED:
            if field not in model:
                err(ref, f"Required field `{field}` is missing")

        for field in MODEL_ENTRY_RECOMMENDED:
            if field not in model:
                warn(ref, f"Recommended field `{field}` is missing (model: {model.get('id', '?')})")

        # released must be YYYY-MM-DD
        released = model.get("released")
        if released and not _is_date(str(released)):
            err(ref, f"`released` must be YYYY-MM-DD, got: {released!r}")

        # type must be known
        model_type = model.get("type", "")
        if model_type and "proprietary" not in model_type and "open-source" not in model_type and "open_source" not in model_type:
            warn(ref, f"`type` value {model_type!r} is not one of (proprietary, open-source)")

        # verification status, if present
        verification = model.get("verification", {})
        if verification and isinstance(verification, dict):
            status = verification.get("status")
            if status and status not in VALID_VERIFICATION_STATUSES:
                err(ref, f"`verification.status` must be one of {VALID_VERIFICATION_STATUSES}, got: {status!r}")

        # scores must be a dict of numbers
        scores = model.get("scores", {})
        if scores and isinstance(scores, dict):
            for k, v in scores.items():
                if v is not None and not isinstance(v, (int, float)):
                    err(ref, f"`scores.{k}` must be a number or null, got: {v!r}")

        # pricing values must be numbers if present
        pricing = model.get("pricing", {})
        if pricing and isinstance(pricing, dict):
            for k in ("input_per_m", "output_per_m", "composite_per_m"):
                if k in pricing and not isinstance(pricing[k], (int, float)):
                    err(ref, f"`pricing.{k}` must be a number, got: {pricing[k]!r}")


def validate_benchmarks_file(filepath: Path, data: dict):
    base = filepath.name

    benchmarks = data.get("benchmarks", {})
    if not isinstance(benchmarks, dict):
        err(base, "`benchmarks` must be a dict of benchmark entries")
        return

    for bk, bv in benchmarks.items():
        ref = f"{base} → benchmarks.{bk}"
        if not isinstance(bv, dict):
            err(ref, "Expected a dict")
            continue
        for field in BENCHMARK_ENTRY_REQUIRED:
            if field not in bv:
                err(ref, f"Required field `{field}` is missing")

        cat = bv.get("category", "")
        if cat and cat not in VALID_BENCHMARK_CATEGORIES:
            err(ref, f"`category` {cat!r} is not valid. Allowed: {VALID_BENCHMARK_CATEGORIES}")

        hib = bv.get("higher_is_better")
        if hib is not None and not isinstance(hib, bool):
            err(ref, f"`higher_is_better` must be true or false, got: {hib!r}")


def validate_snapshot_file(filepath: Path, data: dict):
    base = filepath.name

    # snapshot_date
    sd = data.get("snapshot_date")
    if not sd:
        err(base, "Required field `snapshot_date` is missing")
    elif not _is_date(str(sd)):
        err(base, f"`snapshot_date` must be YYYY-MM-DD, got: {sd!r}")

    # leaderboard
    leaderboard = data.get("leaderboard", [])
    if not isinstance(leaderboard, list):
        err(base, "`leaderboard` must be a list")
        return
    if len(leaderboard) == 0:
        warn(base, "`leaderboard` is empty")

    for i, entry in enumerate(leaderboard):
        ref = f"{base} → leaderboard[{i}]"
        for field in SNAPSHOT_ENTRY_REQUIRED:
            if field not in entry:
                err(ref, f"Required field `{field}` is missing")
        rank = entry.get("rank")
        if rank is not None and (not isinstance(rank, int) or rank < 1):
            err(ref, f"`rank` must be a positive integer, got: {rank!r}")


def _is_date(s: str) -> bool:
    import re
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", s))

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    repo_root = Path(__file__).parent.parent.parent
    data_root = repo_root / "data"

    if not data_root.exists():
        print(f"{RED}data/ directory not found at {data_root}{RESET}")
        sys.exit(1)

    print(f"\n{BOLD}{CYAN}Frontier AI Benchmark Tracker — YAML Validator{RESET}\n")

    files_checked = 0

    # Model files
    models_dir = data_root / "models"
    for yaml_file in sorted(models_dir.glob("*.yaml")):
        print(f"  Checking {CYAN}{yaml_file.relative_to(repo_root)}{RESET}")
        try:
            data = load_yaml(yaml_file)
            validate_model_file(yaml_file, data)
            files_checked += 1
        except yaml.YAMLError as e:
            err(yaml_file.name, f"YAML parse error: {e}")

    # Benchmarks file
    bench_file = data_root / "benchmarks" / "benchmarks.yaml"
    if bench_file.exists():
        print(f"  Checking {CYAN}{bench_file.relative_to(repo_root)}{RESET}")
        try:
            data = load_yaml(bench_file)
            validate_benchmarks_file(bench_file, data)
            files_checked += 1
        except yaml.YAMLError as e:
            err(bench_file.name, f"YAML parse error: {e}")
    else:
        warn("data/benchmarks/benchmarks.yaml", "File not found — expected benchmark definitions here")

    # Snapshot files
    snapshots_dir = data_root / "snapshots"
    for yaml_file in sorted(snapshots_dir.glob("*.yaml")):
        print(f"  Checking {CYAN}{yaml_file.relative_to(repo_root)}{RESET}")
        try:
            data = load_yaml(yaml_file)
            validate_snapshot_file(yaml_file, data)
            files_checked += 1
        except yaml.YAMLError as e:
            err(yaml_file.name, f"YAML parse error: {e}")

    # Summary
    print(f"\n{BOLD}── Results ──────────────────────────────────────────{RESET}")
    print(f"  Files checked : {files_checked}")
    print(f"  Errors        : {len(errors)}")
    print(f"  Warnings      : {len(warnings)}")

    if warnings:
        print(f"\n{YELLOW}Warnings:{RESET}")
        for w in warnings:
            print(w)

    if errors:
        print(f"\n{RED}Errors:{RESET}")
        for e in errors:
            print(e)
        print(f"\n{RED}{BOLD}Validation FAILED — fix the errors above before merging.{RESET}\n")
        sys.exit(1)
    else:
        print(f"\n{GREEN}{BOLD}All files passed validation ✓{RESET}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
