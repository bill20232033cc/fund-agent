# Docling EvidenceAnchor Mapping No-live Implementation Re-review - DS - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping No-live Implementation Re-review Gate`
Review role: AgentDS re-reviewer
Release/readiness: `NOT_READY`

## 1. Scope

This re-review checks only the three accepted findings from the original DS implementation review. It does not re-audit the full implementation, run Docling conversion, live/network/EID/FDR/PDF/source acquisition, provider/LLM, analyze/checklist/golden/readiness/release/PR/push/merge commands.

## 2. Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-review-ds-20260616.md` | Original DS review with findings DS2-F4, DS-IMPL-F1, MIMO-IMPL-F1 |
| `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-fix-evidence-20260616.md` | Fix evidence |
| `tests/fund/documents/test_docling_evidence_anchor_mapping.py` | Updated test file |

## 3. Validation

```bash
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
# Result: 12 passed in 0.53s (was 9, +3 new tests)

uv run ruff check fund_agent/fund/documents/candidates/evidence_anchor_mapping.py tests/fund/documents/test_docling_evidence_anchor_mapping.py
# Result: All checks passed!

git diff -- tests/fund/documents/test_docling_evidence_anchor_mapping.py docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-fix-evidence-20260616.md
# Result: no output (untracked allowed-write-set)
```

## 4. Finding-by-Finding Re-review

### DS-IMPL-F1: S4/S5/S6 cell happy path test absent

**Original**: No test exercised `schema_family="S4_S5_S6_lightweight"` with a fully resolved cell.

**Fix**: Added `test_s4_s5_s6_cell_happy_path_maps_with_exact_tuple` (line 350).

The test:
- Projects a Docling PDF candidate document with complete cell tuple (cell_index=0, row_start=1, column_start=1)
- Maps with `schema_family="S4_S5_S6_lightweight"`
- Asserts cell mapping is present with `block_type == "cell"`
- Asserts `table_id == "tbl_8_1"`, `page_number == 62`
- Asserts `row_locator == "cell:r1:c1:idx0;row_label=股票A;column_header=占基金资产净值比例"` — confirming `cell_index` is included as required for S4/S5/S6

The S4/S5/S6-specific positive guards in `_validate_cell_parent_table` (table page_number requirement, cell_index requirement) and `_cell_row_locator` (cell_index mandatory for S4/S5/S6) are now exercised in a positive mapping scenario.

**Disposition**: **RESOLVED**.

### DS2-F4: S4/S5/S6 section-hierarchy-absent test scenario

**Original**: No test constructed an S4/S5/S6 lightweight document with absent section hierarchy.

**Fix**: Added two tests:

1. `test_s4_s5_s6_maps_without_section_nodes_when_heading_path_is_one_to_one` (line 402):
   - Projects document with `sections=()` (no section tree)
   - Heading path `["§8 投资组合报告"]` provides one-to-one section mapping via `_SECTION_KEYWORD_FAMILIES`
   - Asserts cell with `section_id == "§8"` is mapped — deterministic heading-path mapping works

2. `test_s4_s5_s6_blocks_without_section_nodes_when_heading_path_is_ambiguous` (line 423):
   - Projects document with `sections=()` (no section tree)
   - Heading path `["§8 投资组合报告", "§9 基金份额持有人信息"]` creates multi-match ambiguity
   - Asserts `result.mapped == ()` and all blocked reason codes are `unstable_section_context` — ambiguous heading path blocking works

**Disposition**: **RESOLVED**.

### MIMO-IMPL-F1: Missing vs unstable section context distinction in S4/S5/S6

**Original**: Separate tests existed for `missing_section_context` and `unstable_section_context` but neither used S4/S5/S6 schema family, and the unstable test was mixed-mode (heading mapped + paragraph blocked).

**Fix**: The two new DS2-F4 tests jointly distinguish the two stop codes in S4/S5/S6 context:

| Test | S4/S5/S6 context | Section tree | Heading path | Outcome |
| --- | --- | --- | --- | --- |
| `test_s4_s5_s6_maps_without_section_nodes_when_heading_path_is_one_to_one` | Yes | Absent | One-to-one `["§8 ..."]` | Mapped (stable) |
| `test_s4_s5_s6_blocks_without_section_nodes_when_heading_path_is_ambiguous` | Yes | Absent | Multi-match `["§8 ...", "§9 ..."]` | Blocked `unstable_section_context` |
| `test_missing_section_context_blocks_mapping` (existing, S1) | No (S1) | Absent | Empty `[]` | Blocked `missing_section_context` |

The `unstable_section_context` test is now clean: no mixed-mode mapping, all blocked entries carry exactly `unstable_section_context`. The three tests together make the distinction explicit: zero candidates → missing, multi-match → unstable, one-to-one → mapped.

**Disposition**: **RESOLVED**.

## 5. Final Disposition Summary

| Finding | Source | Severity (original) | Status |
| --- | --- | --- | --- |
| DS2-F4: S4/S5/S6 section-hierarchy-absent test missing | Controller binding requirement | Medium | RESOLVED — 2 tests added |
| DS-IMPL-F1: S4/S5/S6 cell happy path test absent | Plan-required case | Medium | RESOLVED — 1 test added |
| MIMO-IMPL-F1: missing/unstable distinction incomplete for S4/S5/S6 | Controller binding requirement | Low | RESOLVED — distinction now clear in S4/S5/S6 context |

No new findings. No implementation code was changed — the fix added only test coverage. Boundary containment, production isolation, algorithm correctness, and all other positive observations from the original DS review remain intact.

## 6. Final Verdict

```text
VERDICT: RE_REVIEW_PASS_NOT_READY
```

All three controller-accepted findings are resolved. Test count increased from 9 to 12. Ruff passes. No code changes were needed — the implementation was already correct, and the test gaps are now closed. Release/readiness remains `NOT_READY`.
