# MVP typed diagnostic serialization repair code review (DS)

## Reviewer Self-Check

- Role: AgentDS, independent code reviewer (not controller).
- Gate: `MVP typed diagnostic serialization repair implementation gate`.
- Classification: heavy.
- Scope: code review only; no code changes, no live provider, no staging/commit/push.
- Inputs reviewed: git diff, all 6 changed files, implementation evidence, controller judgment, design/plan, AGENTS.md.

## Verdict

**PASS — no blocking findings.**

## Findings

### F1 (minor) — `_safe_status_code` 在两个模块中重复定义

`fund_agent/services/chapter_orchestrator.py:3086` 和 `fund_agent/services/llm_run_artifacts.py:834` 各自定义了完全相同的 `_safe_status_code()` 函数。

**Why not blocking:** 两处逻辑相同（均为 4 行），两个模块不应互相依赖（`llm_run_artifacts` 已依赖 `chapter_orchestrator` 的类型，但 `chapter_orchestrator` 不应反向依赖 artifact writer）。这是整个 `_runtime_diagnostic_payload` 也重复定义的同一模式，属于现有设计选择而非本次引入的回归。

**Residual risk:** 如果将来 `status_code` 过滤规则变化，需要同时更新两处。建议在后续重构中考虑提取为共享工具函数。

### F2 (minor) — `_RUNTIME_STOP_REASON_CATEGORY` 映射表缺少 `llm_exception`

`chapter_orchestrator.py:178` 的 `_RUNTIME_STOP_REASON_CATEGORY` 包含 4 个映射，但 `_RUNTIME_TERMINAL_STOP_REASONS` frozenset 包含 5 个值（多了 `llm_exception`）。

**Why not blocking:** 代码正确处理了 `expected_category is None` 的分支（`_terminal_runtime_diagnostic:2873`、`_diagnostic_matches_terminal:2940`、`_diagnostic_consistency_status:2970`）。`llm_exception` 是兜底分类，匹配逻辑退化为"任何有 `provider_runtime_category` 的 diagnostic"，语义合理。

**Residual risk:** 读者可能误以为映射表不完整是遗漏。建议加一行注释说明 `llm_exception` 无特定 category 映射是有意设计。

### F3 (minor) — attempt 级 consistency payload 的语义需要读者理解上下文

当章节因 `llm_timeout` 失败，且 timeout 诊断仅存在于章节级（例如 writer repair timeout 发生在创建新 attempt record 之前），所有 attempt 的 `diagnostic_consistency_status` 均为 `"missing_terminal_runtime_diagnostic"`。从 attempt 自身角度看这是准确的——attempt 自己的 `runtime_diagnostics` 中确实没有 terminal diagnostic。

**Why not blocking:** Implementation evidence 已明确文档化此设计。章节级 `runtime_diagnostic_consistency_payload` 和 summary `first_failed` 提供了完整信息。attempt 级语义与章节级互补而非矛盾。

**Residual risk:** 不熟悉此设计的读者可能误以为"attempt 级 `missing_terminal_runtime_diagnostic` = 数据丢失"，需要查阅 implementation evidence 或代码注释。建议在 `attempt_runtime_diagnostic_consistency_payload` docstring 中增加一句说明。

### F4 (observation) — fake client 行为顺序变更是安全的

`_FakeChapterLLMClient.call()` 和 `_FakeAuditLLMClient.call()` 的异常抛出优先级从 `exception > raises > texts/raw_responses` 变为 `raises > texts/raw_responses > exception`。

**确认安全:** 所有已有 `exception=` 用法（6 处 writer、0 处 auditor）均不同时传入 `texts`/`raw_responses`，行为不变。新顺序使 multi-call 测试场景（先返回正常响应、再抛出 timeout）成为可能。全部 1292 测试通过。

**Residual risk:** 将来若有人同时传入 texts 和 exception，行为会与旧代码不同。这是测试辅助代码，不影响生产路径。

## Review Matrix

| Focus Area | Finding |
|---|---|
| correctness: terminal diagnostics not shadowed | PASS — `_exception_result()` 的 `attached_to_attempt` 标志正确区分"已挂载到 attempt"与"无对应 attempt record"两种场景。`_representative_runtime_diagnostics()` 在 terminal runtime failure 时过滤不匹配的 prior audit rows。 |
| correctness: first-failed representative selection | PASS — `_terminal_runtime_diagnostic()` 按 `stop_reason` 精确匹配 terminal diagnostic；`_diagnostic_matches_terminal()` 进一步按 `operation`、`repair_attempt_index`、`provider_runtime_category` 过滤。`llm_timeout` 特殊处理：`_is_timeout_runtime_diagnostic()` 接受 `provider_runtime_category="timeout"` 或 `timeout_budget_kind is not None`。 |
| no behavior change: chapter acceptance | PASS — `_exception_result()` 的 `stop_reason`、`failure_category`、`issues` 字段不变。`ChapterRunResult.status` 仍为 `"failed"`。accepted 路径（`_WRITER_STOP_REASON_MAPPING`、`_decide_repair`、`_final_assembly`）未修改。 |
| no behavior change: auditor rules | PASS — 审计规则码、`_audit_prompt_contract_diagnostic`、`_chapter_failure_category_from_audit_result` 未修改。 |
| no behavior change: prompt/draft/raw | PASS — prompt 合约、writer draft、raw provider/audit response 字段未新增、未变更。 |
| no behavior change: timeout defaults | PASS — `MAX_REPAIR_ATTEMPTS`、`_WRITER_STOP_REASON_MAPPING` 等常量未修改。 |
| no behavior change: deterministic paths | PASS — 确定性 CLI 路径（非 `--use-llm`）不经过 `chapter_orchestrator` 的 LLM 路径。 |
| no behavior change: final assembly | PASS — `FinalChapterAssemblyResult` 结构和组装逻辑未修改。 |
| no behavior change: fail-closed | PASS — 阻塞/失败状态语义不变。新增字段仅观测性增强，不改变决策逻辑。 |
| artifact schema safety: new fields scalar only | PASS — 7 个新字段全部为 allowlisted scalar（`str`、`bool`、`int | None`、`str | None`）。`DiagnosticConsistencyStatus` 为 4 值 Literal。 |
| artifact schema safety: no secret leak | PASS — `terminal_issue_class` 仅输出异常类名或安全 issue prefix。`_first_safe_issue_prefix()` 过滤到 ASCII alphanum + `_:-` 且限制在 `writer:/programmatic:/llm:/audit:` 前缀。验证：测试断言 `"secret-model" not in str(payload)` 和 `"provider body" not in str(payload)` 均通过。 |
| artifact schema safety: status_code handling | PASS — `_safe_status_code()` 限制为 `100..599` 标准 HTTP 状态码；`isinstance(status_code, bool)` 显式排除 `bool`（`bool` 是 `int` 子类）；非标准值序列化为 `null`。测试验证：`status_code=2000` → `None`，`status_code=504` → `504`，`status_code=900` → `None`。 |
| artifact schema safety: request_id handling | PASS — `request_id` 作为 opaque string 透传，不用于归因。Implementation evidence 明确标注"removable if future provider format embeds account/model/region data"。 |
| attempt-level lineage semantics | PASS — `attempt_runtime_diagnostic_consistency_payload()` 使用 attempt 自身 `runtime_diagnostics` 计算 consistency。章节级和 attempt 级各司其职（见 F3）。 |
| path truth fix | PASS — `DEFAULT_LLM_RUN_ARTIFACT_ROOT` 移到 `paths.py` 作为唯一真源。`llm_run_artifacts.py` 通过 `from fund_agent.config.paths import ...` 导入并重导出为同名 public alias。无 import cycle（`paths.py` 无任何 `fund_agent.*` import）。`config/README.md` 同步更新。 |
| tests: shadow prevention | PASS — `test_repair_timeout_terminal_diagnostic_is_not_shadowed_by_prior_audit_row` 验证 terminal timeout diagnostic 不被 prior audit row 遮蔽。 |
| tests: chapter-level retention | PASS — `test_writer_repair_timeout_terminal_diagnostic_uses_chapter_level_row` 验证无 attempt record 时章节级 terminal row 保留。 |
| tests: missing diagnostic handling | PASS — `test_timeout_terminal_without_matching_runtime_row_marks_missing` 验证缺失 timeout row 时正确报告 `missing_terminal_runtime_diagnostic` 且不伪造 timeout scalar。 |
| tests: retained artifact lineage | PASS — `test_artifact_records_terminal_runtime_lineage_at_chapter_and_attempt_levels` 验证章节级和 attempt 级 terminal lineage 写入 retained artifact。 |
| tests: status_code safety | PASS — 以上测试中 coverage：非标准 2000/900 → null，标准 504 → 504。 |
| tests: prompt_cost_diagnostic exclusion | PASS — `test_artifact_records_terminal_runtime_lineage` 断言 `"prompt_cost_diagnostic" not in diagnostics[0]`。 |
| tests: secret safety | PASS — 所有新测试均含 `"secret-model" not in str(payload)` / `"provider body" not in str(payload)` 断言。 |
| validation credibility | PASS — 82 个服务测试、1292 全量 pytest、ruff check、py_compile、git diff --check 全部通过。 |

## Prompt-Cost Diagnostic Check

确认 `prompt_cost_diagnostic` 处理符合 controller judgment 要求：

- `chapter_orchestrator.py` 的 `_runtime_diagnostic_payload()` 继续通过 `_prompt_cost_diagnostic_payload()` 序列化 prompt-cost 子字段。此函数为既有实现，未在本次改动中变更。
- `llm_run_artifacts.py` 的 `_runtime_diagnostic_payload()` **不**序列化 `prompt_cost_diagnostic`。此行为为既有实现，未在本次改动中变更。
- 新 terminal lineage 字段不包含任何 prompt-cost 数据。
- 测试显式断言 `"prompt_cost_diagnostic" not in diagnostics[0]`。

结论：`prompt_cost_diagnostic` 的现有安全 allowlist 未被本次改动破坏。

## Adversarial Failure Pass

| Scenario | Disposition |
|---|---|
| 两次不同 stop_reason 的 exception 先后发生 | `_terminal_runtime_diagnostic()` 只看 `result.stop_reason`（终态），只匹配最终失败原因。中间状态的 diagnostic 会被 `_representative_runtime_diagnostics()` 过滤。 |
| `operation` 相同但 `repair_attempt_index` 不同的多个 diagnostic 都存在 | `_diagnostic_matches_terminal()` 要求 `repair_attempt_index` 精确匹配，只选取 terminal attempt 的 diagnostic。 |
| 非 runtime terminal（如 `prompt_contract`）与 provider runtime diagnostic 共存 | `_diagnostic_consistency_status()` 返回 `"non_runtime_terminal_without_scalar"`，清晰区分。 |
| `terminal_diagnostic` 存在但 `expected_category` 不匹配 | 返回 `"terminal_category_conflict"`，不会静默接受。 |
| `status_code` 为 `bool(True)` | `isinstance(status_code, bool)` 显式排除，返回 `None`。 |
| `request_id` 未来嵌入敏感信息 | 当前 opaque 透传；implementation evidence 标记为 removable。 |
| fake client 同时设置 texts 和 exception | 当前无此用法。将来若出现，texts 耗尽后才会 raise exception。行为已由新测试代码隐式文档化。 |

## Residual Risks

1. **`_safe_status_code` 重复定义**（见 F1）——两个模块各自维护相同逻辑。
2. **`_RUNTIME_STOP_REASON_CATEGORY` 文档缺口**（见 F2）——缺少 `llm_exception` 映射可能让读者困惑。
3. **attempt 级 consistency 语义需要上下文**（见 F3）——不熟悉设计的读者可能误读。
4. **CLI 输出未新增回归测试**——DS plan review 建议的 CLI first-failed 回归未新增专门测试。已有 CLI 测试（`llm and incomplete` 4 个、`llm and timeout` 3 个）均通过。`serialize_chapter_runtime_diagnostics()` 的被调用方（CLI 和 artifact writer）共享同一序列化函数，行为一致性由服务层测试覆盖。
5. **`_first_safe_issue_prefix` fallback 路径**——非 provider exception 的 failure 场景下能正确匹配（`writer:`/`programmatic:`/`llm:`/`audit:` 前缀），但 provider exception 的 issue 格式不匹配这些前缀，导致 fallback 返回 `None`。`_terminal_issue_class()` 在 fallback 之前的主路径（runtime terminal + exception name matching）已覆盖 provider exception，无功能影响。

## Secret Safety Confirmation

本 review 确认以下内容未被新增字段泄露：API key、Authorization header、Bearer token、cookie、password、provider base URL、model 名称/值、prompt body、draft body、raw provider response、raw audit response、report body、raw PDF text、raw parsed annual-report text。
