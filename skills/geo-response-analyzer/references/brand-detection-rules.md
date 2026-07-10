# Brand Detection Rules

Use deterministic text rules for MVP analysis.

## Mention Detection

Detect mentions with case-insensitive matching against:

- Exact brand name.
- Dotless/base variant for domain-like names, such as `AdCreative` for `AdCreative.ai`.
- Compact and spaced variants when practical, such as `CreativeHit` and `Creative Hit`.

Use boundaries so `Pencil` does not match unrelated longer words.

## Position Detection

For each response:

1. Find tracked brand mentions.
2. If brands appear in numbered or bulleted lines, order brands by those list lines.
3. Otherwise order brands by first character occurrence in the answer.
4. Assign positions starting at 1.

`recommended_brands_order` should preserve this inferred order.

## Mention Type

Allowed values:

- `recommended`
- `listed`
- `compared`
- `mentioned`
- `negative`
- `not_mentioned`

Recommendation keywords include:

```text
recommend
recommended
best
top
good option
great option
suitable
ideal
strong choice
worth considering
well suited
```

Comparison keywords include:

```text
vs
versus
compared with
compared to
alternative to
better than
instead of
similar to
```

Negative keywords include:

```text
not recommended
less suitable
limited
lacks
weak
unknown
not enough information
hard to verify
unclear
```

If both positive and negative cues exist for a brand, prefer `negative` only when the negative cue appears near the brand. Otherwise classify by the strongest nearby cue.

## Sentiment

Allowed values:

- `positive`
- `neutral`
- `negative`
- `mixed`
- `uncertain`
- `not_applicable`

Use context around each brand mention. Do not score absent brands.

Positive cues:

```text
recommended
best
strong
strong choice
ideal
good option
well suited
popular
robust
useful
effective
```

Negative or uncertainty cues:

```text
not recommended
less suitable
limited
lacks
not enough information
unknown
unclear
hard to verify
cannot confirm
not widely documented
```

Use `mixed` when clear positive and negative cues both appear near the same brand. Use `uncertain` when the answer mainly says information is missing or cannot be verified.
