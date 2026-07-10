# Source Handling

Use this reference when the client provides mixed materials.

## Source Inventory

Create a `source_inventory` entry for every material used:

```json
{
  "source_id": "S01",
  "type": "free_text",
  "name": "client message",
  "usable": true,
  "notes": ""
}
```

Recommended source types:

- `free_text`
- `form`
- `chat_transcript`
- `website`
- `competitor_notes`
- `pdf`
- `pptx`
- `docx`
- `spreadsheet`
- `image_or_screenshot`
- `other`

## Extraction Guidance

### Free Text

Extract explicitly stated fields first. Preserve useful original phrases in `raw_evidence`.

### Forms

Map form labels to the core fields. If form labels are ambiguous, keep the original label in `raw_evidence`.

### Chat Transcripts

Separate client-provided facts from discussion, guesses, or agency suggestions. Prefer the latest explicit client statement when the conversation evolves.

### Websites

Inspect public pages only. For this skill, perform lightweight extraction of brand, homepage domain, product/service direction, visible target persona, and obvious constraints. Do not perform deep website research unless the user explicitly asks; that belongs in a downstream research or prompt-generation skill.

### Competitor Notes

Normalize names and preserve aliases. Do not add competitors that are not present in provided materials unless the user explicitly requests research.

### PDF

Extract text, headings, tables, and title-like content when possible. Pitch decks and product PDFs often contain brand, product direction, target market, personas, and constraints.

### PPTX

Extract slide text and speaker notes when available. Preserve slide numbers or titles in source notes when they support important fields.

### DOC/DOCX

Extract headings, paragraphs, tables, and comments when available. Brand guidelines and project briefs often contain constraints.

### CSV/XLSX

Use table headers and rows to identify competitors, markets, products, personas, and deliverable quantities. Do not flatten tables into vague prose when structured rows are useful evidence.

### Images Or Screenshots

MVP support is limited. Extract only visible text if OCR or image inspection is available. Mark low confidence when the image is hard to read.

## Evidence Rules

- Every confirmed field should cite at least one `source_id`.
- Conflicting values should cite the conflicting source IDs.
- Inferred fields may cite the source that supports the inference, but must also be listed in `assumptions`.
- Missing fields should have no source IDs.
