# P1-S4 Code Review — AgentMiMo

> 日期：2026-05-17
> Reviewer：AgentMiMo
> gate：`P1-S4 code review`
> 分支：`chore/reconcile-baseline`
> 审查范围：9 个 P1-S4 文件

## 结论

**PASS — 无 blocking finding。**

P1-S4 实现满足基线裁决、plan 约束和 AGENTS.md 硬约束的全部关键要求。以下列出 non-blocking findings 和 residual risk。

---

## 审查清单逐项评价

### 1. 基金类型判断是否优先于通用分析

**通过。**

- `extract_profile()` (`fund_agent/fund/extractors/profile.py:302`) 第一行即调用 `classify_fund_type(report)`，在任何画像字段构造之前。
- `test_extract_profile_classifies_before_general_field_builders()` (`tests/fund/extractors/test_profile.py:93-143`) 通过 monkeypatch 直接锁定调用顺序 `["classify", "basic", "product", "benchmark", "fee"]`。
- 构造顺序由代码结构保证，不是约定性注释。

### 2. classified_fund_type 与 classification_basis 是否成为稳定输出

**通过。**

- `FundTypeClassification` (`fund_agent/fund/fund_type.py:59-69`) 是 `frozen=True, slots=True` 的 dataclass，字段不可变。
- `classified_fund_type` 类型为 `FundType` Literal，编译期可检查标签集合。
- `classification_basis` 类型为 `tuple[str, ...]`，不允许为空——每条分类路径都至少返回一个 basis 元素（`fund_type.py:139-142, 147-150, 153-159, 164-176, 179-183, 187-192`）。
- `basic_identity.value` 通过 `_build_basic_identity()` (`profile.py:175-183`) 显式包含 `classified_fund_type` 和 `classification_basis` 两个 key。
- 测试 `test_extract_profile_outputs_classification_basis_and_anchors_for_active_fund()` (`test_profile.py:164-165`) 断言了两个字段的存在。

### 3. 是否存在基金代码特判或不必要硬编码

**通过。**

- `classify_fund_type()` 的全部分支逻辑基于 `§1/§2` 文本中的 `fund_name`、`fund_category`、`benchmark`、`investment_scope` 四个字段做关键词匹配。
- 无任何 `if fund_code == "..."` 或基金代码级条件分支。
- `_INDEX_NAME_KEYWORDS`、`_ENHANCED_KEYWORDS`、`_QDII_KEYWORDS` 等关键词常量属于分类规则配置，不是基金代码硬编码。

### 4. fee_schedule、benchmark、fund_scale、fund_manager 是否都有可溯源 EvidenceAnchor

**通过。**

- `_build_fee_schedule()` (`profile.py:256-286`)：对 `management_fee` 和 `custody_fee` 各调用 `_extract_field()` → `_build_anchor()`，anchor 携带 `section_id`、`row_locator`（字段名）和 `note`（原始命中行）。
- `_build_benchmark()` (`profile.py:232-253`)：同理，单个 anchor。
- `basic_identity` 中的 `fund_scale` 和 `fund_manager` 通过 `_build_basic_identity()` (`profile.py:168-188`) 统一走 `_extract_field()` → `_build_anchor()`。
- 测试 `test_profile.py:166-173` 断言了 `{"fund_scale", "fund_manager"} <= basic_anchor_labels` 和 `{"management_fee", "custody_fee"} <= fee_anchor_labels`。

### 5. 是否严格停留在 §1/§2 最小边界

**通过。**

- `fund_type.py` 的 `_extract_profile_value()` 只遍历 `("§1", "§2")`（第 87 行）。
- `profile.py` 的 `_FIELD_PATTERNS` 中所有字段的 pattern 组合只关联 `"§1"` 或 `"§2"`（第 13-52 行）。
- 无任何对 `§3` 及以后章节的引用。
- 无对 `data_extractor.py`、`documents/**`、`pdf/**` 的修改或越界引用——`profile.py` 仅通过 `ParsedAnnualReport.get_section_text()` 消费已冻结的公共契约。

### 6. 是否符合 AGENTS.md Capability 边界、中文 docstring、测试要求

**部分符合，有 non-blocking findings。详见下文 N-01 ~ N-03。**

### 7. 测试是否足以锁定当前 slice 的正确性

**基本通过，有 non-blocking findings。详见下文 N-04 ~ N-05。**

---

## Non-blocking Findings

### N-01 — docstring "Raises" 声明存在形式化冗余

**严重度**：low
**文件**：
- `fund_agent/fund/fund_type.py:83-84`（`_extract_profile_value`）
- `fund_agent/fund/fund_type.py:110-112`（`_contains_any`）
- `fund_agent/fund/extractors/profile.py:115-117`（`_build_anchor`）

**描述**：多个函数的 docstring 包含 `Raises: 无显式抛出。` 或 `Raises: 无。`。AGENTS.md:113 要求"所有函数必须提供完整中文 docstring（参数、返回值、异常）"，但列出"无显式抛出"既不增加信息量也不降低维护成本，且与 AGENTS.md 的 spirit（注释要说明意图）不完全一致。

**建议**：deferred——后续 slice 统一清理 docstring 风格即可。

### N-02 — `_FIELD_PATTERNS` 与 `_PROFILE_FIELD_PATTERNS` 存在 pattern 重复

**严重度**：low
**文件**：
- `fund_agent/fund/fund_type.py:41-56`（`_PROFILE_FIELD_PATTERNS`）
- `fund_agent/fund/extractors/profile.py:13-52`（`_FIELD_PATTERNS`）

**描述**：两个模块各自维护了一套 `fund_name`、`fund_category`、`benchmark`、`investment_scope` 的正则 pattern，且 pattern 内容高度重叠（如 `r"基金名称\s*[：:]\s*(.+)"` 在两处各出现一次）。若后续年报格式变化需要新增 pattern 变体，两处需同步修改。

**建议**：deferred——当前 slice 边界内不阻塞，但 P1-S8 集成时建议统一到单一 pattern 源，避免 drift。

### N-03 — `_extract_field` 与 `_extract_profile_value` 实现结构重复

**严重度**：low
**文件**：
- `fund_agent/fund/fund_type.py:72-97`（`_extract_profile_value`）
- `fund_agent/fund/extractors/profile.py:72-102`（`_extract_field`）

**描述**：两个函数的核心逻辑几乎一致——遍历 section → 逐行匹配 → 返回首个命中。区别仅在于 `profile.py` 版本返回 `_MatchedField` 对象（携带 section_id 和 matched_line），而 `fund_type.py` 版本只返回字符串。这是两个模块各自的私有函数，不违反 slice 边界，但在 P1-S8 集成阶段值得考虑统一为共享 utility。

**建议**：deferred——当前不阻塞。

### N-04 — 测试未覆盖 index_fund 纯指数分类路径

**严重度**：medium
**文件**：`tests/fund/extractors/test_profile.py`

**描述**：三个 fixture 覆盖了 `active_fund`（110011）、`enhanced_index`（161725）、`bond_fund`（000123），但没有覆盖纯 `index_fund` 类型。`classify_fund_type()` 中 `index_fund` 分支（`fund_type.py:170-176`）是一条独立路径，当 `fund_category` 含"指数"且 `name_and_benchmark` 不含"增强"时命中。当前无 fixture 走这条路径。

**建议**：deferred——不阻塞当前 slice，但建议在 P1-S8 集成测试矩阵或后续 fixture 扩展时补上纯指数基金 fixture。

### N-05 — 测试未覆盖 QDII、FOF 分类路径

**严重度**：medium
**文件**：`tests/fund/extractors/test_profile.py`

**描述**：`classify_fund_type()` 定义了 6 种类型标签，但测试只验证了 3 种（`active_fund`、`enhanced_index`、`bond_fund`）。`qdii_fund`（`fund_type.py:136-142`）和 `fof_fund`（`fund_type.py:144-150`）两条路径无 fixture 覆盖。分类 fallback 路径（`fund_type.py:186-192`，未命中任何规则时默认 `active_fund`）同样无测试。

**建议**：deferred——基线裁决（`p1-s4-baseline-reconciliation-2026-05-17.md:109-110`）已声明"至少覆盖 3 只样本基金里与 §1/§2 相关的最小事实片段"，当前 3 只已满足最低要求。但 QDII/FOF 分类路径在后续 slice 接入更多样本时应优先补充 fixture。

---

## Residual Risk

### RR-S4-1 — 分类规则对 `fund_category` 字段的依赖

当前分类优先级把 `fund_category`（"混合型"、"股票型"、"指数型"等）放在非常高的位置。如果某只基金的年报 `§1/§2` 中 `基金类别` 字段使用了非标准措辞（如"灵活配置型"而非"混合型"），可能落入 fallback 路径被默认归为 `active_fund`。

**影响**：中等——影响后续 `preferred_lens` 应用，但当前 P1-S4 不做 lens 应用，且 fallback 为主动权益基金属于保守选择。
**缓解**：后续 slice 通过更多样本 fixture 暴露边缘 case 后增补关键词。

### RR-S4-2 — fixture 为手工构造的最小文本，非真实年报

三个 fixture 文件均为手工编写的 `§1/§2` 最小片段，格式高度规整。真实年报中的 `基金名称：` 行可能有额外空格、全角冒号变体、或被表格结构打断。

**影响**：低——正则已做了 `\s*[：:]` 兼容处理，但真实年报的复杂度只有在 P1-S8 集成测试时才能充分暴露。
**缓解**：P1-S8 的 3 只样本基金端到端验证矩阵将覆盖真实年报。

### RR-S4-3 — `fund_scale` 与 `fund_manager` anchor 粒度

当前 `_build_anchor()` 对 `fund_scale` 和 `fund_manager` 的 `row_locator` 仅记录字段名，`note` 记录原始命中行。锚点中没有页码和表格 ID，因为 `§1/§2` 文本抽取阶段尚无法获取这些信息。

**影响**：低——plan 中已明确"当前 §1/§2 文本抽取阶段 page_number 可为 None"（`models.py:21` 注释），后续 P2/P3 渲染时再做精确锚点提升。
**缓解**：`EvidenceAnchor` 的 `page_number` 和 `table_id` 已预留字段，后续 slice 可补充。

---

## 总结

| 审查维度 | 判定 |
|---------|------|
| 基金类型判断优先于通用分析 | PASS |
| classified_fund_type 与 classification_basis 为稳定输出 | PASS |
| 无基金代码特判 | PASS |
| fee_schedule / benchmark / fund_scale / fund_manager 有 anchor | PASS |
| 严格停留在 §1/§2 最小边界 | PASS |
| AGENTS.md Capability 边界 | PASS |
| 测试覆盖 | PASS（3 种类型，满足最低要求；纯 index_fund / QDII / FOF 待后续补充） |

**Blocking findings**：0
**Non-blocking findings**：5（N-01 ~ N-05，均建议 deferred）
**Residual risk**：3（RR-S4-1 ~ RR-S4-3）

P1-S4 可以进入 controller acceptance。
