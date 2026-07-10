#!/usr/bin/env python3
"""Validate cleaned ChatGPT GEO response JSONL data."""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


REQUIRED_FIELDS = [
    "run_id",
    "response_id",
    "prompt_id",
    "prompt",
    "platform",
    "run_status",
    "raw_answer",
    "clean_answer",
    "answer_text_hash",
    "answer_length_chars",
    "answer_length_words",
    "is_analyzable",
    "answer_quality_status",
    "quality_flags",
    "duplicate_group_id",
    "is_duplicate_answer",
    "cleaning_notes",
]

QUALITY_STATUSES = {
    "analyzable",
    "empty_answer",
    "failed_run",
    "skipped_run",
    "needs_retry",
    "refusal_or_cannot_answer",
    "non_answer",
    "too_short",
    "duplicate_answer",
    "unsupported_platform",
}


def iter_jsonl(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if text:
                yield line_no, json.loads(text)


def answer_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest() if text else ""


def validate(path):
    errors = []
    warnings = []
    counts = Counter()
    response_ids = set()
    duplicate_groups = defaultdict(list)

    for line_no, record in iter_jsonl(path):
        counts["records"] += 1
        if not isinstance(record, dict):
            errors.append(f"line {line_no}: record must be an object")
            continue
        for field in REQUIRED_FIELDS:
            if field not in record:
                errors.append(f"line {line_no}: missing required field {field}")
        response_id = record.get("response_id")
        if response_id:
            if response_id in response_ids:
                errors.append(f"line {line_no}: duplicate response_id {response_id}")
            response_ids.add(response_id)
        status = record.get("answer_quality_status")
        if status not in QUALITY_STATUSES:
            errors.append(f"line {line_no}: invalid answer_quality_status {status}")
        else:
            counts[status] += 1
        if record.get("platform") != "ChatGPT":
            if status != "unsupported_platform":
                errors.append(f"line {line_no}: non-ChatGPT platform must be unsupported_platform")
            else:
                warnings.append(f"line {line_no}: unsupported non-ChatGPT platform preserved")
        elif status == "unsupported_platform":
            errors.append(f"line {line_no}: ChatGPT record cannot be unsupported_platform")
        if not isinstance(record.get("is_analyzable"), bool):
            errors.append(f"line {line_no}: is_analyzable must be boolean")
        if record.get("is_analyzable") and status != "analyzable":
            errors.append(f"line {line_no}: only analyzable status can have is_analyzable=true")
        if status == "analyzable" and not record.get("is_analyzable"):
            errors.append(f"line {line_no}: analyzable status should have is_analyzable=true")
        clean_answer = record.get("clean_answer") or ""
        expected_hash = answer_hash(clean_answer)
        if record.get("answer_text_hash") != expected_hash:
            errors.append(f"line {line_no}: answer_text_hash does not match clean_answer")
        if record.get("answer_length_chars") != len(clean_answer):
            errors.append(f"line {line_no}: answer_length_chars does not match clean_answer")
        if not isinstance(record.get("quality_flags"), list):
            errors.append(f"line {line_no}: quality_flags must be a list")
        if not isinstance(record.get("cleaning_notes"), list):
            errors.append(f"line {line_no}: cleaning_notes must be a list")
        if record.get("run_status") == "completed" and not clean_answer and status != "empty_answer":
            warnings.append(f"line {line_no}: completed empty answer should be empty_answer")
        if status == "duplicate_answer" and not record.get("is_duplicate_answer"):
            errors.append(f"line {line_no}: duplicate_answer should set is_duplicate_answer=true")
        group_id = record.get("duplicate_group_id")
        if group_id:
            duplicate_groups[group_id].append(line_no)

    for group_id, lines in duplicate_groups.items():
        if len(lines) < 2:
            warnings.append(f"duplicate_group_id {group_id} has only one record")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "counts": dict(counts),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cleaned_responses", help="Path to cleaned_responses.jsonl")
    args = parser.parse_args()
    print(json.dumps(validate(args.cleaned_responses), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
