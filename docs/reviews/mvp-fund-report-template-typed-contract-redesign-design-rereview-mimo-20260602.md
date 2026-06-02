# MVP fund report template typed contract redesign design — re-review (AgentMiMo)

## Reviewer Self-Check

- Role: independent re-review worker (AgentMiMo), not controller.
- Gate: `MVP fund report template typed contract redesign gate`, classification `heavy`.
- Re-review scope: whether accepted findings from MiMo F1-F12 and DS F1-F8 were adequately fixed or converted into explicit residual/precondition/deferred gate.
- Original review: `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-review-mimo-20260602.md`
- Peer review: `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-review-ds-20260602.md`
- Fixed design: `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-20260602.md`
- Fix evidence: `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-review-fix-evidence-20260602.md`
- Actions intentionally not taken: no implementation, no code, no template truth replacement, no `contracts.py`/auditor/provider budget/score-loop changes, no commit/push/PR, no edit to any file except this single re-review artifact.

---

## Per-Finding Status Mapping

### MiMo Original Findings (F1-F12)

| Finding | Description | Status | Rationale |
|---------|-------------|--------|-----------|
| MiMo F1 | audit_focus 控制边界歧义，可能侵入程序化审计领域 | **fixed** | Decision 7 now explicitly states "Adding their names to `audit_focus` does not implement those checks and does not let LLM-only focus substitute for programmatic blockers." Composition rule added: evidence predicates control clause applicability, `audit_focus` never controls programmatic participation. Four new `AuditFocusLiteral` items are bounded to LLM semantic emphasis; corresponding programmatic checks are explicitly deferred to separate extension gates. |
| MiMo F2 | `EvidenceAvailability.source_strength_by_requirement` 语义未定义 | **fixed** | Decision 2 now states: "`source_strength_by_requirement` is not accepted as an implementable field in this gate. A later gate may add it only after defining strength levels." Field is moved to Deferred with explicit rationale. |
| MiMo F3 | `MustNotCoverClause.allowed_contexts` 程序化审计行为未指定 | **fixed** | Decision 3 now states: "Programmatic C2 is expected to use `allowed_contexts` when implementing evidence-conditional `must_not_cover`; otherwise the retained Ch3 C2 failure mode is not fixed." Each context type (`required_label`, `evidence_gap_statement`, `anchor_caption`, `quote`) has explicit semantic constraints. |
| MiMo F4 | 外部草案 timeout 根因分析与控制器证据不一致 | **fixed** | Decision 3 non-goals and "What Must Not Enter Accepted Future Design Yet" both explicitly reject "External draft D-2 style timeout root-cause allocation or percentages" and state Ch2/Ch4/Ch6 timeout evidence remains provider runtime gate evidence because retained diagnostics show `small_prompt_provider_timeout`. |
| MiMo F5 | evidence-conditional 声明基于单一章节证据 | **fixed** | Recommendation text now reads: "Accept evidence-conditional `must_not_cover` as the most important future contract change **for the retained Ch3 failure mode. Broader applicability across other chapters is plausible but not proven by this gate and requires additional evidence.**" |
| MiMo F6 | `quote` 上下文边界条件未定义 | **fixed** | Decision 3 now defines: "`quote` is limited to a bounded direct quotation or source label needed for evidence traceability. A quote may mention a forbidden phrase, but it cannot be used to add, imply, or launder a positive conclusion in the writer's own voice." |
| MiMo F7 | EvidenceAvailability 与 ChapterFactProjection 关系未定义 | **fixed** | Decision 2 now explicitly states: "`EvidenceAvailability` is a derived supplemental availability view over same-source chapter facts and anchors. It does not replace the current `ChapterFactProjection` unless a later gate explicitly accepts that replacement." |
| MiMo F8 | Ch7 依赖链在 Ch2 拆分推迟下未闭合 | **fixed** | Decision 5 now states: "If a later structural gate accepts a Ch2 split, the Ch7 dependency chain and Ch0 final-assembly preconditions must be revisited in the same structural gate." Decision 6 also adds: "updated Ch7 `consumes_chapter_conclusions` dependency chain, including how performance, attribution, and cost conclusions feed final judgment." |
| MiMo F9 | 接受 typed ChapterContract 与拒绝 Ch2 拆分一致性未论证 | **fixed** | Decision 6 now explicitly states: "Typed contract precision and structural chapter split are independent design dimensions: this gate accepts the former and defers the latter." |
| MiMo F10 | Ch2 拆分推迟但 0+9 重编号未显式隔离 | **fixed** | Decision 1 now states: "Accepted `chapter_id` range remains `0-7`, matching the current 8 chapter template. Any chapter renumbering, 0+9 structure, 0+10 structure, or public chapter count change requires a separate structural gate." Decision 6 non-goals also state: "Do not write `0+9` or `0+10` as accepted future design from this gate." |
| MiMo F11 | 部分证据可用性场景审计行为未设计 | **fixed** | Decision 3 now includes a "Partial availability behavior" subsection defining: (a) bounded conclusions over available evidence only with explicit missing boundary naming; (b) Ch3 specific example where turnover-only cannot support positive `言行一致`; (c) programmatic audit treating full forbidden conclusion as blocked when any predicate component is missing; (d) prohibition on converting missing evidence into positive conclusions through softer quasi-positive phrasing. |
| MiMo F12 | `MustAnswerClause.fallback` 与 `RequiredOutputItem.when_evidence_missing` 语义重叠 | **fixed** | Decision 1 now states: "`MustAnswerClause` must not introduce an overlapping fallback system at this gate. Missing-evidence behavior is governed by `RequiredOutputItem.when_evidence_missing`." Decision 4 confirms: "`RequiredOutputItem.when_evidence_missing` is the only accepted missing-evidence behavior in this gate. Clause-level fallback is deferred." |

### DS Original Findings (F1-F8)

| Finding | Description | Status | Rationale |
|---------|-------------|--------|-----------|
| DS F1 | Chinese assertion polarity robustness — handoff risk | **fixed** | Now a mandatory precondition in Handoff Criteria: "Run a Chinese assertion polarity/quasi-positive feasibility or calibration step before implementing polarity-bearing `MustNotCoverClause` behavior; brittle global phrase matching is not an accepted solution." Also in Decision 3 non-goals: "Do not accept brittle global Chinese phrase matching as the implementation solution for polarity/quasi-positive detection." |
| DS F2 | typed subcontracts concept ambiguous | **fixed** | Decision 6 now explicitly states: "These units must remain inside a single `ChapterContract(chapter_id=2)`. They must not have independent chapter ids, must not appear as separate chapter-matrix rows, must not change renderer/public chapter count, and must not imply acceptance of 0+9/0+10 numbering." |
| DS F3 | audit_focus / evidence-conditional must_not_cover interaction | **fixed** | Decision 3 composition rule now states: "`applies_when` gates clause applicability. If the evidence predicate is false, that specific clause does not participate in audit." and "`audit_focus` only affects bounded LLM semantic audit emphasis and repair hint grouping in this gate." and "Evidence-disabled clauses are not checked. Evidence-enabled clauses are checked programmatically where a programmatic checker exists, regardless of `audit_focus`." |
| DS F4 | Ch0 masking unsafe Ch7 | **fixed** | Decision 5 now includes: "final assembly constraint: fail closed if any required body chapter, currently chapters 1-6, is not accepted" and "Ch0 must not mask unsafe Ch7. Final assembly must fail closed when required body chapters are incomplete, rejected, or unaccepted, even if a Ch7-looking bundle exists." |
| DS F5 | `first_class_facets` scope undefined | **fixed** | Decision 1 future contract shape no longer includes `first_class_facets`. Handoff Criteria explicitly defers: "`first_class_facets` implementation and facet-respect programmatic wiring are deferred to a separate facet wiring/programmatic audit gate." |
| DS F6 | EvidenceAvailability missing year-tier availability | **fixed** | Decision 2 future contract shape now includes `data_tier_availability: map[Literal["1Y","3Y","5Y"], available | missing | not_applicable | unreviewed]` and `available_report_years`. Decision 2 text includes Ch2-style example with `data_tier_availability["1Y"]`, `data_tier_availability["3Y"]`, `data_tier_availability["5Y"]`. |
| DS F7 | required_output block semantics undefined | **fixed** | Decision 4 now defines: "`block` is reserved for core facts whose absence makes the chapter unsafe. A missing item should block only when any substantive conclusion in that chapter would become unreliable, when downstream Ch7 final judgment would be unsafe, or when the contract authoring gate explicitly marks the item as non-degradable and reviewers accept that item-level reason." |
| DS F8 | absent explicit handoff criteria | **fixed** | A full "Handoff Criteria" section was added with: accepted decisions for next gate, deferred/rejected items, mandatory preconditions before implementation, and next likely gate options. |

---

## Status Summary

| Status | Count | Findings |
|--------|-------|----------|
| fixed | 20 | MiMo F1-F12, DS F1-F8 |
| partially fixed | 0 | — |
| still open | 0 | — |
| evidence invalidated | 0 | — |

---

## New Blocker Check

No new blockers introduced by the fixes. All changes are tightening, clarifying, deferring, or adding preconditions. No fix introduces new ambiguity, scope creep, or boundary violations.

One observation: the fix for MiMo F5 (narrowing "most important" to "for Ch3") is effective but the original broad claim text is still present in Decision 3's opening line ("Accept evidence-conditional `must_not_cover` as the most important future contract change for the retained Ch3 failure mode"). The qualifying phrase "for the retained Ch3 failure mode" is correctly appended, making the scoping clear. This is acceptable.

---

## Residual Risks

These are not fix failures but pre-existing design-level residuals that the controller must track:

1. **Chinese polarity/quasi-positive detection feasibility**: Now correctly a mandatory precondition, but no feasibility or calibration work has been done yet. This remains the highest-risk implementation blocker.
2. **Programmatic `allowed_contexts` matching**: The design states programmatic C2 "is expected to use `allowed_contexts`" but the matching rules (how to distinguish `quote` from writer statement in code) are not yet designed.
3. **`EvidenceAvailability` derivation from `ChapterFactProjection`**: The relationship is clarified (derived supplemental view), but the derivation mechanism is not designed.
4. **Provider runtime timeout for Ch2/Ch4/Ch6**: Correctly excluded from this gate. Remains a separate provider runtime budget gate concern.
5. **`block` item-level criteria**: The semantics are defined but no specific items have been marked as `block` yet — this is expected to happen in the contract authoring gate.

---

## Conclusion

**Pass.** All 20 accepted findings (MiMo F1-F12, DS F1-F8) are adequately fixed or converted into explicit residual/precondition/deferred gate entries. No partially-fixed or still-open findings. No new blockers introduced by fixes. The design artifact is handoff-ready for the next gate.

---

## Validation

```bash
git diff --check -- docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-rereview-mimo-20260602.md
```

Expected: no whitespace diagnostics (new file).

Secret-safety statement: this artifact contains no API key, Authorization header, Bearer token, cookie, password, private key, raw provider response, raw prompt body, or secret-bearing runtime payload. It references only safe local artifact paths, safe diagnostic labels, and short design excerpts needed for re-review traceability.
