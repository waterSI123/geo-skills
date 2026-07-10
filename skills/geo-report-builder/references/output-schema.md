# Output Schema

Write these files to the selected output directory.

## geo_diagnostic_report.md

Client-facing Markdown report with required sections:

```text
# GEO Diagnostic Report
## Executive Summary
## Project Scope
## Market-Proxy GEO Visibility Scorecard
## Competitor Comparison
## Topic-Level Diagnosis
## Content Gap Findings
## Risk Findings
## Prioritized GEO Action Plan
## Method Notes
```

`Method Notes` is allowed as a final section for sample and limitation framing.

## geo_diagnostic_report.json

```json
{
  "report_method": "rule_based_report_builder_v1",
  "generated_at": "",
  "source_files": {},
  "client": {},
  "scope": {},
  "executive_summary": [],
  "scorecard": [],
  "market_proxy_scorecard": [],
  "competitor_comparison": [],
  "topic_diagnosis": [],
  "content_gap_findings": [],
  "risk_findings": [],
  "action_plan": [],
  "method_notes": []
}
```

## report_brief_for_content_writer.json

Follow `content-writer-brief-schema.md`.

## executive_summary.md

Compact standalone summary. It should repeat the client brand, core metric highlights, top opportunity topic, top risk, and recommended next step.
