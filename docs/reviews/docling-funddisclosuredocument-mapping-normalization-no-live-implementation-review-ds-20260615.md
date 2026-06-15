# Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Review (AgentDS)

Date: 2026-06-15

Gate: `Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Gate`

Role: review worker (AgentDS), not controller

Readiness state: `NOT_READY`

Verdict: `PASS_WITH_NONBLOCKING_FINDINGS`

## 1. Scope

This review evaluates the implementation evidence at `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-evidence-20260615.md` against:

- The accepted no-live implementation plan `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-20260615.md`
- The controller judgment `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-controller-judgment-20260615.md`
- Current truth guardrails in `docs/implementation-control.md`
- `AGENTS.md` hard constraints

Review only; no code fixes are performed.

## 2. Evidence Reviewed

**Control/docs:**
- `AGENTS.md`
- `docs/implementation-control.md` Current Truth Guardrails / Current Gate
- `docs/current-startup-packet.md` Current Mainline / Resume Checklist
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-evidence-20260615.md`

**Implementation files (read-only):**
- `fund_agent/fund/documents/candidates/__init__.py`
- `fund_agent/fund/documents/candidates/models.py`
- `fund_agent/fund/documents/candidates/normalization.py`
- `fund_agent/fund/documents/candidates/locators.py`
- `fund_agent/fund/documents/candidates/failures.py`
- `tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json`
- `tests/fund/documents/test_docling_candidate_models.py`
- `tests/fund/documents/test_docling_normalization.py`
- `tests/fund/documents/test_docling_locators.py`
- `tests/fund/documents/test_docling_failure_mapping.py`
- `tests/fund/documents/test_docling_no_consumption_guards.py`
- `tests/fund/documents/test_repository.py`

**Key production files checked for non-change:**
- `fund_agent/fund/documents/__init__.py`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/documents/repository.py`

## 3. Validation Commands Run

- `uv run pytest tests/fund/documents/test_docling_candidate_models.py tests/fund/documents/test_docling_normalization.py tests/fund/documents/test_docling_locators.py tests/fund/documents/test_docling_failure_mapping.py tests/fund/documents/test_docling_no_consumption_guards.py -q` → **20 passed**
- `uv run pytest tests/fund/documents/test_repository.py -q` → **20 passed**
- `uv run ruff check fund_agent/fund/documents tests/fund/documents` → **All checks passed**
- `git diff --check` → **no whitespace issues**
- Forbidden commands (PDF/Docling conversion, PDF parser, EID/FDR/network, provider/LLM, analyze/checklist/golden/readiness/release/PR): **not run**

## 4. Review Findings

### 4.1 Scope Boundary: Strictly Limited to Accepted Write Set

**Finding DS-REV-S1 (PASS):** Implementation writes are exactly the accepted set: 5 candidate internals files, 1 excerpt fixture, 5 test files, and 1 narrow test addition to `test_repository.py`. No production `FundDocumentRepository.load_annual_report()` behavior change. No `EvidenceAnchor` schema change. No `EvidenceSourceKind` expansion (`annual_report`/`external_api`/`derived` unchanged at `fund_agent/fund/extractors/models.py:11`). No source policy/fallback code touched. No Service/UI/Host/renderer/quality-gate behavior changed. Holds across `git diff` and static checks.

**Finding DS-REV-S2 (PASS):** `fund_agent/fund/documents/__init__.py` still exports only `ANNUAL_REPORT_DOCUMENT_KIND`, `DocumentKey`, `ParsedAnnualReport`, `ParsedTable`, `ReportSection`, `FundDocumentRepository` — zero candidate internals in public surface. Test `test_candidate_internals_are_not_public_documents_exports` (test_docling_candidate_models.py:184) passes.

**Finding DS-REV-S3 (PASS):** Forbidden consumers do not import candidates. AST guard (`test_docling_no_consumption_guards.py:25`) covers Service/UI/Host/template/audit/report_quality_validation + extractors (per amendment DS-IMPL-F4). Manual `rg` confirms zero `docling`, `fund_agent.fund.documents.candidates`, `fund_agent.fund.documents.adapters.annual_report_pdf`, or `fund_agent.fund.documents.cache` imports in any guarded path.

### 4.2 Candidate Package Isolation

**Finding DS-REV-C1 (PASS):** `fund_agent/fund/documents/candidates/__init__.py` is a minimal docstring-only module. It does not re-export models, normalization helpers, or locators. The package is importable by tests but not discoverable from production paths.

**Finding DS-REV-C2 (PASS):** `fund_agent/fund/extractors/models.py` has zero diff — current `EvidenceSourceKind` literal excludes `docling_pdf_candidate`. Tests assert this directly (`test_candidate_internals_are_not_public_documents_exports` asserts `"docling_pdf_candidate" not in get_args(EvidenceSourceKind)`).

### 4.3 NormalizationRuleName / NormalizedText / CandidateTableGroup / CandidateEvidenceAnchorNote

**Finding DS-REV-N1 (PASS):** `NormalizationRuleName = Literal[...]` (models.py:19-31) exactly matches the plan's 11-rule closed vocabulary. `NORMALIZATION_RULE_NAMES` constant is identical. Test `test_normalization_rule_type_matches_closed_vocabulary_exactly` (test_docling_candidate_models.py:168) proves `get_args(NormalizationRuleName) == NORMALIZATION_RULE_NAMES`. Test `test_implemented_normalization_rule_names_match_closed_vocabulary` (test_docling_locators.py:66) proves implementation returns equal to constant.

**Finding DS-REV-N2 (PASS):** `NormalizedText` (models.py:170-199) is explicitly defined as a `@dataclass(frozen=True, slots=True)` with `raw_text`, `normalized_text`, `rules_applied`, `failure_code`, and `blocked` property. Matches controller amendment DS-IMPL-F1.

**Finding DS-REV-N3 (PASS):** Text-level and table/locator-level normalization APIs are separated (amendment DS-IMPL-F2): `normalization.py` exposes `normalize_text()` and `implemented_text_normalization_rules()` (4 rules), while `locators.py` exposes table/locator helpers and `implemented_locator_normalization_rules()` (7 rules). Tests prove separation (`test_text_normalization_rule_contract_is_separate_from_locator_rules` in test_docling_normalization.py:78).

**Finding DS-REV-N4 (PASS):** `CandidateTableGroup` (models.py:367-378) is defined with `group_id`, `source_table_ids`, `page_numbers`, `table_family`, `stitched_table` (nullable), `failure_code`, `normalization_notes`. Matches amendment DS-IMPL-F3.

**Finding DS-REV-N5 (PASS):** `CandidateEvidenceAnchorNote` (models.py:147-166) is a `TypedDict` under candidate internals with `candidate_source_kind`, `source_table_ref`, `page_no`, `bbox`, row/col offsets, `row_label_path`, `column_header_path`, `cell_text`, `cell_hash`, `locator_hash`, `normalization`, `source_truth_status`, `field_correctness_status`. Matches plan section 6.3 and amendment MIMO-NLIP-005.

### 4.4 Numeric Whitespace Grouping Repair/Block

**Finding DS-REV-W1 (PASS):** `_is_accepted_whitespace_group()` (normalization.py:206-229) implements the deterministic conditions from plan section 9.1: first group 1-3 digits, subsequent groups exactly 3 digits, all-digit groups, and the 2-group exception (first group < 3 not accepted). The `_replace()` inner function (normalization.py:148-176) checks adjacent business characters per plan section 9.2 (CJK/Latin adjacent → block), validates the collapsed string grammar, and blocks on any ambiguity.

**Finding DS-REV-W2 (PASS):** Tests cover all plan-mandated cases (test_docling_normalization.py:53-75): `100 000` → `100000`, `1 234 567` → `1234567`, `12 345.67` → `12345.67`, `-1 234 567.89` → `-1234567.89` (repair); `1 23 456`, `50 100`, `A 100 000` (block as `NUMERIC_REPAIR_AMBIGUOUS`). No Decimal parsing occurs — `normalized_text` remains `str`.

**Finding DS-REV-W3 (PASS):** Fixture `normalization_cases` (excerpt.json:755-762) include both accepted numeric-punctuation and whitespace-grouping cases, plus ambiguity cases, matching plan section 10.3 and section 9.

### 4.5 Fixture Minimality and Correctness

**Finding DS-REV-F1 (PASS):** Fixture metadata (excerpt.json:2-18) has `route_a_json_sha256` matching the accepted Route A JSON hash, `route_a_markdown_sha256` for Markdown hash, `full_json_committed: false`, all `not_proven`/`not_authorized` statuses, and explicit non-truth notes. Tests assert these values (test_docling_candidate_models.py:49-72).

**Finding DS-REV-F2 (PASS):** All 7 required table cases have non-empty `table_cells` and `prov` entries (amendment MIMO-NLIP-002). Test `test_required_table_cases_have_non_empty_cells_and_provenance` (test_docling_candidate_models.py:75-96) asserts both. Each `table_cells` entry has `bbox` field.

**Finding DS-REV-F3 (PASS):** Full Route A JSON/Markdown/PDF/cache/model artifacts are not committed. Only `excerpt.json` is under `tests/fixtures/fund/docling_route_a/`. `git ls-files --others` confirms no other artifacts leaked.

**Finding DS-REV-F4 (info, non-blocking):** `excerpt_hash_sha256` is `"minimal-excerpt-hash-not-source-truth"` — a descriptive placeholder rather than an actual SHA256 of the excerpt file. The plan section 10.1 says "computed over the checked-in excerpt file". While the placeholder reinforces non-truth status, a real hash would allow downstream excerpt-integrity checks.

### 4.6 Locator/Stitch/Projection Helper Boundaries

**Finding DS-REV-L1 (PASS):** `locators.py` performs only candidate locator operations: grid expansion, header row detection, repeated header detection, row/column path generation, cell/locator hashing, TOC exclusion, cross-page stitching. No Decimal parsing, no business field selection, no field correctness logic, no production `EvidenceAnchor` instantiation (only test does that).

**Finding DS-REV-L2 (PASS):** `build_candidate_anchor_note()` (locators.py:102-134) returns a `dict` with all plan-mandated fields and `not_proven` statuses. The function guards against missing path/hash with `CELL_LOCATOR_UNSTABLE`. Test `test_candidate_anchor_note_keeps_docling_source_kind_inside_note` (test_docling_locators.py:225-258) uses `EvidenceAnchor` only in test scope to prove current `source_kind` field remains `"annual_report"` while candidate note carries `"docling_pdf_candidate"` inside `note`.

**Finding DS-REV-L3 (PASS):** Cross-page stitching (`stitch_candidate_tables`, locators.py:137-193) validates section_id consistency, table_family consistency, column count compatibility, header signature compatibility, and page ordering before stitching. Returns `CandidateTableGroup` with nullable `stitched_table` on failure. Tests cover compatible accept (synthetic continuation of table 74) and header-mismatch reject (tables 61/62 with different period headers), matching plan section 11.4.

### 4.7 Failure Mapping

**Finding DS-REV-M1 (PASS):** Every `CandidateFailureCode` enum member (24 total) is mapped in `_FAILURE_MAPPING` (failures.py:17-42). `mapped_candidate_failure_codes()` returns `frozenset(_FAILURE_MAPPING)`. Test `test_every_candidate_failure_code_is_mapped` (test_docling_failure_mapping.py:13-26) proves `mapped == frozenset(CandidateFailureCode)`.

**Finding DS-REV-M2 (PASS):** All mappings use only current canonical `AnnualReportSourceFailureCategory` values: `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`. No fallback category, no source expansion branch. Test `test_failure_mapping_uses_only_current_canonical_categories` (test_docling_failure_mapping.py:29-63) iterates all codes and asserts result ∈ CANONICAL.

**Finding DS-REV-M3 (info, non-blocking):** `CandidateFailureCode` enum has 24 members versus the plan's section 6.1 listing of 20. Three are additions: `CANDIDATE_NOT_FOUND`, `CANDIDATE_UNAVAILABLE`, `CELL_TEXT_EMPTY`. These are needed: `CANDIDATE_NOT_FOUND` and `CANDIDATE_UNAVAILABLE` map to canonical `not_found`/`unavailable` (plan section 11.6 mapping table references these conditions); `CELL_TEXT_EMPTY` is a reasonable locator-level failure. All are properly mapped, so this does not break the closed vocabulary contract.

### 4.8 No-consumption Guards and Repository Non-behavior

**Finding DS-REV-G1 (PASS):** `test_docling_no_consumption_guards.py` AST guard correctly checks Service, UI, Host, template, audit, extractors, and `report_quality_validation.py` (GUARDED_PATHS at line 14-21) for forbidden imports. Test checks `docling`, `fund_agent.fund.documents.candidates`, `fund_agent.fund.documents.adapters.annual_report_pdf`, `fund_agent.fund.documents.cache` prefixes. Cross-verified with manual `rg` — zero matches in guarded paths.

**Finding DS-REV-G2 (PASS):** `test_documents_public_init_does_not_export_candidate_internals` (test_docling_no_consumption_guards.py:50-65) reads `fund_agent/fund/documents/__init__.py` and asserts no `"candidates"` or `"Candidate"` string in file content.

**Finding DS-REV-G3 (PASS):** `test_repository_load_annual_report_has_no_candidate_route` (test_repository.py:1167-1186) uses `inspect.getsource` to verify `FundDocumentRepository.load_annual_report` source contains neither `"documents.candidates"` nor `"docling_pdf_candidate"`, and the repository object has no `load_candidate_document` or `load_fund_disclosure_document` attributes. Existing 19 repository tests all pass (20 total), confirming no production behavior regression.

### 4.9 Test Quality and Missing Assertions

**Finding DS-REV-T1 (info, non-blocking):** Locator tests (`test_docling_locators.py`) verify specific cells (e.g., `"00939"` in stock holding table, `"50~100"` in manager holding) with specific expected paths. This is strong for the covered cases but the test set is small (6 tests). The plan explicitly scoped tests to "2-4 representative body rows" (section 10.2), so this is within accepted scope. Cross-page stitching test constructs a synthetic second table via deep-copy — acceptable for no-live testing but does not test real Route A continuation pairs.

**Finding DS-REV-T2 (info, non-blocking):** No test covers the `CandidateSection` or `CandidateParagraphBlock` dataclasses directly, or the full `CandidateBlockReason` / `CandidateSectionSource` closed sets. These types exist in models.py but are not yet exercised by locator or normalization tests. The plan's Slice 1 says "candidate identity round-trips from fixture metadata" — only identity is tested. This is consistent with plan scope (Slice 1 tests focus on identity + status invariants).

**Finding DS-REV-T3 (PASS):** Normalization tests directly use fixture `normalization_cases` data implicitly (the cases match what's in the fixture), but the fixture's `normalization_cases` array is not programmatically iterated — the test writes inline assertions. This is acceptable because the test assertions are concrete and verifiable, but it means fixture `normalization_cases` entries are documentation-only.

## 5. Binding Amendment Closure Verification

| Amendment | Status | Evidence |
|---|---|---|
| DS-IMPL-F1: Define `NormalizedText` explicitly | **Closed** | `NormalizedText` dataclass at models.py:170 with `blocked` property |
| DS-IMPL-F2: Split text vs table/locator API | **Closed** | `normalization.py` (text only) vs `locators.py` (table/locator); separate rule name constants; test proves separation |
| DS-IMPL-F3: Define stitched return contract | **Closed** | `CandidateTableGroup` at models.py:367 |
| DS-IMPL-F4: Include `fund_agent/fund/extractors` in guard | **Closed** | `GUARDED_PATHS` at test_docling_no_consumption_guards.py:20 |
| DS-IMPL-F5: Retain provenance entries | **Closed** | All excerpted objects retain `prov`; test asserts non-empty prov |
| DS-IMPL-F6: Test file names | **Closed** | Deferred per controller; Docling-specific names kept |
| MIMO-NLIP-001: `NormalizationRuleName` type alias | **Closed** | `Literal[...]` at models.py:19 with exact 11 rules |
| MIMO-NLIP-002: Non-empty fixture table_cells | **Closed** | Test asserts `table_cells` non-empty; fixture has actual cells |
| MIMO-NLIP-003: Slice 3/4/5 as cohesive pass | **Closed** | Single `locators.py` and `test_docling_locators.py` |
| MIMO-NLIP-004: Test rules match closed vocabulary | **Closed** | Two tests: `test_normalization_rule_type_matches_closed_vocabulary_exactly` + `test_implemented_normalization_rule_names_match_closed_vocabulary` |
| MIMO-NLIP-005: `CandidateEvidenceAnchorNote` location | **Closed** | In `models.py` under candidate internals |

All 11 binding amendments are closed.

## 6. Stop Condition Verification

Plan section 13 stop conditions checked:

| Condition | Status |
|---|---|
| `EvidenceAnchor` public schema or `EvidenceSourceKind` changed | Did not occur |
| `docling_pdf_candidate` proposed as production `source_kind` | Did not occur |
| Service/UI/Host/renderer/quality gate imports Docling/candidates | Did not occur; AST guard + rg both pass |
| `FundDocumentRepository.load_annual_report()` behavior changed | Did not occur; source inspection test passes |
| EID single-source/no-fallback policy changed | Did not occur |
| Full Route A JSON/Markdown/PDF/model/cache committed | Did not occur; only minimal excerpt.json |
| PDF/Docling conversion/parser/EID/FDR/network required | Not run |
| Normalization parses Decimal or claims field correctness | Did not occur; stays in string domain |
| Same-report comparison or consumer integration needed to pass tests | Did not occur |
| Candidate output described as truth/proof | Did not occur; statuses fixed to `not_proven`/`not_authorized` |
| New normalization rule name needed | Did not occur; all 11 rules in closed vocabulary |

No stop condition was triggered.

## 7. Residuals

- `excerpt_hash_sha256` is a placeholder string, not a computed SHA256 (non-blocking).
- `CandidateFailureCode` has 3 enum members beyond plan section 6.1 listing — all functionally justified and properly mapped (non-blocking).
- `CandidateSection` / `CandidateParagraphBlock` / closed label sets are declared but not yet tested — within plan scope.
- Fixture `normalization_cases` are tested by inline assertions, not by iterating the fixture array — acceptable current state.
- Route A single-sample limitation remains — documented in evidence §8.

## 8. Final Verdict

```text
VERDICT: PASS_WITH_NONBLOCKING_FINDINGS
```

All tests pass (20 candidate + 20 repository), ruff is clean, and `git diff --check` is clean. Implementation strictly follows the accepted write set. All 11 controller binding amendments are closed. No production boundary (EvidenceAnchor, EvidenceSourceKind, FundDocumentRepository, source policy, Service/UI/Host/renderer/quality gate) was breached. No stop condition was triggered. Findings are informational only: a placeholder hash, 3 additional (justified) failure enum members, and partial coverage of declared-but-untested model types within plan scope.

`NOT_READY` is preserved. No implementation behavior change in production path. Release/readiness remains `NOT_READY`.
