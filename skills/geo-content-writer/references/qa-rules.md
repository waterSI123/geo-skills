# QA Rules

Validate content package completeness and safety.

## Required Files

- `content_plan.md`
- `content_package.json`
- `qa_report.json`
- at least one file under `drafts/`

## Package Checks

- Every generated asset has `content_id`, `asset_type`, `title`, `target_topic`, `draft_file`, `recommended_url_slug`, and `status`.
- Draft files referenced in `content_package.json` exist.
- The package includes coverage for priority topics and risk fixes where possible.

## Draft Checks

Each draft should contain:

- client brand
- official website or domain when available
- target topic
- FAQ section
- GEO Optimization Notes section
- frontmatter

## Safety Checks

Warn when:

- proof-oriented assets do not include `[CLIENT EVIDENCE NEEDED]`
- risk-review drafts do not include manual-review language
- competitor context is missing for comparison articles
- no high-priority topic is covered

Fail when:

- required files are missing
- a draft referenced by package metadata is missing
- a draft does not include the client brand
- no drafts are generated
