---
name: geo-client-intake-normalizer
description: Extract and normalize GEO / AI Visibility client project intake from messy multi-source materials. Use when the user provides free-form client text, forms, chat transcripts, website domains, competitor notes, PDFs, PPTX files, DOC/DOCX files, spreadsheets, or other uploaded project materials and needs standardized client fields for downstream GEO skills. This skill produces a source-backed client_intake object for prompt generation, monitoring, analysis, reporting, and content writing; it does not generate prompts, run monitoring, analyze AI responses, or write optimization content.
---

# GEO Client Intake Normalizer

Convert messy client-provided materials into a standardized GEO project intake. Focus on extracting, normalizing, and source-backing the required fields for downstream skills.

## Core Fields

Always output these fields, even when missing:

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

Each field must include `value`, `status`, and `sources`. Allowed `status` values are `confirmed`, `inferred`, `missing`, and `conflicting`.

## References

Read the relevant references before producing final output:

- `references/field-schema.md` for field definitions and extraction rules.
- `references/source-handling.md` when client materials include files, chat transcripts, forms, websites, or multiple sources.
- `references/normalization-rules.md` before standardizing countries, languages, platforms, names, and constraints.
- `references/missing-field-questions.md` before writing missing-field follow-up questions.
- `references/output-schema.md` before final output.

Use `scripts/validate_client_intake.py` when a JSON intake file exists or when the user asks for validation.

## Workflow

1. Inventory sources.
   - Assign source IDs such as `S01`, `S02`.
   - Record source type, name, usable status, and notes.
   - Use public website pages only when a website domain is provided.

2. Extract source text.
   - Prefer structured extraction for PDFs, PPTX, DOCX, CSV, XLSX, and forms.
   - Preserve source attribution for facts.
   - Do not treat inferred positioning as confirmed.

3. Extract the core fields.
   - Fill every core field.
   - Use arrays for multi-value fields.
   - Record the source IDs that support each field.
   - Put unsupported but useful interpretation in `assumptions`.

4. Normalize values.
   - Standardize country/region names, language names, GEO platform names, competitor names, and repeated aliases.
   - Keep the customer's original wording in `raw_evidence` when useful.

5. Detect missing fields and conflicts.
   - Put absent fields in `missing_fields`.
   - Put contradictory source-backed values in `conflicts`.
   - Ask only blocking questions when service direction, target market, language, or optimization platform cannot be inferred.

6. Decide downstream readiness.
   - Mark `ready_for_prompt_generation` true only when service direction, target market, language, and optimization platform are available as confirmed or low-risk inferred values.
   - Mark monitoring, analysis, report, and content readiness based on whether their required upstream artifacts exist.

7. Output both machine and human summaries.
   - Return `client_intake.json`-style structured JSON.
   - Also include a concise `intake_summary` for human review.

## Boundaries

- Do not generate GEO prompts.
- Do not run ChatGPT, Perplexity, Gemini, Google AI Overview, or other monitoring.
- Do not analyze AI answer visibility.
- Do not generate optimization articles or landing-page copy.
- Do not perform deep competitor research unless explicitly asked; only normalize competitor information provided by the client or found in provided sources.
- Do not invent products, markets, claims, integrations, customers, compliance certifications, pricing, or competitors.
- Do not mark inferred information as confirmed.
