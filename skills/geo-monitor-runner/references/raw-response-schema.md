# Raw Response Schema

`raw_responses.jsonl` contains one JSON object per run-sheet row.

## Record

```json
{
  "run_id": "",
  "response_id": "",
  "row_id": "",
  "run_iteration": 1,
  "topic_id": "",
  "topic": "",
  "prompt_id": "",
  "prompt": "",
  "platform": "ChatGPT",
  "market": "",
  "language": "",
  "persona": "",
  "brand_type": "",
  "intent_stage": "",
  "monitoring_role": "market_proxy",
  "prompt_realism_score": 0.9,
  "demand_weight": 1.0,
  "buyer_journey_stage": "evaluation",
  "source_basis": ["customer_pain_point"],
  "overfit_risk": "low",
  "run_mode": "manual_import",
  "run_status": "completed",
  "raw_answer": "",
  "answer_url": "",
  "screenshot_path": "",
  "model_or_surface": "ChatGPT default",
  "account_context": "",
  "operator": "",
  "run_timestamp": "",
  "source_row": 1,
  "notes": ""
}
```

## Rules

- Preserve `raw_answer` exactly; do not clean, summarize, translate, or rewrite.
- Include failed and skipped rows so downstream QA can see coverage gaps.
- Use unique `response_id` values within a file.
- Keep prompt metadata attached to every record.
- Keep market-proxy metadata attached to every record so primary KPI calculations can exclude or down-weight diagnostic prompts.
- Use `ChatGPT` only in this MVP.
