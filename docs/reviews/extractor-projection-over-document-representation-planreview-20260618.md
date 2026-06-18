# Extractor Projection Over Document Representation — Plan Review

> **Date**: 2026-06-18
> **Reviewer**: AgentDS (independent plan reviewer)
> **Target plan**: `docs/reviews/extractor-projection-over-document-representation-plan-20260618.md`
> **Gate**: Extractor Projection Over Document Representation Planning Gate
> **Classification**: standard; planning review
> **Posture**: adversarial

---

## Verdict

**PLAN_NEEDS_FIX_NOT_READY**

The plan is structurally sound in goal/non-goal definition and boundary awareness, but has three concrete issues that must be fixed before the plan is code-generation-ready:

1. **CRITICAL — `EvidenceSourceKind` production type pollution**: Adding `candidate_only` to the `EvidenceSourceKind` literal in `extractors/models.py` modifies a production type consumed by `EvidenceAnchor` in the active production extraction path. The plan classifies this risk as "No (additive)" (§9 residual table), which understates the hazard.
2. **HIGH — `FundDisclosureDocumentStub` placement**: Putting a candidate-only stub into `documents/models.py` (which holds production models `ParsedAnnualReport`, `DocumentKey`, etc.) blurs the production/candidate boundary.
3. **MEDIUM — `fund_disclosure_dispatch.py` scope ambiguity**: The plan describes this file as both "enforcing mapping" (§7) and "only the mapping contract" (§7末), creating implementation ambiguity.

---

## 1. Boundary Checks

### 1.1 FundDocumentRepository / Fund Processor-Extractor boundaries

**PASS** — The plan keeps all proposed changes within the Fund/Agent layer (`fund_agent/fund/processors/`, `fund_agent/fund/documents/`, `fund_agent/fund/data_extractor.py`). It does not propose touching `FundDocumentRepository`, Service, UI, Host, renderer, or quality gate.

The plan explicitly states (Non-goals §1):
- Does not replace production parser
- Does not expose candidate representations to Service/UI/Host/renderer/quality gate/LLM prompt
- Does not authorize field_correctness_status / source_truth_status beyond `not_proven`

The test plan (§8.4) explicitly prohibits importing from Service/UI/Host/Agent.

### 1.2 Candidate object promotion to source truth or parser replacement

**PASS** — The plan correctly enforces `CandidateBoundaryStatus` invariants (§4.4) and keeps all statuses at `not_proven` / `not_ready`. However, see §2.1 below for a related issue.

### 1.3 Non-active legacy path preservation

**PASS** — The plan explicitly tests that non-active fund types still use the legacy path (test case #10, §8.1).

### 1.4 Service/UI/Host/renderer/quality-gate direct parser consumption

**PASS** — No proposed changes touch these layers.

---

## 2. Specific Design Findings

### 2.1 CRITICAL: `EvidenceSourceKind` production type pollution

**Location**: Plan §6.2 and §9 residual table

The plan proposes adding `candidate_only` to `EvidenceSourceKind`:

```python
# Current (fund_agent/fund/extractors/models.py:11):
EvidenceSourceKind = Literal["annual_report", "external_api", "derived"]

# Proposed:
EvidenceSourceKind = Literal["annual_report", "external_api", "derived", "candidate_only"]
```

**Why this is a problem**:

1. `EvidenceSourceKind` is used by `EvidenceAnchor.source_kind`, which is consumed in the **production extraction path**. `FundFieldFamilyResult.__post_init__` (contracts.py:264-280) validates that accepted/partial field families carry `EvidenceAnchor` objects. Adding `candidate_only` to the literal means production anchors could legally carry `source_kind="candidate_only"`.

2. The plan's own §6.2 says: `EvidenceAnchor.source_kind` must be one of `annual_report`, `external_api`, `derived` for **production paths**. But by adding `candidate_only` to the shared `EvidenceSourceKind` literal, the type system no longer enforces this constraint — it becomes a runtime documentation convention.

3. The plan classifies this as "No (additive)" residual risk (§9), which is incorrect. A production type change that relaxes a constraint is not merely additive.

4. The `FundExtractionSourceBoundary` literal in `contracts.py` **already** includes `candidate_only` (contracts.py:57-67 line 60: `"candidate_only"`). But that's a separate type at the processor level, not the extractor level. The plan is extending the extractor-level type, which has wider blast radius.

**Required fix**: Either:
- (a) Keep `EvidenceSourceKind` unchanged and use `FundExtractionSourceBoundary` (which already has `candidate_only`) for candidate-path anchors, with a clear conversion boundary; or
- (b) Create a processor-local `ProcessorEvidenceSourceKind` that extends `EvidenceSourceKind` only within the processor boundary; or
- (c) Explicitly document a migration plan for when `candidate_only` is removed from production types after candidate paths are proven.

### 2.2 HIGH: `FundDisclosureDocumentStub` placement in `documents/models.py`

**Location**: Plan §3 allowed files table, row 4

The plan proposes adding `FundDisclosureDocumentStub` to `fund_agent/fund/documents/models.py`. This file currently holds:

- `ParsedAnnualReport` — production model, consumed by `FundDataExtractor.extract()` and `ActiveFundAnnualProcessor.extract()`
- `DocumentKey` — production identity key
- `AnnualReportSourceMetadata` — production source metadata
- `ReportSection`, `ParsedTable` — production parser output

Adding a candidate-only stub here mixes `candidate_only` / `not_proven` semantics into the same namespace as production models. This creates:

1. **Namespace pollution**: Future code that imports from `documents.models` gets both production and candidate models, making it harder to enforce the candidate boundary.
2. **Precedent risk**: If `FundDisclosureDocumentStub` lives in `documents/models.py`, the natural next step ("add more fields to the stub") keeps expanding a production file with candidate semantics.

**Required fix**: Place `FundDisclosureDocumentStub` in either:
- `fund_agent/fund/processors/contracts.py` (alongside other processor-level types like `CandidateBoundaryStatus`), or
- A new `fund_agent/fund/processors/disclosure_models.py` if the stub grows beyond a single dataclass.

At minimum, the plan must justify why `documents/models.py` is the right home despite the production/candidate boundary concern.

### 2.3 MEDIUM: `fund_disclosure_dispatch.py` scope ambiguity

**Location**: Plan §3 (file purpose), §5.3, §7

The plan describes `fund_disclosure_dispatch.py` with an ambiguous scope:

- §3: "Define how `FundDisclosureDocument`-like objects are admitted to the dispatch boundary"
- §5.3: "S3 adds a test proving that `fund_disclosure_document.v1` + `active_fund` with only `ActiveFundAnnualProcessor` registered raises `UnsupportedFundProcessorError`"
- §7: "The S3 dispatch helper (`fund_disclosure_dispatch.py`) must enforce this mapping" (the failure-class to gap-code mapping)
- §7末: "No fallback logic is implemented in S3 — only the mapping contract"

Three interpretations are possible, and the plan doesn't resolve which one is intended:

1. **Pure constants file**: Just the failure-class-to-gap-code mapping table, a lookup function.
2. **Dispatch validation helper**: A function that validates a `FundDisclosureDocumentIntermediate` against a `FundProcessorDispatchKey` and returns gaps.
3. **Mini-processor**: Admission logic that constructs `FundProcessorInput` from a disclosure document.

The implementation worker will have to decide, which is exactly what a plan should prevent.

**Required fix**: Explicitly list the functions/classes that `fund_disclosure_dispatch.py` will export, with signatures and docstrings.

### 2.4 MEDIUM: Missing existing test verification

The plan specifies validation commands for the future implementation gate (§10), but does not verify that the current test suite passes before modifications are proposed. Specifically:

- The plan proposes modifying `tests/fund/processors/test_registry.py` and `tests/fund/test_data_extractor.py` — but doesn't confirm these files exist (they do: `tests/fund/processors/test_registry.py` and `tests/fund/test_data_extractor.py`).
- The plan doesn't include a pre-modification baseline: "run existing tests, confirm they pass, record the count."

This is a procedural gap, not a design flaw, but it means the implementation worker has no baseline to validate "legacy preservation" against.

### 2.5 LOW: Missing `__init__.py` export considerations

The plan creates new public types (`FundDisclosureDocumentIntermediate` protocol, `FundDisclosureDocumentStub`) and a new module (`fund_disclosure_dispatch.py`) but doesn't address whether these need to be exported from `processors/__init__.py` or `documents/__init__.py`. The current `processors/__init__.py` has an explicit `__all__` — the plan should note whether new exports are needed.

---

## 3. Coherence Checks

### 3.1 Failure taxonomy consistency

**PASS** — The five failure classes map correctly to AGENTS.md canonical categories. The mapping to `contract_status` is coherent:
- `schema_drift` / `identity_mismatch` / `integrity_error` → `blocked`
- `not_found` / `unavailable` → `partial` or `missing`

This aligns with the AGENTS.md fallback policy.

### 3.2 Identity checks alignment with S2 code

**PASS** — The plan's identity check (§7.1) mirrors the existing S2 `_validate_processor_result_identity()` (data_extractor.py:511-554), comparing `fund_code` and `report_year` (via `document_year`). The plan correctly references S2 behavior.

### 3.3 Source provenance handling

**PASS** — The plan requires `source_provenance` to be explicit or projectable (§4.2), and emits `source_provenance_unsafe` gap when missing. This aligns with the existing `FundProcessorInput.source_provenance` field (contracts.py:204).

### 3.4 `FundIntermediateKind` literal already declares `fund_disclosure_document.v1`

**PASS (code fact confirmed)** — `contracts.py:22` already includes `"fund_disclosure_document.v1"` in `FundIntermediateKind`. The plan doesn't need to add it.

### 3.5 `FundProcessorInput.intermediate` is already `ParsedAnnualReport | object`

**PASS (code fact confirmed)** — `contracts.py:201`: `intermediate: ParsedAnnualReport | object`. The union type already admits non-`ParsedAnnualReport` objects. The plan's extension is coherent with the existing type.

### 3.6 `ActiveFundAnnualProcessor.supports()` already checks `intermediate_kind`

**PASS (code fact confirmed)** — `active_annual.py:226-231`: `context.intermediate_kind == "parsed_annual_report.v1"` is already in the supports() check. The plan correctly leaves this unchanged.

---

## 4. Test Plan Adequacy

### 4.1 Coverage completeness

**ADEQUATE with gaps** — The test plan covers:
- Protocol conformance for minimal stub
- CandidateBoundaryStatus invariant enforcement (3 negative cases)
- All 5 failure class mappings
- contract_status for blocked/partial/unsupported
- Identity mismatch detection
- source_provenance_unsafe gap
- Registry dispatch key raising UnsupportedFundProcessorError
- Legacy path preservation for non-active fund
- No Service/UI/Host imports

**Missing test cases**:
- `failure_class=None` → normal processing path (what happens when candidate has no failure?)
- `CandidateBoundaryStatus` with all fields correct (happy path)

### 4.2 Legacy path preservation verification

**ADEQUATE** — The plan requires existing tests to pass without modification, and adds a negative test proving non-active fund still uses legacy path.

---

## 5. Residual Risk Assessment

| Residual | Plan's classification | Reviewer assessment |
|---|---|---|
| `EvidenceSourceKind` extension | "No (additive)" | **Disagree** — This is a production type change with real blast radius. Reclassify as at least "Needs migration plan." See §2.1. |
| `FundDisclosureDocumentStub` placement | Not listed as residual | **Should be added** — Mixing candidate and production models is a boundary hygiene concern. See §2.2. |
| `fund_disclosure_dispatch.py` scope | Not listed as residual | **Should be added** — Scope ambiguity risks implementation drift. See §2.3. |
| No concrete processor | Correctly classified | Agree — blocks release |
| Full schema not implemented | Correctly classified | Agree — blocks release |
| Candidate statuses remain `not_proven` | Correctly classified | Agree — blocks release |

---

## 6. Conclusion

The plan correctly identifies goal/non-goal boundaries, preserves the non-active legacy path, and maintains fail-closed semantics. The failure taxonomy, identity checks, source provenance handling, and test plan are coherent with current code facts and AGENTS.md constraints.

However, three concrete issues prevent the plan from being code-generation-ready:

1. **CRITICAL**: `EvidenceSourceKind` literal extension from `extractors/models.py` is a production type change that the plan incorrectly classifies as non-blocking additive. The fix must either isolate the candidate path to processor-level types (`FundExtractionSourceBoundary` already has `candidate_only`) or provide an explicit migration plan.

2. **HIGH**: `FundDisclosureDocumentStub` should not live in `documents/models.py` alongside production models. Relocate to `processors/contracts.py` or a new processor-level models file.

3. **MEDIUM**: `fund_disclosure_dispatch.py` scope is ambiguous between constants, validation helper, and mini-processor. The plan must list explicit function/class signatures.

These fixes are narrow — they don't require redesigning the slice scope, the dispatch contract, or the test plan. The plan is close to ready.
