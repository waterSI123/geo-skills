# Run Quality Rules

Apply these checks before handing data to `geo-conversation-cleaner`.

## Required

- Every record must have `run_id`, `response_id`, `prompt_id`, `prompt`, `platform`, and `run_status`.
- `platform` must be `ChatGPT`.
- `completed` rows must have non-empty `raw_answer`.
- `failed`, `skipped`, and `needs_retry` rows should have `notes`.
- Duplicate `response_id` values are errors.
- Duplicate prompt runs are allowed only when `run_iteration` or `response_id` differs.

## Preserve Raw Evidence

- Do not edit grammar, markdown, citations, or formatting in `raw_answer`.
- Do not remove hallucinations or irrelevant content at this stage.
- Do not add analysis labels such as brand mention or ranking; that belongs downstream.

## Recommended Metadata

- `model_or_surface`: e.g. `ChatGPT default`.
- `account_context`: e.g. `clean account, no custom instructions`.
- `operator`: person who ran the prompt.
- `run_timestamp`: when the response was collected.

## Summary Counts

Report:

- total rows
- completed
- pending
- failed
- skipped
- needs_retry
- empty completed answers
- duplicate response IDs
