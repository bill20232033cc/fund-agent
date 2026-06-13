# Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Implementation Review — MiMo

Date: 2026-06-14

Role: AgentMiMo reviewer

Gate: `Provider/LLM Chapter 2 L1 Deterministic Gap Rendering No-live Implementation Gate`

## 1. Verdict

`PASS_WITH_FINDINGS`

## 2. Findings

### F1 — Template structure preservation confirmed, no item id/order/text drift

Severity: **informational**

The template draft diff shows only `when_evidence_missing` and `missing_evidence_reason` changed for the seven Chapter 2 `required_output_items`. Item ids (`ch2.required_output.item_01` through `item_07`), item text, chapter structure (8 chapters, 0-7), internal subcontract ids (`performance`, `attribution`, `cost`), and subcontract `requirement_ids` are unchanged.

The test `test_chapter_2_missing_behavior_preserves_structure_and_exact_reasons` (test_typed_contracts.py:173) asserts all seven `(item_id, text, when_evidence_missing, missing_evidence_reason)` tuples and the subcontract id ordering, which provides a strong structural lock.

No finding.

### F2 — Exact `missing_evidence_reason` values are specified and asserted

Severity: **informational**

The evidence artifact (section 3) documents the four exact reason groups:
- Performance (item_01, item_02): `render_evidence_gap`
- Attribution (item_03, item_04): `render_minimum_verification_question`
- Cost (item_05, item_06): `render_evidence_gap`
- Synthesis (item_07): `render_minimum_verification_question`

The test file `test_typed_contracts.py` imports and uses the exact same constant strings (lines 28-42). The template JSON contains the identical text. Cross-referencing confirms consistency.

No finding.

### F3 — Typed `EvidenceAvailability` non-available triggers gap/minimum-verification

Severity: **informational**

Tests `test_chapter_2_missing_performance_renders_evidence_gap` (test_chapter_writer.py:346) and `test_chapter_2_missing_synthesis_renders_minimum_verification_question` (test_chapter_writer.py:398) construct `ExtractedField(value=None, extraction_mode="missing")` fixtures, derive `EvidenceAvailability`, and assert the correct `render_evidence_gap` / `render_minimum_verification_question` actions with correct `missing_evidence_reason` in the prompt plan.

The orchestrator test `test_chapter_2_typed_missing_evidence_gap_path_accepts_without_repair` (test_chapter_orchestrator.py:2338) proves the full pipeline: non-available evidence → gap plan → single writer call → accepted status with no repair needed.

No finding.

### F4 — Available-fact fail-closed under `l1_numerical_closure` preserved

Severity: **informational**

Test `test_chapter_2_typed_available_facts_still_fail_l1_after_one_repair` (test_chapter_orchestrator.py:2393) uses a writer that emits unanchored percentages with available facts. The test asserts `status == "failed"`, `stop_reason == "repair_budget_exhausted"`, `failure_category == "prompt_contract"`, `failure_subcategory == "l1_numerical_closure"`, and exactly 2 writer calls (initial + 1 repair). This proves available-fact L1 fail-closed behavior is unchanged.

No finding.

### F5 — Missing `EvidenceAvailability` envelope remains `ValueError`

Severity: **informational**

Test `test_chapter_2_missing_availability_envelope_remains_fail_closed` (test_chapter_writer.py:437) passes `evidence_availability=None` and asserts `pytest.raises(ValueError, match="EvidenceAvailability")` with zero writer requests. This confirms the envelope guard is preserved.

No finding.

### F6 — Writer issue-id semantics preserved for available-fact block cases; gap-specific ids used for non-available defective output

Severity: **informational**

Test `test_chapter_2_missing_gap_without_gap_phrase_uses_specific_issue_id` (test_chapter_writer.py:454) asserts:
- `issue.issue_id == "writer:required_output_gap_missing:ch2.required_output.item_01"` (gap-specific)
- `issue.issue_id != "writer:required_output_block:ch2.required_output.item_01"` (not block-specific)

This matches the controller amendment (MiMo F2): preserve `writer:required_output_block:` for available-fact block cases; use more specific gap/verification issue ids for non-available defective output.

The Service test `test_partial_llm_result_does_not_fallback_when_ch2_gap_output_is_unsafe` (test_fund_analysis_service_llm.py:541) similarly asserts the gap-specific issue id at the Service layer.

No finding.

### F7 — Repair budget unchanged

Severity: **informational**

Evidence artifact section 4 states `max_repair_attempts` remains unchanged. The orchestrator test `test_chapter_2_typed_missing_evidence_gap_path_accepts_without_repair` uses `max_repair_attempts=1` and asserts only 1 writer call (no repair needed for gap output). The available-fact fail-closed test uses `max_repair_attempts=1` and asserts 2 writer calls (initial + 1 repair = budget exhausted). Both confirm the one-repair default is preserved.

No finding.

### F8 — `writer:required_output_block:` preserved for available-fact block cases

Severity: **informational**

Existing tests `test_writer_blocks_missing_required_output_marker_before_audit` (test_chapter_writer.py:1093) use chapter 1 (no `when_evidence_missing` changes) and assert `stop_reason == "missing_required_output_marker"`. The new gap-specific tests use chapter 2 non-available evidence and assert `writer:required_output_gap_missing:*` issue ids. The two patterns are distinct and do not interfere.

No finding.

### F9 — Agent runner and Service final-assembly coverage

Severity: **informational**

Runner tests:
- `test_chapter_2_missing_evidence_gap_renders_and_builds_readiness` (test_runner.py:382): positive gap output → accepted + readiness
- `test_chapter_2_missing_evidence_without_gap_phrase_blocks_before_readiness` (test_runner.py:414): unsafe gap output → blocked + readiness False

Service tests:
- `test_analyze_with_llm_accepts_final_assembly_when_ch2_degrades_to_gap` (test_fund_analysis_service_llm.py:505): positive → full assembly 8 chapters
- `test_partial_llm_result_does_not_fallback_when_ch2_gap_output_is_unsafe` (test_fund_analysis_service_llm.py:541): unsafe → incomplete, no deterministic fallback

These cover the positive and negative paths at both Agent and Service layers.

No finding.

### F10 — Prompt-assembly assertions confirm gap reasons do not conflict with gap/minimum-verification instructions

Severity: **informational**

Test `test_chapter_2_missing_performance_renders_evidence_gap` (test_chapter_writer.py:346) asserts:
- `f"原因={CH2_PERFORMANCE_REASON}" in prompt.user_prompt` — the reason is injected into the prompt
- The prompt also contains `render_evidence_gap` action in the evidence plan

The test `test_writer_prompt_contains_l1_numerical_closure_anchor_rule` (test_chapter_writer.py:592) asserts the L1 numerical closure contract is present in chapter 2 prompts. Since the gap path bypasses L1 (gap output has no concrete percentages), and the L1 path is only triggered for available facts, there is no conflict.

No finding.

### F11 — EID single-source/no-fallback policy untouched

Severity: **informational**

No source, provider, fallback, Eastmoney, fund-company, or CNINFO code was modified. The evidence artifact confirms no live/provider/network commands were run. The implementation only touches template JSON and test files.

No finding.

### F12 — `test_chapter_auditor.py` not modified — existing coverage sufficient

Severity: **low**

The evidence artifact states `tests/fund/test_chapter_auditor.py` was not changed because it "already covered safe Ch2 gap/minimum-verification pass and concrete unanchored percentage L1 fail." However, the controller judgment's allowed write set includes this file and the required validation command includes it. The test suite passes (`260 passed`), so existing coverage is adequate, but the worker's reasoning for not modifying it should be verified.

Checking: the test suite includes `test_chapter_auditor.py` in the validation command and all 260 tests pass. The auditor tests were not modified because existing tests already cover the relevant scenarios. This is acceptable since the auditor behavior is unchanged — it still checks L1 numerical closure for concrete percentages regardless of the template `when_evidence_missing` setting.

**Finding**: No action required, but documentation could be clearer about which existing auditor tests cover the Ch2 gap/minimum-verification pass scenario.

### F13 — No production source touched

Severity: **informational**

The evidence artifact states "Production Python source was not touched." The git diff confirms only `docs/fund-analysis-template-draft.md` and test files were modified. This is within the allowed write set.

No finding.

## 3. Residuals

| Residual | Disposition |
|---|---|
| No-live tests cannot prove future live LLM wording compliance. | Carried to future bounded live/provider evidence gate. |
| Exact live sample fact-absence vs present-but-ignored ambiguity is not proven under this no-live boundary. | Preserved by typed availability discriminator and available-fact L1 fail-closed tests. |
| `tests/fund/test_chapter_auditor.py` was not modified despite being in the allowed write set. | Acceptable: existing tests cover the relevant auditor scenarios; no new auditor behavior was introduced. |
| Release/readiness remains incomplete. | `NOT_READY`; no readiness or release claim made. |

## 4. Recommendation for Controller

Implementation is within the accepted allowed write set and no-live boundaries. All six required boundary assertions from the controller judgment are satisfied:

1. Exact `missing_evidence_reason` text per item group: **confirmed** (4 distinct reason texts, all asserted in tests)
2. Chapter 2 item ids/order/text/chapter structure unchanged: **confirmed** (structural lock test)
3. `writer:required_output_block:` preserved for available-fact block cases: **confirmed** (existing tests pass, gap-specific tests use distinct issue ids)
4. `max_repair_attempts` unchanged: **confirmed** (one-repair default preserved)
5. EID single-source/no-fallback policy untouched: **confirmed** (no source/provider code modified)
6. Release/readiness remains `NOT_READY`: **confirmed** (no readiness claim made)

Validation evidence: `260 passed`, ruff passed, `git diff --check` passed.

Recommendation: **PASS** for controller acceptance.
