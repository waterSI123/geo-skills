---
name: geo-intent-prompt-generator
description: Generate GEO / AI Visibility intent prompt sets for overseas markets. Use when the user wants to turn a product or service direction, target personas, market, language, platform, context, and optional website domain into commercial search topics and realistic AI monitoring prompts grouped by topic. This skill is for MVP prompt generation, not keyword difficulty scoring, competition scoring, pricing, content writing, or AI visibility measurement execution.
---

# GEO Intent Prompt Generator

Generate an MVP-ready AI Visibility prompt set from customer business inputs. Treat "prompt generation" as topic and prompt design, not SEO keyword expansion or a packaging exercise.

## Defaults

- Topics: 8 unless the user specifies another number.
- Prompts per topic: 5 unless the user specifies another number.
- Brand mix: 80% unbranded, 20% branded.
- Intent mix: 25% info, 50% commercial, 25% transactional.
- Default output: grouped by topics.

## Required Inputs

Use the user's provided inputs:

- Services: product or service direction.
- Personas: target user roles or buying decision makers.
- Target market and language.
- Platform: ChatGPT, Perplexity, Gemini, Google AI Overview, etc.
- Additional context: positioning, competitors, advantages, industry constraints, or focus areas.
- Website domain: optional but strongly recommended.

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
   - Required input fields: Services, Personas, Target Market, Language, Platform, Additional Context.
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
   - Apply branded/unbranded and info/commercial/transactional distribution across the full prompt set.
   - Adapt the distribution by topic when a topic naturally needs more or fewer branded, info, commercial, or transactional prompts.
   - Include branded prompts only when a brand name is known or inferable from the website.
   - Do not force exact distribution if it makes prompts unnatural; explain deviations in QA.

5. QA, dedupe, and localize.
   - Remove prompts that are not something a real user would ask an AI assistant.
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
- Do not use a website domain to crawl private pages, login areas, or non-public data.
