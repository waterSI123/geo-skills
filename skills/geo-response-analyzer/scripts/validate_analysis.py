#!/usr/bin/env python3
"""Validate GEO response analysis output files."""

import argparse
import json
from collections import Counter
from pathlib import Path


REQUIRED_FILES = [
    "analyzed_responses.jsonl",
    "visibility_analysis.json",
    "topic_analysis.json",
    "opportunity_findings.json",
]

REQUIRED_ANALYZED_FIELDS = {
    "response_id",
    "prompt_id",
    "is_analyzable",
    "brands_detected",
    "client_brand_mentioned",
    "client_brand_position",
    "client_brand_mention_type",
    "client_brand_sentiment",
    "recommended_brands_order",
    "content_gap_signals",
    "risk_signals",
    "analysis_method",
}

REQUIRED_METRIC_FIELDS = {
    "brand",
    "role",
    "responses_mentioned",
    "visibility_score",
    "visibility_rank",
    "mention_occurrences",
    "share_of_voice",
    "share_of_voice_rank",
    "average_position",
    "average_position_rank",
    "top_3_rate",
    "sentiment_score",
    "sentiment_rank",
}


def load_json(path, errors):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"Missing file: {path}")
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {path}: {exc}")
    return None


def load_jsonl(path, errors):
    records = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                text = line.strip()
                if not text:
                    continue
                try:
                    records.append(json.loads(text))
                except json.JSONDecodeError as exc:
                    errors.append(f"Invalid JSONL in {path}:{line_no}: {exc}")
    except FileNotFoundError:
        errors.append(f"Missing file: {path}")
    return records


def validate_score(value, name, errors):
    if value is None:
        return
    if not isinstance(value, (int, float)):
        errors.append(f"{name} must be numeric or null")
        return
    if value < -1 or value > 1:
        errors.append(f"{name} must be between -1 and 1")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", required=True, help="Directory produced by analyze_cleaned_responses.py")
    args = parser.parse_args()

    analysis_dir = Path(args.analysis_dir)
    errors = []
    warnings = []
    for filename in REQUIRED_FILES:
        if not (analysis_dir / filename).exists():
            errors.append(f"Missing required output file: {filename}")

    analyzed_records = load_jsonl(analysis_dir / "analyzed_responses.jsonl", errors)
    visibility = load_json(analysis_dir / "visibility_analysis.json", errors)
    topic_analysis = load_json(analysis_dir / "topic_analysis.json", errors)
    opportunities = load_json(analysis_dir / "opportunity_findings.json", errors)

    response_ids = []
    for index, record in enumerate(analyzed_records, start=1):
        missing = sorted(REQUIRED_ANALYZED_FIELDS - set(record))
        if missing:
            errors.append(f"analyzed_responses row {index} missing fields: {', '.join(missing)}")
        response_id = record.get("response_id")
        if response_id:
            response_ids.append(response_id)
        if not isinstance(record.get("brands_detected", []), list):
            errors.append(f"analyzed_responses row {index} brands_detected must be a list")
        if not isinstance(record.get("content_gap_signals", []), list):
            errors.append(f"analyzed_responses row {index} content_gap_signals must be a list")
        if not isinstance(record.get("risk_signals", []), list):
            errors.append(f"analyzed_responses row {index} risk_signals must be a list")

    duplicates = [response_id for response_id, count in Counter(response_ids).items() if count > 1]
    if duplicates:
        errors.append(f"Duplicate response_id values: {', '.join(sorted(duplicates)[:10])}")

    if visibility:
        for key in ["analysis_method", "scope", "client_brand", "brand_metrics", "rankings"]:
            if key not in visibility:
                errors.append(f"visibility_analysis.json missing key: {key}")
        metrics = visibility.get("brand_metrics", [])
        if not isinstance(metrics, list) or not metrics:
            errors.append("visibility_analysis.json brand_metrics must be a non-empty list")
        client_metrics = [item for item in metrics if item.get("role") == "client"]
        if len(client_metrics) != 1:
            errors.append("visibility_analysis.json must include exactly one client brand metric")
        for metric in metrics:
            missing = sorted(REQUIRED_METRIC_FIELDS - set(metric))
            if missing:
                errors.append(f"brand metric for {metric.get('brand', '<unknown>')} missing fields: {', '.join(missing)}")
            validate_score(metric.get("visibility_score"), f"{metric.get('brand')} visibility_score", errors)
            validate_score(metric.get("share_of_voice"), f"{metric.get('brand')} share_of_voice", errors)
            validate_score(metric.get("top_3_rate"), f"{metric.get('brand')} top_3_rate", errors)
            validate_score(metric.get("sentiment_score"), f"{metric.get('brand')} sentiment_score", errors)
        scope = visibility.get("scope", {})
        expected_analyzable = sum(1 for record in analyzed_records if record.get("is_analyzable"))
        if scope.get("analyzable_response_count") != expected_analyzable:
            errors.append("visibility scope analyzable_response_count does not match analyzed_responses.jsonl")

    if topic_analysis:
        topics = topic_analysis.get("topics", [])
        if not isinstance(topics, list):
            errors.append("topic_analysis.json topics must be a list")
        for topic in topics:
            for key in ["topic", "response_count", "client_visibility_score", "client_absent_rate", "topic_opportunity_level"]:
                if key not in topic:
                    errors.append(f"topic entry missing key: {key}")
            if topic.get("topic_opportunity_level") not in {"high", "medium", "low"}:
                errors.append(f"Invalid topic_opportunity_level: {topic.get('topic_opportunity_level')}")

    if opportunities:
        findings = opportunities.get("findings", [])
        if not isinstance(findings, list):
            errors.append("opportunity_findings.json findings must be a list")
        for finding in findings:
            for key in ["finding_id", "type", "category", "severity", "response_count", "recommended_next_step"]:
                if key not in finding:
                    errors.append(f"finding missing key: {key}")
            if finding.get("severity") not in {"high", "medium", "low"}:
                errors.append(f"Invalid finding severity: {finding.get('severity')}")

    summary_path = analysis_dir / "analysis_summary.md"
    if not summary_path.exists():
        warnings.append("analysis_summary.md is missing")

    result = {
        "analysis_dir": str(analysis_dir),
        "records": len(analyzed_records),
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
