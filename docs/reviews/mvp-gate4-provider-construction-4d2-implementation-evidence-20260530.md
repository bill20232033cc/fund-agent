# MVP Gate 4 Slice 4D2 implementation evidence

日期：2026-05-30
角色：Gateflow implementation worker（非 controller）
Gate：`MVP Gate 4 Slice 4D2: CLI --use-llm provider construction wiring`
状态：implementation completed；未 review、未 commit、未 push、未 PR、未 merge、未 release。

## Worker self-check

- Current gate / role：当前只执行 4D2 implementation；我是 implementation worker，不是 controller。
- Source of truth：已读取 `AGENTS.md`、`docs/current-startup-packet.md` Gate 4 / Route C 状态、`docs/design.md` Route C / Gate 4 段落、4D plan、plan decision A1-A8、4D1 controller judgment，以及指定 CLI/config/provider/Service/test 文件。
- Scope boundary：只修改允许文件 `fund_agent/ui/cli.py`、`tests/ui/test_cli.py` 与本 evidence artifact；未修改 Service/Fund internals、design/control docs、README、golden/score/snapshot/quality semantics。
- Stop conditions：未触发；CLI 未 import `fund_agent.fund.*`、Host/dayu、provider SDK；测试未使用真实 provider/network/API key。
- Evidence and validation：见下方命令结果。
- Next action：交回 controller 做 code review / 后续 gate；本 worker 不 commit、不 push、不 PR。

## Preflight

```text
$ git branch --show-current
codex/local-reconciliation
```

```text
$ git status --short
?? --help
?? docs/reviews/overnight-release-maintenance-deferred-coverage-status-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-decision-20260529.json
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-mimo-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-implementation-evidence-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-mimo-20260529.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md
?? docs/reviews/repo-review-20260526-231040.md
?? docs/reviews/repo-review-20260527-215953.md
?? docs/reviews/repo-review-20260527-225303.md
?? docs/tmux-agent-memory-store.md
?? reviews/
```

判断：无 tracked dirty；untracked 与用户提示一致，未 stage/delete/modify。

## Changed files

- `fund_agent/ui/cli.py`
  - Removed temporary CLI-only `LLMProviderUnavailableError` and `LLM_PROVIDER_UNAVAILABLE_MESSAGE`.
  - `_build_llm_clients_or_fail()` now returns `(ChapterOrchestratorLLMClients, ChapterOrchestrationPolicy)`.
  - Helper loads typed env config via `load_llm_provider_config_from_env()`, builds clients via `build_chapter_llm_clients(config)`, and passes `ChapterOrchestrationPolicy(max_output_chars=config.max_output_chars)`.
  - `analyze --use-llm` now calls `FundAnalysisService().analyze_with_llm(request, llm_clients=..., chapter_policy=...)`.
  - Default `analyze` path still calls deterministic `analyze()` and does not construct/read LLM provider config.
  - Missing/invalid config exits 1 with `LLM provider 配置错误：...`; construction failure exits 1 with `LLM provider 构造失败：...`; quality gate blocked/not-run remains exit 2.
  - Incomplete LLM assembly exits 1 with `LLM 分析未完成：...`, stdout empty, no deterministic fallback.
- `tests/ui/test_cli.py`
  - Updated fake Service LLM signature to require explicit `chapter_policy`.
  - Added/updated tests for missing config, construction error, configured accepted path, incomplete result, default deterministic path isolation, LLM quality gate blocked/not-run exit 2, and checklist `--use-llm` invalid behavior.

## Validation results

```text
$ uv run ruff check fund_agent/ui/cli.py tests/ui/test_cli.py
All checks passed!
```

```text
$ uv run pytest tests/ui/test_cli.py -q
51 passed in 1.09s
```

```text
$ uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py -q
74 passed in 0.72s
```

```text
$ git diff --check
passed
```

Additional full validation was affordable and completed:

```text
$ uv run ruff check .
All checks passed!
```

```text
$ uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
1106 passed in 5.07s
Total coverage: 91.76%
Required test coverage of 50% reached.
```

## Network isolation evidence

- CLI tests use monkeypatch fakes for `load_llm_provider_config_from_env()` and `build_chapter_llm_clients()` on configured paths.
- Missing config test uses absent env and fails before Service call.
- No CLI test uses a real API key, real endpoint or live provider.
- Provider adapter tests remain in `tests/services/test_llm_provider.py` and use fake HTTP transport from 4D1; 4D2 did not add live network tests.

## Boundary confirmations

- No Host/Agent/dayu integration.
- No `fund_agent.fund.*` import added to CLI.
- No provider SDK import, `httpx` import, PDF cache, annual-report source, download helper or `extra_payload` use added to CLI.
- No golden, score, snapshot, final judgment, FQ0-FQ6 or quality gate semantic changes.
- No deterministic fallback in LLM path; incomplete LLM result exits non-zero with stdout empty.
- No docs/design/control sync in 4D2; `docs/design.md`, `docs/current-startup-packet.md` and `docs/implementation-control.md` are deferred to 4D3 per amendment A8.

## Residual risks

- 4D3 still owns README/design/control sync after controller review acceptance.
- Retry/backoff, live provider smoke, multi-model writer/auditor split, chapter 0/7 LLM polish, Evidence Confirm and Host/Agent/dayu remain future gates per accepted plan.

Self-check: pass.
