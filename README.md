# GEO Intent Prompt Generator

Codex skill for generating MVP GEO / AI Visibility intent prompt sets.

## What It Does

This skill turns customer business inputs into:

- website research brief when a domain is provided
- monitoring topics
- realistic AI-user prompts grouped by topic
- QA and distribution report

It is designed for MVP prompt generation, not keyword difficulty scoring, competition scoring, pricing, or content writing.

## Install In Codex

Copy this folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R geo-intent-prompt-generator ~/.codex/skills/
```

Then restart Codex or force reload skills.

## Use

```text
$geo-intent-prompt-generator

Services: AI ad creative generator
Personas: ecommerce marketer, performance marketing manager, DTC founder
Target Market: US
Language: English
Platform: ChatGPT
Website Domain: https://example.com
Additional Context: Generate ad creatives that follow brand guidelines and platform policies.
Competitors: Creatify, Pencil, AdCreative.ai
Generate 8 topics and 40 prompts.
```

## Files

- `SKILL.md`: main skill workflow
- `agents/openai.yaml`: Codex UI metadata
- `references/`: prompt generation rules, website research, output schema, QA rubric
- `scripts/`: prompt deduplication and output validation helpers
