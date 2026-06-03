# MVP typed template contract Slice 6 Ch0/Ch7 readiness implementation evidence

## Scope

- Gate: `MVP typed template contract Slice 6 Ch0 consumes Ch7 with fail-closed required-body readiness implementation gate`
- Classification: `heavy`
- Role: implementation worker only, not controller
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Objective: make final assembly dependency explicit so Ch7 readiness depends on required body chapters and Ch0 consumes Ch7 instead of independently deriving or strengthening final action.

## Self-check

- Read required gate inputs: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, Slice 6 section in `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md`, current assembler and target tests.
- Confirmed required body chapters remain exactly public ids `1-6`.
- Confirmed implementation stayed in Service final assembly path and tests/docs allowed by the gate.
- Confirmed no provider/default/runtime/live probe, Agent runtime/tool-loop, score-loop, golden/readiness promotion, deterministic default behavior, schema replacement, quality gate, final judgment taxonomy, template truth, commit, push or PR action was taken.
- Confirmed unrelated pre-existing untracked workspace files were not modified.

## Changed files

- `fund_agent/services/final_chapter_assembler.py`
- `tests/services/test_final_chapter_assembler.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/ui/test_cli.py`
- `tests/README.md`
- `docs/reviews/mvp-typed-template-contract-slice6-ch0-ch7-readiness-implementation-evidence-20260603.md`

## Behavior summary

- Added `FinalAssemblyReadiness` typed adapter inside `final_chapter_assembler.v1`.
- Ch7 readiness is `ready` only when Gate 3 accepted body chapters `1-6` are present and each required chapter has `status="accepted"`, non-empty `accepted_draft`, and non-empty `accepted_conclusion`.
- Missing/unaccepted required body chapters now block Ch7 generation and therefore block Ch0/full report assembly. Default incomplete output keeps `report_markdown=None`, `chapter0_markdown=None`, and `chapter7_markdown=None`.
- Ch7 typed summary now carries action, core basis, easiest misread, next validation plan, threshold events, evidence status, readiness status, and accepted body chapter ids.
- Ch0 renders its action from the Ch7 typed summary and has an explicit equality guard: Ch0 current action must equal Ch7 action exactly.
- Missing Ch7 typed bundle produces incomplete final assembly; Ch0 does not independently derive or strengthen final action.
- Existing `--use-llm` incomplete behavior remains fail-closed with empty stdout and no deterministic fallback. Deterministic default `analyze/checklist` behavior was not modified.

## Tests added or updated

- `tests/services/test_final_chapter_assembler.py::test_ch0_action_must_equal_ch7_action`
- `tests/services/test_final_chapter_assembler.py::test_missing_required_body_chapter_blocks_ch7_and_ch0`
- `tests/services/test_final_chapter_assembler.py::test_missing_ch7_blocks_ch0_complete_report`
- `tests/services/test_fund_analysis_service_llm.py::test_partial_llm_result_does_not_fallback_to_deterministic_after_typed_readiness`
- `tests/ui/test_cli.py::test_use_llm_incomplete_typed_readiness_empty_stdout_exit_one`

## Validation

```bash
uv run pytest tests/services/test_final_chapter_assembler.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py
```

Result: PASS, `112 passed in 0.88s`.

```bash
uv run ruff check fund_agent/services tests/services tests/ui
```

Result: PASS, `All checks passed!`.

```bash
git diff --check
```

Result: PASS, no output.

## Non-goals explicitly preserved

- No Service facade typed path wiring beyond existing final assembly call surface.
- No provider/default/runtime/live probe or endpoint disposition work.
- No Agent runtime/tool-loop migration.
- No score-loop, golden/readiness promotion, snapshot refresh or quality gate semantic change.
- No deterministic default `analyze/checklist` behavior change.
- No template truth replacement and no `docs/fund-analysis-template-draft.md` edit.
- No commit, push, draft PR or live provider probe.

## Residual risks

- Ch7 is still deterministic Service-local final assembly over `FinalJudgmentDecision`; Ch7 LLM polish/audit and future Agent-owned `FinalAssemblyReadiness` remain separate future gates.
- Ch0 no-new-facts enforcement is still structural and source-bounded rather than a semantic LLM/evidence-confirm pass.
- `FinalAssemblyReadiness` is internal to the current Service assembler; future Agent execution migration must decide whether to promote or rename this contract.
