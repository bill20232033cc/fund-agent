# Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Review — MiMo

Date: 2026-06-15

Gate: `Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Review Gate`

Role: review worker (AgentMiMo)

Readiness state: `NOT_READY`

Verdict: `PASS_WITH_NONBLOCKING_FINDINGS`

## 1. Evidence Reviewed

- `AGENTS.md`
- `docs/implementation-control.md` Current Truth Guardrails / Current Gate
- `docs/current-startup-packet.md` Current Mainline / Resume Checklist
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-evidence-20260615.md`
- Implementation diff limited to accepted write set

## 2. Validation Commands And Results

```text
uv run pytest tests/fund/documents/test_docling_candidate_models.py tests/fund/documents/test_docling_normalization.py tests/fund/documents/test_docling_locators.py tests/fund/documents/test_docling_failure_mapping.py tests/fund/documents/test_docling_no_consumption_guards.py -q
Result: 20 passed

uv run pytest tests/fund/documents/test_repository.py -q
Result: 20 passed

uv run ruff check fund_agent/fund/documents tests/fund/documents
Result: All checks passed.

git diff --check
Result: (clean)
```

## 3. Review Focus Findings

### 3.1 Write Set Boundary — PASS

| Boundary check | Result |
|---|---|
| `fund_agent/fund/documents/candidates/` (5 files) | Untracked, within accepted write set |
| `tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json` | Untracked, within accepted write set |
| `tests/fund/documents/test_docling_*.py` (5 files) | Untracked, within accepted write set |
| `tests/fund/documents/test_repository.py` | Modified, narrow addition only (one new test + `import inspect`) |
| `EvidenceAnchor` schema (`fund_agent/fund/extractors/models.py`) | Unchanged; `EvidenceSourceKind = Literal["annual_report", "external_api", "derived"]` confirmed at line 11 |
| `FundDocumentRepository` production behavior | Unchanged; 20 existing tests pass; new test asserts no candidate route |
| Source policy / fallback | Unchanged; failure mapping uses only 5 canonical terminal categories |
| Service / UI / Host / renderer / quality gate behavior | Unchanged; AST guard tests confirm no candidate imports |
| `fund_agent/fund/documents/__init__.py` | Unchanged; `__all__` exports only production types |

No forbidden writes detected. `AGENTS.md`, `docs/current-startup-packet.md`, `docs/design.md`, `docs/implementation-control.md` are modified but these are out-of-scope for this review (not part of accepted write set, likely from prior gates).

### 3.2 Candidate Package Isolation — PASS

- `fund_agent/fund/documents/candidates/__init__.py` declares `__doc__` only; no re-exports.
- `fund_agent/fund/documents/__init__.py` has no import of `candidates`.
- No-consumption guard (`test_docling_no_consumption_guards.py`) covers `fund_agent/services`, `fund_agent/ui`, `fund_agent/host`, `fund_agent/fund/template`, `fund_agent/fund/audit`, `fund_agent/fund/extractors`, `fund_agent/fund/report_quality_validation.py` — AST scan confirms zero `fund_agent.fund.documents.candidates` or `docling` imports.
- `test_docling_candidate_models.py:197` asserts `"CandidateArtifactIdentity" not in documents_public_exports`.
- `test_docling_candidate_models.py:198` asserts `"docling_pdf_candidate" not in get_args(EvidenceSourceKind)`.

### 3.3 Binding Amendments Closure — PASS

| Amendment | Status |
|---|---|
| `NormalizationRuleName = Literal[...]` exactly matching closed vocabulary | `models.py:19-31` defines it; `NORMALIZATION_RULE_NAMES` tuple at `models.py:33-45` matches; `test_docling_candidate_models.py:181` asserts `get_args(NormalizationRuleName) == NORMALIZATION_RULE_NAMES` |
| `NormalizedText` explicitly defined | `models.py:169-199` frozen dataclass with `raw_text`, `normalized_text`, `rules_applied`, `failure_code`, `blocked` property |
| Text normalization API separated from table/locator helper API | `normalization.py` exports `DOCUMENT_TEXT_NORMALIZATION_RULE_NAMES` (4 rules); `locators.py` exports `TABLE_LOCATOR_NORMALIZATION_RULE_NAMES` (7 rules); `test_docling_normalization.py:91-96` asserts separation |
| `CandidateTableGroup` return contract | `models.py:367-378` frozen dataclass with `group_id`, `source_table_ids`, `page_numbers`, `table_family`, `stitched_table`, `failure_code`, `normalization_notes` |
| `CandidateEvidenceAnchorNote` under candidate internals | `models.py:147-166` TypedDict; constructed by `locators.py:102-134` |
| `fund_agent/fund/extractors` in no-consumption guard scope | `test_docling_no_consumption_guards.py:18` includes `Path("fund_agent/fund/extractors")` |
| Fixture non-empty representative table cells | `test_docling_candidate_models.py:94` asserts `item["table_cells"]` (truthy); fixture has non-empty cells for all 7 required table cases |
| Fixture provenance retention | `test_docling_candidate_models.py:95` asserts `item["prov"]`; each table/text excerpt retains `prov` entries |
| Slice 3/4/5 as cohesive locator pass | Single `locators.py` + single `test_docling_locators.py` |
| Implemented normalization rule names equal closed vocabulary | `test_docling_locators.py:66-89` asserts `implemented_normalization_rules() == NORMALIZATION_RULE_NAMES` and `set(implemented_normalization_rules()) == set(get_args(NormalizationRuleName))` |

### 3.4 Numeric Whitespace Grouping — PASS

`normalization.py:132-187` `repair_numeric_whitespace_grouping()`:

- **Deterministic repair**: regex `(?<![A-Za-z0-9])[-+]?\d[\d,\.\s]*\d(?![A-Za-z0-9])` matches digit-only whitespace tokens. `_is_accepted_whitespace_group()` requires: all groups are digits, first group ≤3 digits, subsequent groups exactly 3 digits, minimum 2 groups with first group == 3 when exactly 2 groups. Decimal suffix accepted when `decimal_part.isdigit()`.
- **Fail-closed**: blocks when adjacent to CJK/Latin business chars (`_is_adjacent_business_char`), when groups are not accepted pattern, or when final result doesn't match `^[-+]?\d+(?:\.\d+)?$`.
- **Tests**: `test_docling_normalization.py:53-75` covers accepted repairs (`100 000`, `1 234 567`, `12 345.67`, `-1 234 567.89`) and blocks (`1 23 456`, `50 100`, `A 100 000`).

### 3.5 Fixture Minimality — PASS

- Single `excerpt.json` at `tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json`.
- Contains: `metadata` with Route A hashes and non-proof statuses, `origin_excerpt`, 2 text excerpts, 7 table excerpts (minimal cells per table), 6 normalization cases, 3 failure cases.
- `full_json_committed: false`, explicit non-proof notes.
- No full JSON/Markdown/PDF/cache/model artifacts committed.
- Each table excerpt retains `prov` entries with page_no and bbox.

### 3.6 Locator / Stitch / Projection Scope — PASS

- `locators.py` builds table blocks from `table_cells`, reconstructs header/row paths, records merged-cell expansion, excludes TOC tables, hashes cells/locators, returns `CandidateTableGroup`, and builds fixture-only anchor notes.
- No `Decimal` parsing, no field correctness logic, no business field selection.
- `build_candidate_anchor_note()` returns a `dict[str, object]` (not production `EvidenceAnchor`), with `candidate_source_kind` inside `note` dict, not as `EvidenceAnchor.source_kind`.

### 3.7 Failure Mapping — PASS

- `failures.py` maps every `CandidateFailureCode` to exactly one canonical `AnnualReportSourceFailureCategory`.
- Canonical categories: `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error` — matches EID single-source terminal outcomes.
- `test_docling_failure_mapping.py:26` asserts `mapped_candidate_failure_codes() == frozenset(CandidateFailureCode)`.
- No fallback branch or Eastmoney/CNINFO/fund-company expansion.

### 3.8 Test Coverage — PASS

| Concern | Coverage |
|---|---|
| No-consumption guards | AST scan over 7 guarded paths; `documents.__init__` candidate exclusion |
| Repository non-behavior | `test_repository_load_annual_report_has_no_candidate_route` asserts no `load_candidate_document`/`load_fund_disclosure_document` attr, no `"documents.candidates"` or `"docling_pdf_candidate"` in source |
| Closed vocabulary | `get_args(NormalizationRuleName) == NORMALIZATION_RULE_NAMES`; `implemented_normalization_rules() == NORMALIZATION_RULE_NAMES`; text/locator rule separation |
| Candidate status non-proof | `__post_init__` rejects `source_truth_status != "not_proven"` and `production_parser_replacement_status != "not_authorized"` |
| Truth claim rejection test | `test_candidate_identity_rejects_truth_claims` |

## 4. Findings

| ID | Severity | Finding | Evidence | Impact |
|---|---|---|---|---|
| MIMO-R-F1 | info | `CandidateFailureCode` StrEnum includes two members (`CANDIDATE_NOT_FOUND`, `CANDIDATE_UNAVAILABLE`) not in the plan's section 6.1 enum listing, though they are mapped by the plan's section 6 failure mapping table and section 10 failure mapping is exhaustive. | `models.py:68-69`; `failures.py:18-19` map them to `not_found`/`unavailable`; `test_docling_failure_mapping.py:26` asserts full coverage | Non-blocking. These members are logically required by the canonical mapping table and are covered by tests. No scope boundary violation. |
| MIMO-R-F2 | info | `test_docling_candidate_models.py` imports `from fund_agent.fund.documents import __all__ as documents_public_exports` — this is a read-only boundary assertion, not a production coupling. | `test_docling_candidate_models.py:17` | Non-blocking. Test-only import for boundary verification. |

No blocking findings.

## 5. Residuals

- Route A remains one local sample only: `004393 / 2025`.
- Candidate locator quality is not field correctness proof.
- Same-report comparison across EID HTML render, current pdfplumber and Docling remains deferred.
- Local model cache provenance remains benchmark-only, not production model provenance acceptance.
- Production parser integration, public source-kind/schema decisions and consumer integration remain separate controller gates.

## 6. Verdict

```text
VERDICT: PASS_WITH_NONBLOCKING_FINDINGS
```

Release/readiness remains `NOT_READY`.

Output artifact: `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-review-mimo-20260615.md`
