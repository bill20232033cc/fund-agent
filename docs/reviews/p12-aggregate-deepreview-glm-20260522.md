# P12 Aggregate Deep Review (AgentGLM)

> **日期**: 2026-05-22
> **Review range**: `ba77e02..HEAD`
> **Review agent**: AgentGLM
> **Base commit**: `ba77e02`
> **Head commit**: `HEAD` (main)

---

## 结论：PASS

P12 完整实现了 ITEM_RULE deterministic renderer/audit compliance，无 blocking findings。所有 P12-S1 和 P12-S2 review 中标记的 residuals 均有明确 owner/destination，scope 控制严格，无越界改动。

---

## 1. Review Scope

### 1.1 Diff 概览

`ba77e02..HEAD` 共 32 文件变更（+3158 / -20）：

| 类别 | 文件 | 说明 |
|------|------|------|
| **源码** | `fund_agent/fund/template/item_rules.py` | 新增 `TemplateItemRuleAuditContext` 类型 |
| **源码** | `fund_agent/fund/template/renderer.py` | ITEM_RULE 决策解析、按基金类型渲染/删除固定段落、多锚点证据边界 |
| **源码** | `fund_agent/fund/template/__init__.py` | 导出 `TemplateItemRuleAuditContext` |
| **源码** | `fund_agent/fund/audit/audit_programmatic.py` | 新增 `_audit_item_rule_compliance` 和 `_audit_single_item_rule_decision` |
| **测试** | `tests/fund/template/test_renderer.py` | 六类基金渲染矩阵、固定段落验证、证据边界覆盖 |
| **测试** | `tests/fund/audit/test_audit_programmatic.py` | ITEM_RULE 审计 failure paths 覆盖 |
| **文档** | `fund_agent/fund/README.md` | renderer/audit/ITEM_RULE 说明同步 |
| **文档** | `tests/README.md` | 测试覆盖描述同步 |
| **Review/Control** | `docs/implementation-control.md` + 24 review artifacts | Phase 记录、S1/S2 review、follow-up planning |

### 1.2 排除确认

- `docs/repo-audit-20260521.md`：**未纳入** diff（`git diff --name-only ba77e02..HEAD | grep repo-audit` = 0 matches）。
- RR-13 源数据（`016492` 相关）：**未纳入** diff。
- Quality gate 源码 `fund_agent/fund/audit/quality_gate.py`：**未修改**（`grep FQ5` 无输出）。

---

## 2. 逐项审查

### 2.1 ITEM_RULE Deterministic Renderer/Audit Compliance（重点 1）

**结论：完整满足，无 overclaiming。**

- Renderer 通过 `_resolve_item_rule_decisions()` 从 `structured_data.basic_identity.value.classified_fund_type` 确定性调用 `evaluate_template_item_rules(fund_type=..., facets=())` 生成决策。
- 四条 ITEM_RULE 段落均有固定 heading + 固定 bullet key：`_render_index_constituents_segment`、`_render_manager_philosophy_segment`、`_render_alpha_yearly_breakdown_segment`、`_render_tracking_error_segment`。
- 未触发 conditional 规则不渲染段落；`_render_item_rule_segments_for_chapter` 只对 `decision.status == "render"` 且 `decision.chapter_id == chapter_id` 的决策输出段落。
- 无 LLM 调用、无文本推断、无外部数据依赖。

### 2.2 Renderer/Audit 共享同一 Decision Source（重点 2）

**结论：消费同一 ITEM_RULE decision source，无 divergent inference。**

- Renderer `render_template_report()` 生成 `item_rule_decisions` 后同时写入 `TemplateRenderResult.item_rule_decisions` 和 `TemplateRenderResult.audit_input.item_rule_decisions`。
- Audit `_audit_item_rule_compliance()` 只消费 renderer 传入的 `decisions`，不重新从报告 prose 或 fund type 推断决策。
- 证据链：`item_rules.py evaluate_template_item_rules()` → `renderer.py _resolve_item_rule_decisions()` → `TemplateRenderResult.audit_input.item_rule_decisions` → `audit_programmatic.py _audit_item_rule_compliance()`。单链路，无分叉。

### 2.3 identity_missing / identity_present / unsupported Fail-Closed（重点 3）

**结论：三种路径全部 fail-closed 或兼容。**

| 路径 | 行为 | 验证 |
|------|------|------|
| `identity_missing`（`basic_identity.value is None`） | 返回 `(), "identity_missing"`；audit 收到空决策 + `identity_missing` context 时跳过 ITEM_RULE 检查 | `test_run_programmatic_audit_skips_missing_decision_issue_for_identity_missing_context` |
| `identity_present` + decisions 正常 | Audit 逐条验证 render/delete 与 chapter block 一致 | `test_render_template_report_applies_item_rule_segments_by_fund_type` × 6 类型 |
| `identity_present` + decisions 为空 | Audit 触发 C2 blocker：`"基金身份存在但缺少 ITEM_RULE 决策"` | `test_run_programmatic_audit_detects_identity_present_missing_item_rule_decisions` |
| `classified_fund_type` 缺失 | Renderer 抛出 `ValueError("P1 结构化数据缺少有效 classified_fund_type")` | `test_render_template_report_rejects_present_identity_without_classified_fund_type` |
| `classified_fund_type` 不受支持 | `evaluate_template_item_rules` → `_validate_fund_type` 抛出 `ValueError` | `test_render_template_report_rejects_unsupported_classified_fund_type` |

### 2.4 Conditional Segment Render/Delete Chapter-Scoped and Marker-Based（重点 4）

**结论：严格 chapter-scoped、marker-based，不扫 global markdown。**

- Audit `_audit_single_item_rule_decision` 通过 `blocks_by_id.get(decision.chapter_id)` 定位目标章节块，只在 `block.body_markdown` 中检查 `rendered_segment_present(block.body_markdown, rule)`。
- `rendered_segment_present` 使用 `rule.segment_markers_any`（`#### 指数编制规则与成分股` 等 heading 级标记），不使用普通正文短语（`_FORBIDDEN_SEGMENT_MARKERS` 排除 `跟踪指数` 等）。
- 测试 `test_run_programmatic_audit_checks_item_rule_markers_inside_matching_chapter_only` 验证：将 marker 从正确章节移到错误章节后，audit 报告正确章节缺失、不误报错误章节命中。

### 2.5 Multi-Anchor Provenance No Overclaiming（重点 5）

**结论：锚点只表达 provenance，不暗示 tracking-error/index methodology/constituents 已有实质数据。**

- `_item_rule_evidence_bullet` 渲染全部去重锚点，用 `；` 连接，prefix 为 `- 证据边界：`。
- 所有四条 ITEM_RULE 段落中，tracking error、index methodology、constituents 均显式输出 `_INSUFFICIENT_TEXT`（`"数据不足，当前输入未抽取跟踪误差"` 等）。
- 锚点引用只证明数据来源引用（provenance），不证明数据内容完整性。README 明确声明："这些锚点只表达 provenance，不证明跟踪误差、指数编制方法或成分股已经具备实质数据"。
- `> 📎 证据` 章节级证据行格式未在 ITEM_RULE 段落内使用，避免破坏每章一条契约。测试 `test_render_template_report_renders_item_rule_segments_with_fixed_bullets_and_evidence_boundaries` 显式验证 `not any(line.startswith("> 📎 证据") for line in index_segment)`。

### 2.6 FQ5/Quality Gate 语义未扩大（重点 6）

**结论：FQ5 语义未变。**

- `fund_agent/fund/audit/quality_gate.py` 在 P12 diff 中 **无修改**（`grep FQ5` 返回空）。
- README 更新仅 **澄清** FQ5 的职责边界："FQ5 只消费 score.json 中由 CHAPTER_CONTRACT / ITEM_RULE manifest 派生的适用性事实……renderer/audit 的 ITEM_RULE 合规由程序审计 C2 在报告渲染后验证"。
- ITEM_RULE 当前不接入质量门禁。README 显式声明："ITEM_RULE 当前不接入质量门禁、Service/UI/CLI 产品选项，也不改变 FQ5 语义"。

### 2.7 无越界改动（重点 7）

**结论：严格遵守模块边界。**

检查 P12 全部源码变更：

- `fund_agent/fund/template/`（Capability 层）：ITEM_RULE 类型定义、renderer 段落渲染逻辑、`__init__.py` 导出。
- `fund_agent/fund/audit/`（Capability 层）：C2 ITEM_RULE 合规审计。
- 无 Service 层、UI 层、CLI、Engine、Runtime 变更。
- 无 `dayu-agent` 依赖引入。
- 无 documents repository、PDF parser、external API 变更。
- 符合 `AGENTS.md` 模块边界第 6 条：Capability 层包含基金领域知识、审计规则，不依赖上层。

### 2.8 测试覆盖（重点 8）

**结论：覆盖完整。**

| 测试维度 | 测试文件 | 覆盖内容 |
|----------|----------|----------|
| **Render 矩阵** | `test_renderer.py` `test_render_template_report_applies_item_rule_segments_by_fund_type` | 6 类基金 × 4 个 marker parametrize |
| **固定段落验证** | `test_renderer.py` `test_render_template_report_renders_item_rule_segments_with_fixed_bullets_and_evidence_boundaries` | 4 条规则固定 bullet + 数据不足声明 |
| **空锚点边界** | `test_renderer.py` `test_render_template_report_renders_item_rule_empty_anchor_boundary_for_present_identity` | 身份存在 + 空 anchors → 精确缺证文本 |
| **锚点去重** | `test_renderer.py` `test_item_rule_evidence_bullet_deduplicates_duplicate_anchors` | 重复 anchor 只渲染一次 |
| **identity_missing 路径** | `test_renderer.py` missing data path + `test_audit_programmatic.py` identity_missing skip | 空决策 + identity_missing context |
| **Audit: render marker missing** | `test_audit_programmatic.py` | 触发段落被删除 → C2 失败 |
| **Audit: delete marker present** | `test_audit_programmatic.py` | 应删除段落残留 → C2 失败 |
| **Audit: identity_present no decisions** | `test_audit_programmatic.py` | C2 blocker |
| **Audit: duplicate/unknown/mismatched** | `test_audit_programmatic.py` | 三类非法决策均 fail closed |
| **Audit: chapter-scoped only** | `test_audit_programmatic.py` | marker 移到错误章节 → 原章节报缺失 |
| **Docs sync** | README 两处 | `fund_agent/fund/README.md` 和 `tests/README.md` 同步更新 |

### 2.9 Residuals 与 Closeout（重点 9）

**结论：所有 residuals 有明确 owner/destination，main-branch closeout 合理。**

P12 aggregate pass 后的 residuals 全部从 S1/S2 继承，无新增：

| Residual | Owner/Destination | 状态 |
|----------|-------------------|------|
| Real tracking-error extraction | 后续 extractor slice | Deferred |
| Real index methodology extraction | 后续 extractor slice | Deferred |
| Evidence sufficiency (E1/E2/E3) | 后续审计层 slice | Deferred |
| Long-anchor truncation | 后续 UI/rendering slice | Deferred |
| Future ITEM_RULE expansion | 由模板草稿和 design doc 驱动 | Design-gated |
| Chapter-mismatch C2 noise cleanup | 后续 audit slice | Deferred |
| RR-13 duplicate `016492` | Human-owned | Open |
| `docs/repo-audit-20260521.md` | 排除在 P12 外 | Excluded |

---

## 3. 验证结果摘要

| 检查项 | 结果 |
|--------|------|
| `git diff --check ba77e02..HEAD` | Passed（无 whitespace/trailing errors） |
| Targeted template/audit tests | 83 passed |
| Adjacent extraction_score/quality_gate tests | 43 passed |
| `ruff check` on P12 source/test files | Passed |
| Full pytest | 403 passed |

---

## 4. Findings

无 blocking 或 non-blocking findings。

P12 在 S1/S2 review 中已被两位 reviewer 充分审查，controller judgment 对四项 GLM findings 和 residuals 做了明确 disposition。Aggregate review 确认：

- S1/S2 所有 findings 已在 S2 或 README 中 disposition 完毕。
- 无新增 scope、无遗漏测试路径、无隐式耦合。
- 所有 residuals 有 owner/destination，closeout 策略合理。

---

## 5. 对照文档一致性

| 文档 | 一致性 | 说明 |
|------|--------|------|
| `AGENTS.md` | 一致 | Capability 层变更，不违反模块边界和硬约束 |
| `docs/design.md` | 一致 | ITEM_RULE 属于第 3.1 节模板渲染，C2 属于第 5.2 节程序审计 |
| `docs/implementation-control.md` | 一致 | P12 phase notes 和 active residuals 已更新 |
| `docs/reviews/post-p12-s2-follow-up-plan-review-controller-judgment-20260522.md` | 一致 | Aggregate review 是 controller 指定的 next gate |
| `docs/reviews/p12-s1-code-review-controller-judgment-20260522.md` | 一致 | S1 findings 已 disposition |
| `docs/reviews/p12-s2-code-review-controller-judgment-20260522.md` | 一致 | S2 findings 已 disposition |

---

## 6. 最终裁定

**PASS**

P12 aggregate deep review 确认：ITEM_RULE deterministic renderer/audit compliance 完整实现，renderer 和 audit 消费同一 decision source，identity/unsupported 路径全部 fail-closed，chapter-scoped marker-based 检查无 global scan 风险，multi-anchor provenance 不暗示数据完备，FQ5 语义未扩大，无越界改动，测试覆盖 render 矩阵 + audit failure paths + evidence boundary + docs sync。所有 residuals 有明确 owner。P12 可以关闭。
