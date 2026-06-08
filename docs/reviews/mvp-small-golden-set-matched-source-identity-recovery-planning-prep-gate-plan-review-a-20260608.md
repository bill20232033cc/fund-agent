# Plan Review A: Matched Source Identity Recovery Planning/Prep Gate

## Findings

### High - Manual PDF/local path evidence route can bypass document repository boundary

- Location: `docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-20260608.md:83`, `:117-124`, `:132`, `:181-186`.
- Issue: the plan allows a future `matched-source manual evidence intake gate` to use a user-provided PDF path, local file path, PDF checksum, and title-page anchor to establish matched identity, but does not specify how those PDFs/local files can be read, checked, or anchored without direct filesystem document access.
- Conflict: `AGENTS.md` requires fund document access through a unified document repository and production annual-report PDF access through `FundDocumentRepository`; `docs/design.md` also treats `FundDocumentRepository` as the only document read entry and preserves provenance/fallback semantics.
- Impact: a future implementation worker may compute `pdf_sha256` or read a title page directly, creating a second source path outside Fund document boundaries.
- Required fix: split manual evidence into two paths. If the agent does not read PDF files, it may only record user/human-provided official metadata, checksum, anchors, and reviewer/controller acceptance. If the agent must read a PDF/file, a separate heavy gate must define a `FundDocumentRepository`-compatible manual intake/adapter or equivalent unified repository entry with explicit PDF/file access authorization.

### High - Schema/status is not code-generation-ready

- Location: `docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-20260608.md:74-77`, `:141-148`, `:203-212`.
- Issue: the plan introduces `identity_status=matched/unmatched/...`, `identity_review_status=...`, and `matched_identity_no_field_unlock`, but does not map them to the accepted manifest status `pending_offline_fixture`, fixture status `source_identity.status=unmatched_synthetic`, or existing matched-row guard expectations.
- Impact: future work could create a third status machine or inconsistent truth sources across the review manifest, fixture-adjacent record, and `expected_fields.json`.
- Required fix: add a schema section that defines the target file or single allowed location, `schema_version`, row key, field key, status enums, mapping from `pending_offline_fixture` / `unmatched_synthetic`, review-only fields, fixture-projected fields, and tests for each transition.

## Open Questions

1. In the manual PDF/URL evidence route, is identity verification done by a human outside the agent, or by the agent reading/checking the file? The authorization boundary differs.
2. Is the future source identity truth source an extension of `expected_fields.json`, or a new review-owned manifest? The projection relation is not yet specified.

## Verdict

FAIL. Direction is correct, and non-goals align with current accepted facts, but the plan is not yet code-generation-ready for a heavy planning/prep gate.
