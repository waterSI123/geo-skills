# Cleaned Response Schema

`cleaned_responses.jsonl` contains one JSON object per raw response.

## Record

```json
{
  "run_id": "",
  "response_id": "",
  "prompt_id": "",
  "topic_id": "",
  "topic": "",
  "prompt": "",
  "platform": "ChatGPT",
  "market": "",
  "language": "",
  "persona": "",
  "brand_type": "",
  "intent_stage": "",
  "run_status": "completed",
  "raw_answer": "",
  "clean_answer": "",
  "answer_text_hash": "",
  "answer_length_chars": 0,
  "answer_length_words": 0,
  "is_analyzable": true,
  "answer_quality_status": "analyzable",
  "quality_flags": [],
  "duplicate_group_id": "",
  "is_duplicate_answer": false,
  "model_or_surface": "",
  "account_context": "",
  "operator": "",
  "run_timestamp": "",
  "source_row": 1,
  "notes": "",
  "cleaning_notes": []
}
```

## Rules

- Preserve `raw_answer`.
- Put cleaned text in `clean_answer`.
- Do not add brand-visibility analysis fields.
- Keep one cleaned record for every raw record.
- Use `is_analyzable` to decide downstream inclusion.
