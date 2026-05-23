# P8-S3 Source Fallback Policy Design Plan（2026-05-21）

## Scope

P8-S3 addresses the Post-P8-S2 residual:

> EID is now the official primary annual-report source, but fallback eligibility is still implicit in exception control flow.

The goal is to make source failure taxonomy, fallback policy, and provenance explicit inside the Fund Capability document source layer. This is not an availability-improvement slice. It preserves the current conservative rule that official-source drift or identity contradictions must not be hidden by Eastmoney fallback.

## Current Code Facts

- `AnnualReportSourceOrchestrator` lives in `fund_agent/fund/documents/sources.py`.
- Default source order is `(EidAnnualReportSource, EastmoneyAnnualReportSource)`.
- All production annual-report access still goes through `FundDocumentRepository`; source orchestration is an internal adapter concern.
- Current explicit source exceptions:
  - `AnnualReportSourceNotFoundError`
  - `AnnualReportSourceUnavailableError`
  - `AnnualReportSourceMismatchError`
  - `AnnualReportSourceSchemaError`
- Current `AnnualReportSourceFailure.category` only accepts `not_found` and `unavailable`.
- Current fallback behavior:
  - `not_found` continues to next source.
  - `unavailable` continues to next source.
  - `mismatch` raises immediately and blocks fallback.
  - `schema` raises immediately and blocks fallback.
- Existing tests in `tests/fund/documents/test_annual_report_sources.py` already prove the above behavior, including `fallback_used=True` when Eastmoney succeeds after an EID failure.

## Design Decision

Add an explicit source failure taxonomy and table-driven fallback policy while preserving behavior:

| Taxonomy category | Meaning | Fallback eligible? | Current mapping |
|---|---|---:|---|
| `not_found` | Source successfully responded but has no requested fund/year report. | yes | `AnnualReportSourceNotFoundError` |
| `unavailable` | Network, timeout, transient HTTP/server, or local source dependency unavailable. | yes | `AnnualReportSourceUnavailableError` |
| `schema_drift` | Official source response shape, required fields, candidate multiplicity, or unsupported attachment shape differs from contract. | no | `AnnualReportSourceSchemaError` |
| `identity_mismatch` | Source returned candidate contradicting requested fund code, fund id, year, report type, or annual-report identity. | no | `AnnualReportSourceMismatchError` |
| `integrity_error` | Retrieved PDF/file content fails integrity checks such as content type or `%PDF-` header. | no | new subclass or explicit wrapper for PDF integrity failures |

The orchestrator should record all source failures as `AnnualReportSourceFailure`, including fail-closed failures. When a blocking category occurs, it should raise a structured exception carrying the blocking failure and any prior failures. That makes “fallback blocked because official source drifted” auditable without weakening the policy.

## Public Contract

### New Type Alias

Add a source failure category alias near the source models in `fund_agent/fund/documents/sources.py`:

```python
AnnualReportSourceFailureCategory = Literal[
    "not_found",
    "unavailable",
    "schema_drift",
    "identity_mismatch",
    "integrity_error",
]
```

`AnnualReportSourceFailure.category` should use this alias instead of the current two-value literal.

### Blocking Exception

Add:

```python
class AnnualReportSourceFallbackBlockedError(Exception):
    failures: tuple[AnnualReportSourceFailure, ...]
    blocking_failure: AnnualReportSourceFailure
```

Rules:

- It is raised when a source failure category is not fallback-eligible.
- Its message includes all recorded failures in existing `_format_failures(...)` style.
- It should not inherit from `FileNotFoundError`, `AnnualReportSourceNotFoundError`, or `AnnualReportSourceUnavailableError`.
- It should preserve the original exception as `__cause__`.

Rationale:

- Existing mismatch/schema exceptions do not carry source/category/provenance.
- Reusing `AnnualReportSourceAggregateError` would blur “all sources exhausted” with “fallback intentionally blocked.”
- A dedicated exception keeps the policy visible and testable while leaving repository callers on the existing exception hierarchy for not-found and unavailable exhaustion.

### Integrity Error

Add:

```python
class AnnualReportSourceIntegrityError(ValueError):
    ...
```

Use it for PDF integrity failures. P8-S3 should avoid broad rewrites: it can change `_validate_pdf_response(...)` and `_write_pdf_bytes_atomic(...)` to raise `AnnualReportSourceIntegrityError` for content type, missing `%PDF-`, and invalid PDF bytes. Other EID JSON/schema issues remain `AnnualReportSourceSchemaError`.

## Fallback Policy

Keep policy local and table-driven:

```python
_FALLBACK_ELIGIBLE_CATEGORIES: Final[frozenset[AnnualReportSourceFailureCategory]] = frozenset(
    {"not_found", "unavailable"}
)
```

Helper:

```python
def _can_fallback_after_failure(category: AnnualReportSourceFailureCategory) -> bool:
    return category in _FALLBACK_ELIGIBLE_CATEGORIES
```

The helper should stay private unless implementation review finds a real external need. Tests can validate behavior through `AnnualReportSourceOrchestrator`.

## Orchestrator Semantics

Update `AnnualReportSourceOrchestrator.fetch_annual_report_pdf(...)`:

1. Initialize `failures: list[AnnualReportSourceFailure]`.
2. For each source:
   - On success:
     - if prior failures exist, mark result metadata `fallback_used=True`;
     - return result.
   - On `AnnualReportSourceNotFoundError`, append category `not_found`; continue.
   - On `AnnualReportSourceUnavailableError`, append category `unavailable`; continue.
   - On `AnnualReportSourceMismatchError`, append category `identity_mismatch`; raise `AnnualReportSourceFallbackBlockedError`.
   - On `AnnualReportSourceSchemaError`, append category `schema_drift`; raise `AnnualReportSourceFallbackBlockedError`.
   - On `AnnualReportSourceIntegrityError`, append category `integrity_error`; raise `AnnualReportSourceFallbackBlockedError`.
3. If all sources are exhausted with only eligible categories, keep current `_raise_exhausted_sources(...)` behavior:
   - all `not_found` -> `AnnualReportSourceNotFoundError`
   - single unavailable-only source -> `AnnualReportSourceUnavailableError`
   - mixed or multi-source unavailable -> `AnnualReportSourceAggregateError`

P8-S3 should not change source order, cache paths, network retry behavior, parsed-report cache behavior, or repository public method signatures.

## Provenance Requirements

Fallback-used path:

- Preserve current `AnnualReportSourceMetadata.fallback_used=True` when a lower-priority source succeeds after any prior eligible failure.

Fallback-blocked path:

- `AnnualReportSourceFallbackBlockedError.failures` contains prior eligible failures plus the blocking failure.
- `blocking_failure` is the last failure and has category `schema_drift`, `identity_mismatch`, or `integrity_error`.
- The exception string includes source/category/message, so CLI/service logs remain readable without custom serialization.

Do not add fallback-blocked fields to `AnnualReportSourceMetadata` in P8-S3 because there is no successful annual-report PDF metadata object on the blocked path.

## Implementation Plan

### S1. Taxonomy And Policy

Files:

- `fund_agent/fund/documents/sources.py`
- `tests/fund/documents/test_annual_report_sources.py`

Changes:

- Add `AnnualReportSourceFailureCategory`.
- Expand `AnnualReportSourceFailure.category`.
- Add `_FALLBACK_ELIGIBLE_CATEGORIES`.
- Add `_can_fallback_after_failure(...)`.
- Add `AnnualReportSourceFallbackBlockedError`.
- Add tests proving:
  - `not_found` still falls back.
  - `unavailable` still falls back.
  - exhausted eligible categories keep current final exceptions.

### S2. Blocking Categories

Files:

- `fund_agent/fund/documents/sources.py`
- `tests/fund/documents/test_annual_report_sources.py`

Changes:

- Map `AnnualReportSourceMismatchError` to `identity_mismatch`.
- Map `AnnualReportSourceSchemaError` to `schema_drift`.
- Raise `AnnualReportSourceFallbackBlockedError` instead of leaking the original mismatch/schema exception directly from the orchestrator.
- Preserve original exception in `__cause__`.
- Add tests proving fallback source is not called and `blocking_failure.category` is correct.

### S3. Integrity Error

Files:

- `fund_agent/fund/documents/sources.py`
- `tests/fund/documents/test_annual_report_sources.py`

Changes:

- Add `AnnualReportSourceIntegrityError`.
- Use it for PDF content-type and `%PDF-` header failures.
- Map it to `integrity_error` in orchestrator.
- Add tests for:
  - EID invalid PDF response raises integrity error when source used directly.
  - orchestrator blocks fallback and records `integrity_error` when primary source raises integrity error.

### S4. Docs

Files:

- `fund_agent/fund/README.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `tests/README.md`

Updates:

- Explain the source fallback policy table at the Fund Capability level.
- State that EID schema drift, identity mismatch, and integrity errors fail closed.
- Keep public user docs focused on current behavior; do not add future-source promises.

## Testing Plan

Targeted:

```bash
pytest tests/fund/documents/test_annual_report_sources.py tests/fund/documents/test_repository.py -q
```

Related:

```bash
pytest tests/fund/documents tests/fund/pdf -q
```

Full verification:

```bash
pytest
ruff check
git diff --check
```

## Non-Goals

- Do not add 天天基金 or any third source.
- Do not make Eastmoney a peer primary source.
- Do not change `FundDocumentRepository` public API.
- Do not change PDF parser behavior.
- Do not change source cache schema unless tests show provenance cannot be preserved without it.
- Do not weaken fail-closed behavior for official-source schema drift, identity mismatch, or integrity errors.
- Do not touch quality gate, renderer, audit, Service, UI, or Engine.

## Acceptance Criteria

- Source failure taxonomy covers all five accepted categories.
- Fallback eligibility is table-driven and tested.
- EID not-found and unavailable still allow Eastmoney fallback.
- EID schema drift, identity mismatch, and integrity errors block fallback.
- Blocked fallback raises a structured exception carrying source/category/message provenance.
- Fallback success still marks `AnnualReportSourceMetadata.fallback_used=True`.
- Docs and tests reflect current implemented behavior.
