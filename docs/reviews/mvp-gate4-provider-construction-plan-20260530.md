# MVP Gate 4 Slice 4D production LLM provider construction Plan

日期：2026-05-30
角色：Gateflow planning worker
Gate：`MVP Gate 4 Slice 4D: production LLM provider construction plan gate`
分类：`heavy`
状态：planning artifact；未实现代码、未修改 runtime、未 commit、未 push、未 PR。

## 1. Worker Self-Check

- Current gate / role：当前只执行 Slice 4D planning handoff；我是 planning worker，不是 controller、implementation worker 或 reviewer。
- Source of truth：已读取 `AGENTS.md`、`docs/current-startup-packet.md`、`docs/design.md` Route C / Gate 4 段落、`docs/implementation-control.md` 当前控制面、Gate 4 plan / decision / Slice 4C controller judgment，以及当前 CLI、Service、orchestrator、Fund writer/auditor、`pyproject.toml`。
- Scope boundary：只写本 plan artifact；不得实现 provider、改 runtime、stage/delete/modify unrelated untracked、commit、push、PR、merge、release 或 promotion。
- Stop conditions：preflight 未发现 tracked dirty；provider vendor/model/secrets policy 若被 controller 判定不能采用本 plan 的 `openai_compatible` HTTP 默认策略，则实施前停止回 controller。
- Evidence and validation：本 gate 完成信号是 code-generation-ready plan artifact；implementation validation 只在后续 gate 执行。
- Next action：交 controller 做 plan review / decision；不得自行进入 implementation。

## 2. Preflight Commands

必须先运行的命令与结果：

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

判断：当前分支不是 protected trunk；`git status --short` 无 tracked dirty。上述 untracked 均按用户说明视为无关，不得 stage/delete/modify。

## 3. Direct Evidence

- `docs/current-startup-packet.md` 与 `docs/implementation-control.md`：下一入口是 `MVP Gate 4 Slice 4D: production LLM provider construction plan gate`；Slice 4C accepted locally；当前 CLI `--use-llm` 因 provider construction 未接受而 fail-closed。
- `docs/design.md` §5.4.1：Route C Gate 4 Slices 4A/4B/4C 已是代码事实；当前没有 production LLM provider construction、Host scheduling、Agent runner/tool loop 或 dayu runtime。
- `docs/reviews/mvp-gate4-final-assembler-cli-plan-decision-20260530.md`：4D 必须单独 provider-specific plan/review，覆盖 provider choice、config/env、typed client construction、failure semantics、tests without live network 和 CLI wiring。
- `docs/reviews/mvp-gate4-cli-use-llm-controller-judgment-20260530.md`：当前 `_build_llm_clients_or_fail() -> NoReturn` 只在 provider construction absent 时 accepted；Slice 4D 必须修改该签名。
- `fund_agent/ui/cli.py`：`analyze --use-llm` 当前调用 `_build_llm_clients_or_fail()` 后仍走 deterministic `analyze()`；helper 始终抛出 `LLMProviderUnavailableError("LLM provider 未配置/未实现")`。
- `fund_agent/services/fund_analysis_service.py`：`FundAnalysisService.analyze_with_llm()` 已接受显式 `ChapterOrchestratorLLMClients`，复用 deterministic core、Gate 3 和 final assembly；不构造 provider。
- `fund_agent/services/chapter_orchestrator.py`：`ChapterOrchestratorLLMClients` 显式注入 writer/auditor Protocol clients；provider 异常当前会被 Service fail-closed 为 chapter run `llm_exception`。
- `fund_agent/fund/chapter_writer.py` / `chapter_auditor.py`：Fund writer/auditor 只依赖 Protocol，不导入 provider SDK；`None` client 对应 `llm_unavailable`；malformed/empty response 有 fail-closed contract。
- `pyproject.toml`：已有 `httpx>=0.28.0`，无真实 provider SDK 依赖。
- `fund_agent/config/README.md`：config 当前只维护静态路径，不读取 env；Slice 4D 若引入 env config 必须更新此说明。

## 4. Goal

把当前 CLI fail-closed helper `_build_llm_clients_or_fail()` 替换为显式 production LLM provider construction 路径，使：

1. `fund-analysis analyze --use-llm` 在配置完整时构造真实 provider-backed `ChapterOrchestratorLLMClients`。
2. CLI 调用 `FundAnalysisService().analyze_with_llm(request, llm_clients=..., chapter_policy=...)`，输出 LLM assembled report。
3. provider construction、env parsing、timeout、malformed response、rate limit 等失败都 fail-closed，不回退 deterministic report。
4. Fund writer/auditor 继续只认 Protocol，不导入 vendor SDK、env/config 或 HTTP 细节。
5. pytest 不访问 live network；所有 provider tests 只用 fake HTTP transport / monkeypatch。

## 5. Hard Non-Goals

- 不实现 Host/Agent/dayu；不创建 `fund_agent/host` / `fund_agent/agent`，不引入 `dayu.host` / `dayu.engine`。
- 不改变 final judgment、quality gate、FQ0-FQ6、score、snapshot、golden fixture、golden answer、manifest、promotion state。
- 不改变 Fund 语义：CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、证据锚点、writer/auditor 审计规则不变。
- 不让 Fund writer/auditor 直接导入 provider SDK、`httpx` adapter、env/config 或 CLI。
- 不在 pytest 中做 live provider smoke；live smoke 如需要，必须是后续手动命令或独立 gate，且不进入默认 pytest。
- 不在 production CLI 注入 fake clients。
- 不做 deterministic fallback；LLM 路径失败时 stdout 为空或不输出报告，exit non-zero。
- 不实现 chapter 0/7 LLM polish、Evidence Confirm、完整 tool loop、并发调度、retry framework、streaming 或 provider fallback。
- 不通过 `extra_payload` 传递 provider/model/secret/timeout/max_output_chars 等显式参数。

## 6. Provider Selection / Config Strategy

### 6.1 MVP provider abstraction

MVP 选择一个最小 provider abstraction：`openai_compatible` HTTP chat-completions adapter，使用现有 `httpx` 依赖，不新增 vendor SDK 依赖。

原因：

- 当前 Fund writer/auditor 已经定义稳定 Protocol：`ChapterLLMClient.generate_chapter()` 和 `ChapterAuditLLMClient.audit_chapter()`。
- Service 只需要把 provider-backed clients 装进 `ChapterOrchestratorLLMClients`，不需要 Fund 感知 SDK。
- `httpx` 已是项目依赖；新增 SDK 会扩大供应商耦合、安装面和测试 mock 面。
- `openai_compatible` 作为 provider name 表示 HTTP contract，不把默认供应商、默认模型或真实 endpoint 写死到 Fund/Service 领域逻辑。

最小实现为一个 Service-owned adapter，同时实现 writer 与 auditor 两个 Protocol：

```python
class OpenAICompatibleChapterLLMClient(ChapterLLMClient, ChapterAuditLLMClient):
    def __init__(
        self,
        *,
        config: LLMProviderConfig,
        http_client: httpx.Client | None = None,
    ) -> None: ...

    def generate_chapter(self, request: ChapterLLMRequest) -> ChapterLLMResponse: ...

    def audit_chapter(self, request: ChapterAuditLLMRequest) -> ChapterAuditLLMResponse: ...
```

同一个 adapter 可以先同时供 writer/auditor 使用；未来如果 controller 接受分模型策略，可在新 gate 拆 `writer_model` / `auditor_model`。

### 6.2 No new dependency

不得修改 `pyproject.toml` dependencies。`httpx` 已存在，tests 可用 `httpx.MockTransport`。如果 implementation 发现必须依赖 vendor SDK，停止回 controller；不能在本 slice 临时新增。

### 6.3 Avoid live network in tests

- provider unit tests 必须传入 `httpx.Client(transport=httpx.MockTransport(...))`。
- CLI tests 必须 monkeypatch env/config 或 monkeypatch Service factory，不能设置真实 key 后访问公网。
- pytest 中禁止任何 live provider endpoint；不新增 `@pytest.mark.integration` live test 到默认 test suite。

## 7. Config / Env Contract

新增 typed config，禁止自由 dict / `extra_payload`。

建议新增文件：`fund_agent/config/llm.py`。

Public types：

```python
LLMProviderName = Literal["openai_compatible"]

@dataclass(frozen=True, slots=True, kw_only=True)
class LLMProviderConfig:
    """生产 LLM provider 配置，见模板第 1-6 章 LLM 写作/审计路径。"""

    provider_name: LLMProviderName
    model: str
    base_url: str
    api_key_env_var: str
    api_key: str = field(repr=False)
    timeout_seconds: float
    max_output_chars: int
```

Config loader：

```python
class LLMProviderConfigError(ValueError):
    """LLM provider 配置错误。"""


def load_llm_provider_config_from_env(
    environ: Mapping[str, str] | None = None,
) -> LLMProviderConfig:
    """从显式环境变量构造 provider config。"""
```

Env contract：

| Env var | Required | Default | Validation |
|---|---:|---|---|
| `FUND_AGENT_LLM_PROVIDER` | yes | none | only `openai_compatible` |
| `FUND_AGENT_LLM_MODEL` | yes | none | non-empty |
| `FUND_AGENT_LLM_BASE_URL` | yes | none | absolute `http://` or `https://`; no query/fragment |
| `FUND_AGENT_LLM_API_KEY_ENV_VAR` | no | `FUND_AGENT_LLM_API_KEY` | non-empty env var name |
| value of `api_key_env_var` | yes | none | non-empty; never logged or included in repr |
| `FUND_AGENT_LLM_TIMEOUT_SECONDS` | no | `60` | float > 0 and <= 300 |
| `FUND_AGENT_LLM_MAX_OUTPUT_CHARS` | no | `12000` | int > 0 and <= 50000 |

No default model or base URL in code. This avoids silently selecting a vendor/model that may not match user secrets policy. The production CLI becomes configured only when env explicitly supplies provider/model/base_url/key.

`max_output_chars` is passed into `ChapterOrchestrationPolicy(max_output_chars=config.max_output_chars)` and also enforced by Gate 2 writer. It is a character acceptance bound, not a provider token budget. Do not invent `max_tokens` unless a later provider contract gate accepts it.

## 8. Module Ownership

### 8.1 Ownership decision

| Concern | Owner | Files |
|---|---|---|
| Parse typed provider env config | Config | `fund_agent/config/llm.py` |
| Construct Protocol clients from typed config | Service | `fund_agent/services/llm_provider.py` |
| CLI user opt-in and exit/status mapping | UI | `fund_agent/ui/cli.py` |
| Writer/auditor Protocol and validation | Agent/Fund | existing `fund_agent/fund/chapter_writer.py`, `chapter_auditor.py`; no provider imports |
| LLM report orchestration | Service | existing `fund_agent/services/fund_analysis_service.py`, `chapter_orchestrator.py`; minimal wiring only |

### 8.2 Boundary rule

Production path after Slice 4D:

```text
UI CLI
  -> config.load_llm_provider_config_from_env()
  -> Service build_chapter_llm_clients(config)
  -> Service FundAnalysisService.analyze_with_llm(..., llm_clients, chapter_policy)
  -> Service ChapterOrchestrator
  -> Agent/Fund writer/auditor Protocol calls
```

This preserves current transition path `UI -> Service -> fund_agent/fund`. Host/Agent/dayu remains future Gate 5 and must not be introduced.

UI may import config and Service public APIs. UI must not import `fund_agent.fund.*` or concrete annual-report sources. Service provider factory may import Fund Protocol types because current Service already depends on Fund public contracts for Route C orchestration.

## 9. Public Contracts / Function Signatures

建议新增 `fund_agent/services/llm_provider.py`：

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class LLMProviderResponse:
    text: str
    model_name: str | None
    finish_reason: str | None


class LLMProviderConstructionError(RuntimeError):
    """provider client 构造失败。"""


class LLMProviderRuntimeError(RuntimeError):
    """provider 调用失败。"""


class LLMProviderRateLimitError(LLMProviderRuntimeError):
    """provider rate limit。"""


class LLMProviderMalformedResponseError(LLMProviderRuntimeError):
    """provider 响应结构不符合 contract。"""


def build_chapter_llm_clients(config: LLMProviderConfig) -> ChapterOrchestratorLLMClients:
    """构造 Route C Gate 3 所需 writer/auditor LLM clients。"""
```

Adapter internal methods：

```python
def _chat_completions_url(base_url: str) -> str: ...

def _chat_payload(*, model: str, system_prompt: str, user_prompt: str) -> dict[str, object]: ...

def _extract_text(payload: Mapping[str, object]) -> LLMProviderResponse: ...
```

`generate_chapter()` mapping：

```python
def generate_chapter(self, request: ChapterLLMRequest) -> ChapterLLMResponse:
    provider_response = self._complete(
        system_prompt=request.system_prompt,
        user_prompt=request.user_prompt,
    )
    return ChapterLLMResponse(
        text=provider_response.text,
        model_name=provider_response.model_name,
        finish_reason=provider_response.finish_reason,
    )
```

`audit_chapter()` mapping：

```python
def audit_chapter(self, request: ChapterAuditLLMRequest) -> ChapterAuditLLMResponse:
    provider_response = self._complete(
        system_prompt=request.system_prompt,
        user_prompt=_audit_user_prompt(request),
    )
    return ChapterAuditLLMResponse(
        raw_text=provider_response.text,
        model_name=provider_response.model_name,
        finish_reason=provider_response.finish_reason,
    )
```

`_audit_user_prompt()` must include existing `request.user_prompt`, `request.draft_markdown`, allowed fact ids / anchor ids, and repeat the `SEVERITY|LOCATION|MESSAGE` protocol. It must not read PDFs or external facts.

## 10. CLI Wiring

Change `_build_llm_clients_or_fail()` in `fund_agent/ui/cli.py` from `NoReturn` to:

```python
def _build_llm_clients_or_fail() -> tuple[ChapterOrchestratorLLMClients, ChapterOrchestrationPolicy]:
    """从生产配置构造 LLM clients 和章节策略。"""
```

Implementation outline:

```python
if use_llm:
    llm_clients, chapter_policy = _build_llm_clients_or_fail()
    result = asyncio.run(
        FundAnalysisService().analyze_with_llm(
            request,
            llm_clients=llm_clients,
            chapter_policy=chapter_policy,
        )
    )
else:
    result = asyncio.run(FundAnalysisService().analyze(request))
```

After `analyze_with_llm()`:

- If `result.final_assembly_result.report_markdown is None`, CLI must exit `1`, stderr starts with `LLM 分析未完成：...`, stdout empty, and no deterministic fallback.
- If accepted, print `_echo_quality_gate_summary(result)` then `result.report_markdown`.
- Existing deterministic `QualityGateBlockedError` / `QualityGateNotRunBlockedError` handling remains unchanged and must still exit `2`.
- Existing generic exception behavior remains exit `1`, but provider-specific config/construction/runtime errors should have clearer messages.

`checklist` remains without `--use-llm`.

## 11. Failure Semantics

### 11.1 Fail before Service call

These errors occur before `FundAnalysisService.analyze_with_llm()` and must not create writer/auditor clients:

| Failure | Detection | CLI behavior |
|---|---|---|
| missing `FUND_AGENT_LLM_PROVIDER` | config loader | exit `1`, stderr `LLM provider 配置错误：缺少 FUND_AGENT_LLM_PROVIDER`, stdout empty |
| unsupported provider | config loader | exit `1`, stderr `LLM provider 配置错误：unsupported provider ...`, stdout empty |
| missing model | config loader | exit `1`, stderr config error, stdout empty |
| missing/invalid base_url | config loader | exit `1`, stderr config error, stdout empty |
| missing API key env var value | config loader | exit `1`, stderr names env var but never prints key, stdout empty |
| invalid timeout/max_output_chars | config loader | exit `1`, stderr config error, stdout empty |
| provider client construction invariant failure | Service factory | exit `1`, stderr `LLM provider 构造失败：...`, stdout empty |

These failures replace current `LLM provider 未配置/未实现` fail-closed helper.

### 11.2 Enter writer/auditor as existing fail-closed LLM semantics

These failures may happen after Service starts LLM orchestration:

| Failure | Provider adapter behavior | Current/Planned Service result | CLI behavior |
|---|---|---|---|
| writer/auditor client accidentally `None` in non-CLI tests/API usage | existing Fund Protocol handling | `llm_unavailable` blocked result | no production CLI path should pass `None`; direct Service tests assert existing behavior |
| timeout/network/DNS/connect/read error | raise `LLMProviderRuntimeError` with safe message | `ChapterRunStopReason="llm_exception"` via current orchestrator catch, or controller may accept a small Service mapping to `llm_unavailable` if reviewer requires it | final assembly incomplete; CLI exit `1`, no deterministic fallback |
| HTTP 429/rate limit | raise `LLMProviderRateLimitError` | `llm_exception` unless Service maps typed rate limit to unavailable | exit `1`, stderr includes rate-limit category, no stdout |
| HTTP 5xx | raise `LLMProviderRuntimeError` | `llm_exception` | exit `1`, no fallback |
| HTTP 4xx auth/config-like error | raise `LLMProviderRuntimeError` with status only, no key | `llm_exception` | exit `1`, no fallback |
| provider malformed JSON/shape | raise `LLMProviderMalformedResponseError` | `llm_exception` | exit `1`, no fallback |
| provider returns empty text | return protocol response with empty text | existing writer `llm_empty_response` or auditor parse failure | final assembly incomplete; exit `1` |
| provider returns markdown violating anchors/forbidden phrases | return protocol response | existing writer/auditor `llm_contract_violation` / audit fail | final assembly incomplete; exit `1` |

MVP should not broaden Fund writer/auditor exception handling. If review insists timeout/network/rate-limit must be typed as `llm_unavailable` rather than `llm_exception`, the allowed smallest change is in Service `chapter_orchestrator.py` only: add a private `_map_provider_exception_to_stop_reason()` that maps `LLMProviderRuntimeError` subclasses to `llm_unavailable` while preserving all non-provider exceptions as `llm_exception`. Do not change Fund Protocols for this.

## 12. Implementation Slices

### 4D1 - Typed config and provider factory

Objective：新增 typed config + HTTP provider adapter + Service factory；不 touch CLI command flow yet.

Allowed files:

- `fund_agent/config/llm.py`
- `fund_agent/config/__init__.py`
- `fund_agent/services/llm_provider.py`
- `fund_agent/services/__init__.py`
- `tests/config/test_llm_config.py`
- `tests/services/test_llm_provider.py`
- `tests/README.md`
- implementation evidence under `docs/reviews/`

Exact changes:

- Implement `LLMProviderConfig`, `LLMProviderConfigError`, `load_llm_provider_config_from_env()`.
- Implement `OpenAICompatibleChapterLLMClient` and `build_chapter_llm_clients(config)`.
- Use `httpx.Client(timeout=config.timeout_seconds)` in production construction; support injected `http_client` only in adapter constructor for unit tests.
- Parse OpenAI-compatible response shape conservatively: require `choices[0].message.content` string; optional `model`; optional `choices[0].finish_reason`.
- Never log or repr API key.
- Do not import CLI in Service/config.
- Do not import provider module in Fund.

Non-goals:

- No CLI `--use-llm` behavior change in this slice.
- No env defaults for provider/model/base_url.
- No live HTTP tests.

Validation:

```text
uv run ruff check fund_agent/config/llm.py fund_agent/services/llm_provider.py tests/config/test_llm_config.py tests/services/test_llm_provider.py
uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py -q
```

Expected assertions:

- Missing provider/model/base_url/key fail config.
- Unsupported provider fail config.
- API key not present in `repr(config)` or error text.
- MockTransport receives Authorization bearer header and expected JSON body.
- Writer maps provider response to `ChapterLLMResponse`.
- Auditor maps provider response to `ChapterAuditLLMResponse.raw_text`.
- 429/timeout/malformed response raise typed provider errors without live network.

Stop condition:

- If implementation requires a vendor SDK or real network to parse response, stop and return to controller.

### 4D2 - CLI `--use-llm` wiring

Objective：replace `_build_llm_clients_or_fail()` fail-closed stub with config/factory construction and call `analyze_with_llm()`.

Allowed files:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`
- implementation evidence under `docs/reviews/`

Exact changes:

- Import only public Service/config APIs; keep test `test_cli_module_imports_service_but_not_agent_internals` passing.
- `_build_llm_clients_or_fail()` returns `(ChapterOrchestratorLLMClients, ChapterOrchestrationPolicy)`.
- `analyze --use-llm` calls `FundAnalysisService().analyze_with_llm(...)`, not deterministic `analyze()`.
- Missing config/API key exits `1`, stderr config error, stdout empty, Service not called.
- Configured path passes returned clients and `ChapterOrchestrationPolicy(max_output_chars=config.max_output_chars)` to Service.
- Incomplete LLM result exits `1`, stderr explains orchestration/final assembly status, stdout empty; no fallback.
- Keep quality gate errors exit `2` unchanged.
- Keep `checklist --use-llm` rejected by Typer because checklist has no such option.

Non-goals:

- No changes to Service internals except using accepted public APIs.
- No fake clients in production helper; tests may monkeypatch factory/config at module boundary.

Validation:

```text
uv run ruff check fund_agent/ui/cli.py tests/ui/test_cli.py
uv run pytest tests/ui/test_cli.py -q
```

Expected assertions:

- `analyze --use-llm` missing config: exit `1`, stdout empty, no Service call.
- Configured `--use-llm`: calls `analyze_with_llm()` exactly once, does not call `analyze()`.
- Configured accepted result: prints LLM report markdown.
- Configured incomplete result: exit `1`, no deterministic report.
- Quality gate blocked/not-run still exit `2`.
- Default `analyze` path unchanged and does not construct provider.
- `checklist --use-llm` remains invalid.

Stop condition:

- If CLI needs to import `fund_agent.fund.*` to construct clients, stop and return to controller.

### 4D3 - Docs, design/control sync, regression validation

Objective：document current provider contract and prove full regression surface stays inside Slice 4D.

Allowed files:

- `README.md`
- `fund_agent/README.md`
- `fund_agent/config/README.md`
- `tests/README.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- implementation evidence under `docs/reviews/`

Exact changes:

- Root README: document `fund-analysis analyze --use-llm` env contract and fail-closed behavior; keep deterministic default path as primary.
- `fund_agent/config/README.md`: update that config now owns typed LLM env config in addition to static paths.
- `fund_agent/README.md`: note Service-owned provider construction and Fund Protocol boundary without leaking implementation details.
- `tests/README.md`: state provider tests use fake HTTP only; no live network in pytest.
- `docs/design.md` / startup/control docs: after implementation acceptance, update Route C Gate 4 Slice 4D from future-only to current accepted fact; keep Host/Agent/dayu future-only.

Validation:

```text
uv run ruff check .
uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/ui/test_cli.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py -q
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
git diff --check
```

Expected assertions:

- Full pytest remains network-free.
- Coverage remains above current project gate.
- Docs do not claim Host/Agent/dayu or provider fallback exists.

Stop condition:

- If docs need to represent provider/model/secrets policy not covered by this plan, record blocking question for controller.

## 13. Test Strategy

- Unit tests use fake HTTP/client only. Preferred: `httpx.MockTransport` for provider adapter; monkeypatch `os.environ` mapping for config loader; monkeypatch CLI config/factory for CLI path tests.
- No real API key required for pytest.
- No outbound network allowed in pytest. Add tests that would fail if `httpx.Client` reaches live transport by not using default client in provider unit tests.
- CLI tests cover both configured and fail-closed paths.
- Service tests remain provider-agnostic: existing `tests/services/test_fund_analysis_service_llm.py` should keep fake Protocol clients and not import provider config.
- Existing Fund writer/auditor tests should remain unchanged; provider construction must not force Fund tests to know HTTP/config.

## 14. Review Matrix

Plan review should verify:

| Area | Review question |
|---|---|
| Architecture boundary | Does UI still depend only on config/Service public APIs and never `fund_agent.fund.*`? |
| Service/config ownership | Is env parsing in config and Protocol client construction in Service, not Fund? |
| No extra_payload | Are provider/model/base_url/key env var/timeout/max_output_chars typed fields only? |
| Failure semantics | Do missing config and unsupported provider fail before Service call? Do runtime provider failures fail closed with no deterministic fallback? |
| Test isolation | Can all provider tests run without live network or real key? |
| Dependency discipline | Does implementation reuse `httpx` and avoid new SDK dependency? |
| Route C scope | Are Host/Agent/dayu, final judgment, quality/golden/score/snapshot/promotion untouched? |
| Docs sync | Do README/config/design/control describe current facts only after implementation? |

Implementation/code review should verify:

- `_build_llm_clients_or_fail()` no longer returns `NoReturn`, but still fails closed on config/construction errors.
- Production helper never constructs fake clients.
- API key never appears in repr/log/stderr.
- Provider adapter handles malformed response and non-2xx status deterministically.
- `analyze --use-llm` does not call deterministic `analyze()`.
- Deterministic default `analyze` and `checklist` behavior remains unchanged.

## 15. Residual Risks

| Risk | Disposition / owner |
|---|---|
| `openai_compatible` HTTP shape may not fit the user's eventual production vendor | Stop condition: controller/user must choose another provider contract before implementation or open later provider-specific gate |
| Single model for writer and auditor may be suboptimal | Accepted MVP simplification; future gate may add `writer_model` / `auditor_model` typed config |
| No retry/backoff may make transient network failures frequent | Accepted MVP fail-closed behavior; retry policy is future reliability gate |
| No live smoke in pytest means credentials/endpoints are not verified by CI | Intentional; live smoke must be manual/explicit and outside default pytest |
| `max_output_chars` is a local acceptance cap, not provider token cap | Documented; future provider token budget needs separate typed contract |
| Runtime provider exceptions currently surface as `llm_exception` unless Service mapping is accepted | Review/controller may require small Service mapping to `llm_unavailable`; do not change Fund to solve this |

## 16. Blocking Questions For Controller

No current blocking question under this plan's working decision:

- MVP provider contract is `openai_compatible` HTTP chat-completions over existing `httpx`.
- Model, base URL and API key are deployment env configuration, not code defaults.
- API key is read from the env var named by `FUND_AGENT_LLM_API_KEY_ENV_VAR` defaulting to `FUND_AGENT_LLM_API_KEY`.

Blocking if controller/user rejects any of those three decisions: implementation must stop before 4D1 and return for provider/secrets policy decision.

## 17. Completion Report Format For Implementation Worker

Implementation worker must report:

- Self-check: pass / blocked with reason.
- Slice id completed.
- Changed files.
- Public contracts added/changed.
- Validation commands and results.
- Network isolation evidence: no live provider/API calls in pytest.
- Docs updated or explicit docs deferral reason.
- Residual risks classified against this plan.
- Confirmation: no Host/Agent/dayu, no final judgment/quality/golden/score/snapshot/promotion changes, no deterministic fallback.
