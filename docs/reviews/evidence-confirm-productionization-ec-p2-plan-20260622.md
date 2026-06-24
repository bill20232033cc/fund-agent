# Evidence Confirm Productionization EC-P2 Plan

## Verdict

`PLAN_READY_FOR_REVIEW_NOT_READY`

## Scope

- Work unit: `Evidence Confirm Productionization Program`
- Slice: `EC-P2 Repository-bounded Live Source/PDF Evidence Gate`
- Gate: `plan`
- Gate classification: `heavy`
- Artifact: `docs/reviews/evidence-confirm-productionization-ec-p2-plan-20260622.md`
- Branch: `evidence-confirm-productionization`
- Upstream PR: PR-40 (`https://github.com/bill20232033cc/fund-agent/pull/40`)
- User authorization: `同意 EC-P2：sample 004393/2025，授权 repository-bounded live/PDF 命令。`

This plan does not implement source code, run live/network/PDF/provider/LLM commands, alter Service/UI/Host/renderer/quality-gate behavior, change source fallback behavior, mark PR-40 ready, merge, or claim release/readiness.

## Goal

Prove that the EC-P1A `ParsedAnnualReport` reference materializer can be reached through the production document repository boundary and can produce deterministic Evidence Confirm references from a single authorized live annual-report sample.

The smallest valid implementation is a Fund-layer repository runner/facade that:

1. accepts an injected repository for fake no-live tests;
2. defaults to `FundDocumentRepository()` only in the runner when no repository is injected;
3. calls only `repository.load_annual_report(fund_code, report_year, force_refresh=...)`;
4. feeds the returned `ParsedAnnualReport` into `build_annual_report_evidence_confirm_references()`;
5. returns safe scalar provenance, build status, issue reasons, reference counts, and optional V2 Evidence Confirm status;
6. classifies repository/source failures without changing fallback behavior.

## Motivation

EC-P1A proved only no-live materialization over caller-supplied `ParsedAnnualReport`. It did not prove that live source/PDF annual-report acquisition can enter Evidence Confirm through `FundDocumentRepository`, and it did not prove that live source failure branches are classified without hidden fallback.

EC-P2 should therefore prove the repository boundary before Service/UI/quality-gate integration or semantic entailment. Integrating upward before this proof would make upper layers depend on unproven source/PDF behavior.

## Success Signals

- Fake repository positive path calls exactly `load_annual_report()` and never calls PDF/cache/source helper methods.
- Fake repository failure cases classify `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, and `integrity_error`.
- Positive path preserves current EID single-source/no-fallback admission before creating `proven` annual-report references.
- The authorized live sample is exactly `004393 / 2025 / annual_report` with `force_refresh=True`.
- Live evidence artifact records only safe scalar metadata: source name, selected source, source mode, fallback flags, primary failure category, reference count, issue reasons, materializer status, and V2 status if a projection is supplied.
- Live V2 evidence uses only an EC-P2 pathway-smoke projection derived from the loaded `ParsedAnnualReport`; it proves repository -> parsed report -> section reference materializer -> V2 wiring, not field extraction correctness or product fact correctness.
- Any ambiguous failure classification stops as `ambiguous_repository_failure` and routes to a source/failure-class gate.
- No Service/UI/Host/renderer/quality-gate behavior changes occur in EC-P2.

## Non-goals

- No semantic entailment Evidence Confirm.
- No deterministic production facade composition beyond this repository runner.
- No Service/UI/renderer/quality-gate consumption.
- No production default-on policy.
- No multi-sample live matrix.
- No provider/LLM execution.
- No source fallback behavior change.
- No `EvidenceSourceKind` or public `EvidenceAnchor` expansion.
- No Docling/pdfplumber/EID HTML candidate direct consumption.
- No PR mark-ready, reviewer request, merge, release, or readiness transition.

## Direct Code Evidence

| Evidence | Meaning |
|---|---|
| `fund_agent/fund/evidence_confirm_sources.py` | EC-P1A materializer consumes only supplied `ParsedAnnualReport` and `ChapterFactProjection`; it does not instantiate `FundDocumentRepository` or call live/PDF/cache/source helpers. |
| `fund_agent/fund/evidence_confirm_sources.py` `_metadata_admission_satisfied()` | Current proof-positive reference admission requires EID source, `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=False`, `fallback_used=False`, no `primary_failure_category`, and fund/year identity match. |
| `fund_agent/fund/documents/repository.py` `FundDocumentRepository.load_annual_report()` | Current public repository boundary returns `ParsedAnnualReport` and does not expose local PDF path upward. |
| `fund_agent/fund/documents/repository.py` `_is_current_eid_single_source_metadata()` | Repository cache reuse is already constrained to current EID single-source metadata. |
| `fund_agent/fund/documents/sources.py` | Source layer owns `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error` classification and fallback blocking. |
| `fund_agent/fund/evidence_confirm.py` | V2 confirm consumes explicit `EvidenceConfirmReference` values and fails closed on candidate-only/not-proven/wrong source/year/value mismatch. |
| `docs/design.md` source policy sections | Current production annual-report source policy is EID single-source with no fallback. |
| `docs/reviews/evidence-confirm-productionization-ec-p2-goal-confirmation-authorization-20260622.md` | EC-P2 authorization is limited to sample `004393 / 2025` and repository-bounded live/PDF command. |

## Affected Files

Implementation gate may edit only:

- `fund_agent/fund/evidence_confirm_sources.py`
- `tests/fund/test_evidence_confirm_sources.py`
- `scripts/evidence_confirm_ec_p2_live_sample.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- EC-P2 implementation/review/evidence artifacts under `docs/reviews/`

The implementation gate must not edit:

- `fund_agent/services/`
- `fund_agent/ui/` or CLI behavior
- renderers
- `fund_agent/fund/quality_gate.py`
- `fund_agent/fund/quality_gate_integration.py`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/sources.py`
- public `EvidenceSourceKind` / `EvidenceAnchor` schemas

If implementation discovers a need to edit repository/source internals or upper layers, stop and route to a separate reviewed gate.

## Contract

Add EC-P2 runner contracts in `fund_agent/fund/evidence_confirm_sources.py`.

### Types

Add:

```python
EvidenceConfirmRepositoryRunStatus = Literal["pass", "fail"]
EvidenceConfirmRepositoryFailureCategory = Literal[
    "not_found",
    "unavailable",
    "schema_drift",
    "identity_mismatch",
    "integrity_error",
    "ambiguous_repository_failure",
]
```

Add frozen slotted dataclasses:

```python
@dataclass(frozen=True, slots=True)
class EvidenceConfirmRepositoryRunRequest:
    fund_code: str
    report_year: int
    projection: ChapterFactProjection
    repository: object | None = None
    force_refresh: bool = False
    max_section_excerpt_chars: int = DEFAULT_MAX_SECTION_EXCERPT_CHARS
    run_v2_confirm: bool = True

@dataclass(frozen=True, slots=True)
class EvidenceConfirmRepositorySourceProvenance:
    source: str | None
    selected_source: str | None
    source_mode: str | None
    fallback_enabled: bool | None
    fallback_used: bool | None
    primary_failure_category: str | None
    metadata_admitted: bool

@dataclass(frozen=True, slots=True)
class EvidenceConfirmRepositoryRunIssue:
    issue_id: str
    severity: Literal["blocking", "informational"]
    reason: str
    message: str
    failure_category: EvidenceConfirmRepositoryFailureCategory | None = None

@dataclass(frozen=True, slots=True)
class EvidenceConfirmRepositoryRunResult:
    status: EvidenceConfirmRepositoryRunStatus
    fund_code: str
    report_year: int
    source_provenance: EvidenceConfirmRepositorySourceProvenance | None
    reference_build_result: EvidenceConfirmReferenceBuildResult | None
    evidence_confirm_result: EvidenceConfirmResultV2 | None
    issues: tuple[EvidenceConfirmRepositoryRunIssue, ...]
```

The result may include full in-memory `reference_build_result` and `evidence_confirm_result` for Fund-layer tests. The live evidence script must serialize only safe scalar fields and must not persist full excerpts unless a later artifact explicitly authorizes retained excerpt storage.

### Public Function

Add:

```python
async def run_repository_bounded_evidence_confirm(
    request: EvidenceConfirmRepositoryRunRequest,
) -> EvidenceConfirmRepositoryRunResult:
    ...
```

Behavior:

1. Normalize and validate `fund_code` and `report_year` using local simple checks; do not import repository private validators.
2. Use `request.repository` when supplied.
3. If no repository is supplied, instantiate `FundDocumentRepository()` inside this function only.
4. Require the repository object to expose coroutine method `load_annual_report`; otherwise return `fail` with `invalid_repository`.
5. Call exactly `await repository.load_annual_report(request.fund_code, request.report_year, force_refresh=request.force_refresh)`.
6. Do not call `fetch_pdf`, `fetch_pdf_path`, `parse_pdf`, cache APIs, source adapters, filesystem paths, Docling/pdfplumber/EID candidate helpers, Service, Host, renderer, quality gate, or provider.
7. Extract safe scalar provenance from `parsed_report.metadata.source`.
8. If provenance does not satisfy the same current EID single-source/no-fallback admission used by EC-P1A, return `fail` with `source_truth_metadata_negative` and do not create proven references.
9. Build references by calling `build_annual_report_evidence_confirm_references()` with `source_truth_status="proven"`.
10. If `run_v2_confirm=True`, call `confirm_projection_evidence_v2(request.projection, build_result.references)`.
11. Overall `status` is `pass` only when repository load succeeds, provenance is admitted, reference build status is `pass`, and V2 result is absent or `overall_status == "pass"`.

The runner does not create projections. Any caller, including the authorized live script, must pass a projection explicitly. This preserves the EC-P2 boundary: repository/source/PDF admission and materializer wiring are proved, while field extraction and production projection generation remain later gates.

## Failure Classification

Add a local classifier for exceptions raised by `repository.load_annual_report()`. It must not change repository/source behavior.

Classification order:

1. `FileNotFoundError` -> `not_found`.
2. Existing source exceptions from `fund_agent.fund.documents.sources`:
   - `AnnualReportSourceUnavailableError` -> `unavailable`.
   - `AnnualReportSourceFallbackBlockedError` -> use its current failure category if available; if unavailable, `ambiguous_repository_failure`.
   - `AnnualReportSourceAggregateError` -> use aggregate/current category only if available and in the allowed five categories; otherwise `ambiguous_repository_failure`.
3. Exceptions with a string or attribute category exactly in `{"not_found", "unavailable", "schema_drift", "identity_mismatch", "integrity_error"}` may be classified to that category for fake-repository testing and typed source errors.
4. Any other exception -> `ambiguous_repository_failure`.

For `ambiguous_repository_failure`, the runner returns `fail`, records only exception class name and safe message, and does not fallback or reclassify as `unavailable`.

The classifier must be unit-tested with fake exceptions for all five accepted categories and one ambiguous exception.

## Live Projection Source

The authorized live sample must not call Service, `FundDataExtractor`, Processor/Extractor facade, renderer, quality gate, provider, or LLM to create a projection. It must not hand-code product facts or use another fund/year fixture.

Instead, the live script may create one local EC-P2 pathway-smoke projection after `FundDocumentRepository.load_annual_report("004393", 2025, force_refresh=True)` succeeds:

1. Select the first stable section from the loaded `ParsedAnnualReport.sections` sorted by `section_id` whose `get_section_text(section_id)` is non-empty after whitespace normalization.
2. Derive a short smoke value from the same section excerpt, using the first non-empty normalized token of at least two characters.
3. Construct a minimal in-memory `ChapterFactProjection` with:
   - `fund_code="004393"`;
   - `report_year=2025`;
   - one available smoke fact whose value is the derived token;
   - one `ChapterEvidenceAnchor` with `source_kind="annual_report"`, `document_year=2025`, the selected `section_id`, and no table/row locator.
4. Pass that projection into `run_repository_bounded_evidence_confirm()`.
5. Mark the serialized output with `projection_kind="ec_p2_live_section_smoke"` and `field_correctness_proven=false`.

This projection exists only to prove the live repository/materializer/V2 wiring path. It is not a product fact, not a field-family source-truth extraction result, not semantic entailment, not golden/readiness evidence, and not authorized for Service/UI/renderer/quality-gate consumption.

If no non-empty section can be selected, the script must fail with `live_projection_section_unavailable` and must not synthesize text from PDF/cache/source helper or parser artifacts outside `ParsedAnnualReport`.

## Fake Repository Tests

Add no-live tests before live execution:

- Positive fake repository:
  - exposes only async `load_annual_report()`;
  - records the exact `(fund_code, year, force_refresh)` call;
  - returns a fake `ParsedAnnualReport` with current EID single-source metadata;
  - result has `status="pass"`, source provenance admitted, references present, V2 `overall_status="pass"`.
- Boundary fake repository:
  - has poison `fetch_pdf`, `fetch_pdf_path`, and `parse_pdf` methods that raise if called;
  - test proves runner only calls `load_annual_report()`.
- Invalid repository:
  - missing coroutine `load_annual_report()` returns `invalid_repository`.
- Negative provenance:
  - fallback-used or non-EID metadata returns `source_truth_metadata_negative` and no V2 pass.
- Materializer failure:
  - unsupported table/row or missing section propagates materializer issue reasons and `status="fail"`.
- V2 mismatch:
  - references build but fact value mismatch returns `status="fail"` with V2 `overall_status="fail"`.
- Failure categories:
  - fake repository raises one exception for each of `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`;
  - runner returns corresponding failure category and no references.
- Ambiguous failure:
  - generic runtime exception returns `ambiguous_repository_failure`.
- Live projection smoke helper:
  - selects a non-empty section from a fake parsed report deterministically;
  - fails with `live_projection_section_unavailable` when all section texts are empty;
  - does not call Service, extractor/facade, renderer, quality gate, provider, or source helpers.
- Import isolation update:
  - replace the current source-text assertion that forbids `"load_annual_report"` in `evidence_confirm_sources.py`;
  - preserve the actual boundary assertion that importing the module does not instantiate `FundDocumentRepository`, touch network, read PDF/cache, or call `load_annual_report()`;
  - use monkeypatch/subprocess isolation to fail if import-time repository construction occurs.

## Authorized Live Evidence Command

After plan review, accepted plan commit, implementation, code review, fix/re-review, and accepted slice commit, the EC-P2 execution artifact may run exactly one live command for the authorized sample:

```bash
uv run python scripts/evidence_confirm_ec_p2_live_sample.py --fund-code 004393 --report-year 2025 --force-refresh
```

The script may be added only if it:

- calls the new runner;
- the runner calls only `FundDocumentRepository.load_annual_report("004393", 2025, force_refresh=True)`;
- builds only the EC-P2 pathway-smoke projection described above after repository load succeeds;
- rejects any fund/year other than `004393 / 2025`;
- prints JSON safe scalar output only;
- does not print PDF path, cache path, source URL, full excerpt text, provider payload, or raw parser artifact;
- exits non-zero on failure or ambiguous classification.

If adding a script is considered unnecessary in implementation review, an inline reviewed execution snippet may be used instead, but it must preserve the same command boundary and safe scalar output.

Expected live JSON scalar fields:

- `schema_version`
- `fund_code`
- `report_year`
- `status`
- `source`
- `selected_source`
- `source_mode`
- `fallback_enabled`
- `fallback_used`
- `primary_failure_category`
- `metadata_admitted`
- `reference_count`
- `reference_build_status`
- `reference_issue_reasons`
- `evidence_confirm_overall_status`
- `failure_category`
- `projection_kind`
- `field_correctness_proven`

## Validation Commands

Implementation gate must run:

```bash
uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py -q
uv run ruff check fund_agent/fund/evidence_confirm.py fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py
git diff --check -- fund_agent/fund/evidence_confirm.py fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm_sources.py scripts/evidence_confirm_ec_p2_live_sample.py fund_agent/fund/README.md tests/README.md
```

Live execution gate, after implementation is accepted, must run only the authorized command above and write an execution artifact under:

`docs/reviews/evidence-confirm-productionization-ec-p2-live-execution-20260622.md`

## Docs Decision

Implementation must update:

- `fund_agent/fund/README.md`: add current EC-P2 runner boundary, repository-only access, safe provenance output, and no upper-layer consumption.
- `tests/README.md`: add fake repository and single authorized live evidence test surface.

Do not update Service/UI/renderer/quality-gate docs in EC-P2 because their behavior must not change.

## Residual Risks

| Risk | Classification | Owner / Destination |
|---|---|---|
| Multi-sample live matrix not covered | covered by later approved slice | EC-P2 follow-up only after single positive sample accepted |
| Semantic entailment absent | covered by later approved slice | EC-P4 / EC-P5 |
| Service/UI/renderer/quality-gate still not consuming Evidence Confirm | covered by later approved slice | EC-P6 / EC-P7 / EC-P8 |
| Release/readiness remains unproven | covered by later approved slice | EC-P10 / EC-P11 |
| Repository/source internals may expose ambiguous exception shape | requiring new issue or explicit user decision if observed | source/failure-class gate |
| EC-P2 live smoke projection does not prove field correctness | covered by later approved slice | EC-P3 / Service integration and later source-truth/readiness gates |

## Stop Conditions

Stop and return to controller if any of these occur:

- Implementation needs to edit repository/source internals.
- Implementation needs direct PDF/cache/source helper calls.
- Fake repository tests cannot prove `load_annual_report()` is the only access method.
- Live script cannot build the EC-P2 pathway-smoke projection from `ParsedAnnualReport.sections` without using other layers.
- Live sample does not satisfy EID single-source/no-fallback provenance.
- Live failure category is ambiguous.
- Implementation requires Service/UI/Host/renderer/quality-gate changes.
- Implementation requires provider/LLM, semantic entailment, multi-sample live execution, PR mark-ready, merge, or release/readiness claim.

## Completion Report Format

Implementation worker must report:

- changed files;
- runner/facade contract summary;
- fake repository coverage matrix;
- live projection kind and explicit statement that field correctness is not proven;
- validation commands and results;
- live command artifact path and scalar result, only after implementation/review acceptance;
- residual risks with owner/destination;
- explicit statement that Service/UI/Host/renderer/quality-gate behavior, source fallback behavior, PR readiness, merge, and release/readiness were not changed.
