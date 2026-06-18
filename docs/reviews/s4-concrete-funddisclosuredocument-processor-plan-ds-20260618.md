# S4 Concrete FundDisclosureDocument Processor Plan - 2026-06-18

Status: DRAFT_FOR_REVIEW
Verdict: PLAN_READY_NOT_READY

---

## 1. First-Principles Goal and Non-Goals

### Goal

Deliver a minimal concrete `FundDisclosureDocumentProcessor` that registers in `FundProcessorRegistry`, validates `dispatch_key` vs `intermediate` identity, consumes the S3 admission helper, and produces fail-closed `FundProcessorResult`. The processor skeleton closes the S3 residual "no concrete processor exists" without implementing any field-family extraction logic — extraction requires the `FundDisclosureDocument` schema, which is a separate gate.

### Non-Goals

- Does **not** implement `FundDisclosureDocument` schema (deferred to Fund documents schema gate).
- Does **not** implement field-family extraction from `FundDisclosureDocument` — S4 extract() returns fully-gapped result (all six field families = `missing`).
- Does **not** modify `FundDataExtractor.extract()` or any production facade (deferred to S5 facade integration gate).
- Does **not** modify `FundDocumentRepository`, source acquisition, PDF cache, fallback, or Docling/pdfplumber/EID HTML conversion.
- Does **not** expand `EvidenceSourceKind` or `EvidenceAnchor.source_kind`.
- Does **not** change EID single-source policy, provider defaults, repair budget, or readiness/release status.
- Does **not** declare source truth, parser replacement, field correctness, golden/readiness, or release. Release/readiness remains `NOT_READY`.
- Does **not** implement non-active fund type processors.

---

## 2. S4 Minimal Target: Concrete Processor Only, No Facade Integration

### Decision

| Question | Answer |
|---|---|
| Concrete processor vs only support/registration/detection? | **Concrete processor** — a class implementing `FundProcessorProtocol` with `supports()` and `extract()`. The `extract()` is a skeleton: it validates identity, consumes the admission helper, and returns a `FundProcessorResult` with fully-gapped field families (or blocked/unsupported contract status). It does NOT extract any actual field values from the intermediate. |
| Facade integration in S4 or deferred? | **Deferred to S5**. S4 processor is registered and resolvable via registry, but `FundDataExtractor.extract()` does not call it. The facade cannot consume `fund_disclosure_document.v1` without a loading path (how the intermediate enters the system), which depends on the `FundDisclosureDocument` schema and repository integration — both separate gates. |

### Rationale

1. The existing `FundDataExtractor.extract()` receives `fund_code` and `report_year`, loads a `ParsedAnnualReport` via `FundDocumentRepository`, and dispatches to `parsed_annual_report.v1` processor. There is no `FundDisclosureDocument` loading path.
2. Adding a loading path requires either modifying `FundDocumentRepository` (forbidden in S4) or creating a separate entry point.
3. The `FundDisclosureDocument` schema is not yet implemented. Without it, even if the facade routed to the new processor, the intermediate object wouldn't carry extractable content.
4. S4 delivers the processor as a **discoverable, registered, identity-validating artifact** that can be tested independently. S5 will handle facade routing.

---

## 3. Code-Generation Plan

### 3.1 Write Set

Implementation worker writes these files:

| File | Action | Purpose |
|---|---|---|
| `fund_agent/fund/processors/fund_disclosure_processor.py` | **New** | Concrete `FundDisclosureDocumentProcessor`: `processor_id`, `priority`, `supports()`, `extract()` |
| `fund_agent/fund/processors/registry.py` | **Modify** | `create_default()` registers the new processor alongside `ActiveFundAnnualProcessor` |
| `tests/fund/processors/test_fund_disclosure_processor.py` | **New** | No-live focused tests for processor registration, identity validation, admission consumption, fail-closed extract |
| `tests/fund/processors/test_registry.py` | **Modify** | Reverse the S3 unsupported test: after S4, default registry now supports `fund_disclosure_document.v1` |
| `fund_agent/fund/README.md` | **Modify** | Fund package change triggers README sync per `AGENTS.md`; add S4 current-implementation entry. No source truth/readiness/parser replacement claim. |

Controller bookkeeping only (NOT implementation worker write set):

| File | Owner | Purpose |
|---|---|---|
| `docs/implementation-control.md` | Controller | Advance gate to S4 implementation evidence; record accepted artifacts |
| `docs/current-startup-packet.md` | Controller | Update current active gate pointer |

Unchanged (explicitly confirmed no edits needed):

| File | Reason |
|---|---|
| `tests/README.md` | No test convention or layer changes |

### 3.2 Forbidden Files

| File | Reason |
|---|---|
| `fund_agent/fund/data_extractor.py` | Facade integration deferred to S5 |
| `fund_agent/fund/documents/models.py` | No `FundDisclosureDocument` schema implementation |
| `fund_agent/fund/extractors/models.py` | No `EvidenceSourceKind` expansion |
| `fund_agent/fund/processors/fund_disclosure_dispatch.py` | S3 admission helper is stable; no behavioral change needed |
| `fund_agent/fund/processors/contracts.py` | S3 contracts are stable; no new types needed |
| `fund_agent/fund/documents/candidates/` | Candidate harness is not production; processor does not import it |
| Service/UI/Host/Agent/renderer/quality-gate code | Out of Fund layer scope |

### 3.3 Processor Class Definition

```python
# fund_agent/fund/processors/fund_disclosure_processor.py

class FundDisclosureDocumentProcessor:
    """FundDisclosureDocument 中间态 processor（S4 skeleton）。

    本 processor 只做：注册、身份校验、S3 admission 判定消费、fail-closed extract。
    字段族提取在 FundDisclosureDocument schema gate 完成前全部返回 missing。
    不读取 FundDocumentRepository、PDF/cache/source helper、Docling、network、
    provider、LLM、Service/UI/Host、renderer 或 quality gate。
    """

    processor_id: Final[str] = "fund_disclosure_document.fund_disclosure_document.v1"
    priority: Final[int] = 50
    output_schema_version: Final[str] = "fund_processor_result.v1"

    def supports(self, context: FundProcessorDispatchKey) -> bool:
        """仅 fund_disclosure_document.v1 + active_fund + annual_report 返回 True。

        不与 parsed_annual_report.v1 竞争：checked intermediate_kind 精确匹配。
        """
        return (
            context.fund_type == "active_fund"
            and context.report_type == "annual_report"
            and context.intermediate_kind == "fund_disclosure_document.v1"
            and context.processor_goal == "template_chapters_1_6_minimum_field_families"
        )

    def extract(self, input_data: FundProcessorInput) -> FundProcessorResult:
        """执行 admission 判定与 identity 校验；字段抽取 deferred 到 schema gate。"""
        ...
```

### 3.4 extract() Exact Logic

Steps executed in order inside `extract()`:

1. **Supports guard**: If `not self.supports(input_data.context)`, return `blocked` result with `unsupported_intermediate` gap. (Mirrors ActiveFundAnnualProcessor pattern.)

2. **Intermediate type guard**: If `input_data.intermediate` does not satisfy `isinstance(intermediate, FundDisclosureDocumentIntermediate)`, return `blocked` result with `input_type_mismatch` gap.

3. **Identity validation** (closes S3 residual "dispatch_key identity cross-check deferred"):

   Four identity fields checked in order. Every mismatch returns a `blocked` `FundProcessorResult` with `contract_status="blocked"`. The gap code and source boundary are mapped per mismatch category using **only existing `FundExtractionGapCode` and `FundExtractionSourceBoundary` values** (no `identity_mismatch` — that value is not in the current contract):

   | Mismatch field | `gap_code` | `source_boundary` | Rationale |
   |---|---|---|---|
   | `intermediate_kind` | `input_type_mismatch` | `unsupported_intermediate` | Type-boundary violation: intermediate claims a different intermediate kind than dispatch key. Mirrors `ActiveFundAnnualProcessor` isinstance guard pattern. |
   | `document_kind` | `unsupported_report_type` | `unsupported_report_type` | Report type boundary violation: intermediate claims a different report type. |
   | `fund_code` | `unsupported_intermediate` | `unsupported_intermediate` | This intermediate serves a different fund than requested. |
   | `report_year` | `unsupported_intermediate` | `unsupported_intermediate` | This intermediate serves a different year than requested. |

   Each mismatch produces its own result with the mapped gap. The specific mismatch detail (expected vs actual) goes into `gap.message`. All four checks are fail-closed; no fallback.

4. **Admission helper invocation**: Call `admit_disclosure_intermediate(intermediate, dispatch_key)` from S3. Map the result:

   | Admission Decision | Processor Action |
   |---|---|
   | `admitted=True, contract_status="satisfied"` | Produce fully-gapped `FundProcessorResult` (all 6 field families = `missing` with `field_family_missing` gaps). `contract_status="missing"`. |
   | `admitted=True, contract_status="blocked"` (candidate_boundary) | Produce fully-gapped `FundProcessorResult`. `contract_status="blocked"`. Candidate boundary gap carried into result. |
   | `admitted=False` (failure_class or missing provenance) | Return `blocked` result mapped from admission decision's `gap_code`/`source_boundary`/`contract_status`. |

5. **KeyError handling** (closes S3 residual "raw KeyError"): Wrap the `admit_disclosure_intermediate` call in a try/except that catches `KeyError` and converts it to a `blocked` `FundProcessorResult` with `gap_code="unsupported_intermediate"`, message describing the unrecognized failure class, `source_boundary="unsupported_intermediate"`, `contract_status="unsupported"`. This preserves fail-closed while replacing raw `KeyError` with a stable business result.

   **Decision**: The S3 admission helper's `KeyError` contract is preserved (not modified). The processor wraps it, so the processor's caller never sees raw `KeyError`. The admission helper itself stays unchanged — it still raises `KeyError` on non-canonical input, which remains a documented fail-closed contract for direct callers.

6. **Satisfied path — fully-gapped result**: When admission returns satisfied, the processor produces a `FundProcessorResult` where:
   - All six field families (`product_essence.v1` through `core_risk.v1`) have `status="missing"`, `extraction_mode="missing"`, empty `value={}`, empty `anchors=()`, one gap with `gap_code="field_family_missing"`.
   - `contract_status="missing"`.
   - Result-level `gaps=()` — per-family gaps stay in field families (enforced by S1 `__post_init__`).
   - `source_provenance` from `intermediate.source_provenance`.
   - `candidate_boundary` from `intermediate.candidate_boundary` (None for non-candidate satisfied path).

### 3.5 Registry Registration

Modify `FundProcessorRegistry.create_default()`:

```python
@classmethod
def create_default(cls) -> "FundProcessorRegistry":
    from fund_agent.fund.processors.active_annual import ActiveFundAnnualProcessor
    from fund_agent.fund.processors.fund_disclosure_processor import (
        FundDisclosureDocumentProcessor,
    )

    registry = cls()
    registry.register(ActiveFundAnnualProcessor)        # priority=100
    registry.register(FundDisclosureDocumentProcessor)   # priority=50
    return registry
```

**Priority rationale**: `ActiveFundAnnualProcessor` at priority 100, `FundDisclosureDocumentProcessor` at priority 50. Since their `supports()` checks are mutually exclusive (different `intermediate_kind`), priority ordering doesn't affect correctness. The lower priority explicitly signals "not the primary production path." If both were somehow eligible (e.g., future registry with overlapping intermediate kinds), `ActiveFundAnnualProcessor` would win.

**S3 test reversal**: The S3 test `test_registry_default_does_not_support_fund_disclosure_document_intermediate` that asserts `UnsupportedFundProcessorError` for `fund_disclosure_document.v1` must be updated. The new test asserts that `registry.resolve(_fund_disclosure_dispatch_key())` returns a `FundDisclosureDocumentProcessor` instance.

### 3.6 Identity Validation Detailed Contract

Identity checks are placed **before** the admission helper call: a wrong intermediate (e.g., a `parsed_annual_report.v1` intermediate passed with a `fund_disclosure_document.v1` dispatch key) must fail on identity before entering admission logic.

Each mismatch returns a `blocked` `FundProcessorResult` mapping to **only existing `FundExtractionGapCode` and `FundExtractionSourceBoundary` values** (the string `"identity_mismatch"` is not in `FundExtractionGapCode` and must not be used):

| Field | dispatch_key attr | intermediate attr | `gap_code` | `source_boundary` |
|---|---|---|---|---|
| Intermediate kind | `context.intermediate_kind` | `intermediate_kind` | `input_type_mismatch` | `unsupported_intermediate` |
| Report type | `context.report_type` | `document_kind` | `unsupported_report_type` | `unsupported_report_type` |
| Fund code | `context.fund_code` | `fund_code` | `unsupported_intermediate` | `unsupported_intermediate` |
| Report year | `context.document_year` | `report_year` | `unsupported_intermediate` | `unsupported_intermediate` |

All four mismatch paths set `contract_status="blocked"`. Specific mismatch detail (expected vs actual) goes into `gap.message`. Fail-closed; no fallback.

### 3.7 EvidenceAnchor / Source Kind

No change. The processor produces `EvidenceAnchor` objects only through the existing contract path. Candidate route identity is expressed via `CandidateBoundaryStatus`, `FundExtractionGap.source_boundary`, and `FundProcessorResult.candidate_boundary` — never via `EvidenceAnchor.source_kind`.

### 3.8 Repository / Source / Parser

No change. The processor does not import `FundDocumentRepository`, source helpers, PDF cache, Docling, pdfplumber, or EID HTML render modules. It only reads what is passed via `FundProcessorInput`.

---

## 4. Test Matrix

All tests are no-live. Test-local stubs are used; no production `FundDisclosureDocument` object is created. No test calls `FundDataExtractor.extract()`.

### 4.1 Focused Tests in `test_fund_disclosure_processor.py`

| # | Test | What It Proves |
|---|---|---|
| 1 | `test_processor_registered_in_default_registry` | `create_default()` includes `FundDisclosureDocumentProcessor`; `registry.resolve(fund_disclosure_dispatch_key)` returns instance with correct `processor_id` |
| 2 | `test_supports_fund_disclosure_document_v1` | `supports()` returns `True` for active_fund + annual_report + fund_disclosure_document.v1 |
| 3 | `test_supports_rejects_parsed_annual_report_v1` | `supports()` returns `False` for parsed_annual_report.v1 — no shadowing of ActiveFundAnnualProcessor |
| 4 | `test_supports_rejects_non_active_fund_type` | `supports()` returns `False` for non-active fund types |
| 5 | `test_supports_rejects_non_annual_report` | `supports()` returns `False` for non-annual_report types |
| 6 | `test_extract_rejects_wrong_intermediate_type` | Passing `ParsedAnnualReport` as intermediate → blocked result with `input_type_mismatch` |
| 7 | `test_extract_rejects_identity_mismatch_fund_code` | dispatch_key.fund_code != intermediate.fund_code → blocked, `gap_code="unsupported_intermediate"`, `source_boundary="unsupported_intermediate"`, `contract_status="blocked"` |
| 8 | `test_extract_rejects_identity_mismatch_report_year` | dispatch_key.document_year != intermediate.report_year → blocked, `gap_code="unsupported_intermediate"`, `source_boundary="unsupported_intermediate"`, `contract_status="blocked"` |
| 9 | `test_extract_rejects_identity_mismatch_document_kind` | dispatch_key.report_type != intermediate.document_kind → blocked, `gap_code="unsupported_report_type"`, `source_boundary="unsupported_report_type"`, `contract_status="blocked"` |
| 10 | `test_extract_rejects_identity_mismatch_intermediate_kind` | dispatch_key.intermediate_kind != intermediate.intermediate_kind → blocked, `gap_code="input_type_mismatch"`, `source_boundary="unsupported_intermediate"`, `contract_status="blocked"` |
| 11 | `test_extract_blocks_on_failure_class_schema_drift` | intermediate with `failure_class="schema_drift"` → blocked result via admission helper |
| 12 | `test_extract_blocks_on_missing_source_provenance` | intermediate with `source_provenance=None` → blocked result via admission helper |
| 13 | `test_extract_admits_candidate_boundary_but_returns_blocked` | candidate intermediate → `contract_status="blocked"`, all field families missing |
| 14 | `test_extract_satisfied_returns_fully_gapped_result` | valid non-candidate intermediate → `contract_status="missing"`, 6 field families all `status="missing"` |
| 15 | `test_extract_satisfied_result_preserves_source_provenance` | `result.source_provenance` == `intermediate.source_provenance` |
| 16 | `test_extract_satisfied_result_preserves_candidate_boundary_none` | Non-candidate intermediate → `result.candidate_boundary is None` |
| 17 | `test_extract_candidate_boundary_result_preserves_candidate_boundary` | Candidate intermediate → `result.candidate_boundary` is the `CandidateBoundaryStatus` object |
| 18 | `test_extract_keyerror_on_invalid_failure_class_is_caught` | Admission helper raises `KeyError` → processor catches it, returns blocked result (not raw KeyError) |
| 19 | `test_extract_result_gaps_are_cross_family_only` | Result-level `gaps` do not carry per-family gap codes (S1 invariant) |
| 20 | `test_extract_unsupported_context_returns_blocked` | dispatch_key with wrong fund_type → blocked via supports guard |
| 21 | `test_processor_does_not_import_forbidden_boundaries` | AST check: no imports from services/ui/host/agent/documents.models/candidates |

### 4.2 Modified Tests in `test_registry.py`

| # | Test | Change |
|---|---|---|
| 1 | `test_registry_default_does_not_support_fund_disclosure_document_intermediate` | **Remove or invert**: after S4, default registry does support this dispatch key. Replace with test that resolution succeeds and returns correct processor_id. |
| 2 | All existing registry tests | Must continue passing unchanged (legacy preservation). |

### 4.3 Legacy Preservation

- `tests/fund/processors/test_active_annual_processor.py` — all 9 tests continue passing.
- `tests/fund/processors/test_fund_disclosure_dispatch.py` — all 16 tests continue passing.
- `tests/fund/processors/test_registry.py` — 6 of 7 existing tests continue passing; 1 replaced.
- `tests/fund/test_data_extractor.py` — all active-fund processor path tests continue passing.
- `EvidenceSourceKind` unchanged; `EvidenceAnchor.source_kind` unchanged.
- No test imports from Service/UI/Host/Agent or calls `FundDataExtractor.extract()`.

---

## 5. Validation Commands

```bash
# 1. Focused processor tests
uv run pytest tests/fund/processors/ -v --tb=short

# 2. Full test suite (legacy preservation)
uv run pytest --tb=short -q

# 3. Lint
uv run ruff check fund_agent/ tests/

# 4. Format (slice files only)
uv run ruff format --check \
  fund_agent/fund/processors/fund_disclosure_processor.py \
  fund_agent/fund/processors/registry.py \
  tests/fund/processors/test_fund_disclosure_processor.py \
  tests/fund/processors/test_registry.py

# 5. Git hygiene
git diff --check
```

---

## 6. Stop Condition

The S4 implementation gate passes when **all** of the following hold:

1. All existing tests pass without modification (except the S3 unsupported test that gets replaced).
2. New `test_fund_disclosure_processor.py` passes all 21 test cases.
3. Updated `test_registry.py` passes: default registry resolves `fund_disclosure_document.v1` to `FundDisclosureDocumentProcessor`.
4. `ruff check` passes for all changed files.
5. Focused `ruff format --check` passes for the 4 changed files.
6. `git diff --check` passes.
7. `FundDisclosureDocumentProcessor` is registered in `create_default()` at priority 50.
8. `supports()` correctly discriminates `fund_disclosure_document.v1` from `parsed_annual_report.v1`.
9. Identity validation fails closed on any of the four identity fields, each mapped to its specified existing `FundExtractionGapCode` (`input_type_mismatch`, `unsupported_report_type`, or `unsupported_intermediate`). No test asserts the non-existent value `identity_mismatch`.
10. Admission helper is consumed; all four admission outcomes map to correct `FundProcessorResult`.
11. `KeyError` from admission helper is caught and converted to stable business result.
12. Satisfied admission path produces `FundProcessorResult` with exactly 6 field families, all `status="missing"`.
13. No new file imports from `fund_agent/services/`, `fund_agent/ui/`, `fund_agent/host/`, `fund_agent/agent/`, `fund_agent/fund/documents/models.py`, or `fund_agent/fund/documents/candidates/`.
14. No change to `EvidenceSourceKind`, `EvidenceAnchor.source_kind`, `FundDataExtractor.extract()`, repository behavior, source policy, or readiness/release status.
15. Release/readiness remains `NOT_READY`.

---

## 7. Documentation / Control Sync Ownership

### Implementation Worker (part of S4 write set)

- `fund_agent/fund/README.md`: Add S4 entry under "当前实现" section — `FundDisclosureDocumentProcessor` is registered, validates identity, consumes admission helper; field extraction is fully-gapped pending schema gate; facade integration deferred to S5. No source truth/readiness/parser replacement claim. Triggered by `AGENTS.md` rule: `fund_agent/fund/` changes require README sync.

### Implementation Worker — Explicitly Unchanged

- `tests/README.md`: No test convention or layer changes in S4. Not part of write set.

### Controller Bookkeeping Only (NOT implementation worker write set)

- `docs/implementation-control.md`: Controller advances gate to S4 implementation evidence and records accepted artifacts after implementation acceptance. Implementation worker does not edit this file.
- `docs/current-startup-packet.md`: Controller updates current active gate pointer after implementation acceptance. Implementation worker does not edit this file.

---

## 8. Residual Owners

| Residual | Owner | Destination Gate | Blocks Release? |
|---|---|---|---|
| `FundDisclosureDocument` schema not implemented | Fund documents owner | FundDisclosureDocument Schema Implementation Gate | Yes — without schema, processor cannot extract fields |
| `FundDataExtractor.extract()` facade not consuming `fund_disclosure_document.v1` | Fund extractor owner | S5 Facade Integration Gate | Yes — processor is registered but unreachable from production facade |
| Field-family extraction from `FundDisclosureDocument` intermediate | Fund extractor owner | Post-schema extraction gate (S6+) | Yes — S4 extract() returns fully-gapped result |
| Non-active fund type processors (bond, index, QDII, FOF) | Fund extractor owner | Per-type processor gates | Yes |
| Candidate route `field_correctness_status` / `source_truth_status` remain `not_proven` | Evidence/review owner | Future evidence gates | Yes |
| `parser_replacement_authorized` remains `False` | Controller | Baseline disposition gate | Yes |
| Full-repo ruff format baseline drift | Formatting owner | Separate formatting-baseline gate | No (accepted residual) |
| `EvidenceSourceKind` unchanged | — | — | No |
| `EvidenceAnchor.source_kind` unchanged | — | — | No |
| Release/readiness `NOT_READY` | Release owner | Future release readiness gate | N/A — current state |

---

## 9. Relation to Future Gates

```
S3: Admission Helper (accepted)
  │
  ▼
S4: Concrete Processor Registration + Identity + Admission Consumption (this plan)
  │
  ▼
FundDisclosureDocument Schema Implementation Gate (separate owner)
  │
  ▼
S5: FundDataExtractor Facade Integration for fund_disclosure_document.v1
  │
  ▼
S6+: Field-Family Extraction from FundDisclosureDocument
```

S4 is intentionally bounded. It delivers a registered, identity-validating processor. The next two gates (schema + facade) are prerequisites for actual field extraction. This ordering avoids building extraction logic against an undefined schema.
