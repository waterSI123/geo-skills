# Input Schema

The primary input is `raw_responses.jsonl` from `geo-monitor-runner`.

## Raw Response Fields

Expected fields:

- `run_id`
- `response_id`
- `row_id`
- `run_iteration`
- `topic_id`
- `topic`
- `prompt_id`
- `prompt`
- `platform`
- `market`
- `language`
- `persona`
- `brand_type`
- `intent_stage`
- `run_mode`
- `run_status`
- `raw_answer`
- `answer_url`
- `screenshot_path`
- `model_or_surface`
- `account_context`
- `operator`
- `run_timestamp`
- `source_row`
- `notes`

Missing optional fields should be filled with empty strings. Missing critical fields should be flagged in validation, not guessed.

## Optional Inputs

`run_manifest.json` may provide run-level context such as platform, market, language, expected response count, and model/surface.

`client_intake.json` may provide brand and market context, but this skill should not perform brand visibility analysis.
