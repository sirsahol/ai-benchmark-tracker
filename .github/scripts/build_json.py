#!/usr/bin/env python3
"""
YAML → Versioned JSON builder for ai-benchmark-tracker.

Supports the v2 schema where scores can be either:
  - A bare number:   swe_bench_verified: 80.8
  - A rich object:   swe_bench_verified:
                       value: 80.8
                       self_reported: true
                       benchmark_date: 2026-02-19
                       source: "https://..."
                       notes: "..."

Outputs:
  data/dashboard.json           ← always latest, consumed by index.html
  data/versions/YYYY-MM-DD.json ← immutable dated snapshot

Run: python .github/scripts/build_json.py [--dry-run]
"""

import argparse
import json
import sys
import yaml
from datetime import date, datetime
from pathlib import Path

REPO_ROOT  = Path(__file__).resolve().parent.parent.parent
DATA_DIR   = REPO_ROOT / "data"
MODELS_DIR = DATA_DIR / "models"
BENCH_FILE = DATA_DIR / "benchmarks" / "benchmarks.yaml"
OUT_LATEST = DATA_DIR / "dashboard.json"
OUT_VERS   = DATA_DIR / "versions"

GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def normalise_score(raw) -> dict:
    """
    Accept both bare-number and rich-object score formats.
    Always returns a dict:
      { value, self_reported, benchmark_date, source, notes }
    """
    if raw is None:
        return {"value": None, "self_reported": False,
                "benchmark_date": None, "source": None, "notes": None}
    if isinstance(raw, (int, float)):
        return {"value": raw, "self_reported": False,
                "benchmark_date": None, "source": None, "notes": None}
    if isinstance(raw, dict):
        return {
            "value":          raw.get("value"),
            "self_reported":  bool(raw.get("self_reported", False)),
            "benchmark_date": str(raw["benchmark_date"]) if raw.get("benchmark_date") else None,
            "source":         raw.get("source"),
            "notes":          raw.get("notes"),
        }
    # Fallback: coerce to number if possible
    try:
        return {"value": float(raw), "self_reported": False,
                "benchmark_date": None, "source": None, "notes": None}
    except (TypeError, ValueError):
        return {"value": None, "self_reported": False,
                "benchmark_date": None, "source": None, "notes": str(raw)}


def build_payload() -> dict:
    build_ts = datetime.utcnow().isoformat() + "Z"

    # ── Benchmarks ──────────────────────────────────────────────────────────
    benchmarks = {}
    if BENCH_FILE.exists():
        benchmarks = load_yaml(BENCH_FILE).get("benchmarks", {})

    # ── Models ───────────────────────────────────────────────────────────────
    models    = []
    providers = {}

    for yaml_file in sorted(MODELS_DIR.glob("*.yaml")):
        raw      = load_yaml(yaml_file)
        prov_id  = yaml_file.stem
        prov_meta = raw.get("provider", {})
        providers[prov_id] = prov_meta

        for model in raw.get("models", []):
            # Normalise every score entry
            raw_scores = model.get("scores") or {}
            model["scores"] = {k: normalise_score(v) for k, v in raw_scores.items()}

            # Attach provider metadata
            model["provider_id"]    = prov_id
            model["provider_name"]  = prov_meta.get("name", prov_id)
            model["provider_color"] = prov_meta.get("brand_color", "#888888")

            # Convenience: flat score value for sorting
            model["_intelligence"] = (
                model["scores"].get("intelligence_index", {}).get("value") or 0
            )
            models.append(model)

    # Sort by intelligence_index desc, nulls last
    models.sort(key=lambda m: (0 if m["_intelligence"] == 0 else 1, -m["_intelligence"]))
    for m in models:
        del m["_intelligence"]

    return {
        "meta": {
            "built_at":        build_ts,
            "schema_version":  "3",
            "model_count":     len(models),
            "benchmark_count": len(benchmarks),
        },
        "benchmarks": benchmarks,
        "providers":  providers,
        "models":     models,
    }


def write_json(path: Path, payload: dict, dry_run: bool = False):
    content = json.dumps(payload, indent=2, default=str)
    if dry_run:
        print(f"  {YELLOW}[dry-run]{RESET} {path.relative_to(REPO_ROOT)}  ({len(content)/1024:.1f} KB)")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  {GREEN}✓{RESET}  {path.relative_to(REPO_ROOT)}  ({len(content)/1024:.1f} KB)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"\n{BOLD}{CYAN}ai-benchmark-tracker — JSON builder (schema v3){RESET}\n")
    payload   = build_payload()
    today_str = date.today().isoformat()

    print(f"  Models     : {payload['meta']['model_count']}")
    print(f"  Benchmarks : {payload['meta']['benchmark_count']}")
    print(f"  Built at   : {payload['meta']['built_at']}\n")

    write_json(OUT_LATEST, payload, dry_run=args.dry_run)
    write_json(OUT_VERS / f"{today_str}.json", payload, dry_run=args.dry_run)

    verb = "Dry-run complete" if args.dry_run else f"{GREEN}{BOLD}Build complete ✓"
    print(f"\n{verb}{RESET}\n")


if __name__ == "__main__":
    main()
