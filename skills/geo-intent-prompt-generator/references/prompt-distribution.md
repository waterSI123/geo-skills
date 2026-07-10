# Prompt Distribution

Default distribution:

- Unbranded: 80%
- Branded: 20%
- Info: 25%
- Commercial: 50%
- Transactional: 25%
- Monitoring role: 70% `market_proxy`, 20% `buyer_evaluation`, 10% `diagnostic_probe` or `brand_control`

Primary monitoring must be market-proxy first. A prompt set that looks good only because it contains narrow diagnostic prompts is not acceptable.

## Brand Type

`unbranded` prompts simulate discovery-stage or category-stage users. They should not mention the customer's brand.

Examples:

- `best AI ad creative generators for ecommerce brands`
- `which AI tools can generate compliant Meta and TikTok ads?`

`branded` prompts simulate users who already know the brand or are comparing it. Use only when the brand name is known.

Examples:

- `CreativeHit vs Creatify for ecommerce ad creatives`
- `is CreativeHit good for brand-compliant ad generation?`

## Intent Stage

`info`: user is learning the category, problem, or method.

Examples:

- `what is AI creative generation?`
- `can AI ad creative tools follow brand guidelines?`

`commercial`: user is comparing options, shortlisting tools, or evaluating criteria. This is the core GEO monitoring surface.

Examples:

- `best AI ad creative generators for ecommerce brands`
- `alternatives to Creatify and Pencil for ad creative generation`

`transactional`: user is close to buying, trialing, pricing, implementing, or switching.

Examples:

- `how to choose an AI ad creative generator for a DTC brand`
- `CreativeHit pricing`

## Allocation Rules

- Apply distribution globally across the full prompt set.
- Do not make every topic mechanically identical.
- Prioritize unbranded commercial prompts when totals are small.
- If brand name is unknown, convert branded quota into unbranded commercial prompts and explain in QA.
- If competitors are missing, generate comparison prompts around criteria and alternatives rather than named competitors.
- Keep `market_proxy` and `buyer_evaluation` prompts as at least 70% of count and 75% of total demand weight.
- Use `diagnostic_probe` for suspected issues such as compliance gaps, missing proof assets, entity confusion, or competitor advantage. Keep these out of primary KPI interpretation.
- Use `brand_control` sparingly for entity and website verification.

## Demand Weights

Recommended starting values:

- `market_proxy`: `1.0`
- `buyer_evaluation`: `0.75`
- `diagnostic_probe`: `0.35`
- `brand_control`: `0.25`

Increase a weight only when the prompt is clearly supported by real buyer questions, sales-call questions, search terms, ad keywords, or customer language. Lower the weight when a prompt is useful for diagnosis but unlikely to be asked often by a real user.
