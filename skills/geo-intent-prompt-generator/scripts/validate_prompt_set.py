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
    "monitoring_role",
    "prompt_realism_score",
    "demand_weight",
    "buyer_journey_stage",
    "source_basis",
    "overfit_risk",
]
BRAND_TYPES = {"unbranded", "branded"}
INTENT_STAGES = {"info", "commercial", "transactional"}
MONITORING_ROLES = {"market_proxy", "buyer_evaluation", "diagnostic_probe", "brand_control"}
BUYER_JOURNEY_STAGES = {"awareness", "evaluation", "selection", "implementation", "retention"}
OVERFIT_RISKS = {"low", "medium", "high"}
MARKET_PROXY_ROLES = {"market_proxy", "buyer_evaluation"}


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


def as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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
    role_counts = Counter()
    journey_counts = Counter()
    overfit_counts = Counter()
    realism_scores = []
    demand_weight_total = 0.0
    market_proxy_weight_total = 0.0
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

        role = prompt.get("monitoring_role")
        if role not in MONITORING_ROLES:
            errors.append(f"{pid} invalid monitoring_role: {role}")
        else:
            role_counts[role] += 1

        journey = prompt.get("buyer_journey_stage")
        if journey not in BUYER_JOURNEY_STAGES:
            errors.append(f"{pid} invalid buyer_journey_stage: {journey}")
        else:
            journey_counts[journey] += 1

        overfit = prompt.get("overfit_risk")
        if overfit not in OVERFIT_RISKS:
            errors.append(f"{pid} invalid overfit_risk: {overfit}")
        else:
            overfit_counts[overfit] += 1

        realism = as_float(prompt.get("prompt_realism_score"))
        if realism is None or realism < 0 or realism > 1:
            errors.append(f"{pid} prompt_realism_score must be numeric between 0 and 1")
        else:
            realism_scores.append(realism)

        demand_weight = as_float(prompt.get("demand_weight"))
        if demand_weight is None or demand_weight <= 0:
            errors.append(f"{pid} demand_weight must be numeric and > 0")
        else:
            demand_weight_total += demand_weight
            if role in MARKET_PROXY_ROLES:
                market_proxy_weight_total += demand_weight

        source_basis = prompt.get("source_basis")
        if not isinstance(source_basis, list) or not source_basis:
            errors.append(f"{pid} source_basis must be a non-empty list")

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
        market_proxy_share = pct(role_counts["market_proxy"] + role_counts["buyer_evaluation"], total)
        market_weight_share = pct(market_proxy_weight_total, demand_weight_total)
        average_realism = round(sum(realism_scores) / len(realism_scores), 3) if realism_scores else 0.0
        if ub < 65:
            warnings.append(f"unbranded share is low for MVP discovery monitoring: {ub}%")
        if br > 35:
            warnings.append(f"branded share is high for MVP discovery monitoring: {br}%")
        if commercial < 35:
            warnings.append(f"commercial share is low: {commercial}%")
        if market_proxy_share < 70:
            warnings.append(f"market_proxy + buyer_evaluation prompt share is low: {market_proxy_share}%")
        if market_weight_share < 75:
            warnings.append(f"market-proxy demand-weight share is low: {market_weight_share}%")
        if average_realism < 0.65:
            warnings.append(f"average prompt_realism_score is low: {average_realism}")
        if pct(overfit_counts["high"], total) > 15:
            warnings.append(f"high overfit_risk prompt share is high: {pct(overfit_counts['high'], total)}%")
    else:
        average_realism = 0.0
        market_weight_share = 0.0

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "topics": len(topic_ids),
            "prompts": total,
            "brand_type": dict(brand_counts),
            "intent_stage": dict(intent_counts),
            "monitoring_role": dict(role_counts),
            "buyer_journey_stage": dict(journey_counts),
            "overfit_risk": dict(overfit_counts),
            "demand_weight_total": round(demand_weight_total, 3),
            "market_proxy_demand_weight_share": market_weight_share,
            "average_prompt_realism_score": average_realism,
        },
    }


def main():
    raw = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    data = json.loads(raw)
    print(json.dumps(validate(data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
