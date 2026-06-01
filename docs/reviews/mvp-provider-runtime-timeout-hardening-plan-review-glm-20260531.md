# MVP provider runtime timeout hardening plan review (GLM)

日期：2026-05-31

角色：AgentGLM independent plan reviewer，非 controller，非 implementation worker。

Reviewed target：`docs/reviews/mvp-provider-runtime-timeout-hardening-plan-20260531.md`

Reviewed scope：plan 是否 code-generation-ready、bounded retry 是否有界、typed env 是否最小兼容、runtime diagnostics 是否安全有用、非 timeout 分类是否不被 retry、golden/fixtures/score/dayu/Host/Agent 是否未被触及、scope 是否过宽。

## assumptions tested

1. Plan 声称 `LLMProviderConfig` 已有 typed env — 代码事实确认：`fund_agent/config/llm.py:36-56` `LLMProviderConfig` 已有 `timeout_seconds`、`max_output_chars` 等字段，新增字段可复用同一 pattern。✅
2. Plan 声称 `_complete()` 对 `httpx.TimeoutException` 无 retry — 代码事实确认：`fund_agent/services/llm_provider.py:186-187` 直接 raise `LLMProviderTimeoutError`，无 retry loop。✅
3. Plan 声称 `max_repair_attempts` 只控制 audit-driven regenerate — 代码事实确认：`fund_agent/services/chapter_orchestrator.py:676-783` while loop 由 `_decide_repair()` decision 的 `action=="regenerate"` 驱动，`attempt_index` 不受 provider retry 影响。✅
4. Plan 声称 `_exception_result()` 已映射 `LLMProviderTimeoutError -> llm_timeout` — 代码事实确认：`chapter_orchestrator.py:834-835`。✅
5. Plan 声称 `ChapterLLMRequest` 有 `chapter_id`/`fund_code`/`report_year` — 代码事实确认：`chapter_writer.py:115-118`。✅
6. Plan 声称 `ChapterAuditLLMRequest` 有 `chapter_id`/`fund_code`/`report_year` — 代码事实确认：`chapter_auditor.py:155-157`。✅
7. Plan 声称 default deterministic analyze 不读 LLM config — 代码事实确认：`cli.py:243-253`，`use_llm=False` 时走 `FundAnalysisService().analyze(request)` 不触碰 LLM path。✅
8. Plan 声称 bounded formula 为 `<= (max_repair_attempts + 1) * 2 * timeout_max_attempts` — 公式验证：每 orchestration attempt 最多 2 次 provider call（writer + auditor），每次最多 `timeout_max_attempts` HTTP attempt，orchestration attempt 总数为 `max_repair_attempts + 1`。默认 `(1+1)*2*2=8`。✅ 有界。

## findings

### F1-未修复-中-diagnostic propagation 在 Protocol response 边界无明确解析机制

- **位置**: Plan "Runtime diagnostic contract" 放置位置优先级 + Slice B "成功响应返回 diagnostic" + Slice C "write_chapter() 成功/blocked 时保留 provider response diagnostics"
- **问题类型**: 架构边界 / 契约缺失
- **当前写法**: Plan 给出两个 placement priority：1) 定义在 `chapter_writer.py`，auditor 复用；2) 若不需要 Fund primitive 携带成功诊断，则定义在 `chapter_orchestrator.py`。Slice B 说 `_complete()` 成功时返回 diagnostic，但未说明 diagnostic 如何穿越 Protocol return type 到达 orchestrator。
- **反例/失败场景**: `OpenAICompatibleChapterLLMClient.generate_chapter()` 返回 `ChapterLLMResponse`（`chapter_writer.py:145-158`），该类型只有 `text`/`model_name`/`finish_reason`，无 diagnostics 字段。同理 `ChapterAuditLLMResponse`（`chapter_auditor.py:167-180`）只有 `raw_text`/`model_name`/`finish_reason`。Provider 成功调用产生的 diagnostic 无法通过现有 Protocol return type 传递给 `write_chapter()` 或 orchestrator。Implementation worker 必须在 Slice B/C 之间自行设计这个 propagation 机制。
- **为什么有问题**: 两个 placement option 实际隐含不同的实现路径。Option 1 需要给 `ChapterLLMResponse` 和 `ChapterAuditLLMResponse` 新增 optional diagnostics 字段（改变 Protocol response 契约，但加 optional 默认值可 backward-compatible）。Option 2 下 orchestrator 无法从 Protocol return 获取成功诊断，只能从异常获取失败诊断，成功 diagnostic 只能退化为从 response 元数据（model_name/finish_reason）在 orchestrator 层重建。Plan 未做二选一决定，implementation worker 需要自行做架构决策。
- **直接证据**:
  - `ChapterLLMResponse` 字段：`chapter_writer.py:145-158` — 无 diagnostics
  - `ChapterAuditLLMResponse` 字段：`chapter_auditor.py:167-180` — 无 diagnostics
  - `ChapterLLMClient` Protocol：`chapter_writer.py:161-178` — 只定义 `generate_chapter()` 返回 `ChapterLLMResponse`
  - `ChapterAuditLLMClient` Protocol：`chapter_auditor.py:183-197` — 只定义 `audit_chapter()` 返回 `ChapterAuditLLMResponse`
  - Plan 优先级文本未做最终选择
- **影响**: Implementation worker 在 Slice B/C 交界处需自行设计 propagation 机制，可能导致 Slice C 重写或返工。
- **建议改法和验证点**: Plan 应显式选择 Option 1（推荐）：在 `ChapterLLMResponse` 和 `ChapterAuditLLMResponse` 各新增 `runtime_diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...] = ()` optional 字段。这样 `generate_chapter()` / `audit_chapter()` 实现可从 `_complete()` 拿到 diagnostics 并填入 response，`write_chapter()` / `audit_chapter()` 透传，orchestrator 从 `ChapterWriteResult` / `ChapterAuditResult` 提取。验证点：response schema version 不变（新增 optional 字段），test mock 不受影响（默认空 tuple）。
- **修复风险**: 低。新增 optional field 不改变现有行为。
- **严重程度**: 中。不阻塞 Slice A/B 但会导致 Slice C implementation worker 做架构决策。

### F2-未修复-低-repair_attempt_index 在 audit 路径不可用

- **位置**: Plan "Runtime diagnostic contract" `repair_attempt_index` 字段说明 + Slice B "`_complete()` 接收 operation/chapter identity"
- **问题类型**: 契约缺失
- **当前写法**: Plan 说 `repair_attempt_index` 为 "writer repair attempt；audit 无法确认时使用当前 orchestration attempt index"。Plan 还说 `_complete()` 应从 `generate_chapter()` / `audit_chapter()` 接收此参数。
- **反例/失败场景**: `ChapterAuditLLMRequest`（`chapter_auditor.py:138-163`）没有 `repair_context` 字段，因此 provider 的 `audit_chapter()` 无法确定 `repair_attempt_index`。Provider 层也无法获取 "当前 orchestration attempt index"——这个信息只在 `chapter_orchestrator.py:676` 的 while loop 的 `attempt_index` 变量中。
- **为什么有问题**: Implementation worker 需要决定 audit 路径的 `repair_attempt_index` 取值：固定为 0？从 orchestrator 传入？这又回到 Protocol 是否扩展的问题。
- **直接证据**: `ChapterAuditLLMRequest` 字段列表：`chapter_auditor.py:154-163`，无 `repair_context`。Orchestrator 的 `attempt_index` 是局部变量：`chapter_orchestrator.py:675`。
- **影响**: 低。Diagnostic 的 `repair_attempt_index` 对 audit 路径可安全设为 `None` 或 `0`，不影响 bounded retry 或 fail-closed 行为。
- **建议改法和验证点**: Plan 显式说明：audit 路径 `repair_attempt_index` 使用 `None`。后续若 orchestrator 从 `ChapterAttemptRecord.attempt_index` 填充，可在 Slice C 聚合时覆盖。
- **修复风险**: 低
- **严重程度**: 低

### F3-未修复-低-完整 error taxonomy 混合 provider 层和 domain 层分类

- **位置**: Plan "Runtime diagnostic contract" `category` 字段枚举 + "Error taxonomy mapping" 表
- **问题类型**: 过度设计 / 架构边界
- **当前写法**: `ChapterLLMRuntimeDiagnostic.category` 包含 10 个值：`success`/`timeout`/`rate_limit`/`malformed`/`network`/`http_error`/`prompt_contract`/`audit_parse`/`fact_gap`/`code_bug`。前 6 个是 provider 层 runtime 分类，后 4 个是 writer/auditor/orchestrator 的 domain 分类。
- **反例/失败场景**: Provider 的 `_complete()` 只会产生 `success`/`timeout`/`rate_limit`/`malformed`/`network`/`http_error`。`prompt_contract`/`audit_parse`/`fact_gap`/`code_bug` 只会在 Slice C 由 orchestrator 从 writer/auditor result 推导。将两类分类放在同一个 enum 里，使 provider 层的 diagnostic type 依赖了 domain 层概念。
- **为什么有问题**: 当前 blocker 只是 `llm_timeout`。完整 taxonomy 有用但把两层分类合并到一个类型里违反了 plan 自己的 layering 目标（provider retry 是 transport hardening，domain 分类是 orchestration concern）。如果未来 domain 分类扩展，provider 层的 diagnostic type 需要同步修改。
- **直接证据**: Provider `_complete()` 只处理 HTTP 级别异常：`llm_provider.py:186-202`。Domain 分类来自 writer stop reasons 和 audit issues：`chapter_orchestrator.py:78-96`、`chapter_auditor.py:26-38`。
- **影响**: 设计耦合但不影响正确性或安全性。可在 Slice C 用两个独立类型或 union 解决。
- **建议改法和验证点**: 考虑将 diagnostic `category` 拆为两个层次：`provider_runtime_category`（provider 层填写）和 `chapter_category`（orchestrator 层聚合时填写）。或保持当前设计但在 plan 中显式承认这是一个 tradeoff，后续可演进。不阻塞。
- **修复风险**: 低
- **严重程度**: 低

### F4-未修复-低-Slice D CLI diagnostic surface 需要深层结果遍历

- **位置**: Plan Slice D "`_llm_incomplete_message()` may append safe classification summary"
- **问题类型**: 切片过粗
- **当前写法**: 当前 `_llm_incomplete_message()`（`cli.py:807-829`）只读取 `result.final_assembly_result.status/issues` 和 `result.llm_orchestration_result.status`。Plan 说可能追加 "first failed chapter id/status/stop_reason" 和 "safe runtime diagnostic categories and provider attempt counts"。
- **反例/失败场景**: 要获取 first failed chapter 的 stop_reason 和 diagnostics，CLI 需要遍历 `result.llm_orchestration_result.chapter_results` → 找 `status != "accepted"` 的第一个 → 读取其 `stop_reason` → 再从 `attempts` 读取 diagnostics。当前 `_llm_incomplete_message()` 不做这个遍历。Implementation worker 需要理解 `ChapterOrchestrationResult` → `ChapterRunResult` → `ChapterAttemptRecord` 三层结构。
- **为什么有问题**: Slice D 说 "may append"，给 implementation worker 留了裁量空间。但 "may" 不够 code-generation-ready。如果 implementation worker 选择不 append，Slice D completion signal 的 "timeout failure stderr includes `llm_timeout` or `timeout` classification and attempt count" 就无法满足。
- **直接证据**: `_llm_incomplete_message()`：`cli.py:807-829`。`ChapterOrchestrationResult` 结构：`chapter_orchestrator.py:276-301`。
- **建议改法和验证点**: Plan 将 "may append" 改为 "must append"，并给出具体遍历路径：遍历 `result.llm_orchestration_result.chapter_results`，取第一个 `status != "accepted"` 的 `ChapterRunResult`，输出 `chapter_id`/`status`/`stop_reason`。Runtime diagnostics 暂不在 CLI stderr 输出（保留在 diagnostic JSON 中）。验证点：timeout 失败时 stderr 含 `llm_timeout`。
- **修复风险**: 低
- **严重程度**: 低

## open questions

无未收敛 open question。以上 finding 均有建议改法。

## residual risks and suggested tracking

1. **Provider 真实延迟可能持续超过 timeout_seconds * timeout_max_attempts + backoff**: Plan 在 residual risks 中已承认。Bounded retry 减少偶发 timeout 但不保证所有 provider 请求成功。建议跟踪在后续 real provider validation gate 中。Plan 已覆盖。
2. **成功 retry 后仍可能遇到 prompt_contract / audit_parse 失败**: Plan 在 residual risks 中已承认。建议跟踪在后续 prompt_contract / audit_parse gate 中。Plan 已覆盖。
3. **429 retry 未在本 gate 覆盖**: Plan 在 non-goals 和 residual risks 中已排除。建议跟踪在后续 rate-limit policy gate 中。Plan 已覆盖。

## conclusion

`pass-with-risks`

Plan 目标明确、bounded retry 设计正确有界、typed env config 最小兼容、non-goals 和 hard constraints 边界清晰、secret hygiene 计划充分、validation matrix 完整。主要风险是 F1：diagnostic propagation 在 Protocol response 边界的 mechanism 未做最终选择，implementation worker 在 Slice B/C 交界处需做架构决策。建议 controller 裁决 F1 是否需要在 plan 中显式 resolve，还是授权 implementation worker 在 Slice C 内自行选择。F2/F3/F4 为低严重度 non-blocking finding，不阻止 implementation。

## reviewer self-check

- reviewed target、scope、source of truth 和 assumptions tested：已写清。✅
- findings 是否 evidence-based、adversarial、可执行，无 style/nit/speculation：4 个 finding 均有直接代码证据和具体改法。✅
- open questions、residual risks、tracking destination 与 findings 分开：已分开。✅
- conclusion 只能是 pass / pass-with-risks / fail：`pass-with-risks`。✅
- output path 使用本机系统时钟生成 timestamp：`20260531-023601`。✅
- 未修改 plan、未实施 fix、未 commit/push/PR。✅
