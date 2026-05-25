# Re-Review: Report-Quality Scoring JSONL Content Validation Plan

> Gate: `report-quality scoring JSONL content validation plan`
> Reviewer: AgentMiMo
> Date: 2026-05-25
> Prior review: `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-review-mimo-20260525.md`
> Plan artifact (patched): `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-20260525.md`

---

## 结论

**PASS**

Plan patch 完整解决了初始 review 的全部 5 个 findings，无新增 blocker。Plan code-generation-ready。

---

## Prior Findings 逐项关闭判定

### F1. [Material] 缺少 ReportSourceDocument fallback_used / fallback_allowed 内部一致性校验

**已关闭。** Patch 新增：

- §4.C 规则 3（第 195 行）：`source_documents[].fallback_allowed` 必须与 `source_failure_category` 一致，仅 `not_found` / `unavailable` 为 `True`。`RQV_FALLBACK_CONFLICT/blocking`。
- §4.C 规则 4（第 196 行）：`fallback_used=True` 时 `fallback_allowed` 必须为 `True`。`RQV_FALLBACK_CONFLICT/blocking`。
- §4.G 规则 5-6（第 254-255 行）：对 `ReportSourceDocument` 级别的 fallback_allowed/fallback_used 一致性做了显式约束。
- 负例矩阵新增 2 行（第 383-384 行）：`fallback_allowed=True, source_failure_category=none` 和 `fallback_used=True, fallback_allowed=False`。

规则在 C 和 G 两个位置互相引用，覆盖完整。

### F2. [Minor] N/A 语义规则 E2 与 invalid combination 规则 C16 严重度建议存在张力

**已关闭。** Patch 修改：

- §4.C 规则 12（第 204 行）：severity 从"minor 或 material，推荐 minor"改为"material"。
- §4.E 规则 2（第 236 行）：从"不应携带 severity"改为"携带 severity 时输出 `RQV_NA_SEMANTICS/material`"，语义明确。
- §5 错误码表（第 306 行）：`RQV_NA_SEMANTICS` 从 `blocking/material/minor` 收窄为 `blocking/material`，移除 minor 级别。
- 测试 10（第 358 行）：重命名为 `test_na_requires_reason_uses_material_for_severity_and_does_not_allow_blocking_gap`，明确期望 material。
- 负例矩阵（第 387 行）：`issue status=N/A with severity=minor` → `RQV_NA_SEMANTICS/material`。

E2 与 C12 现在一致：N/A 携带 severity 是 material 级语义违反，不再有张力。

### F3. [Minor] 测试计划未覆盖嵌套结构内 enum 校验的显式负例

**已关闭。** Patch 修改：

- 测试 4（第 352 行）：增加注释"必须覆盖嵌套 enum，例如 `source_documents[0].source_boundary=\"invalid_value\"`"。
- 负例矩阵（第 385 行）：新增 `source_documents[0].source_boundary=invalid_value` → `RQV_ENUM_INVALID/blocking`。

### F4. [Minor] 双向链接完整性验证可进一步加强

**已关闭。** Patch 修改：

- §4.D 规则 9（第 227 行）：新增"evidence anchor `document_id` 非空时必须存在于 `document_ids`；缺失为 material，若 bundle 声明 `scoring_ready` 则 blocking"。
- 测试 18（第 366 行）：新增 `test_anchor_document_id_must_exist_in_source_documents`。
- 负例矩阵（第 392 行）：新增 `evidence anchor document_id=doc:missing` → `RQV_REF_MISSING/material` 或 scoring_ready 时 blocking。

### F5. [Minor] 未验证 preferred_lens.chapters 内每条记录的字段完整性

**已关闭。** Patch 修改：

- §4.A 条件必填 6（第 179 行）：新增"preferred_lens.chapters[] 每条记录必须包含 chapter_id、lens_key、used_default、primary_focus；缺失为 material，若 bundle 声明 scoring_ready 则 blocking"。
- 测试 17（第 365 行）：新增 `test_preferred_lens_chapter_required_fields_are_validated`。
- 负例矩阵（第 395 行）：新增 `preferred_lens.chapters[0] missing primary_focus` → `RQV_FIELD_MISSING/material` 或 scoring_ready 时 blocking。

---

## Patch 引入的额外改进（非 finding，但值得确认）

1. **§4.C 去重 scoring_ready 规则**（第 194 行）：原 C2-C8 合并为一条引用 §4.H 的规则，避免同一语义被重复计入 summary。§4.H（第 259 行）声明自己是 scoring_ready 前置条件的唯一 canonical location。这是正确的 design，消除了实现时的歧义。

2. **§4.H 新增 fact review_status precondition**（第 273 行）：scoring_ready 要求所有 facts 的 `review_status=="reviewed"`。测试 7（第 355 行）和负例矩阵（第 380 行）已覆盖。与 `_is_scoring_ready()` 中 `context.fact_review_status == "reviewed"` 对齐。

3. **§4.E.4 / §4.F.5 canonical issue 去重**（第 238、246 行）：同一 record 同时违反 N/A 和 chapter_summary 语义时只输出一条 canonical issue，避免 summary counts 重复。负例矩阵（第 389 行）覆盖。

4. **测试计划新增 3 个测试**（测试 7 扩展、测试 17、测试 18），负例矩阵从 10 行扩展到 17 行。覆盖更完整。

5. **§5 错误码表 RQV_FALLBACK_CONFLICT severity**（第 304 行）：从 `blocking/material` 收窄为 `blocking`，与所有 fallback conflict 规则（C3/C4/C6）的 blocking 语义一致。

以上改进均合理，不引入新问题。

---

## 新 Blocker 检查

**无新增 blocker。** Patch 只在现有规则框架内增补和收紧，未改变 plan 的文件范围、非目标、stop conditions 或 success signals。
