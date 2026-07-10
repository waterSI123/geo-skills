#!/usr/bin/env python3
"""Import a completed manual ChatGPT run sheet into raw_responses.jsonl."""

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ALLOWED_STATUSES = {"pending", "completed", "failed", "skipped", "needs_retry"}
ALLOWED_ROLES = {"market_proxy", "buyer_evaluation", "diagnostic_probe", "brand_control"}
ALLOWED_OVERFIT_RISKS = {"low", "medium", "high"}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_status(value):
    status = (value or "pending").strip().lower()
    return status if status in ALLOWED_STATUSES else "needs_retry"


def normalize_platform(value):
    raw = (value or "").strip()
    lowered = raw.lower().replace("-", " ")
    if lowered in {"", "gpt", "chat gpt", "chatgpt", "openai chatgpt", "openai"}:
        return "ChatGPT"
    if lowered == "chatgpt":
        return "ChatGPT"
    raise ValueError(f"Only ChatGPT is supported by this MVP, got: {raw}")


def normalize_role(value):
    role = (value or "market_proxy").strip().lower()
    return role if role in ALLOWED_ROLES else "market_proxy"


def normalize_overfit_risk(value):
    risk = (value or "medium").strip().lower()
    return risk if risk in ALLOWED_OVERFIT_RISKS else "medium"


def parse_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_source_basis(value):
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


def make_record(row, source_row):
    response_id = (row.get("response_id") or f"R{source_row:04d}").strip()
    run_iteration = row.get("run_iteration") or "1"
    try:
        run_iteration_value = int(run_iteration)
    except ValueError:
        run_iteration_value = 1
    return {
        "run_id": (row.get("run_id") or "").strip(),
        "response_id": response_id,
        "row_id": (row.get("row_id") or f"ROW{source_row:04d}").strip(),
        "run_iteration": run_iteration_value,
        "topic_id": (row.get("topic_id") or "").strip(),
        "topic": row.get("topic") or "",
        "prompt_id": (row.get("prompt_id") or "").strip(),
        "prompt": row.get("prompt") or "",
        "platform": normalize_platform(row.get("platform")),
        "market": row.get("market") or "",
        "language": row.get("language") or "",
        "persona": row.get("persona") or "",
        "brand_type": row.get("brand_type") or "",
        "intent_stage": row.get("intent_stage") or "",
        "monitoring_role": normalize_role(row.get("monitoring_role")),
        "prompt_realism_score": parse_float(row.get("prompt_realism_score"), 0.7),
        "demand_weight": parse_float(row.get("demand_weight"), 1.0),
        "buyer_journey_stage": row.get("buyer_journey_stage") or "",
        "source_basis": parse_source_basis(row.get("source_basis")),
        "overfit_risk": normalize_overfit_risk(row.get("overfit_risk")),
        "run_mode": "manual_import",
        "run_status": normalize_status(row.get("run_status")),
        "raw_answer": row.get("raw_answer") or "",
        "answer_url": row.get("answer_url") or "",
        "screenshot_path": row.get("screenshot_path") or "",
        "model_or_surface": row.get("model_or_surface") or "ChatGPT default",
        "account_context": row.get("account_context") or "",
        "operator": row.get("operator") or "",
        "run_timestamp": row.get("run_timestamp") or "",
        "source_row": source_row,
        "notes": row.get("notes") or "",
    }


def write_summary(path, manifest, counts, warnings, output_file):
    run_id = manifest.get("run_id", "") if isinstance(manifest, dict) else ""
    platform = manifest.get("platform", "ChatGPT") if isinstance(manifest, dict) else "ChatGPT"
    lines = [
        "# GEO Monitor Run Summary",
        "",
        f"Run ID: {run_id}",
        f"Platform: {platform}",
        f"Rows: {sum(counts.values())}",
        f"Completed: {counts.get('completed', 0)}",
        f"Failed: {counts.get('failed', 0)}",
        f"Skipped: {counts.get('skipped', 0)}",
        f"Needs Retry: {counts.get('needs_retry', 0)}",
        f"Pending: {counts.get('pending', 0)}",
        "",
        "## Output Files",
        "",
        f"- `{output_file}`",
        "",
        "## Warnings",
        "",
    ]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None")
    lines.extend(["", "## Recommended Next Step", "", "Use `geo-conversation-cleaner` after the raw response dataset is complete."])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-sheet", required=True, help="Completed run_sheet.csv")
    parser.add_argument("--manifest", help="Optional run_manifest.json")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    args = parser.parse_args()

    manifest = load_json(args.manifest) if args.manifest else {}
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "raw_responses.jsonl"
    summary_path = output_dir / "run_summary.md"

    records = []
    warnings = []
    with Path(args.run_sheet).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for source_row, row in enumerate(reader, start=2):
            record = make_record(row, source_row)
            if not record["run_id"] and manifest.get("run_id"):
                record["run_id"] = manifest["run_id"]
            if record["run_status"] == "completed" and not record["raw_answer"].strip():
                warnings.append(f"{record['response_id']} is completed but raw_answer is empty")
            if record["run_status"] in {"failed", "skipped", "needs_retry"} and not record["notes"].strip():
                warnings.append(f"{record['response_id']} is {record['run_status']} but notes is empty")
            records.append(record)

    with raw_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    counts = Counter(record["run_status"] for record in records)
    if not manifest:
        manifest = {"run_id": records[0]["run_id"] if records else "", "platform": "ChatGPT"}
    manifest.setdefault("imported_at", datetime.now(timezone.utc).isoformat())
    write_summary(summary_path, manifest, counts, warnings, raw_path)

    print(json.dumps({"raw_responses": str(raw_path), "run_summary": str(summary_path), "rows": len(records), "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
