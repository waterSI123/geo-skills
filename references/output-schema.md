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
  "website_domain": "",
  "brand_name": "",
  "competitors": [],
  "assumptions": []
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
  "use_cases": [],
  "selling_points": [],
  "customers": [],
  "competitors_or_alternatives": [],
  "integrations": [],
  "limitations_or_constraints": [],
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

## qa_report

```json
{
  "topic_count": 0,
  "prompt_count": 0,
  "brand_distribution": {},
  "intent_distribution": {},
  "localization_notes": [],
  "assumptions": [],
  "source_gaps": [],
  "excluded_or_rewritten_patterns": [],
  "ready_for_monitoring": true
}
```
