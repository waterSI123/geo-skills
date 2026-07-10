# Narrative Rules

Use consultative client-facing language.

## Style

- Lead with conclusion, then evidence.
- Use plain business language instead of internal field names.
- Explain what each metric means for the client.
- Prefer concise bullets and tables.
- Avoid exaggerated certainty.

## Required Framing

Use sample-aware phrasing:

```text
In market-proxy prompts...
In this market-proxy monitoring sample...
ChatGPT responses showed...
Among tracked brands...
```

Avoid absolute phrasing:

```text
ChatGPT always thinks...
The market believes...
AI has decided...
```

## Metric Interpretation

Visibility score:

- High: client is consistently surfaced when brands are mentioned.
- Medium: client appears, but not reliably.
- Low: client is frequently absent from brand recommendations.

Weighted market visibility:

- Higher weighted visibility means the client appears in prompts with stronger realism and demand weight.
- Low weighted visibility is more important than a cosmetic gain in diagnostic prompts.

Share of voice:

- High share means the client takes a larger portion of tracked brand mentions.
- Low share means competitors dominate the answer space.

Average position:

- Lower is better.
- A good average position with low visibility means the client performs well when mentioned but appears too rarely.

Sentiment score:

- Positive sentiment means responses frame the brand favorably.
- Neutral or negative sentiment means content should add evidence, positioning clarity, or corrective signals.

## Evidence Handling

- Use evidence response IDs when available.
- Do not quote long answer text in the MVP report.
- Keep raw evidence traceable through upstream files.

## Risk Language

For review-required risks, use:

```text
This should be manually reviewed before being treated as a confirmed error.
```
