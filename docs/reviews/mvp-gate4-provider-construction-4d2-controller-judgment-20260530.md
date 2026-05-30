# MVP Gate 4 Slice 4D2 Controller Judgment

日期：2026-05-30
角色：phaseflow / gateflow controller
Gate：`MVP Gate 4 Slice 4D2: CLI --use-llm provider construction wiring gate`
结论：accepted local checkpoint

## Scope

本 slice 只接受 CLI provider construction wiring：

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`
- `docs/reviews/mvp-gate4-provider-construction-4d2-implementation-evidence-20260530.md`
- `docs/reviews/mvp-gate4-provider-construction-4d2-implementation-review-mimo-20260530.md`
- `docs/reviews/mvp-gate4-provider-construction-4d2-implementation-review-glm-20260530.md`

本 slice 未修改 Service/Fund/orchestrator internals，未修改 design/control/README docs，未进入 Host/Agent/dayu，未触碰 golden、score、snapshot、final judgment 或 FQ0-FQ6 quality semantics。

## Evidence

- Implementation evidence：`docs/reviews/mvp-gate4-provider-construction-4d2-implementation-evidence-20260530.md`
- MiMo review：`docs/reviews/mvp-gate4-provider-construction-4d2-implementation-review-mimo-20260530.md`
- GLM review：`docs/reviews/mvp-gate4-provider-construction-4d2-implementation-review-glm-20260530.md`

MiMo verdict：`PASS`

- N1：provider runtime errors may fall through to generic `分析失败：` handler if leaked past Service. Controller裁决：non-blocking residual。当前计划 §11.2 要求 fail-closed、exit 1、no deterministic fallback；正常 orchestration path 会将 provider runtime error 收敛为 incomplete final assembly。更细 CLI runtime prefix 可后续独立收敛。
- N2：`_llm_incomplete_message()` 使用 duck typing and no explicit result annotation。Controller裁决：non-blocking。该 helper 是 CLI display helper，兼容 real result 与测试替身，不改变 public contract。

GLM verdict：`PASS`

- N1：provider runtime error message classification。裁决同上。
- N2：catch blocks cover both LLM and non-LLM branches. Controller裁决：non-blocking。统一 exception handling 结构清晰，default branch does not invoke provider config/factory.
- N3：`_llm_incomplete_message()` no explicit type. 裁决同 MiMo N2。

## Controller Validation

已由 controller 重新执行：

```text
uv run ruff check fund_agent/ui/cli.py tests/ui/test_cli.py
```

结果：passed。

```text
uv run pytest tests/ui/test_cli.py -q
```

结果：`51 passed in 1.03s`。

```text
uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py -q
```

结果：`74 passed in 0.53s`。

```text
uv run ruff check .
```

结果：passed。

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

结果：`1106 passed in 5.06s`，total coverage `91.76%`，required coverage `50%` reached。

```text
git diff --check
```

结果：passed。

## Decision

4D2 accepted.

接受依据：

1. Temporary CLI-only `LLMProviderUnavailableError` and `LLM_PROVIDER_UNAVAILABLE_MESSAGE` were removed.
2. `_build_llm_clients_or_fail()` now returns `(ChapterOrchestratorLLMClients, ChapterOrchestrationPolicy)`.
3. `analyze --use-llm` reads typed env config, builds provider clients, passes `ChapterOrchestrationPolicy(max_output_chars=config.max_output_chars)`, and calls `FundAnalysisService().analyze_with_llm(...)`.
4. Default `analyze` remains deterministic and does not read LLM env or construct provider.
5. Missing/invalid config and construction failure exit `1`, write classified stderr, leave stdout empty, and do not call Service.
6. Incomplete LLM final assembly exits `1` with `LLM 分析未完成：...`, leaves stdout empty, and does not fall back to deterministic report.
7. Quality gate blocked/not-run still exit `2` in the LLM path.
8. `checklist --use-llm` remains invalid.
9. CLI import boundary remains UI -> config/Service public APIs; no `fund_agent.fund.*`, Host/dayu, provider SDK/httpx, or `extra_payload` was introduced.
10. Tests use monkeypatch/fakes only; no live provider, real API key, or network test was added.

## Residuals

- `4D3` must update docs and control truth after 4D1/4D2 accepted: root README, `fund_agent/README.md`, `fund_agent/config/README.md`, `tests/README.md`, `docs/design.md`, `docs/current-startup-packet.md`, and `docs/implementation-control.md`.
- Provider runtime error CLI message classification is acceptable for MVP fail-closed behavior; a future polish gate may add a dedicated `LLMProviderRuntimeError` catch if runtime leakage becomes a user-facing diagnostics issue.
- Retry/backoff, live provider smoke, multi-model writer/auditor split, chapter 0/7 LLM polish, Evidence Confirm, and Host/Agent/dayu remain future gates.

## Next Entry Point

`MVP Gate 4 Slice 4D3: docs, design/control sync, and full regression gate`

4D3 may now record provider-backed CLI path as accepted current fact because 4D1 and 4D2 implementation reviews passed. It must not introduce Host/Agent/dayu, provider fallback, live smoke in pytest, score/golden/quality semantics changes, or deterministic fallback.
