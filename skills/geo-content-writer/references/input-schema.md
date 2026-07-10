# Input Schema

## Required Files

```text
report_brief_for_content_writer.json
client_intake.json
```

## Recommended File

```text
geo_diagnostic_report.json
```

## Optional Files

```text
brand_guidelines.md
source_materials/
geo_diagnostic_report.md
opportunity_findings.json
topic_analysis.json
```

Optional evidence can be used to replace `[CLIENT EVIDENCE NEEDED]` placeholders. Do not invent proof when source materials are missing.

## report_brief_for_content_writer.json

Expected top-level fields:

```json
{
  "client_brand": "CreativeHit",
  "website_domain": "https://creativehit.ai",
  "product_or_service_direction": [],
  "target_customer_roles": [],
  "target_countries_or_regions": [],
  "languages": [],
  "target_optimization_platforms": [],
  "priority_topics": [],
  "risk_fixes": [],
  "content_priorities": []
}
```

`priority_topics` should drive the first set of drafts:

```json
{
  "topic": "AI ad creative generator for ecommerce",
  "opportunity_level": "high",
  "target_personas": ["ecommerce marketer"],
  "strong_competitors": ["Creatify"],
  "content_gap_signals": ["competitor_recommended_client_absent"],
  "risk_signals": [],
  "recommended_assets": ["comparison article", "category landing page"],
  "core_message": "",
  "suggested_content_angle": "",
  "source_finding_ids": ["F001"]
}
```

`risk_fixes` should trigger entity clarification, FAQ, or manual-review content:

```json
{
  "risk_type": "brand_existence_uncertain",
  "severity": "high",
  "recommended_fix": "",
  "review_required": false,
  "source_finding_ids": ["F003"]
}
```

## client_intake.json

Accept normalized or flattened shape. Important fields:

- `brand_name`
- `website_domain`
- `product_or_service_direction`
- `target_customer_roles`
- `target_countries_or_regions`
- `languages`
- `target_optimization_platforms`
- `competitor_names`
- `geo_optimization_goals`
- `constraints`

## geo_diagnostic_report.json

Use only as supporting context for:

- action plan
- content gap findings
- risk findings
- method notes

Do not use it to recalculate analyzer metrics.
