---
name: geo-conversation-cleaner
description: Clean and QA raw ChatGPT GEO monitoring responses into analyzable datasets while preserving market-proxy prompt metadata. Use when the user has raw_responses.jsonl from geo-monitor-runner and needs cleaned_responses.jsonl, cleaning_report.json, cleaning_report.md, basic text normalization, quality flags, exact duplicate detection, validation, and preservation of monitoring_role, prompt_realism_score, demand_weight, buyer_journey_stage, source_basis, and overfit_risk before geo-response-analyzer. This MVP supports ChatGPT raw responses only and does not analyze brand mentions, rankings, competitor visibility, sentiment, recommendations, reports, or content writing.
---

# GEO Conversation Cleaner

Convert raw ChatGPT monitoring evidence into a stable cleaned dataset for downstream GEO response analysis.

## Scope

This MVP supports ChatGPT-only raw response cleaning:

- Read `raw_responses.jsonl` from `geo-monitor-runner`.
- Preserve every `raw_answer` exactly.
- Create `clean_answer` for analysis use.
- Add quality status, quality flags, length metrics, hashes, and exact duplicate markers.
- Output `cleaned_responses.jsonl`, `cleaning_report.json`, and `cleaning_report.md`.

## References

Read the relevant references before producing final output:

- `references/input-schema.md` for expected raw response inputs.
- `references/text-cleaning-rules.md` before changing any answer text.
- `references/quality-rules.md` before assigning status, flags, or analyzability.
- `references/cleaned-response-schema.md` before writing cleaned JSONL.
- `references/output-schema.md` before final outputs.

Use scripts for deterministic file work:

- `scripts/clean_raw_responses.py`
- `scripts/validate_cleaned_responses.py`

## Workflow

1. Load inputs.
   - Use `raw_responses.jsonl` from `geo-monitor-runner`.
   - Use `run_manifest.json` and `client_intake.json` only as optional context.

2. Preserve raw evidence.
   - Never overwrite, summarize, translate, or rewrite `raw_answer`.
   - Store cleaned text separately as `clean_answer`.

3. Normalize metadata.
   - Normalize ChatGPT aliases to `ChatGPT`.
   - Mark non-ChatGPT rows as `unsupported_platform`.
   - Fill missing optional fields with empty values.

4. Clean answer text.
   - Remove invisible copy artifacts.
   - Normalize line endings and excessive blank lines.
   - Preserve markdown, URLs, citations, lists, and original wording.

5. Assign quality status and flags.
   - Mark empty, failed, skipped, retry, non-answer, refusal, too-short, duplicate, and unsupported rows.
   - Set `is_analyzable` true only for normal analyzable responses.

6. Detect exact duplicates.
   - Use normalized `clean_answer` hashes.
   - Keep the first analyzable copy as analyzable.
   - Mark later exact duplicates as `duplicate_answer`.

7. Output and validate.
   - Write `cleaned_responses.jsonl`.
   - Write JSON and Markdown cleaning reports.
   - Run `validate_cleaned_responses.py` when a cleaned file exists.

## Script Examples

Clean raw responses:

```bash
skills/geo-conversation-cleaner/scripts/clean_raw_responses.py \
  --raw-responses monitor_run/raw_responses.jsonl \
  --manifest monitor_run/run_manifest.json \
  --output-dir cleaned_run
```

Validate cleaned responses:

```bash
skills/geo-conversation-cleaner/scripts/validate_cleaned_responses.py \
  cleaned_run/cleaned_responses.jsonl
```

## Boundaries

- Do not determine whether the client's brand was mentioned.
- Do not rank brands or competitors.
- Do not perform sentiment, recommendation strength, or share-of-voice analysis.
- Do not remove or alter raw evidence.
- Do not generate client reports, recommendations, content briefs, or articles.
- Do not support non-ChatGPT platforms in this MVP.
