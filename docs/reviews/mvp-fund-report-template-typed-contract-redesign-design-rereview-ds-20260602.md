# MVP fund report template typed contract redesign design — re-review (AgentDS)

## Re-Reviewer Self-Check

- Role: AgentDS as independent re-review worker, not controller.
- Gate: `MVP fund report template typed contract redesign gate`.
- Re-review target: `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-20260602.md` (post-fix).
- Source reviews: AgentDS F1-F8 (`*-design-review-ds-20260602.md`), AgentMiMo F1-F12 (`*-design-review-mimo-20260602.md`).
- Fix evidence: `*-design-review-fix-evidence-20260602.md`.
- Scope: re-review only whether accepted findings from DS F1-F8 and MiMo F1-F12 were adequately fixed or converted into explicit residual/precondition/deferred gate. No new broad review.
- Actions taken: read all four source artifacts, cross-checked each finding against the fixed design text, verified evidence chains.
- Actions intentionally not taken: no Gateflow/Phaseflow controller start, no implementation, no code/test/template/provider/auditor/runtime changes, no edit to design artifact or truth docs, no commit/push/PR.

---

## Per-Finding Status Mapping

### AgentDS Findings

| Finding | Severity | Status | Evidence |
|---------|----------|--------|----------|
| DS F1: Chinese assertion polarity robustness — handoff risk | MEDIUM | **fixed** | Decision 3 non-goals now require feasibility/calibration step before implementation; brittle phrase matching explicitly rejected. Handoff Criteria §Mandatory preconditions echoes this. |
| DS F2: typed subcontracts for Ch2 — concept ambiguous | LOW | **fixed** | Decision 6 now explicitly constrains subcontracts to internal organizational units within a single `ChapterContract(chapter_id=2)`, forbids independent chapter ids, matrix rows, and public chapter count changes. Independence of typed contract precision vs structural split explicitly stated. |
| DS F3: audit_focus / evidence-conditional must_not_cover interaction | MEDIUM | **fixed** | Decision 3 adds explicit composition rule: evidence predicates gate clause applicability; programmatic C2 participation is independent of audit_focus; audit_focus omission must not disable programmatic blockers. Decision 7 reinforces: audit_focus never controls programmatic participation. |
| DS F4: Ch0 masking unsafe Ch7 — risk unmitigated | MEDIUM | **fixed** | Decision 5 now requires final assembly fail-closed when any required body chapter (1-6) is not accepted, even if a Ch7-looking bundle exists. Future Ch2 split must revisit Ch7 dependency chain. |
| DS F5: first_class_facets scope undefined | LOW | **fixed** | `first_class_facets` removed from accepted `ChapterContract` shape in Decision 1. Deferred to separate facet wiring/programmatic audit gate. |
| DS F6: EvidenceAvailability missing year-tier availability | LOW | **fixed** | Decision 2 now includes `data_tier_availability: map[Literal["1Y","3Y","5Y"], available \| missing \| not_applicable \| unreviewed]` and `available_report_years`. |
| DS F7: required_output block semantics undefined | LOW | **fixed** | Decision 4 now defines block criteria: used only when missing evidence makes substantive conclusion unreliable, downstream Ch7 unsafe, or contract authoring gate explicitly marks item non-degradable. Decision 1 defers overlapping MustAnswerClause fallback; Decision 4 confirms `when_evidence_missing` as sole accepted mechanism. |
| DS F8: absent explicit handoff criteria | LOW | **fixed** | Full Handoff Criteria section added with accepted decisions, deferred/rejected items, mandatory preconditions, and likely next gate options. |

### AgentMiMo Findings

| Finding | Severity | Status | Evidence |
|---------|----------|--------|----------|
| MiMo F1: audit_focus 控制边界歧义 | HIGH | **fixed** | Decision 7 now explicitly states programmatic checks for `data_availability_match`, `evidence_gap_declaration`, `cross_chapter_consistency`, `first_class_facet_respect` are separate programmatic audit extension gates. audit_focus controls only LLM semantic emphasis and repair hint grouping. |
| MiMo F2: source_strength_by_requirement 语义未定义 | HIGH | **fixed** | Decision 2: `source_strength_by_requirement` is not accepted as implementable; deferred unless later gate defines strength levels, relationship to availability/data-tier flags, and audit semantics. |
| MiMo F3: allowed_contexts 程序化审计行为未指定 | HIGH | **fixed** | Decision 3: "Programmatic C2 is expected to use allowed_contexts when implementing evidence-conditional must_not_cover; otherwise the retained Ch3 C2 failure mode is not fixed." Each context (`required_label`, `evidence_gap_statement`, `anchor_caption`, `quote`) has bounded semantics. |
| MiMo F4: timeout 根因分析与控制器证据不一致 | MEDIUM | **fixed** | External draft D-2 timeout percentage/root-cause allocation explicitly rejected in recommendation summary, "What Must Not Enter", and Handoff Criteria. Ch2/Ch4/Ch6 timeout evidence remains provider runtime gate evidence. |
| MiMo F5: "最重要" 声明基于单一章节证据 | MEDIUM | **fixed** | Decision 3 narrowed to "the most important future contract change for the retained Ch3 failure mode. Broader applicability across other chapters is plausible but not proven by this gate." |
| MiMo F6: quote 上下文边界条件未定义 | MEDIUM | **fixed** | Decision 3 defines `quote` boundary: bounded direct quotation or source label for traceability; may mention forbidden phrase but cannot add, imply, or launder positive conclusion in writer's own voice. |
| MiMo F7: EvidenceAvailability 与 ChapterFactProjection 关系未定义 | MEDIUM | **fixed** | Decision 2: "EvidenceAvailability is a derived supplemental availability view over same-source chapter facts and anchors. It does not replace the current ChapterFactProjection unless a later gate explicitly accepts that replacement." |
| MiMo F8: Ch7 依赖链在 Ch2 拆分推迟下未闭合 | MEDIUM | **fixed** | Decision 6: "If a later controller accepts a split… updated Ch7 consumes_chapter_conclusions dependency chain, including how performance, attribution, and cost conclusions feed final judgment." |
| MiMo F9: typed ChapterContract 与拒绝 Ch2 拆分的一致性未论证 | LOW | **fixed** | Decision 6: "Typed contract precision and structural chapter split are independent design dimensions: this gate accepts the former and defers the latter." |
| MiMo F10: 0+9 重编号未被显式隔离 | LOW | **fixed** | Decision 1: "Accepted chapter_id range remains 0-7, matching the current 8 chapter template. Any chapter renumbering, 0+9 structure, 0+10 structure, or public chapter count change requires a separate structural gate." |
| MiMo F11: 部分证据可用性场景审计行为未设计 | MEDIUM | **fixed** | Decision 3 adds full "Partial availability behavior" subsection: bounded conclusions only over available evidence with explicit missing-boundary naming; positive/quasi-positive conclusions blocked when required predicate components are missing; quasi-positive phrasing like "倾向一致" explicitly rejected pending polarity calibration. |
| MiMo F12: MustAnswerClause.fallback 与 RequiredOutputItem.when_evidence_missing 语义重叠 | MEDIUM | **fixed** | Decision 1: "MustAnswerClause must not introduce an overlapping fallback system at this gate." Decision 4: "RequiredOutputItem.when_evidence_missing is the only accepted missing-evidence behavior in this gate. Clause-level fallback is deferred; if both mechanisms are later introduced, block must take precedence." |

---

## Assessment of DS Residual Risks (RR-1 through RR-4)

| Residual Risk | Post-Fix Status |
|---------------|-----------------|
| RR-1: audit_focus subsetting before evidence-conditional | Mitigated by Decision 3 composition rule: evidence predicates control clause applicability independently of audit_focus. |
| RR-2: polarity field implementation sensitivity | Converted to mandatory precondition in Handoff Criteria; brittle phrase matching explicitly rejected. Remains a genuine implementation risk but is now gate-gated. |
| RR-3: consumes_chapter_conclusions dependency graph expansion | Still a residual risk; only Ch0 uses it currently. Handoff Criteria flags that Ch2 split would require dependency chain update. Acceptable as deferred concern. |
| RR-4: EvidenceAvailability boundary (Fund vs Service) | Mitigated by Decision 2: EvidenceAvailability is Fund/Agent derived from ChapterFactProjection, not Service-constructed. |

---

## New Blocker Check

No new blockers introduced. All fixes are narrowing (constraints, deferrals, clarifications) rather than expanding. Specific checks:

- Decision 3 composition rule (evidence predicate vs audit_focus) is internally consistent with Decision 7.
- Decision 4 block criteria are concrete and fail-safe.
- Decision 1 removal of first_class_facets doesn't create gaps — the field is deferred, not deleted.
- Decision 2 deferral of source_strength_by_requirement doesn't break other EvidenceAvailability fields.
- Overlap resolution between MustAnswerClause fallback and RequiredOutputItem.when_evidence_missing is clear: the latter is sole mechanism, the former is deferred.
- Partial availability rules in Decision 3 are consistent with the polarity constraint (quasi-positive blocked when evidence missing).

---

## Conclusion

**Verdict: pass.** All 20 accepted findings (DS F1-F8, MiMo F1-F12) are adequately fixed. No findings remain open. No evidence was invalidated. No new blockers were introduced by the fixes.

The fixed design is tighter, more defensive against misreading, and ready for controller judgment. The Handoff Criteria section provides clear input for the next gate worker.

### Residual Risks / Open Questions (carried forward)

1. Chinese assertion polarity/quasi-positive detection feasibility — now a mandatory precondition, not an open question.
2. Programmatic audit extensions (data_availability_match, evidence_gap_declaration, cross_chapter_consistency, facet_respect) — deferred to separate gates.
3. Provider runtime timeout investigation for Ch2/Ch4/Ch6 — outside this design gate scope.
4. Ch2 structural split and 0+9/0+10 numbering — deferred to separate structural gate.
5. `first_class_facets` implementation and facet-respect wiring — deferred to separate gate.
6. `source_strength_by_requirement` definition — deferred unless separately defined.
7. Next gate scope selection (Ch3-only calibration vs broader typed contract schema plan) — controller decision required.

---

## Validation

```bash
git diff --check -- docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-rereview-ds-20260602.md
```

Secret-safety statement: this artifact contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw prompt body, or secret-bearing runtime payload. It references only safe local artifact paths, safe diagnostic labels, and short design excerpts needed for re-review traceability.
