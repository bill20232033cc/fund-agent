# Provider/LLM Chapter 3 Required-output Policy Plan Review — MiMo

Date: 2026-06-14

Reviewer: AgentMiMo

Role: Independent plan review worker.

Gate: `Provider/LLM Chapter 3 Required-output Policy Planning Gate`.

## 1. Scope

This review assesses whether `docs/reviews/provider-llm-chapter3-required-output-policy-plan-20260614.md` is code-generation-ready, appropriately scoped, and correct to recommend changing `ch3.required_output.item_01` from `block` to `render_evidence_gap` with no-live enforcement and final assembly readiness tests.

Hard boundaries observed:

- Review only. No implementation, source modification, control-doc update, live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR command, or stage/commit/push/PR/merge action.
- EID single-source/no-fallback and `NOT_READY` preserved.
- No writer markdown, auditor markdown, raw prompts, provider payload/response, source/cache/PDF body, or final report body read.

## 2. Evidence Reviewed

Truth and control:

- `AGENTS.md`: module boundary, EID single-source/no-fallback, Route C fail-closed, `NOT_READY` conservatism, CHAPTER_CONTRACT goal.
- `docs/current-startup-packet.md`: active gate is `Provider/LLM Chapter 3 Required-output Policy Planning Gate`; planning must decide hard block vs evidence-gap rendering vs minimum verification question.
- `docs/implementation-control.md`: current gate and accepted checkpoint chain through Chapter 3 item 01 fact-gap disposition at `62c7a2e`.
- `docs/fund-analysis-template-draft.md` (lines 665-697): Chapter 3 `required_output_items`; item 01 currently `when_evidence_missing="block"`, items 02-05 use `render_evidence_gap`, item 06 uses `render_minimum_verification_question`.
- `docs/reviews/provider-llm-chapter3-item01-fact-gap-disposition-controller-judgment-20260614.md`: accepted current fact-gap as intentional fail-closed residual.

Code/tests:

- `fund_agent/fund/chapter_writer.py`:
  - `_required_output_action()` (line 1001): already supports `render_evidence_gap` enum branch.
  - `_required_output_preflight_issues()` (line 1097): only blocks items whose computed action is `block`.
  - `_required_output_degrade_issues()` (line 1751): validates `render_evidence_gap` items contain approved gap phrases.
  - `_required_output_prompt_instruction()` (line 1034): already renders safe instruction for `render_evidence_gap` action.
- `fund_agent/fund/evidence_availability.py`:
  - `ch3.required_output.item_01` maps to `structured.basic_identity` and `structured.portfolio_managers`.
- `fund_agent/agent/runner.py`:
  - `_final_readiness()` (line 965): ready iff all tasks are accepted and at least one accepted task exists.
- `fund_agent/services/final_chapter_assembler.py`:
  - `_build_final_assembly_readiness()` (line 476): requires all `required_body_chapter_ids` to be accepted with accepted draft/conclusion.
- `tests/fund/template/test_typed_contracts.py::test_chapter_3_basic_manager_info_missing_behavior_blocks` (line 141): currently asserts `when_evidence_missing == "block"`.
- `tests/agent/test_runner.py::test_chapter_3_missing_basic_manager_info_blocks_before_provider` (line 303): currently asserts `action == "block"` and writer not called.
- `tests/agent/test_runner.py::test_chapter_3_missing_typed_availability_blocks_before_provider` (line 255): envelope fail-closed test.
- `tests/agent/test_runner.py::test_chapter_3_missing_evidence_availability_envelope_remains_value_error` (line 351): missing envelope raises `ValueError`.

Plan review artifact:

- `docs/reviews/provider-llm-chapter3-required-output-policy-plan-20260614.md`

## 3. Findings (severity ordered)

### F1. Slice 3 assembled_chapter_ids assertion over-specifies (SEVERITY: MEDIUM)

Plan Slice 3 asserts:

> `result.final_assembly_result.assembled_chapter_ids == (0, 1, 2, 3, 4, 5, 6, 7)`

This requires the test to produce accepted output for all 8 chapters including Ch0 and Ch7. The test description says "fake writer emits approved evidence-gap wording for ch3.required_output.item_01 and valid output for all other required items/chapters." However, if the test only orchestrates a subset of chapters, this assertion will fail. The test design must either:

- (a) Use full 8-chapter orchestration (which means the test is more complex and may need Ch0/Ch7 assembly logic), or
- (b) Narrow the assertion to only the chapters the test actually produces.

This is not a plan-blocking issue, but the implementation worker must clarify the test scope. The plan text is ambiguous about whether this is a full-report or partial-report test.

### F2. Slice 3 needs explicit negative case for blocked Chapter 3 final assembly (SEVERITY: LOW)

Plan Slice 3 says:

> "if Chapter 3 writer output is unsafe, Service final assembly must remain incomplete with no report markdown."

This is stated as an extension of the existing `test_partial_llm_result_does_not_fallback_to_deterministic_after_typed_readiness`, but the existing test may not specifically exercise the "unsafe Chapter 3 evidence gap output blocks final assembly" path. The plan should explicitly require a dedicated negative test or clearly confirm the existing test covers this.

### F3. Slice 4 docs sync rg scope is broad (SEVERITY: LOW)

Slice 4's check command:

```bash
rg -n "ch3.required_output.item_01|基金经理基本信息|required_output_block|hard block|阻断" docs README.md fund_agent tests
```

This searches a very wide surface including all `docs/` and `tests/`. While the intent is correct (find all hard-block references to narrow-update), the implementation worker should note that this is a scoping check, not a full-text search mandate. Only documents that specifically assert "Chapter 3 item 01 must hard-block" should be updated; general `when_evidence_missing` behavior documentation should not be touched.

### F4. Missing_evidence_reason wording change (SEVERITY: LOW)

Plan Slice 1 proposes:

```json
"missing_evidence_reason": "第 3 章基金经理基本信息缺少已复核证据时只能输出证据缺口，不得进入未经证据支持的基金经理画像判断。"
```

Current template says:

```
"missing_evidence_reason": "第 3 章基金经理基本信息缺少已复核证据时不能进入基金经理画像写作。"
```

The plan changes the reason text. The test assertion says the reason must contain both `缺少已复核证据` and `只能输出证据缺口`. This is a reasonable refinement that aligns with the new `render_evidence_gap` behavior. No issue, just noting the wording delta.

### F5. _required_output_degrade_issues stop_reason mapping (SEVERITY: LOW)

Plan Slice 2 negative test says:

> "expected stop/failure classification should follow the current writer-output validation mapping, not `required_output_block:ch3.required_output.item_01`."

When `_required_output_degrade_issues()` rejects unsafe output, the resulting issue id is `writer:required_output_gap_missing:ch3.required_output.item_01` with stop reason `missing_required_output_marker`. The plan correctly notes this is different from the current `required_output_block` path. No issue.

## 4. Accepted Points

| # | Point | Basis |
|---|---|---|
| A1 | Policy decision: change item 01 from `block` to `render_evidence_gap` | Aligns with items 02-05; keeps required output visible; preserves fail-closed safety through writer output validation; allows final assembly progress |
| A2 | Reject Option A (keep block) | Overly strict vs nearby items; blocks entire Chapter 3 for one data gap |
| A3 | Reject Option C (minimum verification question) | Item 01 is descriptive, not follow-up; less consistent with items 02-05 |
| A4 | Template JSON field change is code-feasible | `_required_output_action()` already handles `render_evidence_gap` branch (line 1023); no code change needed in contracts.py or typed_contracts.py |
| A5 | Evidence availability mapping unchanged | `ch3.required_output.item_01` maps to `structured.basic_identity` and `structured.portfolio_managers`; policy change does not alter same-source requirement |
| A6 | Writer output validation preserves safety | `_required_output_degrade_issues()` (line 1770) checks for approved gap phrases; non-compliant output remains blocked |
| A7 | Missing EvidenceAvailability envelope remains fail-closed | `test_chapter_3_missing_typed_availability_blocks_before_provider` preserved; policy only degrades reviewed missing evidence, not missing contract plumbing |
| A8 | Final assembly readiness is based on accepted chapters, not raw fact completeness | `_build_final_assembly_readiness()` (line 476) checks accepted status + draft/conclusion; `_final_readiness()` (line 965) checks accepted tasks |
| A9 | All validation is no-live | No provider/network/source/PDF/FDR/commands authorized |
| A10 | EID single-source/no-fallback and NOT_READY preserved throughout | Plan explicitly states and maintains these invariants |
| A11 | Four-slice implementation structure is well-scoped | Template policy, no-live writer tests, service assembly tests, conditional docs sync |
| A12 | Risks and residuals are explicitly listed | Post-implementation bounded live re-evidence, broader Chapter 3 policy audit, release/readiness remain deferred |
| A13 | Gate classification standard is appropriate | Policy change to a single template item with focused no-live tests fits standard gate |

## 5. Required Amendments

None. All findings are non-blocking. F1 should be resolved by the implementation worker when writing the actual test (clarify full-report vs partial-report scope). F2 should be confirmed during implementation.

## 6. Verdict

**PASS_WITH_FINDINGS**

The plan is code-generation-ready, correctly scoped, and correct to recommend changing `ch3.required_output.item_01` to `render_evidence_gap` with no-live enforcement and final assembly readiness tests. The policy reasoning is sound: it aligns item 01 with items 02-05, preserves fail-closed safety through existing writer output validation, and allows final assembly to progress when the gap is explicitly rendered. All five findings are non-blocking presentation or implementation-detail clarifications. No required amendments.
