# Docling Baseline Qualification Built-in Representation Handler Implementation Controller Judgment - 2026-06-15

Gate: `Built-in Candidate Representation Route Handler No-live Implementation Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the no-live implementation review for built-in candidate representation route handlers.

Implementation evidence:

- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-implementation-evidence-20260615.md`

Review inputs:

- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-implementation-review-ds-20260615.md`
- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-implementation-review-mimo-20260615.md`
- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-implementation-rereview-ds-20260615.md`
- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-implementation-rereview-mimo-20260615.md`

Reviewed implementation files:

- `fund_agent/fund/documents/candidates/representation_handlers.py`
- `fund_agent/fund/documents/candidates/representation_export.py`
- `tests/fund/documents/test_candidate_representation_handlers.py`
- `tests/fund/documents/test_candidate_representation_export.py`
- `fund_agent/fund/README.md`

## 2. Truth Sources

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-plan-20260615.md`
- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-plan-controller-judgment-20260615.md`

Binding constraints preserved:

- EID single-source/no fallback remains current production source policy.
- Docling/pdfplumber/EID HTML render outputs remain candidate-only and not source truth.
- EID HTML render is not raw XML/XBRL truth.
- No `FundDocumentRepository`, source policy, production cache, Service, UI, Host, renderer, quality gate, extractor, `EvidenceAnchor` or `CHAPTER_CONTRACT` behavior changed.
- Release/readiness remains `NOT_READY`.

## 3. Accepted Implementation Facts

- Added candidate-internal built-in route handlers under `fund_agent/fund/documents/candidates/representation_handlers.py`.
- Added explicit `--run-built-in-handlers` CLI opt-in.
- Added default no-clobber for write-producing entries.
- Kept `reference_existing_json` read-only and never rewritten.
- Added handled-route preflight so missing handlers fail before any write.
- Bound default Docling converter to configured local `artifacts_path`, `do_ocr` and `do_table_structure`.
- Kept Docling import lazy and conversion socket-blocked by default.
- Kept pdfplumber handler fake-testable and candidate-internal.
- Kept EID HTML render handler blocked unless later accepted evidence provides render artifacts.

## 4. Review Disposition

| Finding | Source | Controller disposition | Reason |
|---|---|---|---|
| `DS-IMPL-F1`: default Docling converter checked artifact path existence but did not bind converter to that path. | DS implementation review | ACCEPT_WITH_FIX | `_default_docling_converter()` now constructs `PdfPipelineOptions(artifacts_path=workspace_root / docling_artifacts_path, do_ocr=..., do_table_structure=...)` and passes it through `PdfFormatOption` for `InputFormat.PDF`. Targeted DS re-review passed. |
| Mixed manifest could partially write blocked output before later handled entry failed for missing handler. | MiMo implementation review | ACCEPT_WITH_FIX | `export_manifest()` now preflights handled entries against available route handlers before any write. Regression test covers `(blocked, handled)` with no handler and no partial output. Targeted MiMo re-review passed. |
| Candidate-only / source policy / public boundary checks. | DS + MiMo reviews | ACCEPT | Reviews found no production repository/source/cache behavior change, no public documents export, no Service/UI/Host/renderer/quality gate direct access, no non-EID fallback, and no readiness/source-truth claim after fixes. |

## 5. Validation

Commands accepted for this gate:

```text
uv run pytest tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_export.py tests/fund/documents/test_docling_no_consumption_guards.py -q
uv run ruff check fund_agent/fund/documents/candidates/representation_handlers.py fund_agent/fund/documents/candidates/representation_export.py tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_export.py
git diff --check
```

Results:

- `25 passed in 3.15s`
- `All checks passed!`
- `git diff --check` passed

## 6. Residuals

| Residual | Status | Next handling |
|---|---|---|
| Full S4/S5/S6 Docling/pdfplumber representation export quality not proven. | Deferred | Full Representation Export Evidence Gate. |
| Docling runtime may still fail if local artifacts are incomplete. | Accepted residual | Evidence gate must record exact failure or output hashes. |
| EID HTML render for S4/S5/S6 remains blocked in first-wave manifest. | Accepted residual | Separate bounded EID HTML render discovery/evidence gate if needed. |
| S2/S3 provenance/hash issues remain outside this gate. | Deferred | Separate provenance/disposition gate. |
| Release/readiness remains `NOT_READY`. | Accepted residual | No readiness/release/PR claim. |

## 7. Final Verdict

`VERDICT: ACCEPT_IMPLEMENTATION_READY_FOR_FULL_REPRESENTATION_EXPORT_EVIDENCE_GATE_NOT_READY`

Next recommended gate:

`Full Representation Export Evidence Gate`

Do not proceed to field correctness validation, production integration, readiness, release or PR from this judgment.
