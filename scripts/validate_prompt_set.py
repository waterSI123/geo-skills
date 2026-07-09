#!/usr/bin/env python3
"""Validate a GEO intent prompt-set JSON file.

Checks structure, required fields, topic references, duplicates, and distribution.
"""

import json
import re
import sys
from collections import Counter


REQUIRED_TOP = [
    "input_summary",
    "website_research_brief",
    "intent_pack",
    "topics",
    "prompt_groups",
    "qa_report",
]
REQUIRED_PROMPT = [
    "prompt_id",
    "prompt",
    "brand_type",
    "intent_stage",
    "persona",
    "market",
    "language",
    "platform",
]
BRAND_TYPES = {"unbranded", "branded"}
INTENT_STAGES = {"info", "commercial", "transactional"}


def norm_prompt(text):
    text = (text or "").lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def flatten(data):
    for group in data.get("prompt_groups", []):
        topic_id = group.get("topic_id")
        for prompt in group.get("prompts", []):
            yield topic_id, prompt


def pct(part, total):
    return round(part * 100.0 / total, 1) if total else 0.0


def validate(data):
    errors = []
    warnings = []

    for key in REQUIRED_TOP:
        if key not in data:
            errors.append(f"missing top-level field: {key}")

    topics = data.get("topics", [])
    if not isinstance(topics, list) or not topics:
        errors.append("topics must be a non-empty list")
        topic_ids = set()
    else:
        topic_ids = {t.get("topic_id") for t in topics if isinstance(t, dict)}

    prompt_ids = set()
    prompt_norms = Counter()
    brand_counts = Counter()
    intent_counts = Counter()
    total = 0

    for topic_id, prompt in flatten(data):
        total += 1
        if topic_id not in topic_ids:
            errors.append(f"prompt group references unknown topic_id: {topic_id}")
        if not isinstance(prompt, dict):
            errors.append(f"prompt under {topic_id} is not an object")
            continue
        for field in REQUIRED_PROMPT:
            if prompt.get(field) in (None, ""):
                errors.append(f"{prompt.get('prompt_id', '(no id)')} missing field: {field}")
        pid = prompt.get("prompt_id")
        if pid in prompt_ids:
            errors.append(f"duplicate prompt_id: {pid}")
        prompt_ids.add(pid)

        b = prompt.get("brand_type")
        if b not in BRAND_TYPES:
            errors.append(f"{pid} invalid brand_type: {b}")
        else:
            brand_counts[b] += 1

        stage = prompt.get("intent_stage")
        if stage not in INTENT_STAGES:
            errors.append(f"{pid} invalid intent_stage: {stage}")
        else:
            intent_counts[stage] += 1

        text = prompt.get("prompt", "")
        n = norm_prompt(text)
        prompt_norms[n] += 1
        if len(text) > 180:
            warnings.append(f"{pid} prompt is long: {len(text)} chars")
        if re.search(r"\bSEO\b|keyword|GEO monitoring|mention our brand", text, re.I):
            warnings.append(f"{pid} may sound like a test harness, not a real user prompt")

    for n, count in prompt_norms.items():
        if n and count > 1:
            errors.append(f"duplicate prompt text after normalization: {n}")

    if total:
        ub = pct(brand_counts["unbranded"], total)
        br = pct(brand_counts["branded"], total)
        commercial = pct(intent_counts["commercial"], total)
        if ub < 65:
            warnings.append(f"unbranded share is low for MVP discovery monitoring: {ub}%")
        if br > 35:
            warnings.append(f"branded share is high for MVP discovery monitoring: {br}%")
        if commercial < 35:
            warnings.append(f"commercial share is low: {commercial}%")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "topics": len(topic_ids),
            "prompts": total,
            "brand_type": dict(brand_counts),
            "intent_stage": dict(intent_counts),
        },
    }


def main():
    raw = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    data = json.loads(raw)
    print(json.dumps(validate(data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
