#!/usr/bin/env python3
"""Validate GEO content-writer package outputs."""

import argparse
import json
from pathlib import Path


REQUIRED_FILES = [
    "content_plan.md",
    "content_package.json",
    "qa_report.json",
]

REQUIRED_ASSET_FIELDS = {
    "content_id",
    "asset_type",
    "title",
    "target_topic",
    "monitoring_role_focus",
    "draft_file",
    "recommended_url_slug",
    "status",
    "needs_client_evidence",
}


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
    parser.add_argument("--content-dir", required=True, help="Directory produced by write_content_package.py")
    args = parser.parse_args()

    content_dir = Path(args.content_dir)
    errors = []
    warnings = []

    for filename in REQUIRED_FILES:
        if not (content_dir / filename).exists():
            errors.append(f"Missing required output file: {filename}")

    package = load_json(content_dir / "content_package.json", errors)
    qa_report = load_json(content_dir / "qa_report.json", errors)

    content_plan = content_dir / "content_plan.md"
    if content_plan.exists():
        plan_text = content_plan.read_text(encoding="utf-8")
        if "# GEO Content Plan" not in plan_text:
            errors.append("content_plan.md missing title")
        if "## Generated Assets" not in plan_text:
            errors.append("content_plan.md missing Generated Assets section")

    if package:
        for key in ["package_method", "generated_at", "client_brand", "generated_assets", "coverage"]:
            if key not in package:
                errors.append(f"content_package.json missing key: {key}")
        brand = package.get("client_brand", "")
        assets = package.get("generated_assets", [])
        if not assets:
            errors.append("content_package.json generated_assets is empty")
        seen_ids = set()
        for index, asset in enumerate(assets, start=1):
            missing = sorted(REQUIRED_ASSET_FIELDS - set(asset))
            if missing:
                errors.append(f"asset {index} missing fields: {', '.join(missing)}")
            content_id = asset.get("content_id", "")
            if content_id in seen_ids:
                errors.append(f"Duplicate content_id: {content_id}")
            seen_ids.add(content_id)
            draft_file = asset.get("draft_file", "")
            draft_path = content_dir / draft_file
            if not draft_path.exists():
                errors.append(f"Missing draft file: {draft_file}")
                continue
            text = draft_path.read_text(encoding="utf-8")
            if not text.startswith("---"):
                errors.append(f"{draft_file} missing frontmatter")
            if brand and brand not in text:
                errors.append(f"{draft_file} missing client brand")
            if asset.get("target_topic") and asset["target_topic"] not in text:
                warnings.append(f"{draft_file} does not repeat target topic")
            if "## FAQ" not in text:
                warnings.append(f"{draft_file} missing FAQ section")
            if "## GEO Optimization Notes" not in text:
                warnings.append(f"{draft_file} missing GEO Optimization Notes section")
            if asset.get("needs_client_evidence") and "[CLIENT EVIDENCE NEEDED]" not in text:
                warnings.append(f"{draft_file} needs evidence but lacks evidence placeholder")
        drafts_dir = content_dir / "drafts"
        if not drafts_dir.exists() or not list(drafts_dir.glob("*.md")):
            errors.append("drafts directory is missing or empty")

    if qa_report:
        if "valid" not in qa_report:
            errors.append("qa_report.json missing valid")
        if qa_report.get("errors"):
            errors.extend(f"qa_report error: {item}" for item in qa_report["errors"])
        warnings.extend(f"qa_report warning: {item}" for item in qa_report.get("warnings", []))

    result = {
        "content_dir": str(content_dir),
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
