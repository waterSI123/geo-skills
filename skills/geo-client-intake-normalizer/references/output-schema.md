# Output Schema

Return JSON-like structured Markdown or valid JSON when requested. Preserve these top-level fields:

```json
{
  "source_inventory": [],
  "client_intake": {},
  "assumptions": [],
  "missing_fields": [],
  "conflicts": [],
  "confidence": "medium",
  "downstream_handoff": {},
  "intake_summary": {}
}
```

## source_inventory

```json
{
  "source_id": "S01",
  "type": "free_text",
  "name": "client message",
  "usable": true,
  "notes": ""
}
```

## client_intake

Every field is required:

```json
{
  "brand_name": {
    "value": "",
    "status": "missing",
    "sources": [],
    "raw_evidence": []
  },
  "website_domain": {
    "value": "",
    "status": "missing",
    "sources": [],
    "raw_evidence": []
  },
  "product_or_service_direction": {
    "value": [],
    "status": "missing",
    "sources": [],
    "raw_evidence": []
  },
  "target_customer_roles": {
    "value": [],
    "status": "missing",
    "sources": [],
    "raw_evidence": []
  },
  "target_countries_or_regions": {
    "value": [],
    "status": "missing",
    "sources": [],
    "raw_evidence": []
  },
  "languages": {
    "value": [],
    "status": "missing",
    "sources": [],
    "raw_evidence": []
  },
  "target_optimization_platforms": {
    "value": [],
    "status": "missing",
    "sources": [],
    "raw_evidence": []
  },
  "competitor_names": {
    "value": [],
    "status": "missing",
    "sources": [],
    "raw_evidence": []
  },
  "geo_optimization_goals": {
    "value": [],
    "status": "missing",
    "sources": [],
    "raw_evidence": []
  },
  "constraints": {
    "value": [],
    "status": "missing",
    "sources": [],
    "raw_evidence": []
  }
}
```

Allowed field statuses:

- `confirmed`
- `inferred`
- `missing`
- `conflicting`

## assumptions

Use for inferred values and reasoning:

```json
{
  "field": "languages",
  "assumption": "English inferred from United States target market.",
  "risk": "low"
}
```

## missing_fields

```json
{
  "field": "target_optimization_platforms",
  "severity": "blocking",
  "question": ""
}
```

## conflicts

```json
{
  "field": "target_countries_or_regions",
  "values": [
    {
      "value": "United States",
      "sources": ["S01"]
    },
    {
      "value": "Southeast Asia",
      "sources": ["S03"]
    }
  ],
  "resolution": "needs_user_confirmation"
}
```

## downstream_handoff

```json
{
  "ready_for_prompt_generation": true,
  "ready_for_monitoring": false,
  "ready_for_response_analysis": false,
  "ready_for_reporting": false,
  "ready_for_content_generation": false,
  "recommended_next_skill": "geo-intent-prompt-generator",
  "blocking_gaps": []
}
```

## intake_summary

Human-readable compact summary:

```json
{
  "client": "",
  "offering": "",
  "audience": "",
  "markets": [],
  "languages": [],
  "platforms": [],
  "competitors": [],
  "goals": [],
  "constraints": [],
  "recommended_next_step": ""
}
```
