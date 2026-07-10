# Run Modes

This MVP supports ChatGPT only.

## manual_sheet

Use when the user has a prompt set and needs a CSV for a human operator to run prompts in ChatGPT.

Inputs:

- `prompt_set.json` required.
- `client_intake.json` optional.
- `run_config.json` optional.

Outputs:

- `run_sheet.csv`
- `run_manifest.json`

## manual_import

Use when the user has a completed `run_sheet.csv` with manually pasted ChatGPT answers.

Inputs:

- `run_sheet.csv` required.
- `run_manifest.json` optional but recommended.

Outputs:

- `raw_responses.jsonl`
- `run_summary.md`

## validation

Use when the user has `raw_responses.jsonl` and needs schema and quality checks.

Inputs:

- `raw_responses.jsonl` required.
- `run_manifest.json` optional.

Output:

- JSON validation report.

## Non-MVP Modes

Do not implement these in this skill yet:

- Browser-assisted ChatGPT execution.
- API execution.
- Perplexity, Gemini, Google AI Overview, or Microsoft Copilot runs.
- Screenshot capture automation.
