# Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Plan Review - MiMo

Date: 2026-06-15

Gate: `Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Planning Gate`

Role: AgentMiMo, review worker only

Readiness state: `NOT_READY`

## 1. Scope

Adversarial review of `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-20260615.md` against the 8 review focus areas specified by the gate.

This review does not modify the plan, implement code, or change release/readiness state.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/implementation-control.md` (Current Truth Guardrails / Current Gate)
- `docs/current-startup-packet.md` (Current Mainline / Resume Checklist)
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-20260615.md` (plan under review)
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-controller-judgment-20260615.md` (accepted binding amendments)
- `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md` (Route A evidence)
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-review-mimo-20260615.md` (prior MiMo review of mapping plan)
- Static ownership check: `fund_agent/fund/documents/models.py`, `fund_agent/fund/extractors/models.py`, `fund_agent/fund/documents/__init__.py`

## 3. Review Focus Analysis

### 3.1 Code-generation readiness

The plan provides concrete dataclass/enum/TypedDict designs (section 6), closed normalization vocabulary (section 7), explicit fixture shape (section 10), failure mapping table (section 10 of mapping plan + section 6.1 `CandidateFailureCode`), per-slice contracts and expected assertions (section 11), and validation commands (section 12). The implementation worker does not need to invent schema ownership, fixture shape, normalization vocabulary, failure mapping or test scope.

One gap: `NormalizationRuleName` is referenced as a type annotation in multiple dataclass fields (e.g., `CandidateSection.normalization_notes`, `CandidateParagraphBlock.normalization_applied`, `CandidateTableCellLocator.normalization_notes`) but is never defined as a type alias. Section 7 lists the closed vocabulary but does not define the Python type. The implementation worker must define this as `Literal[...]` or `str` plus runtime validation. The plan should specify the exact type definition.

### 3.2 Allowed write set breadth

The allowed write set (section 4) restricts writes to:
- `fund_agent/fund/documents/candidates/` (new package)
- `tests/fixtures/fund/docling_route_a/004393_2025/` (excerpt fixture)
- `tests/fund/documents/test_docling_*.py` (new test files)
- narrow additions to `tests/fund/documents/test_repository.py`
- conditional `fund_agent/fund/README.md` or `tests/README.md`

Forbidden writes explicitly exclude: production Service/UI/Host/renderer/quality-gate behavior, `EvidenceAnchor` schema, `EvidenceSourceKind`, `FundDocumentRepository.load_annual_report()` production behavior, source policy/fallback, full Route A artifacts, readiness/release/PR.

The write set is appropriately narrow. No production behavior change, no schema change, no boundary violation.

One observation: the allowed write set includes conditional README updates, but the forbidden writes section does not explicitly mention README. This is internally consistent (conditional means "only if implementation changes candidate internals/tests"), but a strict reading could find it ambiguous. The implementation worker should treat README updates as allowed only when the change documents candidate-only status, fixture provenance or no-consumption boundaries.

### 3.3 Candidate-only constraint

All proposed models/enums/TypedDicts are scoped to `fund_agent/fund/documents/candidates/`. The plan explicitly states:
- "Do not export from `fund_agent/fund/documents/__init__.py` unless controller later authorizes public contract" (section 4)
- "Existing `fund_agent/fund/extractors/models.py` remains the public `EvidenceAnchor` schema surface and must not import candidate internals" (section 5.1)
- `EvidenceSourceKind` remains `Literal["annual_report", "external_api", "derived"]` (section 3.1)
- Candidate statuses are fixed to `not_proven` / `not_authorized` (section 6.1)

The plan preserves candidate-only constraint. No public contract overreach.

### 3.4 Normalization vocabulary closure

Section 7 defines exactly 11 rule names in a closed vocabulary table. Each rule has layer, applies-to and output semantics. Section 13 stop condition 10 states: "normalization vocabulary needs a new rule name outside section 7" triggers `BLOCKED_NOT_READY`.

The vocabulary is closed and the stop condition is explicit.

Whitespace-only numeric grouping (section 9) defines deterministic repair conditions (5 conditions), accepted repair examples (4 cases), fail-closed/no-repair conditions (5 conditions), and no-repair examples (5 cases). These are testable against the `numeric-whitespace-grouping` fixture case in section 10.3.

One gap: the plan does not specify a test that asserts every `NormalizationRuleName` in the closed vocabulary is actually implemented. The failure mapping slice (Slice 6) tests that every `CandidateFailureCode` maps to a canonical outcome, but there is no equivalent test for normalization rules. The implementation worker should add a test that the set of implemented rules matches the closed vocabulary.

### 3.5 Fixture/excerpt minimality

The fixture design (section 10) uses one checked-in JSON excerpt (`excerpt.json`) with hash metadata tying it to Route A without embedding full JSON. The plan explicitly states:
- "Do not commit full `004393_2025_docling.json`, full Markdown, PDF, cache artifacts or model artifacts" (section 4)
- `full_json_committed: false` (section 10.1)
- "The implementation worker must not copy the full Route A JSON" (section 10.3)
- Table excerpts include "only the header rows and 2-4 representative body rows per table" (section 10.2)

The fixture is appropriately minimal.

One observation: the fixture content shape in section 10.2 shows `table_cells: []` (empty array) for each table excerpt. The plan then says table_cells "should contain only the header rows and 2-4 representative body rows." This is not a contradiction (the shape is a template, not the actual fixture), but the implementation worker must fill these arrays. The plan should clarify that the empty arrays in the example are placeholders, not the expected fixture content.

### 3.6 Slice size and no-live constraint

Slices are small and focused:
- Slice 0: fixture contract + red tests (1 fixture file, 4 test files)
- Slice 1: candidate models (1 source file, 1 test file)
- Slice 2: text normalization (1 source file, 1 test file)
- Slice 3: table structure + locators (1 source file, 1 test file)
- Slice 4: cross-page stitching (extends Slice 3 files)
- Slice 5: projection fixture (extends Slice 3 files)
- Slice 6: failure mapping (1 source file, 1 test file)
- Slice 7: repository + no-consumption guards (2 test files)
- Slice 8: README docs (conditional)

Validation commands (section 12) are all `pytest` targeted tests and `ruff check`. Forbidden validation explicitly excludes PDF/Docling conversion, parser execution, EID/FDR/network, provider/LLM, analyze/checklist/golden/readiness/release/PR.

Slices are small enough and validation is no-live only.

One observation: Slices 3, 4, and 5 all extend `fund_agent/fund/documents/candidates/locators.py` and `tests/fund/documents/test_docling_locators.py`. This is fine for logical separation but means those files grow across three implementation commits. The implementation worker should keep commits separable if the controller requests that workflow, as noted in section 11.

### 3.7 No-consumption guards and repository non-behavior tests

Slice 7 defines:
- `FundDocumentRepository.load_annual_report()` production behavior remains unchanged
- Candidate modules are not imported/called by Service/UI/Host/renderer/quality gate
- Current production parser/cache boundary remains inside Fund documents
- `fund_agent/fund/documents/__init__.py` does not export candidate internals
- `EvidenceSourceKind` still excludes `docling_pdf_candidate`

The no-consumption guard test checks imports in `fund_agent/services`, `fund_agent/ui`, `fund_agent/host`, `fund_agent/fund/template`, `fund_agent/fund/audit`, `fund_agent/fund/report_quality_validation.py` for `fund_agent.fund.documents.candidates`, `docling`, PDF cache helpers, parser adapters or Docling/PDF parser helpers directly.

This is comprehensive. The repository non-behavior test proves the default load path remains `ParsedAnnualReport` and the candidate route is not invoked by default.

### 3.8 NOT_READY preservation

The plan preserves `NOT_READY` throughout:
- Readiness state: `NOT_READY` (header)
- Non-proofs section (section 3.2) explicitly lists all non-proofs
- Stop conditions (section 13) block any source truth, field correctness, raw XML/XBRL, taxonomy, parser replacement or readiness claim
- Final verdict: `PLAN_READY_FOR_REVIEW_NOT_READY`
- Completion report format (section 16) requires `NOT_READY` preservation

The plan does not declare source truth, field correctness, raw XML/XBRL, taxonomy compatibility, parser replacement or readiness.

## 4. Findings

| ID | Severity | Section | Finding | Required handling |
|---|---|---|---|---|
| MIMO-NLIP-001 | medium | Section 6.2, 6.3 | `NormalizationRuleName` type is referenced in 4 dataclass fields (`CandidateSection.normalization_notes`, `CandidateParagraphBlock.normalization_applied`, `CandidateTableCellLocator.normalization_notes`, `CandidateEvidenceAnchorNote.normalization`) but never defined as a Python type alias. Section 7 lists the closed vocabulary but does not specify the type definition. The implementation worker must define this as `Literal[...]` or `str` plus runtime validation, which is an invention the plan is supposed to prevent. | Add explicit type definition: `NormalizationRuleName = Literal["cjk_space_repair", "date_space_repair", "numeric_punctuation_repair", "numeric_whitespace_grouping_repair_or_block", "header_path_reconstruction", "repeated_header_exclusion", "cross_page_table_stitching", "merged_cell_expansion", "toc_header_footer_exclusion", "row_label_path_generation", "column_header_path_generation"]` to section 6.1 or 7. |
| MIMO-NLIP-002 | medium | Section 10.2 | Fixture content shape shows `table_cells: []` for all table excerpts. Section 10.2 text says "table_cells should contain only the header rows and 2-4 representative body rows per table." The empty arrays are placeholders but this is not explicitly stated. The implementation worker may interpret `[]` as the expected fixture content, which would make table-dependent tests vacuous. | Add explicit note that `table_cells: []` in the shape example is a structural placeholder; the actual checked-in fixture must contain minimal representative cells per section 10.2 instructions. Or provide at least one table excerpt with non-empty cells in the shape example. |
| MIMO-NLIP-003 | low | Section 11, Slice 3-5 | Slices 3, 4, and 5 all extend the same two files (`locators.py` and `test_docling_locators.py`). While logically separated, the plan does not specify whether each slice should be a separate commit or whether they can be combined. The section 11 intro says "Later implementation should keep commits/review artifacts separable if the controller requests that workflow" but does not set a default. | Clarify default: either all three are one implementation unit, or each is a separate commit by default. |
| MIMO-NLIP-004 | low | Section 7, Section 11 | No test asserts that the set of implemented `NormalizationRuleName` values matches the closed vocabulary in section 7. Slice 6 tests that every `CandidateFailureCode` maps to a canonical outcome, but there is no equivalent completeness test for normalization rules. | Add to Slice 2 or Slice 3 expected assertions: a test that verifies the set of rule names accepted by the normalization functions matches the closed vocabulary exactly. |
| MIMO-NLIP-005 | low | Section 6.3 | `CandidateEvidenceAnchorNote` is described as "should be a TypedDict or JSON-compatible dataclass" and "used only by fixture tests" but its module location is not specified. Section 5.2 does not list it. It is likely in `locators.py` per the Slice 5 projection helper reference, but this is implicit. | Add `CandidateEvidenceAnchorNote` to section 5.2 proposed files table, assigned to `fund_agent/fund/documents/candidates/locators.py` (or `models.py`). |

## 5. Binding Amendment Compliance Check

The controller judgment `docling-funddisclosuredocument-mapping-normalization-plan-controller-judgment-20260615.md` specified 7 binding amendments for the next gate. Compliance:

| Amendment | Plan compliance | Notes |
|---|---|---|
| 1. Keep `docling_pdf_candidate` candidate-only | PASS | Section 3.1, 5.1, 6.1, 13 |
| 2. Define closed normalization-rule vocabulary | PASS | Section 7 |
| 3. Split document normalization from extractor/value parsing | PASS | Section 8 |
| 4. Define whitespace-only numeric grouping semantics | PASS | Section 9 |
| 5. Keep candidate projection fixture-only | PASS | Section 6.3, 11 Slice 5 |
| 6. Preserve FundDocumentRepository boundary and no-consumption guards | PASS | Section 4, 11 Slice 7 |
| 7. Preserve EID single-source/no-fallback and NOT_READY | PASS | Section 1.3, 3.2, 13 |

All 7 binding amendments are addressed in the plan.

## 6. Verdict

```text
VERDICT: PASS_WITH_NONBLOCKING_FINDINGS
```

The plan is code-generation-ready for an implementation worker. All 7 binding amendments from the prior controller judgment are addressed. The normalization vocabulary is closed. The fixture design is minimal. Slices are small and no-live only. No-consumption guards and repository non-behavior tests are specified. `NOT_READY` is preserved throughout.

The 5 findings are non-blocking:
- MIMO-NLIP-001 (medium): `NormalizationRuleName` type definition missing -- implementation worker can derive it from section 7 but the plan should be explicit.
- MIMO-NLIP-002 (medium): empty `table_cells` in fixture shape example -- implementation worker should fill them but the plan should clarify this is a placeholder.
- MIMO-NLIP-003 (low): Slice 3/4/5 commit separation default unspecified.
- MIMO-NLIP-004 (low): no normalization vocabulary completeness test.
- MIMO-NLIP-005 (low): `CandidateEvidenceAnchorNote` module location unspecified.

None of these findings block implementation. The implementation worker can proceed with the plan as-is, but should address MIMO-NLIP-001 and MIMO-NLIP-002 early in the implementation to avoid ambiguity.

## 7. Final Verdict

```text
VERDICT: PASS_WITH_NONBLOCKING_FINDINGS_NOT_READY
```

Stop here. Do not enter implementation.
