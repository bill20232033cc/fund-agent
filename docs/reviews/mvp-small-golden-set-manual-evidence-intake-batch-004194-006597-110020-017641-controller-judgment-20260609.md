# Manual Evidence Intake Batch Controller Judgment

## Gate

- Gate: `matched-source manual evidence intake gate`.
- Classification: `standard`.
- Judgment date: `2026-06-09`.
- Rows: `004194`, `006597`, `110020`, `017641` for report year `2024`.
- Scope: docs-only manual source identity evidence intake.

## Inputs

- Intake artifacts:
  - `docs/reviews/mvp-small-golden-set-manual-evidence-intake-004194-20260609.md`
  - `docs/reviews/mvp-small-golden-set-manual-evidence-intake-006597-20260609.md`
  - `docs/reviews/mvp-small-golden-set-manual-evidence-intake-110020-20260609.md`
  - `docs/reviews/mvp-small-golden-set-manual-evidence-intake-017641-20260609.md`
- Source payloads:
  - `docs/reviews/mvp-small-golden-set-manual-evidence-intake-004194-20260609-source-payload.json`
  - `docs/reviews/mvp-small-golden-set-manual-evidence-intake-006597-20260609-source-payload.json`
  - `docs/reviews/mvp-small-golden-set-manual-evidence-intake-110020-20260609-source-payload.json`
  - `docs/reviews/mvp-small-golden-set-manual-evidence-intake-017641-20260609-source-payload.json`
- Manifest: `docs/reviews/mvp-small-golden-set-source-identity-recovery-manifest-20260608.json`.
- Independent reviews:
  - `docs/reviews/mvp-small-golden-set-manual-evidence-intake-batch-004194-006597-110020-017641-review-ds-20260609.md`: PASS.
  - `docs/reviews/mvp-small-golden-set-manual-evidence-intake-batch-004194-006597-110020-017641-review-mimo-20260609.md`: PASS.

## Decision

Accepted.

The controller accepts `004194 / 2024`, `006597 / 2024`, `110020 / 2024` and `017641 / 2024` as review-owned docs-only manual annual-report source identity evidence.

## Accepted Facts

- The accepted evidence is user-provided official locator/id/metadata/checksum captured in `docs/reviews`.
- The accepted evidence is sufficient only for source identity recovery status under `source_boundary=manual_review`.
- `004393 / 2024` remains accepted from the prior manual evidence intake gate.
- The source identity recovery manifest may advance the four reviewed rows from `pending_review` to `controller_accepted`.

## Explicit Non-Acceptance

- No external URL, registry page or PDF was verified.
- No PDF was opened, downloaded, read or hashed by this gate.
- No `FundDocumentRepository` access was performed.
- No fallback was invoked.
- No extractor was changed.
- No fixture projection was performed.
- No retained excerpt fixture was created.
- No field-level expected values were accepted.
- No exact/numeric extractor correctness was accepted.
- No row-field unlocks were granted.
- No golden/readiness or promotion semantics changed.

## Residuals

- `004194`, `006597`, `110020` and `017641` do not have accepted field-level excerpts or expected values.
- Rows with `user_provided_pdf_sha256=not_provided` do not prove PDF byte identity.
- `006597`, `110020` and `017641` retain EID document-id uncertainty where noted in their intake artifacts.
- `110020` future row-field assertions must distinguish share-class columns because `Y=022928` was added from `2024-12-13` per user-provided note.
- `017641` remains a QDII row and is not promotion-ready.

## Next Entry Point

Stop after local accepted checkpoint and wait for explicit user authorization for one of:

- additional docs-only manual evidence intake gate;
- matched-source retained excerpt fixture gate;
- row-field extractor-correctness implementation gate after accepted field excerpts and expected values;
- matched-source `FundDocumentRepository` acquisition evidence gate;
- separate non-extractor phase.

Do not enter extractor, fixture projection, `FundDocumentRepository`, PDF/network/live/fallback, Chapter calibration, Agent runtime, multi-year, score-loop, PR/release, golden/readiness promotion, provider/default/runtime/budget/config changes, or exact/numeric correctness without a separate reviewed gate and explicit authorization.
