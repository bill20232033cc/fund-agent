# Docling EvidenceAnchor Mapping No-live Implementation Review - DS - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping No-live Implementation Gate`
Review role: AgentDS implementation reviewer
Release/readiness: `NOT_READY`

## 1. Scope

This is the AgentDS scoped implementation review. It reviews only the candidate-internal implementation and no-live tests. It does not run Docling conversion, live/network/EID/FDR/PDF/source acquisition, provider/LLM, analyze/checklist/golden/readiness/release/PR/push/merge commands.

## 2. Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Rule truth |
| `docs/current-startup-packet.md` | Current startup packet |
| `docs/implementation-control.md` | Current control truth |
| `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-plan-controller-judgment-20260616.md` | Controller judgment with binding constraints and findings DS2-F1 through DS2-F4, MIMO-IMPL-F1 |
| `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-plan-20260616.md` | Accepted no-live implementation plan |
| `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-evidence-20260616.md` | Implementation evidence |
| `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` | Implementation under review |
| `tests/fund/documents/test_docling_evidence_anchor_mapping.py` | Tests under review |

## 3. Validation Commands Executed

```bash
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
# Result: 9 passed in 0.48s

uv run ruff check fund_agent/fund/documents/candidates/evidence_anchor_mapping.py tests/fund/documents/test_docling_evidence_anchor_mapping.py
# Result: All checks passed!

git diff -- fund_agent/fund/documents/candidates/evidence_anchor_mapping.py tests/fund/documents/test_docling_evidence_anchor_mapping.py docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-evidence-20260616.md
# Result: no output (files are untracked allowed-write-set)
```

## 4. Controller Finding Disposition

### DS2-F1: S1 multi-page table bbox containment

**Disposition: ADDRESSED.**

Code at `evidence_anchor_mapping.py:389`:

```python
if schema_family == "S1_full" and len(table.page_numbers) > 1 and cell.source_locator.page_number is None:
    return "missing_page_number"
```

S1 tables spanning multiple pages fail closed when the cell lacks its own page number. The bbox containment path in `_table_contains_cell_bbox` (line 443) iterates `bbox_by_page` with per-page bbox dictionaries, so a cell on page N is matched against the same-page table bbox. Multi-page table safety is implemented and fail-closed.

### DS2-F2: S4/S5/S6 table_id availability

**Disposition: ADDRESSED.**

Code at `evidence_anchor_mapping.py:380-381`:

```python
if not table.table_id:
    return "missing_table_id"
```

This guard applies to ALL schema families including S4/S5/S6 lightweight. If `table_id` is absent, cell mapping is blocked before S4/S5/S6-specific tuple checks. Happy-path expectation is validated programmatically, not assumed.

### DS2-F3: section keyword family list

**Disposition: ADDRESSED.**

`_SECTION_KEYWORD_FAMILIES` at lines 33-44 is a closed `frozenset`-backed dict keyed by `§1` through `§10`, with explicit per-section keyword tuples. Module docstring at line 6 declares the closed nature. Keyword inference from paragraph/cell text alone is not used — `_section_candidates_from_block` only extracts from structural fields (section_id, heading_path, heading_text).

### DS2-F4: S4/S5/S6 section-hierarchy-absent test scenario

**Disposition: NOT ADDRESSED — finding persists.**

The controller accepted this as `ACCEPT_AS_TEST_REQUIREMENT`: "Add no-live test coverage for S4/S5/S6 missing section hierarchy with deterministic heading-path mapping and ambiguous heading-path blocking if applicable."

Existing tests `test_missing_section_context_blocks_mapping` and `test_unstable_section_context_blocks_mapping` only use `schema_family="S1_full"`. No test constructs an S4/S5/S6 lightweight document with absent or truncated section hierarchy and verifies the resulting stop code (`missing_section_context` or `unstable_section_context`).

Severity: **Medium**. The code path for section resolution is shared across schema families (section resolution does not branch on schema_family), so the S1 test exercises the same code. However, this is a controller-accepted binding requirement, and the absence means the implementation does not satisfy all binding constraints.

### MIMO-IMPL-F1: Explicit missing/unstable_section_context distinction

**Disposition: PARTIALLY ADDRESSED — residual persists.**

Separate tests `test_missing_section_context_blocks_mapping` and `test_unstable_section_context_blocks_mapping` exist and exercise distinct stop codes. However:

- `test_unstable_section_context_blocks_mapping` is mixed-mode: the heading in the fixture maps successfully while the paragraph is blocked, making it harder to read the intended unstable-section assertion.
- Neither test exercises the distinction under S4/S5/S6.
- The controller requirement called for test coverage that "distinguishes" the two — the current tests separate them but do not make the distinction explicit in a single comparative test or in S4/S5/S6 context.

Severity: **Low**. The two stop codes are covered by distinct tests.

## 5. New DS Implementation Findings

### DS-IMPL-F1: S4/S5/S6 cell happy path test absent

Severity: **Medium**.

The plan test matrix requires:

> S4/S5/S6 cell happy path | exact `table_id + table.page_number + cell_index + row_start + column_start` | mapped cell candidate

No test exercises `schema_family="S4_S5_S6_lightweight"` with a fully resolved cell. The S4/S5/S6 tests only cover stop paths (`test_s4_s5_s6_cell_blocks_missing_tuple_member`, `test_s4_s5_s6_cell_blocks_duplicate_tuple`). The S4/S5/S6-specific positive guards are:

- `_validate_cell_parent_table:383-385` — requires `table.page_number` or `table.page_numbers` for S4/S5/S6 tables
- `_cell_row_locator:769-770` — requires `cell_index is not None` for S4/S5/S6

These guards are not exercised in a positive mapping scenario. The common mapping code is exercised through S1_full tests, but the S4/S5/S6-specific decision points lack positive coverage.

### DS-IMPL-F2: Candidate/production isolation is programmatic

Severity: **None — positive observation.**

- `CandidateEvidenceAnchorFields` does not subclass `EvidenceAnchor` and is not importable from production anchor paths.
- `CandidateEvidenceAnchorMapping` wraps fields with `candidate_only=True`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"` enforced at construction time via `__post_init__`.
- No `to_evidence_anchor`, `as_evidence_anchor`, `to_production_anchor` method exists. `rg` search confirmed zero matches.
- Public API returns `CandidateEvidenceAnchorMappingResult`, not bare `EvidenceAnchor` or `list[EvidenceAnchor]`. Tests assert `"EvidenceAnchor" not in {type(item).__name__ for item in result.mapped}`.
- `source_kind="annual_report"` appears ONLY inside `CandidateEvidenceAnchorFields` and is typed as `CandidateAnnualSourceKind = Literal["annual_report"]`, not as a production `source_kind` string.
- The module imports only from `fund_agent.fund.documents.candidates.representation_models` — no cross-boundary imports.

### DS-IMPL-F3: S1 parent-table resolution is deterministic and fail-closed

Severity: **None — positive observation.**

`_resolve_parent_table` (line 412) implements exactly the plan's resolution order:
1. Shared ref match (`source_ref` in `{table_id, source_ref, source_locator.source_ref}`) — line 429-436
2. Unique bbox containment on same page — line 437-439
3. Otherwise `None` → blocked `cannot_resolve_parent_table` — line 440

Forbidden heuristics (nearest-previous, page-only, heading similarity, synthetic ids) are absent.

### DS-IMPL-F4: S4/S5/S6 tuple resolution is deterministic and fail-closed

Severity: **None — positive observation.**

`_validate_cell_parent_table` (line 361) implements the exact plan tuple:
- `table_id` required (line 380)
- `table.page_number` or `table.page_numbers` required for S4/S5/S6 (line 383)
- `cell_index`, `row_start`, `column_start` all required (line 385)
- `_duplicate_cell_tuple_exists` blocks duplicate `(cell_index, row_start, column_start)` (line 387, line 394)

### DS-IMPL-F5: Section stability rules are mechanically enforceable

Severity: **None — positive observation.**

`_resolve_section_id` (line 500) implements the plan's stability rules:
- Candidates from block structural fields via `_section_candidates_from_block` (line 530)
- Fallback to document section matching via `_section_candidates_from_document_section` (line 555)
- `§` pattern matching via regex + closed keyword families (line 582)
- Zero candidates → `missing_section_context`
- Multiple candidates → `unstable_section_context`
- Unsupported section id → `unstable_section_context`
- Keyword-only inference from arbitrary text is not used

### DS-IMPL-F6: Missing/unstable section and missing page stop paths are reasonable

Severity: **None — positive observation.**

All stop paths required by the plan are implemented:
- `unsupported_source_kind` for non-Docling routes
- `missing_section_context` for zero section candidates
- `unstable_section_context` for multi-match or unsupported section
- `missing_page_number` for blocks without stable page (including S1 multi-page cell without own page)
- `cannot_resolve_parent_table` for ambiguous/missing parent table
- `missing_table_id` for table without id
- `missing_cell_position` for S4/S5/S6 missing tuple or S1 without row/column
- `ambiguous_cell_tuple` for duplicate S4/S5/S6 tuple

No `section_id=null` anchors are emitted. No template-chapter inference is used.

### DS-IMPL-F7: Boundary containment verified

Severity: **None — positive observation.**

- Module lives at `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` — inside the allowed write set.
- Imports are bounded to `fund_agent.fund.documents.candidates.representation_models`.
- No imports from `fund_agent.fund.documents` (production `EvidenceAnchor`), Service, Host, UI, renderer, quality gate, parser, source, provider, or external packages.
- Tests import only from `fund_agent.fund.documents.candidates.evidence_anchor_mapping` and `fund_agent.fund.documents.candidates.representation_export`/`representation_projection` — all within the candidates boundary.

### DS-IMPL-F8: Row locator rules match plan

Severity: **None — positive observation.**

- Heading, paragraph, table: `row_locator=null` — confirmed at lines 268-271.
- Cell S1 without `cell_index`: `cell:r{row_start}:c{column_start}` — line 768-770.
- Cell S1 with `cell_index`: `cell:r{row_start}:c{column_start}:idx{cell_index}` — line 767-768.
- S4/S5/S6 without `cell_index`: blocked (line 769-770 returns None → `missing_cell_position`).
- `row_locator` is not used to compensate for missing `table_id`, page, or section — all are independently validated before row_locator construction.

## 6. Boundary Verification Summary

| Check | Result |
| --- | --- |
| Candidate wrapper programmatically isolates from production EvidenceAnchor | PASS |
| No `to_evidence_anchor`/`as_evidence_anchor`/`to_production_anchor` | PASS |
| `source_kind=annual_report` only inside CandidateEvidenceAnchorFields | PASS |
| S1 parent-table resolution deterministic/fail-closed | PASS |
| S4/S5/S6 tuple resolution deterministic/fail-closed | PASS |
| Section stability rules mechanically testable | PASS |
| Missing/unstable section stop paths reasonable | PASS |
| Missing page stop path reasonable | PASS |
| Row locator rules match plan | PASS |
| Module stays within Fund documents candidates boundary | PASS |
| No Service/Host/UI/renderer/quality gate imports | PASS |
| No source/FDR/parser/provider/LLM imports | PASS |
| No bare EvidenceAnchor or list[EvidenceAnchor] returned | PASS |
| Tests cover DS2-F1 (S1 multi-page) | PASS |
| Tests cover DS2-F2 (S4/S5/S6 table_id) | PASS |
| Tests cover DS2-F3 (section keywords) | PASS |
| Tests cover DS2-F4 (S4/S5/S6 section-hierarchy-absent) | FAIL — no test |
| Tests cover MIMO-IMPL-F1 (missing vs unstable distinction) | PARTIAL — separate tests exist, no S4/S5/S6 context |
| Tests cover S4/S5/S6 cell happy path | FAIL — no test |
| Tests cover all other plan-required cases (13 of 16) | PASS |

## 7. Residuals

| Residual | Owner | Severity |
| --- | --- | --- |
| DS2-F4: S4/S5/S6 section-hierarchy-absent test missing | Implementation owner | Medium — controller-accepted binding requirement |
| DS-IMPL-F1: S4/S5/S6 cell happy path test missing | Implementation owner | Medium — plan-required case uncovered |
| MIMO-IMPL-F1: missing/unstable distinction incomplete for S4/S5/S6 | Implementation owner | Low — separate tests exist but lack S4/S5/S6 context |
| Coverage command using pytest-cov module source may still expand into source acquisition imports | Tooling follow-up | Accepted residual per evidence |

## 8. Final Verdict

```text
VERDICT: PASS_WITH_FINDINGS_NOT_READY
```

**Rationale**: The implementation correctly implements all algorithmic requirements of the accepted plan. Candidate/production isolation is programmatic, not convention-only. S1 and S4/S5/S6 parent-table resolution are deterministic and fail-closed. Section stability, row locator, and stop-path rules are mechanically sound. Boundary containment is clean — no cross-boundary imports, no production EvidenceAnchor leakage, no admission helpers.

Two controller-accepted test requirements (DS2-F4, MIMO-IMPL-F1) and one plan-required test case (S4/S5/S6 cell happy path) are not fully covered. These are test coverage gaps, not implementation defects. The code paths for the missing tests share logic with covered paths, so the implementation behavior is correct even without the tests.

None of the findings are blocking for correctness, stability, or boundary integrity. The implementation does NOT cross the Fund documents candidates boundary, does NOT touch production EvidenceAnchor, Service, Host, UI, renderer, quality gate, source, FDR, parser, or provider. Release/readiness remains `NOT_READY`.

Recommendation for next gate: accept the implementation with these findings recorded as residuals, and close the test gaps in a follow-up or as part of the evidence gate.
