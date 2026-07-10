#!/usr/bin/env python3
"""Validate a GEO client intake JSON file."""

import json
import sys


REQUIRED_TOP = [
    "source_inventory",
    "client_intake",
    "assumptions",
    "missing_fields",
    "conflicts",
    "confidence",
    "downstream_handoff",
    "intake_summary",
]

REQUIRED_FIELDS = [
    "brand_name",
    "website_domain",
    "product_or_service_direction",
    "target_customer_roles",
    "target_countries_or_regions",
    "languages",
    "target_optimization_platforms",
    "competitor_names",
    "geo_optimization_goals",
    "constraints",
]

FIELD_KEYS = ["value", "status", "sources", "raw_evidence"]
STATUSES = {"confirmed", "inferred", "missing", "conflicting"}
CONFIDENCE = {"high", "medium", "low"}
CRITICAL_FIELDS = {
    "product_or_service_direction",
    "target_countries_or_regions",
    "languages",
    "target_optimization_platforms",
}


def is_empty_value(value):
    return value == "" or value == [] or value is None


def validate(data):
    errors = []
    warnings = []

    for key in REQUIRED_TOP:
        if key not in data:
            errors.append(f"missing top-level field: {key}")

    source_ids = set()
    for index, source in enumerate(data.get("source_inventory", []), start=1):
        sid = source.get("source_id") if isinstance(source, dict) else None
        if not sid:
            errors.append(f"source_inventory[{index}] missing source_id")
        elif sid in source_ids:
            errors.append(f"duplicate source_id: {sid}")
        else:
            source_ids.add(sid)

    intake = data.get("client_intake", {})
    if not isinstance(intake, dict):
        errors.append("client_intake must be an object")
        intake = {}

    for field in REQUIRED_FIELDS:
        item = intake.get(field)
        if not isinstance(item, dict):
            errors.append(f"client_intake.{field} must be an object")
            continue
        for key in FIELD_KEYS:
            if key not in item:
                errors.append(f"client_intake.{field} missing key: {key}")
        status = item.get("status")
        value = item.get("value")
        sources = item.get("sources", [])
        if status not in STATUSES:
            errors.append(f"client_intake.{field} invalid status: {status}")
        if status == "missing" and not is_empty_value(value):
            warnings.append(f"client_intake.{field} has value but status is missing")
        if status in {"confirmed", "conflicting"} and not sources:
            warnings.append(f"client_intake.{field} is {status} but has no sources")
        for sid in sources if isinstance(sources, list) else []:
            if source_ids and sid not in source_ids:
                warnings.append(f"client_intake.{field} references unknown source_id: {sid}")
        if field in CRITICAL_FIELDS and status == "missing":
            warnings.append(f"critical field missing: {field}")

    confidence = data.get("confidence")
    if confidence not in CONFIDENCE:
        errors.append(f"invalid confidence: {confidence}")

    handoff = data.get("downstream_handoff", {})
    if isinstance(handoff, dict):
        ready = handoff.get("ready_for_prompt_generation")
        if not isinstance(ready, bool):
            errors.append("downstream_handoff.ready_for_prompt_generation must be boolean")
        if ready:
            for field in CRITICAL_FIELDS:
                status = intake.get(field, {}).get("status")
                if status == "missing":
                    errors.append(
                        "ready_for_prompt_generation cannot be true when "
                        f"{field} is missing"
                    )
    else:
        errors.append("downstream_handoff must be an object")

    return {"valid": not errors, "errors": errors, "warnings": warnings}


def main():
    raw = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    data = json.loads(raw)
    print(json.dumps(validate(data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
