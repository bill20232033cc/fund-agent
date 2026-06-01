# MVP Gate 4 Slice 4D1 typed LLM config and provider factory implementation evidence

日期：2026-05-30
角色：Gateflow implementation worker
Gate：`MVP Gate 4 Slice 4D1: typed LLM config and provider factory implementation gate`
分类：`heavy`
状态：implementation completed；未 commit、未 push、未 PR、未 merge、未 release、未 promotion。

## Worker Self-Check

- Current gate / role：当前只执行 4D1 implementation handoff；我是 implementation worker，不是 controller。
- Source of truth：已读取 `AGENTS.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`、`docs/design.md` Route C/Gate 4 段、4D plan/decision/reviews、`chapter_writer.py`、`chapter_auditor.py`、`chapter_orchestrator.py` 和 `pyproject.toml`。
- Scope boundary：只触碰 4D1 allowed files；未修改 CLI、Fund、orchestrator、`config/__init__.py`、pyproject、design/control、quality/golden/score/snapshot/manifest、Host/Agent/dayu。
- Stop conditions：未发现需要 vendor SDK、依赖变更、真实网络/API smoke、CLI wiring、Service analyze changes、Fund changes或 provider/secrets policy 变更。
- Evidence and validation：本 artifact 记录分支/status、实现内容、网络隔离和所有指定验证命令结果。
- Completion status：Self-check: pass。

## Preflight Evidence

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

判断：无 tracked dirty；上述 untracked 为用户说明的无关文件，未 stage/delete/modify。

## Changed Files

- `fund_agent/config/llm.py`
- `fund_agent/services/llm_provider.py`
- `fund_agent/services/__init__.py`
- `tests/config/test_llm_config.py`
- `tests/services/test_llm_provider.py`
- `tests/README.md`
- `docs/reviews/mvp-gate4-provider-construction-4d1-implementation-evidence-20260530.md`

## Implemented Contracts

- 新增 `LLMProviderName = Literal["openai_compatible"]`。
- 新增 frozen `LLMProviderConfig`，`api_key` 使用 `repr=False`。
- 新增 `LLMProviderConfigError` 与 `load_llm_provider_config_from_env(environ=None)`。
- Env contract：
  - `FUND_AGENT_LLM_PROVIDER`、`FUND_AGENT_LLM_MODEL`、`FUND_AGENT_LLM_BASE_URL` 必填。
  - `FUND_AGENT_LLM_API_KEY_ENV_VAR` 默认 `FUND_AGENT_LLM_API_KEY`。
  - API key value 必填，空字符串和纯空白视为缺失。
  - `timeout_seconds` 默认 60，要求 `0 < timeout <= 300`。
  - `max_output_chars` 默认 12000，要求 `0 < max <= 50000`。
  - `base_url` 必须是绝对 `http://` 或 `https://`，不得带 query/fragment。
- 新增 Service-owned `OpenAICompatibleChapterLLMClient`，同时实现 `ChapterLLMClient` 与 `ChapterAuditLLMClient`。
- 新增 `build_chapter_llm_clients(config)`，返回 `ChapterOrchestratorLLMClients(writer=client, auditor=client)`。
- HTTP request shape：POST OpenAI-compatible chat completions URL；`Authorization: Bearer <api_key>`；JSON body 只包含 `model` 与 `messages`。
- Response parsing：要求 `choices[0].message.content` 为 string；`model` 与 `choices[0].finish_reason` 可选；malformed 抛 `LLMProviderMalformedResponseError`。
- Runtime errors：新增 `LLMProviderConstructionError`、`LLMProviderRuntimeError`、`LLMProviderRateLimitError`、`LLMProviderMalformedResponseError`。错误消息只包含安全 status/request-id，不包含 API key、Authorization、prompt body 或完整 response body。
- Audit adapter boundary：`ChapterAuditLLMRequest.user_prompt` 作为 Gate 2 审计协议真源；adapter 只把该 prompt 与 `draft_markdown`、allowed ids、audit focus 打包进 provider user message，不重复构造或修改 `SEVERITY|LOCATION|MESSAGE` 协议。

## Tests Added

- `tests/config/test_llm_config.py`
  - missing provider/model/base_url/key fail；
  - unsupported provider fail；
  - base_url query/fragment 或非 HTTP(S) fail；
  - timeout/max_output bounds fail；
  - API key 空白 fail；
  - `repr(config)` 不泄漏 key；
  - custom API key env var、timeout、max_output 正常解析。
- `tests/services/test_llm_provider.py`
  - factory 返回同一 adapter 给 writer/auditor；
  - MockTransport 验证 Authorization header 和 JSON body；
  - writer response 映射到 `ChapterLLMResponse`；
  - auditor response 映射到 `ChapterAuditLLMResponse.raw_text`；
  - auditor 不改变既有 `user_prompt` 协议；
  - 429 映射 `LLMProviderRateLimitError`；
  - 4xx/5xx、network、timeout 映射 `LLMProviderRuntimeError`；
  - malformed response 映射 `LLMProviderMalformedResponseError`；
  - error text 不包含 key、prompt 或 full body。

## Network Isolation Evidence

- Config tests 全部传入 fake env mappings，不读取真实凭据。
- Provider tests 全部通过 `httpx.Client(transport=httpx.MockTransport(...))` 注入 fake HTTP transport。
- 本 slice 未新增 live network/API smoke，未新增 vendor SDK，未修改 `pyproject.toml`。
- 全量 pytest 通过时没有配置真实 provider endpoint 或 API key。

## Validation Output

```text
$ uv run ruff check fund_agent/config/llm.py fund_agent/services/llm_provider.py fund_agent/services/__init__.py tests/config/test_llm_config.py tests/services/test_llm_provider.py
All checks passed!
```

```text
$ uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py -q
.....................................                                    [100%]
37 passed in 0.61s
```

```text
$ uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q
........................................................................ [ 96%]
...                                                                      [100%]
75 passed in 0.54s
```

```text
$ uv run ruff check .
All checks passed!
```

```text
$ uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
1101 passed in 5.00s
Required test coverage of 50% reached. Total coverage: 91.75%
```

```text
$ git diff --check
<no output>
```

## Non-Goals Preserved

- 未修改 `fund_agent/ui/cli.py`，未接入 `--use-llm` provider-backed wiring。
- 未修改 `fund_agent/config/__init__.py`，新 config 类型不 re-export。
- 未修改 `fund_agent/fund/**`。
- 未修改 `fund_agent/services/fund_analysis_service.py` 或 `fund_agent/services/chapter_orchestrator.py`。
- 未修改 `README.md`、`fund_agent/README.md`、`fund_agent/config/README.md`、`docs/design.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`。
- 未修改 `pyproject.toml`，未新增 dependency 或 vendor SDK。
- 未修改 golden/score/snapshot/quality/final judgment/manifest/Host/Agent/dayu。
- 未做 deterministic fallback、retry/backoff、provider fallback、chapter 0/7 LLM polish 或 Evidence Confirm。

## Residuals

- 4D2 仍需把 CLI `--use-llm` 从临时 fail-closed stub 接到 typed config/factory；本 slice 故意不改变 CLI behavior。
- 单一模型同时用于 writer/auditor 是 controller-accepted MVP 简化；未来如需拆分模型，应进入独立 gate。
- 无 retry/backoff；provider runtime error 继续 fail-closed。
- 无 live provider smoke；任何真实凭据/endpoint 验证必须由后续显式授权 gate 或手工 smoke 处理。
