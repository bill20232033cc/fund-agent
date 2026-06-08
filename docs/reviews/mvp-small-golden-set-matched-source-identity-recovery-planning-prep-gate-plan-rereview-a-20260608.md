# Plan Re-Review A: Matched Source Identity Recovery Planning/Prep Gate

## Findings

### High - Manual local PDF path can still enter matched identity state

- Location: `docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-20260608.md:130`, `:153`, `:183-188`.
- Prior finding status: partially resolved.
- Issue: the revised plan correctly says docs-only manual intake must not let the agent read/parse/hash PDFs, and that file/PDF reading requires a separate heavy gate with a `FundDocumentRepository`-compatible intake boundary. However, the same revision still allowed local PDF path plus checksum without official locator/id to enter `matched_identity_no_field_unlock`.
- Impact: without official locator, official announcement id, official document id, or repository-derived provenance, a local PDF path plus checksum could still be treated as an accepted matched identity row.
- Required fix: local PDF path plus checksum without official locator/id must be limited to `manual_review_required`, `deferred`, or `blocked`; it must not enter `matched_identity_no_field_unlock`.

## Residual Risk

Prior schema/status finding is resolved. The revised plan now defines primary manifest, fixture projection, row key, field unlock key, schema version, current manifest/fixture mapping, and `ReportSourceDocument` mapping tests.

## Verdict

FAIL. One localized boundary finding remains.
