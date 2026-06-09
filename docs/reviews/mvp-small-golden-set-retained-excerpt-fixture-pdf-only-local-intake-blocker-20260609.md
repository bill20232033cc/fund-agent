# Retained Excerpt Fixture Gate - PDF-only Local Intake Blocker

## Gate Metadata

- Gate: `retained excerpt fixture gate for accepted rows only`.
- Classification: `heavy`.
- Date: 2026-06-09.
- Authorization: user authorized PDF-only local intake from `/Users/maomao/Downloads/基金年报/`.
- Accepted source identity decision checkpoint: `866a12b`.

## Authorized Scope

Only the following actions are authorized for this gate:

- Read local annual-report PDF files placed under `/Users/maomao/Downloads/基金年报/`.
- Compute each local PDF sha256.
- Extract minimal same-source retained excerpts for accepted rows.
- Record page or section anchors, short excerpts, and field-level expected values needed for later row-field extractor correctness tests.

## Explicit Non-Scope

- No network access.
- No `FundDocumentRepository` live acquisition.
- No fallback invocation.
- No extractor modification.
- No provider/default/runtime/budget/config change.
- No fixture projection beyond a separately accepted retained excerpt fixture artifact.
- No exact/numeric correctness acceptance.
- No golden/readiness promotion.
- No Chapter calibration, Agent runtime expansion, multi-year runtime, score-loop, PR/release/merge/mark-ready.

## Local Directory Check

Command result:

```text
ls -la /Users/maomao/Downloads/基金年报
total 0
drwxr-xr-x   2 maomao  staff    64 May 19 13:33 .
drwx------@ 39 maomao  staff  1248 Jun  9 11:38 ..
```

No PDF files were found under `/Users/maomao/Downloads/基金年报/`.

## Parser Availability Check

- `pdftotext`: not available.
- `pdfinfo`: not available.
- Python environment via `uv run python`: `pdfplumber` is available.

## Blocker

The gate is blocked until the five local annual-report PDFs are placed under `/Users/maomao/Downloads/基金年报/`.

Required rows:

- `004393 / 2024`
- `004194 / 2024`
- `006597 / 2024`
- `110020 / 2024`
- `017641 / 2024`

## Acceptance Status

Not accepted.

No PDF was read, no sha256 was computed for the five reports, no excerpt was extracted, no expected value was recorded, and exact/numeric correctness remains blocked.

## Resume Instruction

After the five PDFs are present, resume this same gate by:

1. Mapping each local PDF to one accepted source identity row.
2. Computing sha256 for each mapped PDF.
3. Extracting only minimal retained excerpts for identity, benchmark, manager, fee, scale, return, holdings, and risk fields as applicable.
4. Recording excerpts and expected values in a review-owned artifact.
5. Running two independent reviews before controller judgment.
