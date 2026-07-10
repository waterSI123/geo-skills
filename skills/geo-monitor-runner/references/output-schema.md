# Output Schema

## run_config.json

Optional input:

```json
{
  "run_id": "",
  "platform": "ChatGPT",
  "market": "United States",
  "language": "English",
  "run_mode": "manual_sheet",
  "model_or_surface": "ChatGPT default",
  "account_context": "clean account, no custom instructions",
  "runs_per_prompt": 1,
  "operator": "",
  "notes": ""
}
```

## run_manifest.json

Created by `create_run_sheet.py`:

```json
{
  "run_id": "",
  "created_at": "",
  "client": {
    "brand_name": "",
    "website_domain": ""
  },
  "platform": "ChatGPT",
  "market": "",
  "language": "",
  "run_mode": "manual_sheet",
  "runs_per_prompt": 1,
  "prompt_count": 0,
  "expected_response_count": 0,
  "model_or_surface": "ChatGPT default",
  "account_context": "",
  "operator": "",
  "input_files": [],
  "output_files": [],
  "quality_rules": []
}
```

## run_summary.md

Created by `import_manual_responses.py`:

```markdown
# GEO Monitor Run Summary

Run ID:
Platform:
Rows:
Completed:
Failed:
Skipped:
Needs Retry:
Pending:

## Output Files

## Warnings

## Recommended Next Step
Use `geo-conversation-cleaner`.
```
