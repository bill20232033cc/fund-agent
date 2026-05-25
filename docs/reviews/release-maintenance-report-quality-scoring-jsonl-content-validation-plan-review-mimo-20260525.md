# Plan Review: Report-Quality Scoring JSONL Content Validation

> Gate: `report-quality scoring JSONL content validation plan`
> Reviewer: AgentMiMo
> Date: 2026-05-25
> Plan artifact: `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-20260525.md`
> Truth sources: `AGENTS.md`, `docs/design.md` §5.4 / §5.4.1 / §5.4.2 / §7.1-§7.6, `docs/implementation-control.md` Startup Packet / Next Entry Point, `fund_agent/fund/report_evidence.py`

---

## 结论

**PASS_WITH_FINDINGS**

Plan 整体 code-generation-ready，第一性原理方向正确，typed domain 复用充分，非目标边界严格，规则集合覆盖面广。存在 1 个 material finding 和 4 个 minor findings；无 blocking finding。

---

## 审查逐项

### 1. 第一性原理：先可验证、可复盘，再接 CLI/Service

**通过。** Plan §2 第 70-71 行明确："当前问题不是'用户如何触发 validator'，而是'评分输入本身是否可验证、可复盘、可驱动后续迭代'"。文件范围仅新增 `report_quality_validation.py` + 测试，不改 renderer、Service、CLI、quality_gate.py。这是正确的 sequency。

### 2. 复用 ReportEvidenceBundle / ReportScoreIssueLink typed domain

**通过。** Plan §3 第 84 行："不允许创建与 ReportEvidenceBundle / ReportScoreIssueLink 平行的 report-quality schema"。API 入口接受 `ReportEvidenceBundle | Mapping[str, object]`，所有 enum domain 从 `report_evidence.py` 复用（§4.B 第 184 行），建议用 `typing.get_args()` 生成 allowlist。Implementation handoff 第 4 步（第 450 行）强调"从 report_evidence.py 导入 typed domain"。

### 3. FQ0-FQ6 不变

**通过。** Plan §1 第 26-27 行明确非目标："本 gate 不替代、不削弱、不重写 FQ0-FQ6；不改变 quality_gate.py 的既有 gate semantics"。Stop condition 第 1 条（第 461 行）将其列为硬停止条件。

### 4. 禁止项合规

**通过。** Plan §1 第 30-38 行逐项声明禁止 PDF/cache/source helper、FundDocumentRepository、Host/Agent/dayu、nav_data projection、fixtures/durable baseline、extra_payload/kwargs。§7 边界检查（第 408-418 行）逐项确认。§6 验证命令（第 392-394 行）用 `rg` 扫描 forbidden imports。Stop condition 第 2-7 条覆盖所有禁止场景。

### 5. 规则集合可实现性、完整性、一致性

**基本通过，有 1 个 material gap。**

- **Field presence (A)**：bundle required fields 与 `ReportEvidenceBundle` dataclass 定义一致（我已逐字段对照 `report_evidence.py:610-652`）。Score issue required fields 与 `ReportScoreIssueLink` 一致（`report_evidence.py:441-481`）。条件必填规则合理。✓
- **Enum domain (B)**：枚举列表完整覆盖 `report_evidence.py` 中所有 Literal domain（我已对照第 29-217 行）。✓
- **Invalid combinations (C)**：16 条规则覆盖面广。C9/C10 覆盖 fail-closed source + fallback。C11 覆盖 external_official。C12 覆盖 extraction_mode/value 矛盾。C13-C15 覆盖 pass/skipped/chapter_summary 语义。✓
- **ID references (D)**：10 条规则覆盖 fact/anchor/gap/issue/document/calculation 间引用。D8 正确区分 `anchor:` 前缀和 Markdown review artifact ref。✓
- **N/A semantics (E)**：4 条规则清晰。✓
- **chapter_summary semantics (F)**：4 条规则与现有 projection validation（`report_evidence.py:1991-1994`）一致。✓
- **Source boundary / failure category (G)**：5 条规则完整。✓
- **scoring_ready preconditions (H)**：10 条前置条件与 `_is_scoring_ready()`（`report_evidence.py:2090-2128`）完全对齐。✓
- **双向链接完整性 (I)**：4 条规则覆盖 gap↔issue↔fact 闭合。✓

**Material gap**：Plan 缺少 `ReportSourceDocument` 级 `fallback_used` / `fallback_allowed` 内部一致性校验。规则 C9/C10 只检查 `fallback_used` 与 `source_failure_category` 的关系，G5 定义了 `fallback_allowed` 与 failure category 的映射，但 validator 不检查 bundle 内 `source_documents[].fallback_allowed` 是否与 `source_documents[].source_failure_category` 一致，也不检查 `fallback_used=True` 时 `fallback_allowed` 是否为 `True`。虽然 projection context guard 已在投影时阻断矛盾（`report_evidence.py:964-967`），但 validator 应独立验证序列化后 bundle 的内部一致性，否则 projection bug 会产生不可检测的脏数据。

### 6. 文件范围、测试计划、验证命令、Stop conditions

**通过。**

- 文件范围精确：1 个新模块 + 1 个新测试文件 + 最小修改 2 个文件。✓
- 测试计划：16 个核心测试 + 负例矩阵 10 个 case，覆盖正例/负例/fail-closed/边界。✓
- 验证命令：pytest + coverage ≥80% + ruff + rg forbidden patterns + git diff --check。✓
- Stop conditions：7 条硬停止条件，覆盖所有 scope creep 场景。✓
- Success signals：8 条可验证信号。✓

---

## Findings（按严重度排序）

### F1. [Material] 缺少 ReportSourceDocument fallback_used / fallback_allowed 内部一致性校验

**位置**：Plan §4.C (Invalid combinations) 和 §4.G (Source boundary / failure category)

**问题**：Plan 规则 C9/C10 只检查 `fallback_used` 与 `source_failure_category` 的关系，G5 定义了 `fallback_allowed` 的语义映射，但 validator 没有显式规则检查 bundle 内 `source_documents[]` 记录的 `fallback_allowed` 字段是否与 `source_failure_category` 一致，也没有检查 `fallback_used=True` 时 `fallback_allowed` 是否为 `True`。

**风险**：如果 projection 代码存在 bug 生成了 `fallback_used=True, fallback_allowed=False` 的 `ReportSourceDocument`，validator 不会检测到。虽然 projection context guard 在投影时已阻断此类矛盾，但 validator 的设计目标是独立验证序列化后 bundle 的完整性。

**建议**：在 §4.C 新增规则：
- `source_documents[].fallback_allowed` 必须与 `source_documents[].source_failure_category` 一致：仅 `not_found` / `unavailable` 为 `True`，其余为 `False`。
- `source_documents[].fallback_used=True` 时 `fallback_allowed` 必须为 `True`。
- 违反为 `RQV_FALLBACK_CONFLICT/blocking`。

### F2. [Minor] N/A 语义规则 E2 与 invalid combination 规则 C16 严重度建议存在张力

**位置**：Plan §4.C 第 207 行（C16）和 §4.E 第 238 行（E2）

**问题**：E2 说"N/A issue 不应携带 severity"，C16 说"status=='N/A' 同时存在 severity：minor 或 material，推荐 minor"。虽然不矛盾（C16 是 validator 对 E2 违反的输出严重度），但"推荐 minor"意味着 validator 对 E2 语义违反只报 minor，下游消费者可能不重视。如果 E2 是硬语义规则，validator 输出应为 material 或 blocking。

**建议**：将 C16 的 severity 建议从"minor 或 material，推荐 minor"改为"material"，与 E2 的"不应"语义强度匹配。或在 C16 中明确说明"当前 slice 选择 minor 是因为 N/A 不进入分母，severity 字段不影响评分计算；后续 gate 可升级为 material"。

### F3. [Minor] 测试计划未覆盖嵌套结构内 enum 校验的显式负例

**位置**：Plan §6 测试计划和负例矩阵

**问题**：负例矩阵第 4 行"test_invalid_enum_value_is_blocking"覆盖了 bundle 顶层 enum，但未显式列出嵌套结构（如 `ReportSourceDocument.source_boundary`、`ReportDataGap.gap_kind`、`ReportFact.extraction_mode`）的非法 enum 值负例。虽然实现应自动覆盖，但显式负例有助于防止实现遗漏。

**建议**：在负例矩阵中增加一行：`source_documents[0].source_boundary="invalid_value"` → `RQV_ENUM_INVALID/blocking`。或在测试 4 的描述中明确要求覆盖嵌套结构。

### F4. [Minor] 双向链接完整性验证可进一步加强

**位置**：Plan §4.I (data_gap_refs / evidence_anchor_refs 完整性)

**问题**：规则 I.1 检查 issue→gap 双向闭合，I.3 检查 issue→fact 闭合，但以下方向未覆盖：
- fact 的 `score_issue_ids` 是否指向 bundle 内实际存在的 issue（D4 已覆盖，但 I 节未提及）。
- `ReportEvidenceAnchor.document_id` 如果非空，是否存在于 `document_ids`（anchors 的 `document_id` 是 optional，projection 代码设置为 `document_id` for annual_report source kind）。

**建议**：在 I 节补充：fact `score_issue_ids` 双向闭合检查已在 D4 覆盖，I 节可引用 D4。anchor `document_id` 非空时应存在于 `document_ids`，缺失为 material。

### F5. [Minor] 未验证 preferred_lens.chapters 内每条记录的字段完整性

**位置**：Plan §4.H (scoring_ready preconditions)

**问题**：H.7 检查 `preferred_lens.chapters` 覆盖 chapter_0 到 chapter_7 且顺序稳定，但不检查每条 `ReportPreferredLensChapter` 的必填字段（`lens_key`、`used_default`、`primary_focus`）。如果 projection 生成了 chapter_id 正确但其他字段缺失的记录，validator 不会检测到。

**风险**：低。Projection 代码（`report_evidence.py:1206-1224`）从 `build_lens_application_plan()` 结果构造章节，结构完整性由上游保证。但 validator 独立验证是防御性编程的好实践。

**建议**：在 §4.A field presence 中为 `ReportPreferredLensChapter` 增加必填字段检查：`chapter_id`、`lens_key`、`used_default`、`primary_focus`。违反为 material。

---

## Residual Risks

| # | Risk | 说明 | Owner |
|---|------|------|-------|
| R1 | 大 JSONL 文件性能 | Plan 未讨论大 JSONL 文件的内存和时间性能约束。当前 scratch 输出规模小，但如果后续 scoring-run 产出大文件，validator 可能需要流式处理。 | future scoring-run scalability gate |
| R2 | derived_calculations 计算状态与 output_value 一致性 | Plan 不验证 `calculation_status` 与 `output_value` 的关系（如 `blocked_by_missing_fact` 时 `output_value` 应为 `None`）。当前 slice 默认空 calculations，后续 derived-calculation source slice 应补充。 | future derived-calculation source slice |
| R3 | 边界 rg 命令覆盖范围 | §6 验证命令的 rg 检查覆盖了主要 forbidden patterns，但不覆盖 `from fund_agent.fund.documents import` 或 `from fund_agent.fund.quality_gate import` 等具名 import。建议 implementation agent 在 §7 边界检查中手动确认 import 语句。 | implementation agent |
| R4 | `data_gap.chapter_ids` 包含 `report_level` 的语义 | `report_level` 在 `ChapterRef` domain 中是合法值，data gaps 使用 `report_level` 表示 bundle 级缺口。Validator 不检查 `report_level` 在 score issue 的 `chapter_id` 中是否合法（`ReportScoreIssueLink.chapter_id` 类型为 `ChapterRef`，包含 `report_level`）。当前 plan 不区分，但后续 gate 可能需要约束 score issue 的 `chapter_id` 范围。 | future scoring-validation follow-up |
| R5 | JSON decode error 处理策略二选一 | §5 第 329-331 行建议 `validate_report_quality_jsonl()` 对 JSON decode error 返回 `RQV_JSONL_INVALID` 或抛出异常，"二者在实现中择一但测试必须固定"。建议实现选择返回 `RQV_JSONL_INVALID` 以保持 fail-closed 语义一致，但这属于实现决策，不阻断 plan。 | implementation agent |

---

## 对照 checklist

| 检查项 | 结果 |
|--------|------|
| 是否符合第一性原理：先可验证可复盘 | ✅ |
| 是否复用 typed domain，无 parallel schema | ✅ |
| FQ0-FQ6 不变 | ✅ |
| 禁止 PDF/cache/source helper/FundDocumentRepository | ✅ |
| 禁止 extra_payload/kwargs | ✅ |
| 禁止 Host/Agent/dayu | ✅ |
| 禁止 nav_data projection | ✅ |
| 禁止 fixtures/durable baseline | ✅ |
| 规则集合可实现 | ✅ |
| 规则集合足够完整 | ⚠️ F1 fallback consistency gap |
| 规则集合无互相矛盾 | ⚠️ F2 N/A severity 张力 |
| 文件范围明确 | ✅ |
| 测试计划足够明确 | ⚠️ F3 嵌套 enum 负例 |
| 验证命令足够明确 | ✅ |
| Stop conditions 足够明确 | ✅ |
| 四层边界检查 | ✅ |
| 工程基线检查 | ✅ |
| Success signals 可验证 | ✅ |
