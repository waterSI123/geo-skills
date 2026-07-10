# Text Cleaning Rules

Create `clean_answer` from `raw_answer` without changing meaning.

## Allowed

- Normalize CRLF and CR line endings to LF.
- Remove zero-width and invisible copy artifacts.
- Trim leading and trailing whitespace.
- Trim trailing whitespace on each line.
- Collapse three or more blank lines into two blank lines.
- Normalize non-breaking spaces to regular spaces.

## Not Allowed

- Do not summarize.
- Do not translate.
- Do not rewrite grammar.
- Do not remove markdown, lists, tables, URLs, citations, or code blocks.
- Do not remove hallucinations or incorrect claims.
- Do not add brand labels, rankings, or analysis fields.

## Hashing

Compute `answer_text_hash` from `clean_answer` after text cleaning. Use SHA-256 hex. Empty answers should use an empty hash.
