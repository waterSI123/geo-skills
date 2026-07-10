# Run Sheet Schema

`run_sheet.csv` is the human-run execution sheet. It should be easy to open in a spreadsheet and paste ChatGPT answers into.

## Columns

Required columns:

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
- `model_or_surface`
- `account_context`
- `run_status`
- `raw_answer`
- `answer_url`
- `screenshot_path`
- `operator`
- `run_timestamp`
- `notes`

## Status Values

Allowed `run_status` values:

- `pending`
- `completed`
- `failed`
- `skipped`
- `needs_retry`

## Human Operator Fields

The human operator usually fills:

- `run_status`
- `raw_answer`
- `answer_url`
- `screenshot_path`
- `operator`
- `run_timestamp`
- `notes`

## Rules

- Keep the original prompt unchanged.
- Use `ChatGPT` as the only supported platform.
- Preserve raw ChatGPT answers exactly as copied.
- Use one row per prompt per run iteration.
- If a row fails or is skipped, set `run_status` and add `notes`.
