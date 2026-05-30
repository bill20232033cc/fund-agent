# MVP Gate 4 Slice 4D Provider Construction Plan Review (GLM)

日期：2026-05-30
角色：plan review worker (GLM)
Review target：`docs/reviews/mvp-gate4-provider-construction-plan-20260530.md`
Gate：`MVP Gate 4 Slice 4D: production LLM provider construction plan gate`
分类：`heavy`

## Verdict

**PASS_WITH_AMENDMENTS**

计划整体结构严谨、边界清晰、slice 可代码生成。以下 2 条 required amendments 不阻断 plan acceptance 但 implementation worker 必须在 4D1/4D2 执行前满足。

---

## Required Amendments

### RA1. 明确 `LLMProviderUnavailableError` / `LLM_PROVIDER_UNAVAILABLE_MESSAGE` 的处置

**Plan 引用**：§10 CLI Wiring、§11.1 Failure Semantics

**问题**：当前 `fund_agent/ui/cli.py:69` 定义了 `LLMProviderUnavailableError` 和 `LLM_PROVIDER_UNAVAILABLE_MESSAGE` 常量。计划 §10 将 `_build_llm_clients_or_fail()` 签名从 `-> NoReturn` 改为 `-> tuple[ChapterOrchestratorLLMClients, ChapterOrchestrationPolicy]`，§11.1 用新的 `LLMProviderConfigError`、`LLMProviderConstructionError` 覆盖了配置/构造失败路径。但计划未说明现有 `LLMProviderUnavailableError` 和 `LLM_PROVIDER_UNAVAILABLE_MESSAGE` 在 Slice 4D2 之后是删除、保留为兼容别名还是完全替换。

**要求**：plan 或 controller decision 必须明确以下之一：

- **方案 A（推荐）**：Slice 4D2 删除 `LLMProviderUnavailableError` 类和 `LLM_PROVIDER_UNAVAILABLE_MESSAGE` 常量；所有 fail-closed 路径改用 config 模块的 `LLMProviderConfigError` 和 Service 模块的 `LLMProviderConstructionError`。CLI `except` 链相应更新。
- **方案 B**：保留 `LLMProviderUnavailableError` 作为 CLI 本地 catch-all 兜底，内部由 config/construction error 链触发。

**Why**：如果 implementation worker 猜测处置方式，可能产生 CLI `except` 链中类型冲突或冗余 catch 路径，导致 fail-closed 语义被静默绕过。

**How to apply**：controller 在 plan decision 中记录选择；implementation worker 按选择执行。推荐方案 A——Slice 4D 的目标正是消除这一临时桩。

### RA2. 明确 `fund_agent/config/__init__.py` 是否需要更新

**Plan 引用**：§12 Slice 4D1 Allowed files 列出 `fund_agent/config/__init__.py` 但 Exact changes 未说明具体修改。

**问题**：当前 `fund_agent/config/__init__.py` 为空（仅 1 行）。Slice 4D1 新增 `fund_agent/config/llm.py` 定义 `LLMProviderConfig`、`LLMProviderConfigError`、`LLMProviderName` 和 `load_llm_provider_config_from_env()`。如果 `__init__.py` 不导出这些类型，CLI 和 Service 必须 `from fund_agent.config.llm import ...`，这可以工作但违反当前 config 包的隐式约定（paths 常量通过 `from fund_agent.config.paths import ...` 直接导入）。

**要求**：plan 应明确以下之一：

- 在 `__init__.py` 中 re-export 公共 config 类型（`LLMProviderConfig`、`LLMProviderConfigError`、`load_llm_provider_config_from_env`）。
- 或明确说明 config 子模块采用直接导入路径 `fund_agent.config.llm`，不在 `__init__.py` 中 re-export。

**Why**：保持导入路径一致性能降低后续维护者困惑；当前 `cli.py` 使用 `from fund_agent.config.paths import ...` 直接导入，而非 `from fund_agent.config import ...`。

**How to apply**：implementation worker 在 4D1 中按 controller 选择执行。当前代码约定是直接导入子模块，因此推荐不 re-export，保持一致。

---

## Blocking Findings

**无。**

以下逐项说明 review lens 验证结果。

---

## Review Lens 验证

### Lens 1: Provider choice — openai_compatible + httpx 是否安全 MVP 默认

**结论：安全。**

- `httpx>=0.28.0` 已是生产依赖（`pyproject.toml:34`），不新增 SDK。
- `openai_compatible` 命名表示 HTTP contract（chat completions 格式），不把供应商/模型/endpoint 写死到 Fund/Service 领域逻辑。
- 计划明确不设默认 model/base_url/API key；生产 CLI 仅在 env 完整配置后才能走 LLM 路径。
- 中国主流 LLM 厂商（智谱、通义、DeepSeek、Moonshot、百川）均暴露 OpenAI 兼容 chat completions 端点，选择面足够宽。
- §16 明确标记为 controller decision point：如果用户/controller 拒绝 `openai_compatible` 策略，implementation 必须在 4D1 前停止。
- 这不是 plan 缺陷，而是正确的决策上交。

### Lens 2: Architecture boundaries — config/env 在 config，provider factory 在 Service，UI 只调公共 API

**结论：边界合规。**

验证矩阵：

| Concern | 计划归属 | 验证 |
|---|---|---|
| Parse typed provider env config | `fund_agent/config/llm.py` | ✓ config 层职责，与 paths.py 同层 |
| Construct Protocol clients from typed config | `fund_agent/services/llm_provider.py` | ✓ Service 层职责，与 chapter_orchestrator.py 同层 |
| CLI user opt-in and exit/status mapping | `fund_agent/ui/cli.py` | ✓ UI 层职责 |
| Writer/auditor Protocol | `fund_agent/fund/chapter_writer.py`, `chapter_auditor.py` | ✓ 不引入 provider 导入 |
| LLM report orchestration | existing Service files | ✓ 只做 wiring |

实际验证的导入路径：

- CLI（ui/cli.py）当前只导入 `fund_agent.config.paths` 和 `fund_agent.services`。Slice 4D2 将增加 `from fund_agent.config.llm import ...` 和 `from fund_agent.services import ChapterOrchestratorLLMClients, ChapterOrchestrationPolicy`——不违反 UI 只依赖 Service/Config 的约束。
- `ChapterOrchestratorLLMClients` 和 `ChapterOrchestrationPolicy` 已通过 `fund_agent/services/__init__.py` 的 `__all__` 公开导出。
- Service provider adapter 需要导入 Fund Protocol 类型（`ChapterLLMClient`、`ChapterAuditLLMClient`、`ChapterLLMRequest`、`ChapterLLMResponse`、`ChapterAuditLLMRequest`、`ChapterAuditLLMResponse`）。这是 Service 对 Fund 公共契约的依赖，与 `chapter_orchestrator.py` 已有的导入模式一致。
- Fund writer/auditor 不导入任何新模块。✓
- 无 Host/Agent/dayu 引入。✓

### Lens 3: Explicit contracts — no extra_payload, typed env, API key secret, failure mappings, no deterministic fallback

**结论：合约完备。**

逐项验证：

| 合约要求 | 计划覆盖 | 验证 |
|---|---|---|
| 无 extra_payload | §5 Hard Non-Goals 明确禁止 | ✓ |
| Typed env config | `LLMProviderConfig` frozen dataclass, `load_llm_provider_config_from_env(environ)` 显式参数 | ✓ |
| API key secret | `api_key: str = field(repr=False)`；错误消息只命名 env var 不打印 key | ✓ |
| Failure mappings | §11.1 (config 阶段) + §11.2 (运行时) 完整表格，覆盖 missing config / unsupported provider / timeout / 429 / 5xx / 4xx / malformed / empty / contract violation | ✓ |
| No deterministic fallback | §5 + §10 + §11 反复声明 LLM 失败 → exit 1, stdout 空 | ✓ |
| 无 default model/base_url | §7 Env contract 表格中 provider/model/base_url 为 Required=yes, Default=none | ✓ |
| `max_output_chars` 不混淆为 provider token budget | §7 明确注释为 character acceptance bound，不发明 `max_tokens` | ✓ |

### Lens 4: Implementation slices — code-generation-ready, 足够小，allowed files 和 stop conditions 清晰

**结论：slice 设计合理。**

| Slice | 允许文件数 | 核心变更 | Stop condition | 评估 |
|---|---|---|---|---|
| 4D1 | 8 | config + provider adapter + tests | 需要 vendor SDK 或真实网络时停止 | ✓ 充分小且自包含 |
| 4D2 | 3 | CLI wiring | CLI 需要导入 fund_agent.fund.* 时停止 | ✓ 充分小 |
| 4D3 | 8 | docs sync | docs 需要表示未覆盖的 policy 时记录 blocking question | ✓ 纯文档 |

Slice 顺序正确：4D1 建立基础能力和独立测试 → 4D2 连接 CLI → 4D3 文档同步。每个 slice 都有明确的 validation commands 和 expected assertions。

### Lens 5: Test strategy — no live network/API in pytest, CLI configured/fail-closed paths covered

**结论：测试策略充分。**

- Provider unit tests 使用 `httpx.MockTransport`，不访问网络。✓
- Config tests monkeypatch `os.environ` mapping。✓
- CLI tests monkeypatch config/factory，不设真实 key。✓
- 明确禁止 `@pytest.mark.integration` live test 进入默认 suite。✓
- Existing Fund writer/auditor tests 不变。✓
- Existing Service `test_fund_analysis_service_llm.py` 保持 fake Protocol clients，不导入 provider config。✓
- Slice 4D3 validation 包含全量 `--cov-fail-under=50` 回归。✓

---

## Non-blocking Observations

### N1. `_audit_user_prompt()` 需在实现时验证 `ChapterAuditLLMRequest` 字段映射

Plan §9 描述 `_audit_user_prompt(request)` 必须包含 `request.user_prompt`、`request.draft_markdown`、allowed fact ids / anchor ids 和 SEVERITY|LOCATION|MESSAGE protocol。实现 worker 应在 4D1 编码前确认 `ChapterAuditLLMRequest` 的实际字段列表（定义在 `fund_agent/fund/chapter_auditor.py`）与 plan 描述一致。如果不一致，应调整 prompt 构造逻辑而非修改 Protocol 类型。

### N2. 单一 adapter 同时实现 writer 和 auditor Protocol 的 MVP 简化可接受

`OpenAICompatibleChapterLLMClient` 同时实现 `ChapterLLMClient` 和 `ChapterAuditLLMClient`，共用同一 `_complete()` 方法和 HTTP client。Plan §15 已将 writer/auditor 分模型列为 residual risk。这是合理的 MVP 简化。

### N3. 运行时 provider exception 到 orchestrator stop_reason 的映射策略

Plan §11.2 正确指出当前 provider runtime errors 会通过 orchestrator 的 catch 链映射为 `llm_exception`。Plan 提议的可选 `_map_provider_exception_to_stop_reason()` 方案（仅修改 Service `chapter_orchestrator.py`）是最小变更。Review 不强制要求这一映射——MVP 阶段 `llm_exception` fail-closed 已足够——但 controller 如果希望区分 rate limit / timeout 与真正的 provider 错误，该映射是推荐改进。

### N4. Plan §6.1 adapter 名称与 Fund writer `model_name`/`finish_reason` 的兼容性

`ChapterLLMResponse` 已有 `model_name: str | None` 和 `finish_reason: str | None`。Plan 的 `LLMProviderResponse` 定义了相同字段。Adapter 的 `generate_chapter()` 直接透传这些字段。这是正确的 Protocol 映射。

### N5. `load_llm_provider_config_from_env()` 接受 `environ: Mapping[str, str] | None` 参数

这使得测试可以传入显式 dict 而不 monkeypatch `os.environ`。这是良好的可测试性设计。

### N6. `ChapterOrchestrationPolicy` 的 `max_output_chars` 默认值与 `LLMProviderConfig` 的默认值一致（均为 12000）

CLI 传递 `config.max_output_chars` 到 `ChapterOrchestrationPolicy(max_output_chars=...)`。这建立了单一配置源驱动的链条，避免了 config 和 policy 默认值分歧。

---

## Review Validation Performed

1. 读取 `AGENTS.md`：确认四层边界、禁止 extra_payload、Dayu 纪律、Host/Agent/dayu deferred。
2. 读取 `docs/current-startup-packet.md`：确认当前 gate 为 Slice 4D，4C 已 accepted locally。
3. 读取 `docs/design.md`：确认 Route C Gate 4 §5.4.1 已实现状态、当前无 provider、Host/Agent/dayu。
4. 读取 `docs/implementation-control.md`：确认 next entry 为 Slice 4D plan gate，heavy 分类。
5. 读取 Gate 4 plan decision：确认 4D 需要 provider-specific plan/review，覆盖 provider choice/config/env/factory/failure/tests/CLI wiring。
6. 读取 Slice 4C controller judgment：确认 `_build_llm_clients_or_fail() -> NoReturn` 只在 provider absent 时 accepted，Slice 4D 必须修改签名。
7. 读取 `fund_agent/ui/cli.py`：确认当前 `_build_llm_clients_or_fail()` 始终抛出 `LLMProviderUnavailableError`；`analyze --use-llm` 后仍走 `analyze()`；`LLMProviderUnavailableError` 定义在 CLI 局部。
8. 读取 `pyproject.toml`：确认 `httpx>=0.28.0` 已是依赖，无 vendor SDK。
9. 验证 Protocol 类型：`ChapterLLMClient`（`chapter_writer.py:128`）、`ChapterLLMRequest`（`:84`）、`ChapterLLMResponse`（`:111`）；`ChapterAuditLLMClient`（`chapter_auditor.py`，由 orchestrator 导入）；`ChapterOrchestratorLLMClients`（`chapter_orchestrator.py:84`）；`ChapterOrchestrationPolicy`（`:97`）；均与 plan 描述一致。
10. 验证导出：`ChapterOrchestratorLLMClients` 和 `ChapterOrchestrationPolicy` 已通过 `fund_agent/services/__init__.py` 的 `__all__` 公开导出。
11. 验证 `fund_agent/config/__init__.py` 当前为空。

---

## Summary

Plan 在 provider 选择（openai_compatible + httpx）、架构边界（config/Service/UI/Fund 四层归属）、合约完备性（typed config, secret handling, failure mapping, no fallback）、slice 设计（4D1/4D2/4D3 递进）和测试策略（no live network）五个维度均通过 review lens 检验。

Required amendments 共 2 条：明确 `LLMProviderUnavailableError` 的处置方式（RA1），明确 `config/__init__.py` 导出策略（RA2）。均可在 controller decision 中一步解决，不阻断 plan acceptance。
