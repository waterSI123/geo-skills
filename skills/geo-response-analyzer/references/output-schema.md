# Output Schema

Write all output files to the selected output directory.

## analyzed_responses.jsonl

One JSON object per cleaned response:

```json
{
  "response_id": "R0001",
  "prompt_id": "P001",
  "topic_id": "T01",
  "topic": "AI ad creative generator",
  "persona": "ecommerce marketer",
  "monitoring_role": "market_proxy",
  "prompt_realism_score": 0.9,
  "demand_weight": 1.0,
  "effective_demand_weight": 0.9,
  "buyer_journey_stage": "evaluation",
  "source_basis": ["customer_pain_point"],
  "overfit_risk": "low",
  "platform": "ChatGPT",
  "is_analyzable": true,
  "brands_detected": [
    {
      "brand": "Creatify",
      "role": "competitor",
      "mention_count": 2,
      "first_position": 1,
      "mention_type": "recommended",
      "sentiment": "positive",
      "evidence": "..."
    }
  ],
  "client_brand_mentioned": false,
  "client_brand_position": null,
  "client_brand_mention_type": "not_mentioned",
  "client_brand_sentiment": "not_applicable",
  "recommended_brands_order": ["Creatify", "Pencil"],
  "content_gap_signals": [],
  "risk_signals": [],
  "analysis_method": "rule_based_v1"
}
```

## visibility_analysis.json

```json
{
  "analysis_method": "rule_based_v1",
  "scope": {
    "platform": "ChatGPT",
    "analyzable_response_count": 0,
    "brand_mentioning_response_count": 0,
    "market_proxy_response_count": 0,
    "market_proxy_brand_mentioning_response_count": 0,
    "monitoring_role_breakdown": {},
    "tracked_brands": []
  },
  "client_brand": "CreativeHit",
  "primary_kpis": {
    "primary_scope": "market_proxy_and_buyer_evaluation",
    "market_visibility_score": 0.0,
    "market_visibility_rank": 1,
    "weighted_market_visibility_score": 0.0,
    "weighted_market_visibility_rank": 1,
    "market_share_of_voice": 0.0,
    "market_share_of_voice_rank": 1,
    "market_average_position": null,
    "market_average_position_rank": null,
    "qualified_recommendation_rate": 0.0,
    "qualified_recommendation_rank": 1
  },
  "brand_metrics": [
    {
      "brand": "CreativeHit",
      "role": "client",
      "responses_mentioned": 0,
      "visibility_score": 0.0,
      "visibility_rank": 1,
      "weighted_visibility_score": 0.0,
      "weighted_visibility_rank": 1,
      "mention_occurrences": 0,
      "share_of_voice": 0.0,
      "share_of_voice_rank": 1,
      "weighted_share_of_voice": 0.0,
      "weighted_share_of_voice_rank": 1,
      "average_position": null,
      "average_position_rank": null,
      "weighted_average_position": null,
      "weighted_average_position_rank": null,
      "top_3_rate": 0.0,
      "sentiment_score": null,
      "sentiment_rank": null,
      "qualified_recommendation_rate": 0.0,
      "qualified_recommendation_rank": 1
    }
  ],
  "market_proxy_metrics": [],
  "rankings": {}
}
```

## topic_analysis.json

```json
{
  "analysis_method": "rule_based_v1",
  "topics": [
    {
      "topic_id": "T01",
      "topic": "AI ad creative generator",
      "response_count": 0,
      "brand_mentioning_response_count": 0,
      "market_response_count": 0,
      "market_brand_mentioning_response_count": 0,
      "client_visibility_score": 0.0,
      "market_client_visibility_score": 0.0,
      "market_weighted_visibility_score": 0.0,
      "client_share_of_voice": 0.0,
      "client_average_position": null,
      "client_sentiment_score": null,
      "market_qualified_recommendation_rate": 0.0,
      "client_absent_rate": 0.0,
      "weak_recommendation_rate": 0.0,
      "strong_competitors": [],
      "content_gap_counts": {},
      "risk_signal_counts": {},
      "topic_opportunity_level": "low"
    }
  ]
}
```

## opportunity_findings.json

```json
{
  "analysis_method": "rule_based_v1",
  "summary_counts": {
    "content_gap_signals": {},
    "risk_signals": {}
  },
  "findings": [
    {
      "finding_id": "F001",
      "type": "competitor_recommended_client_absent",
      "category": "content_gap",
      "severity": "high",
      "topic_id": "T01",
      "topic": "AI ad creative generator",
      "response_count": 3,
      "evidence_response_ids": ["R0001"],
      "recommended_next_step": "Create content that positions the client brand for this topic."
    }
  ]
}
```

## analysis_summary.md

Human-readable compact summary for operators. This is not the final client report.
