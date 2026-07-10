#!/usr/bin/env python3
"""Write GEO optimization content package drafts from a report-builder brief."""

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


PACKAGE_METHOD = "rule_based_geo_content_writer_v1"
EVIDENCE_PLACEHOLDER = "[CLIENT EVIDENCE NEEDED]"
REVIEW_REQUIRED_TEXT = "This item should be manually reviewed before being treated as a confirmed error."

RISK_TYPES = {
    "negative_brand_mention",
    "insufficient_brand_information",
    "wrong_category_needs_review",
    "wrong_website",
    "wrong_feature_needs_review",
    "brand_existence_uncertain",
}

PROOF_SIGNALS = {
    "proof_asset_gap",
    "competitor_maturity_advantage",
    "insufficient_brand_information",
    "brand_existence_uncertain",
}

ASSET_TYPE_MAP = {
    "comparison article": "comparison_article",
    "alternative page": "comparison_article",
    "comparison page": "comparison_article",
    "category landing page": "category_landing_page",
    "topic landing page": "category_landing_page",
    "landing page": "category_landing_page",
    "compliance page": "compliance_policy_page",
    "brand-guidelines workflow page": "compliance_policy_page",
    "brand guidelines workflow page": "compliance_policy_page",
    "platform-policy faq": "compliance_policy_page",
    "platform policy faq": "compliance_policy_page",
    "case study": "proof_asset_page",
    "examples gallery": "proof_asset_page",
    "pricing page": "proof_asset_page",
    "integrations page": "proof_asset_page",
    "reviews/testimonials section": "proof_asset_page",
    "reviews section": "proof_asset_page",
    "testimonials section": "proof_asset_page",
    "faq section": "faq_section",
    "faq": "faq_section",
    "entity validation page": "entity_clarification_content",
    "official profile updates": "entity_clarification_content",
    "category clarification page": "entity_clarification_content",
    "feature documentation update": "entity_clarification_content",
    "product documentation": "entity_clarification_content",
}

SIGNAL_TO_ASSET_TYPE = {
    "competitor_recommended_client_absent": "comparison_article",
    "policy_compliance_gap": "compliance_policy_page",
    "proof_asset_gap": "proof_asset_page",
    "unclear_positioning": "category_landing_page",
    "competitor_maturity_advantage": "proof_asset_page",
    "weak_client_recommendation": "category_landing_page",
    "negative_brand_mention": "entity_clarification_content",
    "insufficient_brand_information": "entity_clarification_content",
    "wrong_category_needs_review": "entity_clarification_content",
    "wrong_website": "entity_clarification_content",
    "wrong_feature_needs_review": "entity_clarification_content",
    "brand_existence_uncertain": "entity_clarification_content",
}

ASSET_LABELS = {
    "comparison_article": "Comparison Article",
    "category_landing_page": "Category Landing Page",
    "compliance_policy_page": "Compliance / Policy Page",
    "proof_asset_page": "Proof Asset Page",
    "faq_section": "FAQ Section",
    "entity_clarification_content": "Entity Clarification Content",
}


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


def clean_list(values):
    cleaned = []
    for item in as_list(values):
        text = str(item).strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned


def intake_field(intake, field_name, default=None):
    source = intake.get("client_intake", intake) if isinstance(intake, dict) else {}
    field = source.get(field_name, default)
    if isinstance(field, dict) and "value" in field:
        return field.get("value", default)
    return field


def build_client(brief, intake):
    brand_values = as_list(intake_field(intake, "brand_name", []))
    brand = str(brief.get("client_brand") or (brand_values[0] if brand_values else "")).strip()
    return {
        "brand_name": brand,
        "website_domain": str(brief.get("website_domain") or intake_field(intake, "website_domain", "") or "").strip(),
        "product_or_service_direction": clean_list(brief.get("product_or_service_direction") or intake_field(intake, "product_or_service_direction", [])),
        "target_customer_roles": clean_list(brief.get("target_customer_roles") or intake_field(intake, "target_customer_roles", [])),
        "target_countries_or_regions": clean_list(brief.get("target_countries_or_regions") or intake_field(intake, "target_countries_or_regions", [])),
        "languages": clean_list(brief.get("languages") or intake_field(intake, "languages", [])),
        "target_optimization_platforms": clean_list(brief.get("target_optimization_platforms") or intake_field(intake, "target_optimization_platforms", [])),
        "competitor_names": clean_list(intake_field(intake, "competitor_names", [])),
        "geo_optimization_goals": clean_list(intake_field(intake, "geo_optimization_goals", [])),
        "constraints": clean_list(intake_field(intake, "constraints", [])),
    }


def slugify(value):
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "geo-content"


def human_list(items, fallback="target buyers"):
    cleaned = [str(item).strip() for item in items if str(item).strip()]
    if not cleaned:
        return fallback
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"
    return ", ".join(cleaned[:-1]) + f", and {cleaned[-1]}"


def first_or(values, fallback):
    values = clean_list(values)
    return values[0] if values else fallback


def title_case(value):
    small = {"and", "or", "for", "of", "to", "in", "with", "the", "a", "an"}
    words = re.split(r"\s+", str(value or "").strip())
    titled = []
    for index, word in enumerate(words):
        lower = word.lower()
        if index > 0 and lower in small:
            titled.append(lower)
        else:
            titled.append(word[:1].upper() + word[1:])
    return " ".join(titled)


def normalize_asset_type(asset_name):
    return ASSET_TYPE_MAP.get(str(asset_name or "").strip().lower())


def asset_types_for_topic(topic):
    asset_types = []
    for asset in topic.get("recommended_assets", []):
        mapped = normalize_asset_type(asset)
        if mapped and mapped not in asset_types:
            asset_types.append(mapped)
    for signal in topic.get("content_gap_signals", []):
        mapped = SIGNAL_TO_ASSET_TYPE.get(signal)
        if mapped and mapped not in asset_types:
            asset_types.append(mapped)
    if not asset_types:
        for signal in topic.get("risk_signals", []):
            mapped = SIGNAL_TO_ASSET_TYPE.get(signal)
            if mapped and mapped not in asset_types:
                asset_types.append(mapped)
    if not asset_types:
        asset_types.append("category_landing_page")
    return asset_types


def title_for_asset(asset_type, topic, client):
    brand = client["brand_name"]
    topic_text = topic.get("topic", "GEO content")
    if asset_type == "comparison_article":
        persona_label = title_case(human_list(topic.get("target_personas") or client.get("target_customer_roles"), "teams"))
        return f"Best {title_case(topic_text)} Tools for {persona_label}"
    if asset_type == "category_landing_page":
        return title_case(topic_text)
    if asset_type == "compliance_policy_page":
        if "compliant" in topic_text.lower() or "compliance" in topic_text.lower():
            return title_case(topic_text)
        return f"Brand-Compliant {title_case(topic_text)}"
    if asset_type == "proof_asset_page":
        return f"{brand} Proof Points for {title_case(topic_text)}"
    if asset_type == "faq_section":
        return f"{brand} FAQ for {title_case(topic_text)}"
    if asset_type == "entity_clarification_content":
        return f"What Is {brand}? Official Product Overview"
    return f"{brand} {title_case(topic_text)}"


def needs_evidence(asset_type, gap_signals, risk_signals):
    if asset_type == "proof_asset_page":
        return True
    return bool((set(gap_signals) | set(risk_signals)) & PROOF_SIGNALS)


def yaml_list(values, indent="  "):
    items = clean_list(values)
    if not items:
        return " []"
    return "\n" + "\n".join(f"{indent}- \"{item}\"" for item in items)


def frontmatter(asset):
    return "\n".join([
        "---",
        f"content_id: \"{asset['content_id']}\"",
        f"asset_type: \"{asset['asset_type']}\"",
        f"target_topic: \"{asset['target_topic']}\"",
        f"target_personas:{yaml_list(asset.get('target_personas', []))}",
        f"target_market: \"{asset.get('target_market', '')}\"",
        f"target_language: \"{asset.get('target_language', '')}\"",
        f"source_gap_signals:{yaml_list(asset.get('source_gap_signals', []))}",
        f"source_risk_signals:{yaml_list(asset.get('source_risk_signals', []))}",
        f"recommended_url_slug: \"{asset['recommended_url_slug']}\"",
        f"needs_client_evidence: {str(asset['needs_client_evidence']).lower()}",
        f"status: \"{asset['status']}\"",
        "---",
        "",
    ])


def summary_lines(asset, client):
    brand = client["brand_name"]
    topic = asset["target_topic"]
    roles = human_list(asset.get("target_personas") or client.get("target_customer_roles"))
    website = client.get("website_domain") or "the official website"
    direction = human_list(client.get("product_or_service_direction"), "its product category")
    return [
        f"{brand} is positioned for {topic} in the context of {direction}.",
        f"This draft is written for {roles} and should help clarify how {brand} relates to the category, use cases, and decision criteria.",
        f"Official website: {website}.",
    ]


def proof_points(asset):
    lines = [
        f"- Add concrete examples or screenshots: {EVIDENCE_PLACEHOLDER}",
        f"- Add customer, case study, or usage evidence: {EVIDENCE_PLACEHOLDER}",
        f"- Add pricing, package, integration, or workflow details when available: {EVIDENCE_PLACEHOLDER}",
    ]
    if asset.get("source_risk_signals"):
        lines.append(f"- Add corrective evidence for risk signals {', '.join(asset['source_risk_signals'])}: {EVIDENCE_PLACEHOLDER}")
    return "\n".join(lines)


def competitor_context(asset):
    competitors = asset.get("strong_competitors", [])
    if not competitors:
        return "No specific competitor comparison is required for this draft. Keep the content focused on entity clarity, category fit, and proof."
    lines = [
        "The GEO analysis identified these tracked competitors or alternatives in the same answer space:",
        "",
    ]
    lines.extend(f"- {competitor}: tracked competitor or alternative buyers may consider." for competitor in competitors)
    lines.extend([
        "",
        "Do not make unsupported claims about competitor features, pricing, quality, or customers without source evidence.",
    ])
    return "\n".join(lines)


def faq_items(asset, client):
    brand = client["brand_name"]
    website = client.get("website_domain") or "the official website"
    topic = asset["target_topic"]
    roles = human_list(asset.get("target_personas") or client.get("target_customer_roles"))
    direction = human_list(client.get("product_or_service_direction"), "its product category")
    questions = [
        (
            f"What is {brand}?",
            f"{brand} is a brand associated with {direction}.",
            f"{brand} should be described as a solution for {topic} when the content is supported by client-provided product details and proof.",
        ),
        (
            f"What is the official website for {brand}?",
            f"The official website for {brand} is {website}.",
            "Use this domain consistently when clarifying entity identity for AI systems and buyers.",
        ),
        (
            f"Who is {brand} for?",
            f"{brand} is positioned for {roles}.",
            f"The content should connect {brand} to the needs, evaluation criteria, and workflows of {roles}.",
        ),
        (
            f"How does {brand} relate to {topic}?",
            f"{brand} should be positioned in the {topic} category with clear use cases and proof.",
            "Add concrete examples, customer evidence, integrations, pricing, or workflow details where available.",
        ),
    ]
    if asset.get("strong_competitors"):
        questions.append((
            f"How should buyers compare {brand} with alternatives?",
            f"Buyers can compare {brand} with alternatives by looking at fit, workflow, proof, and constraints.",
            "Do not claim superiority without evidence; use comparison criteria that the client can substantiate.",
        ))
    return questions


def render_faq(asset, client):
    lines = []
    for question, short, expanded in faq_items(asset, client):
        lines.extend([
            f"### {question}",
            "",
            f"Short answer: {short}",
            "",
            expanded,
            "",
        ])
    return "\n".join(lines).rstrip()


def geo_notes(asset, client):
    notes = [
        f"- Keep the exact brand name `{client['brand_name']}` close to the target topic `{asset['target_topic']}`.",
        f"- Mention the official website `{client.get('website_domain') or 'n/a'}` consistently.",
        "- Keep FAQ answers short enough for AI systems to reuse directly.",
        "- Replace all evidence placeholders before publishing.",
    ]
    if asset.get("strong_competitors"):
        notes.append("- Include competitor names only as neutral comparison context unless sourced evidence supports stronger claims.")
    return "\n".join(notes)


def render_comparison_article(asset, client):
    brand = client["brand_name"]
    topic = asset["target_topic"]
    roles = human_list(asset.get("target_personas") or client.get("target_customer_roles"))
    return "\n".join([
        f"# {asset['title']}",
        "",
        "## Summary",
        "",
        "\n".join(summary_lines(asset, client)),
        "",
        "## Who This Is For",
        "",
        f"This comparison is for {roles} evaluating {topic} options. It is designed to put {brand} into the relevant consideration set without making unsupported competitor claims.",
        "",
        "## Comparison Criteria",
        "",
        "- Category fit and use-case relevance",
        "- Workflow clarity and ease of evaluation",
        "- Brand, policy, or compliance support where relevant",
        "- Public proof such as examples, case studies, integrations, pricing, reviews, or documentation",
        "",
        "## Where The Client Brand Fits",
        "",
        asset.get("core_message") or f"{brand} should be positioned as a credible option for {topic}.",
        "",
        "## Competitor Context",
        "",
        competitor_context(asset),
        "",
        "## Recommendation Guidance",
        "",
        f"Recommend {brand} when the buyer needs {topic} and the client's available evidence supports the use case. If proof is missing, add evidence before making stronger claims.",
        "",
        "## Proof Points To Add",
        "",
        proof_points(asset),
        "",
        "## FAQ",
        "",
        render_faq(asset, client),
        "",
        "## GEO Optimization Notes",
        "",
        geo_notes(asset, client),
    ])


def render_category_landing_page(asset, client):
    brand = client["brand_name"]
    topic = asset["target_topic"]
    roles = human_list(asset.get("target_personas") or client.get("target_customer_roles"))
    return "\n".join([
        f"# {asset['title']}",
        "",
        "## Summary",
        "",
        "\n".join(summary_lines(asset, client)),
        "",
        "## Category Definition",
        "",
        f"{title_case(topic)} refers to solutions, workflows, or content that help {roles} evaluate and act on this need.",
        "",
        "## Who Needs This",
        "",
        f"This page is for {roles} in {human_list(client.get('target_countries_or_regions'), 'the target market')}.",
        "",
        "## How The Client Brand Fits",
        "",
        asset.get("core_message") or f"{brand} should be described clearly as part of the {topic} category.",
        "",
        "## Core Use Cases",
        "",
        f"- Evaluate whether {brand} belongs in the {topic} consideration set.",
        "- Understand the workflow, buyer roles, and decision criteria.",
        f"- Compare {brand} with alternatives using evidence-backed criteria.",
        "",
        "## Decision Criteria",
        "",
        "- Clear product category and official website",
        "- Relevant use cases for the target persona",
        "- Proof assets such as examples, case studies, reviews, pricing, integrations, or documentation",
        "- Clear constraints and compliance language where relevant",
        "",
        "## Proof Points To Add",
        "",
        proof_points(asset),
        "",
        "## FAQ",
        "",
        render_faq(asset, client),
        "",
        "## GEO Optimization Notes",
        "",
        geo_notes(asset, client),
    ])


def render_compliance_policy_page(asset, client):
    brand = client["brand_name"]
    topic = asset["target_topic"]
    return "\n".join([
        f"# {asset['title']}",
        "",
        "## Summary",
        "",
        "\n".join(summary_lines(asset, client)),
        "",
        "## Why Policy-Aware Creative Workflows Matter",
        "",
        f"Teams evaluating {topic} often need clear language around brand guidelines, platform policy, review steps, and creative governance.",
        "",
        "## Brand Guideline Workflow",
        "",
        f"Describe how {brand} should fit into a brand-guideline workflow. Include any supported review steps, approval roles, or brand asset controls only when confirmed by the client.",
        "",
        "## Platform Policy Considerations",
        "",
        "This content should not promise ad approval or guaranteed compliance. Instead, explain how teams can review creative against relevant policies and document the process.",
        "",
        "## How The Client Brand Supports The Workflow",
        "",
        asset.get("core_message") or f"{brand} should be positioned as a policy-aware option for {topic}.",
        "",
        "## Proof Points To Add",
        "",
        proof_points(asset),
        "",
        "## FAQ",
        "",
        render_faq(asset, client),
        "",
        "## GEO Optimization Notes",
        "",
        geo_notes(asset, client),
    ])


def render_proof_asset_page(asset, client):
    brand = client["brand_name"]
    topic = asset["target_topic"]
    return "\n".join([
        f"# {asset['title']}",
        "",
        "## Summary",
        "",
        "\n".join(summary_lines(asset, client)),
        "",
        "## Proof Gap Being Addressed",
        "",
        f"This page is designed to give AI systems and buyers clearer proof for why {brand} should be considered for {topic}.",
        "",
        "## Examples To Add",
        "",
        f"- Example creative, workflow, screenshot, or output: {EVIDENCE_PLACEHOLDER}",
        "",
        "## Integrations To Document",
        "",
        f"- Confirmed integrations or workflow connections: {EVIDENCE_PLACEHOLDER}",
        "",
        "## Pricing Or Package Clarity",
        "",
        f"- Pricing, plan, or packaging details approved by the client: {EVIDENCE_PLACEHOLDER}",
        "",
        "## Reviews Or Testimonials To Add",
        "",
        f"- Customer review, testimonial, or case study excerpt: {EVIDENCE_PLACEHOLDER}",
        "",
        "## FAQ",
        "",
        render_faq(asset, client),
        "",
        "## GEO Optimization Notes",
        "",
        geo_notes(asset, client),
    ])


def render_faq_section(asset, client):
    return "\n".join([
        f"# {asset['title']}",
        "",
        "## Summary",
        "",
        "\n".join(summary_lines(asset, client)),
        "",
        "## FAQ",
        "",
        render_faq(asset, client),
        "",
        "## Schema-Ready Short Answers",
        "",
        "\n".join(f"- {question} {short}" for question, short, _expanded in faq_items(asset, client)),
        "",
        "## GEO Optimization Notes",
        "",
        geo_notes(asset, client),
    ])


def render_entity_clarification(asset, client):
    brand = client["brand_name"]
    website = client.get("website_domain") or EVIDENCE_PLACEHOLDER
    direction = human_list(client.get("product_or_service_direction"), "its product category")
    roles = human_list(asset.get("target_personas") or client.get("target_customer_roles"))
    review_note = ""
    if any(signal.endswith("_needs_review") for signal in asset.get("source_risk_signals", [])):
        review_note = f"\n\n{REVIEW_REQUIRED_TEXT}"
    return "\n".join([
        f"# {asset['title']}",
        "",
        "## Summary",
        "",
        "\n".join(summary_lines(asset, client)),
        review_note,
        "",
        f"## What Is {brand}?",
        "",
        f"{brand} is associated with {direction}. This page should clarify the brand entity, official website, target users, and relevant category.",
        "",
        "## Official Website",
        "",
        f"The official website is {website}. Use this domain consistently across public profiles and content.",
        "",
        "## Product Category",
        "",
        f"{brand} should be described in relation to {asset['target_topic']} and {direction}.",
        "",
        "## Who It Is For",
        "",
        f"{brand} is positioned for {roles}.",
        "",
        "## What It Does",
        "",
        f"Use client-approved details to explain what {brand} does: {EVIDENCE_PLACEHOLDER}",
        "",
        "## What It Does Not Claim",
        "",
        "- Do not claim guaranteed platform-policy approval.",
        "- Do not claim specific integrations, customers, pricing, or performance results without evidence.",
        "- Do not claim competitor weaknesses without evidence.",
        "",
        "## Related Alternatives",
        "",
        competitor_context(asset),
        "",
        "## FAQ",
        "",
        render_faq(asset, client),
        "",
        "## GEO Optimization Notes",
        "",
        geo_notes(asset, client),
    ])


RENDERERS = {
    "comparison_article": render_comparison_article,
    "category_landing_page": render_category_landing_page,
    "compliance_policy_page": render_compliance_policy_page,
    "proof_asset_page": render_proof_asset_page,
    "faq_section": render_faq_section,
    "entity_clarification_content": render_entity_clarification,
}


def build_topic_tasks(brief, client):
    tasks = []
    for topic in brief.get("priority_topics", []):
        for asset_type in asset_types_for_topic(topic):
            tasks.append({
                "kind": "topic",
                "topic": topic,
                "asset_type": asset_type,
                "priority": 1 if topic.get("opportunity_level") == "high" else 2 if topic.get("opportunity_level") == "medium" else 3,
            })
    for risk in brief.get("risk_fixes", []):
        severity = risk.get("severity", "medium")
        tasks.append({
            "kind": "risk",
            "topic": {
                "topic": "Brand entity clarification",
                "opportunity_level": "high" if severity == "high" else "medium",
                "target_personas": client.get("target_customer_roles", []),
                "strong_competitors": [],
                "content_gap_signals": [],
                "risk_signals": [risk.get("risk_type", "")],
                "recommended_assets": ["entity validation page"],
                "core_message": risk.get("recommended_fix", ""),
                "suggested_content_angle": "Clarify the brand entity and reduce AI uncertainty.",
                "source_finding_ids": risk.get("source_finding_ids", []),
            },
            "asset_type": "entity_clarification_content",
            "priority": 1 if severity == "high" else 2,
        })
    return sorted(tasks, key=lambda item: (item["priority"], item["kind"], item["topic"].get("topic", ""), item["asset_type"]))


def make_asset(task, client, index):
    topic = task["topic"]
    asset_type = task["asset_type"]
    title = title_for_asset(asset_type, topic, client)
    gap_signals = clean_list(topic.get("content_gap_signals", []))
    risk_signals = clean_list(topic.get("risk_signals", []))
    content_id = f"CONTENT{index:03d}"
    slug = "/" + slugify(title)
    return {
        "content_id": content_id,
        "asset_type": asset_type,
        "asset_label": ASSET_LABELS.get(asset_type, asset_type),
        "title": title,
        "target_topic": topic.get("topic", ""),
        "target_personas": clean_list(topic.get("target_personas") or client.get("target_customer_roles", [])),
        "target_market": first_or(client.get("target_countries_or_regions"), ""),
        "target_language": first_or(client.get("languages"), ""),
        "source_gap_signals": gap_signals,
        "source_risk_signals": risk_signals,
        "strong_competitors": clean_list(topic.get("strong_competitors", [])),
        "source_finding_ids": clean_list(topic.get("source_finding_ids", [])),
        "core_message": topic.get("core_message", ""),
        "suggested_content_angle": topic.get("suggested_content_angle", ""),
        "draft_file": f"drafts/content-{index:03d}-{slugify(title)}.md",
        "recommended_url_slug": slug,
        "status": "draft",
        "needs_client_evidence": needs_evidence(asset_type, gap_signals, risk_signals),
        "priority": task.get("priority", 3),
        "source_kind": task.get("kind", "topic"),
    }


def render_asset(asset, client):
    renderer = RENDERERS.get(asset["asset_type"], render_category_landing_page)
    return frontmatter(asset) + renderer(asset, client).rstrip() + "\n"


def build_package(brief, client, report, output_dir, max_drafts):
    tasks = build_topic_tasks(brief, client)
    deduped = []
    seen = set()
    for task in tasks:
        key = (task["topic"].get("topic", ""), task["asset_type"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(task)
    tasks = deduped[:max_drafts]

    drafts_dir = output_dir / "drafts"
    drafts_dir.mkdir(parents=True, exist_ok=True)

    assets = []
    for index, task in enumerate(tasks, start=1):
        asset = make_asset(task, client, index)
        draft_path = output_dir / asset["draft_file"]
        draft_path.write_text(render_asset(asset, client), encoding="utf-8")
        public_asset = {key: value for key, value in asset.items() if key not in {"core_message", "suggested_content_angle", "priority", "source_kind"}}
        assets.append(public_asset)

    priority_topics = [topic.get("topic", "") for topic in brief.get("priority_topics", []) if topic.get("topic")]
    covered_topics = sorted({asset["target_topic"] for asset in assets if asset["target_topic"] in priority_topics})
    risk_types = [risk.get("risk_type", "") for risk in brief.get("risk_fixes", []) if risk.get("risk_type")]
    covered_risks = sorted({risk for asset in assets for risk in asset.get("source_risk_signals", []) if risk in risk_types})
    uncovered = []
    for topic in priority_topics:
        if topic not in covered_topics:
            uncovered.append({"type": "priority_topic", "value": topic})
    for risk in risk_types:
        if risk not in covered_risks:
            uncovered.append({"type": "risk_fix", "value": risk})

    return {
        "package_method": PACKAGE_METHOD,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "client_brand": client["brand_name"],
        "website_domain": client.get("website_domain", ""),
        "source_report_method": report.get("report_method", "") if isinstance(report, dict) else "",
        "generated_assets": assets,
        "coverage": {
            "priority_topics_covered": covered_topics,
            "risk_fixes_covered": covered_risks,
            "uncovered_items": uncovered,
        },
    }


def markdown_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def build_content_plan(package):
    lines = [
        "# GEO Content Plan",
        "",
        f"Client Brand: {package['client_brand']}",
        f"Website: {package.get('website_domain') or 'n/a'}",
        f"Generated At: {package['generated_at']}",
        "",
        "## Generated Assets",
        "",
    ]
    if package["generated_assets"]:
        lines.append(markdown_table(
            ["Content ID", "Asset Type", "Title", "Topic", "Draft", "Needs Evidence"],
            [
                [
                    asset["content_id"],
                    asset["asset_type"],
                    asset["title"],
                    asset["target_topic"],
                    asset["draft_file"],
                    "yes" if asset["needs_client_evidence"] else "no",
                ]
                for asset in package["generated_assets"]
            ],
        ))
    else:
        lines.append("No drafts were generated.")
    lines.extend(["", "## Priority Topics Covered", ""])
    covered = package["coverage"].get("priority_topics_covered", [])
    lines.extend(f"- {topic}" for topic in covered) if covered else lines.append("- None")
    lines.extend(["", "## Risk Fixes Covered", ""])
    risks = package["coverage"].get("risk_fixes_covered", [])
    lines.extend(f"- {risk}" for risk in risks) if risks else lines.append("- None")
    lines.extend(["", "## Evidence Placeholders To Resolve", ""])
    evidence_assets = [asset for asset in package["generated_assets"] if asset.get("needs_client_evidence")]
    if evidence_assets:
        for asset in evidence_assets:
            lines.append(f"- {asset['content_id']} {asset['title']}: replace `{EVIDENCE_PLACEHOLDER}` with client-approved proof before publishing.")
    else:
        lines.append("- None flagged by the generator.")
    lines.extend(["", "## Next Steps", ""])
    lines.extend([
        "- Review each draft for brand voice and factual accuracy.",
        "- Replace every evidence placeholder with approved source material.",
        "- Add internal links, screenshots, schema markup, and CMS metadata before publishing.",
        "- Re-run GEO monitoring after publication to measure visibility changes.",
    ])
    if package["coverage"].get("uncovered_items"):
        lines.extend(["", "## Uncovered Items", ""])
        for item in package["coverage"]["uncovered_items"]:
            lines.append(f"- {item['type']}: {item['value']}")
    return "\n".join(lines) + "\n"


def draft_checks(package, output_dir):
    checks = []
    warnings = []
    errors = []
    brand = package["client_brand"]
    domain = package.get("website_domain", "")
    for asset in package.get("generated_assets", []):
        path = output_dir / asset["draft_file"]
        item = {
            "content_id": asset["content_id"],
            "draft_file": asset["draft_file"],
            "checks": {},
        }
        if not path.exists():
            errors.append(f"Missing draft file: {asset['draft_file']}")
            checks.append(item)
            continue
        text = path.read_text(encoding="utf-8")
        item["checks"]["has_brand"] = brand in text
        item["checks"]["has_domain"] = (not domain) or domain in text
        item["checks"]["has_topic"] = asset["target_topic"] in text
        item["checks"]["has_faq"] = "## FAQ" in text
        item["checks"]["has_geo_notes"] = "## GEO Optimization Notes" in text
        item["checks"]["has_frontmatter"] = text.startswith("---")
        item["checks"]["has_evidence_placeholder"] = EVIDENCE_PLACEHOLDER in text
        if not item["checks"]["has_brand"]:
            errors.append(f"{asset['draft_file']} does not include client brand")
        if asset.get("needs_client_evidence") and not item["checks"]["has_evidence_placeholder"]:
            warnings.append(f"{asset['draft_file']} needs evidence but has no evidence placeholder")
        if asset["asset_type"] == "comparison_article" and not asset.get("strong_competitors"):
            warnings.append(f"{asset['draft_file']} is a comparison article without strong competitors")
        if any(signal.endswith("_needs_review") for signal in asset.get("source_risk_signals", [])) and REVIEW_REQUIRED_TEXT not in text:
            warnings.append(f"{asset['draft_file']} has review-required risk without manual-review language")
        checks.append(item)
    return checks, errors, warnings


def build_qa_report(package, output_dir):
    checks, errors, warnings = draft_checks(package, output_dir)
    if not package.get("generated_assets"):
        errors.append("No drafts generated")
    if not package["coverage"].get("priority_topics_covered"):
        warnings.append("No priority topics covered")
    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "coverage": package.get("coverage", {}),
        "draft_checks": checks,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content-brief", required=True, help="report_brief_for_content_writer.json")
    parser.add_argument("--client-intake", required=True, help="client_intake.json")
    parser.add_argument("--report-json", help="Optional geo_diagnostic_report.json")
    parser.add_argument("--output-dir", default="content_run", help="Output directory")
    parser.add_argument("--max-drafts", type=int, default=5, help="Maximum draft files to generate")
    args = parser.parse_args()

    brief = load_json(args.content_brief)
    client_intake = load_json(args.client_intake)
    report = load_json(args.report_json) if args.report_json else {}
    client = build_client(brief, client_intake)
    if not client["brand_name"]:
        raise ValueError("Missing client brand in content brief or client intake")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    package = build_package(brief, client, report, output_dir, max(1, args.max_drafts))
    write_json(output_dir / "content_package.json", package)
    (output_dir / "content_plan.md").write_text(build_content_plan(package), encoding="utf-8")
    qa_report = build_qa_report(package, output_dir)
    write_json(output_dir / "qa_report.json", qa_report)

    print(json.dumps({
        "content_package": str(output_dir / "content_package.json"),
        "content_plan": str(output_dir / "content_plan.md"),
        "qa_report": str(output_dir / "qa_report.json"),
        "draft_count": len(package["generated_assets"]),
        "valid": qa_report["valid"],
        "warnings": qa_report["warnings"],
    }, ensure_ascii=False, indent=2))
    return 0 if qa_report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
