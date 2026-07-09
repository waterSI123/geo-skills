# Website Research

Use this reference when the user provides a website domain.

## Goal

Extract source-backed business context that improves topic and prompt generation. Website research is not SEO crawling. It is positioning discovery for AI Visibility monitoring.

## Pages To Inspect

Start with the homepage, then inspect high-value public pages when available:

- `/product`
- `/features`
- `/solutions`
- `/use-cases`
- `/pricing`
- `/customers`
- `/case-studies`
- `/integrations`
- `/about`
- `/blog`
- `/compare`
- `/alternatives`

If exact paths are unavailable, use homepage navigation links and inspect up to 12 public pages. Prefer English pages for English-market prompt generation.

## Extracted Fields

Return a `website_research_brief` with:

- `domain`
- `official_brand_name`
- `one_line_description`
- `core_services`
- `target_personas`
- `products`
- `selling_points`
- `scenarios`
- `customers`
- `competitors`
- `integrations`
- `limitations`
- `source_urls`
- `confidence`
- `confirmation_status`
- `unconfirmed_or_inferred_items`

## Rules

- Use only public pages.
- Keep facts source-backed.
- If a claim is useful but unsupported, put it in `unconfirmed_or_inferred_items`.
- Do not invent competitors, customers, certifications, integrations, or pricing.
- If the site is vague, use the user's input as the primary business intent and mark the website brief as low confidence.
