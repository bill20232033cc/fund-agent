# Manual Evidence Intake All-5 Controller Judgment

## Gate Metadata

- Gate: `manual evidence intake gate for all 5 rows`.
- Classification: `standard`.
- Date: 2026-06-09.
- Payload: `docs/reviews/mvp-small-golden-set-manual-evidence-intake-all5-20260609-source-payload.json`.
- Evidence artifact: `docs/reviews/mvp-small-golden-set-manual-evidence-intake-all5-20260609.md`.
- Reviews:
  - `docs/reviews/mvp-small-golden-set-manual-evidence-intake-all5-review-ds-20260609.md`
  - `docs/reviews/mvp-small-golden-set-manual-evidence-intake-all5-review-mimo-20260609.md`

## Judgment

Accepted.

The all-5 manual evidence intake payload is accepted as review-owned docs-only metadata intake under the reconciled source identity policy.

## Accepted Facts

- Rows covered: `004393`, `004194`, `006597`, `110020`, `017641`, all `report_year=2024`.
- EID is recorded as preferred official registry locator where available.
- `official_document_url` may be EID official PDF, CNINFO PDF or fund-company official PDF.
- Each row records official document id, annual-report title, publisher, publication date, fund name, share-class mapping, PDF hash status and identity anchors.
- Search result, fallback, synthetic fixture, LLM summary and historical output are not source truth.
- Each row remains `pending_source_identity_acceptance_decision`.

## Non-Accepted Scope

This judgment does not:

- independently verify URLs or PDF contents;
- read, hash, download or parse PDFs;
- call `FundDocumentRepository`, EID, akshare, network, provider or fallback;
- accept `matched` source identity;
- create retained excerpts;
- accept expected values;
- unlock exact/numeric extractor correctness;
- project fixtures;
- modify extractor, provider/default/runtime/budget/config, quality gate, golden/readiness or release/PR state.

## Validation

- `python -m json.tool docs/reviews/mvp-small-golden-set-manual-evidence-intake-all5-20260609-source-payload.json`: PASS.
- `jq -r '.rows | length, (.[].fund_code)' docs/reviews/mvp-small-golden-set-manual-evidence-intake-all5-20260609-source-payload.json`: row count 5; rows `004393`, `004194`, `006597`, `110020`, `017641`.
- `git diff --check -- docs/reviews/mvp-small-golden-set-manual-evidence-intake-all5-20260609.md docs/reviews/mvp-small-golden-set-manual-evidence-intake-all5-20260609-source-payload.json`: PASS.

## Next Entry

Next gate: `source identity acceptance decision gate`.

The next gate must classify each row as:

- `matched`;
- `matched_without_hash`;
- `needs_manual_hash`;
- `rejected_identity_mismatch`;
- `deferred_insufficient_evidence`.

Matched or matched-without-hash rows may proceed only to retained excerpt fixture work. They still do not unlock exact/numeric correctness without retained row-field excerpts and accepted expected values.
