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
        for field in REQUIRED_KEYS:
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
