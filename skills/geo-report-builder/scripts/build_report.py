#!/usr/bin/env python3
"""Build a client-facing GEO diagnostic report from structured analysis outputs."""

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPORT_METHOD = "rule_based_report_builder_v1"


SIGNAL_LABELS = {
    "competitor_recommended_client_absent": "Competitors are recommended while the client brand is absent",
    "policy_compliance_gap": "Policy, compliance, or brand-guideline content gap",
    "proof_asset_gap": "Proof asset gap",
    "unclear_positioning": "Client positioning is unclear",
    "competitor_maturity_advantage": "Competitors are framed as more mature or better known",
    "weak_client_recommendation": "Client is mentioned but not strongly recommended",
    "negative_brand_mention": "Negative brand mention",
    "insufficient_brand_information": "Insufficient public brand information",
    "wrong_category_needs_review": "Possible wrong category classification",
    "wrong_website": "Wrong website or domain risk",
    "wrong_feature_needs_review": "Possible wrong feature attribution",
    "brand_existence_uncertain": "Brand existence or entity confidence risk",
}

ASSET_MAP = {
    "competitor_recommended_client_absent": ["comparison article", "category landing page", "alternative page"],
    "policy_compliance_gap": ["compliance page", "brand-guidelines workflow page", "platform-policy FAQ"],
    "proof_asset_gap": ["case study", "examples gallery", "pricing page", "integrations page", "reviews/testimonials section"],
    "unclear_positioning": ["positioning page", "homepage messaging update", "product overview page"],
    "competitor_maturity_advantage": ["trust page", "customer proof page", "benchmark/comparison page"],
    "weak_client_recommendation": ["recommendation-focused category page", "use-case page", "proof-led FAQ"],
    "negative_brand_mention": ["corrective evidence page", "documentation update"],
    "insufficient_brand_information": ["entity validation page", "product documentation", "third-party profile updates"],
    "wrong_category_needs_review": ["manual review", "category clarification page"],
    "wrong_website": ["official profile updates", "entity consistency update"],
    "wrong_feature_needs_review": ["manual review", "feature documentation update"],
    "brand_existence_uncertain": ["entity validation page", "official profile updates", "third-party mentions"],
}

OWNER_MAP = {
    "competitor_recommended_client_absent": "Content",
    "policy_compliance_gap": "Product marketing",
    "proof_asset_gap": "Marketing",
    "unclear_positioning": "Product marketing",
    "competitor_maturity_advantage": "Marketing",
    "weak_client_recommendation": "Content",
    "negative_brand_mention": "Founder / leadership",
    "insufficient_brand_information": "Marketing",
    "wrong_category_needs_review": "Product marketing",
    "wrong_website": "Web / SEO",
    "wrong_feature_needs_review": "Product marketing",
    "brand_existence_uncertain": "Founder / leadership",
}

RISK_TYPES = {
    "negative_brand_mention",
    "insufficient_brand_information",
    "wrong_category_needs_review",
    "wrong_website",
    "wrong_feature_needs_review",
    "brand_existence_uncertain",
}

SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}
OPPORTUNITY_RANK = {"high": 0, "medium": 1, "low": 2}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def intake_field(intake, field_name, default=None):
    source = intake.get("client_intake", intake) if isinstance(intake, dict) else {}
    field = source.get(field_name, default)
    if isinstance(field, dict) and "value" in field:
        return field.get("value", default)
    return field


def clean_list(values):
    cleaned = []
    for item in as_list(values):
        text = str(item).strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned


def count_prompts(prompt_set):
    prompt_count = 0
    for group in prompt_set.get("prompt_groups", []) if isinstance(prompt_set, dict) else []:
        prompt_count += len(group.get("prompts", []))
    if prompt_count:
        return prompt_count
    return len(prompt_set.get("prompts", [])) if isinstance(prompt_set, dict) else 0


def prompt_scope(prompt_set):
    topics = prompt_set.get("topics", []) if isinstance(prompt_set, dict) else []
    personas = []
    markets = []
    languages = []
    platforms = []
    for group in prompt_set.get("prompt_groups", []) if isinstance(prompt_set, dict) else []:
        if group.get("persona"):
            personas.append(group["persona"])
        for prompt in group.get("prompts", []):
            for source, target in [
                (prompt.get("persona"), personas),
                (prompt.get("market"), markets),
                (prompt.get("language"), languages),
                (prompt.get("platform"), platforms),
            ]:
                if source:
                    target.append(source)
    return {
        "topic_count": len(topics) or len(prompt_set.get("prompt_groups", [])) if isinstance(prompt_set, dict) else 0,
        "prompt_count": count_prompts(prompt_set),
        "personas": sorted(set(personas)),
        "markets": sorted(set(markets)),
        "languages": sorted(set(languages)),
        "platforms": sorted(set(platforms)),
    }


def format_percent(value):
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def format_number(value):
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def sentence(text):
    text = str(text or "").strip()
    if not text:
        return ""
    return text if text.endswith((".", "!", "?")) else text + "."


def human_list(items, fallback="target buyers"):
    cleaned = [str(item).strip() for item in items if str(item).strip()]
    if not cleaned:
        return fallback
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"
    return ", ".join(cleaned[:-1]) + f", and {cleaned[-1]}"


def rank_text(rank):
    return f"#{rank}" if rank is not None else "n/a"


def metric_by_brand(visibility):
    return {item.get("brand"): item for item in visibility.get("brand_metrics", [])}


def client_metric(visibility, client_brand):
    metrics = metric_by_brand(visibility)
    if client_brand in metrics:
        return metrics[client_brand]
    for item in visibility.get("brand_metrics", []):
        if item.get("role") == "client":
            return item
    return {}


def leading_competitor(metrics, value_key, lower_is_better=False):
    competitors = [item for item in metrics if item.get("role") == "competitor" and item.get(value_key) is not None]
    if not competitors:
        return None
    return sorted(competitors, key=lambda item: item[value_key], reverse=not lower_is_better)[0]


def score_interpretation(metric_name, client_value, client_rank, leading):
    if metric_name == "Visibility Score":
        if client_value is None:
            return "Visibility could not be calculated from the supplied analysis."
        if client_value >= 0.7:
            return "The client is consistently surfaced when tracked brands are mentioned."
        if client_value >= 0.35:
            return "The client appears in the sample, but visibility is not yet reliable."
        return "The client is frequently absent when tracked brands are mentioned."
    if metric_name == "Share Of Voice":
        if client_value is None:
            return "Share of voice could not be calculated from the supplied analysis."
        if client_rank == 1:
            return "The client takes a leading share of tracked brand mentions."
        if leading:
            return f"{leading['brand']} takes more of the tracked answer space."
        return "Competitors take more of the tracked answer space."
    if metric_name == "Average Position":
        if client_value is None:
            return "The client was not mentioned often enough to establish an average position."
        if client_rank == 1:
            return "When the client appears, it tends to appear early in the answer."
        return "The client appears behind at least one tracked competitor."
    if metric_name == "Sentiment Score":
        if client_value is None:
            return "The client was not mentioned often enough to score sentiment."
        if client_value > 0.4:
            return "The client is described positively when mentioned."
        if client_value >= 0:
            return "The client is described neutrally or inconsistently, leaving room to strengthen proof."
        return "The client receives negative or uncertain framing in this sample."
    return ""


def build_scorecard(visibility, client_brand):
    metrics = visibility.get("brand_metrics", [])
    client = client_metric(visibility, client_brand)
    specs = [
        ("Visibility Score", "visibility_score", "visibility_rank", False, format_percent),
        ("Share Of Voice", "share_of_voice", "share_of_voice_rank", False, format_percent),
        ("Average Position", "average_position", "average_position_rank", True, format_number),
        ("Sentiment Score", "sentiment_score", "sentiment_rank", False, format_number),
    ]
    scorecard = []
    for label, value_key, rank_key, lower_is_better, formatter in specs:
        leading = leading_competitor(metrics, value_key, lower_is_better=lower_is_better)
        client_value = client.get(value_key)
        scorecard.append({
            "metric": label,
            "client_value": client_value,
            "client_display_value": formatter(client_value),
            "client_rank": client.get(rank_key),
            "leading_competitor": leading.get("brand") if leading else "",
            "leading_competitor_value": leading.get(value_key) if leading else None,
            "interpretation": score_interpretation(label, client_value, client.get(rank_key), leading),
        })
    return scorecard


def competitor_advantage(metric, client):
    advantages = []
    if metric.get("visibility_score", 0) > client.get("visibility_score", 0):
        advantages.append("higher visibility")
    if metric.get("share_of_voice", 0) > client.get("share_of_voice", 0):
        advantages.append("higher share of voice")
    if client.get("average_position") is None and metric.get("average_position") is not None:
        advantages.append("appears where the client is absent")
    elif metric.get("average_position") is not None and client.get("average_position") is not None and metric["average_position"] < client["average_position"]:
        advantages.append("better average position")
    if metric.get("sentiment_score") is not None and (client.get("sentiment_score") is None or metric["sentiment_score"] > client["sentiment_score"]):
        advantages.append("stronger sentiment")
    return ", ".join(advantages) if advantages else "no clear metric advantage in this sample"


def build_competitor_comparison(visibility, client_brand):
    client = client_metric(visibility, client_brand)
    rows = []
    for metric in visibility.get("brand_metrics", []):
        if metric.get("role") != "competitor":
            continue
        rows.append({
            "brand": metric.get("brand", ""),
            "visibility_score": metric.get("visibility_score"),
            "share_of_voice": metric.get("share_of_voice"),
            "average_position": metric.get("average_position"),
            "sentiment_score": metric.get("sentiment_score"),
            "main_advantage": competitor_advantage(metric, client),
        })
    rows.sort(key=lambda item: (-(item.get("visibility_score") or 0), -(item.get("share_of_voice") or 0), item["brand"].lower()))
    return rows


def topic_diagnosis_text(topic):
    competitors = [item.get("brand", "") for item in topic.get("strong_competitors", []) if item.get("brand")]
    if topic.get("client_absent_rate", 0) >= 0.6 and competitors:
        return f"The client is often absent while {', '.join(competitors[:3])} show stronger performance."
    if topic.get("weak_recommendation_rate", 0) >= 0.5:
        return "The client appears in this topic but recommendation strength is weak."
    if competitors:
        return f"Competitors show stronger signals in this topic, led by {', '.join(competitors[:3])}."
    return "The client has usable visibility in this topic, but should keep reinforcing proof and relevance."


def topic_action_text(topic):
    gap_counts = topic.get("content_gap_counts", {})
    if gap_counts.get("policy_compliance_gap"):
        return "Create policy, compliance, or brand-guideline content for this topic."
    if gap_counts.get("competitor_recommended_client_absent"):
        return "Create comparison and category content that positions the client brand alongside recommended competitors."
    if gap_counts.get("proof_asset_gap"):
        return "Add proof assets such as examples, case studies, pricing, integrations, reviews, or demos."
    if gap_counts.get("weak_client_recommendation"):
        return "Strengthen recommendation cues with clearer positioning, use cases, and evidence."
    return "Expand topic-specific content with clear positioning, proof, and competitor-aware messaging."


def build_topic_diagnosis(topic_analysis, limit=10):
    topics = topic_analysis.get("topics", [])
    sorted_topics = sorted(
        topics,
        key=lambda item: (
            OPPORTUNITY_RANK.get(item.get("topic_opportunity_level"), 9),
            -(item.get("client_absent_rate") or 0),
            item.get("topic", ""),
        ),
    )
    rows = []
    for topic in sorted_topics[:limit]:
        rows.append({
            "topic_id": topic.get("topic_id", ""),
            "topic": topic.get("topic", ""),
            "opportunity_level": topic.get("topic_opportunity_level", "low"),
            "client_visibility_score": topic.get("client_visibility_score"),
            "client_absent_rate": topic.get("client_absent_rate"),
            "weak_recommendation_rate": topic.get("weak_recommendation_rate"),
            "strong_competitors": [item.get("brand", "") for item in topic.get("strong_competitors", []) if item.get("brand")],
            "content_gap_counts": topic.get("content_gap_counts", {}),
            "risk_signal_counts": topic.get("risk_signal_counts", {}),
            "diagnosis": topic_diagnosis_text(topic),
            "recommended_action": topic_action_text(topic),
        })
    return rows


def suggested_assets(signal_type):
    return ASSET_MAP.get(signal_type, ["content update"])


def split_findings(opportunities):
    content = []
    risks = []
    for finding in opportunities.get("findings", []):
        target = risks if finding.get("category") == "risk" or finding.get("type") in RISK_TYPES else content
        target.append(finding)
    key = lambda item: (SEVERITY_RANK.get(item.get("severity"), 9), item.get("topic", ""), item.get("type", ""))
    return sorted(content, key=key), sorted(risks, key=key)


def why_gap_matters(signal_type):
    messages = {
        "competitor_recommended_client_absent": "When competitors are recommended and the client is absent, the buyer may never consider the client brand.",
        "policy_compliance_gap": "Policy and compliance language is a decision criterion for many teams; absence here weakens relevance.",
        "proof_asset_gap": "AI answers often rely on visible proof assets when deciding what to recommend.",
        "unclear_positioning": "Unclear positioning makes it harder for AI systems to place the brand in the right buying context.",
        "competitor_maturity_advantage": "Maturity and trust cues can shift recommendations toward better-known competitors.",
        "weak_client_recommendation": "A mention without a strong recommendation is less likely to influence selection.",
    }
    return messages.get(signal_type, "This signal indicates a content or positioning gap that may reduce GEO visibility.")


def risk_business_impact(signal_type):
    messages = {
        "negative_brand_mention": "Negative framing can reduce recommendation strength and trust.",
        "insufficient_brand_information": "Missing public information makes it harder for AI systems to verify and recommend the brand.",
        "wrong_category_needs_review": "A category mismatch can place the brand in the wrong buying conversation.",
        "wrong_website": "Wrong domain/entity signals can confuse attribution and reduce trust.",
        "wrong_feature_needs_review": "Incorrect feature attribution can create buyer confusion and should be checked.",
        "brand_existence_uncertain": "Entity uncertainty is a foundational visibility issue because the brand may not be treated as verifiable.",
    }
    return messages.get(signal_type, "This risk may reduce trust, relevance, or recommendation strength.")


def build_content_gap_findings(findings):
    rows = []
    for finding in findings:
        signal_type = finding.get("type", "")
        rows.append({
            "finding_id": finding.get("finding_id", ""),
            "type": signal_type,
            "label": SIGNAL_LABELS.get(signal_type, signal_type),
            "severity": finding.get("severity", "medium"),
            "topic": finding.get("topic", ""),
            "why_it_matters": why_gap_matters(signal_type),
            "evidence_response_ids": finding.get("evidence_response_ids", []),
            "recommended_action": finding.get("recommended_next_step") or topic_action_text({"content_gap_counts": {signal_type: 1}}),
            "suggested_content_assets": suggested_assets(signal_type),
        })
    return rows


def build_risk_findings(findings):
    rows = []
    for finding in findings:
        signal_type = finding.get("type", "")
        review_required = bool(finding.get("review_required") or signal_type.endswith("_needs_review"))
        rows.append({
            "finding_id": finding.get("finding_id", ""),
            "type": signal_type,
            "label": SIGNAL_LABELS.get(signal_type, signal_type),
            "severity": finding.get("severity", "medium"),
            "topic": finding.get("topic", ""),
            "business_impact": risk_business_impact(signal_type),
            "evidence_response_ids": finding.get("evidence_response_ids", []),
            "recommended_fix": finding.get("recommended_next_step", ""),
            "review_required": review_required,
        })
    return rows


def priority_for_finding(finding):
    signal_type = finding.get("type", "")
    severity = finding.get("severity", "medium")
    if severity == "high" or signal_type in {"brand_existence_uncertain", "wrong_website", "insufficient_brand_information"}:
        return 1
    if signal_type in {"policy_compliance_gap", "competitor_maturity_advantage", "weak_client_recommendation", "competitor_recommended_client_absent"}:
        return 2
    return 3


def expected_impact(signal_type):
    messages = {
        "competitor_recommended_client_absent": "Increase the chance that the client brand appears in category and comparison answers.",
        "policy_compliance_gap": "Improve relevance in compliance and brand-governance prompts.",
        "proof_asset_gap": "Give AI systems stronger evidence to cite or rely on.",
        "unclear_positioning": "Help AI systems classify the brand more clearly.",
        "competitor_maturity_advantage": "Reduce trust and maturity gaps versus better-known competitors.",
        "weak_client_recommendation": "Improve recommendation strength when the brand is already mentioned.",
        "negative_brand_mention": "Reduce negative framing and support corrective evidence.",
        "insufficient_brand_information": "Improve entity confidence and recommendation readiness.",
        "wrong_category_needs_review": "Prevent category confusion after manual verification.",
        "wrong_website": "Improve entity consistency around the official website.",
        "wrong_feature_needs_review": "Prevent feature confusion after manual verification.",
        "brand_existence_uncertain": "Strengthen brand verification signals for AI systems.",
    }
    return messages.get(signal_type, "Improve GEO visibility and answer quality for this opportunity.")


def action_for_finding(finding):
    signal_type = finding.get("type", "")
    label = SIGNAL_LABELS.get(signal_type, signal_type.replace("_", " "))
    if signal_type.endswith("_needs_review"):
        return f"Manually review and correct: {label}"
    if finding.get("category") == "risk" or signal_type in RISK_TYPES:
        return f"Fix risk signal: {label}"
    assets = suggested_assets(signal_type)
    return f"Create or update {assets[0]} to address {label.lower()}"


def build_action_plan(content_findings, risk_findings, topic_rows, limit=12):
    raw_items = []
    for finding in risk_findings + content_findings:
        raw_items.append({
            "priority": priority_for_finding(finding),
            "action": action_for_finding(finding),
            "mapped_topic": finding.get("topic", ""),
            "reason": SIGNAL_LABELS.get(finding.get("type", ""), finding.get("type", "")),
            "expected_geo_impact": expected_impact(finding.get("type", "")),
            "recommended_owner": OWNER_MAP.get(finding.get("type", ""), "Marketing"),
            "next_skill": "manual_review" if finding.get("type", "").endswith("_needs_review") else "geo-content-writer",
            "source_finding_id": finding.get("finding_id", ""),
        })

    for topic in topic_rows:
        if topic.get("opportunity_level") not in {"high", "medium"}:
            continue
        raw_items.append({
            "priority": 1 if topic.get("opportunity_level") == "high" else 2,
            "action": topic.get("recommended_action", ""),
            "mapped_topic": topic.get("topic", ""),
            "reason": topic.get("diagnosis", ""),
            "expected_geo_impact": "Improve visibility, relevance, and recommendation strength for this topic.",
            "recommended_owner": "Content",
            "next_skill": "geo-content-writer",
            "source_finding_id": "",
        })

    deduped = []
    seen = set()
    for item in sorted(raw_items, key=lambda item: (item["priority"], item["mapped_topic"], item["action"])):
        key = (item["action"], item["mapped_topic"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped[:limit]


def build_executive_summary(client_brand, scorecard, topic_rows, content_gaps, risks, action_plan):
    visibility = next((item for item in scorecard if item["metric"] == "Visibility Score"), {})
    sov = next((item for item in scorecard if item["metric"] == "Share Of Voice"), {})
    top_topic = next((item for item in topic_rows if item.get("opportunity_level") in {"high", "medium"}), topic_rows[0] if topic_rows else {})
    top_gap = content_gaps[0] if content_gaps else {}
    top_risk = risks[0] if risks else {}
    next_action = action_plan[0] if action_plan else {}
    bullets = [
        f"In this monitoring sample, {client_brand} has a visibility score of {visibility.get('client_display_value', 'n/a')} and ranks {rank_text(visibility.get('client_rank'))} among tracked brands.",
        f"{client_brand}'s share of voice is {sov.get('client_display_value', 'n/a')}. {sov.get('interpretation', 'Competitor comparison is available in the scorecard.')}",
    ]
    if top_topic:
        bullets.append(f"The highest-priority topic is {top_topic.get('topic')}, where the opportunity level is {top_topic.get('opportunity_level')}.")
    if top_gap:
        bullets.append(f"The most important content gap is: {top_gap.get('label')}.")
    if top_risk:
        bullets.append(f"The most important risk signal is: {top_risk.get('label')}.")
    if next_action:
        bullets.append(f"Recommended next action: {sentence(next_action.get('action')).rstrip('.')}.")
    bullets.append("The next workflow step is to use the content-writer brief to create or update priority GEO content assets.")
    return bullets[:8]


def core_message(client, topic, gap_signals):
    brand = client["brand_name"]
    roles = human_list(client.get("target_customer_roles", [])[:2])
    direction = human_list(client.get("product_or_service_direction", [])[:1], fallback="its product category")
    if "policy_compliance_gap" in gap_signals:
        return f"{brand} helps {roles} evaluate {direction} with clearer brand-guideline, platform-policy, and compliance proof."
    if "proof_asset_gap" in gap_signals:
        return f"{brand} should be supported with examples, proof, and decision assets for {topic}."
    return f"{brand} should be positioned as a credible option for {topic} with clear use cases, proof, and competitor-aware messaging."


def suggested_angle(topic, gap_signals):
    if "competitor_recommended_client_absent" in gap_signals:
        return "Position the client brand directly in the category conversation where competitors are currently recommended."
    if "policy_compliance_gap" in gap_signals:
        return "Show how the client supports brand-safe and policy-aware workflows."
    if "competitor_maturity_advantage" in gap_signals:
        return "Use proof and trust signals to address maturity and adoption concerns."
    return "Strengthen the topic with clear positioning, evidence, and recommendation cues."


def build_content_writer_brief(client, topic_rows, content_gaps, risks, action_plan):
    findings_by_topic = defaultdict(list)
    for finding in content_gaps + risks:
        findings_by_topic[finding.get("topic", "")].append(finding)

    priority_topics = []
    for topic in topic_rows:
        if topic.get("opportunity_level") not in {"high", "medium"} and len(priority_topics) >= 5:
            continue
        topic_findings = findings_by_topic.get(topic.get("topic", ""), [])
        gap_signals = sorted({finding["type"] for finding in topic_findings if finding["type"] not in RISK_TYPES})
        risk_signals = sorted({finding["type"] for finding in topic_findings if finding["type"] in RISK_TYPES})
        assets = []
        for signal_type in gap_signals:
            assets.extend(suggested_assets(signal_type))
        if not assets:
            assets = ["topic landing page", "FAQ section"]
        priority_topics.append({
            "topic": topic.get("topic", ""),
            "opportunity_level": topic.get("opportunity_level", "low"),
            "target_personas": client.get("target_customer_roles", []),
            "strong_competitors": topic.get("strong_competitors", []),
            "content_gap_signals": gap_signals,
            "risk_signals": risk_signals,
            "recommended_assets": sorted(set(assets))[:6],
            "core_message": core_message(client, topic.get("topic", ""), gap_signals),
            "suggested_content_angle": suggested_angle(topic.get("topic", ""), gap_signals),
            "source_finding_ids": [finding.get("finding_id", "") for finding in topic_findings if finding.get("finding_id")],
        })
        if len(priority_topics) >= 8:
            break

    risk_fixes = [
        {
            "risk_type": risk.get("type", ""),
            "severity": risk.get("severity", "medium"),
            "recommended_fix": risk.get("recommended_fix", ""),
            "review_required": risk.get("review_required", False),
            "source_finding_ids": [risk.get("finding_id", "")] if risk.get("finding_id") else [],
        }
        for risk in risks[:8]
    ]

    return {
        "client_brand": client["brand_name"],
        "website_domain": client.get("website_domain", ""),
        "product_or_service_direction": client.get("product_or_service_direction", []),
        "target_customer_roles": client.get("target_customer_roles", []),
        "target_countries_or_regions": client.get("target_countries_or_regions", []),
        "languages": client.get("languages", []),
        "target_optimization_platforms": client.get("target_optimization_platforms", []),
        "priority_topics": priority_topics,
        "risk_fixes": risk_fixes,
        "content_priorities": action_plan,
    }


def markdown_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def build_markdown(report):
    client = report["client"]
    scope = report["scope"]
    lines = [
        "# GEO Diagnostic Report",
        "",
        f"Client: {client['brand_name']}",
        f"Generated At: {report['generated_at']}",
        "",
        "## Executive Summary",
        "",
    ]
    lines.extend(f"- {item}" for item in report["executive_summary"])
    lines.extend([
        "",
        "## Project Scope",
        "",
        markdown_table(
            ["Field", "Value"],
            [
                ["Brand", client["brand_name"]],
                ["Website", client.get("website_domain", "") or "n/a"],
                ["Product / Service Direction", ", ".join(client.get("product_or_service_direction", [])) or "n/a"],
                ["Target Roles", ", ".join(client.get("target_customer_roles", [])) or "n/a"],
                ["Market", ", ".join(client.get("target_countries_or_regions", [])) or ", ".join(scope.get("markets", [])) or "n/a"],
                ["Language", ", ".join(client.get("languages", [])) or ", ".join(scope.get("languages", [])) or "n/a"],
                ["Platform", ", ".join(client.get("target_optimization_platforms", [])) or ", ".join(scope.get("platforms", [])) or "n/a"],
                ["Competitors", ", ".join(client.get("competitor_names", [])) or "n/a"],
                ["Topics / Prompts", f"{scope.get('topic_count', 0)} topics / {scope.get('prompt_count', 0)} prompts"],
                ["Analyzable Responses", scope.get("analyzable_response_count", 0)],
                ["Brand-Mentioning Responses", scope.get("brand_mentioning_response_count", 0)],
            ],
        ),
        "",
        "## Overall GEO Visibility Scorecard",
        "",
        markdown_table(
            ["Metric", "Client Score", "Rank", "Leading Competitor", "Interpretation"],
            [
                [
                    row["metric"],
                    row["client_display_value"],
                    rank_text(row["client_rank"]),
                    row["leading_competitor"] or "n/a",
                    row["interpretation"],
                ]
                for row in report["scorecard"]
            ],
        ),
        "",
        "## Competitor Comparison",
        "",
    ])
    if report["competitor_comparison"]:
        lines.append(markdown_table(
            ["Brand", "Visibility", "Share Of Voice", "Avg Position", "Sentiment", "Main Advantage"],
            [
                [
                    row["brand"],
                    format_percent(row["visibility_score"]),
                    format_percent(row["share_of_voice"]),
                    format_number(row["average_position"]),
                    format_number(row["sentiment_score"]),
                    row["main_advantage"],
                ]
                for row in report["competitor_comparison"]
            ],
        ))
    else:
        lines.append("No competitor metrics were available in the supplied analysis.")

    lines.extend(["", "## Topic-Level Diagnosis", ""])
    if report["topic_diagnosis"]:
        for topic in report["topic_diagnosis"]:
            competitors = ", ".join(topic.get("strong_competitors", [])[:4]) or "none"
            lines.extend([
                f"### {topic['topic']}",
                "",
                f"- Opportunity Level: {topic['opportunity_level']}",
                f"- Client Visibility: {format_percent(topic['client_visibility_score'])}",
                f"- Client Absent Rate: {format_percent(topic['client_absent_rate'])}",
                f"- Weak Recommendation Rate: {format_percent(topic['weak_recommendation_rate'])}",
                f"- Strong Competitors: {competitors}",
                f"- Diagnosis: {topic['diagnosis']}",
                f"- Recommended Action: {topic['recommended_action']}",
                "",
            ])
    else:
        lines.append("No topic-level analysis was available.")

    lines.extend(["## Content Gap Findings", ""])
    if report["content_gap_findings"]:
        for finding in report["content_gap_findings"][:12]:
            lines.extend([
                f"### {finding['label']}",
                "",
                f"- Severity: {finding['severity']}",
                f"- Topic: {finding.get('topic') or 'n/a'}",
                f"- Why It Matters: {finding['why_it_matters']}",
                f"- Evidence Response IDs: {', '.join(finding.get('evidence_response_ids', [])) or 'n/a'}",
                f"- Recommended Action: {finding['recommended_action']}",
                f"- Suggested Content Asset: {', '.join(finding.get('suggested_content_assets', []))}",
                "",
            ])
    else:
        lines.append("No content gap findings were detected in the supplied analysis.\n")

    lines.extend(["## Risk Findings", ""])
    if report["risk_findings"]:
        for risk in report["risk_findings"][:12]:
            review_note = " This should be manually reviewed before being treated as a confirmed error." if risk.get("review_required") else ""
            lines.extend([
                f"### {risk['label']}",
                "",
                f"- Severity: {risk['severity']}",
                f"- Topic: {risk.get('topic') or 'n/a'}",
                f"- Business Impact: {risk['business_impact']}",
                f"- Evidence Response IDs: {', '.join(risk.get('evidence_response_ids', [])) or 'n/a'}",
                f"- Recommended Fix: {risk['recommended_fix']}{review_note}",
                f"- Review Required: {'yes' if risk.get('review_required') else 'no'}",
                "",
            ])
    else:
        lines.append("No risk findings were detected in the supplied analysis.\n")

    lines.extend(["## Prioritized GEO Action Plan", ""])
    if report["action_plan"]:
        lines.append(markdown_table(
            ["Priority", "Action", "Mapped Topic", "Expected GEO Impact", "Owner", "Next Skill"],
            [
                [
                    row["priority"],
                    row["action"],
                    row.get("mapped_topic") or "n/a",
                    row["expected_geo_impact"],
                    row["recommended_owner"],
                    row["next_skill"],
                ]
                for row in report["action_plan"]
            ],
        ))
    else:
        lines.append("No action items were generated from the supplied analysis.")

    lines.extend(["", "## Method Notes", ""])
    lines.extend(f"- {note}" for note in report["method_notes"])
    return "\n".join(lines) + "\n"


def build_executive_summary_md(report):
    lines = [
        "# Executive Summary",
        "",
        f"Client: {report['client']['brand_name']}",
        "",
    ]
    lines.extend(f"- {item}" for item in report["executive_summary"])
    return "\n".join(lines) + "\n"


def build_client(intake):
    return {
        "brand_name": str(as_list(intake_field(intake, "brand_name", [""]))[0]).strip(),
        "website_domain": str(intake_field(intake, "website_domain", "") or "").strip(),
        "product_or_service_direction": clean_list(intake_field(intake, "product_or_service_direction", [])),
        "target_customer_roles": clean_list(intake_field(intake, "target_customer_roles", [])),
        "target_countries_or_regions": clean_list(intake_field(intake, "target_countries_or_regions", [])),
        "languages": clean_list(intake_field(intake, "languages", [])),
        "target_optimization_platforms": clean_list(intake_field(intake, "target_optimization_platforms", [])),
        "competitor_names": clean_list(intake_field(intake, "competitor_names", [])),
        "geo_optimization_goals": clean_list(intake_field(intake, "geo_optimization_goals", [])),
        "constraints": clean_list(intake_field(intake, "constraints", [])),
    }


def build_report(client_intake, prompt_set, visibility, topic_analysis, opportunities, source_files):
    client = build_client(client_intake)
    if not client["brand_name"]:
        raise ValueError("client_intake is missing brand_name")

    scope = prompt_scope(prompt_set)
    visibility_scope = visibility.get("scope", {})
    scope.update({
        "analyzable_response_count": visibility_scope.get("analyzable_response_count", 0),
        "brand_mentioning_response_count": visibility_scope.get("brand_mentioning_response_count", 0),
        "tracked_brands": visibility_scope.get("tracked_brands", []),
    })

    scorecard = build_scorecard(visibility, client["brand_name"])
    competitor_rows = build_competitor_comparison(visibility, client["brand_name"])
    topic_rows = build_topic_diagnosis(topic_analysis)
    content_raw, risk_raw = split_findings(opportunities)
    content_gaps = build_content_gap_findings(content_raw)
    risks = build_risk_findings(risk_raw)
    action_plan = build_action_plan(content_raw, risk_raw, topic_rows)
    executive_summary = build_executive_summary(client["brand_name"], scorecard, topic_rows, content_gaps, risks, action_plan)

    report = {
        "report_method": REPORT_METHOD,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": source_files,
        "client": client,
        "scope": scope,
        "executive_summary": executive_summary,
        "scorecard": scorecard,
        "competitor_comparison": competitor_rows,
        "topic_diagnosis": topic_rows,
        "content_gap_findings": content_gaps,
        "risk_findings": risks,
        "action_plan": action_plan,
        "method_notes": [
            "This report is based on the supplied ChatGPT monitoring sample and structured analyzer outputs.",
            "Visibility, share of voice, average position, and sentiment are read from geo-response-analyzer outputs rather than recalculated here.",
            "Review-required risks should be manually checked before being treated as confirmed factual errors.",
        ],
    }
    return report, build_content_writer_brief(client, topic_rows, content_gaps, risks, action_plan)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-intake", required=True, help="client_intake.json")
    parser.add_argument("--prompt-set", required=True, help="prompt_set.json")
    parser.add_argument("--visibility-analysis", required=True, help="visibility_analysis.json")
    parser.add_argument("--topic-analysis", required=True, help="topic_analysis.json")
    parser.add_argument("--opportunity-findings", required=True, help="opportunity_findings.json")
    parser.add_argument("--analysis-summary", help="Optional analysis_summary.md")
    parser.add_argument("--output-dir", default="report_run", help="Output directory")
    args = parser.parse_args()

    source_files = {
        "client_intake": str(Path(args.client_intake)),
        "prompt_set": str(Path(args.prompt_set)),
        "visibility_analysis": str(Path(args.visibility_analysis)),
        "topic_analysis": str(Path(args.topic_analysis)),
        "opportunity_findings": str(Path(args.opportunity_findings)),
    }
    if args.analysis_summary:
        source_files["analysis_summary"] = str(Path(args.analysis_summary))

    report, brief = build_report(
        load_json(args.client_intake),
        load_json(args.prompt_set),
        load_json(args.visibility_analysis),
        load_json(args.topic_analysis),
        load_json(args.opportunity_findings),
        source_files,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_json_path = output_dir / "geo_diagnostic_report.json"
    report_md_path = output_dir / "geo_diagnostic_report.md"
    brief_path = output_dir / "report_brief_for_content_writer.json"
    executive_path = output_dir / "executive_summary.md"

    write_json(report_json_path, report)
    report_md_path.write_text(build_markdown(report), encoding="utf-8")
    write_json(brief_path, brief)
    executive_path.write_text(build_executive_summary_md(report), encoding="utf-8")

    print(json.dumps({
        "geo_diagnostic_report_md": str(report_md_path),
        "geo_diagnostic_report_json": str(report_json_path),
        "report_brief_for_content_writer": str(brief_path),
        "executive_summary": str(executive_path),
        "client_brand": report["client"]["brand_name"],
        "actions": len(report["action_plan"]),
        "priority_topics": len(brief["priority_topics"]),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
