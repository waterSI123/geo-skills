# Prompt Quality Rubric

Use this rubric before final output.

## Keep Prompts That

- Sound like a real user asking an AI assistant.
- Have one clear intent.
- Are natural in the target market and language.
- Could plausibly trigger an AI answer that lists, recommends, compares, cites, or explains brands.
- Are relevant to the customer's service direction.
- Are specific enough to be actionable but not so narrow that no answer is likely.
- Represent a plausible market-proxy question from a buyer, user, evaluator, founder, marketer, or operator.
- Can be backed by at least one `source_basis` item such as `buyer_question`, `customer_pain_point`, `sales_call_question`, `search_term`, `ad_keyword`, `competitor_context`, `website_research`, or `business_kpi`.

## Remove Or Rewrite Prompts That

- Look like SEO keyword fragments.
- Stuff too many modifiers into one phrase.
- Ask the model to mention or rank the customer's brand artificially.
- Combine multiple unrelated intents.
- Are only minor rewrites of another prompt.
- Are too generic for the business, such as `best AI tools`.
- Make unsupported claims about the brand.
- Are unnatural for the target market.
- Are so vertical or artificial that they are likely to improve only the dashboard, not real buyer visibility.
- Ask directly whether the monitored brand appears, is missing, or should be recommended.

## Practical Limits

- Prefer prompts under 160 characters unless the language or use case requires more.
- Use natural question or search phrasing.
- Keep branded prompts realistic: review, comparison, pricing, alternatives, "is it good for X".
- Keep unbranded prompts useful for monitoring category discovery and recommendation behavior.
- Assign `prompt_realism_score` from `0` to `1`; use `0.8+` only for natural, common buyer questions.
- Assign `overfit_risk`: `low` for broad realistic questions, `medium` for niche but plausible questions, and `high` for narrow diagnostic probes.
- Main KPI prompts should usually have `monitoring_role` of `market_proxy` or `buyer_evaluation`.

## QA Report

Include:

- Total topics.
- Total prompts.
- Brand distribution.
- Intent distribution.
- Monitoring role distribution.
- Average prompt realism score.
- Market-proxy demand weight share.
- Localization notes.
- Assumptions.
- Website/source gaps.
- Excluded or rewritten prompt patterns.
