# Prompt Distribution

Default distribution:

- Unbranded: 80%
- Branded: 20%
- Info: 25%
- Commercial: 50%
- Transactional: 25%

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
