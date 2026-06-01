# MVP provider runtime timeout hardening implementation evidence

日期：2026-05-31

Gate：`MVP provider runtime timeout hardening implementation gate`

Role：AgentCodex implementation worker, not controller and not reviewer.

## Self-check

- Current gate / role：当前只执行 implementation handoff；未启动完整 `$gateflow`，未进入 review、commit、push、PR 或 release。
- Source of truth：依据 `docs/reviews/mvp-provider-runtime-timeout-hardening-plan-20260531.md` 与 `docs/reviews/mvp-provider-runtime-timeout-hardening-plan-controller-judgment-20260531.md`。
- Scope boundary：实现只触碰 allowed runtime/test/doc 文件；未修改 `fund_agent/fund/chapter_writer.py`、`fund_agent/fund/chapter_auditor.py`、Fund LLM dataclass/Protocol、Host/Agent/dayu、golden/fixtures/score/quality gate。
- Stop condition：真实 provider rerun 被当前 shell 缺失 `FUND_AGENT_LLM_*` 配置阻断；按 plan stop condition 记录为 validation blocked，不做 config fallback。

## Changed files

- `fund_agent/config/llm.py`：新增 typed env fields `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS` 与 `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS`，默认 `2` / `1.0`，边界 `[1,3]` / `[0,30]`。
- `fund_agent/services/llm_provider.py`：实现 timeout-only bounded retry/backoff；provider runtime exceptions 携带 provider-local safe diagnostics；rate limit、network、malformed、non-2xx 不 retry。
- `fund_agent/services/chapter_orchestrator.py`：新增 Service-layer `ChapterLLMRuntimeDiagnostic`；orchestrator enrich provider diagnostics with chapter identity；映射 provider runtime / prompt_contract / audit_parse / fact_gap / code_bug。
- `fund_agent/ui/cli.py`：`--use-llm` incomplete stderr 增加首个失败章节 `chapter_id/status/stop_reason`，stdout 仍为空且不 fallback。
- `tests/config/test_llm_config.py`、`tests/services/test_llm_provider.py`、`tests/services/test_chapter_orchestrator.py`、`tests/ui/test_cli.py`：补充 config、retry、diagnostic、CLI fail-closed 覆盖。
- `fund_agent/config/README.md`：同步新增 LLM timeout retry env 当前用法。

## Implemented slices

- Slice A：complete。Typed config 默认值、合法边界、非法边界、非数字和 repr 不泄密已覆盖。
- Slice B：complete。Timeout-only retry/backoff、timeout exhausted diagnostics、非 timeout 不 retry、安全错误文本已覆盖。
- Slice C：complete。Provider diagnostics 由 exception 携带，orchestrator 补齐章节身份和分类；timeout 不触发额外 regenerate。
- Slice D：complete for code/tests；real provider validation blocked by missing env in current shell。

## Validation

- `uv run ruff check .`：PASS。
- `uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q`：PASS，`157 passed`。
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`：PASS，`1151 passed`，coverage `91.82%`。
- missing-config `--use-llm` smoke：PASS，exit `1`，stdout empty，stderr `LLM provider 配置错误：missing FUND_AGENT_LLM_PROVIDER`。
- deterministic analyze `006597 / 2024` smoke：PASS，exit `0`。
- checklist `006597 / 2024` smoke：PASS，exit `0`。
- real provider `006597 / 2024 --use-llm`：blocked - current validation shell has no `FUND_AGENT_LLM_*` env; config failed before provider construction.
- `git diff --check`：PASS。

## Real provider evidence

- CLI stdout path：`reports/mvp-local-acceptance/20260531-provider-timeout-hardening/real-provider-006597-2024.stdout`
- CLI stderr path：`reports/mvp-local-acceptance/20260531-provider-timeout-hardening/real-provider-006597-2024.stderr`
- CLI exit code path：`reports/mvp-local-acceptance/20260531-provider-timeout-hardening/real-provider-006597-2024.exitcode`
- diagnostic JSON path：`reports/mvp-local-acceptance/20260531-provider-timeout-hardening/real-provider-006597-2024-diagnostic.json`
- safe classification：`provider_config_missing`

The run did not reach provider runtime, so it cannot classify as `provider_runtime_timeout` in this shell.

## Secret hygiene

- API key/header/full prompt/full draft/full provider response leaked：no.
- Focused new-report scan command：
  `rg -n "Authorization|Bearer|FUND_AGENT_LLM_API_KEY|sk-|full provider|writer user|draft markdown" reports/mvp-local-acceptance/20260531-provider-timeout-hardening`
- Focused new-report scan result：no hits.
- Broad historical `docs/reviews` scan produced existing safe-text/hygiene hits only; no new secret-bearing value was found in this gate output.

## Scope guard

- Default deterministic analyze/checklist unchanged：yes, both smoke commands exit `0`.
- Golden/fixtures/score/quality gate unchanged by this implementation：yes, scope diff query returned empty.
- Host/Agent/dayu untouched：yes.
- Fund-layer writer/auditor dataclasses and Protocol signatures unchanged by this implementation：yes.

## Residual risks

- Real provider acceptance remains unverified in this shell because provider env is absent. Owner：controller / validation environment.
- Bounded timeout retry cannot guarantee provider completion if model latency exceeds `FUND_AGENT_LLM_TIMEOUT_SECONDS * FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS`. Owner：future provider runtime tuning gate if reproduced with configured provider.
- Existing worktree contained unrelated dirty files before this handoff, including prohibited files from prior work; this implementation did not edit or revert them.

## Stop status

blocked - implementation is complete and local validation passed, but required real provider rerun is blocked by missing provider env in the current validation shell.
