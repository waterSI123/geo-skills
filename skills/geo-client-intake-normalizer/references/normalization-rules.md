# Normalization Rules

Normalize values before final output. Preserve important original wording in `raw_evidence`.

## Countries And Regions

Use common English names:

- `US`, `USA`, `U.S.`, `America` -> `United States`
- `UK`, `U.K.` -> `United Kingdom`
- `SEA` -> `Southeast Asia`
- `EU` -> `European Union`

When a source says "global" or "overseas", keep it as a region-like value and mark confidence lower unless a target market is also specified.

## Languages

Use English language names:

- `EN`, `en-US`, `American English` -> `English`
- `ZH`, `Chinese`, `Mandarin` -> `Chinese`
- `ES`, `es` -> `Spanish`

If market is known but language is missing, infer the dominant business language only when low risk, and list the inference in `assumptions`.

## Platforms

Normalize GEO / AI answer platforms:

- `GPT`, `Chat GPT`, `OpenAI` when used as a user-facing answer surface -> `ChatGPT`
- `Google AIO`, `AI Overview`, `SGE` -> `Google AI Overview`
- `Bing Copilot`, `Microsoft Copilot` -> `Microsoft Copilot`
- `Perplexity AI` -> `Perplexity`
- `Gemini AI`, `Google Gemini` -> `Gemini`

Do not convert ad platforms such as Meta, TikTok, or Google Ads into GEO optimization platforms. Put them in `constraints` or `raw_evidence` if they are policy/channel constraints.

## Competitor Names

Normalize obvious casing and punctuation while preserving brand identity:

- `adcreative ai`, `Adcreative.ai` -> `AdCreative.ai`
- `pencil` when used as a brand -> `Pencil`

Do not merge brands unless the source clearly refers to the same company/product.

## Product Or Service Direction

Keep concise noun phrases. Remove generic filler such as "best-in-class", "innovative", or "leading" unless it is part of the actual positioning claim.

Good:

- `AI ad creative generator`
- `ecommerce product photography tool`

Too vague:

- `AI platform`
- `marketing solution`

## Constraints

Group constraints as short, actionable rules. Prefer:

- `Follow brand guidelines`
- `Follow platform ad policies`
- `Avoid unsupported performance claims`

Avoid vague constraints:

- `Make it good`
- `Be professional`

## Confidence

Use final `confidence`:

- `high`: most core fields are confirmed and sources agree.
- `medium`: fields are mostly complete but some are inferred or lightly sourced.
- `low`: critical fields are missing, conflicting, or mostly inferred.
