# P12-S1 ITEM_RULE Renderer / Audit Compliance Plan Review — AgentMiMo

- **Reviewer**: AgentMiMo (independent plan reviewer)
- **Gate**: `P12-S1 ITEM_RULE renderer/audit compliance plan/review`
- **Plan artifact**: `docs/reviews/p12-s1-item-rule-renderer-audit-compliance-plan-20260522.md`
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`
- **Previous planning artifact**: `docs/reviews/post-p11-second-follow-up-planning-20260522.md`
- **Code reviewed**: `fund_agent/fund/template/item_rules.py`, `fund_agent/fund/template/renderer.py`, `fund_agent/fund/audit/audit_programmatic.py`, `tests/fund/audit/test_audit_programmatic.py`, `tests/fund/template/test_renderer.py`
- **Baseline**: `79fb3e3`

---

## Verdict: PASS_WITH_FINDINGS

Plan is architecturally sound and correctly scoped. Three findings require clarification or minor plan amendment before implementation proceeds.

---

## Review Summary

The plan correctly identifies ITEM_RULE as the next deterministic compliance gap after P11. The core design — renderer produces `item_rule_decisions` from `classified_fund_type`, audit consumes the same tuple — is clean, deterministic, and respects all MVP boundaries. Implementation slicing is correctly ordered (plumbing → rendering → audit → docs). Non-goals are well-defined.

However, the plan has an internal contradiction on fail-closed semantics that will impact existing tests, lacks explicit test coverage for 4 of 6 fund types, and has an ambiguity on evidence anchoring for new segments that risks evidence fabrication if implemented naively.

---

## Finding 1: Fail-closed check scope contradiction with existing tests

**Severity**: HIGH

**Evidence**:

Section 4.3 states:
> "If decisions are absent while report Markdown/chapter blocks exist, audit should not silently pass ITEM_RULE compliance."

The compatibility note then states:
> "the fail-closed 'missing ITEM_RULE decisions' check should trigger only when enough report/chapter input exists to claim C2 compliance, or affected tests should explicitly pass decisions when they expect full C2 pass"

These two statements are in tension. The first is absolute: chapter_blocks present + decisions empty → C2 issue. The second softens it with "enough report/chapter input" — an undefined threshold.

**Impact analysis from code review**:

Current audit tests construct `ProgrammaticAuditInput` in two patterns:

| Pattern | chapter_blocks | item_rule_decisions | Count | ITEM_RULE check impact |
|---|---|---|---|---|
| C2 tests via `_rendered_audit_input(use_explicit_blocks=True)` | non-empty | not provided (default `()`) | 5 tests | **WOULD FAIL** — chapter_blocks non-empty, decisions empty |
| C2 tests via direct construction with chapter_blocks | non-empty | not provided | 4 tests | **WOULD FAIL** |
| L1/R1/R2 tests, no chapter_blocks | `()` (default) | not provided | 10 tests | safe — check skips when blocks empty |
| Splitter fallback tests | `()` (default) | not provided | 2 tests | safe |

After implementation, **9 existing C2 tests will break** because they provide chapter_blocks but no item_rule_decisions. The `_rendered_audit_input` helper constructs `ProgrammaticAuditInput` independently from the renderer, so it won't automatically receive decisions.

**Root cause**: The compatibility note acknowledges the problem but frames it as "affected tests should explicitly pass decisions" without quantifying the blast radius. The plan should either:

1. **Amend**: Explicitly state that the fail-closed check fires whenever `chapter_blocks` is non-empty and `item_rule_decisions` is empty, and enumerate the ~9 tests that need updating in Slice 3, OR
2. **Amend**: Make the check conditional on a new boolean flag (e.g., `item_rule_compliance_requested`) so tests that don't care about ITEM_RULE can opt out cleanly.

**Recommended fix**: Option 1 is simpler and more honest. Update Slice 3 step 4 to list the specific test update scope: "Update `_rendered_audit_input` helper to pass `item_rule_decisions` from the render result; update 4 direct-construction C2 tests to pass explicit decisions tuple."

---

## Finding 2: Missing test coverage for enhanced_index, bond_fund, qdii_fund, fof_fund

**Severity**: MEDIUM

**Evidence**:

Section 6 (Edge Cases) correctly identifies behavior for all 6 fund types:

| Fund type | Expected ITEM_RULE behavior |
|---|---|
| `active_fund` | render manager philosophy + alpha breakdown; delete index constituents + tracking error |
| `index_fund` | render index constituents + tracking error; delete manager philosophy + alpha breakdown |
| `enhanced_index` | render index constituents + alpha breakdown + tracking error; delete manager philosophy |
| `bond_fund` | all 4 conditional rules delete |
| `qdii_fund` | all 4 conditional rules delete |
| `fof_fund` | all 4 conditional rules delete |

But Slice 1 step 5 only requires tests for:
> "active fund, index fund, enhanced index, missing identity, present identity without classified_fund_type"

**Gap**: `bond_fund`, `qdii_fund`, `fof_fund` have no renderer integration test. Current renderer tests only cover `active_fund` and `index_fund` end-to-end; `enhanced_index` also lacks renderer test coverage. While `test_item_rules.py` covers rule evaluation for all types, the renderer-to-audit integration path is untested for 4 of 6 types.

**Impact**: If a renderer segment helper has a fund-type dispatch bug (e.g., `enhanced_index` accidentally renders manager philosophy), no test catches it.

**Recommended fix**: Add to Slice 1 step 5 or Slice 2:
- `enhanced_index` renders index constituents + alpha breakdown + tracking error, deletes manager philosophy.
- At least one of `bond_fund` / `qdii_fund` / `fof_fund` verifies all 4 conditional segments are deleted.

Parametrize the existing `_render_input(fund_type=...)` fixture pattern to cover all 6 types for ITEM_RULE segment presence/absence assertions.

---

## Finding 3: Evidence anchoring ambiguity for new segments

**Severity**: MEDIUM

**Evidence**:

Section 4.2 states:
> "use existing `_evidence_line(...)` where a segment uses a source field or attribution"

Section 6 states:
> "New segments must reuse existing extracted-field or R=A+B-C anchors where available and use explicit `未披露`/`数据不足` rather than fabricating source facts."

**Ambiguity**: The four new segments lack dedicated data sources in `StructuredFundDataBundle`:

| Segment | Available data source | Evidence anchor source |
|---|---|---|
| `#### 指数编制规则与成分股` | `basic_identity`, `benchmark` (indirect) | **No direct source** — benchmark text mentions index name but not constituents or methodology |
| `#### 基金经理投资哲学` | `manager_strategy_text` (§4) | Has anchors from `manager_strategy_text.anchors` |
| `#### 超额收益分年度拆解` | `rabc_attributions` | Has anchors from `RabcAttribution.anchors` |
| `#### 跟踪误差分析` | **No source** — plan says "Current P1/P2 does not provide tracking error" | Must use `数据不足` |

Only 2 of 4 segments have clear evidence anchor sources. For index constituents, the renderer would need to reuse `benchmark.anchors` or `basic_identity.anchors`, but these don't actually contain index methodology or constituent data — they contain benchmark text and fund identity. Using them as evidence for a segment about "指数编制规则与成分股" would be misleading.

**Risk**: Implementor might either (a) reuse mismatched anchors (benchmark text anchors as evidence for constituent analysis), or (b) always use `数据不足` even when some data is available, making the segment uninformative.

**Recommended fix**: Add a clarification to Slice 2 step 5:
- `指数编制规则与成分股`: Use `benchmark.anchors` only for benchmark name reference; for index methodology and constituents, render `数据不足` with evidence line citing the benchmark anchor. Do not claim benchmark text contains constituent data.
- `跟踪误差分析`: Always render `数据不足` with available `rabc_attributions` anchors where relevant; do not calculate or infer tracking error.

---

## Finding 4: docs/implementation-control.md update scope

**Severity**: LOW

**Evidence**:

Section 2 (Non-goals) states:
> "不改 `docs/implementation-control.md`"

But the phaseflow protocol in `AGENTS.md` and `docs/implementation-control.md` itself requires updating the Active Gate Ledger and Phase History Index when phases transition. The Startup Packet's "next entry point" field needs to advance from `P12-S1 plan/review` to `P12-S1 implementation` after plan acceptance.

**Assessment**: The non-goal likely means "don't change implementation-control.md's design rules or phase definitions" — not "don't update phase status tracking." This is standard control doc maintenance, not a design change. But the wording is ambiguous.

**Recommended fix**: Amend the non-goal to: "不改 `docs/implementation-control.md` 的设计规则、phase 定义或验证要求；phase 状态跟踪按 phaseflow 正常维护。"

---

## Positive Assessment

The following aspects of the plan are well-designed:

1. **Single decision source**: Renderer produces decisions, audit consumes them. No divergent inference paths. This is the correct first-principles approach.

2. **Implementation slicing order**: Plumbing → rendering → audit → docs. Each slice builds on the previous. No circular dependencies.

3. **Fail-closed semantics mirror existing patterns**: Missing identity → empty decisions (matches `_resolve_lens_application_plan`). Present identity without classified_fund_type → `ValueError` (matches existing preferred_lens behavior).

4. **Facets=() enforcement**: Explicitly prevents prose-based facet inference. Maintains deterministic boundaries.

5. **No FQ5 behavior change**: Correctly identifies that FQ5 proves template applicability, not renderer compliance. Avoids scope creep.

6. **Deterministic MVP compliance**: No LLM, Host, Engine, tool loop, Evidence Confirm, or RepairContract. Pure Python deterministic logic.

7. **Segment marker validation**: Using manifest `segment_markers_any` instead of ordinary prose prevents false positives. The `_FORBIDDEN_SEGMENT_MARKERS` set in item_rules.py provides additional protection.

8. **bond/qdii/fof handling**: Correctly identifies that all 4 built-in conditional rules delete for these types. No special-casing needed.

---

## Severity Matrix

| # | Finding | Severity | Category | Fix scope |
|---|---|---|---|---|
| 1 | Fail-closed check scope contradiction | HIGH | Audit semantics / test compatibility | Clarify plan wording + enumerate test update scope in Slice 3 |
| 2 | Missing fund type test coverage | MEDIUM | Test coverage | Add enhanced_index + one of bond/qdii/fof to Slice 1 or 2 test requirements |
| 3 | Evidence anchoring ambiguity | MEDIUM | Evidence integrity | Clarify per-segment evidence strategy in Slice 2 |
| 4 | Control doc update scope | LOW | Documentation | Amend non-goal wording |

---

## Recommendation

**PASS_WITH_FINDINGS**. Plan is accepted pending:

1. Clarify Finding 1: Either commit to "chapter_blocks non-empty + decisions empty → C2 issue" and enumerate ~9 tests to update, or define the conditional trigger explicitly.
2. Address Finding 2: Add `enhanced_index` and at least one non-triggering fund type to Slice 1/2 test requirements.
3. Address Finding 3: Add per-segment evidence source clarification to Slice 2.
4. Optionally address Finding 4: Tighten non-goal wording.

No changes to the core architecture, contracts, slicing order, or non-goals are needed.
