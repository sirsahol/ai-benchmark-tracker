#!/usr/bin/env python3
"""
Auto-populate benchmark scores from free public APIs.

Data sources:
  - HuggingFace Open LLM Leaderboard API
  - Artificial Analysis leaderboard

Updates YAML model files under data/models/ with new scores, marking each
auto-populated value with source metadata.  Never crashes on API failures.

Run:  python .github/scripts/auto_populate_scores.py [--dry-run]
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import ssl
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = REPO_ROOT / "data" / "models"

# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ---------------------------------------------------------------------------
# Mapping: external model name -> (yaml_file_stem, model_id)
# ---------------------------------------------------------------------------
MODEL_ID_MAP: dict[str, tuple[str, str]] = {
    # HuggingFace / Artificial Analysis names
    "gpt-5.4":               ("openai",    "gpt-5.4"),
    "gpt-5.3-codex":         ("openai",    "gpt-5.3-codex"),
    "gpt-5.2":               ("openai",    "gpt-5.2"),
    "gpt-5.1":               ("openai",    "gpt-5.1"),
    "claude-opus-4.6":       ("anthropic", "claude-opus-4.6"),
    "claude-sonnet-4.6":     ("anthropic", "claude-sonnet-4.6"),
    "claude-opus-4.5":       ("anthropic", "claude-opus-4.5"),
    "gemini-3.1-pro":        ("google",    "gemini-3.1-pro"),
    "gemini-3-pro":          ("google",    "gemini-3-pro"),
    "gemini-3-flash":        ("google",    "gemini-3-flash"),
    "grok-4.20-beta":        ("xai",       "grok-4.20-beta"),
    "grok-4":                ("xai",       "grok-4"),
    "llama-4-scout":         ("meta",      "llama-4-scout"),
    "llama-4-maverick":      ("meta",      "llama-4-maverick"),
    "deepseek-v4-pro":       ("deepseek",  "deepseek-v4-pro"),
    "deepseek-v4-flash":     ("deepseek",  "deepseek-v4-flash"),
    "glm-5.1":               ("zai",       "glm-5.1"),
    "glm-5":                 ("zai",       "glm-5"),
    "glm-4.7":               ("zai",       "glm-4.7"),
    "kimi-k2.5":             ("moonshot",  "kimi-k2.5"),
    "kimi-k2":               ("moonshot",  "kimi-k2"),
    "minimax-m2.7":          ("minimax",   "minimax-m2.7"),
    "minimax-m2.5":          ("minimax",   "minimax-m2.5"),
    "mistral-large-3":       ("mistral",   "mistral-large-3"),
    "mimo-v2-pro":           ("xiaomi",    "mimo-v2-pro"),
    "mimo-v2.5-pro":         ("xiaomi",    "mimo-v2.5-pro"),
}

# ---------------------------------------------------------------------------
# Mapping: external benchmark key -> our YAML score key
# ---------------------------------------------------------------------------
BENCHMARK_MAP: dict[str, str] = {
    # HuggingFace leaderboard columns
    "average":               "average",
    "ifeval":                "ifeval",
    "hellaswag":             "hellaswag",
    "mmlu":                  "mmlu",
    "mmlu_pro":              "mmlu_pro",
    "arc_challenge":         "arc_challenge",
    "gpqa_diamond":          "gpqa_diamond",
    "math_500":              "math_500",
    "gpqa":                  "gpqa_diamond",
    "swe_bench_verified":    "swe_bench_verified",
    # Artificial Analysis
    "intelligence_index":    "intelligence_index",
    "gdpval_aa_elo":         "gdpval_aa_elo",
}

# ---------------------------------------------------------------------------
# HTTP helper — stdlib only
# ---------------------------------------------------------------------------
def fetch_json(url: str, timeout: int = 30) -> dict | list | None:
    """GET *url* and return parsed JSON, or None on any failure."""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "ai-benchmark-tracker/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            if resp.status == 200:
                raw = resp.read()
                return json.loads(raw)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError,
            TimeoutError, OSError) as exc:
        print(f"  {RED}fetch error{RESET} {url}: {exc}")
    return None

# ---------------------------------------------------------------------------
# Data source: HuggingFace Open LLM Leaderboard
# ---------------------------------------------------------------------------
HF_LEADERBOARD_URL = (
    "https://huggingface.co/api/spaces/open-llm-leaderboard/open_llm_leaderboard"
    "/api/v1/leaderboard"
)

def fetch_huggingface_leaderboard() -> list[dict]:
    """Return list of {model, benchmarks} dicts from HF leaderboard."""
    print(f"\n{CYAN}Fetching HuggingFace leaderboard...{RESET}")
    data = fetch_json(HF_LEADERBOARD_URL)
    if not data or not isinstance(data, list):
        print(f"  {YELLOW}No data returned from HuggingFace API{RESET}")
        return []

    results = []
    for entry in data[:200]:  # cap to first 200 entries
        model_name = entry.get("model") or entry.get("model_name") or ""
        if not model_name:
            continue
        # Normalise: strip org prefix for matching (e.g. "openai/gpt-5.4" -> "gpt-5.4")
        short = model_name.split("/")[-1].lower().replace(" ", "-")
        scores: dict[str, float] = {}
        for ext_key, int_key in BENCHMARK_MAP.items():
            val = entry.get(ext_key)
            if val is not None:
                try:
                    scores[int_key] = float(val)
                except (TypeError, ValueError):
                    pass
        if scores:
            results.append({"model": short, "scores": scores,
                            "source": "huggingface"})
    print(f"  Found scores for {len(results)} models")
    return results

# ---------------------------------------------------------------------------
# Data source: Artificial Analysis
# ---------------------------------------------------------------------------
AA_LEADERBOARD_URL = (
    "https://artificialanalysis.ai/api/leaderboard/models"
)

def fetch_artificial_analysis() -> list[dict]:
    """Return list of model score dicts from Artificial Analysis."""
    print(f"\n{CYAN}Fetching Artificial Analysis leaderboard...{RESET}")
    data = fetch_json(AA_LEADERBOARD_URL)
    if not data:
        print(f"  {YELLOW}No data returned from Artificial Analysis API{RESET}")
        return []

    models_list = data if isinstance(data, list) else data.get("models", [])
    results = []
    for entry in models_list:
        name = (entry.get("model") or entry.get("name") or "").lower().replace(" ", "-")
        if not name:
            continue
        scores: dict[str, float] = {}
        for ext_key, int_key in BENCHMARK_MAP.items():
            val = entry.get(ext_key)
            if val is not None:
                try:
                    scores[int_key] = float(val)
                except (TypeError, ValueError):
                    pass
        if scores:
            results.append({"model": name, "scores": scores,
                            "source": "artificial_analysis"})
    print(f"  Found scores for {len(results)} models")
    return results

# ---------------------------------------------------------------------------
# YAML update logic
# ---------------------------------------------------------------------------
SOURCE_URLS = {
    "huggingface":          "https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard",
    "artificial_analysis":  "https://artificialanalysis.ai/leaderboards/models",
}

def update_model_scores(model_data: dict, fetched: list[dict],
                        dry_run: bool) -> int:
    """
    Merge fetched scores into a single model dict.
    Returns number of scores updated.
    Only overwrites if the new score is more recent or the field is empty.
    """
    model_id = model_data.get("id", "")
    if not model_id:
        return 0

    today_str = date.today().isoformat()
    scores = model_data.setdefault("scores", {})
    updated = 0

    for entry in fetched:
        # Try to match fetched model name to our model ID
        fetched_name = entry["model"]
        # Direct match
        matched = fetched_name == model_id.lower()
        # Fuzzy: check if our model_id is contained in fetched name
        if not matched:
            matched = model_id.lower() in fetched_name or fetched_name in model_id.lower()
        # Explicit map lookup
        if not matched:
            for ext_name, (yaml_file, yaml_id) in MODEL_ID_MAP.items():
                if yaml_id == model_id and ext_name.lower() == fetched_name:
                    matched = True
                    break

        if not matched:
            continue

        src_key = entry["source"]
        src_url = SOURCE_URLS.get(src_key, "")

        for bench_key, new_val in entry["scores"].items():
            existing = scores.get(bench_key)
            # Only update if: no existing score, or existing is a bare number / dict without source
            should_update = False
            if existing is None:
                should_update = True
            elif isinstance(existing, (int, float)) and existing != new_val:
                should_update = True
            elif isinstance(existing, dict):
                # Don't overwrite manually curated scores (those with explicit source URLs)
                old_src = existing.get("source", "")
                if not old_src or "artificialanalysis" in old_src or "huggingface" in old_src:
                    old_val = existing.get("value")
                    if old_val is None or abs(float(old_val) - new_val) > 0.05:
                        should_update = True

            if should_update:
                scores[bench_key] = {
                    "value": new_val,
                    "benchmark_date": today_str,
                    "source": src_url,
                    "auto_populated": True,
                }
                updated += 1
                status = f"{YELLOW}updated{RESET}" if dry_run else f"{GREEN}updated{RESET}"
                print(f"    {status} {bench_key}: {new_val}  ({src_key})")

    return updated

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Auto-populate benchmark scores")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing files")
    args = parser.parse_args()

    print(f"\n{BOLD}{CYAN}Auto-populate benchmark scores{RESET}")
    print(f"  Date : {date.today().isoformat()}")
    if args.dry_run:
        print(f"  Mode : {YELLOW}DRY-RUN{RESET}")

    # Fetch from all sources
    all_fetched: list[dict] = []
    all_fetched.extend(fetch_huggingface_leaderboard())
    all_fetched.extend(fetch_artificial_analysis())

    if not all_fetched:
        print(f"\n{RED}No data fetched from any source. Exiting.{RESET}")
        sys.exit(1)

    # Process each YAML file
    total_updates = 0
    files_changed = 0

    for yaml_file in sorted(MODELS_DIR.glob("*.yaml")):
        with open(yaml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        file_updates = 0
        for model in data.get("models", []):
            file_updates += update_model_scores(model, all_fetched, args.dry_run)

        if file_updates > 0:
            total_updates += file_updates
            files_changed += 1
            if not args.dry_run:
                with open(yaml_file, "w", encoding="utf-8") as f:
                    yaml.dump(data, f, default_flow_style=False,
                              allow_unicode=True, sort_keys=False)
                print(f"  {GREEN}Wrote{RESET} {yaml_file.name}  ({file_updates} scores)")
            else:
                print(f"  {YELLOW}[dry-run]{RESET} would write {yaml_file.name}  ({file_updates} scores)")

    # Summary
    print(f"\n{BOLD}Summary{RESET}")
    print(f"  Sources queried  : 2")
    print(f"  Records fetched  : {len(all_fetched)}")
    print(f"  Scores updated   : {total_updates}")
    print(f"  Files changed    : {files_changed}")

    if args.dry_run:
        print(f"\n{YELLOW}Dry-run complete — no files written.{RESET}\n")
    else:
        print(f"\n{GREEN}{BOLD}Done.{RESET}\n")

if __name__ == "__main__":
    main()
