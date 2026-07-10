# Metrics Definitions

All MVP metrics are calculated over analyzable ChatGPT responses only.

## Tracked Brands

Tracked brands are:

```text
client brand + competitor_names
```

The MVP should not infer additional brands from the answer text.

## Brand-Mentioning Responses

A brand-mentioning response is an analyzable response that mentions at least one tracked brand.

This denominator is used for visibility score and share of voice.

## Visibility Score

Definition:

```text
responses where brand appears / responses mentioning any tracked brand
```

Example: 100 responses mention at least one tracked brand. The client brand appears in 50 of them. Visibility score is `50%`.

Rank brands by visibility score descending.

## Share Of Voice

Definition:

```text
brand mention occurrences / all tracked brand mention occurrences
```

Example: tracked brands are mentioned 500 total times. The client brand is mentioned 50 times. Share of voice is `10%`.

Rank brands by share of voice descending.

## Average Position

Definition:

```text
average brand appearance rank in responses where that brand appears
```

Position rules:

1. Prefer obvious ordered or bulleted list order.
2. If no list order is available, use first textual occurrence order.
3. Do not include absent responses in the average.
4. Lower average position is better.

Also calculate:

```text
top_3_rate = responses where brand appears in positions 1-3 / responses mentioning any tracked brand
```

Rank brands by average position ascending. Brands without a position should have no position rank.

## Sentiment Score

Use rule-based sentiment labels:

- `positive` = `+1`
- `neutral` = `0`
- `uncertain` = `0`
- `mixed` = `0`
- `negative` = `-1`
- `not_applicable` = excluded from average

Definition:

```text
average sentiment value across responses where the brand appears
```

Rank brands by sentiment score descending. Brands without mentions should have no sentiment rank.

## Client-Versus-Competitor Rank

Every ranking must include the client brand and all tracked competitors:

- `visibility_rank`
- `share_of_voice_rank`
- `average_position_rank`
- `sentiment_rank`

Use stable tie handling: brands with the same metric value receive the same rank, and the next rank skips by the number of tied brands.
