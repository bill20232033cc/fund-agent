# 发布维护 报告质量基线 S0 Corpus Selection Evidence Review (DS)

> 日期: 2026-05-25
> 审阅者: AgentDS（独立 phaseflow 审核代理）
> 分支: `codex/v0-release-readiness-plan`
> Gate: `release-maintenance report-quality baseline / Fact-Evidence contract plan accepted locally`
> 已审核工件: `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md`
> 下一入口: `report-quality-baseline S1 score-schema fixture draft`（如果通过）

## 自查

- 当前角色: AgentDS，作为 phaseflow 独立审核代理。不更改、提交、推送或发起 PR。
- 真源: `AGENTS.md`；`docs/design.md` 当前架构与 report-quality §5.4–§5.4.3、`FundDocumentRepository` 边界、基金类型检测 §6.5、fallback taxononomy §6.1；`docs/implementation-control.md` Startup Packet / 当前 Gate / 下一入口 / 开放残余 / 活跃 Gate 账本。
- 已接受工件: Fact/Evidence contract plan、MiMo review、DS plan review、controller judgment（均日期 2026-05-25）。
- 已验证代码证据: `fund_agent/fund/fund_type.py`（QDII 优先级高于 FOF，第 324 行与第 338 行）；`fund_agent/fund/documents/repository.py`（`FundDocumentRepository` 第 267 行，`load_annual_report` 第 290 行为异步）；`fund_agent/fund/documents/models.py`（`DocumentKey` 第 315 行）；`.gitignore`（`reports/data-source-runs/` 第 24 行）。
- 范围边界: 仅审核工件。不涉及源代码、测试、渲染器、质量门控、主机/代理包、Dayu 运行时、commit、push、PR。

## 裁决

**PASS_WITH_FINDINGS** — 3 项发现，零项阻断。

## 执行摘要

S0 工件满足控制器判决中为该 gate 定义的所有要求：
- 表格包含所有 7 个必填的 S0 字段，以及证据输入、FOF 尝试结果、状态转换合约、停止条件与非目标重新确认
- `FundDocumentRepository` 边界在整个过程中得到尊重——探针仅调用 `load_annual_report()` 和 `classify_fund_type()`
- FOF 已尝试，未阻断，并记录为 `data_gap`；QDII-FOF 未被错误接受为纯 `fof_fund`
- 为所有 6 种状态定义状态转换，包含 trigger、actor 和 minimum evidence
- 未违反任何已接受的非目标约束

3 项发现如下：1 项 MEDIUM（`load_annual_report` 异步签名需要验证），2 项 LOW（状态字段词汇、DocumentKey 简写）。这些在 S1 前应低成本解决，不保证重新提交工件。

---

## 发现

### 发现 1 — MEDIUM — `load_annual_report` 是异步的；工件未说明异步调用

- **工件行**: 32–33（显示 `FundDocumentRepository().load_annual_report(code, year, force_refresh=False)`）
- **代码证据**: `fund_agent/fund/documents/repository.py`，第 290 行定义 `async def load_annual_report(self, fund_code: str, year: int, *, force_refresh: bool = False) -> ParsedAnnualReport:`
- **风险**: 工件描述探针调用为同步。由于探针脚本 `reports/data-source-runs/s0-corpus-selection-20260525/probe_repository_candidates.py` 位于被忽略的路径中（正确如此），我们无法独立验证探针是否使用 `asyncio.run()` 包装器或等效异步上下文。工件应明确说明这一包装，以便未来读者了解实际的仓库调用契约。
- **建议**: 在工件中添加一条注释，说明探针通过 `asyncio.run()` 或异步上下文管理器包装了异步的 `load_annual_report`。如果在 S1 中将探针模式推广为验证步骤，这一步必须在未来实现的门 gate 中变为同步的 `FundAnalysisService` 编排调用。
- **阻断**: 否。探针输出（reviewed 表格行）与 `classify_fund_type()` 结果一致，确认了仓库遍历路径，且 source failure categories 在外部被证明是合理的。信号存在，即使调用语法不精确。

### 发现 2 — LOW — `repository verification status` 是自由文本，不是受控 enum

- **工件行**: 41–47（状态值: `verified`、`verified_as_annual_report_but_type_gap`）
- **证据**: S0 工件将 `repository verification status` 定义为自然语言值。`verified_as_annual_report_but_type_gap` 令人担忧：在单个字段值中混合了文档身份（“已验证为年报”）和基金类型槽位成员资格（“但类型差距”）。S1 必须在槽位边界和失败类别中明确区分这两个维度。
- **风险**: 如果 S1 将 `verified_as_annual_report_but_type_gap` 视为有效的验证状态而没有仔细检查其含义，可能会削弱评分。分数可能将 `fof_fund` 条目标记为关于 FOF 特定维度的“已验证”，而该条目实际上是 QDII-FOF 且当前分类器未将其识别为 FOF。
- **建议**: 在 S1 的可评分语料库表中，将“文档级身份已验证”与“基金类型槽位成员资格已确认”分离为不同的布尔/枚举字段。当前工件适当地披露了差距（`review state: candidate`、`source failure category: data_gap`），但词汇将来可能会被误用。
- **阻断**: 否。工件在审查状态和失败类别中正确处理了类型差距；这是一个模式定义问题，适合在 S1 中解决。

### 发现 3 — LOW — `DocumentKey` 简写与代码 dataclass repr 不匹配

- **工件行**: 41（`DocumentKey(fund_code=004393, year=2024, annual_report)`）
- **代码证据**: `fund_agent/fund/documents/models.py` 第 315 行: `DocumentKey(fund_code: str, year: int, document_kind: Literal["annual_report"])`。真实 repr 会是 `DocumentKey(fund_code='004393', year=2024, document_kind='annual_report')`。
- **风险**: 当前简写省略了字段名 `document_kind=`，删除了字符串引号，使用了带前导零的整数，并将 `annual_report` 作为位置参数显示。这纯粹是修饰性问题，但如果有人尝试将此工件中的标识符与 `document_kind` 的 `Literal` 类型进行机械匹配，可能会在 S1 中导致混淆。
- **建议**: 如果 `DocumentKey` 简写在后续工件中重复出现，请使用匹配 dataclass 字段名和 Python 语法的规范形式。
- **阻断**: 否。

---

## 积极确认

以下约束已基于可验证证据得到确认：

### S0 必填字段 —— 全部具备
- 工件第 39 行表格: fund type slot、fund code、report year、repository verification status、review state、source failure category、ignored run path。全部 7 项均已填充。
- 通过 `rg` 验证（工件第 116 行）确认这些字段存在于工件中。

### FundDocumentRepository 边界 —— 已尊重
- 工件第 12 行: “生产年报访问仅通过 `FundDocumentRepository.load_annual_report(...)`；未触及直接 PDF 缓存、下载辅助、EID 辅助或东方财富辅助。”
- 工件第 32–34 行: 探针只调用 `FundDocumentRepository().load_annual_report()` 和 `classify_fund_type(report)`。
- 已验证: `FundDocumentRepository` 存在于 `fund_agent/fund/documents/repository.py:267`。`load_annual_report` 存在于第 290 行。`classify_fund_type` 存在于 `fund_agent/fund/fund_type.py:300`。代理层基金领域能力，在正确边界内调用。

### FOF 处理 —— 正确
- 尝试了 S0 FOF 与两个候选基金: `007721` 和 `017970`（工件第 53–54 行）。
- 均因 QDII-FOF 分类为 `qdii_fund` 而非 `fof_fund`。代码级证据: `classify_fund_type()` 在第 324 行检查 QDII 关键词，在第 338 行检查 FOF。由于 `007721`（“天弘标普500发起(QDII-FOF)A”）命中 `_QDII_KEYWORDS = ("QDII", "境外")`，在未到达 FOF 检查之前就返回了 `qdii_fund`。
- 工件记录 `data_gap`，非阻断性失败（工件第 58 行）。这与控制器判决一致（第 42 行：S0 不应因 FOF 缺失而阻断，必须记录为 `data_gap`，FOF 在第二轮通行中成为必需）。
- 工件将 QDII-FOF 标识为 QDII-FOF，而非纯 `fof_fund`（工件第 56 行：“现有已审核黄金证据也将 classified_fund_type 记录为 qdii_fund”）。正确。

### 审查状态转换 —— 完整定义
- 工件第 65–80 行: 所有 6 种状态均定义了 trigger、actor 和 minimum evidence。
- `candidate -> repository_verified`: 触发因素是通过 `FundDocumentRepository` 成功进行的年报身份探针。Actor: 证据工作者或未来脚本；控制器审核工件。证据: 基金代码、报告年份、文档种类、来源元数据、已解析章节/表格存在性、基金类型分类、failure category。
- `repository_verified -> fact_prefill_generated`: 触发因素是结构化提取/预填命令运行。Actor: 未来 S1/S2 实现工作者。证据: 被忽略的运行路径、命令、输入语料库 ID、生成的事实与锚点或差距记录。
- `fact_prefill_generated -> fact_prefill_reviewed`: 触发因素是人类审核员对每个评分字段的接受/纠正/推迟。Actor: 人类审核员。证据: `docs/reviews/` 下的 Markdown 证据表。
- `fact_prefill_reviewed -> scoring_ready`: 触发因素是控制器确认。Actor: 控制器。证据: 已审核证据工件路径、语料库表、无身份不匹配、显式 N/A 处理。
- `scoring_ready -> accepted_baseline`: 触发因素是观测性评分运行完成并审核接受。Actor: S1 审核员 + 控制器。证据: 评分问题及本地化、分母语义、来源边界、failure categories、下一 gate 建议。

### 非目标 —— 未违反
- 工件第 92–100 行明确重新确认: 无渲染器更改、无 FQ0-FQ6 行为更改、无 LLM 审计/证据确认/修复循环声明、无 Host/Agent 包创建、无 `dayu.host`/`dayu.engine` 引入、无直接 PDF/缓存/辅助访问、无 fixture 推广。
- 已验证: `git status` 确认无源代码更改（所有内容均为 `docs/reviews/` 下的未跟踪文档工件）。

### 停止条件 —— 已定义
- 工件第 84–90 行: 如果多个基金类型槽位的身份验证失败，则在 S0 后停止。为 `schema_drift`、`identity_mismatch`、`integrity_error` 定义显式 fail-closed 条件。`not_found`/`unavailable` 模式应转到来源可靠性工作。未经验证的替代品不得被接受以弥补覆盖差距。

### 运行工件卫生 —— 正确
- `.gitignore:24:reports/data-source-runs/` 覆盖 `reports/data-source-runs/s0-corpus-selection-20260525/`（工件第 125 行验证）。
- 工件第 100 行: “未将本地运行输出推广为跟踪的 fixtures”。

### 审查状态与仓库验证状态一致性
- `active_fund` (004393): `verified` → `repository_verified`。分类器返回 `active_fund`，匹配槽位。正确。
- `index_fund` (110020): `verified` → `repository_verified`。分类器返回 `index_fund`，匹配。正确。
- `enhanced_index` (004194): `verified` → `repository_verified`。分类器返回 `enhanced_index`，匹配。正确。
- `bond_fund` (006597): `verified` → `repository_verified`。分类器返回 `bond_fund`，匹配。正确。
- `qdii_fund` (017641): `verified` → `repository_verified`。分类器返回 `qdii_fund`，匹配。正确。
- `fof_fund` (007721): `verified_as_annual_report_but_type_gap` → `candidate`。分类器返回 `qdii_fund`，与 `fof_fund` 槽位不匹配。工件保守地保留了 `candidate` 审查状态，这是合适的。
- `fof_fund` (017970): `verified_as_annual_report_but_type_gap` → `candidate`。相同逻辑。正确。

---

## 开放问题 / 残余

| 问题 | 严重性 | 由谁处理 |
|-------|----------|-----------|
| 探针脚本无法验证（在被忽略的路径中）——信任工作者自报，风险可接受，S0 证据在表格行中，而非脚本内容 | LOW，信任但不可验证 | 控制器判决接受此风险或要求验证 |
| 东方财富 fallback 原始失败类别未保留（工件第 108 行确认） | LOW，已知残余 | S1 来源可靠性 gate 通过保留原始失败类别来选择持久语料库 |
| `verified_as_annual_report_but_type_gap` 应该拆分为 S1 的两个字段 | LOW，S1 模式设计 | S1 工件必须定义单独的身份与类型槽位成员资格字段 |
| `DocumentKey` 简写在工件中不精确 | LOW，修饰性 | S1 工件作者 |

---

## 控制器接受前需修复的项

无。3 项发现均不阻断。

**建议**: 作为 S1 启动包的一部分，要求 Future S1 evidence worker 解决 F-1（记录异步调用）。F-2 和 F-3 是模式设计问题，自然属于 S1 的 `score-schema fixture draft` gate。

---

## 推荐

**进入下一 gate**: `report-quality-baseline S1 score-schema fixture draft`。

S0 工件为涵盖 5 种基金类型的语料库建立了可审核的、经仓库验证的证据（第 6 种为 `data_gap`），在正确的仓库边界内，具备完整的状态转换定义和明确的停止条件。S1 应继承 S0 的语料库表作为输入，将 `repository verification status` 词汇统一为单独的字段，并定义观察性评分模式，不推广 fixtures。

---

## 验证

```text
rg -n "fund type slot|repository verification status|review state|source failure category|ignored run path|fof_fund|data_gap|FundDocumentRepository|load_annual_report|classify_fund_type|async|DocumentKey" docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-review-ds-20260525.md
git diff --check
```

`pytest` 或 `ruff` 不适用——此工件仅更改文档，不包含可执行代码、测试、包元数据、渲染器行为或质量门控行为。
