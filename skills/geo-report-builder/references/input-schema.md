# Input Schema

Use these inputs from upstream GEO skills.

## Required Files

```text
client_intake.json
prompt_set.json
visibility_analysis.json
topic_analysis.json
opportunity_findings.json
```

## Optional Files

```text
analysis_summary.md
analyzed_responses.jsonl
cleaning_report.json
run_summary.md
```

The MVP script only requires the five required files. Optional files can support manual report polishing but should not override structured metrics.

## client_intake.json

Accept either the full normalized output or a flattened object.

Important fields:

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

## prompt_set.json

Use for scope counts:

- topic count
- prompt count
- personas
- market
- language
- platform

## visibility_analysis.json

Use as the authority for:

- visibility score and rank
- share of voice and rank
- average position and rank
- sentiment score and rank
- tracked brand list
- analyzable response count
- brand-mentioning response count

## topic_analysis.json

Use as the authority for:

- topic opportunity level
- client absent rate
- weak recommendation rate
- strong competitors
- content gap counts
- risk signal counts

## opportunity_findings.json

Use as the authority for:

- content gap findings
- risk findings
- severity
- evidence response IDs
- recommended next steps
- review-required status
