---
name: geo-response-analyzer
description: Analyze cleaned ChatGPT GEO monitoring responses into structured brand visibility, share of voice, average rank, sentiment, topic-level opportunities, content gap signals, and risk signals. Use when the user has cleaned_responses.jsonl from geo-conversation-cleaner plus client_intake.json and prompt_set.json, and needs MVP rule-based GEO response analysis before report generation or content writing. This skill does not collect responses, clean raw answers, generate prompts, write client reports, or create optimization content.
---

# GEO Response Analyzer

Convert cleaned ChatGPT monitoring answers into structured GEO visibility diagnostics for downstream reporting and content generation.

## Scope

This MVP analyzes ChatGPT-only cleaned responses and produces:

- Overall brand metrics for the client and tracked competitors.
- Rankings for visibility score, share of voice, average position, and sentiment score.
- Topic-level analysis for client absence, strong competitors, and weak recommendation signals.
- Rule-based content gap and risk signals.
- Machine-readable JSON/JSONL outputs plus a compact Markdown summary.

## References

Read the relevant references before producing final output:

- `references/input-schema.md` before loading client, prompt, or cleaned response files.
- `references/metrics-definitions.md` before calculating visibility, share of voice, average rank, or sentiment.
- `references/brand-detection-rules.md` before detecting brand mentions, positions, mention type, or sentiment.
- `references/topic-analysis-rules.md` before aggregating by topic.
- `references/gap-and-risk-rules.md` before assigning content gap or risk signals.
- `references/output-schema.md` before writing final outputs.

Use scripts for deterministic file work:

- `scripts/analyze_cleaned_responses.py`
- `scripts/validate_analysis.py`

## Workflow

1. Load inputs.
   - Use `client_intake.json` from `geo-client-intake-normalizer`.
   - Use `prompt_set.json` from `geo-intent-prompt-generator`.
   - Use `cleaned_responses.jsonl` from `geo-conversation-cleaner`.
   - Analyze only records where `is_analyzable` is true.

2. Build the tracked brand set.
   - Treat the client brand as the primary brand.
   - Treat `competitor_names` as tracked competitors.
   - Use website domain only as supporting context for wrong-website checks.

3. Analyze each response.
   - Detect client and competitor mentions.
   - Count mention occurrences.
   - Estimate brand position from list order or first textual occurrence.
   - Classify mention type as `recommended`, `listed`, `compared`, `mentioned`, `negative`, or `not_mentioned`.
   - Assign rule-based sentiment.
   - Emit content gap and risk signals with evidence snippets.

4. Aggregate overall metrics.
   - Calculate visibility score, share of voice, average position, top-3 rate, and sentiment score.
   - Rank the client brand against tracked competitors for each metric.

5. Aggregate topic metrics.
   - Identify topics where the client brand is often absent.
   - Identify topics where competitors are stronger.
   - Identify topics where the client brand appears with weak recommendation language.

6. Output and validate.
   - Write `analyzed_responses.jsonl`.
   - Write `visibility_analysis.json`.
   - Write `topic_analysis.json`.
   - Write `opportunity_findings.json`.
   - Write `analysis_summary.md`.
   - Run `validate_analysis.py` after analysis files are produced.

## Script Examples

Analyze cleaned responses:

```bash
skills/geo-response-analyzer/scripts/analyze_cleaned_responses.py \
  --client-intake client_intake.json \
  --prompt-set prompt_set.json \
  --cleaned-responses cleaned_run/cleaned_responses.jsonl \
  --output-dir analysis_run
```

Validate analysis output:

```bash
skills/geo-response-analyzer/scripts/validate_analysis.py \
  --analysis-dir analysis_run
```

## Boundaries

- Do not generate or rewrite prompts.
- Do not run ChatGPT or collect monitoring data.
- Do not clean raw answers or alter evidence text.
- Do not write the final client report.
- Do not generate optimization articles, landing pages, or briefs.
- Do not make definitive claims about wrong category or wrong features when rule confidence is low; mark these as review-required risk signals.
- Do not call an LLM in the MVP script path; use deterministic rule-based analysis.
