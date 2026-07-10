# Input Schema

The analyzer expects these files from upstream GEO skills.

## client_intake.json

Accept either the full `geo-client-intake-normalizer` output or a flattened intake object.

Preferred normalized shape:

```json
{
  "client_intake": {
    "brand_name": {"value": "CreativeHit"},
    "website_domain": {"value": "https://creativehit.ai"},
    "product_or_service_direction": {"value": ["AI ad creative generator"]},
    "target_customer_roles": {"value": ["ecommerce marketer"]},
    "target_countries_or_regions": {"value": ["US"]},
    "languages": {"value": ["English"]},
    "target_optimization_platforms": {"value": ["ChatGPT"]},
    "competitor_names": {"value": ["Creatify", "Pencil", "AdCreative.ai"]},
    "geo_optimization_goals": {"value": []},
    "constraints": {"value": []}
  }
}
```

Flattened shape is also acceptable:

```json
{
  "brand_name": "CreativeHit",
  "website_domain": "https://creativehit.ai",
  "product_or_service_direction": ["AI ad creative generator"],
  "competitor_names": ["Creatify", "Pencil", "AdCreative.ai"]
}
```

Required fields for meaningful analysis:

- `brand_name`
- `competitor_names`

Recommended fields:

- `website_domain`
- `product_or_service_direction`
- `target_customer_roles`
- `target_countries_or_regions`
- `languages`
- `target_optimization_platforms`
- `geo_optimization_goals`
- `constraints`

## prompt_set.json

Accept `geo-intent-prompt-generator` output:

```json
{
  "topics": [
    {
      "topic_id": "T01",
      "topic": "AI ad creative generator for ecommerce",
      "persona": "ecommerce marketer"
    }
  ],
  "prompt_groups": [
    {
      "topic_id": "T01",
      "topic": "AI ad creative generator for ecommerce",
      "prompts": [
        {
          "prompt_id": "P001",
          "prompt": "What are the best AI ad creative generators for ecommerce?",
          "brand_type": "unbranded",
          "intent_stage": "commercial",
          "persona": "ecommerce marketer",
          "market": "US",
          "language": "English",
          "platform": "ChatGPT"
        }
      ]
    }
  ]
}
```

Use `prompt_id` to attach topic, persona, market, language, brand type, and intent stage to each response. If prompt metadata is missing, fall back to fields already present in the cleaned response record.

## cleaned_responses.jsonl

One JSON object per cleaned response:

```json
{
  "response_id": "R0001",
  "prompt_id": "P001",
  "topic_id": "T01",
  "topic": "AI ad creative generator for ecommerce",
  "platform": "ChatGPT",
  "persona": "ecommerce marketer",
  "brand_type": "unbranded",
  "intent_stage": "commercial",
  "clean_answer": "...",
  "raw_answer": "...",
  "is_analyzable": true,
  "answer_quality_status": "analyzable"
}
```

Only analyze records where `is_analyzable` is true. Preserve `clean_answer` and response identifiers in outputs for traceability.
