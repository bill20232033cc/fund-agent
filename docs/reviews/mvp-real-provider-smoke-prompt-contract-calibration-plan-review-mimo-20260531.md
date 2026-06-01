# MVP real provider smoke prompt-contract calibration plan review — MiMo

日期：2026-05-31

角色：plan review worker。不改代码、不 commit、不 push、不 PR。

## Review target

`docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-20260531.md`

## Truth sources read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-provider-runtime-timeout-hardening-controller-judgment-20260531.md`
- `fund_agent/fund/chapter_writer.py`（当前代码事实）
- `fund_agent/fund/chapter_auditor.py`（当前代码事实）
- `fund_agent/services/chapter_orchestrator.py`（当前代码事实）
- `tests/fund/test_chapter_writer.py`（当前测试结构）
- `tests/fund/test_chapter_auditor.py`（当前测试结构）

## Review criteria checklist

| Criterion | Verdict | Notes |
|---|---|---|
| handoff-ready / code-generation-ready | PASS | 5 个切片定义清晰，文件范围、任务、预期测试和验证矩阵完整 |
| 聚焦 provider config/auth 已通过后的 writer/auditor contract calibration | PASS | Section 4 明确引用 provider auth 已通过证据；Section 5 明确不回退 provider config/auth |
| 覆盖 writer marker/anchor/missing/non_asserted facets/length | PASS | Section 7.1 覆盖所有维度：固定结构段落、required marker、anchor marker、missing marker、candidate facet 断言禁止、长度防护 |
| auditor line protocol parse failure fail-closed | PASS | Section 7.2 item 7 明确空响应、前缀文本、非三段格式、allowlist 外 severity、空 location/message 均为 parse failure blocked |
| repair/regenerate bounded and previous failure reason | PASS | Section 7.3 item 1-3：max_repair_attempts 固定 1、每章最大 writer attempts = 2、regenerate 带上一轮 issue ids/messages/required_corrections |
| taxonomy 包含 prompt_contract/audit_parse/llm_timeout/fact_gap/audit_rule_too_strict/code_bug/provider_runtime | PASS with one non-blocking note | 见 Finding F1 |
| smoke evidence 脱敏 | PASS | Section 7.5 完整列出 allowed/forbidden evidence；禁止 API key、Authorization header、full prompt/draft/response |
| 验证矩阵完整 | PASS | Section 10 覆盖 ruff、targeted pytest、full coverage、deterministic analyze/checklist、missing-config smoke、real provider smoke、secret leak scan |
| 硬约束不触碰 golden/fixtures/score/quality gate、Host/Agent/dayu、PR 状态 | PASS | Section 5 non-goals 完整列举所有禁止项 |
| 不放松 evidence/ITEM_RULE/candidate facet/交易建议/E2 deferred | PASS | Section 5 item 12-13 明确不放松 |
| 默认 deterministic analyze/checklist 不变 | PASS | Section 5 item 1 明确 |

## Findings

### F1 — Non-blocking: `audit_rule_too_strict` 引用缺失条件（Section 7.2 item 10）

**Severity**: non-blocking

**Location**: Section 7.2 item 10

**Description**: Plan states "分类为 `audit_rule_too_strict` 只在满足本文 7.5 的条件时允许"，但 Section 7.5 是 Smoke evidence policy，不包含 `audit_rule_too_strict` 的具体触发条件。应引用 Section 7.4 taxonomy 表中 `audit_rule_too_strict` 的定义："Draft 满足 programmatic safety，但 LLM auditor 可解析地提出过严或与 contract 不一致的 blocking/reviewable finding"。

**Impact**: 不阻塞 implementation。当前代码 `_chapter_failure_category_from_audit_result()` 已将可解析 audit fail/blocked 映射为 `prompt_contract`。Plan 的 taxonomy 是概念框架，implementation worker 可按现有映射继续，或在 evidence 中使用 `audit_rule_too_strict` 作为更精确的 evidence-level 分类。

**Fix suggestion**: Section 7.2 item 10 改为引用 Section 7.4 taxonomy 定义，或明确 `audit_rule_too_strict` 暂作为 evidence/reporting 级分类，不强制要求新增 `ChapterFailureCategory` Literal。

### F2 — Non-blocking: taxonomy 与当前代码 `ChapterFailureCategory` Literal 的关系未显式说明（Section 7.4）

**Severity**: non-blocking

**Location**: Section 7.4

**Description**: Plan taxonomy 包含 7 个 category（`prompt_contract`、`audit_parse`、`llm_timeout`、`fact_gap`、`audit_rule_too_strict`、`code_bug`、`provider_runtime`）。当前 `ChapterFailureCategory` Literal 只有 5 个值：`provider_runtime`、`prompt_contract`、`audit_parse`、`fact_gap`、`code_bug`。Plan 未显式说明是否需要扩展 Literal 添加 `audit_rule_too_strict` 和 `llm_timeout`。

当前代码映射现状：
- `llm_timeout` → `provider_runtime`（通过 `_chapter_failure_category_from_exception`）
- 可解析 audit fail/blocked → `prompt_contract`（通过 `_chapter_failure_category_from_audit_result`）

Plan Section 7.4 说 `llm_timeout` 是独立 top-level category，但当前代码将其归入 `provider_runtime`。这在 evidence 报告层面是可接受的（evidence 可记更精确的 `llm_timeout`，代码仍返回 `provider_runtime`），但 plan 应显式说明这一分层。

**Impact**: 不阻塞 implementation。Implementation worker 可选择：(a) 扩展 Literal 添加 `audit_rule_too_strict` 和 `llm_timeout`；(b) 保持现有 5 值 Literal，evidence 层使用更精确分类。两种方式都满足 plan 目标。

**Fix suggestion**: 在 Section 7.4 末尾添加一段说明，明确 taxonomy 是 evidence/reporting 级分类框架，`ChapterFailureCategory` Literal 是否需要扩展由 implementation worker 在 Slice D 中决定，前提是不破坏现有 fail-closed 语义。

## Findings summary

| ID | Severity | Blocking? | Summary |
|---|---|---|---|
| F1 | non-blocking | no | `audit_rule_too_strict` 引用 7.5 条件缺失，应引用 7.4 定义 |
| F2 | non-blocking | no | taxonomy 与代码 Literal 关系未显式说明 |

无 blocking findings。

## Verification against code facts

Plan 的以下声明与当前代码一致：

1. **Writer parser fail-closed**: `chapter_writer.py:803-823` 确认空响应、incomplete finish reason、超长均返回 None + blocking issues。
2. **Writer required structure**: `chapter_writer.py:884-911` 确认第 1-6 章检查 `REQUIRED_BODY_SECTION_HEADINGS`。
3. **Writer required output marker**: `chapter_writer.py:914-939` 确认检查 exact marker presence。
4. **Writer anchor/missing marker parsing**: `chapter_writer.py:958-1021` 确认 allowed set 校验。
5. **Writer invalid marker detection**: `chapter_writer.py:849-881` 确认 anchor/missing marker 非法格式检测。
6. **Writer candidate facet assertion**: `chapter_auditor.py:618-646` 确认 programmatic audit 检查 facet assertion。
7. **Auditor line protocol parser**: `chapter_auditor.py:857-902` 确认严格 line protocol 解析，parse failure 返回 blocked。
8. **Auditor system/user prompt**: `chapter_auditor.py:835-853` 确认 prompt 已包含 pass 格式和 severity line 示例。
9. **Orchestrator repair context**: `chapter_orchestrator.py:1394-1418` 确认 `ChapterRepairContext` 包含 previous_issue_ids/previous_messages/required_corrections。
10. **Orchestrator max repair bounded**: `chapter_orchestrator.py:1351-1358` 确认 `remaining_budget <= 0` 返回 `repair_budget_exhausted`。
11. **Orchestrator failure category mapping**: `chapter_orchestrator.py:1193-1268` 确认 writer blocked 映射到 `prompt_contract` 或 `fact_gap`，audit parse failure 映射到 `audit_parse`，provider exception 映射到 `provider_runtime`。
12. **Orchestrator timeout no repair**: `chapter_orchestrator.py:744-753` 确认 writer exception 直接返回 failed，不进入 repair loop。

## Verdict

**PASS**。Plan 是 handoff-ready / code-generation-ready。两个 non-blocking findings 均为文档精确性改进，不阻塞 implementation worker 按切片执行。Plan 正确聚焦 provider config/auth 已通过后的 writer/auditor contract calibration，覆盖所有要求的安全边界，validation matrix 完整，hard constraints 明确。

Implementation worker 可按 Slice A → B → C → D → E 顺序执行，无需 controller 先回答 blocking questions。
