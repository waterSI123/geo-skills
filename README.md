# GEO Skills

Codex skill collection for GEO / AI Visibility workflows.

This repository is intended to hold multiple related GEO skills. Each skill lives in
`skills/<skill-name>/` as a standalone Codex skill folder with its own `SKILL.md`,
optional `agents/`, `references/`, `scripts/`, and `assets/` directories.

## Skills

| Skill | Status | Description |
| --- | --- | --- |
| `geo-client-intake-normalizer` | Ready | Extract and normalize messy client materials into standardized GEO project intake fields for downstream skills. |
| `geo-conversation-cleaner` | Ready | Clean raw ChatGPT GEO monitoring responses into analyzable datasets and QA reports. |
| `geo-intent-prompt-generator` | Ready | Generate GEO / AI Visibility commercial-search topics and realistic AI monitoring prompts from services, personas, market, language, platform, competitors, and optional website research. |
| `geo-monitor-runner` | Ready | Create manual ChatGPT run sheets, import completed answers, and validate raw GEO monitoring data. |
| `geo-report-builder` | Ready | Build client-facing GEO diagnostic reports and content-writer briefs from structured analysis outputs. |
| `geo-response-analyzer` | Ready | Analyze cleaned ChatGPT responses into brand visibility, share of voice, average rank, sentiment, topic opportunities, content gaps, and risk signals. |

Planned examples:

- `geo-article-writer`: Generate GEO-focused articles from confirmed topics, prompts, brand context, and market constraints.
- `geo-content-brief-generator`: Generate article or landing-page briefs for GEO visibility workflows.

## Repository Layout

```text
geo-skills/
├── README.md
├── scripts/
│   └── install-skill.sh
└── skills/
    ├── geo-client-intake-normalizer/
    ├── geo-conversation-cleaner/
    ├── geo-monitor-runner/
    ├── geo-report-builder/
    ├── geo-response-analyzer/
    └── geo-intent-prompt-generator/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        ├── references/
        └── scripts/
```

## Install In Codex

Install all skills:

```bash
./scripts/install-skill.sh
```

Install one skill:

```bash
./scripts/install-skill.sh geo-client-intake-normalizer
```

By default, the script installs into `${CODEX_HOME:-$HOME/.codex}/skills`.
Set `CODEX_SKILLS_DIR` to override the target directory.

## Use

```text
$geo-intent-prompt-generator

Services: AI ad creative generator
Personas: ecommerce marketer, performance marketing manager, DTC founder
Target Market: US
Language: English
Platform: ChatGPT
Additional Context: Generate ad creatives that follow brand guidelines and platform policies.
Competitors: Creatify, Pencil, AdCreative.ai
Website Domain: https://example.com
Generate 8 topics and 40 prompts.
```

## Adding A Skill

Create each new skill as a sibling under `skills/`:

```text
skills/<new-skill-name>/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── scripts/
```

Keep each skill self-contained. Put shared repository tooling in root-level
`scripts/`, and put skill-specific references or helpers inside that skill folder.
