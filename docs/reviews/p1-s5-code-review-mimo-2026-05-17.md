# P1-S5 Code Review — AgentMiMo

> 日期：2026-05-17
> Reviewer：AgentMiMo
> gate：`P1-S5 code review`
> 分支：`chore/reconcile-baseline`
> 审查范围：7 个 P1-S5 文件

## 结论

**PASS — 无 blocking finding。**

P1-S5 实现满足基线裁决、plan 约束和 AGENTS.md 硬约束的全部关键要求。以下列出 non-blocking findings 和 residual risk。

---

## 审查清单逐项评价

### 1. 是否严格只处理 §3 的 nav_benchmark_performance 与 investor_return

**通过。**

- `performance.py:16`：`_SECTION_ID = "§3"` 为唯一章节入口。
- `performance.py:17-35`：`_FIELD_PATTERNS` 只包含 `nav_growth_rate`、`benchmark_return_rate`、`investor_return_rate`、`estimated_investor_return_rate` 四组 pattern。
- `extract_performance()`（`performance.py:213-229`）唯一公开函数，输出 `PerformanceExtractionResult`，只含 `nav_benchmark_performance` 和 `investor_return` 两个字段。
- `models.py:70-80`：`PerformanceExtractionResult` 只声明上述两个字段，无多余入口。
- 无任何对 `§4/§8/§9/§10` 的引用。

### 2. investor_return 是否明确区分 direct / estimated / missing，且未披露时没有静默空字符串

**通过。**

- `_build_investor_return()`（`performance.py:162-210`）显式构造三条互斥路径：
  1. `investor_return_rate` 直接命中 → `extraction_mode="direct"`（`performance.py:177`），`disclosure_status="direct"`，`fallback_status="not_needed"`。
  2. `estimated_investor_return_rate` 命中 → `extraction_mode="estimated"`（`performance.py:197`），`disclosure_status="estimated"`，`fallback_status="applied_in_section"`。
  3. 均未命中 → `extraction_mode="missing"`（`performance.py:208`），`disclosure_status="missing"`，`fallback_status="pending_later_slice"`，`investor_return_rate=None`。
- 缺失路径返回 `note="§3 未直接披露投资者收益率；当前 slice 仅显式标记 missing，后续再接入 fallback。"`（`performance.py:209`），不是静默空字符串。
- 三条路径在 `test_performance.py` 中分别有独立测试（第 89、115、142 行）。

### 3. 所有直接命中或估算口径命中是否都带 EvidenceAnchor

**通过。**

- `_build_anchor()`（`performance.py:83-105`）为每个 `_MatchedField` 构造 `EvidenceAnchor`，携带 `source_kind="annual_report"`、`document_year`、`section_id="§3"`、`row_locator`（字段名）、`note`（原始命中行）。
- `_build_nav_benchmark_performance()`（`performance.py:144-148`）：对已命中的 `nav_growth_rate` 和 `benchmark_return_rate` 各自构建 anchor。
- `_build_investor_return()` direct 路径（`performance.py:183`）：带 1 个 anchor。
- `_build_investor_return()` estimated 路径（`performance.py:195`）：带 1 个 anchor。
- `_build_investor_return()` missing 路径（`performance.py:207`）：`anchors=()` — 合理，缺失无证据可锚定。
- 测试 `test_performance.py:85-86` 和 `test_performance.py:112, 138` 均断言了 anchor 的存在和 `row_locator` 值。

### 4. 是否未越界到 documents/pdf/data_extractor/nav_data/其他 extractor

**通过。**

- `performance.py` 的 import 只有：
  - `fund_agent.fund.documents.models.ParsedAnnualReport`（已冻结的公共契约）
  - `fund_agent.fund.extractors.models`（本 slice 允许修改）
- `__init__.py` 只新增 `PerformanceExtractionResult` 和 `extract_performance` 的导出。
- 无任何对 `data_extractor.py`、`pdf/**`、`nav_data.py`、`profile.py`（其他 extractor）的 import 或引用。
- `performance.py` 仅通过 `report.get_section_text(_SECTION_ID)` 和 `report.key.year` 消费仓库接口，不直接操作文件系统。

### 5. 当前 estimated 是否仍停留在 P1 允许边界内，没有偷跑 P2 分析公式

**通过。**

- `estimated` 路径（`performance.py:188-199`）只识别 `§3` 文本中显式出现"（估算）"标记的行，如"加权平均投资者收益率（估算）：6.66%"。
- 没有任何跨章节计算、份额变动 × 净值变化估算、或 R=A+B-C 公式。
- 缺失路径（`performance.py:201-210`）显式标注 `fallback_status="pending_later_slice"`，明确推迟到后续 slice。
- 无投资结论或分析判断逻辑。

### 6. 中文 docstring、Capability 边界、测试是否满足 AGENTS.md

**基本通过，有 non-blocking findings。详见 N-04。**

- `performance.py` 所有函数均有中文 docstring，包含参数、返回值和异常说明。
- `models.py` 的 `PerformanceExtractionResult` 有中文 docstring 和 attribute 说明。
- `test_performance.py` 所有测试函数有中文 docstring。
- `performance.py` 位于 `fund_agent/fund/extractors/`，属于 Capability 层，符合 AGENTS.md:84-107 的归属判定。
- `_FIELD_PATTERNS` 为模块级常量 dict，符合 AGENTS.md:128"配置化"要求。

### 7. 测试是否足以锁定当前 slice 的正确性，是否有明显漏测

**基本通过，有 non-blocking findings。详见 N-01 ~ N-03。**

- 4 个测试覆盖了 3 个 fixture 的全部三态路径：
  - `test_extract_performance_outputs_nav_and_benchmark_with_anchors`：直接披露 fixture，验证 nav/benchmark + anchor。
  - `test_extract_performance_outputs_direct_investor_return_when_disclosed`：直接披露路径。
  - `test_extract_performance_outputs_estimated_investor_return_when_marked_in_section`：估算披露路径。
  - `test_extract_performance_marks_missing_investor_return_without_silent_blank`：缺失路径。
- 明确漏测场景见 N-01 ~ N-03。

---

## Non-blocking Findings

### N-01 — 测试未覆盖 §3 章节完全缺失的边界情况

**严重度**：medium
**文件**：`tests/fund/extractors/test_performance.py`

**描述**：当前三个 fixture 都包含有效 `§3` 文本。若 `get_section_text("§3")` 返回 `None` 或空字符串，`_extract_field()` 对所有字段均返回 `None`，`_build_nav_benchmark_performance()` 会走到 `_missing_field("§3 未披露净值增长率/业绩比较基准收益率")`（`performance.py:150`），`_build_investor_return()` 走到 missing 路径（`performance.py:201-210`）。这条完整链路没有测试覆盖。

**建议**：deferred——不阻塞当前 slice，P1-S8 集成测试矩阵中的样本基金应覆盖 §3 缺失场景。

### N-02 — 测试未覆盖 nav_benchmark_performance 部分命中（仅 nav 或仅 benchmark）

**严重度**：medium
**文件**：`tests/fund/extractors/test_performance.py`、`fund_agent/fund/extractors/performance.py:149-158`

**描述**：`_build_nav_benchmark_performance()` 的 `if not anchors:`（`performance.py:149`）只在 nav_growth_rate 和 benchmark_return_rate 同时缺失时返回 missing。若仅命中其一，函数仍返回 `extraction_mode="direct"`，但 `value` 字典中另一个子字段为 `None` 且无对应 anchor。当前所有 fixture 都是"同时存在"或"同时不存在"，未覆盖这个部分命中的中间态。

**建议**：deferred——真实年报中净值增长率和基准收益率通常成对出现，但建议 P1-S8 补一个仅含净值增长率无基准收益率的 fixture 来锁定此行为。

### N-03 — nav_benchmark_performance 在部分子字段缺失时仍标记为 direct

**严重度**：low
**文件**：`fund_agent/fund/extractors/performance.py:151-158`

**描述**：接 N-02。当仅 nav_growth_rate 命中而 benchmark_return_rate 缺失时，`extraction_mode="direct"` 语义上不完全准确——`value` 中有一个子字段是 `None`。更保守的做法是检查两个核心子字段是否都存在，否则降级。但当前设计在 P1 边界内可接受：至少有一个 anchor 证明 §3 有数据。

**建议**：deferred——当前行为在 P1 数据层不构成正确性风险，后续 slice 可考虑在 `note` 中标注部分命中。

### N-04 — docstring "Raises: 无显式抛出。" 存在形式化冗余

**严重度**：low
**文件**：
- `fund_agent/fund/extractors/performance.py:94`（`_build_anchor`）
- `fund_agent/fund/extractors/performance.py:119`（`_missing_field`）
- `fund_agent/fund/extractors/performance.py:139`（`_build_nav_benchmark_performance`）
- `fund_agent/fund/extractors/performance.py:173`（`_build_investor_return`）
- `fund_agent/fund/extractors/performance.py:224`（`extract_performance`）

**描述**：与前序 slice（P1-S1 ~ P1-S4）的同一 finding 一致。5 个函数的 docstring 包含 `Raises: 无显式抛出。`，不增加信息量。

**建议**：deferred——后续统一清理。

### N-05 — fixture 为手工构造的最小文本，未覆盖真实年报格式变体

**严重度**：low
**文件**：
- `tests/fixtures/fund/extractors/performance/performance_with_investor_return.txt`
- `tests/fixtures/fund/extractors/performance/performance_with_estimated_investor_return.txt`
- `tests/fixtures/fund/extractors/performance/performance_without_investor_return.txt`

**描述**：三个 fixture 都是高度规整的 4~5 行文本。真实年报 §3 可能包含多年度对比表格、全角/半角混合、行内空格变体等。`_FIELD_PATTERNS` 的正则已做了 `\s*[：:]` 兼容，但复杂表格结构下的行级抽取能力只能在集成测试时验证。

**建议**：deferred——P1-S8 的 3 只样本基金端到端矩阵将覆盖真实年报。

### N-06 — `investor_return_rate` 与 `estimated_investor_return_rate` pattern 的匹配顺序依赖隐式文本标记

**严重度**：low
**文件**：`fund_agent/fund/extractors/performance.py:175-199`

**描述**：`_build_investor_return()` 先检查 `investor_return_rate`（不含"估算"标记的 pattern），再检查 `estimated_investor_return_rate`（含"（估算）"标记的 pattern）。当前正则设计确保"加权平均投资者收益率（估算）"不会被 `investor_return_rate` 的 pattern 错误捕获（因为 `\s*[：:]` 要求字段名后紧跟冒号，不会匹配到 `（估算）`），匹配顺序是安全的。但这种安全性依赖于 pattern 细节而非显式互斥声明，后续新增 pattern 变体时需留意顺序。

**建议**：deferred——当前正确，建议在 pattern 注释中明确标注顺序依赖。

---

## Residual Risk

### RR-S5-1 — 真实年报 §3 格式异构可能导致 pattern 漏匹配

`_FIELD_PATTERNS` 每个字段提供 2~3 个 pattern 变体，覆盖了"基金份额净值增长率"/"净值增长率"等简称。但不同基金公司的年报可能使用完全不同的字段命名（如"份额净值增长"而非"净值增长率"），当前无法通过手工 fixture 发现。

**影响**：中等——影响提取准确率，但不影响三态逻辑的正确性（漏匹配会走到 missing 路径）。
**缓解**：P1-S8 的 3 只样本端到端验证将暴露格式差异；`missing` 三态已为漏匹配提供了安全的降级路径。

### RR-S5-2 — 百分比值为字符串类型，未做数值解析和校验

`_extract_field()` 返回的是正则捕获的原始字符串（如 `"12.34%"`），没有转换为 `float` 或校验格式。`value` 字典中的 `nav_growth_rate`、`benchmark_return_rate`、`investor_return_rate` 都是字符串类型。

**影响**：低——P1 是数据层，当前行为是"原样提取"，数值解析和校验属于 P2 分析层职责。
**缓解**：后续 P2 消费时再做类型转换和范围校验。

### RR-S5-3 — estimated 路径的语义边界依赖后续 slice 补强

当前 `estimated` 只覆盖"§3 文本中显式出现'（估算）'标记"的情况。`docs/design.md:161-162` 规划的投资者收益率缺失 fallback（按份额变动 × 净值变化估算）属于 P1-S8 或后续 slice，当前 `missing` 路径的 `fallback_status="pending_later_slice"` 已为后续实现预留了明确入口。

**影响**：低——当前 slice 边界内行为正确，且已显式标注待后续处理。
**缓解**：后续 slice 接入 `§10` 份额数据时补强 estimated 路径。

---

## 总结

| 审查维度 | 判定 |
|---------|------|
| 严格只处理 §3 的 nav_benchmark_performance 与 investor_return | PASS |
| investor_return 区分 direct / estimated / missing，无静默空字符串 | PASS |
| 直接命中与估算口径命中均带 EvidenceAnchor | PASS |
| 未越界到 documents/pdf/data_extractor/nav_data/其他 extractor | PASS |
| estimated 停留在 P1 允许边界内，无 P2 分析公式 | PASS |
| 中文 docstring、Capability 边界、测试满足 AGENTS.md | PASS |
| 测试覆盖当前 slice 正确性 | PASS（3 态全覆盖；§3 缺失、部分命中、格式变体待后续补强） |

**Blocking findings**：0
**Non-blocking findings**：6（N-01 ~ N-06，均建议 deferred）
**Residual risk**：3（RR-S5-1 ~ RR-S5-3）

P1-S5 可以进入 controller acceptance。
