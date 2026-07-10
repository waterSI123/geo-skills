# Output Schema

Return JSON-like structured Markdown or valid JSON when requested. Preserve these top-level fields:

```json
{
  "input_summary": {},
  "website_research_brief": {},
  "topics": [],
  "prompt_groups": [],
  "qa_report": {}
}
```

## input_summary

```json
{
  "services": [],
  "personas": [],
  "target_market": "",
  "language": "",
  "platform": "",
  "additional_context": "",
  "competitors": [],
  "website_domain": "",
  "brand_name": "",
  "assumptions": [],
  "market_proxy_inputs_used": {
    "actual_buyer_questions": [],
    "customer_pain_points": [],
    "buying_triggers": [],
    "sales_call_questions": [],
    "existing_search_terms": [],
    "existing_ad_keywords": [],
    "existing_customer_language": [],
    "conversion_goals": [],
    "business_kpis": []
  }
}
```

## website_research_brief

Use this object when a website domain is provided. If no domain is provided, return an empty object and note the source gap in `qa_report`.

```json
{
  "domain": "",
  "official_brand_name": "",
  "one_line_description": "",
  "core_services": [],
  "target_personas": [],
  "products": [],
  "selling_points": [],
  "scenarios": [],
  "customers": [],
  "competitors": [],
  "integrations": [],
  "limitations": [],
  "source_urls": [],
  "confidence": "medium",
  "confirmation_status": "unconfirmed",
  "unconfirmed_or_inferred_items": []
}
```

## topics

```json
{
  "topic_id": "T01",
  "topic": "",
  "intent_definition": "",
  "persona": "",
  "service_area": "",
  "buyer_question": "",
  "monitoring_goal": "",
  "priority": "high",
  "evidence_used": []
}
```

## prompt_groups

Group prompts under their topic:

```json
{
  "topic_id": "T01",
  "topic": "",
  "prompts": [
    {
      "prompt_id": "P001",
      "prompt": "",
      "brand_type": "unbranded",
      "intent_stage": "commercial",
      "persona": "",
      "market": "",
      "language": "",
      "platform": "",
      "monitoring_role": "market_proxy",
      "prompt_realism_score": 0.9,
      "demand_weight": 1.0,
      "buyer_journey_stage": "evaluation",
      "source_basis": ["customer_pain_point", "competitor_context"],
      "overfit_risk": "low",
      "monitoring_goal": ""
    }
  ]
}
```

Allowed `brand_type` values:

- `unbranded`
- `branded`

Allowed `intent_stage` values:

- `info`
- `commercial`
- `transactional`

Allowed `monitoring_role` values:

- `market_proxy`: common real user or buyer question. Use for primary KPI measurement.
- `buyer_evaluation`: realistic deeper evaluation, shortlist, implementation, or switching question. Use for primary KPI measurement with slightly lower demand weight.
- `diagnostic_probe`: targeted probe for a suspected gap, risk, or content question. Do not use for primary KPI inflation.
- `brand_control`: brand/entity verification question. Do not use for primary KPI inflation.

Allowed `buyer_journey_stage` values:

- `awareness`
- `evaluation`
- `selection`
- `implementation`
- `retention`

Allowed `overfit_risk` values:

- `low`
- `medium`
- `high`

`prompt_realism_score` must be numeric from `0` to `1`. `demand_weight` must be numeric and greater than `0`.

## qa_report

```json
{
  "topic_count": 0,
  "prompt_count": 0,
  "brand_distribution": {},
  "intent_distribution": {},
  "monitoring_role_distribution": {},
  "average_prompt_realism_score": 0.0,
  "market_proxy_demand_weight_share": 0.0,
  "localization_notes": [],
  "assumptions": [],
  "source_gaps": [],
  "excluded_or_rewritten_patterns": [],
  "ready_for_monitoring": true
}
```
