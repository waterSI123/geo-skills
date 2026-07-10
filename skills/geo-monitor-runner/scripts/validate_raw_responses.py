#!/usr/bin/env python3
"""Validate ChatGPT GEO raw response JSONL data."""

import argparse
import json
from collections import Counter
from pathlib import Path


REQUIRED_FIELDS = [
    "run_id",
    "response_id",
    "prompt_id",
    "prompt",
    "platform",
    "run_status",
    "run_mode",
]
REQUIRED_KEYS = REQUIRED_FIELDS + ["raw_answer"]
ALLOWED_STATUSES = {"pending", "completed", "failed", "skipped", "needs_retry"}
MARKET_PROXY_FIELDS = [
    "monitoring_role",
    "prompt_realism_score",
    "demand_weight",
    "buyer_journey_stage",
    "source_basis",
    "overfit_risk",
]
ALLOWED_ROLES = {"market_proxy", "buyer_evaluation", "diagnostic_probe", "brand_control"}
ALLOWED_OVERFIT_RISKS = {"low", "medium", "high"}


def as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def iter_jsonl(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            yield line_no, json.loads(text)


def validate(path, manifest=None):
    errors = []
    warnings = []
    counts = Counter()
    response_ids = set()
    prompt_runs = Counter()

    for line_no, record in iter_jsonl(path):
        counts["records"] += 1
        if not isinstance(record, dict):
            errors.append(f"line {line_no}: record must be an object")
            continue
        for field in REQUIRED_KEYS + MARKET_PROXY_FIELDS:
            if field not in record:
                errors.append(f"line {line_no}: missing required key {field}")
        for field in REQUIRED_FIELDS:
            if record.get(field) in (None, ""):
                errors.append(f"line {line_no}: missing required field {field}")
        response_id = record.get("response_id")
        if response_id:
            if response_id in response_ids:
                errors.append(f"line {line_no}: duplicate response_id {response_id}")
            response_ids.add(response_id)
        platform = record.get("platform")
        if platform != "ChatGPT":
            errors.append(f"line {line_no}: platform must be ChatGPT, got {platform}")
        status = record.get("run_status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"line {line_no}: invalid run_status {status}")
        else:
            counts[status] += 1
        if status == "completed" and not (record.get("raw_answer") or "").strip():
            errors.append(f"line {line_no}: completed record has empty raw_answer")
        if status in {"failed", "skipped", "needs_retry"} and not (record.get("notes") or "").strip():
            warnings.append(f"line {line_no}: {status} record should include notes")
        if not record.get("run_timestamp") and status == "completed":
            warnings.append(f"line {line_no}: completed record has no run_timestamp")
        role = record.get("monitoring_role")
        if role not in ALLOWED_ROLES:
            errors.append(f"line {line_no}: invalid monitoring_role {role}")
        realism = as_float(record.get("prompt_realism_score"))
        if realism is None or realism < 0 or realism > 1:
            errors.append(f"line {line_no}: prompt_realism_score must be numeric between 0 and 1")
        demand_weight = as_float(record.get("demand_weight"))
        if demand_weight is None or demand_weight <= 0:
            errors.append(f"line {line_no}: demand_weight must be numeric and > 0")
        if not isinstance(record.get("source_basis"), list):
            errors.append(f"line {line_no}: source_basis must be a list")
        overfit = record.get("overfit_risk")
        if overfit not in ALLOWED_OVERFIT_RISKS:
            errors.append(f"line {line_no}: invalid overfit_risk {overfit}")
        prompt_key = (record.get("prompt_id"), record.get("run_iteration"))
        prompt_runs[prompt_key] += 1

    for (prompt_id, iteration), count in prompt_runs.items():
        if prompt_id and iteration and count > 1:
            warnings.append(f"prompt_id {prompt_id} iteration {iteration} appears {count} times")

    if manifest:
        expected = manifest.get("expected_response_count")
        if isinstance(expected, int) and expected != counts["records"]:
            warnings.append(f"manifest expected_response_count={expected}, records={counts['records']}")
        if manifest.get("platform") and manifest.get("platform") != "ChatGPT":
            errors.append(f"manifest platform must be ChatGPT, got {manifest.get('platform')}")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "counts": dict(counts),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_responses", help="Path to raw_responses.jsonl")
    parser.add_argument("--manifest", help="Optional run_manifest.json")
    args = parser.parse_args()

    manifest = None
    if args.manifest:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    print(json.dumps(validate(args.raw_responses, manifest), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
