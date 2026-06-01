# MVP Independent Body Chapter Execution Plan

## Gate Context

- Role: Gateflow planning worker only.
- Gate: `MVP independent body chapter execution gate`.
- Classification: `heavy`, because this changes the Service-layer LLM chapter state machine and fail-closed reporting semantics.
- Goal: template chapters 1-6 must each run independently from the same `ChapterFactProjection`. A failed body chapter must not cause later body chapters to become synthetic `dependency_missing` skips. Chapter 0, chapter 7 and final assembly must still depend on accepted body conclusions.

## Direct Evidence

- `fund_agent/services/chapter_orchestrator.py` currently defines `ChapterOrchestrationPolicy.fail_fast=True`.
- `orchestrate_chapters()` currently sets `stop_remaining=True` after the first non-accepted chapter when `policy.fail_fast` is true, then appends `_skipped_result()` for later target chapters.
- `_skipped_result()` marks later chapters as `status="skipped"`, `stop_reason="dependency_missing"`, `failure_category="fact_gap"`, with no attempts. This masks provider runtime / prompt-contract / audit diagnostics for chapters 2-6.
- `serialize_chapter_prompt_contract_diagnostics()` and `serialize_chapter_runtime_diagnostics()` already preserve `first_failed` plus per-chapter matrices, but current fail-fast execution means later rows are synthetic skipped rows rather than real chapter outcomes.
- `fund_agent/services/final_chapter_assembler.py` already fail-closes non-accepted orchestration and non-accepted body chapters. It must remain the complete-report gatekeeper.
- `fund_agent/ui/cli.py` currently emits only first-failed summary in `_llm_incomplete_message()`. It needs a safe all-chapter matrix summary so chapter 2-6 diagnostics are visible.

## Non-Goals

- Do not enter Gate 5, Host, Agent runtime, `dayu.host` or `dayu.engine`.
- Do not change Fund-layer writer/auditor audit rules, prompt parsing strictness, repair budgets, evidence-anchor rules, final judgment semantics, golden fixtures, score, snapshot, quality gate or manifests.
- Do not relax fail-closed behavior. Blocked/failed body chapters must not enter an accepted final report.
- Do not change default deterministic `fund-analysis analyze` or deterministic `fund-analysis checklist`.
- Do not record prompt text, draft markdown, raw provider response, raw audit response, API keys, Authorization headers or provider body.
- Do not change PR state, push, commit or create external artifacts.

## Dirty Scope Boundary

Current worktree contains prior accepted local gate changes and many untracked review artifacts. Implementation must treat them as existing local state and must not revert, clean, delete, restage, rename or normalize unrelated files.

Allowed files for implementation:

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/final_chapter_assembler.py` only if needed for explicit diagnostic/incomplete assertions; expected change should be small or none.
- `fund_agent/ui/cli.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_final_chapter_assembler.py`
- `tests/ui/test_cli.py`
- Optional documentation only if implementation changes user-visible CLI diagnostic wording: root `README.md` and/or `tests/README.md`. Prefer no README change unless wording or test conventions materially change.
- Gate evidence/review artifacts under `docs/reviews/` for implementation evidence only.

Explicitly disallowed files:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/config/`, `fund_agent/services/llm_provider.py`
- score, quality gate, golden, fixture, snapshot, manifest and promotion files.
- `AGENTS.md`, `docs/fund-analysis-template-draft.md`, Host/Agent/dayu packages.

## Target State Machine

### Body Chapters 1-6

For every `chapter_id` in `policy.target_chapter_ids`:

1. Resolve exactly one shared `ChapterFactProjection` before the loop.
2. Validate projection coverage for all requested body chapters before writing.
3. Run `_run_single_chapter()` independently for that chapter.
4. Preserve each chapter's own:
   - `status`
   - `stop_reason`
   - `failure_category`
   - `failure_subcategory`
   - `attempts`
   - `issues`
   - `prompt_contract_diagnostics`
   - `runtime_diagnostics`
5. Never skip chapter 2-6 solely because chapter 1 failed.
6. `generated_chapter_ids` must include every chapter that actually entered writer/auditor attempts, including failed chapters with attempts.
7. `skipped_chapter_ids` must be empty for ordinary body chapter failures. It may only be non-empty for real scope/contract skips, not for previous body chapter failure.

Recommended implementation decision:

- Keep `ChapterOrchestrationPolicy.fail_fast` as a constructor field for minimal API churn, but make body chapter orchestration independent by default and in production semantics. The safest code path is to remove `stop_remaining` from `orchestrate_chapters()` for chapters 1-6 and stop using `_skipped_result()` for prior body failures.
- Controller amendment after MiMo/GLM plan review: change `fail_fast` default to `False`, keep accepting explicit `fail_fast=True` for API compatibility, and document it as a legacy/no-op for template body chapters 1-6. No body chapter code path may branch on `policy.fail_fast`.
- Keep `_map_writer_stop_reason("chapter_requires_accepted_conclusions") -> dependency_missing` only for a true writer contract dependency failure. Do not use `dependency_missing` to represent "previous body chapter failed".

### Global Blocks

Global prerequisites can still block all requested chapters before writer execution:

- `projection.fund_type == "unknown"`
- `policy.run_llm_audit and llm_clients.auditor is None`
- invalid input identity or missing projection coverage should continue raising `ValueError`.

Those are not body-chapter dependency skips. They should keep their existing fail-closed semantics, with no provider attempts.

### Orchestration Status

- `accepted`: all target body chapters are accepted.
- `partial`: at least one body chapter is accepted and at least one body chapter is not accepted.
- `blocked`: no body chapter is accepted.

This can remain as currently implemented, as long as later chapters are actually executed instead of skipped.

## Final Assembly Rules

- Full report assembly remains accepted only when all required body chapters 1-6 are accepted, chapter 7 can be rendered from `FinalJudgmentDecision`, and chapter 0 can be rendered from accepted conclusions plus chapter 7 summary.
- `FinalAssemblyPolicy.require_orchestration_accepted=True` remains the default.
- Any body chapter with `status != "accepted"` must produce incomplete final assembly and must not be rendered into an accepted final report.
- A blocked/failed body chapter must have no `accepted_draft` and no `accepted_conclusion`; final assembly must report `chapter_not_accepted`, `missing_accepted_draft` and/or `missing_accepted_conclusion` as applicable.
- Partial body matrices are diagnostic only. They must not be exposed as a complete report and must not appear on stdout for `fund-analysis analyze --use-llm`.
- `allow_incomplete_debug_markdown` remains test/debug-only. Do not enable it in CLI or Service production defaults.

## Failure Summary And Diagnostics

Service serializers:

- Keep `first_failed` for concise controller/operator triage.
- Keep and rely on `chapter_phase_matrix` and `chapter_runtime_matrix` as the complete all-chapter diagnostic source.
- Ensure matrix rows for chapter 2-6 reflect real execution outcomes after chapter 1 failure, not default `skipped/dependency_missing` rows.
- Preserve safe scalar-only serialization. No prompt, draft, provider body, raw response, raw audit, model name, API key or Authorization header.

CLI incomplete message:

- Keep existing first-failed fields:
  - `first_failed_chapter_id`
  - `first_failed_status`
  - `first_failed_stop_reason`
  - `first_failed_category`
  - `first_failed_subcategory`
  - runtime scalar summary
- Add a compact safe all-chapter matrix summary to `_llm_incomplete_message()`.
- Suggested format:
  - `chapter_matrix=1:failed/llm_timeout/llm_timeout/unknown;2:accepted/none/unknown/unknown;...`
  - Include `chapter_id`, `status`, `stop_reason`, `failure_category`, `failure_subcategory`.
  - Do not include issue messages, prompts, drafts, raw responses, provider messages, model names or request bodies.
- `first_failed` must remain the first non-accepted chapter by chapter result order, but it must not be the only visible diagnostic.

Provider runtime diagnostic visibility:

- Writer timeout / rate limit / malformed / network / generic exception must remain visible per chapter.
- Auditor timeout / rate limit / malformed / network / generic exception must remain visible per chapter.
- Writer prompt-contract failures must preserve `failure_category="prompt_contract"` and safe subcategory.
- Auditor parse failures must preserve `failure_category="audit_parse"`.
- Parseable LLM audit failures after programmatic pass must preserve `failure_category="audit_rule_too_strict"`.
- Chapters 2-6 must not default to `dependency_missing` because chapter 1 failed.

## Score-Loop Handoff

- This gate does not implement `chapter_generation_score`.
- The independent per-chapter matrix is a prerequisite for future score-loop work because every body chapter will have an actual outcome row.
- Future score-loop can consume:
  - `chapter_phase_matrix`
  - `chapter_runtime_matrix`
  - per-chapter `status`, `stop_reason`, `failure_category`, `failure_subcategory`, attempt counts and safe runtime counters.
- Do not connect this gate to existing extraction score, golden readiness, fixture promotion, FQ0-FQ6 quality gate or release readiness.

## Implementation Slices

### Slice 1: Orchestrator Body Independence

Files:

- `fund_agent/services/chapter_orchestrator.py`
- `tests/services/test_chapter_orchestrator.py`

Steps:

1. Update `ChapterOrchestrationPolicy` docstring to state body chapter failures do not skip later body chapters. If `fail_fast` remains, mark it legacy/no-op for body chapters or change default to `False`.
2. Replace the `stop_remaining` loop in `orchestrate_chapters()` with a simple per-chapter loop that always calls `_run_single_chapter()` for each target body chapter after global preflight passes.
3. Stop appending `_skipped_result()` for previous body chapter failure.
4. Keep `_skipped_result()` only if needed for narrow internal compatibility, but no normal body failure path should call it.
5. Keep `_orchestration_result()` status aggregation semantics.
6. Update or replace `test_fail_fast_true_skips_later_chapters_after_first_blocked()` so it asserts chapter 2 executes after chapter 1 fails.
7. Add a test where chapter 1 writer timeout fails and chapters 2-6 still receive writer requests / attempt records.
8. Add a mixed matrix test: e.g. chapter 1 timeout, chapter 2 accepted, chapter 3 prompt-contract, chapter 4 audit-parse, chapter 5 fact-gap, chapter 6 accepted. Assert every row preserves own `status`, `stop_reason`, `failure_category`, `failure_subcategory`.
9. Add a dependency test showing `dependency_missing` is used only for a true writer stop reason such as `chapter_requires_accepted_conclusions`, not for prior body chapter failure.
10. Add an all-blocked test where all requested body chapters execute and fail, and assert orchestration status remains `blocked` with `skipped_chapter_ids == ()`.

Acceptance assertions:

- `result.chapter_results` contains one row per target chapter.
- Later rows after a failure have real attempts when their writer/auditor was invoked.
- `result.skipped_chapter_ids == ()` for ordinary body failures.
- `result.generated_chapter_ids` includes attempted failed chapters.
- `result.status` is `partial` when at least one body chapter accepted and one failed; `blocked` when none accepted.

### Slice 2: Final Assembly Incomplete Safety

Files:

- `fund_agent/services/final_chapter_assembler.py` only if required.
- `tests/services/test_final_chapter_assembler.py`

Steps:

1. Prefer no production-code change if existing final assembly already fail-closes partial/blocked orchestration and non-accepted chapters.
2. Add or strengthen tests with an orchestration result containing all chapter rows but with one or more non-accepted body chapters.
3. Assert final assembly returns `status="incomplete"`, `report_markdown is None`, and blocked chapters do not enter the final accepted report.
4. Assert partial matrix/source accepted chapters remain diagnostic only and do not make `source_accepted_chapter_ids` look like a complete body set.
5. Controller amendment after plan review: explicitly assert `source_accepted_chapter_ids` includes only accepted body chapter ids and excludes non-accepted required body chapters.

Acceptance assertions:

- Complete report only exists for accepted final assembly.
- Any failed/blocked body chapter prevents accepted final report.
- Existing chapter 0/7 dependency on accepted body conclusions remains intact.

### Slice 3: CLI All-Chapter Diagnostic Matrix

Files:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`

Steps:

1. Add a helper such as `_chapter_matrix_summary(orchestration_result)` near `_first_failed_chapter_summary()`.
2. The helper should iterate `orchestration_result.chapter_results` and render safe scalar rows only.
3. Include the matrix in `_llm_incomplete_message()` after the first-failed summary.
4. Update existing incomplete/timeout tests to assert first-failed fields remain present.
5. Add a CLI test where the fake orchestration result includes chapter 1 failed, chapter 2 accepted and chapter 3 failed. Assert stderr contains rows for all chapters and does not collapse chapter 2-3 into dependency missing.
6. Extend secret-safety assertions to cover the new matrix string. The negative assertions must include at least `message`, `Authorization`, `Bearer`, `sk-`, `api_key`, `system_prompt`, `user_prompt`, `draft_markdown`, `raw_response`, `raw audit`, `provider_response`, `provider body`, `model_name`, `header` and `key`.

Acceptance assertions:

- CLI exits `1`, stdout empty, no deterministic fallback.
- Stderr includes `first_failed_*` and `chapter_matrix=...`.
- Matrix includes all available chapter rows.
- Matrix contains no prompt/draft/raw response/provider body/model/API key/header/message.

## Validation Plan

Targeted tests:

- `uv run pytest tests/services/test_chapter_orchestrator.py`
- `uv run pytest tests/services/test_final_chapter_assembler.py`
- `uv run pytest tests/ui/test_cli.py`

Full deterministic validation:

- `uv run ruff check .`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
- `uv run fund-analysis analyze 006597 --report-year 2024`
- `uv run fund-analysis checklist 006597 --report-year 2024`

Fail-closed and diagnostics validation:

- Missing-config LLM fail-closed smoke: run `fund-analysis analyze 006597 --report-year 2024 --use-llm` with LLM env absent or sanitized test env, expect exit `1`, empty stdout, no deterministic fallback.
- Real provider smoke is not a required validation item for this gate. If a later controller chooses an optional configured-provider smoke, it must verify chapters 2-6 are no longer `dependency_missing` solely because chapter 1 failed. Do not record prompt, draft, provider response or secrets.
- Secret scan over touched files and artifacts: verify no `Authorization`, `Bearer`, `sk-`, raw prompt, draft markdown, raw provider response, raw audit response or provider body is recorded.
- `git diff --check`

Expected outcomes:

- Targeted and full tests pass.
- Deterministic analyze/checklist outputs remain unchanged in behavior.
- LLM incomplete path remains fail-closed.
- Chapter 2-6 failures, timeouts or contract issues become visible in matrices after chapter 1 failure.

## Review Gates

Implementation review must verify:

- No body-chapter fail-fast dependency skip remains.
- `dependency_missing` appears only for true dependency stop reasons.
- Final assembly cannot produce an accepted report with any failed/blocked body chapter.
- CLI diagnostic matrix is secret-safe and scalar-only.
- No changes entered Host/Agent/dayu, score, golden, fixtures, quality gate, final judgment semantics or Fund writer/auditor rule relaxation.
- Dirty worktree prior changes were not reverted or folded into this gate without controller acceptance.

## Stop Conditions

Stop and return to controller if:

- Implementation requires changing Fund writer/auditor audit rules or prompt parser strictness.
- Implementation requires changing score/golden/quality gate/final judgment semantics.
- A test failure indicates final assembly currently admits incomplete body chapters into accepted reports.
- CLI matrix cannot be made secret-safe without omitting required diagnostic fields.
- Dirty worktree conflicts make it impossible to isolate this gate's diff.
- Any provider smoke would require storing prompts, drafts, raw responses or secrets.

## Blocking Questions

None. Working assumption: `fail_fast` may remain as a legacy policy field for API stability, but it must not cause synthetic dependency skips among template body chapters 1-6.

## Completion Report Format

Implementation worker should report:

- Files changed.
- State-machine change summary.
- Tests/validation commands and results.
- Confirmation that chapter 1 failure no longer suppresses chapter 2-6 execution.
- Confirmation that final assembly still fail-closes incomplete body chapters.
- Confirmation that no secret/prompt/draft/provider response was recorded.
- Residual risks, if any.

## Self-Check

- Current gate / role: `MVP independent body chapter execution gate`; planning worker only.
- Source of truth: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, Service orchestrator/final assembler/CLI diagnostics and targeted tests.
- Scope boundary: plan artifact only; implementation allowed files listed above; no code, commit, push or PR by this worker.
- Stop conditions: no blocking open questions found.
- Evidence and validation: plan is handoff-ready and code-generation-ready; validation matrix included.
- Status: pass.
