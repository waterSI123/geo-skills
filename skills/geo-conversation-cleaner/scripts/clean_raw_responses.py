#!/usr/bin/env python3
"""Clean raw ChatGPT GEO monitoring responses into analyzable JSONL."""

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


SUPPORTED_PLATFORM = "ChatGPT"
ALLOWED_STATUSES = {"pending", "completed", "failed", "skipped", "needs_retry"}
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

REFUSAL_PATTERNS = [
    r"\bi can'?t help\b",
    r"\bi can'?t assist\b",
    r"\bi'?m unable to\b",
    r"\bi cannot\b",
    r"\bi don'?t have access\b",
    r"\bas an ai\b.*\b(can'?t|cannot|unable)\b",
]

NON_ANSWER_PATTERNS = [
    r"\bplease log in\b",
    r"\bsign in\b",
    r"\baccess denied\b",
    r"\bsomething went wrong\b",
    r"\bnetwork error\b",
    r"\btry again later\b",
    r"\berror generating response\b",
    r"\brate limit\b",
]

RAW_DEFAULTS = {
    "run_id": "",
    "response_id": "",
    "prompt_id": "",
    "topic_id": "",
    "topic": "",
    "prompt": "",
    "platform": "",
    "market": "",
    "language": "",
    "persona": "",
    "brand_type": "",
    "intent_stage": "",
    "monitoring_role": "market_proxy",
    "prompt_realism_score": 0.7,
    "demand_weight": 1.0,
    "buyer_journey_stage": "",
    "source_basis": [],
    "overfit_risk": "medium",
    "run_status": "",
    "raw_answer": "",
    "model_or_surface": "",
    "account_context": "",
    "operator": "",
    "run_timestamp": "",
    "source_row": None,
    "notes": "",
}

ALLOWED_ROLES = {"market_proxy", "buyer_evaluation", "diagnostic_probe", "brand_control"}
ALLOWED_OVERFIT_RISKS = {"low", "medium", "high"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def iter_jsonl(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            yield line_no, json.loads(text)


def normalize_platform(value):
    raw = (value or "").strip()
    lowered = raw.lower().replace("-", " ")
    if lowered in {"chatgpt", "chat gpt", "gpt", "openai", "openai chatgpt"}:
        return SUPPORTED_PLATFORM, True
    if raw == SUPPORTED_PLATFORM:
        return SUPPORTED_PLATFORM, True
    return raw or "", False


def clean_text(text):
    if text is None:
        return ""
    text = str(text)
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)
    text = text.replace("\u00a0", " ")
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def coerce_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_role(value):
    role = (value or "market_proxy").strip().lower()
    return role if role in ALLOWED_ROLES else "market_proxy"


def normalize_overfit_risk(value):
    risk = (value or "medium").strip().lower()
    return risk if risk in ALLOWED_OVERFIT_RISKS else "medium"


def normalize_source_basis(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass
    return [item.strip() for item in text.split(";") if item.strip()]


def answer_hash(text):
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def word_count(text):
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def matches(patterns, text):
    return any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in patterns)


def base_quality(record, platform_supported):
    flags = []
    status = (record.get("run_status") or "").strip().lower()
    clean_answer = record["clean_answer"]
    if not record.get("prompt_id"):
        flags.append("missing_prompt_id")
    if not record.get("topic_id"):
        flags.append("missing_topic_id")
    if not record.get("run_timestamp") and status == "completed":
        flags.append("missing_timestamp")

    if not platform_supported:
        flags.append("unsupported_platform")
        return "unsupported_platform", False, flags
    if status == "failed":
        flags.append("failed_status")
        return "failed_run", False, flags
    if status == "skipped":
        flags.append("skipped_status")
        return "skipped_run", False, flags
    if status in {"pending", "needs_retry"}:
        flags.append("pending_status")
        return "needs_retry", False, flags
    if status != "completed":
        flags.append("pending_status")
        return "needs_retry", False, flags
    if not clean_answer:
        flags.append("missing_raw_answer")
        return "empty_answer", False, flags
    if matches(NON_ANSWER_PATTERNS, clean_answer):
        if matches([r"\blog in\b", r"\bsign in\b", r"\baccess denied\b"], clean_answer):
            flags.append("login_or_access_issue")
        else:
            flags.append("network_or_system_error")
        return "non_answer", False, flags
    if matches(REFUSAL_PATTERNS, clean_answer):
        flags.append("possible_refusal")
        return "refusal_or_cannot_answer", False, flags
    if len(clean_answer) < 80:
        flags.append("too_short")
        return "too_short", False, flags
    return "analyzable", True, flags


def clean_records(raw_path):
    cleaned = []
    for line_no, raw in iter_jsonl(raw_path):
        record = {key: raw.get(key, default) for key, default in RAW_DEFAULTS.items()}
        if record["source_row"] is None:
            record["source_row"] = raw.get("source_row", line_no)
        platform, platform_supported = normalize_platform(record.get("platform"))
        record["platform"] = platform
        record["run_status"] = (record.get("run_status") or "").strip().lower()
        record["monitoring_role"] = normalize_role(record.get("monitoring_role"))
        record["prompt_realism_score"] = min(1.0, max(0.0, coerce_float(record.get("prompt_realism_score"), 0.7)))
        record["demand_weight"] = max(0.01, coerce_float(record.get("demand_weight"), 1.0))
        record["source_basis"] = normalize_source_basis(record.get("source_basis"))
        record["overfit_risk"] = normalize_overfit_risk(record.get("overfit_risk"))
        record["raw_answer"] = raw.get("raw_answer", "")
        clean_answer = clean_text(record["raw_answer"])
        record["clean_answer"] = clean_answer
        record["answer_text_hash"] = answer_hash(clean_answer)
        record["answer_length_chars"] = len(clean_answer)
        record["answer_length_words"] = word_count(clean_answer)
        status, is_analyzable, flags = base_quality(record, platform_supported)
        record["is_analyzable"] = is_analyzable
        record["answer_quality_status"] = status
        record["quality_flags"] = flags
        record["duplicate_group_id"] = ""
        record["is_duplicate_answer"] = False
        record["cleaning_notes"] = []
        cleaned.append(record)

    hash_to_indices = defaultdict(list)
    for index, record in enumerate(cleaned):
        if record["is_analyzable"] and record["answer_text_hash"]:
            hash_to_indices[record["answer_text_hash"]].append(index)

    duplicate_group_counter = 1
    for indices in hash_to_indices.values():
        if len(indices) <= 1:
            continue
        group_id = f"D{duplicate_group_counter:03d}"
        duplicate_group_counter += 1
        for position, index in enumerate(indices):
            cleaned[index]["duplicate_group_id"] = group_id
            if position > 0:
                cleaned[index]["is_duplicate_answer"] = True
                cleaned[index]["is_analyzable"] = False
                cleaned[index]["answer_quality_status"] = "duplicate_answer"
                if "duplicate_text" not in cleaned[index]["quality_flags"]:
                    cleaned[index]["quality_flags"].append("duplicate_text")
                cleaned[index]["cleaning_notes"].append("Exact duplicate of an earlier analyzable answer.")

    return cleaned


def write_jsonl(path, records):
    with Path(path).open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_report(records, input_file, output_file, manifest=None):
    status_counts = Counter(record["answer_quality_status"] for record in records)
    flag_counts = Counter(flag for record in records for flag in record.get("quality_flags", []))
    analyzable = sum(1 for record in records if record.get("is_analyzable"))
    duplicate_groups = len({record["duplicate_group_id"] for record in records if record.get("duplicate_group_id")})
    warnings = []
    if manifest and isinstance(manifest.get("expected_response_count"), int):
        expected = manifest["expected_response_count"]
        if expected != len(records):
            warnings.append(f"Manifest expected {expected} responses but cleaned {len(records)} records.")
    return {
        "input_file": str(input_file),
        "output_file": str(output_file),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "records": len(records),
            "analyzable": analyzable,
            "not_analyzable": len(records) - analyzable,
        },
        "quality_status_counts": dict(status_counts),
        "quality_flag_counts": dict(flag_counts),
        "duplicate_groups": duplicate_groups,
        "warnings": warnings,
        "recommended_next_skill": "geo-response-analyzer",
    }


def write_markdown_report(path, report):
    lines = [
        "# GEO Conversation Cleaning Report",
        "",
        f"Input: `{report['input_file']}`",
        f"Output: `{report['output_file']}`",
        "",
        "## Counts",
        "",
    ]
    for key, value in report["counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Quality Status", ""])
    for key, value in sorted(report["quality_status_counts"].items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Quality Flags", ""])
    if report["quality_flag_counts"]:
        for key, value in sorted(report["quality_flag_counts"].items()):
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- None")
    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        lines.extend(f"- {warning}" for warning in report["warnings"])
    else:
        lines.append("- None")
    lines.extend(["", "## Recommended Next Step", "", "Use `geo-response-analyzer`."])
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-responses", required=True, help="Path to raw_responses.jsonl")
    parser.add_argument("--manifest", help="Optional run_manifest.json")
    parser.add_argument("--client-intake", help="Optional client_intake.json; accepted for workflow symmetry")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cleaned_path = output_dir / "cleaned_responses.jsonl"
    report_json_path = output_dir / "cleaning_report.json"
    report_md_path = output_dir / "cleaning_report.md"

    manifest = read_json(args.manifest) if args.manifest else None
    cleaned = clean_records(args.raw_responses)
    write_jsonl(cleaned_path, cleaned)
    report = build_report(cleaned, args.raw_responses, cleaned_path, manifest)
    report_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown_report(report_md_path, report)

    print(
        json.dumps(
            {
                "cleaned_responses": str(cleaned_path),
                "cleaning_report_json": str(report_json_path),
                "cleaning_report_md": str(report_md_path),
                "records": len(cleaned),
                "analyzable": report["counts"]["analyzable"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
