# Output Schema

## cleaned_responses.jsonl

One cleaned response object per line. See `cleaned-response-schema.md`.

## cleaning_report.json

```json
{
  "input_file": "",
  "output_file": "",
  "generated_at": "",
  "counts": {
    "records": 0,
    "analyzable": 0,
    "not_analyzable": 0
  },
  "quality_status_counts": {},
  "quality_flag_counts": {},
  "duplicate_groups": 0,
  "warnings": [],
  "recommended_next_skill": "geo-response-analyzer"
}
```

## cleaning_report.md

```markdown
# GEO Conversation Cleaning Report

Input:
Output:

## Counts

## Quality Status

## Quality Flags

## Warnings

## Recommended Next Step
Use `geo-response-analyzer`.
```
