# MVP Gate 4 Slice 4C CLI --use-llm implementation evidence

日期：2026-05-30

角色：Gateflow-governed implementation worker，不是 controller。

Gate：`MVP Gate 4 Slice 4C: CLI --use-llm opt-in fail-closed integration gate`

## 1. Worker self-check

- Current gate / role：当前只执行 Slice 4C implementation；未启动完整 `$gateflow`，未进入 review、commit、push、PR、merge、release 或 promotion。
- Source of truth：已读取 `AGENTS.md`、`docs/current-startup-packet.md`、`docs/design.md` Route C / Gate 4 段落、Gate 4 plan、plan decision、Slice 4B controller judgment、`fund_agent/ui/cli.py`、`tests/ui/test_cli.py`、`README.md` CLI 相关段落。
- Scope boundary：只修改 allowed files；未修改 `fund_agent/services/fund_analysis_service.py`、`fund_agent/fund/**`、final judgment、quality gate/FQ、score、snapshot、golden fixtures/answers、manifests、Host/Agent/dayu 或 provider construction。
- Stop conditions：未发现 tracked dirty 超出本 slice；无需 API key/env/model/provider/SDK/network smoke；deterministic analyze/checklist 行为可保持。
- Evidence and validation：本 artifact 记录 changed files、行为决策、验证输出、non-goals preserved、residuals。

## 2. Required preflight

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

Preflight conclusion：无 tracked dirty；untracked 均为 controller 已提示的无关文件类别，未 stage、删除或修改。

## 3. Changed files

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`
- `README.md`
- `tests/README.md`
- `docs/reviews/mvp-gate4-cli-use-llm-implementation-evidence-20260530.md`

## 4. Implemented behavior

- `fund-analysis analyze` 新增显式 `--use-llm` opt-in 参数。
- `--use-llm` 未传时保持原 deterministic path：构造同一 `FundAnalysisRequest`，调用 `FundAnalysisService().analyze(request)`，并复用原 quality gate blocked/not-run handling。
- `--use-llm` 传入时通过本地 typed fail-closed helper `_build_llm_clients_or_fail()` 在构造/调用 Service LLM 用例前失败关闭。
- fail-closed message：`LLM provider 未配置/未实现`。
- fail-closed exit code：`1`。
- fail-closed stdout：空；不输出 deterministic markdown。
- production CLI 未注入 fake writer/auditor clients，未调用 `analyze_with_llm()`。
- `fund-analysis checklist` 未增加 `--use-llm`；Typer unknown option 路径拒绝该 flag。

## 5. Tests added / updated

- `test_analyze_cli_calls_service_and_prints_report`：补充断言默认 analyze 调用 fake service `.analyze()`，不调用 `.analyze_with_llm()`。
- `test_analyze_cli_use_llm_fails_closed_before_service`：断言 `analyze --use-llm` exit `1`、stdout empty、stderr 包含 provider unavailable message、fake service `.analyze()` / `.analyze_with_llm()` 均未调用。
- `test_checklist_cli_rejects_use_llm_option`：断言 `checklist --use-llm` 被 Typer 拒绝，且不调用 checklist service。
- `test_analyze_cli_help_documents_auto_valuation_and_opt_out`：补充 analyze help / Click command params 中包含 `--use-llm`。
- `test_cli_module_llm_boundary_has_no_forbidden_runtime_imports`：静态检查 `cli.py` 未引入 `dayu`、`extra_payload`、`openai`、`anthropic`、`httpx`、provider SDK、PDF/cache/source helper 相关入口。

## 6. Documentation decision

- `README.md` 作为用户手册，记录 `fund-analysis analyze --use-llm` 是显式 opt-in；当前真实 provider 尚未接入，因此失败关闭、exit `1`、不输出 deterministic markdown、不回退默认报告；`checklist` 不支持该 flag。
- `tests/README.md` 同步 UI CLI 测试职责，记录 `analyze --use-llm` fail-closed 和 `checklist --use-llm` unknown option 覆盖。

## 7. Validation

```text
$ uv run ruff check fund_agent/ui/cli.py tests/ui/test_cli.py
All checks passed!
```

```text
$ uv run pytest tests/ui/test_cli.py -q
46 passed in 1.04s
```

```text
$ uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_final_chapter_assembler.py tests/services/test_chapter_orchestrator.py -q
51 passed in 0.63s
```

```text
$ uv run ruff check .
All checks passed!
```

```text
$ uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
1064 passed in 4.93s
Required test coverage of 50% reached. Total coverage: 91.74%
```

```text
$ git diff --check
clean
```

## 8. Non-goals preserved

- 未实现 production LLM provider construction、API key/env/config/model choice、network smoke、SDK dependency 或 retry/timeout policy。
- 未调用 `FundAnalysisService().analyze_with_llm()`，因为 Slice 4D provider construction 尚未 accepted。
- 未修改 Service internals、Fund 层、final judgment 语义、quality gate/FQ0-FQ6、score、snapshot、golden fixtures/answers、manifests、Host/Agent/dayu。
- 未把业务参数放进 `extra_payload`。
- 未 stage、删除或修改无关 untracked 文件。

## 9. Residuals

- Slice 4D production LLM provider construction remains residual / future gate owner。
- `--use-llm` 当前是可见 opt-in 入口，但在 provider construction accepted 前生产 CLI 必须继续 fail-closed。
- Chapter 0/7 LLM polish、LLM audit、Evidence Confirm/E2 source verification、Host/Agent/dayu integration 仍按 Route C 后续 gate 处理。

## 10. Completion status

Self-check: pass. Slice 4C implementation scope complete; ready for controller-assigned code review. No commit was created.
