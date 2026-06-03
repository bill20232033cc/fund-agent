# MVP typed template contract Slice 6 Ch0/Ch7 readiness code review

## Review metadata

- Reviewer: MiMo
- Gate: `MVP typed template contract Slice 6 Ch0 consumes Ch7 with fail-closed required-body readiness implementation gate`
- Classification: `heavy`
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Files reviewed: `fund_agent/services/final_chapter_assembler.py`, `tests/services/test_final_chapter_assembler.py`, `tests/services/test_fund_analysis_service_llm.py`, `tests/ui/test_cli.py`, `tests/README.md`
- Sources read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, Slice 6 section of `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md`, `docs/reviews/mvp-typed-template-contract-slice6-ch0-ch7-readiness-implementation-evidence-20260603.md`

## Validation

```
uv run pytest tests/services/test_final_chapter_assembler.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -v --tb=short
```

Result: 112 passed in 1.10s. PASS.

## Findings

### Finding 1: Ch7 user-facing report leaks Python tuple repr and internal readiness enum ids

**Severity**: informational (non-blocking)

**Location**: `final_chapter_assembler.py:819-820`, `final_chapter_assembler.py:874`

**Description**: The rendered Ch7 markdown includes:

```
- **证据/readiness 状态**：accepted_body_chapters；ready；accepted_body_chapters=(1, 2, 3, 4, 5, 6)
```

Three concerns with this user-facing line:

1. `accepted_body_chapters=(1, 2, 3, 4, 5, 6)` uses Python tuple repr with parentheses. End users will not interpret `(1, 2, 3, 4, 5, 6)` as a natural format. A comma-separated list `1, 2, 3, 4, 5, 6` or Chinese `第 1-6 章` would be more readable.

2. The field name `accepted_body_chapters` appears twice: once as the `evidence_status` enum value and once as the rendered label prefix `accepted_body_chapters=...`. This redundancy adds no information.

3. The enum values `accepted_body_chapters` / `incomplete_body_chapters` / `ready` / `blocked` are implementation-level contract labels. They are human-readable but read as developer diagnostics rather than user-facing report language. The template's `证据/readiness 状态` field is explicitly designed to carry this, so it is not a contract violation, but it could be polished in a future UX pass.

**Recommendation**: Non-blocking for this gate. The template explicitly includes this field. Consider a future UX polish to render Chinese-friendly labels (e.g., `正文章节均已 accepted` vs `部分正文章节未完成`) and to format chapter ids as a range or list without Python tuple syntax. Do not block Slice 6 on this.

### Finding 2: CLI test uses hardcoded fake rather than exercising real readiness path

**Severity**: informational (non-blocking)

**Location**: `tests/ui/test_cli.py:2342-2376` (`test_use_llm_incomplete_typed_readiness_empty_stdout_exit_one`)

**Description**: The CLI test uses `_IncompleteLLMService` which returns a hardcoded `_FakeLLMFinalAssemblyResult(status="blocked")`. It does not exercise the real `FinalChapterAssembler` readiness logic through the CLI path. This means the test validates CLI-layer fail-closed behavior (exit 1, empty stdout) but not that the real readiness gate produces the blocked state.

However, this is the established testing pattern in this codebase: CLI tests verify the thin CLI layer's handling of service results, while service-layer tests (`test_partial_llm_result_does_not_fallback_to_deterministic_after_typed_readiness`) and assembler-layer tests (`test_missing_required_body_chapter_blocks_ch7_and_ch0`) verify the real readiness logic. The three test layers together provide full coverage.

**Recommendation**: Non-blocking. The test pattern is consistent with the existing codebase convention. No change needed.

## Review checklist results

| Review question | Verdict | Evidence |
|---|---|---|
| Does `FinalAssemblyReadiness` make Ch7 readiness explicit and require all public body chapters 1-6 accepted with accepted draft and conclusion? | YES | `_build_final_assembly_readiness` checks each chapter in `required_body_chapter_ids` (1-6) for `status=="accepted"`, `accepted_draft is not None`, `accepted_conclusion is not None` via `_validate_orchestration` + accepted_body_chapter_ids comprehension. Only when no issues exist does status become `"ready"`. |
| Can Ch7 be produced as accepted when required body readiness is incomplete? | NO (correct) | `_build_chapter7_summary` returns `None` when `readiness.status != "ready"` or `not readiness.chapter7_ready`. `assemble_final_chapters` returns incomplete when `chapter7_summary is None`. |
| Can Ch0 be complete when Ch7 is missing/unaccepted? | NO (correct) | `assemble_final_chapters` returns incomplete before reaching Ch0 rendering when `chapter7_summary is None`. `_chapter0_source_issues` also emits blocking issue when Ch7 conclusion is missing from sources. |
| Does Ch0 action equal Ch7 action exactly and avoid independently deriving or strengthening final action? | YES | Ch0 renders action as `chapter7_summary.selected_judgment_label` (line 913). `_validate_chapter0_action` checks `expected_line in chapter0_markdown` as a blocking guard. Ch0 does not introduce new judgment labels, new facts, or new anchors. |
| Does Ch7 summary/bundle include action, primary reason/core basis, largest risk/easiest misread, minimum verification question/next validation plan, thresholds, and evidence/readiness status? | YES | `FinalChapter7Summary` carries: `selected_judgment_label` (action), `core_basis` (primary reason), `easiest_misread` (largest risk), `next_validation_plan` (minimum verification question), `threshold_events` (thresholds), `evidence_status` + `readiness_status` (evidence/readiness status), `accepted_body_chapter_ids`. Rendered in `_render_chapter7_markdown` and `_chapter7_accepted_conclusion`. |
| Does user-facing report leak implementation-ish readiness ids? | MINOR (Finding 1) | `accepted_body_chapters=(1, 2, 3, 4, 5, 6)` uses Python tuple repr and internal enum labels. Template explicitly includes `证据/readiness 状态` field. Informational finding, not blocking. |
| Does existing incomplete `--use-llm` behavior remain fail-closed with empty stdout/no deterministic fallback? | YES | CLI test `test_use_llm_incomplete_typed_readiness_empty_stdout_exit_one` verifies exit code 1, empty stdout. Service test `test_partial_llm_result_does_not_fallback_to_deterministic_after_typed_readiness` verifies `report_markdown is None`, `chapter7_markdown is None`, `chapter0_markdown is None`. |
| No provider/runtime/default/live probe? | YES | No changes to `fund_agent/config/llm.py`, provider defaults, timeout defaults, or live provider commands. |
| No Agent runtime/tool-loop? | YES | No changes to `fund_agent/host/` or `fund_agent/agent/`. No tool-loop, ToolRegistry, or ToolTrace code. |
| No score-loop? | YES | No changes to `extraction_score.py`, `extraction_score_service.py`, or score-related code. |
| No golden/readiness promotion? | YES | No changes to golden fixtures, manifests, or promotion state. |
| No template truth replacement? | YES | No changes to `docs/fund-analysis-template-draft.md`. |
| No deterministic default behavior change? | YES | `_validate_policy` enforces `required_body_chapter_ids == (1, 2, 3, 4, 5, 6)` and `include_chapter7 is True`. Default deterministic `analyze/checklist` path is untouched. |
| No direct document/PDF/source access? | YES | Import boundary test `test_final_assembler_imports_stay_above_fact_and_source_boundaries` verifies no forbidden module imports. |
| Tests sufficient and validation credible? | YES | 5 new tests cover Ch0=Ch7 action equality, missing required body chapter blocks Ch7/Ch0, missing Ch7 blocks Ch0, partial LLM result fail-closed, and CLI incomplete exit 1. All 112 tests pass. |

## Adversarial failure analysis

1. **What if all 6 body chapters are accepted but one has empty accepted_draft?** `_validate_required_chapter` emits `missing_accepted_draft` blocking issue. `_build_final_assembly_readiness` propagates this to blocked status. Ch7 returns None. Result: incomplete. PASS.

2. **What if readiness is "ready" but Ch7 summary has mismatched readiness_status?** `_validate_chapter7_summary` compares `summary.readiness_status == readiness.status` and emits `chapter7_readiness_mismatch` blocking issue. Result: incomplete. PASS.

3. **What if policy allows incomplete debug markdown and a late Ch0 blocking issue occurs?** Test `test_incomplete_debug_markdown_can_be_retained_for_late_blocking_issue` verifies `report_markdown is not None` but status is `"incomplete"`. PASS.

4. **What if developer override changes the judgment?** Test `test_chapter7_preserves_developer_override_source_and_conflict_reasons` verifies override source, conflict reasons, and no re-derivation. PASS.

5. **What if Ch0 markdown is truncated and the action line is cut?** `_validate_chapter0_action` checks `expected_line in chapter0_markdown`. If truncation cuts the action line, the check fails → blocking issue. The `max_chapter0_chars` default is 5000, and the action line is rendered early, so this is unlikely in practice but correctly guarded. PASS.

## Project instruction compliance

- AGENTS.md: No forbidden actions taken. No direct PDF/source access. No `extra_payload`. Template terms consistent.
- Module boundary: Changes stay within Service layer `final_chapter_assembler.py`. No UI/Host/Agent boundary violations.
- Test strategy: Tests added for new behavior. Import boundary tests present. Coverage target for the changed module is met.
- Documentation: `tests/README.md` updated to reflect Slice 6 coverage. No premature docs changes.

## Over-coupling check

- `FinalAssemblyReadiness` is internal to `final_chapter_assembler.v1`. It is not exported or consumed outside the assembler module. The `FinalChapter7Summary` carries readiness fields for Ch0 rendering, which is the expected internal coupling between Ch7 and Ch0 within the same assembler.
- No new cross-module dependencies introduced. No new imports from Host, Agent, or external packages.

## Verdict

**PASS** — no blocking findings.

Finding 1 (readiness ids in user-facing report) is informational. The template explicitly includes the `证据/readiness 状态` field; the current rendering uses internal enum labels and Python tuple repr, which is functional but could be polished in a future UX pass. This does not violate the gate's acceptance criteria.
