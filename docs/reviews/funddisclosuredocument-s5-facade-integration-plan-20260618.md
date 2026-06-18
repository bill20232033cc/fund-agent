# FundDisclosureDocument S5 Facade Integration Plan

Verdict: `S5_FACADE_INTEGRATION_PLAN_READY_NOT_READY`

Date: 2026-06-18

Gate: `FundDisclosureDocument S5 Facade Integration Planning Gate`

Role: planning worker only

Release/readiness remains `NOT_READY`.

## Scope and Inputs

This plan is code-generation-ready for a future S5 implementation gate. It decides the exact
contract for whether and how `FundDataExtractor.extract()` may consume
`fund_disclosure_document.v1` through the Fund Processor/Extractor boundary.

Inputs read:

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/funddisclosuredocument-candidate-source-no-live-final-closeout-controller-judgment-20260618.md`
- `docs/reviews/funddisclosuredocument-candidate-source-no-live-implementation-plan-20260618.md`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/processors/registry.py`
- `fund_agent/fund/processors/fund_disclosure_dispatch.py`
- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `fund_agent/fund/processors/contracts.py`
- `fund_agent/fund/documents/candidates/fund_disclosure_document.py`
- `fund_agent/fund/source_provenance.py`
- `tests/fund/test_data_extractor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_dispatch.py`
- `tests/fund/documents/test_docling_no_consumption_guards.py`

## Current Code Facts

1. `FundDataExtractor.extract()` currently loads a `ParsedAnnualReport` through
   `FundDocumentRepository.load_annual_report()`, validates request/report identity before NAV, runs
   `extract_profile(report)`, classifies fund type from `basic_identity`, and only routes exact
   `active_fund` through `FundProcessorRegistry`.
2. Current default active-fund route is:
   `active_fund + annual_report + parsed_annual_report.v1` -> `ActiveFundAnnualProcessor` ->
   `StructuredFundDataBundle`.
3. Non-active or unclassified funds still use the direct legacy residual path. That path is current
   behavior, not a precedent for candidate fallback.
4. `FundProcessorRegistry.create_default()` already registers `FundDisclosureDocumentProcessor`
   after `ActiveFundAnnualProcessor`.
5. `FundDisclosureDocumentProcessor` supports only
   `active_fund + annual_report + fund_disclosure_document.v1 +
   template_chapters_1_6_minimum_field_families`.
6. `FundDisclosureDocumentProcessor` is currently a S4 skeleton: it validates input type, identity and
   S3 admission, then returns all six field families as missing. It does not implement S6+ field
   extraction.
7. Concrete `FundDisclosureDocument` is candidate-only by construction: `candidate_only=True`,
   `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`,
   `parser_replacement_authorized=False`, `readiness_status="not_ready"`.
8. `FundDisclosureDocument`, Docling, pdfplumber full JSON and EID HTML render are not source truth,
   parser replacement, full field correctness proof, golden/readiness proof or direct upper-layer
   inputs.

## Objective

S5 exists because S3/S4 proved the Processor/Extractor admission and registered processor surface,
and Candidate Source No-live proved a concrete candidate-internal schema/failure mapping, but the P1
facade still has no controlled way to exercise `fund_disclosure_document.v1`.

First-principles objective:

- prove `FundDataExtractor.extract()` can route a supplied, already-constructed
  `FundDisclosureDocumentIntermediate` through `FundProcessorRegistry`;
- preserve the current production default path through `parsed_annual_report.v1`;
- keep candidate internals behind Fund Processor/Extractor, never behind Service/UI/Host/renderer/
  quality-gate/LLM prompt/template consumption;
- fail closed for every candidate/source/provenance/identity/processor mismatch;
- produce no source-truth, parser-replacement, full-correctness, readiness or release claim.

## Non-goals / Hard Boundaries

This S5 future implementation must not:

- implement S6+ actual field-family extraction from `FundDisclosureDocument`;
- change `FundDocumentRepository`, source acquisition, cache, parser, fallback or EID policy;
- make `fund_disclosure_document.v1` the default production path;
- bypass `ParsedAnnualReport` identity and fund-type classification;
- expand `EvidenceSourceKind`, `EvidenceAnchor`, `AnnualReportSourceFailureCategory` or public source
  provenance literals;
- import concrete candidate modules in Service/UI/Host/renderer/quality gate/LLM prompt/template;
- import concrete candidate modules in `fund_agent/fund/data_extractor.py`; use only the
  `FundDisclosureDocumentIntermediate` Protocol from `fund_agent.fund.processors.contracts`;
- allow direct upper-layer consumption of sections, tables, cells, raw HTML, raw Markdown, raw JSON,
  Docling output, pdfplumber full JSON or EID HTML render;
- turn candidate selected-fact evidence into field correctness, source truth, golden/readiness or
  release proof;
- run live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference review/provider/LLM
  commands.

## Proposed Future Implementation Write Set

Minimal implementation files:

| File | Required change |
|---|---|
| `fund_agent/fund/data_extractor.py` | Add explicit keyword-only `disclosure_intermediate: FundDisclosureDocumentIntermediate \| None = None` to `FundDataExtractor.extract()`. Add private helper for active-fund disclosure routing. Validate identities, resolve registry with `fund_disclosure_document.v1`, handle processor statuses fail-closed, and project only processor output through existing bundle projection. Do not import `fund_agent.fund.documents.candidates.*`. |
| `tests/fund/test_data_extractor.py` | Add S5 facade tests for default parsed path preservation, explicit opt-in disclosure routing, identity mismatch, source failure, unsafe provenance, candidate boundary, unsupported fund type/report type, registry resolution failure, processor result mismatch, missing success path and no legacy fallback. Test fixtures may use local Protocol stubs and local marker processors. This is also the exact location for the AST guard proving `fund_agent/fund/data_extractor.py` imports `FundDisclosureDocumentIntermediate` only from processor contracts and does not import `fund_agent.fund.documents.candidates`. |
| `fund_agent/fund/README.md` | Required by repository rule if `fund_agent/fund/data_extractor.py` is changed. Update only current Fund package boundary wording: S5 adds explicit internal/test opt-in facade routing for `FundDisclosureDocumentIntermediate`; default production path and candidate-only `NOT_READY` remain unchanged. |

Forbidden implementation files:

- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/sources.py`
- `fund_agent/fund/documents/models.py`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/processors/contracts.py`
- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `fund_agent/fund/processors/fund_disclosure_dispatch.py`
- `fund_agent/fund/documents/candidates/fund_disclosure_document.py`
- `fund_agent/fund/documents/candidates/fund_disclosure_failure_mapping.py`
- Service/UI/Host/Agent/renderer/quality-gate/provider/LLM files
- root README, design/control/startup docs, PR body and unrelated review artifacts

If implementation requires touching any forbidden file, stop with `BLOCKED_NOT_READY`.

## Contract Decisions

### 1. Default Route

`FundDataExtractor.extract(fund_code, report_year, force_refresh=False)` with
`disclosure_intermediate=None` remains byte-for-behavior equivalent in route semantics:

1. load `ParsedAnnualReport` through `FundDocumentRepository`;
2. validate `report.key.fund_code` and `report.key.year`;
3. load NAV with current degraded-unavailable semantics;
4. classify fund type from `extract_profile(report).basic_identity`;
5. route exact `active_fund` via `parsed_annual_report.v1`;
6. route non-active/unclassified through current direct legacy residual path.

No default call may resolve `fund_disclosure_document.v1`.

### 2. Explicit Opt-in Route

Future implementation may add this exact public facade parameter:

```python
async def extract(
    self,
    fund_code: str,
    report_year: int,
    *,
    force_refresh: bool = False,
    disclosure_intermediate: FundDisclosureDocumentIntermediate | None = None,
) -> StructuredFundDataBundle:
```

This is an explicit typed parameter, not `extra_payload`. It is internal/test opt-in only. Service,
UI, Host, renderer, quality gate, LLM prompt and templates must not pass it in S5.

When `disclosure_intermediate` is provided:

1. Still load `ParsedAnnualReport` through `FundDocumentRepository`.
2. Validate loaded report identity against request before NAV.
3. Validate `disclosure_intermediate.fund_code == fund_code`,
   `disclosure_intermediate.report_year == report_year`,
   `disclosure_intermediate.document_kind == "annual_report"` and
   `disclosure_intermediate.intermediate_kind == "fund_disclosure_document.v1"` before NAV.
4. Classify fund type from the loaded `ParsedAnnualReport`, not from candidate content.
5. If classified fund type is not exact `active_fund`, fail closed and do not fall back to direct
   legacy path.
6. Build dispatch key:

```python
FundProcessorDispatchKey(
    fund_type="active_fund",
    report_type="annual_report",
    intermediate_kind="fund_disclosure_document.v1",
    source_kind="annual_report",
    document_year=report_year,
    fund_code=fund_code,
)
```

The `dispatch_key.source_kind` value is deliberately `"annual_report"` because the dispatch key
describes the report category routed through the Fund Processor/Extractor contract, not the concrete
candidate artifact provenance. Candidate provenance remains on
`disclosure_intermediate.source_provenance` and candidate identity fields such as
`FundDisclosureDocumentIdentity.source_kind == "eid_xbrl_html_render_candidate"`. Future processors
must not infer selected source, source truth, parser identity or candidate artifact kind from
`dispatch_key.source_kind`; they must read provenance only from the explicit provenance/candidate
fields in `FundProcessorInput`.

7. Resolve processor through the existing `FundProcessorRegistry`.
8. Pass only Protocol-visible data:

```python
FundProcessorInput(
    context=dispatch_key,
    intermediate=disclosure_intermediate,
    candidate_boundary=disclosure_intermediate.candidate_boundary,
    source_provenance=disclosure_intermediate.source_provenance,
)
```

9. Validate processor result identity with existing `_validate_processor_result_identity()`.
10. If `contract_status in ("unsupported", "blocked")`, raise `RuntimeError` and return no bundle.
11. If `contract_status in ("missing", "partial", "satisfied")`, compute
    `drawdown_metric` / `drawdown_metric_error` exactly as the current active path does by calling
    `_load_drawdown_metric_for_bond_fund()` with the loaded `ParsedAnnualReport` identity and the
    parsed-report classified fund type, then call `extract_bond_risk_evidence(report, ...)` on the
    loaded `ParsedAnnualReport`. For exact `active_fund` this should normally remain the existing
    non-bond missing field, but the helper must still preserve the current parameter contract.
12. Project through existing `_active_processor_result_to_bundle()` and preserve field-family
    missing semantics. The helper name is acceptable for S5 because this route remains exact
    `active_fund`; "active" names fund type, not intermediate kind.

### 3. Candidate-only Consequence

The concrete no-live `FundDisclosureDocument` currently carries `candidate_boundary` by default.
With the current S4 processor, that means real candidate input returns `contract_status="blocked"`.
Therefore S5 does not make concrete candidate documents produce usable production bundles.

The only S5 success-path bundle is for explicit opt-in test/admission harnesses or future
non-candidate-safe intermediates whose processor result is not blocked/unsupported. This is deliberate:
S5 tests facade routing, not field correctness.

### 4. Parsed Path Priority

`parsed_annual_report.v1` remains the default production path. `fund_disclosure_document.v1` never
preempts it by registry priority, default registry order, repository behavior or automatic discovery.
It is selected only by explicit `disclosure_intermediate` parameter.

## Failure / Fail-Closed Matrix

| Condition | Required S5 behavior |
|---|---|
| Loaded `ParsedAnnualReport` identity mismatches request | Raise `RuntimeError("Report identity mismatch...")` before NAV and before processor resolution. Existing behavior preserved. |
| `disclosure_intermediate` fund code/year/report type/intermediate kind mismatches request | Raise `RuntimeError` before NAV and before processor resolution. No fallback. |
| `disclosure_intermediate.failure_class == "identity_mismatch"` | Processor/admission returns blocked; facade raises `RuntimeError`. No bundle. |
| `failure_class == "schema_drift"` | Processor/admission returns blocked; facade raises `RuntimeError`. No bundle. |
| `failure_class == "integrity_error"` | Processor/admission returns blocked; facade raises `RuntimeError`. No bundle. |
| `failure_class == "unavailable"` | Processor/admission returns unsupported; facade raises `RuntimeError`. No parsed-path fallback for explicit disclosure route. |
| `failure_class == "not_found"` | Processor/admission returns unsupported; facade raises `RuntimeError`. No parsed-path fallback for explicit disclosure route. |
| `source_provenance is None` | Processor/admission returns blocked with `source_provenance_unsafe`; facade raises `RuntimeError`. |
| `candidate_boundary is not None` on concrete candidate | Current processor returns blocked; facade raises `RuntimeError`. Candidate-only is not promoted. |
| Classified fund type is not `active_fund` | Explicit disclosure route raises `RuntimeError` / unsupported route error; no direct legacy fallback. Default route without disclosure remains unchanged. |
| Report type unsupported | Dispatch/support failure; no bundle. |
| Registry cannot resolve `fund_disclosure_document.v1` | Propagate `UnsupportedFundProcessorError`; no fallback. |
| Processor result identity mismatches dispatch key | Existing `_validate_processor_result_identity()` raises `RuntimeError`; no bundle. |
| Processor returns `contract_status="blocked"` | Raise `RuntimeError`; no bundle. |
| Processor returns `contract_status="unsupported"` | Raise `RuntimeError`; no bundle. |
| Processor returns `contract_status="missing"` | Return a bundle only as explicit opt-in admission/test output; all missing fields remain `ExtractedField(value=None, anchors=(), extraction_mode="missing", note=...)`. |
| Source-failure-only document with no safe content | Raise through unsupported/blocked status; no fallback and no bundle. |

## Output Semantics

S5 does not authorize any new accepted structured field from `FundDisclosureDocument`.

For the explicit disclosure route, `StructuredFundDataBundle` may contain:

- `fund_code` and `report_year` from validated processor result identity;
- `source_provenance` from `disclosure_intermediate.source_provenance` only if processor result is
  not blocked/unsupported;
- fields projected from processor field families only when the processor returns
  `missing`, `partial` or `satisfied`;
- existing NAV degraded-unavailable semantics, but only after request/report/disclosure identity
  checks pass.
- `bond_risk_evidence` computed from the loaded `ParsedAnnualReport` with the same
  `_load_drawdown_metric_for_bond_fund()` and `extract_bond_risk_evidence()` path used by the
  current active processor route. This field is not sourced from `FundDisclosureDocument` in S5.
- non-processor-family residual fields that `_active_processor_result_to_bundle()` already reuses:
  `index_profile` from `profile_result.index_profile`, `bond_risk_evidence` from parsed-report bond
  risk extraction, and the existing product/core-risk fallback rule for `risk_characteristic_text`.

With the current S4 `FundDisclosureDocumentProcessor`, all six field families remain missing:

- `product_essence.v1`
- `return_attribution.v1`
- `manager_profile.v1`
- `investor_experience.v1`
- `current_stage.v1`
- `core_risk.v1`

Missing field families must be represented by the existing projection semantics:

- missing family -> `ExtractedField(value=None, anchors=(), extraction_mode="missing",
  note="field_family_absent:<field_name>")`;
- missing field in present family -> `ExtractedField(value=None, anchors=(),
  extraction_mode="missing", note="field_not_in_family:<field_family_id>:<field_name>")`;
- `portfolio_managers` is projected from `manager_profile.v1` when that family contains the field;
  otherwise it remains the existing missing `ExtractedField`;
- `risk_characteristic_text` is projected from `product_essence.v1` and may use the existing
  `core_risk.v1` fallback if the processor supplies that field; with current S4 missing families it
  remains missing;
- `index_profile` remains the current S2 residual from `ParsedAnnualReport` profile extraction and
  is not proof that FDD fields were accepted;
- `bond_risk_evidence` remains parsed-report-derived/default-missing as described above and is not
  proof that FDD risk fields were accepted;
- no fabricated anchors;
- no `EvidenceAnchor.source_kind` expansion;
- no candidate section/table/cell locator exposed in the bundle;
- no candidate value promoted as accepted field.

If a future S6+ processor adds real field-family extraction, that future gate must redefine accepted
field mapping, anchors and evidence projection. S5 does not.

## Import / Layering Boundaries

Allowed import in `fund_agent/fund/data_extractor.py`:

```python
from fund_agent.fund.processors.contracts import FundDisclosureDocumentIntermediate
```

Forbidden import in `fund_agent/fund/data_extractor.py`:

```python
from fund_agent.fund.documents.candidates...
import docling
```

Forbidden direct consumer imports:

- `fund_agent.services.*` -> candidate modules
- `fund_agent.ui.*` -> candidate modules
- `fund_agent.host.*` -> candidate modules
- `fund_agent.agent.*` -> candidate modules
- `fund_agent.fund.template.*` -> candidate modules
- `fund_agent.fund.audit.*` -> candidate modules
- `fund_agent.fund.extractors.*` -> candidate modules
- quality gate/report validation -> candidate modules

S5 may use local test stubs implementing `FundDisclosureDocumentIntermediate`. Production code must
depend on the Protocol, not the concrete schema.

## Test Matrix

Future implementation must add or update focused tests under `tests/fund/test_data_extractor.py`:

| Test | Acceptance expectation |
|---|---|
| `test_default_active_fund_still_uses_parsed_annual_report_processor_path()` | Existing marker processor for `parsed_annual_report.v1` still supplies bundle fields when `disclosure_intermediate=None`. |
| `test_default_extract_does_not_resolve_fund_disclosure_processor()` | Recording registry proves default route resolves `parsed_annual_report.v1`, not `fund_disclosure_document.v1`. |
| `test_explicit_disclosure_intermediate_routes_to_registry()` | Local Protocol stub plus local marker processor for `fund_disclosure_document.v1` returns marker fields through bundle projection. |
| `test_explicit_disclosure_intermediate_uses_protocol_not_candidate_import()` | AST check proves `data_extractor.py` imports no `fund_agent.fund.documents.candidates` module. |
| `test_explicit_disclosure_identity_mismatch_fails_before_nav()` | Mismatched disclosure fund/year raises before NAV provider call. |
| `test_explicit_disclosure_wrong_intermediate_kind_fails_before_nav()` | Non-`fund_disclosure_document.v1` intermediate raises before NAV. |
| `test_explicit_disclosure_missing_provenance_fails_closed()` | Default registry + stub with `source_provenance=None` raises; no bundle. |
| `test_explicit_disclosure_candidate_boundary_fails_closed()` | Concrete candidate-like or stub `candidate_boundary` triggers blocked processor result and facade raises. |
| `test_explicit_disclosure_schema_drift_fails_closed()` | `failure_class="schema_drift"` raises; no parsed fallback. |
| `test_explicit_disclosure_identity_mismatch_failure_class_fails_closed()` | `failure_class="identity_mismatch"` raises; no bundle. |
| `test_explicit_disclosure_integrity_error_fails_closed()` | `failure_class="integrity_error"` raises; no bundle. |
| `test_explicit_disclosure_unavailable_fails_closed_no_parsed_fallback()` | `failure_class="unavailable"` raises even though parsed report is loadable. |
| `test_explicit_disclosure_not_found_fails_closed_no_parsed_fallback()` | `failure_class="not_found"` raises even though parsed report is loadable. |
| `test_explicit_disclosure_non_active_fund_raises_no_legacy_fallback()` | Index/bond/QDII/FOF parsed classification plus disclosure parameter raises and does not call the direct legacy path. |
| `test_default_non_active_without_disclosure_preserves_legacy_path()` | Same non-active fixture without `disclosure_intermediate` still returns the existing direct legacy bundle. This must be a separate test or a clearly separate assertion block from the explicit-disclosure failure case. |
| `test_explicit_disclosure_registry_resolution_failure_raises_no_fallback()` | Registry without any processor supporting `fund_disclosure_document.v1` raises `UnsupportedFundProcessorError`; parsed annual fallback is not attempted. |
| `test_explicit_disclosure_processor_result_identity_mismatch_fails_closed()` | Local FDD marker processor returns wrong identity; existing validator raises. |
| `test_explicit_disclosure_non_candidate_admitted_produces_missing_bundle()` | Non-candidate Protocol stub with `candidate_boundary=None`, `failure_class=None` and non-None `source_provenance` reaches the current S4 missing path and returns a bundle whose processor-family fields are missing `ExtractedField`s with no anchors and no candidate value. |
| `test_explicit_disclosure_missing_result_preserves_parsed_report_residual_fields()` | Missing disclosure processor result still preserves the planned non-processor-family semantics: `index_profile` from `profile_result`, `bond_risk_evidence` from parsed-report/default missing, `portfolio_managers` missing from `manager_profile.v1`, and `risk_characteristic_text` missing or core-risk fallback only. |

Existing suites that must remain passing:

- `tests/fund/test_data_extractor.py`
- `tests/fund/processors/test_registry.py`
- `tests/fund/processors/test_active_annual_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_dispatch.py`
- `tests/fund/documents/test_fund_disclosure_document.py`
- `tests/fund/documents/test_fund_disclosure_failure_mapping.py`
- `tests/fund/documents/test_docling_no_consumption_guards.py`

No live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference review/provider/LLM
test is authorized.

## Validation Commands

Focused first:

```bash
uv run pytest tests/fund/test_data_extractor.py \
  tests/fund/processors/test_fund_disclosure_processor.py \
  tests/fund/processors/test_fund_disclosure_dispatch.py \
  tests/fund/documents/test_docling_no_consumption_guards.py -q
```

Candidate/source boundary regression:

```bash
uv run pytest tests/fund/documents/test_fund_disclosure_document.py \
  tests/fund/documents/test_fund_disclosure_failure_mapping.py -q
```

Processor regression:

```bash
uv run pytest tests/fund/processors/ -q
```

Lint/format/diff:

```bash
uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py \
  tests/fund/documents/test_docling_no_consumption_guards.py
uv run ruff format --check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py \
  tests/fund/documents/test_docling_no_consumption_guards.py
git diff --check -- fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py \
  tests/fund/documents/test_docling_no_consumption_guards.py fund_agent/fund/README.md
```

Forbidden-diff checks:

```bash
git diff --name-only -- fund_agent/fund/documents/repository.py
git diff --name-only -- fund_agent/fund/documents/sources.py
git diff --name-only -- fund_agent/fund/documents/models.py
git diff --name-only -- fund_agent/fund/extractors/models.py
git diff --name-only -- fund_agent/fund/processors/contracts.py
git diff --name-only -- fund_agent/fund/processors/fund_disclosure_processor.py
git diff --name-only -- fund_agent/fund/processors/fund_disclosure_dispatch.py
git diff --name-only -- fund_agent/services fund_agent/ui fund_agent/host fund_agent/agent
```

Expected output for each forbidden-diff command: empty.

## Residual Risks and Owners

| Residual | Owner | Destination |
|---|---|---|
| S6+ actual field-family extraction from `FundDisclosureDocument` absent | Fund extractor owner + controller | Future S6+ field-family extraction planning gate |
| EvidenceAnchor projection strategy for candidate section/table/cell locators absent | Fund documents / extractor owner | Future EvidenceAnchor projection design/evidence gate |
| Source truth, full field correctness, raw XML/taxonomy proof, unit/date semantics and cross-year correctness unproven | Fund documents evidence owner | Separate evidence gates |
| Concrete candidate path remains blocked by candidate-only boundary | Fund extractor owner | Intentional S5 residual until source truth / field correctness gates |
| Non-active fund processors not implemented | Fund processor owner | Separate fund-type processor gates |
| Default production parser remains `parsed_annual_report.v1` path | Controller | Intentional boundary, not a defect |
| Release/readiness remains `NOT_READY` | Release owner / controller | Separate release/readiness gates |
| PR #23 remains draft/open | Maintainer / controller | Separate PR disposition gate |

## Implementation Worker Handoff

Future implementation worker may implement only the S5 explicit opt-in facade route described above.

Stop and report `BLOCKED_NOT_READY` if any condition occurs:

1. implementation needs to edit any forbidden file;
2. default `extract()` behavior changes when `disclosure_intermediate=None`;
3. `fund_disclosure_document.v1` becomes automatic/default production path;
4. concrete candidate internals are imported by `data_extractor.py` or any upper-layer consumer;
5. Service/UI/Host/renderer/quality gate/LLM prompt/template passes or consumes
   `disclosure_intermediate`;
6. candidate/source failure is silently downgraded to parsed annual fallback;
7. non-active explicit disclosure route falls back to direct legacy path;
8. blocked/unsupported processor result returns a bundle;
9. `EvidenceSourceKind`, `EvidenceAnchor`, source failure categories or repository/source behavior
   are changed;
10. output claims source truth, full correctness, parser replacement, golden/readiness or release;
11. any focused S5/S4/candidate no-consumption test fails.

Completion signal for implementation worker:

- code/tests/README limited to the future write set;
- focused tests pass;
- ruff check/format pass on touched files;
- `git diff --check` passes on touched files;
- forbidden-diff checks are empty;
- implementation evidence states `NOT_READY` and preserves all residual owners above.
