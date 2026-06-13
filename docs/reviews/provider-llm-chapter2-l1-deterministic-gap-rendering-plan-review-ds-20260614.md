# Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Plan Review — AgentDS

Date: 2026-06-14

Role: AgentDS reviewer (not controller)

Gate: `Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Planning Gate`

Review target: `docs/reviews/provider-llm-chapter2-l1-deterministic-gap-rendering-plan-20260614.md`

Verdict: `PASS_WITH_FINDINGS`

Release/readiness: `NOT_READY`

## 1. Evidence Reviewed

| Evidence | Use |
|---|---|
| `AGENTS.md` | Execution truth, module boundaries, template/audit constraints, EID single-source policy. |
| `docs/current-startup-packet.md` | Active gate confirmation, binding amendments, `NOT_READY` posture. |
| `docs/implementation-control.md` | Current `standard` gate classification, Route C boundaries, repair budget defaults. |
| `docs/reviews/provider-llm-chapter2-l1-deterministic-gap-rendering-plan-20260614.md` | Review target. |
| `docs/reviews/provider-llm-chapter2-l1-live-persistent-failure-disposition-plan-controller-judgment-20260614.md` | Binding controller amendments for this gate. |
| `docs/fund-analysis-template-draft.md` | Ch2 required-output canonical JSON — confirmed all 7 items currently `when_evidence_missing="block"`. |
| `fund_agent/fund/evidence_availability.py` | Ch2 requirement specs map to `structured.nav_benchmark_performance` and `structured.fee_schedule`; status closed set confirmed as `available/missing/unavailable/not_applicable/unreviewed`. |
| `fund_agent/fund/chapter_writer.py` | `_required_output_plan_item()` (line 938), `_required_output_action()` (line 1001), `_required_output_prompt_instruction()` (line 1034) — existing code already resolves `when_evidence_missing` template values to `render_evidence_gap` / `render_minimum_verification_question` actions with prompt instructions. `_required_output_action()` returns `"render"` when `status == "available"`, providing the key guard against gap-masking when facts are present. `missing_availability` path (line 962-963) correctly blocks when `EvidenceAvailability` requirement mapping is absent. |
| `fund_agent/fund/chapter_auditor.py` | L1 `_audit_numerical_closure()` (line 1284) triggers on `NUMERICAL_CLOSURE_RE` + `NUMERIC_TEXT_RE` without nearby anchor marker. Safe gap wording without concrete percentages will not match `NUMERIC_TEXT_RE` and thus passes L1. |

No forbidden body/payload/live/source reads were used.

## 2. Controller Amendment Verification

All 9 binding amendments from `docs/reviews/provider-llm-chapter2-l1-live-persistent-failure-disposition-plan-controller-judgment-20260614.md` Section 6 are satisfied:

| # | Amendment | Plan compliance | Evidence |
|---|---|---|---|
| 1 | Planning only; no implementation | `ACCEPT` | Plan §1: "No implementation in this planning gate." §9 stop condition confirmed. |
| 2 | Preserve L1 severity; no downgrade | `ACCEPT` | Plan §1 non-goals: "Do not weaken L1, downgrade it to warn, or accept unsupported concrete percentages." |
| 3 | Preserve EID single-source/no-fallback | `ACCEPT` | Plan §1 non-goals: "Do not introduce Eastmoney, fund-company, CNINFO or any non-EID fallback." V15 verifies same-source requirement ids. |
| 4 | Preserve current repair budget | `ACCEPT` | Plan §4: "max_repair_attempts remains unchanged." §7: repair budget interaction out of scope for implementation. |
| 5 | Scope to `l1_numerical_closure` | `ACCEPT` | Plan §1: "Scope is limited to template 第 2 章 R=A+B-C 收益归因 required-output behavior. The behavior is not generalized to all L1 subcategories." |
| 6 | Distinguish fact absence vs present-but-ignored | `ACCEPT` | Plan §3: `available` facts with anchors → prompt-contract failure. Missing/insufficient availability → gap/minimum-verification. §4: "If same-source facts are available, the implementation must not auto-gap-render." V9 tests present-but-ignored → fail-closed. |
| 7 | Concrete validation specs | `ACCEPT` | Plan §6: V1-V15 with exact file, fixture/stub layer, test intent, and expected assertions. |
| 8 | Auditor/repair alignment | `ACCEPT` | Plan §4 auditor semantics, §6 V6/V7/V10/V12 cover auditor pass/fail, repair context and unsafe output blocking. |
| 9 | Preserve `NOT_READY` | `ACCEPT` | Plan header and §7: "Implementation evidence and controller judgment must preserve `NOT_READY`." |

DS-specific findings from prior review also resolved:
- DS F1 (gap masking): addressed by availability-gated gap rendering per §3/§4.
- DS F2 (underspecified validation): addressed by V1-V15 matrix per §6.
- DS F3 (auditor/repair alignment): addressed by V6/V7/V10 per §6.

## 3. Findings

### F1 — `missing_evidence_reason` wording unspecified (Medium)

**Location**: Plan §4 item group table vs template draft Ch2 required-output items

**Finding**: The plan proposes changing `when_evidence_missing` and `missing_evidence_reason` per §4, but only specifies user-visible semantics ("Keep exact marker; state reviewed same-source performance/benchmark evidence is insufficient"), not the exact `missing_evidence_reason` text for each of the 7 items. The current `missing_evidence_reason` for all 7 items is the blocking rationale: "第 2 章 R=A+B-C 数值与成本判断缺少同源证据时不得生成替代结论。"

The `missing_evidence_reason` field flows into the writer prompt instruction (line 1058 of `chapter_writer.py`: `f"原因={item.missing_evidence_reason or 'typed reason absent'}"`) and directly shapes what the LLM is told to write. Inconsistent or ambiguous reasons risk confusing the writer.

**Risk**: Implementation worker writes ad-hoc reasons that don't match the product semantics in §3, or the blocking rationale is left unchanged despite the behavior now being gap/minimum-verification.

**Recommendation**: Require implementation to specify exact `missing_evidence_reason` text per item group in §4 during the implementation gate, and include those texts in V1 template assertions.

### F2 — Product wording location in template fields unclear (Low-Medium)

**Location**: Plan §3 residual ambiguity paragraph vs §4 item group table

**Finding**: The plan's product wording rule (§3): "Default wording should say '当前同源已复核证据不足/未复核/不可用，不能完成具体 R=A+B-C 数字闭环'" is stated as a product direction but is not explicitly mapped to any specific template field. The `missing_evidence_reason` field could carry this, or it could be embedded in the `prompt_instruction` generated by the writer (which already includes guidance like "必须包含'证据不足/数据不足/未披露/未复核/不能据此判断'之一").

The existing writer prompt instruction for `render_evidence_gap` (line 1055-1059 of `chapter_writer.py`) already generates: "必须输出该 marker，但只能写证据缺口；状态={status}；原因={item.missing_evidence_reason}；必须包含'证据不足/数据不足/未披露/未复核/不能据此判断'之一，不得给出正向结论。" This covers most of the plan's product wording, but the cluster of status phrases ("未复核/不可用") must be carried by the availability status itself, not by template text.

**Risk**: Implementation may produce ambiguous gap wording that doesn't clearly communicate "reviewed evidence insufficient" vs "source absent."

**Recommendation**: Clarify in the implementation gate that `missing_evidence_reason` should state the domain reason for insufficiency, while the prompt instruction generated by the writer handles the "what to write" mechanics. The existing writer mechanism is sufficient provided the per-item reasons are explicit.

### F3 — Template change alone may not need design doc sync, but rule check is warranted (Low)

**Location**: Plan §5 allowed write set vs `AGENTS.md` line 215

**Finding**: `AGENTS.md` line 215 states: "模板章节结构变化 → 同步更新 `fund_agent/fund/README.md` 和 `docs/design.md`." The plan changes only `when_evidence_missing` and `missing_evidence_reason` values for 7 Ch2 items — item ids, order, text, and chapter structure are unchanged. This is a policy value change, not a structural change, so the AGENTS.md rule likely does NOT trigger.

**Risk**: If the implementation worker or a future reviewer interprets this as a structural change, they may incorrectly require design doc sync. The implementation gate should explicitly confirm no structural change occurred.

**Recommendation**: The implementation gate should include a one-line confirmation that Ch2 item structure (ids, order, text) is unchanged and therefore `AGENTS.md` line 215 does not apply.

### F4 — No-live tests cannot prove gap wording won't trigger L1 false negatives (Informational)

**Location**: Plan §6 V6/V7

**Finding**: The L1 audit (`_audit_numerical_closure`, line 1284 of `chapter_auditor.py`) triggers on `NUMERICAL_CLOSURE_RE` (R=A+B-C pattern variants) AND `NUMERIC_TEXT_RE` (digit-percentage pattern) without nearby anchor marker. The plan's safe gap wording relies on the writer NOT outputting both a closure pattern and a numeric percentage simultaneously. The fake-writer tests (V6/V7) use controlled output, so they can't prove the LLM won't generate ambiguous phrasing that happens to match both patterns.

**Risk**: Low. The writer prompt instruction explicitly tells the LLM "不得给出正向结论" and "必须包含'证据不足'之一." The L1 regex requires BOTH patterns to match, so the LLM would need to output something like "证据不足，但 R=A+B-C 显示 Alpha 为 2.10%" to trigger L1 — which V7 already tests as unsafe. The fake-writer tests provide mechanical coverage of the audit rule; live evidence of LLM compliance is intentionally out of scope for this no-live gate.

**Recommendation**: No action required for this planning gate. The implementation gate should flag this as a known residual for any future live/provider evidence gate.

### F5 — Conditional source rule may understate prompt header interaction (Low)

**Location**: Plan §5 conditional source write set

**Finding**: The plan's Section 5 states "No production Python source change is expected." The code review confirms this is well-supported: `_required_output_action()` (line 1001) already maps `render_evidence_gap` / `render_minimum_verification_question` from template values, and `_required_output_prompt_instruction()` (line 1034) already generates appropriate prompt instructions for these actions. The template change alone should flow through correctly.

However, the plan's `missing_evidence_reason` text change is the only template-side change — the writer prompt instruction generator at line 1055-1068 injects this reason verbatim. If the new reasons contain text that contradicts the generated instruction prefix ("必须输出该 marker，但只能写证据缺口" / "必须输出该 marker，但只能写下一步最小验证问题"), the prompt may confuse the LLM.

**Risk**: Low. Implementation worker will produce template text and can verify correctness via tests. The conditional source rule in §5 is adequate: if the implementation worker finds the prompt instruction needs adjustment, `chapter_writer.py` is explicitly in the allowed conditional source set.

**Recommendation**: No action for this planning gate. The implementation gate should verify the full prompt assembly for Ch2 gap items before accepting.

## 4. Write Set Boundary Verification

The plan's allowed write set (§5) is verified against `AGENTS.md` module boundaries:

| Allowed path | Boundary check |
|---|---|
| `docs/fund-analysis-template-draft.md` | Template contract authored truth source; changing `when_evidence_missing` values is within Fund layer template policy scope. Does not touch source code, design doc, or control truth. |
| Test files (7 paths) | Standard test additions under existing test hierarchy. Do not change production behavior. |
| Conditional source (5 paths) | `chapter_writer.py`, `chapter_auditor.py`, `chapter_orchestrator.py`, `runner.py`, `repair.py` — all within Agent/Fund/Service layers consistent with existing boundaries. |

Forbidden write set correctly excludes `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, root `README.md`, and all source/provider/fallback/readiness artifacts. No boundary violation found.

## 5. Validation Matrix Assessment

The V1-V15 matrix (§6) is assessed as:

- **Coverage**: V1 (template contract), V2-V5 (writer), V6-V7 (auditor), V8-V10 (orchestrator), V11-V12 (agent runner), V13-V14 (service final-assembly), V15 (evidence availability same-source). Covers all layers: Fund → Agent → Service.
- **Positive paths**: V2, V3, V6, V8, V11, V13 — gap/minimum-verification accepted at each layer.
- **Negative paths**: V4 (missing envelope fail-closed), V5 (unsafe gap wording blocked), V7 (concrete percentage L1 failure), V9 (present-but-ignored fail-closed), V12 (agent runner blocked), V14 (service fail-closed).
- **Repair budget**: V8 verifies request count unchanged; V9 verifies two-attempt path preserved; V10 verifies repair context alignment.
- **Feasibility**: All test files exist with current sizes between 15K and 114K lines. Fake-writer and fake-client patterns are established in existing tests. V15 may not need changes if requirement ids are unchanged — the plan says "only if needed."
- **Commands**: `pytest` for 7 specific test files, `ruff check` for same, `git diff --check`. Appropriate for a `standard` gate.

No overbroad validation detected. The test matrix is narrowly scoped to the exact behavior change.

## 6. Residuals

| Residual | Severity | Owner | Recommendation |
|---|---|---|---|
| Exact `missing_evidence_reason` text unspecified for 7 items | Medium | Implementation worker | Controller should require exact reason text in implementation evidence. |
| Product wording template-field mapping implicit | Low-Medium | Implementation worker + controller | Implementation gate should confirm `missing_evidence_reason` carries domain reason; writer prompt instruction carries "what to write." |
| `AGENTS.md` line 215 applicability check deferred | Low | Implementation worker | Confirm in implementation evidence that Ch2 structure is unchanged. |
| No-live fake-writer tests can't prove LLM gap-wording compliance | Informational | Future live evidence gate | Flag as known residual; not actionable in this no-live gate. |
| Prompt header interaction with new `missing_evidence_reason` | Low | Implementation worker | Verify full prompt assembly in implementation gate. |

## 7. Recommendation for Controller

Accept the plan as `PASS_WITH_FINDINGS`. The plan satisfies all 9 controller amendments, the allowed write set is narrow and boundary-consistent, core policies (EID single-source, NOT_READY, repair budget, L1 severity) are preserved, and the validation matrix is concrete and feasible.

The template change route is valid: the existing writer architecture (`_required_output_action` at line 1001, `_required_output_prompt_instruction` at line 1034 of `chapter_writer.py`) already resolves `render_evidence_gap` / `render_minimum_verification_question` from template `when_evidence_missing` values, and Ch3 already uses this accepted pattern. No design doc or control truth authorization is required before implementation — the template draft is the authored truth source for template contracts.

Before the implementation gate, controller should:
1. Require the implementation worker to specify exact `missing_evidence_reason` text per item group and include the text in V1 template assertions (F1).
2. Require implementation evidence to confirm Ch2 item structure (ids, order, text) is unchanged, precluding `AGENTS.md` line 215 trigger (F3).
3. Carry F2, F4, F5 as informational residuals to the implementation gate.

Final verdict:

```text
VERDICT: PASS_WITH_FINDINGS_F1_MISSING_EVIDENCE_REASON_UNSPECIFIED_F2_PRODUCT_WORDING_MAPPING_IMPLICIT_F3_AGENTS_MD_RULE_CHECK_DEFERRED_NOT_READY
```

Recommend proceeding to:

```text
Provider/LLM Chapter 2 L1 Deterministic Gap Rendering No-live Implementation Gate
```
