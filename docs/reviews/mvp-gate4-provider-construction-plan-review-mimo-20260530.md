# MVP Gate 4 Slice 4D provider construction plan review — MiMo

日期：2026-05-30
角色：plan review worker
Review target：`docs/reviews/mvp-gate4-provider-construction-plan-20260530.md`

## Verdict

**PASS_WITH_AMENDMENTS**

Plan 整体设计合理、架构边界清晰、实现切片可生成代码。有 1 个 BLOCKING 发现需要 controller 决策，2 个 REQUIRED AMENDMENTS，以及若干非阻断观察。

## Blocking Findings

### B1. `_audit_user_prompt()` contract 未明确 SEVERITY|LOCATION|MESSAGE 协议包含方式

**Plan §9** `_audit_user_prompt()` 描述为：

> `_audit_user_prompt()` must include existing `request.user_prompt`, `request.draft_markdown`, allowed fact ids / anchor ids, and repeat the `SEVERITY|LOCATION|MESSAGE` protocol.

但 Gate 2 `chapter_auditor.py` 已冻结了 LLM audit 行协议。此处 "repeat the protocol" 含义模糊：是指在 user prompt 文本中重复协议说明，还是指 adapter 层不修改协议、只透传 `ChapterAuditLLMRequest.user_prompt`（该字段已包含协议说明）？

**Why blocking**：如果实现 worker 理解为"adapter 层额外构造协议说明文本"，则与 Gate 2 frozen contract 冲突——Gate 2 已经定义 `ChapterAuditLLMRequest.user_prompt` 包含完整审计协议。若实现 worker 理解为"透传已有字段"，则该句描述多余且易误解。

**Required amendment**：§9 `_audit_user_prompt()` 应明确：adapter 层只透传 `request.user_prompt`（该字段由 Gate 2 chapter_auditor 构造，已包含 SEVERITY|LOCATION|MESSAGE 协议），adapter 不额外构造或重复协议文本。`request.draft_markdown` 的组装方式应由 `chapter_auditor` 已有逻辑决定，adapter 不修改。

### B2. Provider choice 需要 controller 显式确认

**Plan §6.1** 选择 `openai_compatible` HTTP chat-completions 作为 MVP provider abstraction。**Plan §16** 列出 "Blocking if controller/user rejects any of those three decisions"。

但 plan 没有明确将 provider choice 本身作为一个需要 controller 签收的决策点。`openai_compatible` 意味着：
- 用户必须有一个兼容 OpenAI chat-completions API 的 endpoint（如 OpenAI、DeepSeek、Moonshot、vLLM 等）
- 用户必须自行管理 API key 和 base URL
- 该选择不覆盖 Anthropic Claude（需要不同 request/response shape）

**Why blocking**：这不是技术阻断，而是业务/安全决策。controller 必须确认 `openai_compatible` 是可接受的 MVP 默认，还是需要在 plan 中加入 provider 选择文档化或 Anthropic 兼容路径。当前 plan 将此作为 "blocking question" 但放在 §16 靠后位置，review worker 建议 controller 在 plan decision 中显式签收。

**Required action**：controller 在 plan decision 中显式确认 `openai_compatible` provider choice，或要求 plan 增加 provider 选择说明。

## Required Amendments

### R1. `ChapterOrchestrationPolicy` 已有 `max_output_chars` 字段需确认

**Plan §7** 和 **§10** 引用 `ChapterOrchestrationPolicy(max_output_chars=config.max_output_chars)`。需确认 `ChapterOrchestrationPolicy` 已有该字段且类型兼容。若该字段不存在，4D2 CLI wiring 切片会因类型错误阻断。

**Required action**：implementation worker 在 4D1 前验证 `ChapterOrchestrationPolicy` dataclass 是否已有 `max_output_chars: int` 字段；若缺失，需先在 chapter_orchestrator.py 中补充该字段（属于 4D1 或 controller 授权的前置变更）。

### R2. `LLMProviderConfig.api_key` 不应在 dataclass 默认实例中暴露

**Plan §7** 定义 `api_key: str = field(repr=False)`。但 dataclass `frozen=True` 意味着该字段在构造时必须提供。如果 config loader 在缺少 key 时抛出 `LLMProviderConfigError`，这没问题。但 plan 应明确：`load_llm_provider_config_from_env()` 在 API key env var 值为空字符串时必须抛出 `LLMProviderConfigError`，而不是构造一个 `api_key=""` 的 config 对象。

**Required action**：§7 env contract 表中 `value of api_key_env_var` 行的 validation 列应明确 "non-empty string; empty string treated as missing"。

## Non-Blocking Observations

### N1. 单 writer/auditor 模型接受为 MVP 简化

Plan §15 residual 中接受单模型。这合理，但 implementation worker 应确保 `LLMProviderConfig` 未来可扩展为 `writer_model` / `auditor_model` 而不需要破坏 frozen dataclass。当前设计已通过 `model: str` 单字段满足，未来拆分只需新增字段，不会 break 现有构造。

### N2. `max_output_chars` 与 provider token cap 的区分

Plan §15 residual 已说明。建议 §7 env contract 表中对 `FUND_AGENT_LLM_MAX_OUTPUT_CHARS` 加一行说明：这是本地接受字符上限，不是 provider token 上限，避免用户误解。

### N3. 无 retry/backoff 策略

Plan §15 residual 接受无 retry。这合理，但 implementation worker 应在 `LLMProviderRuntimeError` 异常消息中包含 HTTP status code 和请求 ID（如有），便于用户排查。plan §11.2 已说 "with safe message, no key"，建议补充 "include status code and request-id if available"。

### N4. Plan §12 切片验证命令完整性

4D1 验证命令只检查新增文件，不回归现有 Service/Fund 测试。建议 4D3 的 full regression 验证覆盖 4D1/4D2 变更后的完整测试套件。当前 4D3 已包含 `uv run pytest --cov-fail-under=50`，满足要求。

### N5. `docs/design.md` 更新时机

Plan §12 4D3 说 "after implementation acceptance, update Route C Gate 4 Slice 4D from future-only to current accepted fact"。这正确。但 implementation worker 应注意：design.md 更新必须在 controller judgment accepted 后才能写入 "current accepted fact"，不能在 implementation evidence 阶段就声称 accepted。

## Review Validation Performed

| Check | Result |
|-------|--------|
| Provider choice 安全性 | `openai_compatible` + existing `httpx` 是安全 MVP 默认；不引入新依赖；需 controller 签收 |
| 架构边界 | Config 在 config，provider factory 在 Service，UI 只调用 public API，Fund 保持 Protocol-only，无 Host/Agent/dayu ✓ |
| 无 extra_payload | provider/model/base_url/key/timeout/max_output_chars 均为 typed config 字段 ✓ |
| API key secret handling | `repr=False`，不 log，不 include in error ✓（需确认 R2 空字符串边界） |
| Failure mappings | 缺失 config、unsupported provider、runtime 异常均有明确 exit code 和 stderr ✓ |
| No deterministic fallback | §11 明确 "no fallback" ✓ |
| 实现切片可生成代码 | 4D1/4D2/4D3 文件列表、exact changes、validation 命令均明确 ✓ |
| Stop conditions | "requires vendor SDK or real network" 明确 ✓ |
| 测试无 live network | `httpx.MockTransport` + monkeypatch ✓ |
| CLI configured/fail-closed 路径覆盖 | 4D2 expected assertions 覆盖 ✓ |
| `pyproject.toml` 依赖 | 不新增依赖 ✓ |
| Route C scope | 不改变 final judgment/quality/golden/score/snapshot/promotion ✓ |
| Gate 2 frozen contract | §9 `_audit_user_prompt()` 需澄清（B1） |
