---
name: geo-monitor-runner
description: Create, import, and validate manual ChatGPT GEO monitoring runs from a market-proxy GEO prompt set. Use when the user has prompt_set.json from geo-intent-prompt-generator and needs an MVP workflow for ChatGPT-only manual_sheet generation, manual response import, raw_responses.jsonl creation, run_manifest.json, validation, and preservation of monitoring_role, prompt_realism_score, demand_weight, buyer_journey_stage, source_basis, and overfit_risk. This skill does not generate prompts, automate browser/API execution, clean responses, analyze brand visibility, create reports, or write optimization content.
---

# GEO Monitor Runner

Run the MVP monitoring handoff from generated prompts to source-preserved raw ChatGPT response data.

## Scope

This MVP supports ChatGPT only and three modes:

- `manual_sheet`: create `run_sheet.csv` and `run_manifest.json` for a human operator to run prompts in ChatGPT.
- `manual_import`: import a completed `run_sheet.csv` into `raw_responses.jsonl` and `run_summary.md`.
- `validation`: validate `raw_responses.jsonl` for schema, duplicates, missing answers, and status issues.

## References

Read the relevant references before producing final output:

- `references/run-modes.md` for mode selection.
- `references/run-sheet-schema.md` before creating or editing run sheets.
- `references/raw-response-schema.md` before importing raw responses.
- `references/run-quality-rules.md` before validation or QA notes.
- `references/output-schema.md` before final outputs.

Use scripts for deterministic file work:

- `scripts/create_run_sheet.py`
- `scripts/import_manual_responses.py`
- `scripts/validate_raw_responses.py`

## Workflow

1. Load inputs.
   - Use `prompt_set.json` from `geo-intent-prompt-generator`.
   - Use `client_intake.json` from `geo-client-intake-normalizer` when available.
   - Use `run_config.json` when provided; otherwise create conservative defaults.

2. Enforce ChatGPT-only MVP scope.
   - Normalize `GPT`, `Chat GPT`, and `OpenAI ChatGPT` to `ChatGPT`.
   - Reject non-ChatGPT monitoring platforms in scripts unless the user explicitly asks to revise the skill.

3. Create a manual run sheet.
   - Flatten prompts into one row per prompt per run iteration.
   - Preserve prompt IDs, topic IDs, persona, market, language, brand type, intent stage, monitoring role, realism score, demand weight, buyer journey, source basis, and overfit risk.
   - Leave `raw_answer` empty and `run_status` as `pending`.

4. Import completed manual results.
   - Read the completed `run_sheet.csv`.
   - Preserve raw answers exactly as supplied.
   - Write one JSON object per response to `raw_responses.jsonl`.
   - Write `run_summary.md` with counts and next-step guidance.

5. Validate raw responses.
   - Check required fields, duplicate response IDs, supported statuses, ChatGPT platform, missing raw answers, and status/notes consistency.

## Script Examples

Create a run sheet:

```bash
skills/geo-monitor-runner/scripts/create_run_sheet.py \
  --prompt-set prompt_set.json \
  --client-intake client_intake.json \
  --output-dir monitor_run
```

Import completed responses:

```bash
skills/geo-monitor-runner/scripts/import_manual_responses.py \
  --run-sheet monitor_run/run_sheet.csv \
  --manifest monitor_run/run_manifest.json \
  --output-dir monitor_run
```

Validate raw responses:

```bash
skills/geo-monitor-runner/scripts/validate_raw_responses.py \
  monitor_run/raw_responses.jsonl
```

## Boundaries

- Do not generate or rewrite prompts.
- Do not run ChatGPT automatically through browser automation or API calls in this MVP.
- Do not summarize, translate, edit, or clean raw ChatGPT answers.
- Do not label brand mentions, rankings, sentiment, competitor share, or recommendation strength.
- Do not create client-facing diagnosis or optimization content.
- Do not merge multiple platforms into this MVP output; only ChatGPT is supported.
