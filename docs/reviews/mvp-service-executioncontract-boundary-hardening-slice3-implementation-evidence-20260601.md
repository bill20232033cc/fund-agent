# MVP Service ExecutionContract boundary hardening Slice 3 implementation evidence

Date: 2026-06-01
Gate: `MVP Service ExecutionContract boundary hardening gate`
Slice: `Slice 3: CLI -> Host Uses Typed Execution Request`
Approved plan: `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md`
Prior slice checkpoint: `854d4b8 gateflow: accept MVP Service ExecutionContract boundary hardening slice 2`
Status: implemented; awaiting code review handoff because panel review agents failed clear verification

## Step Self-check

- Current gate / role: 当前处于 Slice 3 implementation 完成后、code review 派发前；controller 只记录 evidence、验证 scope 和准备 review handoff。
- Source of truth: accepted plan Slice 3、Slice 3 implementation worker completion report、current diff and targeted test output.
- Scope boundary: Slice 3 当前只修改 `fund_agent/ui/cli.py` 和 `tests/ui/test_cli.py`; historical untracked residuals remain untouched.
- Stop conditions: review panel clear verification failed for AgentDS, AgentMiMo and AgentGLM; no accepted Slice 3 checkpoint can be created until code review/re-review passes.
- Evidence and validation: targeted CLI/Service LLM tests pass; no staged files.
- Next action: obtain a clean review panel or explicit deviation authorization, then run Slice 3 code review.

## Changed Files

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`

## Implemented Plan Items

- CLI `analyze --use-llm` now calls Service-owned `build_fund_llm_execution_request(request, opt_in_mode="explicit_cli_flag")`.
- Removed CLI direct provider preparation dependencies:
  - `load_llm_provider_config_from_env`
  - `build_chapter_llm_clients`
  - `ChapterOrchestrationPolicy`
  - `ChapterOrchestratorLLMClients`
- `_run_llm_analysis_in_host()` now accepts only `FundLLMExecutionRequest`.
- Host timeout is derived from the explicit scalar `execution_request.runtime_plan.host_timeout_seconds`.
- Host operation closure calls `FundAnalysisService().analyze_with_llm_execution(execution_request, host_context=host_context)`.
- Host `operation_name` remains `fund_analysis_llm_report` and does not encode fund code/year.
- Existing fail-closed behavior remains in place:
  - incomplete final assembly attaches the incomplete result and fails closed;
  - quality gate block/not-run exceptions are re-raised to preserve CLI exit behavior;
  - no deterministic fallback is introduced.
- Default deterministic `analyze` branch remains outside the LLM builder/Host path.

## Test Coverage Added Or Updated

- Fake CLI Service now exposes `analyze_with_llm_execution(execution_request, host_context=None)` and records the typed request.
- Configured `--use-llm` test asserts:
  - deterministic `analyze()` is not called;
  - typed `FundLLMExecutionRequest` reaches the Service;
  - contract fund code, report year and opt-in mode are explicit and correct;
  - Host timeout matches `runtime_plan.host_timeout_seconds`;
  - fake Host records only generic run arguments and no business fields.
- Default `analyze` negative boundary test uses raising fakes for the LLM builder and Host runner to prove no opt-in means no LLM preparation and no Host run.
- `checklist` negative boundary test proves checklist does not call LLM builder or Host.
- Unsupported `checklist --use-llm` remains rejected before Service/Host execution.
- Missing config and provider construction failure tests prove failure happens before Host run and before Service report execution.
- Incomplete LLM result tests preserve safe diagnostics, safe matrix output and no deterministic fallback.
- CLI source boundary test continues to reject provider SDK/httpx/direct Fund import/`extra_payload`/`build_chapter_llm_clients`.

## Validation

Command:

```text
uv run pytest tests/ui/test_cli.py tests/services/test_fund_analysis_service_llm.py -q
```

Results:

```text
69 passed in 0.84s
69 passed in 1.17s
```

## Panel Review Handoff Status

Per the user's `$init-agents` instruction, code review/re-review should use AgentMiMo, AgentDS or AgentGLM via tmux panel after:

1. `tmux-cli status`
2. `tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{window_name} #{pane_current_command} #{pane_title}'`
3. `/clear`
4. `tmux-cli wait_idle`
5. `tmux-cli capture` clear verification

Attempted review panel clear verification before this artifact:

- `agents:0.2` AgentDS: two `/clear` attempts; capture still showed stale `PR #21`.
- `agents:0.3` AgentMiMo: two `/clear` attempts; capture still showed stale `PR #21`.
- `agents:0.4` AgentGLM: two `/clear` attempts; capture still showed stale `PR #21`.
- `0:0.2` duplicate AgentMiMo pane: two `/clear` attempts; capture still showed stale `PR #21`.
- Continuation re-check: after rerunning `tmux-cli status` and pane discovery, additional `C-u` / `C-c C-u` input clearing attempts on the same review panes still left capture showing stale `PR #21`.
- Final blocked-audit re-check: reran `tmux-cli status`, pane discovery, `/clear`, `wait_idle`, and `capture` for `agents:0.2`, `agents:0.3`, `agents:0.4`, and `0:0.2`; all captures still showed stale `PR #21`.

Because clear verification failed, no formal Slice 3 code review handoff was sent to those panels. This is an implementation evidence artifact only, not review acceptance.

## Residual Risk Classification

- Slice 3 code review not yet completed.
  - Classification: blocking current slice acceptance.
  - Owner/destination: controller must obtain a clean review panel or explicit deviation authorization before Slice 3 accepted checkpoint.
- Host boundary regression/docs sync are not done in Slice 3.
  - Classification: covered by later approved slice / implementation-exit decision.
  - Owner/destination: Slice 4 and controller final implementation judgment.
- Historical untracked residual artifacts remain untouched.
  - Classification: out of scope for this gate.

## Completion Status

Slice 3 implementation is complete and targeted tests pass, but Slice 3 is not accepted because code review has not yet run.
