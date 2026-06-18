# Docling EvidenceAnchor Mapping No-live Implementation Review - AgentMiMo

Date: 2026-06-16
Role: AgentMiMo implementation reviewer
Gate: `Docling EvidenceAnchor Mapping No-live Implementation Gate`
Release/readiness: `NOT_READY`

## 1. Scope

This review covers the no-live implementation evidence at `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-evidence-20260616.md` and the source files:

- `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py`
- `tests/fund/documents/test_docling_evidence_anchor_mapping.py`

This review does not implement code, change source/tests/runtime behavior, update `EvidenceAnchor` schema, change `FundDocumentRepository`, parser behavior, source policy, CHAPTER_CONTRACT, Service, Host, UI, renderer or quality gate behavior, and does not run Docling conversion, live/network/EID/FDR/PDF/source acquisition, provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge commands.

## 2. Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Rule truth source |
| `docs/design.md` relevant EvidenceAnchor / FundDisclosureDocument / Docling sections | Current design boundaries |
| `docs/implementation-control.md` front section | Current control truth |
| `docs/current-startup-packet.md` | Current startup truth |
| `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-plan-controller-judgment-20260616.md` | Accepted plan and binding constraints |
| `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-plan-20260616.md` | No-live implementation plan |
| `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-evidence-20260616.md` | Implementation evidence |
| `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` | Implementation code |
| `tests/fund/documents/test_docling_evidence_anchor_mapping.py` | Implementation tests |

## 3. Review Findings

### 3.1 Implementation Ownership Containment

**Check**: Implementation ownership fully restricted to `fund_agent/fund/documents/candidates/` and `tests/fund/documents/`.

**Evidence**:

- `evidence_anchor_mapping.py` lives at `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` — within allowed write set.
- Test file lives at `tests/fund/documents/test_docling_evidence_anchor_mapping.py` — within allowed write set.
- `rg` scan of public package `__init__.py` files (`fund_agent/__init__.py`, `fund_agent/fund/__init__.py`, `fund_agent/fund/documents/__init__.py`) found zero matches for `evidence_anchor_mapping` or `CandidateEvidenceAnchor` — candidate internals are not exported through public package surface.

**Verdict**: PASS. Implementation ownership is correctly constrained.

### 3.2 Candidate Metadata Completeness

**Check**: Candidate metadata explicitly includes `candidate_source`, `schema_family`, `sample_id`, `candidate_only`, `field_correctness_status`, `source_truth_status`.

**Evidence**:

- `CandidateEvidenceAnchorMapping.__post_init__()` enforces: `candidate_source == "docling"`, `candidate_only is True`, `field_correctness_status == "not_proven"`, `source_truth_status == "not_proven"` — all raise `ValueError` on violation.
- `CandidateEvidenceAnchorMapping` dataclass fields include `schema_family` and `sample_id`.
- `CandidateEvidenceAnchorMappingBlocked` dataclass carries the same metadata defaults.
- Test `test_document_mapping_emits_candidate_wrappers_for_heading_paragraph_table_and_cell` asserts `candidate_only is True` and `field_correctness_status == "not_proven"`.
- Note string includes `candidate_source=docling; schema_family=...; sample_id=...; candidate_only=true; field_correctness_status=not_proven`.

**Verdict**: PASS. All required metadata fields are present and enforced programmatically.

### 3.3 No Production Admission Helpers

**Check**: No `to_evidence_anchor`, `as_evidence_anchor`, `to_production_anchor` or equivalent production-admission helper.

**Evidence**:

- `rg` scan of `evidence_anchor_mapping.py` and test file for `to_evidence_anchor|as_evidence_anchor|to_production_anchor|EvidenceAnchor\(` returned zero matches.
- The module does not import `EvidenceAnchor` from production code.

**Verdict**: PASS. No production admission surface exists.

### 3.4 No Service/Host/UI/renderer/quality-gate Direct Access

**Check**: Public package does not export candidate internals; no direct external layer dependency.

**Evidence**:

- Public package `__init__.py` scan confirms no re-export of candidate mapping symbols.
- The module docstring explicitly states: "它不导入或返回生产 EvidenceAnchor，不读取 PDF，不调用 Docling，不访问 FundDocumentRepository，也不改变 Service/Host/UI/renderer/quality gate 的消费边界。"
- The allowed commands did not include a cross-module external-import scan. A full `rg` scan across `fund_agent/` excluding `candidates/` was requested but denied as outside the allowed whitelist. Public package boundary check is sufficient for this gate; cross-module import scan is a non-blocking residual.

**Verdict**: PASS. Public package boundary is clean. External import scan recorded as non-blocking residual.

### 3.5 Docs Decision

**Check**: Docs decision is reasonable; no README/control/design sync needed.

**Evidence**:

- Evidence artifact states: "No README update was made because the helper remains candidate-internal and does not add a public usage contract or test grouping."
- Plan section 14 authorizes this: "If candidate-internal behavior becomes documented public developer surface, update `fund_agent/fund/README.md`. Otherwise record 'README unchanged; candidate-internal helper only; no public usage contract change' in implementation evidence."
- `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md` are not modified — correct per plan.

**Verdict**: PASS. Docs decision is consistent with plan and does not cause design/control drift.

### 3.6 No-live Validation Evidence Sufficiency

**Check**: No-live validation evidence is sufficient and does not imply readiness.

**Evidence**:

- `uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q` → `9 passed` (all happy/stop paths covered).
- `uv run ruff check` → `All checks passed!`
- `git diff --check` → clean (no tracked diff; untracked files only).
- Coverage: `87%` for `evidence_anchor_mapping.py` (exceeds 80% target).
- Evidence artifact verdict: `IMPLEMENTED_AND_VALIDATED_NO_LIVE_NOT_READY` — correctly preserves NOT_READY.

**Verdict**: PASS. Validation is sufficient for no-live implementation. NOT_READY preserved.

### 3.7 DS2-F1 to DS2-F4 and MIMO-IMPL-F1 Finding Closure

| Finding | Status | Evidence |
| --- | --- | --- |
| DS2-F1: S1 multi-page table bbox containment | CLOSED | `_validate_cell_parent_table()` line 389: `if schema_family == "S1_full" and len(table.page_numbers) > 1 and cell.source_locator.page_number is None: return "missing_page_number"`. Multi-page table without explicit cell page is blocked. |
| DS2-F2: S4/S5/S6 `table_id` availability | CLOSED | `_validate_cell_parent_table()` line 380: `if not table.table_id: return "missing_table_id"`. Checked before S4/S5/S6 tuple validation. |
| DS2-F3: section keyword family list | CLOSED | `_SECTION_KEYWORD_FAMILIES` dict (lines 33-44) and `_SUPPORTED_SECTION_PREFIXES` frozenset (line 32) are defined as module-level constants. Documented in module docstring: "年报章节归属采用显式 § 章节 token 和闭合年报标题族判断". |
| DS2-F4: S4/S5/S6 section-hierarchy-absent test | CLOSED | `test_s4_s5_s6_cell_blocks_missing_tuple_member()` and `test_s4_s5_s6_cell_blocks_duplicate_tuple()` cover S4/S5/S6 stop paths. `test_missing_section_context_blocks_mapping()` covers missing section for all schema families. Evidence artifact confirms S4/S5/S6 section hierarchy absence is handled by deterministic heading-path mapping when one-to-one, otherwise fail-closed. |
| MIMO-IMPL-F1: `unstable_section_context` stop-path test | CLOSED | `test_unstable_section_context_blocks_mapping()` (lines 403-431) explicitly tests heading_path mapping to multiple section families, asserting `reason_code == "unstable_section_context"`. This is distinct from `test_missing_section_context_blocks_mapping()` which tests `missing_section_context`. |

All five findings are closed with implementation evidence.

## 4. Residuals

| Residual | Severity | Owner |
| --- | --- | --- |
| Cross-module external-import scan not performed (outside allowed command whitelist). Public package boundary check is sufficient for this gate. | Non-blocking | Future evidence gate if needed |
| Candidate mappings are not source truth, field correctness proof or production EvidenceAnchor admission. | Accepted residual | Future evidence/design gate |
| Docling baseline promotion not decided by this gate. | Deferred | Future baseline disposition gate |
| Field correctness comparison against PDF/source truth not performed. | Deferred | Future comparative evidence gate |

## 5. Verdict

```text
VERDICT: PASS_WITH_FINDINGS_NOT_READY
```

Findings: all five accepted review findings (DS2-F1 through DS2-F4, MIMO-IMPL-F1) are closed. Four non-blocking residuals recorded. Implementation is candidate-only, correctly isolated, programmatically enforced, and does not imply readiness.

Release/readiness remains `NOT_READY`.
