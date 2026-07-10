---
name: geo-intent-prompt-generator
description: Generate market-proxy-first GEO / AI Visibility intent prompt sets for overseas markets. Use when the user wants to turn services, personas, target market, language, platform, customer questions, pain points, business goals, additional context, competitors, and an optional website domain into realistic AI monitoring prompts grouped by buyer topic. This skill is for MVP prompt generation and demand-proxy design, not keyword difficulty scoring, competition scoring, pricing, content writing, or AI visibility measurement execution.
---

# GEO Intent Prompt Generator

Generate an MVP-ready AI Visibility prompt set from customer business inputs. Treat "prompt generation" as topic and prompt design, not SEO keyword expansion or a packaging exercise.

## Defaults

- Topics: 8 unless the user specifies another number.
- Prompts per topic: 5 unless the user specifies another number.
- Brand mix: 80% unbranded, 20% branded.
- Intent mix: 25% info, 50% commercial, 25% transactional.
- Monitoring role mix: about 70% `market_proxy`, 20% `buyer_evaluation`, and 10% `diagnostic_probe` or `brand_control`.
- Default output: grouped by topics.

## Required Inputs

Use the user's provided inputs:

- Services: product or service direction.
- Personas: target user roles or buying decision makers.
- Target Market: country, region, or market to monitor.
- Language: output language for topics and prompts.
- Platform: ChatGPT, Perplexity, Gemini, Google AI Overview, etc.
- Additional Context: positioning, advantages, industry constraints, or focus areas.
- Competitors: direct competitors, alternatives, substitutes, or brands the customer wants to compare against.
- Website Domain: optional but strongly recommended.
- Market-proxy demand inputs: actual buyer questions, customer pain points, buying triggers, sales-call questions, search/ad terms, customer language, conversion goals, and business KPIs when available.

If important inputs are missing, make a conservative assumption and list it in `assumptions`. Ask only when market, language, service direction, or platform is missing and cannot be inferred.

## References

Read these before generating the final prompt set:

- `references/website-research.md` when a website domain is provided.
- `references/topic-taxonomy.md` before creating topics.
- `references/prompt-distribution.md` before generating prompts.
- `references/prompt-quality-rubric.md` before QA.
- `references/output-schema.md` before final output.

Use scripts only when a JSON prompt set file exists or when the user asks for validation/deduplication:

- `scripts/dedupe_prompts.py`
- `scripts/validate_prompt_set.py`

## Workflow

1. Collect and normalize business inputs.
   - Required input fields: Services, Personas, Target Market, Language, Platform, Additional Context, Competitors.
   - Website Domain is optional but strongly recommended.
   - Identify brand name, competitors, constraints, and assumptions only when supported by user input or website research.

2. Research the official website when a domain is provided.
   - Inspect public pages only.
   - Extract brand, product, selling points, scenarios, customers, competitors, and limitations.
   - Produce a `website_research_brief`.
   - Ask the user to confirm or edit the brief before generating topics unless the user explicitly asks for a one-pass draft.

3. Generate topics.
   - Generate the requested number of commercial search topics from the user input plus confirmed or draft website research.
   - Each topic should be one distinct buyer/search intention, not a minor wording variant.
   - Use topic IDs such as `T01`, `T02`.

4. Generate prompts by topic.
   - For each topic, generate realistic AI-user prompts in the target language.
   - Make market-proxy prompts simulate common buyer/user questions, not narrow test phrases designed to improve a dashboard.
   - Apply branded/unbranded and info/commercial/transactional distribution across the full prompt set.
   - Assign `monitoring_role`, `prompt_realism_score`, `demand_weight`, `buyer_journey_stage`, `source_basis`, and `overfit_risk` to every prompt.
   - Adapt the distribution by topic when a topic naturally needs more or fewer branded, info, commercial, or transactional prompts.
   - Include branded prompts only when a brand name is known or inferable from the website.
   - Do not force exact distribution if it makes prompts unnatural; explain deviations in QA.

5. QA, dedupe, and localize.
   - Remove prompts that are not something a real user would ask an AI assistant.
   - Down-weight or rewrite prompts that are too vertical, too synthetic, or only useful for a diagnostic dashboard.
   - Remove duplicates and near-duplicates.
   - Remove SEO-fragment strings and unnatural query-stuffed phrases.
   - Check market/language naturalness.
   - Keep commercial prompts as the core monitoring surface.

6. Output prompt groups.
   - Return the full structure from `references/output-schema.md`.
   - Group prompts under topics.
   - Include `qa_report` with counts, distribution, assumptions, source gaps, and any prompts that were intentionally excluded.

## Website Confirmation

If a website domain is provided and the user has not asked for a one-pass draft, stop after `website_research_brief` and ask the user to confirm or edit it. If the user asks for a complete output in one pass, proceed and mark the brief as `unconfirmed`.

## Do Not

- Do not calculate competition, keyword difficulty, premium coefficients, or pricing.
- Do not generate old-style SEO keyword lists as the final artifact.
- Do not invent product claims, certifications, integrations, customers, pricing, or competitors.
- Do not make branded prompts that ask the model to mention the brand; prompts must simulate real users, not test harness instructions.
- Do not optimize prompts to make the client look better in the monitoring dashboard; optimize for realistic buyer demand coverage.
- Do not use a website domain to crawl private pages, login areas, or non-public data.
