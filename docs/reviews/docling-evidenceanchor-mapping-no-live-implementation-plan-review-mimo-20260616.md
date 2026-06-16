# Docling EvidenceAnchor Mapping No-live Implementation Plan Review - AgentMiMo

Date: 2026-06-16
Reviewer: AgentMiMo
Gate: `Docling EvidenceAnchor Mapping No-live Implementation Plan Review Gate`
Review target: `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-plan-20260616.md`
Release/readiness: `NOT_READY`

## 1. Scope And Method

Adversarial review of the no-live implementation plan against:

- `AGENTS.md` rule truth source and Fund documents boundary
- `docs/design.md` EvidenceAnchor / FundDisclosureDocument / Docling sections
- `docs/implementation-control.md` front current-control section
- `docs/current-startup-packet.md` current active gate and guardrails
- `docs/reviews/docling-evidenceanchor-mapping-plan-controller-judgment-20260616.md` binding constraints
- `docs/reviews/docling-evidenceanchor-mapping-plan-review-ds-20260616.md` DS findings DS-F1 through DS-F4
- `docs/reviews/docling-evidenceanchor-mapping-plan-review-mimo-20260616.md` MiMo findings MIMO-F1 through MIMO-F6

Review lenses applied: architecture boundary, best-practice, overcoupling.

## 2. Review Focus

Per gate scope:

1. Does the implementation plan fully carry controller binding constraints?
2. Does candidate/production isolation avoid bare production EvidenceAnchor outputs?
3. Is module ownership correctly limited to Fund documents candidate internals?
4. Are S1 and S4/S5/S6 parent-table resolution strategies deterministic and fail-closed?
5. Are section stability and row_locator rules mechanically testable?
6. Is the no-live test matrix sufficient and correctly scoped?
7. Does the plan avoid production parser replacement, source truth/full correctness/readiness claims and live/provider/source commands?

## 3. Assumptions Tested

| # | Assumption | Test Result |
|---|-----------|-------------|
| A1 | Plan carries all DS-F1 through DS-F4 binding constraints from controller judgment | PASS — DS-F1 → §6 programmatic candidate/production boundary; DS-F2 → §5 module ownership; DS-F3 → §8 S1 parent-table resolution; DS-F4 → §10 S4/S5/S6 section hierarchy verification |
| A2 | Plan carries all MIMO-F1 through MIMO-F6 binding constraints from controller judgment | PASS — MIMO-F1 → §5; MIMO-F2 → §8/§9; MIMO-F3 → §10 section stability rules; MIMO-F4 → §11/§7.4 `row_locator=null` default; MIMO-F5 → §12 test matrix; MIMO-F6 → §7.3/§11 paragraph `row_locator=null` |
| A3 | Candidate/production isolation is programmatic, not convention-only | PASS — §6 defines `CandidateEvidenceAnchorFields` as independent dataclass, forbids `to_evidence_anchor` / `as_evidence_anchor` methods, requires candidate wrapper return types |
| A4 | S1 parent-table resolution is deterministic and fail-closed | PASS — §8 defines 4-step priority chain with explicit `cannot_resolve_parent_table` stop; forbidden heuristics are listed |
| A5 | S4/S5/S6 tuple resolution is complete and fail-closed | PASS — §9 defines exact tuple match with `ambiguous_cell_tuple` stop on non-unique tuples |
| A6 | Section stability rules are mechanically testable | PASS — §10 defines stable/unstable criteria with concrete conditions; stop behavior is explicit |
| A7 | No-live test matrix covers both happy paths and stop paths | PARTIAL — §12 has 16 cases covering happy/stop/source-kind/isolation/containment; one gap: `unstable_section_context` stop path not explicitly listed |
| A8 | Plan avoids production parser replacement, source truth and readiness claims | PASS — §1/§2/§15 explicitly forbid these; §18 verdict is `NOT_READY` |
| A9 | Validation commands are no-live only | PASS — §13 commands are pytest/coverage/git-diff only; no live/network/EID/provider/LLM commands |
| A10 | Module ownership is correctly constrained to Fund documents candidate internals | PASS — §5 explicitly binds to `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` and blocks Service/Host/UI/renderer/quality-gate access |

## 4. Findings

### Findings Table

| ID | Severity | Status | Summary |
|----|----------|--------|---------|
| MIMO-IMPL-F1 | Low | accepted-candidate | Test matrix missing explicit `unstable_section_context` stop-path case |

### MIMO-IMPL-F1 - [Low] - Test matrix missing explicit `unstable_section_context` stop-path case

- **位置**: §12 No-live Test Matrix, §10 Section Stability Rules
- **问题类型**: 测试缺口
- **当前写法**: §10 defines two distinct stop conditions: `missing_section_context` (section id is absent) and `unstable_section_context` (section id present but ambiguous — heading path maps to multiple section families, only page proximity available, or section inferred from arbitrary keywords). §12 test matrix includes "Missing section stop" row with description "heading/paragraph/table/cell without stable section | blocked, no anchor emitted" but does not explicitly list `unstable_section_context` as a separate stop-path case.
- **反例/失败场景**: Implementation worker implements `missing_section_context` stop correctly (section id absent) but does not implement `unstable_section_context` stop (section id present but maps to multiple families). The ambiguity-resolution failure path is not mechanically tested, so unstable section ids may be accepted as stable, producing candidate anchors with incorrect `section_id`.
- **为什么有问题**: §10 explicitly distinguishes stable from unstable section contexts with concrete unstable conditions (heading path maps to multiple section families, only page proximity, keyword inference). The test matrix should have at least one case that triggers `unstable_section_context` to verify the implementation handles ambiguity correctly, not just absence.
- **直接证据**: §10 "A section context is unstable when: heading path maps to multiple section families; only page proximity is available; section is inferred from arbitrary keywords." §12 test matrix row "Missing section stop | heading/paragraph/table/cell without stable section | blocked, no anchor emitted" — does not distinguish missing from unstable.
- **影响**: 实施 Agent 可能遗漏 `unstable_section_context` stop path 的实现；heading path 多义匹配场景下可能错误接受不稳定的 section context
- **建议改法和验证点**: 在 §12 test matrix 中增加一行: "Unstable section stop | heading/paragraph/table/cell with section id present but heading path maps to multiple section families | blocked `unstable_section_context`, no anchor emitted". 验证点：实现代码必须对 §10 列出的每种 unstable 条件都有独立的 stop 路径。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## 5. Controller Binding Constraints Carry-through Assessment

| Binding Constraint (from controller judgment) | Plan Section | Assessment |
|---|---|---|
| Programmatic candidate/production boundary (DS-F1) | §6 Candidate Output Model Strategy | CARRIED — `CandidateEvidenceAnchorFields` is independent dataclass, not subclass of `EvidenceAnchor`; `to_evidence_anchor`/`as_evidence_anchor` methods explicitly forbidden; mapping functions return candidate wrapper types only |
| Module ownership in Fund documents candidate internals (DS-F2, MIMO-F1) | §5 Module Ownership Recommendation | CARRIED — exact path `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py`; Service/Host/UI/renderer/quality-gate direct access explicitly blocked |
| S1 parent-table resolution specified (DS-F3, MIMO-F2) | §8 S1 Full-schema Parent-table Resolution | CARRIED — 4-step deterministic priority chain; forbidden heuristics listed; `cannot_resolve_parent_table` stop on failure |
| S4/S5/S6 section hierarchy verification (DS-F4) | §10 Section Stability Rules | CARRIED — "implementation must first verify whether section hierarchy exists in the lightweight candidate object... otherwise it must accept low yield and fail closed" |
| Section stability rules (MIMO-F3) | §10 Section Stability Rules | CARRIED — stable/unstable criteria defined with concrete conditions; stop behavior explicit for both missing and unstable |
| Table-level `row_locator=null` default (MIMO-F4) | §7.4 Tables, §11 Row Locator Rules | CARRIED — `row_locator=null` by default; `row_locator="table:<ordinal>"` explicitly forbidden without ordinal basis |
| No-live test matrix (MIMO-F5) | §12 No-live Test Matrix | CARRIED — 16 test cases covering happy paths, stop paths, source-kind boundary, production isolation, metadata and containment |
| Paragraph `row_locator=null` (MIMO-F6) | §7.3 Paragraphs, §11 Row Locator Rules | CARRIED — `row_locator=null` always for paragraphs; paragraph/block identity in metadata/note |

## 6. Architecture Boundary Assessment

- Module location: correctly bound to `fund_agent/fund/documents/candidates/` (§5).
- Dependency direction: mapping module may depend on candidate representation models and locator helpers under `candidates/`; must not call Docling, parser cache, source helpers, PDF files, live acquisition, `FundDocumentRepository`, provider/LLM, analyzer or checklist commands (§5).
- Public contract: narrow callable surface `map_candidate_locator_to_anchor_candidate(...)` and `map_candidate_document_anchor_candidates(...)` returning candidate result types only (§5).
- Forbidden writes: explicit list in §4 prevents unauthorized scope expansion.
- Service/Host/UI containment: §16 review focus explicitly requires AgentMiMo to verify no direct external layer dependency; §12 includes "Service/Host/UI containment" test case.

## 7. Candidate/Production Isolation Assessment

- Programmatic boundary: `CandidateEvidenceAnchorFields` mirrors `EvidenceAnchor` fields but is not the production dataclass and must not subclass it (§6).
- Metadata enforcement: `CandidateEvidenceAnchorMapping` wraps fields with `candidate_source="docling"`, `candidate_only=True`, `field_correctness_status="not_proven"` (§6).
- No production-admission helpers: explicit prohibition of `to_evidence_anchor`, `as_evidence_anchor`, `to_production_anchor` or equivalent (§6).
- Test enforcement: "Tests must assert the public mapping API does not return bare `EvidenceAnchor` objects or `list[EvidenceAnchor]`" (§6).
- Stop condition: §15 line 3 "Implementation would return or store bare production `EvidenceAnchor` objects" triggers return to controller.

## 8. Parent-table Resolution Determinism Assessment

### S1 (§8)

Resolution is a strict 4-step priority chain:
1. Explicit parent table reference → deterministic
2. Structural containment in candidate JSON → deterministic
3. Shared table identifier → deterministic
4. Bbox containment (exactly one table on same page contains cell bbox) → deterministic, fails closed when zero or multiple tables contain cell

All fallbacks are forbidden: nearest-previous-table, page-only matching, heading/title text similarity, synthetic table ids. `cannot_resolve_parent_table` stop on any failure.

### S4/S5/S6 (§9)

Resolution is tuple-based: `table_id + table.page_number + cell_index + row_start + column_start`. All five components must be present and unique under the same table_id. `ambiguous_cell_tuple` stop on duplicate; `missing_parent_table_context`/`missing_page_number`/`missing_cell_position` stops on absent components. Explicit fail-closed: "If future evidence shows S4/S5/S6 have no table entry to match `table_id`, implementation must fail closed for cell anchors instead of creating table ids from cell tuples."

## 9. Section Stability Mechanical Testability Assessment

§10 defines stability with concrete, testable conditions:

**Stable when** (at least one):
- explicit section id maps one-to-one to known annual-report section family
- enclosing section hierarchy contains block without multiple possible parent sections
- normalized heading path deterministically maps to one section family with no multi-match

**Unstable when**:
- section id missing
- heading path maps to multiple section families
- only page proximity available
- section inferred from arbitrary keywords
- section depends on fund-analysis template chapter inference

Each condition is mechanically testable by checking: presence/absence of section id, count of heading-path matches to known section families, availability of structural hierarchy vs page proximity only, keyword vs structural inference. Stop behavior is explicit for both missing and unstable cases.

## 10. Row Locator Mechanical Testability Assessment

§11 defines a deterministic format per anchor kind:

| Anchor kind | `row_locator` | Testability |
|---|---|---|
| Heading | `null` | Assert null |
| Paragraph | `null` | Assert null |
| Table-level | `null` | Assert null |
| Cell | `cell:r<row_start>:c<column_start>:idx<cell_index>` | Parse and verify format; S1 may omit `idx` when no `cell_index` exists |

The cell format is mechanically parseable and verifiable. The constraint "Cell `row_locator` must not be used to compensate for missing `table_id`, page or section" is enforceable by checking that stop conditions fire before row_locator is set.

## 11. No-live Test Matrix Assessment

§12 defines 16 test cases:

| Category | Cases | Coverage |
|---|---|---|
| S1 happy paths | heading, paragraph, table, cell (parent pointer), cell (bbox) | 5 |
| S1 stop paths | ambiguous bbox, page-only table | 2 |
| S4/S5/S6 happy path | exact tuple match | 1 |
| S4/S5/S6 stop paths | missing tuple member, duplicate tuple | 2 |
| Section/page stops | missing section, missing page | 2 |
| Source-kind boundary | no new production source_kind | 1 |
| Metadata | required candidate metadata present | 1 |
| Production isolation | no bare EvidenceAnchor returned | 1 |
| Containment | import scan / static assertion | 1 |

Coverage target: 80% single-file. Gap: `unstable_section_context` stop path not explicitly listed (see MIMO-IMPL-F1).

## 12. Non-goal Compliance Assessment

The plan correctly avoids:
- Production parser replacement (§1/§2/§15)
- Source truth or full field correctness claims (§1/§3/§18)
- Readiness/release/PR claims (§1/§15/§18)
- Live/network/EID/FDR/PDF/source acquisition (§2/§13/§15)
- Provider/LLM/analyze/checklist/golden/readiness/release/PR commands (§13/§15)
- Unrelated untracked residue as proof (§2/§15)
- Design/control/startup doc updates (§14)

## 13. Open Questions

| # | Question | Recommended owner |
|---|---|---|
| Q1 | Should the implementation explicitly forbid importing production `EvidenceAnchor` in the mapping module, or is the wrapper-type + no-production-return constraint sufficient? | Implementation gate |

## 14. Accepted / Rewritten / Rejected / Deferred Findings

| Finding | Disposition | Reason |
|---------|-------------|--------|
| MIMO-IMPL-F1 | accepted-candidate | Low severity test gap; `unstable_section_context` stop path should be explicitly tested to match §10 distinction from `missing_section_context` |

## 15. Residuals

| Residual | Owner | Next Handling |
|----------|-------|---------------|
| MIMO-IMPL-F1: add `unstable_section_context` stop-path test to matrix | Implementation gate | Add test case in §12 or verify during implementation |
| EvidenceAnchor mapping implementation remains open | documents/schema owner | `Docling EvidenceAnchor Mapping No-live Implementation Gate` |
| Field-level correctness beyond selected facts remains unproven | baseline qualification owner | Comparative correctness gate |
| Production baseline disposition remains open | baseline qualification owner | Baseline disposition gate |
| Release/readiness remains `NOT_READY` | release owner | Future readiness gate only |

## 16. Reviewer Self-Check

- [x] Reviewed target, scope, source of truth and assumptions tested are written
- [x] Findings are evidence-based, adversarial, actionable, and not style/nit/speculation
- [x] Open questions, residual risks, tracking destination are separate from findings
- [x] Conclusion is `pass`, `pass-with-risks`, or `fail`
- [x] Output path uses timestamp format

## 17. Final Recommendation

The plan is thorough and code-generation-ready. It fully carries all 10 controller binding constraints:

- Programmatic candidate/production isolation via `CandidateEvidenceAnchorFields` wrapper type (DS-F1)
- Module ownership explicitly bound to `fund_agent/fund/documents/candidates/` (DS-F2, MIMO-F1)
- S1 parent-table resolution with deterministic 4-step priority chain and forbidden heuristics (DS-F3, MIMO-F2)
- S4/S5/S6 tuple-based resolution with fail-closed semantics (DS-F4)
- Section stability rules with concrete stable/unstable criteria (MIMO-F3)
- Table-level `row_locator=null` default (MIMO-F4)
- No-live test matrix with 16 cases (MIMO-F5)
- Paragraph `row_locator=null` always (MIMO-F6)
- Validation commands scoped to no-live only
- Explicit non-goal enforcement and stop conditions

One low-severity finding (MIMO-IMPL-F1): the test matrix should include an explicit `unstable_section_context` stop-path case to match §10's distinction between missing and unstable section contexts. This is a minor gap that does not block the plan.

```text
VERDICT: PASS_WITH_FINDINGS
```
