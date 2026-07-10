---
name: geo-report-builder
description: Build client-facing market-proxy GEO / AI Visibility diagnostic reports from structured analysis outputs. Use when the user has visibility_analysis.json, topic_analysis.json, opportunity_findings.json, plus client_intake.json and prompt_set.json, and needs geo_diagnostic_report.md, geo_diagnostic_report.json, and report_brief_for_content_writer.json for service delivery, with primary KPIs based on market_proxy and buyer_evaluation prompts rather than diagnostic probes. This skill does not collect data, clean responses, recalculate brand metrics, generate prompts, or write the final optimization articles.
---

# GEO Report Builder

Turn `geo-response-analyzer` outputs into a readable, evidence-grounded GEO diagnostic report and a structured brief for downstream content writing.

## Scope

This MVP builds:

- `geo_diagnostic_report.md`: client-facing Markdown report.
- `geo_diagnostic_report.json`: structured report data.
- `report_brief_for_content_writer.json`: prioritized handoff for `geo-content-writer`.
- `executive_summary.md`: compact operator/client summary.

## References

Read the relevant references before producing final output:

- `references/input-schema.md` before loading report inputs.
- `references/report-structure.md` before drafting report sections.
- `references/narrative-rules.md` before writing client-facing interpretation.
- `references/action-plan-rules.md` before prioritizing recommendations.
- `references/content-writer-brief-schema.md` before writing the downstream brief.
- `references/output-schema.md` before final outputs.

Use scripts for deterministic file work:

- `scripts/build_report.py`
- `scripts/validate_report.py`

## Workflow

1. Load inputs.
   - Use `client_intake.json` for brand, website, audience, market, language, platform, competitors, goals, and constraints.
   - Use `prompt_set.json` for prompt/topic counts and scope metadata.
   - Use `visibility_analysis.json`, `topic_analysis.json`, and `opportunity_findings.json` from `geo-response-analyzer`.
   - Use `analysis_summary.md` only as optional supporting context.

2. Preserve metric authority.
   - Do not recalculate visibility, share of voice, average position, recommendation quality, or sentiment from raw responses.
   - Read `primary_kpis` and `market_proxy_metrics` from `visibility_analysis.json` and topic values from `topic_analysis.json`.
   - State that primary KPIs are based on market-proxy and buyer-evaluation prompts; diagnostic and brand-control prompts are supporting context only.

3. Build the report.
   - Lead with conclusions, then supporting evidence.
   - Include the eight required report sections.
   - Convert field-heavy analysis output into client-readable language.
   - Use market-proxy wording for scorecard and executive summary.
   - Keep risk findings separate from content opportunities.

4. Build the content-writer brief.
   - Select priority topics and findings.
   - Map each priority to recommended content assets.
   - Include market-proxy focus, market weighted visibility, strong competitors, gap signals, risk signals, suggested angles, and next-step priority.

5. Validate.
   - Ensure required report files exist.
   - Ensure required sections and core metrics are present.
   - Ensure the content-writer brief is present and references the client brand.

## Script Examples

Build a report:

```bash
skills/geo-report-builder/scripts/build_report.py \
  --client-intake client_intake.json \
  --prompt-set prompt_set.json \
  --visibility-analysis analysis_run/visibility_analysis.json \
  --topic-analysis analysis_run/topic_analysis.json \
  --opportunity-findings analysis_run/opportunity_findings.json \
  --output-dir report_run
```

Validate report outputs:

```bash
skills/geo-report-builder/scripts/validate_report.py \
  --report-dir report_run
```

## Boundaries

- Do not generate or rewrite prompts.
- Do not run ChatGPT or collect monitoring responses.
- Do not clean raw answer text.
- Do not recalculate brand metrics from cleaned responses.
- Do not generate final GEO articles, landing pages, or optimization copy.
- Do not present review-required findings as confirmed errors.
- Do not create PDF, DOCX, or PPTX deliverables in the MVP unless the user explicitly asks for a format extension.
