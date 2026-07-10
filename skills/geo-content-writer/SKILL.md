---
name: geo-content-writer
description: Generate GEO / AI Visibility optimization content packages from report-builder handoff files. Use when the user has report_brief_for_content_writer.json, client_intake.json, and optionally geo_diagnostic_report.json, and needs content_plan.md, content_package.json, qa_report.json, and Markdown drafts for comparison articles, category landing pages, compliance pages, proof asset pages, FAQ sections, or entity clarification content. This skill does not collect monitoring data, analyze responses, build diagnostic reports, publish to a CMS, or invent unsupported case studies, pricing, reviews, integrations, or product claims.
---

# GEO Content Writer

Turn GEO diagnosis and content briefs into publishable Markdown content drafts that help AI systems understand, classify, and recommend the client brand.

## Scope

This MVP writes content packages:

- `content_plan.md`: production plan and rationale.
- `content_package.json`: structured inventory of generated assets.
- `drafts/*.md`: Markdown drafts with frontmatter and GEO-oriented sections.
- `qa_report.json`: deterministic coverage and safety checks.

Supported MVP asset types:

- `comparison_article`
- `category_landing_page`
- `compliance_policy_page`
- `proof_asset_page`
- `faq_section`
- `entity_clarification_content`

## References

Read the relevant references before producing final output:

- `references/input-schema.md` before loading briefs or client context.
- `references/asset-types.md` before selecting content asset types.
- `references/content-templates.md` before drafting content.
- `references/geo-writing-rules.md` before writing GEO-oriented copy.
- `references/evidence-and-claims-rules.md` before making product, proof, competitor, pricing, review, or integration claims.
- `references/output-schema.md` before writing package outputs.
- `references/qa-rules.md` before validation.

Use scripts for deterministic file work:

- `scripts/write_content_package.py`
- `scripts/validate_content_package.py`

## Workflow

1. Load inputs.
   - Use `report_brief_for_content_writer.json` from `geo-report-builder`.
   - Use `client_intake.json` for brand, website, offering, audience, market, language, platform, competitors, goals, and constraints.
   - Use `geo_diagnostic_report.json` as optional context for action plan and report findings.
   - Use `brand_guidelines.md` or source materials only when supplied by the user.

2. Select content assets.
   - Prioritize high-opportunity topics and high-severity risk fixes.
   - Map `recommended_assets` and gap/risk signals to supported MVP asset types.
   - Default to at most 5 drafts unless the user asks for more.

3. Draft content.
   - Include frontmatter for target topic, persona, market, language, source signals, and URL slug.
   - Write clear brand/entity/category context.
   - Include FAQ sections for AI-readable entity and decision answers.
   - Include competitor context without inventing competitor facts.
   - Mark missing proof with `[CLIENT EVIDENCE NEEDED]`.

4. Build package metadata.
   - Write `content_package.json` with generated assets, coverage, source signals, status, draft paths, and evidence flags.
   - Write `content_plan.md` summarizing priority, asset type, topic, and next editing steps.

5. Validate.
   - Ensure high-priority topics and risks are covered where possible.
   - Ensure drafts include client brand, website/domain, topic, persona, FAQ, and evidence placeholders when needed.
   - Ensure no required files are missing.

## Script Examples

Generate a content package:

```bash
skills/geo-content-writer/scripts/write_content_package.py \
  --content-brief report_run/report_brief_for_content_writer.json \
  --client-intake client_intake.json \
  --report-json report_run/geo_diagnostic_report.json \
  --output-dir content_run \
  --max-drafts 5
```

Validate outputs:

```bash
skills/geo-content-writer/scripts/validate_content_package.py \
  --content-dir content_run
```

## Boundaries

- Do not collect new monitoring responses.
- Do not analyze cleaned responses or recalculate visibility metrics.
- Do not rebuild the diagnostic report.
- Do not browse for competitor facts unless the user explicitly asks for a research extension.
- Do not invent case studies, pricing, reviews, integrations, customer names, benchmarks, or product features.
- Do not promise platform-policy approval or guaranteed ad compliance.
- Do not publish to a CMS in the MVP.
- Do not remove `[CLIENT EVIDENCE NEEDED]` placeholders unless real client evidence is provided.
