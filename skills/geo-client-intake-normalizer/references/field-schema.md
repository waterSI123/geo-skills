# Field Schema

Extract exactly these core GEO intake fields. Always include every field in final output.

## Field Object

Each field uses:

```json
{
  "value": "",
  "status": "confirmed",
  "sources": ["S01"],
  "raw_evidence": []
}
```

Use arrays for multi-value fields. Use an empty string or empty array when missing.

Allowed statuses:

- `confirmed`: directly supported by provided material.
- `inferred`: reasonable but not directly stated; explain in `assumptions`.
- `missing`: no reliable value found.
- `conflicting`: multiple supported values disagree; explain in `conflicts`.

## Core Fields

### brand_name

The client brand, product brand, or company name being optimized for GEO visibility.

Examples: `CreativeHit`, `Acme AI`, `Northstar CRM`.

### website_domain

The official website domain or homepage URL. Prefer canonical HTTPS URLs when available.

Examples: `https://creativehit.ai`, `https://example.com`.

### product_or_service_direction

What the customer sells or wants to be known for. Extract as concise service/product phrases, not long marketing copy.

Examples: `AI ad creative generator`, `B2B SaaS CRM`, `cross-border logistics platform`.

### target_customer_roles

Buyer personas, user roles, or decision-maker roles.

Examples: `ecommerce marketer`, `performance marketing manager`, `DTC founder`.

### target_countries_or_regions

Markets to monitor or optimize for. Normalize to country/region names.

Examples: `United States`, `United Kingdom`, `Southeast Asia`.

### languages

Languages for monitoring prompts, reports, or content.

Examples: `English`, `Chinese`, `Spanish`.

### target_optimization_platforms

AI answer platforms or surfaces the client wants to influence or monitor.

Examples: `ChatGPT`, `Perplexity`, `Gemini`, `Google AI Overview`.

### competitor_names

Direct competitors, alternatives, substitutes, or brands the client wants to compare against.

Examples: `Creatify`, `Pencil`, `AdCreative.ai`.

### geo_optimization_goals

The intended GEO outcome. Extract business goals, monitoring goals, and optimization goals.

Examples:

- Increase brand mention rate in AI answers.
- Appear in recommended tool lists.
- Improve competitive comparison against named alternatives.
- Identify content gaps and generate optimization content.

### constraints

Rules, requirements, and limitations that should shape downstream prompt generation, analysis, reports, and content.

Examples:

- Follow brand guidelines.
- Follow platform ad policies.
- Avoid unsupported medical claims.
- Do not mention pricing.
- Use US English.

## Critical Missing Fields

Treat these as blocking for prompt generation when absent and not safely inferable:

- `product_or_service_direction`
- `target_countries_or_regions`
- `languages`
- `target_optimization_platforms`
