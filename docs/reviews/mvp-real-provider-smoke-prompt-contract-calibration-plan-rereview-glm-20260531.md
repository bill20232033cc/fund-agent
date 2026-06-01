# Plan re-review: MVP real provider smoke prompt-contract calibration

日期：2026-05-31
Review target：`docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-20260531.md`（修正后）
Plan fix artifact：`docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-fix-20260531.md`
Prior review：`docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-review-glm-20260531.md`
Reviewer：GLM plan review worker
Role：targeted re-review，只复核 F1-F4。

## Finding disposition

### F1-已修复-高-llm_timeout 双重分类

Prior finding：Plan 声明 `llm_timeout` 为独立 top-level category 但未指定代码级 `ChapterFailureCategory` Literal 扩展路径和映射函数修改。

Fix verification：

- Plan section 7.4 新增 "Required code-level decision" 段落，明确 "选择方案 A：把 `llm_timeout` 添加为独立 `ChapterFailureCategory` 成员"。
- 明确 timeout provider diagnostics / exception category 必须返回 `llm_timeout`，rate_limit / malformed / network / http_error 仍归 `provider_runtime`。
- Section 7.3 item 6 更新为 "`llm_timeout` 必须归为独立 `llm_timeout` failure category"。
- Section 7.1 expected categories 新增 "provider timeout exception：`llm_timeout`，chapter failure category `llm_timeout`"。
- Classification rules 明确 "代码级 `ChapterFailureCategory`、runtime diagnostics、`ChapterRunResult.failure_category`、CLI safe summary 和 smoke evidence 都必须优先记为 `llm_timeout`"。

结论：**已修复**。方案 A 已明确选择，`_enrich_provider_diagnostic()` 和 `_chapter_failure_category_from_exception()` 的修改路径可从 plan 直接推导。

### F2-已修复-中-CLI first_failed_category 提取路径

Prior finding：`ChapterRunResult` 不暴露 `chapter_failure_category`，CLI 提取路径未指定。

Fix verification：

- Plan section 7.4 明确 "选择方案 A：在 `ChapterRunResult` 增加可选 `failure_category: ChapterFailureCategory | None` 字段，由 writer blocked、audit blocked/failed、exception result construction、repair budget exhausted/result construction 等路径填入"。
- 明确 "CLI `first_failed_category` 只能从 `ChapterRunResult.failure_category` 读取，不得遍历 attempts、runtime_diagnostics 或 provider diagnostics 内部结构"。
- 明确 "CLI stdout 必须保持 empty/no fallback；category 只允许进入 stderr safe summary"。

结论：**已修复**。数据模型变更、填入路径、CLI 读取路径和输出位置全部明确。

### F3-已修复-中-audit_rule_too_strict 触发条件

Prior finding：`audit_rule_too_strict` 分类语义已声明但 `_chapter_failure_category_from_audit_result()` 修改逻辑未指定。

Fix verification：

- Plan section 7.4 明确 "新增 Literal 值至少包含 `llm_timeout` 和 `audit_rule_too_strict`"。
- Classification rules 明确四条件 AND："programmatic audit accepted/pass；LLM audit 是可解析的 fail/blocked/reviewable issue；不存在 `llm:parse_failure`；不存在 `needs_more_facts` repair hint 或 fact-gap 类 issue"。
- 明确 "programmatic fail 仍按 `prompt_contract` 或 `fact_gap` 分类，不得被 LLM audit 覆盖"。

结论：**已修复**。触发条件精确到四个 AND 条件，`_chapter_failure_category_from_audit_result()` 的分支逻辑可从 plan 直接推导。

### F4-已修复-低-llm_empty_response 列举不一致

Prior finding：Section 7.1 expected categories 不含 `llm_empty_response`，section 7.4 taxonomy 包含。

Fix verification：

- Plan section 7.1 expected writer failure categories 新增 "空响应：`llm_empty_response`，chapter failure category `prompt_contract`"。

结论：**已修复**。

## Final conclusion

**PASS**

F1-F4 全部已修复。Plan fix artifact 准确记录了 controller finding decisions，修正已回写到 plan 原文。Implementation worker 可按修正后的 plan 直接执行，无需自行裁决数据模型设计或分类逻辑。
