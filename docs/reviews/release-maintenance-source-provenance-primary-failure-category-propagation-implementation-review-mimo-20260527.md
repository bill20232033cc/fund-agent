# Code Review

## Scope

- Mode: current changes (workspace uncommitted changes relative to `main`)
- Branch: `codex/local-reconciliation`
- Base: `main`
- Output file: `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-implementation-review-mimo-20260527.md`
- Included scope: all 12 uncommitted modified files (3 implementation, 6 tests, 3 doc sync)
- Excluded scope: renderer, FQ0-FQ6, CLI, Host, Agent, dayu, baseline, golden
- Parallel review coverage: 无
- Truth sources: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, accepted plan `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-design-plan-20260527.md`, controller judgment `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-design-plan-controller-judgment-20260527.md`, implementation evidence `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-implementation-evidence-20260527.md`

## Findings

未发现实质性问题。

### Verification Summary

**1. AnnualReportSourceFailureCategory move to models.py and import safety**

- `fund_agent/fund/documents/models.py:15-21`: Type correctly defined next to `AnnualReportSourceName`. No circular import; `models.py` has zero imports from `sources.py`.
- `fund_agent/fund/documents/sources.py:21-25`: Imports `AnnualReportSourceFailureCategory` from `models`. Local alias removed.
- `tests/fund/documents/test_cache.py:186-201` (`test_document_models_exports_source_failure_category_without_sources_import`): Proves import safety — all three types importable from `models` without touching `sources`.

**2. Metadata serialization/deserialization/backward compatibility**

- `fund_agent/fund/documents/models.py:93`: `to_dict()` includes exact key `"primary_failure_category"`.
- `fund_agent/fund/documents/models.py:111,128`: `from_dict()` reads via `_optional_string` then `_normalize_failure_category()`.
- `fund_agent/fund/documents/models.py:326-349`: `_normalize_failure_category()` accepts the five known categories; missing/unknown/empty returns `None` — no exception, no new public enum value.
- `tests/fund/documents/test_cache.py:134-183`: Round-trip test and legacy/unknown degradation test both pass. Legacy JSON without the key deserializes `primary_failure_category=None`. Unknown string `"unexpected"` degrades to `None`.

**3. AnnualReportSourceOrchestrator fallback success records failures[0].category**

- `fund_agent/fund/documents/sources.py:652-658`: After a primary source failure and successful fallback, passes `failures[0].category` to `_mark_fallback_used()`. Fail-closed categories (`schema_drift`, `identity_mismatch`, `integrity_error`) still raise `AnnualReportSourceFallbackBlockedError` before fallback is attempted — source ordering and fail-closed strategy unchanged.
- `fund_agent/fund/documents/sources.py:767-792`: `_mark_fallback_used()` signature now includes `primary_failure_category` kwarg; sets both `fallback_used=True` and the category on metadata via `dataclasses.replace`.
- `tests/fund/documents/test_annual_report_sources.py:737-758,953-980,984-1008`: Tests prove `not_found` and `unavailable` both persist correctly. Fail-closed tests (lines 762-788, 1011-1101) prove `schema_drift`, `identity_mismatch`, `integrity_error` still block fallback.

**4. source_provenance effective_category precedence and missing-category unknown behavior**

- `fund_agent/fund/source_provenance.py:139-143`: `effective_category` correctly prefers `source_metadata.primary_failure_category` when non-`None`, falls back to kwarg otherwise. Matches the accepted plan truth table.
- `fund_agent/fund/source_provenance.py:167-176`: Missing category (`effective_category is None`) falls through to `unknown_public_metadata_absent` with `source_provenance_status="incomplete"`.
- `tests/fund/test_source_provenance.py:89-111,114-141,143-164,167-221,223-270`: All five precedence truth-table rows verified: metadata wins over kwarg, kwarg fallback works when metadata category is `None`, missing category remains unknown, eligible/fail-closed classification correct.

**5. Tests actually cover the required scenarios**

| Required scenario | Test file | Verdict |
|---|---|---|
| Metadata wins over kwarg | `test_source_provenance.py:223-247` | PASS |
| Kwarg fallback when metadata missing | `test_source_provenance.py:250-270` | PASS |
| Old/invalid metadata | `test_cache.py:160-183` | PASS |
| Fail-closed source chain blocked | `test_annual_report_sources.py:762-788,1011-1101` | PASS |
| Snapshot fields stable + category copied | `test_extraction_snapshot.py:126-221,223-272` | PASS |
| Score no-change | Not modified (existing `test_extraction_score.py` unchanged) | PASS |
| Import safety | `test_cache.py:186-201` | PASS |
| Bundle default provenance not_applicable | `test_data_extractor.py:194-231` | PASS |
| Extractor projects metadata category | `test_data_extractor.py:294-324` | PASS |
| Missing category stays unknown via extractor | `test_data_extractor.py:264-290` | PASS |

**6. Scope creep verification**

- Changed files: `models.py`, `sources.py`, `source_provenance.py` (implementation); 6 test files; `docs/design.md`, `fund_agent/fund/README.md`, `tests/README.md` (doc sync).
- No renderer, FQ0-FQ6, scoring policy, quality gate, CLI, Host/Agent, dayu, baseline, golden, or source strategy changes.
- Doc sync changes are minimal: `design.md` adds one clause about `primary_failure_category` persistence in the metadata bullet and updates the source provenance paragraph; `fund_agent/fund/README.md` and `tests/README.md` update field/provenance descriptions to reflect the new behavior. All within accepted plan boundaries.

**7. Validation results**

- `uv run pytest tests/fund/documents/test_annual_report_sources.py tests/fund/documents/test_cache.py tests/fund/documents/test_repository.py tests/fund/test_source_provenance.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py -q`: 100 passed
- `uv run ruff check fund_agent/fund tests/fund`: All checks passed
- `git diff --check`: Clean

## Open Questions

无。

## Residual Risk

- Old cached metadata with `fallback_used=true` and no `primary_failure_category` will continue to classify as `unknown_public_metadata_absent` until refreshed. This is accepted compatibility behavior documented in the plan and evidence.
- Multi-source chains beyond primary + fallback remain out of scope; would require a future provenance-chain schema gate.
- No bounded `110020` / `017641` evidence rerun was performed in this review (per handoff instructions).

## Verdict

**PASS**. Implementation matches the accepted plan and controller judgment exactly. All required verifiers pass. No material correctness, stability, or maintainability findings.
