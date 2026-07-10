# Output Schema

Write outputs to the selected content directory.

## Directory Layout

```text
content_run/
├── content_plan.md
├── content_package.json
├── qa_report.json
└── drafts/
    ├── content-001-best-ai-ad-creative-generators.md
    └── content-002-brand-compliant-ai-ad-creative-generation.md
```

## content_package.json

```json
{
  "package_method": "rule_based_geo_content_writer_v1",
  "generated_at": "",
  "client_brand": "CreativeHit",
  "website_domain": "https://creativehit.ai",
  "generated_assets": [
    {
      "content_id": "CONTENT001",
      "asset_type": "comparison_article",
      "title": "Best AI Ad Creative Generators for Ecommerce Teams",
      "target_topic": "AI ad creative generator for ecommerce",
      "monitoring_role_focus": "market_proxy",
      "market_weighted_visibility_score": 0.21,
      "market_qualified_recommendation_rate": 0.0,
      "target_personas": ["ecommerce marketer"],
      "source_gap_signals": [],
      "source_risk_signals": [],
      "draft_file": "drafts/content-001-best-ai-ad-creative-generators-for-ecommerce-teams.md",
      "recommended_url_slug": "/best-ai-ad-creative-generators-for-ecommerce-teams",
      "status": "draft",
      "needs_client_evidence": true
    }
  ],
  "coverage": {
    "priority_topics_covered": [],
    "risk_fixes_covered": [],
    "uncovered_items": []
  }
}
```

## content_plan.md

Human-readable production plan containing:

- package scope
- generated asset table
- priority topics covered
- risk fixes covered
- evidence placeholders to resolve

## qa_report.json

```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "coverage": {},
  "draft_checks": []
}
```
