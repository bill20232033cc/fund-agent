# Extractor Projection Over Document Representation — S3 Plan

> **Date**: 2026-06-18
> **Gate**: Extractor Projection Over Document Representation Planning Gate
> **Classification**: standard; planning only
> **Author**: AgentMiMo planning worker

---

## Verdict

**PLAN_READY_NOT_READY**

The plan below defines a processor-contract/admission-helper slice that is code-generation-ready: protocol, admission helper, failure taxonomy projection, and no-live tests are fully specified. No production facade change or repository behavior change is included; concrete processor/facade integration is deferred to a later gate.

---

## 1. First-principles Goal and Non-goals

### Goal

Let a controlled document representation — especially `FundDisclosureDocument`-like candidate/intermediate objects — be projected through the Fund Processor/Extractor boundary. The projection must not bypass `FundDocumentRepository`, `EvidenceAnchor`, provenance, `CHAPTER_CONTRACT`, fail-closed gap semantics, or UI/Service/Host/renderer/quality-gate boundaries.

### Non-goals

- Does **not** replace the production parser (`pdfplumber -> ParsedAnnualReport`).
- Does **not** promote any candidate representation (`Docling`, `pdfplumber full JSON`, `EID HTML render`) to source truth.
- Does **not** change EID single-source policy, fallback behavior, provider defaults, repair budget, annual-period LLM route, or readiness/release status.
- Does **not** implement new fund-type processors (bond, index, QDII, FOF); only extends the dispatch contract and adds a `FundDisclosureDocument` intermediate path for `active_fund`.
- Does **not** expose candidate/internal representations to Service, UI, Host, renderer, quality gate, or LLM prompt.
- Does **not** authorize `field_correctness_status`, `source_truth_status`, `parser_replacement_authorized`, or `readiness_status` beyond `not_proven` / `not_ready`.
- Does **not** modify public `EvidenceSourceKind` or `EvidenceAnchor.source_kind` — these remain `annual_report` / `external_api` / `derived`. Candidate route identity is expressed via `FundExtractionSourceBoundary` (already includes `candidate_only`), `CandidateBoundaryStatus`, `FundExtractionGap.source_boundary`, candidate note/metadata, or processor-level provenance.
- Does **not** modify `FundDataExtractor.extract()` or any production facade entry point. S3 is a pure processor-contract/admission-helper planning slice; concrete processor/facade integration is deferred to a later gate.

---

## 2. Current Code Facts vs Accepted Future Design vs Candidate/Research Inputs

### Current Code Facts (S2 accepted)

| Fact | Location | Boundary |
|---|---|---|
| `FundProcessorRegistry` with priority-based dispatch | `fund_agent/fund/processors/registry.py` | Pure memory; no IO |
| `ActiveFundAnnualProcessor` supports `active_fund + annual_report + parsed_annual_report.v1` | `fund_agent/fund/processors/active_annual.py` | Consumes only `ParsedAnnualReport` |
| `FundProcessorDispatchKey` with `intermediate_kind: FundIntermediateKind` | `fund_agent/fund/processors/contracts.py` | Already declares `fund_disclosure_document.v1` as valid literal |
| `FundProcessorInput.intermediate` typed as `ParsedAnnualReport \| object` | `fund_agent/fund/processors/contracts.py` | Union type already admits non-`ParsedAnnualReport` |
| `FundDataExtractor.extract()` routes `active_fund` through registry, others through legacy | `fund_agent/fund/data_extractor.py:321-339` | Gate on `classified_fund_type` only |
| `CandidateBoundaryStatus` enforces `candidate_only=True`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"` | `fund_agent/fund/processors/contracts.py:136-178` | Fail-closed invariant |
| `StructuredFundDataBundle` is the canonical output | `fund_agent/fund/data_extractor.py:188-248` | Consumed by renderer, audit, quality gate |
| Docling candidate models exist at `fund_agent/fund/documents/candidates/` | `candidates/models.py`, `representation_models.py`, etc. | Non-production, non-exported |

### Accepted Future Design (not yet implemented)

| Design | Source | Status |
|---|---|---|
| `FundDisclosureDocument` as Fund documents internal intermediate | `design.md` §6.1 | Accepted as future design; no schema implementation |
| `eid_xbrl_html_render_candidate` as candidate source kind | XBRL route realignment judgment | Accepted as candidate-only |
| `FundDisclosureDocument Candidate Source Schema Plan` | `funddisclosuredocument-candidate-source-schema-plan-20260614.md` | Accepted with plan-fix; no-live implementation planning authorized |

### Candidate/Research Inputs (evidence chain only)

| Input | Status |
|---|---|
| Docling `004393/2025` selected-fact match (21/21) | Candidate-only; not source truth |
| Docling EvidenceAnchor mapping (102/23475 yield) | Candidate-only; 99.96% missing section context |
| EID HTML render artifact discovery for `004393/2025` | Candidate-only; not raw XML |
| Candidate `representation_models.py`, `template_field_extraction.py` | Non-production internals |

---

## 3. Proposed Implementation Slice Boundaries and Allowed Modules/Files

### Slice Scope: S3 — `FundDisclosureDocument` Intermediate Admission to Processor Registry

This slice defines the processor-contract and admission-helper layer for `FundDisclosureDocument`-like intermediate objects. It does **not** implement a concrete `FundDisclosureDocumentProcessor` — that is a follow-up gate. It does **not** modify `FundDataExtractor.extract()` or any production facade entry point; concrete processor/facade integration is deferred to a later gate.

### Allowed New/Modified Files

| File | Action | Purpose |
|---|---|---|
| `fund_agent/fund/processors/contracts.py` | Modify | Add `FundDisclosureDocumentIntermediate` protocol |
| `fund_agent/fund/processors/fund_disclosure_dispatch.py` | **New** | Admission helper: failure taxonomy projection, CandidateBoundaryStatus validation, admission-decision computation |
| `tests/fund/processors/test_fund_disclosure_dispatch.py` | **New** | No-live contract tests for admission helper, no-leak tests, protocol conformance |
| `tests/fund/processors/test_registry.py` | Modify | Add dispatch-key coverage for `fund_disclosure_document.v1` (registry resolve raises UnsupportedFundProcessorError) |

### Explicitly Out-of-scope

- Concrete `FundDisclosureDocument` full schema implementation (deferred to schema planning gate)
- Concrete `DoclingFundDisclosureDocumentProcessor` implementation (deferred)
- `eid_xbrl_html_render_candidate` processor (deferred)
- Non-active fund type processors
- `FundDataExtractor.extract()` facade modification or admission of `fund_disclosure_document.v1` through the production facade (deferred to concrete processor gate)
- `FundDisclosureDocumentStub` in production `documents/models.py` — if a test-local stub is needed, it lives in the test file and is explicitly non-exported
- Service/UI/Host/renderer/quality-gate consumption of new intermediate

---

## 4. Input Contract

### 4.1 Intermediate Kind / Media Type / Version / Identity Fields

`FundProcessorDispatchKey` already declares:

```python
FundIntermediateKind = Literal[
    "parsed_annual_report.v1",
    "fund_disclosure_document.v1",          # ← already present
    "docling_pdf_candidate.v1",
    "pdfplumber_pdf_candidate.v1",
    "eid_xbrl_html_render_candidate.v1",
]
```

S3 adds a `FundDisclosureDocumentIntermediate` protocol to `contracts.py`:

```python
class FundDisclosureDocumentIntermediate(Protocol):
    """受控文档表示中间态协议。

    任何进入 Processor 边界的 FundDisclosureDocument-like 对象必须实现此协议。
    它只描述身份、来源 provenance 和 failure taxonomy；不描述完整文档内容。
    """

    @property
    def document_kind(self) -> Literal["annual_report"]: ...

    @property
    def fund_code(self) -> str: ...

    @property
    def report_year(self) -> int: ...

    @property
    def intermediate_kind(self) -> FundIntermediateKind: ...

    @property
    def source_provenance(self) -> PublicSourceProvenance | None: ...

    @property
    def candidate_boundary(self) -> CandidateBoundaryStatus | None: ...

    @property
    def failure_class(self) -> Literal[
        "not_found", "unavailable", "schema_drift",
        "identity_mismatch", "integrity_error", None
    ]: ...
```

**Note**: This protocol does **not** include `source_kind`. Candidate route identity is expressed via `FundExtractionSourceBoundary` (which already includes `candidate_only`), `CandidateBoundaryStatus`, and `FundExtractionGap.source_boundary` — not via public `EvidenceAnchor.source_kind` which remains `annual_report` / `external_api` / `derived`.

### 4.2 Source Provenance

- `source_provenance` must be explicitly provided or projectable from the intermediate's metadata.
- If `source_provenance` is `None` and the intermediate has no projectable metadata, the processor must emit a `source_provenance_unsafe` gap and block.
- Candidate intermediates must carry `CandidateBoundaryStatus(candidate_only=True)`.

### 4.3 Parser Failure Taxonomy Projection

Failure classes map to existing `FundExtractionGapCode` / `FundExtractionSourceBoundary` / `FundProcessorContractStatus` exactly. **No new gap codes are introduced.** The mapping is defined in `fund_disclosure_dispatch.py` as `FAILURE_CLASS_ADMISSION_MAP`.

Exact projection table:

| `AnnualReportSourceFailureCategory` | `FundExtractionGapCode` | `FundExtractionSourceBoundary` | `FundProcessorContractStatus` | Fallback |
|---|---|---|---|---|
| `not_found` | `unsupported_intermediate` | `unsupported_intermediate` | `unsupported` | No — no concrete processor exists |
| `unavailable` | `unsupported_intermediate` | `unsupported_intermediate` | `unsupported` | No — no concrete processor exists |
| `schema_drift` | `candidate_boundary_blocked` | `candidate_only` | `blocked` | No — fail-closed |
| `identity_mismatch` | `candidate_boundary_blocked` | `candidate_only` | `blocked` | No — fail-closed |
| `integrity_error` | `candidate_boundary_blocked` | `candidate_only` | `blocked` | No — fail-closed |

**Why this mapping**: S3 has no concrete processor, so `not_found` / `unavailable` map to `unsupported_intermediate` (the intermediate cannot be processed). `schema_drift` / `identity_mismatch` / `integrity_error` are structural failures that block the candidate boundary. These are existing gap codes — no new codes are added to `FundExtractionGapCode`.

**Important**: This mapping is the **admission-decision projection only**. When a concrete `FundDisclosureDocumentProcessor` is implemented (S4+), it will use `FundProcessorResult` with field-family-level gaps. The admission helper does not produce `FundProcessorResult`; it produces `DisclosureAdmissionDecision`. Fallback logic for `not_found` / `unavailable` is **not** implemented in S3.

### 4.4 Candidate Admission Rule

Candidate objects are admitted **only** when:
1. `candidate_boundary.candidate_only == True`
2. `candidate_boundary.field_correctness_status == "not_proven"`
3. `candidate_boundary.source_truth_status == "not_proven"`
4. `candidate_boundary.parser_replacement_authorized == False`
5. `candidate_boundary.readiness_status == "not_ready"`

Violation of any invariant raises `ValueError` at the `CandidateBoundaryStatus` constructor (already enforced by S1).

---

## 5. Processor Dispatch Rule

### 5.1 Current Dispatch

`FundProcessorRegistry.resolve()` iterates registrations by `(-priority, order)` and calls `processor.supports(context)`. The first `True` wins.

### 5.2 S3 Scope: Admission Helper Only

S3 does not change the registry's dispatch algorithm or `FundDataExtractor.extract()` behavior. S3 defines:

1. **`FundDisclosureDocumentIntermediate` protocol** in `contracts.py` — the contract for objects that may enter the processor boundary.
2. **`fund_disclosure_dispatch.py`** — admission helper that validates intermediate conformance and computes admission decisions. See §7 for exact function signatures.
3. **No-live tests** proving admission logic, failure taxonomy projection, and no-leak behavior.

Concrete processor registration and `FundDataExtractor` facade integration are **deferred to a later gate**. The existing `ActiveFundAnnualProcessor.supports()` check (`context.intermediate_kind == "parsed_annual_report.v1"`) remains unchanged.

### 5.3 Unsupported Handling

When no processor `supports()` the dispatch key:
- `resolve()` raises `UnsupportedFundProcessorError` (existing behavior).
- S3 adds a no-live test proving that `fund_disclosure_document.v1` + `active_fund` with only `ActiveFundAnnualProcessor` registered raises `UnsupportedFundProcessorError` from the registry.
- The admission helper returns `DisclosureAdmissionDecision(admitted=False, gap_code="unsupported_intermediate", source_boundary="unsupported_intermediate", contract_status="unsupported")` when no concrete processor exists. This is a planning/contract assertion only — the admission helper is not called from `FundDataExtractor` in this slice.

---

## 6. Output Contract

### 6.1 StructuredFundDataBundle Projection

The output remains `StructuredFundDataBundle`. No new output type is introduced.

When a future `FundDisclosureDocumentProcessor` is implemented:
- It must produce `FundProcessorResult` with the same `field_families`, `gaps`, `anchors`, `source_provenance` and `contract_status` contract.
- `FundDataExtractor` maps `FundProcessorResult` to `StructuredFundDataBundle` through the existing `_build_bundle_from_processor_result()` path.

### 6.2 EvidenceAnchor / Provenance / Gap State

Every `FundFieldFamilyResult` must:
- Carry at least one `EvidenceAnchor` if `status` is `accepted` or `partial` (enforced by S1 `__post_init__`).
- Carry at least one `FundExtractionGap` if `status` is `missing` (enforced by S1 `__post_init__`).
- `EvidenceAnchor.source_kind` must be one of `annual_report`, `external_api`, `derived`. **No change to `EvidenceSourceKind` in this slice.** Candidate route identity is expressed via `FundExtractionSourceBoundary` (already includes `candidate_only`), `CandidateBoundaryStatus`, `FundExtractionGap.source_boundary`, candidate note/metadata, or processor-level provenance — not via public `EvidenceAnchor.source_kind`.

### 6.3 Fail-closed Categories

| Category | Result behavior |
|---|---|
| `field_family_missing` | `status="missing"`, `extraction_mode="missing"`, gap emitted |
| `field_family_partial` | `status="partial"`, `extraction_mode="direct"`, gap emitted |
| `evidence_anchor_missing` | `status="missing"` if required; gap emitted |
| `candidate_boundary_blocked` | `contract_status="blocked"`, all field families blocked |
| `candidate_only_not_source_truth` | Gap emitted; does not block but prevents promotion |
| `unsupported_intermediate` | `contract_status="unsupported"` |
| `unsupported_intermediate_kind` | `contract_status="unsupported"` |
| `identity_mismatch` | `contract_status="blocked"` |
| `integrity_error` | `contract_status="blocked"` |
| `schema_drift` | `contract_status="blocked"` |

---

## 7. `fund_disclosure_dispatch.py` Exact Definition

This file is a **pure processor-contract/admission-helper** module. It defines the failure taxonomy projection and intermediate admission validation. It does not implement fallback logic, concrete processor behavior, or repository/facade integration.

### 7.1 Exported Symbols

| Symbol | Kind | Description |
|---|---|---|
| `FAILURE_CLASS_ADMISSION_MAP` | `dict[AnnualReportSourceFailureCategory, tuple[FundExtractionGapCode, FundExtractionSourceBoundary, FundProcessorContractStatus]]` | Frozen mapping from failure category to (gap_code, source_boundary, contract_status) triple. See §4.3 for exact values. |
| `DisclosureAdmissionDecision` | `@dataclass(frozen=True, slots=True)` | Admission decision result. Fields: `admitted: bool`, `gap_code: FundExtractionGapCode | None`, `source_boundary: FundExtractionSourceBoundary | None`, `contract_status: FundProcessorContractStatus`. |
| `admit_disclosure_intermediate(intermediate: FundDisclosureDocumentIntermediate, dispatch_key: FundProcessorDispatchKey) -> DisclosureAdmissionDecision` | Function | Admission validation. See §7.2 for exact logic. |

### 7.2 `admit_disclosure_intermediate` Exact Logic

```python
def admit_disclosure_intermediate(
    intermediate: FundDisclosureDocumentIntermediate,
    dispatch_key: FundProcessorDispatchKey,
) -> DisclosureAdmissionDecision:
    """Validate a disclosure intermediate for processor admission.

    Checks:
    1. CandidateBoundaryStatus invariants (if present) — delegated to CandidateBoundaryStatus.__post_init__.
    2. failure_class projection to gap_code/source_boundary/contract_status.
    3. source_provenance presence (None → source_provenance_unsafe gap).

    Does NOT check:
    - Identity (fund_code/report_year) — that is the processor's responsibility.
    - Whether a concrete processor supports this intermediate — that is the registry's responsibility.
    - Fallback logic — not implemented in S3.
    """
```

Step-by-step logic:

1. If `intermediate.failure_class is not None`:
   a. Look up `FAILURE_CLASS_ADMISSION_MAP[intermediate.failure_class]` → `(gap_code, source_boundary, contract_status)`.
   b. Return `DisclosureAdmissionDecision(admitted=False, gap_code=gap_code, source_boundary=source_boundary, contract_status=contract_status)`.

2. If `intermediate.candidate_boundary is not None`:
   a. `CandidateBoundaryStatus.__post_init__` already enforces `candidate_only=True`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`, `parser_replacement_authorized=False`, `readiness_status="not_ready"`. Violation raises `ValueError`.
   b. Return `DisclosureAdmissionDecision(admitted=True, gap_code="candidate_boundary_blocked", source_boundary="candidate_only", contract_status="blocked")` — candidate intermediates are always blocked from production promotion.

3. If `intermediate.source_provenance is None`:
   a. Return `DisclosureAdmissionDecision(admitted=False, gap_code="source_provenance_unsafe", source_boundary="source_provenance_unsafe", contract_status="blocked")`.

4. Otherwise:
   a. Return `DisclosureAdmissionDecision(admitted=True, gap_code=None, source_boundary=None, contract_status="satisfied")`.

### 7.3 Identity / Schema / Integrity Failure Handling (Processor Responsibility)

Identity mismatch, schema drift, and integrity error detection are the **processor's responsibility**, not the admission helper's. When a concrete `FundDisclosureDocumentProcessor` is implemented (S4+):

- Identity mismatch (`fund_code` / `report_year`): emit `identity_mismatch` gap → mapped to `candidate_boundary_blocked` gap code, `candidate_only` source boundary, `blocked` contract status (via `FAILURE_CLASS_ADMISSION_MAP`).
- Schema drift: emit `schema_drift` gap → same mapping.
- Integrity error: emit `integrity_error` gap → same mapping.

The admission helper does **not** perform identity checks. The mapping in `FAILURE_CLASS_ADMISSION_MAP` defines the projection only.

### 7.4 No Fallback Logic in S3

`not_found` / `unavailable` map to `unsupported_intermediate` in S3 because no concrete processor exists. When a concrete processor is implemented (S4+), these failure classes may map to `partial` / `missing` with appropriate field-family gaps. That decision is deferred to the concrete processor gate.

---

## 8. Test Plan

All tests are **no-live** — they use test-local fakes/stubs, not production objects. No test requires `FundDataExtractor.extract()` to accept `fund_disclosure_document.v1` in this slice.

### 8.1 No-live Unit / Contract Tests

| # | Test file | Test case | What it proves |
|---|---|---|---|
| 1 | `test_fund_disclosure_dispatch.py` | `FundDisclosureDocumentIntermediate` protocol conformance for a test-local stub | Protocol is implementable by test-local objects |
| 2 | `test_fund_disclosure_dispatch.py` | `CandidateBoundaryStatus(candidate_only=False)` → `ValueError` | Fail-closed invariant |
| 3 | `test_fund_disclosure_dispatch.py` | `CandidateBoundaryStatus(parser_replacement_authorized=True)` → `ValueError` | Fail-closed invariant |
| 4 | `test_fund_disclosure_dispatch.py` | `CandidateBoundaryStatus(readiness_status="ready")` → `ValueError` | Fail-closed invariant |
| 5 | `test_fund_disclosure_dispatch.py` | `admit_disclosure_intermediate` with `failure_class="schema_drift"` → `admitted=False`, `gap_code="candidate_boundary_blocked"`, `source_boundary="candidate_only"`, `contract_status="blocked"` | Failure taxonomy projection |
| 6 | `test_fund_disclosure_dispatch.py` | `admit_disclosure_intermediate` with `failure_class="identity_mismatch"` → same as above | Failure taxonomy projection |
| 7 | `test_fund_disclosure_dispatch.py` | `admit_disclosure_intermediate` with `failure_class="integrity_error"` → same as above | Failure taxonomy projection |
| 8 | `test_fund_disclosure_dispatch.py` | `admit_disclosure_intermediate` with `failure_class="not_found"` → `admitted=False`, `gap_code="unsupported_intermediate"`, `source_boundary="unsupported_intermediate"`, `contract_status="unsupported"` | Failure taxonomy projection |
| 9 | `test_fund_disclosure_dispatch.py` | `admit_disclosure_intermediate` with `failure_class="unavailable"` → same as above | Failure taxonomy projection |
| 10 | `test_fund_disclosure_dispatch.py` | `admit_disclosure_intermediate` with `candidate_boundary` present → `admitted=True`, `gap_code="candidate_boundary_blocked"`, `contract_status="blocked"` | Candidate always blocked from promotion |
| 11 | `test_fund_disclosure_dispatch.py` | `admit_disclosure_intermediate` with `source_provenance=None` → `admitted=False`, `gap_code="source_provenance_unsafe"`, `contract_status="blocked"` | Provenance required |
| 12 | `test_fund_disclosure_dispatch.py` | `admit_disclosure_intermediate` with valid non-candidate intermediate → `admitted=True`, `gap_code=None`, `contract_status="satisfied"` | Happy path (no failure, no candidate) |
| 13 | `test_fund_disclosure_dispatch.py` | No public `EvidenceAnchor.source_kind` leakage: `admit_disclosure_intermediate` result never sets `EvidenceAnchor.source_kind` to `candidate_only`; `EvidenceSourceKind` remains `Literal["annual_report", "external_api", "derived"]` | No-leak: candidate route stays out of public anchor |
| 14 | `test_fund_disclosure_dispatch.py` | `FAILURE_CLASS_ADMISSION_MAP` covers all five canonical failure categories and uses only existing gap codes (`candidate_boundary_blocked`, `unsupported_intermediate`, `source_provenance_unsafe`) | No new gap codes introduced |
| 15 | `test_fund_disclosure_dispatch.py` | No import from `fund_agent/services/`, `fund_agent/ui/`, `fund_agent/host/`, `fund_agent/agent/`, `fund_agent/fund/documents/models.py` | Boundary isolation |
| 16 | `test_registry.py` | `fund_disclosure_document.v1` dispatch key raises `UnsupportedFundProcessorError` when only `ActiveFundAnnualProcessor` registered | Registry dispatch: no concrete processor yet |
| 17 | `test_registry.py` | Existing registry tests continue passing unchanged | Legacy registry behavior preserved |
| 18 | `test_registry.py` | Non-active fund type still uses legacy path (registry not involved) | Legacy path preservation |

### 8.2 Test-Local Stub (Not Exported)

Tests use a test-local `StubDisclosureIntermediate` that implements `FundDisclosureDocumentIntermediate`. This stub is **not** exported from any production module:

```python
# In tests/fund/processors/test_fund_disclosure_dispatch.py

@dataclass(frozen=True, slots=True)
class StubDisclosureIntermediate:
    """Test-local stub. Not exported. Not a production model."""

    document_kind: Literal["annual_report"] = "annual_report"
    fund_code: str = "004393"
    report_year: int = 2025
    intermediate_kind: str = "fund_disclosure_document.v1"
    source_provenance: PublicSourceProvenance | None = None
    candidate_boundary: CandidateBoundaryStatus | None = None
    failure_class: Literal[
        "not_found", "unavailable", "schema_drift",
        "identity_mismatch", "integrity_error", None
    ] = None
```

### 8.3 Legacy Path Preservation

- Existing `ActiveFundAnnualProcessor` tests (`test_active_annual_processor.py`) must continue passing without modification.
- Existing `test_registry.py` must continue passing.
- Existing `test_data_extractor.py` active-fund processor path tests must continue passing.
- Non-active fund legacy path must be unaffected.
- `EvidenceSourceKind` remains `Literal["annual_report", "external_api", "derived"]` — no change.
- `EvidenceAnchor.source_kind` remains `annual_report` / `external_api` / `derived` — no change.

### 8.4 No Service/UI/Host/renderer/quality-gate Direct Consumption

- No test in this slice calls `FundAnalysisService`, `render_template_report`, `run_quality_gate_for_bundle`, or any Host/Agent runner.
- No test imports from `fund_agent/services/`, `fund_agent/ui/`, `fund_agent/host/`, `fund_agent/agent/`.
- No test imports `FundDisclosureDocumentStub` from `fund_agent/fund/documents/models.py` (it does not exist there).

---

## 9. Residual Risks and Owners

| Residual | Owner | Next gate | Blocks release? |
|---|---|---|---|
| No concrete `FundDisclosureDocumentProcessor` implementation | Fund extractor owner | S4 implementation gate | Yes — S3 only defines the admission contract |
| `FundDisclosureDocument` full schema not implemented | Fund documents owner | Schema implementation gate | Yes — S3 only defines the intermediate protocol |
| `FundDataExtractor.extract()` does not admit `fund_disclosure_document.v1` | Fund extractor owner | Concrete processor gate | Yes — S3 does not modify the production facade |
| `eid_xbrl_html_render_candidate` processor not implemented | Fund documents/source owner | Future candidate processor gate | Yes |
| Non-active fund type processors (bond, index, QDII, FOF) | Fund extractor owner | Per-type processor gates | Yes |
| Candidate `field_correctness_status` remains `not_proven` | Evidence/review owner | Comparative evidence gate | Yes |
| Candidate `source_truth_status` remains `not_proven` | Evidence/review owner | Source truth gate | Yes |
| `parser_replacement_authorized` remains `False` | Controller | Baseline disposition gate | Yes |
| `readiness_status` remains `not_ready` | Release owner | Release readiness gate | Yes |
| `EvidenceSourceKind` unchanged (`annual_report` / `external_api` / `derived`) | — | — | No — correct boundary |
| `EvidenceAnchor.source_kind` unchanged | — | — | No — correct boundary |

---

## 10. Exact Validation Commands for the Future Implementation Gate

```bash
# 1. Focused processor tests (includes new test_fund_disclosure_dispatch.py)
uv run pytest tests/fund/processors/ -v --tb=short 2>&1

# 2. Full test suite (legacy preservation)
uv run pytest --tb=short -q 2>&1

# 3. Lint
uv run ruff check fund_agent/ tests/ 2>&1

# 4. Format
uv run ruff format --check fund_agent/ tests/ 2>&1

# 5. Git hygiene
git diff --check -- docs/reviews/extractor-projection-over-document-representation-plan-20260618.md 2>&1
```

---

## 11. Stop Condition for the Future Implementation Gate

The implementation gate passes when **all** of the following hold:

1. All existing tests pass without modification (legacy preservation).
2. New `test_fund_disclosure_dispatch.py` passes all 18 test cases.
3. New dispatch-key tests in `test_registry.py` pass (including `UnsupportedFundProcessorError` for `fund_disclosure_document.v1`).
4. `ruff check` and `ruff format --check` pass.
5. `git diff --check -- docs/reviews/extractor-projection-over-document-representation-plan-20260618.md` passes.
6. `CandidateBoundaryStatus` invariants are enforced at construction time (S1 already does this).
7. `FAILURE_CLASS_ADMISSION_MAP` covers all five canonical failure categories and maps to existing gap codes only.
8. `admit_disclosure_intermediate` returns correct `DisclosureAdmissionDecision` for all test cases.
9. `source_provenance_unsafe` gap is emitted when provenance is missing on candidate intermediates.
10. No new file imports from `fund_agent/services/`, `fund_agent/ui/`, `fund_agent/host/`, `fund_agent/agent/`.
11. No change to `EvidenceSourceKind` or `EvidenceAnchor.source_kind`.
12. No change to EID single-source policy, fallback behavior, provider defaults, repair budget, or readiness/release status.
13. No change to `FundDataExtractor.extract()` or production facade behavior.
14. `FundDisclosureDocumentStub` does not exist in `fund_agent/fund/documents/models.py`.

---

## Appendix A: Allowed Module/File Boundary Summary

```
fund_agent/fund/processors/contracts.py        — modify (add FundDisclosureDocumentIntermediate protocol)
fund_agent/fund/processors/fund_disclosure_dispatch.py  — NEW (admission helper, failure taxonomy projection)
tests/fund/processors/test_fund_disclosure_dispatch.py  — NEW (no-live contract tests, no-leak tests)
tests/fund/processors/test_registry.py         — modify (add dispatch-key tests for fund_disclosure_document.v1)
```

No other files are modified or created by this slice.

**Explicitly not modified**:
- `fund_agent/fund/documents/models.py` — no `FundDisclosureDocumentStub` added to production models
- `fund_agent/fund/data_extractor.py` — no facade modification in this slice
- `fund_agent/fund/extractors/models.py` — no `EvidenceSourceKind` change
- `tests/fund/test_data_extractor.py` — no facade-level tests in this slice
