# Docling EvidenceAnchor Mapping No-live Implementation Re-review - AgentMiMo

Date: 2026-06-16
Role: AgentMiMo re-reviewer
Gate: `Docling EvidenceAnchor Mapping No-live Implementation Re-review Gate`
Release/readiness: `NOT_READY`

## 1. Scope

This re-review verifies that accepted findings from the prior MiMo implementation review (`docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-review-mimo-20260616.md`) are closed after the fix pass (`docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-fix-evidence-20260616.md`).

This re-review does not implement code, change source/tests/runtime behavior, update `EvidenceAnchor` schema, change `FundDocumentRepository`, parser behavior, source policy, CHAPTER_CONTRACT, Service, Host, UI, renderer or quality gate behavior, and does not run Docling conversion, live/network/EID/FDR/PDF/source acquisition, provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge commands.

## 2. Re-review Focus

### 2.1 Candidate Metadata/Isolation Did Not Regress

**Check**: Fix pass added tests only; implementation code unchanged; candidate isolation preserved.

**Evidence**:

- Fix evidence artifact states: "No implementation code was changed in this fix pass." Only `tests/fund/documents/test_docling_evidence_anchor_mapping.py` was modified.
- Test file still imports only from `fund_agent.fund.documents.candidates.evidence_anchor_mapping` — no production `EvidenceAnchor` import.
- `test_document_mapping_emits_candidate_wrappers_for_heading_paragraph_table_and_cell()` (lines 245-276) still asserts `candidate_only is True`, `field_correctness_status == "not_proven"`, and `"EvidenceAnchor" not in {type(item).__name__ for item in result.mapped}`.
- No `to_evidence_anchor`, `as_evidence_anchor`, `to_production_anchor` or `EvidenceAnchor(` patterns added by the fix.
- `uv run pytest` → `12 passed` (9 prior + 3 new). No regressions.
- `uv run ruff check` → `All checks passed!`

**Verdict**: PASS. Candidate metadata and isolation did not regress.

### 2.2 DS2-F4: S4/S5/S6 Section-hierarchy-absent Tests Are Now Explicit

**Check**: Two new S4/S5/S6 section-hierarchy-absent tests added.

**Evidence** (test file lines 402-446):

- `test_s4_s5_s6_maps_without_section_nodes_when_heading_path_is_one_to_one()` (line 402): constructs payload with `sections=()`, asserts S4/S5/S6 cell maps with `section_id == "§8"` when heading path maps one-to-one to a section family.
- `test_s4_s5_s6_blocks_without_section_nodes_when_heading_path_is_ambiguous()` (line 423): constructs payload with `sections=()` and ambiguous `heading_path=["§8 投资组合报告", "§9 基金份额持有人信息"]`, asserts `reason_code == "unstable_section_context"`.

Both tests explicitly exercise S4/S5/S6 lightweight schema with absent section hierarchy, covering the one-to-one happy path and the ambiguous blocking path.

**Verdict**: PASS. DS2-F4 is closed with explicit tests.

### 2.3 S4/S5/S6 Happy Path Exists

**Check**: S4/S5/S6 cell happy path test exists.

**Evidence**:

- `test_s4_s5_s6_cell_happy_path_maps_with_exact_tuple()` (lines 350-372): uses default `_payload()` with `schema_family="S4_S5_S6_lightweight"`, asserts cell mapping with `table_id == "tbl_8_1"`, `page_number == 62`, and expected `row_locator` format.

**Verdict**: PASS. S4/S5/S6 happy path is covered.

### 2.4 Missing vs Unstable Section Distinction Remains Explicit

**Check**: `missing_section_context` and `unstable_section_context` are tested as distinct stop paths.

**Evidence**:

- `test_missing_section_context_blocks_mapping()` (line 449): empty `heading_path`, no section candidates → `missing_section_context`.
- `test_unstable_section_context_blocks_mapping()` (line 475): multi-section heading path for S1_full → `unstable_section_context`.
- `test_s4_s5_s6_blocks_without_section_nodes_when_heading_path_is_ambiguous()` (line 423): multi-section heading path for S4_S5_S6_lightweight → `unstable_section_context`.

Three tests cover both reason codes across both schema families.

**Verdict**: PASS. Missing vs unstable distinction remains explicit.

### 2.5 No New Docs/Control/Design/README Obligation Introduced

**Check**: Fix pass did not introduce documentation or control document obligations.

**Evidence**:

- Fix evidence artifact states: only test file was changed. No implementation code, design, control doc, README or startup packet was modified.
- `git diff -- tests/fund/documents/test_docling_evidence_anchor_mapping.py docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-fix-evidence-20260616.md` → clean (no tracked diff beyond the fix scope).

**Verdict**: PASS. No new obligations introduced.

## 3. Residuals

| Residual | Severity | Owner |
| --- | --- | --- |
| Candidate mappings are not source truth, field correctness proof or production EvidenceAnchor admission. | Accepted residual | Future evidence/design gate |
| Docling baseline promotion not decided by this gate. | Deferred | Future baseline disposition gate |
| Cross-module external-import scan not performed (outside allowed command whitelist). | Non-blocking | Future evidence gate if needed |

These residuals are carried forward from the prior implementation review and are unchanged by the fix pass.

## 4. Verdict

```text
VERDICT: RE_REVIEW_PASS_NOT_READY
```

All five accepted findings are closed. Candidate metadata/isolation did not regress. DS2-F4 S4/S5/S6 section-hierarchy-absent tests are now explicit. S4/S5/S6 happy path exists. Missing vs unstable section distinction remains explicit. No new docs/control/design/README obligation was introduced.

Release/readiness remains `NOT_READY`.
