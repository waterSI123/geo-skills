#!/usr/bin/env python3
"""Validate GEO report-builder outputs."""

import argparse
import json
from pathlib import Path


REQUIRED_FILES = [
    "geo_diagnostic_report.md",
    "geo_diagnostic_report.json",
    "report_brief_for_content_writer.json",
]

REQUIRED_SECTIONS = [
    "## Executive Summary",
    "## Project Scope",
    "## Market-Proxy GEO Visibility Scorecard",
    "## Competitor Comparison",
    "## Topic-Level Diagnosis",
    "## Content Gap Findings",
    "## Risk Findings",
    "## Prioritized GEO Action Plan",
]

REQUIRED_METRICS = [
    "Market Visibility Score",
    "Weighted Market Visibility Score",
    "Market Share Of Voice",
    "Market Average Position",
    "Qualified Recommendation Rate",
    "Sentiment Score",
]


def load_json(path, errors):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"Missing file: {path}")
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {path}: {exc}")
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", required=True, help="Directory produced by build_report.py")
    args = parser.parse_args()

    report_dir = Path(args.report_dir)
    errors = []
    warnings = []

    for filename in REQUIRED_FILES:
        if not (report_dir / filename).exists():
            errors.append(f"Missing required output file: {filename}")

    report_md_path = report_dir / "geo_diagnostic_report.md"
    report_md = ""
    if report_md_path.exists():
        report_md = report_md_path.read_text(encoding="utf-8")
        if "# GEO Diagnostic Report" not in report_md:
            errors.append("Markdown report is missing '# GEO Diagnostic Report'")
        for section in REQUIRED_SECTIONS:
            if section not in report_md:
                errors.append(f"Markdown report missing section: {section}")
        for metric in REQUIRED_METRICS:
            if metric not in report_md:
                errors.append(f"Markdown report missing metric: {metric}")

    report = load_json(report_dir / "geo_diagnostic_report.json", errors)
    brief = load_json(report_dir / "report_brief_for_content_writer.json", errors)

    if report:
        for key in [
            "report_method",
            "generated_at",
            "client",
            "scope",
            "executive_summary",
            "scorecard",
            "market_proxy_scorecard",
            "competitor_comparison",
            "topic_diagnosis",
            "content_gap_findings",
            "risk_findings",
            "action_plan",
        ]:
            if key not in report:
                errors.append(f"geo_diagnostic_report.json missing key: {key}")
        client_brand = report.get("client", {}).get("brand_name", "")
        if not client_brand:
            errors.append("Report JSON missing client.brand_name")
        elif report_md and client_brand not in report_md:
            errors.append("Markdown report does not include the client brand")
        scorecard_metrics = {item.get("metric") for item in report.get("scorecard", [])}
        for metric in REQUIRED_METRICS:
            if metric not in scorecard_metrics:
                errors.append(f"Report JSON scorecard missing metric: {metric}")
        if not report.get("executive_summary"):
            errors.append("Report JSON executive_summary is empty")
        if not report.get("action_plan"):
            warnings.append("Report JSON action_plan is empty")

    if brief:
        for key in [
            "client_brand",
            "website_domain",
            "priority_topics",
            "risk_fixes",
            "content_priorities",
        ]:
            if key not in brief:
                errors.append(f"report_brief_for_content_writer.json missing key: {key}")
        if report and brief.get("client_brand") != report.get("client", {}).get("brand_name"):
            errors.append("Brief client_brand does not match report client brand")
        if not isinstance(brief.get("priority_topics", []), list):
            errors.append("Brief priority_topics must be a list")
        if not isinstance(brief.get("content_priorities", []), list):
            errors.append("Brief content_priorities must be a list")
        for index, topic in enumerate(brief.get("priority_topics", []), start=1):
            for key in ["topic", "opportunity_level", "recommended_assets", "core_message", "suggested_content_angle"]:
                if key not in topic:
                    errors.append(f"Brief priority_topics[{index}] missing key: {key}")

    if not (report_dir / "executive_summary.md").exists():
        warnings.append("executive_summary.md is missing")

    result = {
        "report_dir": str(report_dir),
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
