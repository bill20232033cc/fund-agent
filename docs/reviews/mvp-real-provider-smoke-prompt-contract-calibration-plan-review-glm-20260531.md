# Plan review: MVP real provider smoke prompt-contract calibration

日期：2026-05-31
Review target：`docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-20260531.md`
Reviewer：GLM plan review worker
Role：adversarial plan reviewer，不是 controller、implementation worker 或 code reviewer。

## Reviewed scope

- Plan artifact：`docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-20260531.md` 全文
- Truth sources：`AGENTS.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`、`docs/reviews/mvp-provider-runtime-timeout-hardening-controller-judgment-20260531.md`
- Code facts verified：`fund_agent/fund/chapter_writer.py`、`fund_agent/fund/chapter_auditor.py`、`fund_agent/services/chapter_orchestrator.py`、`fund_agent/services/llm_provider.py`、`fund_agent/ui/cli.py`

## Assumptions tested

1. Provider config/auth 已验证可用，不需要回退到 provider_config/provider_auth 门 — verified by controller judgment 和 startup packet。
2. 当前精确失败是 `llm_timeout` / `llm_contract_violation`，不是 provider auth/config — verified by controller evidence。
3. Writer/auditor 现有 fail-closed 合约不放松 — verified in code，parser 全部 blocked。
4. Taxonomy 扩展 `ChapterFailureCategory` Literal 是必要代码变更 — verified，当前 Literal 只有 `provider_runtime | prompt_contract | audit_parse | fact_gap | code_bug`。
5. Prompt 重构可以改善模型遵守率 — 未验证，属于实验性假设。

## Findings

### F1-未修复-高-llm_timeout 双重分类导致实现歧义

- **位置**: Section 7.4 Failure taxonomy + Slice D task 1
- **问题类型**: 契约缺失
- **当前写法**: Section 7.4 声明 "`llm_timeout` 是独立 top-level category，同时也属于 provider runtime family；在 smoke evidence 中优先记为 `llm_timeout`，不要只写泛化 `provider_runtime`"。Slice D task 1 说 "Add or align taxonomy Literal values with 7.4 if needed"。
- **反例/失败场景**: 当前 `ChapterFailureCategory` Literal 不含 `llm_timeout`。`_enrich_provider_diagnostic()` 在 `chapter_orchestrator.py:1060` 硬编码 `chapter_failure_category="provider_runtime"`，不区分 timeout 和其他 provider runtime 错误。`_chapter_failure_category_from_exception()` 对所有 provider runtime 异常统一返回 `"provider_runtime"`。如果 implementation agent 添加 `"llm_timeout"` 到 Literal，则必须同时修改这两处映射；如果保持 `"provider_runtime"` 作为 timeout 的 failure category，则 plan 声明的 "独立 top-level" 语义无法兑现。两种路径代码变更不同，plan 没有明确选择哪一种。
- **为什么有问题**: Plan 声明了双重分类语义但未指定代码级实现路径，implementation agent 需要自行裁决数据模型设计，违反 handoff-ready 要求。
- **直接证据**: `chapter_orchestrator.py:79-85` 定义 `ChapterFailureCategory = Literal["provider_runtime", "prompt_contract", "audit_parse", "fact_gap", "code_bug"]`，不含 `llm_timeout`。`chapter_orchestrator.py:1060` 写 `chapter_failure_category="provider_runtime"` 无条件赋值。Plan section 7.4 声明 `llm_timeout` 为独立 top-level category。
- **影响**: Implementation agent 可能选择不一致的实现路径；taxonomy 语义与代码不匹配；smoke evidence 分类口径与 plan 声明不一致。
- **建议改法和验证点**: Plan 应明确选择以下之一：(A) 将 `llm_timeout` 添加到 `ChapterFailureCategory` Literal 作为独立值，并修改 `_enrich_provider_diagnostic()` 和 `_chapter_failure_category_from_exception()` 在 timeout 时返回 `"llm_timeout"` 而非 `"provider_runtime"`；或 (B) 保持 `ChapterFailureCategory` 中 timeout 归为 `"provider_runtime"`，在 `ChapterRunStopReason` 层面已精确区分（`stop_reason="llm_timeout"` 已实现），smoke evidence 通过 stop_reason 而非 failure category 表达精确性。推荐 (A)，因为它与 plan 的 "独立 top-level" 声明一致。验证点：修改后 `_enrich_provider_diagnostic()` 对 timeout 返回 `"llm_timeout"`，对 rate_limit/malformed/network/http_error 返回 `"provider_runtime"`。
- **修复风险（低）**: 只影响 Literal 和两处映射函数，测试可精确覆盖。
- **严重程度（高）**: 如果歧义未解决，taxonomy 核心语义在代码中无法兑现。

### F2-未修复-中-CLI first_failed_category 提取路径未指定

- **位置**: Slice D task 3
- **问题类型**: 不可直接实施
- **当前写法**: Slice D task 3 说 "If a safe failure category is available, include it as `first_failed_category=<category>`"。当前 `_first_failed_chapter_summary()` 在 `cli.py:835-860` 只从 `ChapterRunResult` 读取 `chapter_id`、`status`、`stop_reason`，不读取 `chapter_failure_category`。
- **反例/失败场景**: `ChapterRunResult` dataclass 不包含 `chapter_failure_category` 字段。该信息嵌套在 `ChapterAttemptRecord.runtime_diagnostics` 的 `ChapterLLMRuntimeDiagnostic.chapter_failure_category` 中。Implementation agent 必须设计从 `runtime_diagnostics` 提取第一个非 None `chapter_failure_category` 的路径，但 plan 没有描述这条路径。
- **为什么有问题**: Plan 要求 CLI 输出一个当前数据模型不直接暴露的字段，但未说明如何从现有结构提取，implementation agent 需要自行设计遍历逻辑。
- **直接证据**: `chapter_orchestrator.py:314-337` 定义 `ChapterRunResult`，不包含 `chapter_failure_category`。`chapter_orchestrator.py:117-158` 定义 `ChapterLLMRuntimeDiagnostic`，包含 `chapter_failure_category`。`cli.py:835-860` 的 `_first_failed_chapter_summary()` 只读取 `chapter_results[].{chapter_id, status, stop_reason}`。
- **影响**: Implementation agent 可能选择不同的提取路径（从 attempts 遍历 vs 从 runtime_diagnostics 遍历 vs 给 ChapterRunResult 增加顶层字段），导致实现不一致。
- **建议改法和验证点**: Plan 应明确选择以下之一：(A) 在 `ChapterRunResult` 增加可选 `failure_category: ChapterFailureCategory | None` 字段，由 `_run_single_chapter()` / `_exception_result()` 在构造时填入；或 (B) CLI helper 遍历 `attempts[].runtime_diagnostics[].chapter_failure_category` 取第一个非 None 值。推荐 (A)，更直接且避免 CLI 耦合内部结构。验证点：`_first_failed_chapter_summary()` 输出包含 `first_failed_category=<category>` 且值来自 `ChapterRunResult.failure_category`。
- **修复风险（低）**: 数据模型增加一个可选字段，向后兼容。
- **严重程度（中）**: 不解决时 implementation agent 设计分歧，但不影响安全语义。

### F3-未修复-中-audit_rule_too_strict 触发条件需要 _chapter_failure_category_from_audit_result() 重新设计

- **位置**: Section 7.2 item 10 + Section 7.4 `audit_rule_too_strict` 行 + Slice B task 4
- **问题类型**: 契约缺失
- **当前写法**: Plan 声明 `audit_rule_too_strict` 分类条件为 "Draft 满足 programmatic safety，但 LLM auditor 可解析地提出过严或与 contract 不一致的 blocking/reviewable finding"。当前 `_chapter_failure_category_from_audit_result()` 在 `chapter_orchestrator.py:1246-1268` 的逻辑为：有 `llm:parse_failure` → `audit_parse`；`repair_hint == "needs_more_facts"` → `fact_gap`；status 为 fail/blocked → `prompt_contract`；否则 → `code_bug`。没有 `audit_rule_too_strict` 分支。
- **反例/失败场景**: Programmatic audit 通过但 LLM audit 输出可解析 BLOCKING，当前代码路径走到 `status in ("fail", "blocked")` → 返回 `"prompt_contract"`，不是 `"audit_rule_too_strict"`。Plan 声明的语义无法在现有代码路径中表达。
- **为什么有问题**: Plan 引入了新的分类语义但未指定对 `_chapter_failure_category_from_audit_result()` 的修改逻辑。Implementation agent 需要自行设计条件分支：何时判定为 `audit_rule_too_strict` 而非 `prompt_contract`。
- **直接证据**: `chapter_orchestrator.py:1246-1268` 函数不含 `audit_rule_too_strict` 分支。`ChapterFailureCategory` Literal 不含 `audit_rule_too_strict`。Plan section 7.4 定义了该 category。
- **影响**: 如果不修改该函数，`audit_rule_too_strict` 场景会被错误分类为 `prompt_contract`，taxonomy 语义失效。
- **建议改法和验证点**: Plan 应在 section 7.2 或 7.4 中明确：当 `audit_result.programmatic.status == "pass"` 且 `audit_result.llm.status in ("fail", "blocked")` 且无 `llm:parse_failure` 时，`_chapter_failure_category_from_audit_result()` 应返回 `"audit_rule_too_strict"`。需同步将 `"audit_rule_too_strict"` 添加到 `ChapterFailureCategory` Literal。验证点：programmatic pass + LLM fail with parseable issues → `audit_rule_too_strict`；programmatic fail + LLM fail → `prompt_contract`。
- **修复风险（低）**: 增加条件分支和 Literal 成员，向后兼容。
- **严重程度（中）**: 新分类语义在代码中无实现路径，但不影响现有 fail-closed 安全行为。

### F4-未修复-低-llm_empty_response 在 7.1 和 7.4 之间不一致

- **位置**: Section 7.1 Expected writer failure categories vs Section 7.4 Failure taxonomy table
- **问题类型**: 其它
- **当前写法**: Section 7.1 列出 7 个 expected writer failure categories（缺结构段落、缺 required marker、未授权 anchor、非法 marker/missing/facet、超长、incomplete、timeout），不含 `llm_empty_response`。Section 7.4 taxonomy 表格 `prompt_contract` 行的 Typical stop reasons 包含 `llm_empty_response`。
- **反例/失败场景**: Implementation agent 按 section 7.1 实现 Slice A 时可能忽略 `llm_empty_response` 的 prompt_contract 分类，但 taxonomy 要求它归入 `prompt_contract`。
- **为什么有问题**: 两个章节对同一 stop reason 的列举不一致。
- **直接证据**: Plan section 7.1 列表不含 `llm_empty_response`。Plan section 7.4 表格 `prompt_contract` 行包含 `llm_empty_response`。当前代码 `chapter_writer.py:28-44` 的 `ChapterWriteStopReason` 包含 `"llm_empty_response"`。
- **影响**: 不影响功能，但可能让 implementation agent 在 Slice A 中遗漏 `llm_empty_response` 的 prompt 分类测试。
- **建议改法和验证点**: 在 section 7.1 的 Expected writer failure categories 列表中添加："- 空 response：`llm_empty_response`，chapter failure category `prompt_contract`。"
- **修复风险（低）**: 文档一致性问题。
- **严重程度（低）**: 不影响安全语义或功能正确性。

## Open questions

1. Plan 是否选择 F1 建议的方案 (A)（`llm_timeout` 作为独立 `ChapterFailureCategory` 成员）？这决定了 Slice D 的核心代码变更路径。
2. Plan 对 `audit_rule_too_strict` 的判定是否要求 implementation agent 自行判断"与 contract 不一致"的具体条件？还是只要 programmatic pass + LLM fail/blocked with parseable output 就归为 `audit_rule_too_strict`？

## Residual risks

| Risk | Tracking destination |
|---|---|
| Prompt 重构后真实模型仍频繁 `llm_contract_violation` | Writer prompt contract calibration follow-up（plan section 13 已记录） |
| `llm_timeout` 由 prompt 过长导致，而非 provider budget 不足 | Provider runtime budget tuning gate / prompt length reduction（plan section 7.3 item 6 已 defer） |
| Auditor line protocol parse failure 反复出现 | Auditor protocol calibration follow-up（plan section 13 已记录） |
| 完整 0-7 章通过但质量未达 promotion-ready | Future score-loop / golden promotion gate（plan section 13 已记录） |

## Special review lenses applied

- **Architecture boundary review**: Plan 只修改 Fund 层 writer/auditor 和 Service 层 orchestrator/provider/CLI，不触碰 UI 渲染、Host、Agent、dayu 或 golden/fixtures。Allowed files 列表与模块边界一致。PASS。
- **Best-practice review**: Fail-closed 合约保持不变；bounded repair；no deterministic fallback；secret-safe diagnostics。这些符合当前 gate 的安全要求。PASS。
- **Optimal-solution review**: Prompt 重构是当前最小成本尝试；如果不生效，residual risk owner 捕获了后续入口。Taxonomy 扩展对齐了 controller judgment 的精确分类要求。PASS with F1 concern。
- **Overengineering review**: Plan 不引入 streaming、并发、multi-model split、provider fallback 或 Evidence Confirm。Taxonomy 7 类目为最小必要集合。PASS。
- **Overcoupling review**: Slice 之间依赖关系合理（A/B → C → D → E），但 plan 没有显式声明。每个 slice 的文件边界清晰，不跨层穿透。PASS。

## Final conclusion

**pass-with-risks**

Plan 整体 handoff-ready，goal/motivation/non-goals/allowed-files/validation-matrix/completion-format 完整且与控制面一致。Fail-closed 安全边界未被放松。4 个 findings 中无严重级别 blocking issue。

F1（`llm_timeout` 双重分类歧义）是最强 finding：plan 声明了 taxonomy 语义但未指定代码级数据模型变更路径，implementation agent 必须在 `_enrich_provider_diagnostic()` 和 `_chapter_failure_category_from_exception()` 之间做选择。建议 controller 在 handoff 前确认方案 (A)，或接受 implementation agent 在 Slice D 中自行裁决。

F2 和 F3 是中等级别的实现细节欠规格问题，不阻塞 handoff 但可能影响实现一致性。

F4 是低级别文档一致性问题。

若 F1 在 implementation 前由 controller 或 plan 更新确认了实现路径，本 review 可视为 pass。
