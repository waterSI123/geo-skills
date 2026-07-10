# Topic Analysis Rules

Group responses by topic using this priority:

1. `topic_id` and `topic` from `prompt_set.json`.
2. `topic_id` and `topic` from the cleaned response record.
3. `prompt_id` as a fallback topic key.

## Topic Metrics

For each topic, calculate:

- `response_count`
- `brand_mentioning_response_count`
- `client_visibility_score`
- `client_share_of_voice`
- `client_average_position`
- `client_sentiment_score`
- `client_absent_rate`
- `weak_recommendation_rate`
- `strong_competitors`
- `content_gap_counts`
- `risk_signal_counts`

## Client Absent Rate

Definition:

```text
brand-mentioning topic responses where client brand is absent / brand-mentioning topic responses
```

If no tracked brand appears in the topic, use all analyzable topic responses as the denominator and treat the client as absent.

## Weak Recommendation Rate

Definition:

```text
client-mentioned topic responses where client mention_type is not recommended or sentiment is not positive / client-mentioned topic responses
```

If the client is never mentioned in a topic, set this to `0` and let `client_absent_rate` carry the opportunity signal.

## Strong Competitors

A competitor is strong in a topic when at least one is true:

- Competitor visibility is higher than client visibility.
- Competitor share of voice is higher than client share of voice.
- Competitor average position is better than client average position.
- Competitor receives positive sentiment while the client is absent or neutral/negative.

## Topic Opportunity Level

Use:

- `high`: client absent rate is at least 60% and at least one competitor is strong, or high-severity risk signals appear.
- `medium`: client absent rate is at least 30%, weak recommendation rate is at least 50%, or repeated content gaps appear.
- `low`: client is visible and no repeated weak/gap/risk pattern appears.

These levels are triage signals for reporting and content writing, not final strategic judgment.
