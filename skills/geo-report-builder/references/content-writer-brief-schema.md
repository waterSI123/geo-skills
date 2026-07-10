# Content Writer Brief Schema

`report_brief_for_content_writer.json` is the downstream handoff for `geo-content-writer`.

## Top-Level Shape

```json
{
  "client_brand": "CreativeHit",
  "website_domain": "creativehit.ai",
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

## priority_topics

```json
{
  "topic": "Brand compliant ad creative generation",
  "opportunity_level": "high",
  "target_personas": ["performance marketing manager"],
  "strong_competitors": ["Creatify", "AdCreative.ai"],
  "content_gap_signals": ["policy_compliance_gap"],
  "risk_signals": [],
  "recommended_assets": ["compliance page", "comparison article"],
  "core_message": "CreativeHit helps performance marketers generate ad creatives while following brand guidelines and platform policies.",
  "suggested_content_angle": "Position the client brand as a credible option for this topic.",
  "source_finding_ids": ["F001"]
}
```

## risk_fixes

```json
{
  "risk_type": "brand_existence_uncertain",
  "severity": "high",
  "recommended_fix": "Add entity validation signals such as official site content, profiles, schema, and third-party mentions.",
  "review_required": false,
  "source_finding_ids": ["F003"]
}
```

## content_priorities

```json
{
  "priority": 1,
  "action": "Create a brand-compliance focused comparison page",
  "mapped_topic": "Brand compliant ad creative generation",
  "expected_geo_impact": "Increase visibility and recommendation strength in compliance-related prompts.",
  "next_skill": "geo-content-writer"
}
```
