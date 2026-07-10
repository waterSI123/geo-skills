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
- Use `ChatGPT` only in this MVP.
