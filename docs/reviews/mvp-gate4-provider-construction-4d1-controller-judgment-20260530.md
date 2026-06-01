# MVP Gate 4 Slice 4D1 Controller Judgment

日期：2026-05-30
角色：phaseflow / gateflow controller
Gate：`MVP Gate 4 Slice 4D1: typed LLM config and provider factory implementation gate`
结论：accepted local checkpoint

## Scope

本 slice 只接受 typed LLM provider config 与 openai-compatible provider factory 支撑代码：

- `fund_agent/config/llm.py`
- `fund_agent/services/llm_provider.py`
- `fund_agent/services/__init__.py`
- `tests/config/test_llm_config.py`
- `tests/services/test_llm_provider.py`
- `tests/README.md`

本 slice 未接入 CLI `--use-llm` provider construction，未改变 Fund writer/auditor contract，未改变 Service orchestrator runtime path，未进入 Host/Agent/dayu，未触碰 golden、score、snapshot 或 quality gate。

## Evidence

- Implementation evidence：`docs/reviews/mvp-gate4-provider-construction-4d1-implementation-evidence-20260530.md`
- MiMo review：`docs/reviews/mvp-gate4-provider-construction-4d1-implementation-review-mimo-20260530.md`
- GLM review：`docs/reviews/mvp-gate4-provider-construction-4d1-implementation-review-glm-20260530.md`

MiMo verdict：`PASS_WITH_NON_BLOCKING`

- Non-blocking N1：audit 协议唯一性断言可加强。裁决：defer，当前测试已断言 provider user message 中 `SEVERITY|LOCATION|MESSAGE` 恰好出现一次，足以证明 adapter 未重建协议。
- Non-blocking N2：`build_chapter_llm_clients()` 的 broad `except Exception` 可进一步收窄或改善消息。裁决：defer，当前 `from exc` 保留 cause，且顶层消息不泄漏 prompt/key/body。

GLM verdict：`PASS`

- Non-blocking observations：具体类导出、URL 间接测试、无 retry、单模型、无 live smoke。裁决：全部 accepted residual。它们符合 4D MVP scope；retry、live smoke、多模型和 public export 收敛均需后续独立 gate，不阻塞 4D1。

## Controller Validation

已由 controller 重新执行：

```text
uv run ruff check fund_agent/config/llm.py fund_agent/services/llm_provider.py fund_agent/services/__init__.py tests/config/test_llm_config.py tests/services/test_llm_provider.py
```

结果：passed。

```text
uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py -q
```

结果：`37 passed in 0.74s`。

```text
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q
```

结果：`75 passed in 0.57s`。

```text
uv run ruff check .
```

结果：passed。

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

结果：`1101 passed in 5.08s`，total coverage `91.75%`，required coverage `50%` reached。

```text
git diff --check
```

结果：passed。

## Decision

4D1 accepted.

接受依据：

1. Env contract 是 typed、fail-closed 的；没有默认 vendor/model/base_url。
2. 空白 API key 被视为 missing；API key 不进入 config repr、错误消息、response parsing error 或 test output。
3. Provider adapter 只使用现有 `httpx` 和 `openai_compatible` chat-completions contract；没有新增 vendor SDK 或 dependency。
4. Tests 使用 fake env mapping 和 `httpx.MockTransport`；没有 live network。
5. Audit adapter 保留 `ChapterAuditLLMRequest.user_prompt` 作为 Gate 2 协议真源，不重建或弱化 `SEVERITY|LOCATION|MESSAGE` 协议。
6. Scope 未越界到 CLI wiring、Fund/Service orchestration、Host/dayu、golden/readiness、score、quality gate 或 `extra_payload`。

## Residuals

- `4D2`：CLI `--use-llm` provider construction wiring。需要把 temporary unavailable path 替换为 typed config/provider construction/runtime error handling。
- `4D3`：provider-backed report path accepted 后再同步 `docs/design.md`、`docs/current-startup-packet.md` 和 `docs/implementation-control.md`。4D1/4D2 期间不得把 provider-backed CLI 写成当前完成事实。
- Future：retry/backoff、live provider smoke、多模型 writer/auditor split、provider public export 收敛，均不阻塞 4D1。

## Next Entry Point

`MVP Gate 4 Slice 4D2: CLI --use-llm provider construction wiring gate`

保守边界：4D2 只接入 config loader 与 provider factory，处理 typed errors；不得改 writer/auditor contract、orchestrator semantics、Host/dayu、golden、score 或 quality gate。
