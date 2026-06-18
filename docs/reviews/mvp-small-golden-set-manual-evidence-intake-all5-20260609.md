# MVP Small Golden Set Manual Evidence Intake - All 5 Rows

## Gate Metadata

- Gate: `manual evidence intake gate for all 5 rows`.
- Classification: `standard`.
- Date: 2026-06-09.
- Scope: docs-only manual metadata intake.
- Payload: `docs/reviews/mvp-small-golden-set-manual-evidence-intake-all5-20260609-source-payload.json`.

## Current Facts

- Control truth reconciliation checkpoint `15d5675` accepts the updated source identity route.
- EID is a preferred official registry locator, not a mandatory automatic extraction source or exclusive source truth.
- `official_document_url` may come from EID, fund-company official website/CDN PDF, CNINFO PDF or another official/first-party disclosure platform.
- Exact/numeric extractor correctness remains blocked.
- No retained field excerpts, expected values, row-field unlocks or fixture projection are accepted by this gate.

## Intake Scope

This gate records user-provided metadata for:

| fund_code | report_year | official_document_url origin | hash status |
|---|---:|---|---|
| `004393` | 2024 | EID official PDF | `user_provided` |
| `004194` | 2024 | EID official PDF | `not_provided` |
| `006597` | 2024 | CNINFO PDF | `not_provided` |
| `110020` | 2024 | Fund-company official PDF | `not_provided` |
| `017641` | 2024 | Fund-company official PDF | `not_provided` |

Each row records:

- `fund_code`, `report_year`, `document_kind`;
- official registry locator, with EID captured where available;
- `official_document_url`;
- `official_document_id`;
- `source_document_title`;
- `source_publisher`;
- `publication_date`;
- `fund_name`;
- share-class target code and other share classes;
- `user_provided_pdf_sha256` or `not_provided`;
- identity anchors for annual-report title, publisher and PDF §2/profile fund-code/name/share-class mapping.

## Source Truth Boundary

- Search results are locator evidence only.
- EID search/detail is preferred registry locator evidence, not document source truth by itself.
- Fund-company official PDF and CNINFO PDF URLs may be recorded as `official_document_url` under the accepted control policy.
- LLM summaries, generated reports, synthetic fixtures, fallback traces and unproven historical outputs are not source truth.
- The payload does not claim source identity final acceptance; each row remains `pending_source_identity_acceptance_decision`.

## No-Live / No-Source-Acquisition Statement

This gate did not:

- download, open, read, OCR or hash PDFs;
- call `FundDocumentRepository`;
- use network, EID live access, akshare, curl, DNS, socket, endpoint/provider probe or fallback;
- modify extractors, tests, fixtures, provider/default/runtime/budget/config, quality gate, golden/readiness or PR/release state;
- use unrelated untracked workspace residue as source truth.

## Validation Matrix

| Check | Evidence | Expected |
|---|---|---|
| Branch check | `git branch --show-current` | `feat/mvp-llm-incomplete-run-artifacts` |
| Dirty scope check | `git status --short` | Only gate-owned docs/reviews files staged for this gate; unrelated untracked residue untouched |
| JSON parse | `python -m json.tool docs/reviews/mvp-small-golden-set-manual-evidence-intake-all5-20260609-source-payload.json` | PASS |
| Row count | payload `rows` | Exactly 5 rows |
| Required fields | payload row keys | All required intake fields present |
| Formatting | `git diff --check -- <gate files>` | PASS |

## Residuals

- `004194`, `006597`, `110020` and `017641` have `pdf_hash_status=not_provided`; the source identity acceptance decision gate may classify them as `matched_without_hash` or `needs_manual_hash`.
- The payload records user-provided profile anchors, but this gate does not independently verify PDF contents.
- Exact/numeric correctness remains blocked until source identity acceptance plus retained row-field excerpts and expected values are accepted.

## Next Entry

Next gate: `source identity acceptance decision gate`.

The next gate must decide each row as one of:

- `matched`;
- `matched_without_hash`;
- `needs_manual_hash`;
- `rejected_identity_mismatch`;
- `deferred_insufficient_evidence`.

Matched rows may proceed only to retained excerpt fixture work. They do not directly unlock exact/numeric extractor correctness.
