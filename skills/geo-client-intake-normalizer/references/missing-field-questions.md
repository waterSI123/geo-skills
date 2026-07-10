# Missing Field Questions

Ask only useful questions. Do not block on every optional gap.

## Blocking Questions

Ask these when the field is missing and cannot be safely inferred:

- `product_or_service_direction`: "What product or service should this GEO project focus on?"
- `target_countries_or_regions`: "Which country or region should the GEO monitoring and optimization target?"
- `languages`: "Which language should prompts, analysis, and content use?"
- `target_optimization_platforms`: "Which AI answer platforms should be monitored or optimized, such as ChatGPT, Perplexity, Gemini, or Google AI Overview?"

## Important Non-Blocking Questions

Ask these when they would improve downstream quality:

- `brand_name`: "What brand or product name should be tracked?"
- `website_domain`: "What is the official website domain?"
- `target_customer_roles`: "Which buyer personas or user roles should the prompts represent?"
- `competitor_names`: "Which competitors or alternatives should be included in comparison prompts?"
- `geo_optimization_goals`: "What outcome matters most: more mentions, better ranking, stronger recommendation language, competitor displacement, or content gap discovery?"
- `constraints`: "Are there brand, legal, platform-policy, claim, tone, or compliance constraints that downstream content must follow?"
- `actual_buyer_questions`: "What questions do real prospects, customers, or sales leads ask before choosing a solution like this?"
- `customer_pain_points`: "What customer pains, buying triggers, or repeated sales-call questions should the prompts simulate?"
- `conversion_goals`: "Which business outcomes should GEO optimization influence, such as AI referral traffic, demo requests, trials, qualified leads, or revenue?"

## Missing Fields Output

Use:

```json
{
  "field": "target_optimization_platforms",
  "severity": "blocking",
  "question": "Which AI answer platforms should be monitored or optimized, such as ChatGPT, Perplexity, Gemini, or Google AI Overview?"
}
```

Allowed severities:

- `blocking`
- `important`
- `optional`

## Asking Rules

- If the user asked for a one-pass draft, do not stop; output assumptions and missing fields.
- If multiple blocking fields are missing, ask a compact set of questions.
- If the user provided enough information to continue, proceed and mark uncertain values as `inferred`.
