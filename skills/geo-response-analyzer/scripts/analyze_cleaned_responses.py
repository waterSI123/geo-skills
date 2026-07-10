#!/usr/bin/env python3
"""Analyze cleaned ChatGPT GEO responses into brand visibility metrics."""

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


ANALYSIS_METHOD = "rule_based_v1"
SUPPORTED_PLATFORM = "ChatGPT"
MONITORING_ROLES = {"market_proxy", "buyer_evaluation", "diagnostic_probe", "brand_control"}
MARKET_PROXY_ROLES = {"market_proxy", "buyer_evaluation"}
ROLE_DEFAULT_DEMAND_WEIGHTS = {
    "market_proxy": 1.0,
    "buyer_evaluation": 0.75,
    "diagnostic_probe": 0.35,
    "brand_control": 0.25,
}
OVERFIT_RISKS = {"low", "medium", "high"}

RECOMMENDATION_KEYWORDS = [
    "recommend",
    "recommended",
    "best",
    "top",
    "good option",
    "great option",
    "suitable",
    "ideal",
    "strong choice",
    "worth considering",
    "well suited",
]

POSITIVE_KEYWORDS = [
    "recommended",
    "best",
    "strong",
    "strong choice",
    "ideal",
    "good option",
    "great option",
    "well suited",
    "popular",
    "robust",
    "useful",
    "effective",
]

COMPARISON_KEYWORDS = [
    " vs ",
    "versus",
    "compared with",
    "compared to",
    "alternative to",
    "better than",
    "instead of",
    "similar to",
]

NEGATIVE_KEYWORDS = [
    "not recommended",
    "less suitable",
    "limited",
    "lacks",
    "weak",
    "unknown",
    "not enough information",
    "hard to verify",
    "unclear",
]

UNCERTAIN_KEYWORDS = [
    "not enough information",
    "limited information",
    "unknown",
    "unclear",
    "hard to verify",
    "cannot confirm",
    "can't confirm",
    "not widely documented",
]

POLICY_KEYWORDS = [
    "brand guidelines",
    "platform policy",
    "ad policy",
    "compliance",
    "creative compliance",
    "copyright",
    "usage rights",
]

PROOF_ASSET_KEYWORDS = [
    "case studies",
    "pricing",
    "integrations",
    "reviews",
    "examples",
    "testimonials",
    "customer stories",
    "benchmarks",
    "demo",
]

MATURITY_KEYWORDS = [
    "more established",
    "better known",
    "more mature",
    "widely used",
    "more suitable",
    "stronger option",
    "better fit",
]

EXISTENCE_UNCERTAIN_KEYWORDS = [
    "cannot confirm",
    "can't confirm",
    "does not appear to exist",
    "doesn't appear to exist",
    "not sure it exists",
    "hard to verify",
    "not widely documented",
    "no reliable information",
]

FEATURE_CLAIM_KEYWORDS = [
    "offers",
    "supports",
    "features",
    "includes",
    "provides",
    "can generate",
    "can create",
]

OFF_DOMAIN_FEATURE_TERMS = [
    "crm",
    "email marketing",
    "project management",
    "accounting",
    "inventory",
    "help desk",
    "customer support",
    "seo crawler",
    "payment processing",
]

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "ai",
    "tool",
    "platform",
    "service",
    "services",
    "software",
    "solution",
    "solutions",
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def iter_jsonl(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                yield line_no, json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no} is not valid JSON: {exc}") from exc


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path, records):
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in value if item not in (None, "")]
    if isinstance(value, tuple):
        return [item for item in value if item not in (None, "")]
    if isinstance(value, str):
        value = value.strip()
        return [value] if value else []
    return [value]


def coerce_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_monitoring_role(value):
    role = (value or "market_proxy").strip().lower()
    return role if role in MONITORING_ROLES else "market_proxy"


def normalize_overfit_risk(value):
    risk = (value or "medium").strip().lower()
    return risk if risk in OVERFIT_RISKS else "medium"


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


def normalize_prompt_metadata(record):
    role = normalize_monitoring_role(record.get("monitoring_role"))
    realism = min(1.0, max(0.0, coerce_float(record.get("prompt_realism_score"), 0.7)))
    demand_weight = coerce_float(record.get("demand_weight"), ROLE_DEFAULT_DEMAND_WEIGHTS.get(role, 1.0))
    if demand_weight <= 0:
        demand_weight = ROLE_DEFAULT_DEMAND_WEIGHTS.get(role, 1.0)
    return {
        "monitoring_role": role,
        "prompt_realism_score": realism,
        "demand_weight": demand_weight,
        "buyer_journey_stage": str(record.get("buyer_journey_stage") or "").strip(),
        "source_basis": normalize_source_basis(record.get("source_basis")),
        "overfit_risk": normalize_overfit_risk(record.get("overfit_risk")),
    }


def effective_weight(record):
    metadata = normalize_prompt_metadata(record)
    return max(0.0, metadata["demand_weight"] * metadata["prompt_realism_score"])


def is_market_proxy_record(record):
    return normalize_monitoring_role(record.get("monitoring_role")) in MARKET_PROXY_ROLES


def intake_field(intake, field_name, default=None):
    source = intake.get("client_intake", intake) if isinstance(intake, dict) else {}
    field = source.get(field_name, default)
    if isinstance(field, dict) and "value" in field:
        return field.get("value", default)
    return field


def normalize_domain(value):
    if not value:
        return ""
    raw = str(value).strip()
    parsed = urlparse(raw if re.match(r"^[a-z]+://", raw, flags=re.I) else f"//{raw}")
    host = parsed.netloc or parsed.path.split("/")[0]
    host = host.lower().strip()
    if host.startswith("www."):
        host = host[4:]
    return host


def domain_root(domain):
    host = normalize_domain(domain)
    if not host:
        return ""
    parts = host.split(".")
    return parts[0] if parts else host


def split_camel(value):
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", value)


def compact_alnum(value):
    return re.sub(r"[^A-Za-z0-9]+", "", value or "")


def build_aliases(brand, website_domain=""):
    aliases = set()
    brand = str(brand or "").strip()
    if not brand:
        return []
    aliases.add(brand)
    aliases.add(split_camel(brand))
    compact = compact_alnum(brand)
    if compact:
        aliases.add(compact)
        aliases.add(split_camel(compact))
    if "." in brand:
        aliases.add(brand.split(".")[0])
    root = domain_root(website_domain)
    if root:
        aliases.add(root)
        aliases.add(split_camel(root))
    return sorted({alias.strip() for alias in aliases if alias and alias.strip()}, key=lambda item: (-len(item), item.lower()))


def alias_pattern(alias):
    escaped = re.escape(alias.strip())
    escaped = escaped.replace(r"\ ", r"[\s-]+")
    return re.compile(rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])", re.IGNORECASE)


def overlaps(span_a, span_b):
    return span_a[0] < span_b[1] and span_b[0] < span_a[1]


def find_brand_spans(text, aliases):
    candidates = []
    for alias in aliases:
        pattern = alias_pattern(alias)
        for match in pattern.finditer(text):
            candidates.append((match.start(), match.end(), match.group(0)))
    candidates.sort(key=lambda item: (item[0], -(item[1] - item[0])))
    selected = []
    for candidate in candidates:
        if any(overlaps(candidate, (existing[0], existing[1])) for existing in selected):
            continue
        selected.append(candidate)
    return selected


def contains_any(text, keywords):
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def first_keyword(text, keywords):
    lowered = text.lower()
    hits = []
    for keyword in keywords:
        index = lowered.find(keyword.lower())
        if index >= 0:
            hits.append((index, keyword))
    if not hits:
        return ""
    return sorted(hits)[0][1]


def excerpt(text, start=0, end=0, width=180):
    if not text:
        return ""
    if start == 0 and end == 0:
        start = 0
        end = min(len(text), width)
    left = max(0, start - width // 2)
    right = min(len(text), end + width // 2)
    snippet = re.sub(r"\s+", " ", text[left:right]).strip()
    if left > 0:
        snippet = "..." + snippet
    if right < len(text):
        snippet = snippet + "..."
    return snippet


def keyword_excerpt(text, keywords):
    lowered = text.lower()
    for keyword in keywords:
        index = lowered.find(keyword.lower())
        if index >= 0:
            return excerpt(text, index, index + len(keyword))
    return excerpt(text)


def context_for_spans(text, spans, width=180):
    contexts = []
    for start, end, _match in spans:
        contexts.append(excerpt(text, start, end, width=width))
    return contexts


def brand_context_text(text, spans, width=220):
    return "\n".join(context_for_spans(text, spans, width=width))


def line_order(text, brand_spans):
    line_hits = []
    offset = 0
    for line in text.splitlines(True):
        stripped = line.strip()
        is_list_line = bool(re.match(r"^(?:\d+[\.\)]|[-*+])\s+", stripped))
        if is_list_line:
            line_start = offset
            line_end = offset + len(line)
            for brand, spans in brand_spans.items():
                if any(start >= line_start and end <= line_end for start, end, _match in spans):
                    line_hits.append((line_start, brand))
        offset += len(line)
    ordered = []
    for _line_start, brand in sorted(line_hits):
        if brand not in ordered:
            ordered.append(brand)
    return ordered


def infer_brand_order(text, brand_spans):
    ordered = line_order(text, brand_spans)
    if len(ordered) >= 2:
        return ordered
    first_hits = []
    for brand, spans in brand_spans.items():
        if spans:
            first_hits.append((spans[0][0], brand))
    return [brand for _index, brand in sorted(first_hits)]


def classify_sentiment(context):
    if not context:
        return "not_applicable"
    has_positive = contains_any(context, POSITIVE_KEYWORDS)
    has_negative = contains_any(context, NEGATIVE_KEYWORDS)
    has_uncertain = contains_any(context, UNCERTAIN_KEYWORDS)
    if has_positive and (has_negative or has_uncertain):
        return "mixed"
    if has_negative:
        return "negative"
    if has_uncertain:
        return "uncertain"
    if has_positive:
        return "positive"
    return "neutral"


def classify_mention_type(text, context, in_order, sentiment):
    if not context:
        return "not_mentioned"
    if sentiment == "negative":
        return "negative"
    if contains_any(context, RECOMMENDATION_KEYWORDS) or (in_order and contains_any(text[:500], RECOMMENDATION_KEYWORDS)):
        return "recommended"
    if contains_any(context, COMPARISON_KEYWORDS):
        return "compared"
    if in_order:
        return "listed"
    return "mentioned"


def sentiment_value(label):
    if label == "positive":
        return 1
    if label == "negative":
        return -1
    if label in {"neutral", "uncertain", "mixed"}:
        return 0
    return None


def tokenize(value):
    return {token.lower() for token in re.findall(r"[A-Za-z][A-Za-z0-9]+", value or "") if token.lower() not in STOPWORDS}


def service_tokens(product_or_service_direction):
    tokens = set()
    for item in as_list(product_or_service_direction):
        tokens.update(tokenize(str(item)))
    return tokens


def token_overlap_ratio(context, reference_tokens):
    if not reference_tokens:
        return 1.0
    context_tokens = tokenize(context)
    if not context_tokens:
        return 0.0
    return len(context_tokens & reference_tokens) / max(1, len(reference_tokens))


def find_domains(text):
    domains = set()
    for match in re.finditer(r"\b(?:https?://)?(?:www\.)?([A-Za-z0-9-]+\.[A-Za-z]{2,}(?:\.[A-Za-z]{2,})?)\b", text):
        domains.add(normalize_domain(match.group(0)))
    return sorted(domain for domain in domains if domain)


def signal(signal_type, severity, evidence, review_required=False):
    return {
        "type": signal_type,
        "severity": severity,
        "evidence": evidence,
        "review_required": bool(review_required),
    }


def merge_signals(signals):
    seen = set()
    merged = []
    for item in signals:
        key = (item["type"], item.get("evidence", ""))
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)
    return merged


def analyze_signals(text, client_brand, client_entry, competitor_entries, website_domain, service_reference_tokens):
    gaps = []
    risks = []
    client_mentioned = client_entry["mention_count"] > 0
    client_context = client_entry.get("context", "")
    competitor_recommended = [
        entry for entry in competitor_entries
        if entry["mention_count"] > 0 and (entry["mention_type"] == "recommended" or entry["sentiment"] == "positive")
    ]

    if competitor_recommended and not client_mentioned:
        names = ", ".join(entry["brand"] for entry in competitor_recommended[:3])
        gaps.append(signal("competitor_recommended_client_absent", "high", f"Competitors recommended while {client_brand} is absent: {names}."))

    if contains_any(text, POLICY_KEYWORDS) and not client_mentioned:
        gaps.append(signal("policy_compliance_gap", "medium", keyword_excerpt(text, POLICY_KEYWORDS)))

    if contains_any(text, PROOF_ASSET_KEYWORDS):
        gaps.append(signal("proof_asset_gap", "medium", keyword_excerpt(text, PROOF_ASSET_KEYWORDS)))

    if client_mentioned and contains_any(client_context, UNCERTAIN_KEYWORDS):
        gaps.append(signal("unclear_positioning", "medium", keyword_excerpt(client_context, UNCERTAIN_KEYWORDS)))

    maturity_competitors = []
    for entry in competitor_entries:
        if entry["mention_count"] > 0 and contains_any(entry.get("context", ""), MATURITY_KEYWORDS):
            maturity_competitors.append(entry["brand"])
    if maturity_competitors:
        gaps.append(signal("competitor_maturity_advantage", "high", f"Competitors described with maturity advantage: {', '.join(maturity_competitors[:3])}."))

    if client_mentioned and not (client_entry["mention_type"] == "recommended" and client_entry["sentiment"] == "positive"):
        gaps.append(signal("weak_client_recommendation", "medium", client_entry.get("evidence", "")))

    if client_entry.get("sentiment") == "negative":
        risks.append(signal("negative_brand_mention", "high", client_entry.get("evidence", "")))

    if client_mentioned and contains_any(client_context, UNCERTAIN_KEYWORDS):
        risks.append(signal("insufficient_brand_information", "medium", keyword_excerpt(client_context, UNCERTAIN_KEYWORDS)))

    if client_mentioned and contains_any(client_context, EXISTENCE_UNCERTAIN_KEYWORDS):
        risks.append(signal("brand_existence_uncertain", "high", keyword_excerpt(client_context, EXISTENCE_UNCERTAIN_KEYWORDS)))

    official_domain = normalize_domain(website_domain)
    if client_mentioned and official_domain:
        competitor_domains = {normalize_domain(entry["brand"]) for entry in competitor_entries if normalize_domain(entry["brand"])}
        nearby_domains = [
            domain for domain in find_domains(client_context)
            if domain != official_domain and domain not in competitor_domains
        ]
        if nearby_domains and official_domain not in find_domains(client_context):
            risks.append(signal("wrong_website", "high", f"Domain(s) near {client_brand}: {', '.join(nearby_domains)}. Official domain: {official_domain}."))

    if client_mentioned and re.search(r"\b(is an?|as an?|platform for|tool for|software for)\b", client_context, flags=re.I):
        if token_overlap_ratio(client_context, service_reference_tokens) < 0.12:
            risks.append(signal("wrong_category_needs_review", "medium", client_entry.get("evidence", ""), review_required=True))

    if client_mentioned and contains_any(client_context, FEATURE_CLAIM_KEYWORDS) and contains_any(client_context, OFF_DOMAIN_FEATURE_TERMS):
        if token_overlap_ratio(client_context, service_reference_tokens) < 0.2:
            risks.append(signal("wrong_feature_needs_review", "medium", client_entry.get("evidence", ""), review_required=True))

    return merge_signals(gaps), merge_signals(risks)


def build_prompt_lookup(prompt_set):
    lookup = {}
    topic_lookup = {}
    for topic in prompt_set.get("topics", []) if isinstance(prompt_set, dict) else []:
        topic_id = str(topic.get("topic_id", "")).strip()
        if topic_id:
            topic_lookup[topic_id] = topic
    for group in prompt_set.get("prompt_groups", []) if isinstance(prompt_set, dict) else []:
        group_topic_id = str(group.get("topic_id", "")).strip()
        group_topic = group.get("topic", "")
        for prompt in group.get("prompts", []):
            prompt_id = str(prompt.get("prompt_id", "")).strip()
            if not prompt_id:
                continue
            topic_meta = topic_lookup.get(group_topic_id, {})
            merged = {}
            merged.update(topic_meta)
            merged.update({key: value for key, value in group.items() if key != "prompts"})
            merged.update(prompt)
            merged.setdefault("topic_id", group_topic_id)
            merged.setdefault("topic", group_topic)
            lookup[prompt_id] = merged
    return lookup


def merge_response_metadata(record, prompt_lookup):
    prompt_id = str(record.get("prompt_id", "")).strip()
    prompt_meta = prompt_lookup.get(prompt_id, {})
    merged = dict(record)
    for key in [
        "topic_id",
        "topic",
        "persona",
        "market",
        "language",
        "brand_type",
        "intent_stage",
        "monitoring_role",
        "prompt_realism_score",
        "demand_weight",
        "buyer_journey_stage",
        "source_basis",
        "overfit_risk",
        "platform",
        "prompt",
    ]:
        if not merged.get(key) and prompt_meta.get(key):
            merged[key] = prompt_meta.get(key)
    merged.update(normalize_prompt_metadata(merged))
    return merged


def build_tracked_brands(client_brand, competitors, website_domain):
    tracked = []
    tracked.append({
        "brand": client_brand,
        "role": "client",
        "aliases": build_aliases(client_brand, website_domain),
    })
    seen = {client_brand.lower()}
    for competitor in competitors:
        name = str(competitor or "").strip()
        if not name or name.lower() in seen:
            continue
        tracked.append({
            "brand": name,
            "role": "competitor",
            "aliases": build_aliases(name),
        })
        seen.add(name.lower())
    return tracked


def analyze_record(record, tracked_brands, client_brand, competitors, website_domain, service_reference_tokens, prompt_lookup):
    merged = merge_response_metadata(record, prompt_lookup)
    text = merged.get("clean_answer") or ""
    is_analyzable = bool(merged.get("is_analyzable"))
    base = {
        "response_id": merged.get("response_id", ""),
        "prompt_id": merged.get("prompt_id", ""),
        "topic_id": merged.get("topic_id", ""),
        "topic": merged.get("topic", ""),
        "persona": merged.get("persona", ""),
        "market": merged.get("market", ""),
        "language": merged.get("language", ""),
        "brand_type": merged.get("brand_type", ""),
        "intent_stage": merged.get("intent_stage", ""),
        "monitoring_role": merged.get("monitoring_role", "market_proxy"),
        "prompt_realism_score": merged.get("prompt_realism_score", 0.7),
        "demand_weight": merged.get("demand_weight", 1.0),
        "effective_demand_weight": effective_weight(merged),
        "buyer_journey_stage": merged.get("buyer_journey_stage", ""),
        "source_basis": merged.get("source_basis", []),
        "overfit_risk": merged.get("overfit_risk", "medium"),
        "platform": merged.get("platform", SUPPORTED_PLATFORM),
        "is_analyzable": is_analyzable,
        "analysis_method": ANALYSIS_METHOD,
    }
    if not is_analyzable:
        base.update({
            "brands_detected": [],
            "client_brand_mentioned": False,
            "client_brand_position": None,
            "client_brand_mention_type": "not_mentioned",
            "client_brand_sentiment": "not_applicable",
            "recommended_brands_order": [],
            "content_gap_signals": [],
            "risk_signals": [],
            "analysis_notes": ["Skipped because is_analyzable is false."],
        })
        return base

    brand_spans = {item["brand"]: find_brand_spans(text, item["aliases"]) for item in tracked_brands}
    brand_order = infer_brand_order(text, brand_spans)
    brand_positions = {brand: index + 1 for index, brand in enumerate(brand_order)}

    detected = []
    for item in tracked_brands:
        brand = item["brand"]
        spans = brand_spans[brand]
        context = brand_context_text(text, spans)
        sentiment = classify_sentiment(context)
        in_order = brand in brand_positions
        mention_type = classify_mention_type(text, context, in_order, sentiment)
        evidence = context_for_spans(text, spans[:1])[0] if spans else ""
        detected.append({
            "brand": brand,
            "role": item["role"],
            "mention_count": len(spans),
            "first_position": brand_positions.get(brand),
            "mention_type": mention_type,
            "sentiment": sentiment,
            "evidence": evidence,
            "context": context,
        })

    client_entry = next(entry for entry in detected if entry["brand"] == client_brand)
    competitor_entries = [entry for entry in detected if entry["brand"] in competitors]
    gaps, risks = analyze_signals(text, client_brand, client_entry, competitor_entries, website_domain, service_reference_tokens)

    public_detected = [
        {key: value for key, value in entry.items() if key != "context"}
        for entry in detected
        if entry["mention_count"] > 0
    ]

    base.update({
        "brands_detected": public_detected,
        "client_brand_mentioned": client_entry["mention_count"] > 0,
        "client_brand_position": client_entry["first_position"],
        "client_brand_mention_type": client_entry["mention_type"],
        "client_brand_sentiment": client_entry["sentiment"],
        "recommended_brands_order": brand_order,
        "content_gap_signals": gaps,
        "risk_signals": risks,
        "analysis_notes": [],
    })
    return base


def collect_brand_entries(analysis_records, tracked_brands):
    entries_by_brand = {item["brand"]: [] for item in tracked_brands}
    for record in analysis_records:
        if not record.get("is_analyzable"):
            continue
        entry_map = {entry["brand"]: entry for entry in record.get("brands_detected", [])}
        for item in tracked_brands:
            brand = item["brand"]
            entries_by_brand[brand].append(entry_map.get(brand, {
                "brand": brand,
                "role": item["role"],
                "mention_count": 0,
                "first_position": None,
                "mention_type": "not_mentioned",
                "sentiment": "not_applicable",
                "evidence": "",
            }))
    return entries_by_brand


def rank_metric(metrics, value_key, rank_key, descending=True):
    ranked = [item for item in metrics if item.get(value_key) is not None]
    ranked.sort(key=lambda item: item[value_key], reverse=descending)
    previous_value = object()
    previous_rank = 0
    for index, item in enumerate(ranked, start=1):
        value = item[value_key]
        if value != previous_value:
            previous_rank = index
            previous_value = value
        item[rank_key] = previous_rank
    for item in metrics:
        if item.get(value_key) is None:
            item[rank_key] = None


def round_or_none(value, places=4):
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return round(value, places)


def compute_brand_metrics(analysis_records, tracked_brands):
    analyzable_records = [record for record in analysis_records if record.get("is_analyzable")]
    brand_mentioning_records = [
        record for record in analyzable_records
        if any(entry.get("mention_count", 0) > 0 for entry in record.get("brands_detected", []))
    ]
    brand_mentioning_denominator = len(brand_mentioning_records)
    total_mentions = sum(entry.get("mention_count", 0) for record in analyzable_records for entry in record.get("brands_detected", []))
    brand_mentioning_weight_denominator = sum(effective_weight(record) for record in brand_mentioning_records)
    total_weighted_mentions = sum(
        entry.get("mention_count", 0) * effective_weight(record)
        for record in analyzable_records
        for entry in record.get("brands_detected", [])
    )
    entries_by_brand = collect_brand_entries(analysis_records, tracked_brands)
    metrics = []

    for item in tracked_brands:
        brand = item["brand"]
        entries = entries_by_brand[brand]
        mentioned_entries = [entry for entry in entries if entry.get("mention_count", 0) > 0]
        positions = [entry["first_position"] for entry in mentioned_entries if entry.get("first_position") is not None]
        sentiment_values = [sentiment_value(entry.get("sentiment")) for entry in mentioned_entries]
        sentiment_values = [value for value in sentiment_values if value is not None]
        mention_occurrences = sum(entry.get("mention_count", 0) for entry in entries)
        responses_mentioned = len(mentioned_entries)
        positive = sum(1 for entry in mentioned_entries if entry.get("sentiment") == "positive")
        neutral = sum(1 for entry in mentioned_entries if entry.get("sentiment") == "neutral")
        negative = sum(1 for entry in mentioned_entries if entry.get("sentiment") == "negative")
        mixed = sum(1 for entry in mentioned_entries if entry.get("sentiment") == "mixed")
        uncertain = sum(1 for entry in mentioned_entries if entry.get("sentiment") == "uncertain")
        weighted_responses_mentioned = 0.0
        weighted_mentions = 0.0
        weighted_position_sum = 0.0
        weighted_position_denominator = 0.0
        qualified_recommendation_weight = 0.0
        mentioned_weight_denominator = 0.0

        for record in analyzable_records:
            weight = effective_weight(record)
            entry = next((candidate for candidate in record.get("brands_detected", []) if candidate.get("brand") == brand), None)
            if not entry or entry.get("mention_count", 0) <= 0:
                continue
            weighted_responses_mentioned += weight
            weighted_mentions += entry.get("mention_count", 0) * weight
            mentioned_weight_denominator += weight
            if entry.get("first_position") is not None:
                weighted_position_sum += entry["first_position"] * weight
                weighted_position_denominator += weight
            if entry.get("mention_type") == "recommended" and entry.get("sentiment") in {"positive", "neutral"}:
                qualified_recommendation_weight += weight

        metric = {
            "brand": brand,
            "role": item["role"],
            "responses_mentioned": responses_mentioned,
            "visibility_score": round_or_none(responses_mentioned / brand_mentioning_denominator if brand_mentioning_denominator else 0.0),
            "visibility_rank": None,
            "weighted_responses_mentioned": round_or_none(weighted_responses_mentioned),
            "weighted_visibility_score": round_or_none(weighted_responses_mentioned / brand_mentioning_weight_denominator if brand_mentioning_weight_denominator else 0.0),
            "weighted_visibility_rank": None,
            "mention_occurrences": mention_occurrences,
            "share_of_voice": round_or_none(mention_occurrences / total_mentions if total_mentions else 0.0),
            "share_of_voice_rank": None,
            "weighted_mention_occurrences": round_or_none(weighted_mentions),
            "weighted_share_of_voice": round_or_none(weighted_mentions / total_weighted_mentions if total_weighted_mentions else 0.0),
            "weighted_share_of_voice_rank": None,
            "average_position": round_or_none(sum(positions) / len(positions) if positions else None),
            "average_position_rank": None,
            "weighted_average_position": round_or_none(weighted_position_sum / weighted_position_denominator if weighted_position_denominator else None),
            "weighted_average_position_rank": None,
            "top_3_rate": round_or_none(sum(1 for position in positions if position <= 3) / brand_mentioning_denominator if brand_mentioning_denominator else 0.0),
            "sentiment_score": round_or_none(sum(sentiment_values) / len(sentiment_values) if sentiment_values else None),
            "sentiment_rank": None,
            "qualified_recommendation_rate": round_or_none(
                qualified_recommendation_weight / mentioned_weight_denominator if mentioned_weight_denominator else 0.0
            ),
            "qualified_recommendation_rank": None,
            "positive_mentions": positive,
            "neutral_mentions": neutral,
            "negative_mentions": negative,
            "mixed_mentions": mixed,
            "uncertain_mentions": uncertain,
            "not_mentioned_count": len(analyzable_records) - responses_mentioned,
        }
        metrics.append(metric)

    rank_metric(metrics, "visibility_score", "visibility_rank", descending=True)
    rank_metric(metrics, "weighted_visibility_score", "weighted_visibility_rank", descending=True)
    rank_metric(metrics, "share_of_voice", "share_of_voice_rank", descending=True)
    rank_metric(metrics, "weighted_share_of_voice", "weighted_share_of_voice_rank", descending=True)
    rank_metric(metrics, "average_position", "average_position_rank", descending=False)
    rank_metric(metrics, "weighted_average_position", "weighted_average_position_rank", descending=False)
    rank_metric(metrics, "sentiment_score", "sentiment_rank", descending=True)
    rank_metric(metrics, "qualified_recommendation_rate", "qualified_recommendation_rank", descending=True)
    return metrics, analyzable_records, brand_mentioning_records, total_mentions, total_weighted_mentions


def ranking_list(metrics, key, rank_key):
    return [
        {
            "rank": item.get(rank_key),
            "brand": item["brand"],
            "role": item["role"],
            "value": item.get(key),
        }
        for item in sorted(metrics, key=lambda item: (item.get(rank_key) is None, item.get(rank_key) or 9999, item["brand"].lower()))
    ]


def role_breakdown(records):
    counts = Counter()
    analyzable_counts = Counter()
    weight_totals = Counter()
    for record in records:
        role = normalize_monitoring_role(record.get("monitoring_role"))
        counts[role] += 1
        if record.get("is_analyzable"):
            analyzable_counts[role] += 1
            weight_totals[role] += effective_weight(record)
    return {
        role: {
            "records": counts.get(role, 0),
            "analyzable_records": analyzable_counts.get(role, 0),
            "effective_demand_weight": round_or_none(weight_totals.get(role, 0.0)),
        }
        for role in sorted(MONITORING_ROLES)
        if counts.get(role, 0) or analyzable_counts.get(role, 0)
    }


def client_metric_from(metrics, client_brand):
    return next((item for item in metrics if item["brand"] == client_brand), None)


def build_primary_kpis(market_metrics, client_brand):
    client = client_metric_from(market_metrics, client_brand)
    if not client:
        return {}
    return {
        "client_brand": client_brand,
        "primary_scope": "market_proxy_and_buyer_evaluation",
        "market_visibility_score": client.get("visibility_score"),
        "market_visibility_rank": client.get("visibility_rank"),
        "weighted_market_visibility_score": client.get("weighted_visibility_score"),
        "weighted_market_visibility_rank": client.get("weighted_visibility_rank"),
        "market_share_of_voice": client.get("share_of_voice"),
        "market_share_of_voice_rank": client.get("share_of_voice_rank"),
        "weighted_market_share_of_voice": client.get("weighted_share_of_voice"),
        "weighted_market_share_of_voice_rank": client.get("weighted_share_of_voice_rank"),
        "market_average_position": client.get("average_position"),
        "market_average_position_rank": client.get("average_position_rank"),
        "weighted_market_average_position": client.get("weighted_average_position"),
        "weighted_market_average_position_rank": client.get("weighted_average_position_rank"),
        "qualified_recommendation_rate": client.get("qualified_recommendation_rate"),
        "qualified_recommendation_rank": client.get("qualified_recommendation_rank"),
        "market_sentiment_score": client.get("sentiment_score"),
        "market_sentiment_rank": client.get("sentiment_rank"),
    }


def build_visibility_analysis(analysis_records, tracked_brands, client_brand, input_files):
    metrics, analyzable_records, brand_mentioning_records, total_mentions, total_weighted_mentions = compute_brand_metrics(analysis_records, tracked_brands)
    market_records = [record for record in analysis_records if is_market_proxy_record(record)]
    market_metrics, market_analyzable_records, market_brand_mentioning_records, market_total_mentions, market_weighted_mentions = compute_brand_metrics(market_records, tracked_brands)
    return {
        "analysis_method": ANALYSIS_METHOD,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_files": input_files,
        "scope": {
            "platform": SUPPORTED_PLATFORM,
            "analyzable_response_count": len(analyzable_records),
            "brand_mentioning_response_count": len(brand_mentioning_records),
            "total_tracked_brand_mentions": total_mentions,
            "total_weighted_tracked_brand_mentions": round_or_none(total_weighted_mentions),
            "monitoring_role_breakdown": role_breakdown(analysis_records),
            "primary_kpi_scope": "market_proxy_and_buyer_evaluation",
            "market_proxy_response_count": len(market_analyzable_records),
            "market_proxy_brand_mentioning_response_count": len(market_brand_mentioning_records),
            "market_proxy_total_tracked_brand_mentions": market_total_mentions,
            "market_proxy_total_weighted_tracked_brand_mentions": round_or_none(market_weighted_mentions),
            "tracked_brands": [{"brand": item["brand"], "role": item["role"]} for item in tracked_brands],
        },
        "client_brand": client_brand,
        "primary_kpis": build_primary_kpis(market_metrics, client_brand),
        "brand_metrics": metrics,
        "market_proxy_metrics": market_metrics,
        "rankings": {
            "visibility": ranking_list(metrics, "visibility_score", "visibility_rank"),
            "weighted_visibility": ranking_list(metrics, "weighted_visibility_score", "weighted_visibility_rank"),
            "share_of_voice": ranking_list(metrics, "share_of_voice", "share_of_voice_rank"),
            "weighted_share_of_voice": ranking_list(metrics, "weighted_share_of_voice", "weighted_share_of_voice_rank"),
            "average_position": ranking_list(metrics, "average_position", "average_position_rank"),
            "weighted_average_position": ranking_list(metrics, "weighted_average_position", "weighted_average_position_rank"),
            "sentiment": ranking_list(metrics, "sentiment_score", "sentiment_rank"),
            "qualified_recommendation": ranking_list(metrics, "qualified_recommendation_rate", "qualified_recommendation_rank"),
            "market_proxy_visibility": ranking_list(market_metrics, "visibility_score", "visibility_rank"),
            "market_proxy_weighted_visibility": ranking_list(market_metrics, "weighted_visibility_score", "weighted_visibility_rank"),
        },
    }


def signal_counts(records, signal_field):
    counts = Counter()
    for record in records:
        for item in record.get(signal_field, []):
            counts[item["type"]] += 1
    return dict(sorted(counts.items()))


def topic_key(record):
    topic_id = record.get("topic_id") or ""
    topic = record.get("topic") or ""
    if topic_id or topic:
        return f"{topic_id}::{topic}"
    return f"prompt::{record.get('prompt_id', '')}"


def build_topic_analysis(analysis_records, tracked_brands, client_brand):
    grouped = defaultdict(list)
    for record in analysis_records:
        if record.get("is_analyzable"):
            grouped[topic_key(record)].append(record)

    topics = []
    for _key, records in grouped.items():
        sample = records[0]
        metrics, analyzable_records, brand_mentioning_records, _total_mentions, _weighted_mentions = compute_brand_metrics(records, tracked_brands)
        market_records = [record for record in records if is_market_proxy_record(record)]
        if market_records:
            opportunity_records = market_records
        else:
            opportunity_records = records
        market_metrics, market_analyzable_records, market_brand_mentioning_records, _market_mentions, _market_weighted_mentions = compute_brand_metrics(opportunity_records, tracked_brands)
        metric_by_brand = {item["brand"]: item for item in metrics}
        market_metric_by_brand = {item["brand"]: item for item in market_metrics}
        client_metric = metric_by_brand[client_brand]
        market_client_metric = market_metric_by_brand.get(client_brand, client_metric)
        brand_denominator = len(market_brand_mentioning_records) or len(market_analyzable_records)
        client_mentioned_records = [record for record in opportunity_records if record.get("client_brand_mentioned")]
        weak_client_records = [
            record for record in client_mentioned_records
            if record.get("client_brand_mention_type") != "recommended" or record.get("client_brand_sentiment") != "positive"
        ]
        client_absent_count = sum(1 for record in (market_brand_mentioning_records or market_analyzable_records) if not record.get("client_brand_mentioned"))
        client_absent_rate = client_absent_count / brand_denominator if brand_denominator else 0.0
        weak_rate = len(weak_client_records) / len(client_mentioned_records) if client_mentioned_records else 0.0

        strong_competitors = []
        for metric in market_metrics:
            if metric["role"] != "competitor":
                continue
            stronger = False
            if metric["weighted_visibility_score"] > market_client_metric["weighted_visibility_score"]:
                stronger = True
            if metric["weighted_share_of_voice"] > market_client_metric["weighted_share_of_voice"]:
                stronger = True
            if market_client_metric["average_position"] is None and metric["average_position"] is not None:
                stronger = True
            elif metric["average_position"] is not None and market_client_metric["average_position"] is not None and metric["average_position"] < market_client_metric["average_position"]:
                stronger = True
            if metric["sentiment_score"] is not None and (market_client_metric["sentiment_score"] is None or metric["sentiment_score"] > market_client_metric["sentiment_score"]):
                stronger = True
            if stronger:
                strong_competitors.append({
                    "brand": metric["brand"],
                    "visibility_score": metric["visibility_score"],
                    "weighted_visibility_score": metric["weighted_visibility_score"],
                    "share_of_voice": metric["share_of_voice"],
                    "weighted_share_of_voice": metric["weighted_share_of_voice"],
                    "average_position": metric["average_position"],
                    "sentiment_score": metric["sentiment_score"],
                })

        gap_counts = signal_counts(records, "content_gap_signals")
        risk_counts = signal_counts(records, "risk_signals")
        high_risk = any(item.get("severity") == "high" for record in records for item in record.get("risk_signals", []))
        repeated_gaps = sum(gap_counts.values()) >= 2
        if (client_absent_rate >= 0.6 and strong_competitors) or high_risk:
            level = "high"
        elif client_absent_rate >= 0.3 or weak_rate >= 0.5 or repeated_gaps:
            level = "medium"
        else:
            level = "low"

        topics.append({
            "topic_id": sample.get("topic_id", ""),
            "topic": sample.get("topic", "") or sample.get("prompt_id", ""),
            "response_count": len(analyzable_records),
            "brand_mentioning_response_count": len(brand_mentioning_records),
            "market_response_count": len(market_analyzable_records),
            "market_brand_mentioning_response_count": len(market_brand_mentioning_records),
            "monitoring_role_counts": dict(Counter(normalize_monitoring_role(record.get("monitoring_role")) for record in records)),
            "client_visibility_score": client_metric["visibility_score"],
            "client_share_of_voice": client_metric["share_of_voice"],
            "client_average_position": client_metric["average_position"],
            "client_sentiment_score": client_metric["sentiment_score"],
            "market_client_visibility_score": market_client_metric["visibility_score"],
            "market_weighted_visibility_score": market_client_metric["weighted_visibility_score"],
            "market_client_share_of_voice": market_client_metric["share_of_voice"],
            "market_weighted_share_of_voice": market_client_metric["weighted_share_of_voice"],
            "market_client_average_position": market_client_metric["average_position"],
            "market_qualified_recommendation_rate": market_client_metric["qualified_recommendation_rate"],
            "client_absent_rate": round_or_none(client_absent_rate),
            "weak_recommendation_rate": round_or_none(weak_rate),
            "strong_competitors": sorted(strong_competitors, key=lambda item: (-(item["weighted_visibility_score"] or 0), -(item["weighted_share_of_voice"] or 0), item["brand"].lower())),
            "content_gap_counts": gap_counts,
            "risk_signal_counts": risk_counts,
            "topic_opportunity_level": level,
        })

    level_order = {"high": 0, "medium": 1, "low": 2}
    topics.sort(key=lambda item: (level_order.get(item["topic_opportunity_level"], 9), -item["client_absent_rate"], item["topic"]))
    return {
        "analysis_method": ANALYSIS_METHOD,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topics": topics,
    }


def recommendation_for(signal_type):
    recommendations = {
        "competitor_recommended_client_absent": "Create comparison and category content that positions the client brand in this topic.",
        "policy_compliance_gap": "Add content proving brand-guideline, platform-policy, and compliance handling.",
        "proof_asset_gap": "Add proof assets such as examples, case studies, pricing, integrations, reviews, or demos.",
        "unclear_positioning": "Clarify positioning, target users, use cases, and evidence for the client brand.",
        "competitor_maturity_advantage": "Add trust-building content that addresses maturity, adoption, proof, and suitability.",
        "weak_client_recommendation": "Strengthen content that gives AI systems reasons to recommend the client brand.",
        "negative_brand_mention": "Review the source claim and prepare corrective brand evidence.",
        "insufficient_brand_information": "Publish clearer product information, proof points, documentation, and third-party references.",
        "wrong_category_needs_review": "Manually review the answer and add category clarification content if the classification is wrong.",
        "wrong_website": "Check entity consistency and reinforce the official website/domain in public profiles and content.",
        "wrong_feature_needs_review": "Manually review feature claims and publish authoritative feature documentation.",
        "brand_existence_uncertain": "Add entity validation signals such as official site content, profiles, schema, and third-party mentions.",
    }
    return recommendations.get(signal_type, "Review this signal and decide the next GEO optimization action.")


def build_opportunity_findings(analysis_records):
    grouped = {}
    for record in analysis_records:
        if not record.get("is_analyzable"):
            continue
        for category, field in [("content_gap", "content_gap_signals"), ("risk", "risk_signals")]:
            for item in record.get(field, []):
                key = (category, item["type"], record.get("topic_id", ""), record.get("topic", ""))
                bucket = grouped.setdefault(key, {
                    "category": category,
                    "type": item["type"],
                    "severity": item.get("severity", "medium"),
                    "topic_id": record.get("topic_id", ""),
                    "topic": record.get("topic", ""),
                    "response_ids": [],
                    "evidence": [],
                    "monitoring_roles": Counter(),
                    "review_required": False,
                })
                if item.get("severity") == "high":
                    bucket["severity"] = "high"
                if record.get("response_id"):
                    bucket["response_ids"].append(record["response_id"])
                if item.get("evidence"):
                    bucket["evidence"].append(item["evidence"])
                bucket["monitoring_roles"][normalize_monitoring_role(record.get("monitoring_role"))] += 1
                bucket["review_required"] = bucket["review_required"] or bool(item.get("review_required"))

    findings = []
    severity_order = {"high": 0, "medium": 1, "low": 2}
    for index, bucket in enumerate(sorted(grouped.values(), key=lambda item: (severity_order.get(item["severity"], 9), item["category"], item["type"], item["topic"])), start=1):
        findings.append({
            "finding_id": f"F{index:03d}",
            "type": bucket["type"],
            "category": bucket["category"],
            "severity": bucket["severity"],
            "topic_id": bucket["topic_id"],
            "topic": bucket["topic"],
            "response_count": len(set(bucket["response_ids"])),
            "monitoring_role_counts": dict(bucket["monitoring_roles"]),
            "market_proxy_response_count": sum(count for role, count in bucket["monitoring_roles"].items() if role in MARKET_PROXY_ROLES),
            "evidence_response_ids": sorted(set(bucket["response_ids"]))[:8],
            "evidence_examples": bucket["evidence"][:3],
            "review_required": bucket["review_required"],
            "recommended_next_step": recommendation_for(bucket["type"]),
        })

    return {
        "analysis_method": ANALYSIS_METHOD,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary_counts": {
            "content_gap_signals": signal_counts(analysis_records, "content_gap_signals"),
            "risk_signals": signal_counts(analysis_records, "risk_signals"),
        },
        "findings": findings,
    }


def format_percent(value):
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def build_summary(visibility, topic_analysis, opportunities):
    client_brand = visibility["client_brand"]
    client_metric = next((item for item in visibility["brand_metrics"] if item["brand"] == client_brand), None)
    primary = visibility.get("primary_kpis", {})
    lines = [
        "# GEO Response Analysis Summary",
        "",
        f"Generated At: {visibility['generated_at']}",
        f"Analysis Method: {ANALYSIS_METHOD}",
        f"Client Brand: {client_brand}",
        "",
        "## Overall",
        "",
    ]
    if client_metric:
        lines.extend([
            f"- Market Visibility Score: {format_percent(primary.get('market_visibility_score'))} (rank {primary.get('market_visibility_rank')})",
            f"- Weighted Market Visibility Score: {format_percent(primary.get('weighted_market_visibility_score'))} (rank {primary.get('weighted_market_visibility_rank')})",
            f"- Market Share Of Voice: {format_percent(primary.get('market_share_of_voice'))} (rank {primary.get('market_share_of_voice_rank')})",
            f"- Market Average Position: {primary.get('market_average_position') if primary.get('market_average_position') is not None else 'n/a'} (rank {primary.get('market_average_position_rank')})",
            f"- Qualified Recommendation Rate: {format_percent(primary.get('qualified_recommendation_rate'))} (rank {primary.get('qualified_recommendation_rank')})",
        ])
    lines.extend(["", "## Highest Opportunity Topics", ""])
    high_topics = [topic for topic in topic_analysis["topics"] if topic["topic_opportunity_level"] in {"high", "medium"}][:8]
    if high_topics:
        for topic in high_topics:
            competitors = ", ".join(item["brand"] for item in topic.get("strong_competitors", [])[:3]) or "none"
            lines.append(f"- {topic['topic']}: {topic['topic_opportunity_level']} opportunity, client absent rate {format_percent(topic['client_absent_rate'])}, strong competitors: {competitors}")
    else:
        lines.append("- No high or medium opportunity topics detected.")
    lines.extend(["", "## Top Findings", ""])
    if opportunities["findings"]:
        for finding in opportunities["findings"][:8]:
            lines.append(f"- [{finding['severity']}] {finding['type']} in {finding.get('topic') or 'unassigned topic'}: {finding['recommended_next_step']}")
    else:
        lines.append("- No content gap or risk findings detected.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-intake", required=True, help="client_intake.json from geo-client-intake-normalizer")
    parser.add_argument("--prompt-set", required=True, help="prompt_set.json from geo-intent-prompt-generator")
    parser.add_argument("--cleaned-responses", required=True, help="cleaned_responses.jsonl from geo-conversation-cleaner")
    parser.add_argument("--output-dir", default="analysis_run", help="Output directory")
    args = parser.parse_args()

    client_intake = load_json(args.client_intake)
    prompt_set = load_json(args.prompt_set)
    prompt_lookup = build_prompt_lookup(prompt_set)
    client_brand_values = as_list(intake_field(client_intake, "brand_name"))
    if not client_brand_values:
        raise ValueError("client_intake is missing brand_name")
    client_brand = str(client_brand_values[0]).strip()
    competitors = [str(item).strip() for item in as_list(intake_field(client_intake, "competitor_names")) if str(item).strip()]
    website_domain = str(intake_field(client_intake, "website_domain", "") or "")
    product_direction = intake_field(client_intake, "product_or_service_direction", [])
    service_reference_tokens = service_tokens(product_direction)
    tracked_brands = build_tracked_brands(client_brand, competitors, website_domain)

    cleaned_records = [record for _line_no, record in iter_jsonl(args.cleaned_responses)]
    analysis_records = [
        analyze_record(record, tracked_brands, client_brand, competitors, website_domain, service_reference_tokens, prompt_lookup)
        for record in cleaned_records
    ]

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    analyzed_path = output_dir / "analyzed_responses.jsonl"
    visibility_path = output_dir / "visibility_analysis.json"
    topic_path = output_dir / "topic_analysis.json"
    opportunities_path = output_dir / "opportunity_findings.json"
    summary_path = output_dir / "analysis_summary.md"

    input_files = {
        "client_intake": str(Path(args.client_intake)),
        "prompt_set": str(Path(args.prompt_set)),
        "cleaned_responses": str(Path(args.cleaned_responses)),
    }
    visibility = build_visibility_analysis(analysis_records, tracked_brands, client_brand, input_files)
    topic_analysis = build_topic_analysis(analysis_records, tracked_brands, client_brand)
    opportunities = build_opportunity_findings(analysis_records)
    summary = build_summary(visibility, topic_analysis, opportunities)

    write_jsonl(analyzed_path, analysis_records)
    write_json(visibility_path, visibility)
    write_json(topic_path, topic_analysis)
    write_json(opportunities_path, opportunities)
    summary_path.write_text(summary, encoding="utf-8")

    print(json.dumps({
        "analyzed_responses": str(analyzed_path),
        "visibility_analysis": str(visibility_path),
        "topic_analysis": str(topic_path),
        "opportunity_findings": str(opportunities_path),
        "analysis_summary": str(summary_path),
        "responses": len(analysis_records),
        "analyzable": visibility["scope"]["analyzable_response_count"],
        "brand_mentioning_responses": visibility["scope"]["brand_mentioning_response_count"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
