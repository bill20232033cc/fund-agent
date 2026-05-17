# P1-S4 Code Review (AgentGLM)

> 日期：2026-05-17
> Reviewer：AgentGLM
> Phase / Slice：P1 / P1-S4 基础画像与基金类型识别
> 分支：`chore/reconcile-baseline`
> 审查输入：
> - Baseline：`docs/reviews/p1-s4-baseline-reconciliation-2026-05-17.md`
> - Implementation：`docs/reviews/p1-s4-implementation-2026-05-17.md`
> - Plan：`docs/reviews/p1-plan-2026-05-17.md`
> - 设计真源：`docs/design.md`
> - 总控：`docs/implementation-control.md`

---

## 结论

**PASS — 无 blocking finding。**

P1-S4 实现满足当前 slice 的全部核心约束：基金类型判断先于通用抽取、`classified_fund_type` 与 `classification_basis` 成为稳定输出、无基金代码特判、关键字段均带 `EvidenceAnchor`、严格停留在 `§1/§2` 边界内。测试 4/4 通过。

下文列出 3 条 non-blocking findings，建议在后续 slice 或 refactor 窗口处理。

---

## 检查点逐项评价

### 1. 基金类型判断是否优先于通用分析

**结论：满足。**

- `extract_profile()` 在 `profile.py:302` 显式先调用 `classify_fund_type(report)`，再构建画像字段。
- 测试 `test_extract_profile_classifies_before_general_field_builders`（`test_profile.py:93-143`）通过 monkeypatch 锁定调用顺序为 `["classify", "basic", "product", "benchmark", "fee"]`。
- 顺序由测试直接断言，不依赖实现细节注释。

### 2. classified_fund_type 与 classification_basis 是否成为稳定输出

**结论：满足。**

- `FundTypeClassification` dataclass（`fund_type.py:59-69`）定义了 `classified_fund_type: FundType` 与 `classification_basis: tuple[str, ...]`。
- `basic_identity.value` 在 `profile.py:181-182` 包含这两个字段。
- 所有 4 个测试均断言 `result.basic_identity.value["classified_fund_type"]` 和 `classification_basis` 非空。
- `FundType` 是 `Literal` 类型（`fund_type.py:15-22`），枚举值固定为 6 种，类型层面防止了非法标签。

### 3. 是否存在基金代码特判或不必要硬编码

**结论：满足。无基金代码特判。**

- `classify_fund_type()`（`fund_type.py:117-192`）仅基于 `fund_name`、`fund_category`、`benchmark`、`investment_scope` 四个字段的关键词匹配。
- 不存在任何 `if fund_code == "110011"` 式特判。
- 分类关键词定义为模块级 `Final` 常量（`fund_type.py:24-40`），便于后续扩展。
- 测试 `test_extract_profile_classifies_multiple_fund_types_without_code_special_case`（`test_profile.py:176-208`）使用不同基金代码验证分类不依赖代码。

### 4. fee_schedule、benchmark、fund_scale、fund_manager 是否都有可溯源 EvidenceAnchor

**结论：满足。**

- `fee_schedule`：`_build_fee_schedule()`（`profile.py:256-286`）为 `management_fee` 和 `custody_fee` 各构造 `EvidenceAnchor`，包含 `source_kind="annual_report"`、`document_year`、`section_id`、`row_locator`、`note`（原始命中行）。
- `benchmark`：`_build_benchmark()`（`profile.py:232-253`）构造单个 anchor。
- `fund_scale`、`fund_manager`：在 `_build_basic_identity()`（`profile.py:168-194`）中作为 matched_fields 参与 anchors 构造。
- 测试 `test_extract_profile_outputs_classification_basis_and_anchors_for_active_fund`（`test_profile.py:146-173`）断言 `{"fund_scale", "fund_manager"} <= basic_anchor_labels` 和 `{"management_fee", "custody_fee"} <= fee_anchor_labels`，以及 `benchmark.anchors[0].section_id == "§2"`。

### 5. 是否严格停留在 §1/§2 最小边界

**结论：满足。**

- `_extract_field()`（`profile.py:86-102`）的 `_FIELD_PATTERNS` 仅定义 `§1` 和 `§2` 的 pattern。
- `_extract_profile_value()`（`fund_type.py:72-97`）仅遍历 `("§1", "§2")`。
- 没有任何对 `§3/§4/§8/§9/§10` 的引用。
- 没有触碰 `data_extractor.py`、`documents/**`（除 import models 公共契约）、`pdf/**`。

### 6. 是否符合 AGENTS.md 的 Capability 边界、中文 docstring、测试要求

**结论：基本满足。有 1 条 non-blocking finding。**

- Capability 边界：所有新增代码位于 `fund_agent/fund/`，符合 AGENTS.md:84-88 的 Capability 层定义。
- 中文 docstring：所有公开和私有函数均有中文 docstring，包含 Args/Returns/Raises 三段。
- 测试：4 个测试覆盖分类顺序、分类依据+anchor、多基金类型识别。
- **Finding N-2**（见下文）：6 种基金类型中只测试了 3 种，覆盖缺口需后续补齐。

### 7. 测试是否足以锁定当前 slice 的正确性

**结论：满足最低通过门槛，但有补强空间。**

- 最低通过标准（plan §8.2："3 只样本基金都能输出 `classified_fund_type` 与 `classification_basis`"）已满足。
- 3 个 fixture 分别覆盖 `active_fund`、`enhanced_index`、`bond_fund`。
- 缺失覆盖见 Finding N-2、N-3。

---

## Findings

### N-1 [MEDIUM] fund_type.py 与 profile.py 之间存在 regex pattern 重复定义

**严重度：Non-blocking**

**文件与行号：**
- `fund_type.py:41-56`（`_PROFILE_FIELD_PATTERNS`）
- `profile.py:13-52`（`_FIELD_PATTERNS`）

**事实：**

两个模块各自独立定义了 `fund_name`、`fund_category`、`benchmark`、`investment_scope` 四个字段的正则 pattern。以 `fund_name` 为例：

- `fund_type.py:43-44`：`(r"基金名称\s*[：:]\s*(.+)", r"基金简称\s*[：:]\s*(.+)")`
- `profile.py:14-17`：`("§1", (r"基金名称\s*[：:]\s*(.+)", r"基金简称\s*[：:]\s*(.+)"))` 以及 `("§2", (r"基金名称\s*[：:]\s*(.+)",))`

两者 pattern 文本相同但结构不同（fund_type.py 不区分章节，profile.py 按章节分组）。如果未来新增 pattern 别名（如 `基金全称`），需要同步修改两处，存在漂移风险。

**建议：** 在 P1-S8 或后续 refactor 窗口，将 pattern 定义收口到一个共享位置，或让 `fund_type.py` 直接复用 `profile.py` 的提取结果。当前 slice 不需要改动。

---

### N-2 [MEDIUM] 6 种基金类型仅测试 3 种，index_fund / qdii_fund / fof_fund 无 fixture 无测试

**严重度：Non-blocking**

**文件与行号：**
- `fund_type.py:15-22`：`FundType` 定义了 6 种类型
- `test_profile.py:176-181`：parametrize 只覆盖 `enhanced_index` 和 `bond_fund`
- `tests/fixtures/fund/extractors/profile/`：只有 3 个 fixture 文件

**事实：**

当前 `classify_fund_type()` 定义了 6 种分类路径（QDII → FOF → 主动权益 → 指数/增强指数 → 债券 → 兜底），但测试只验证了 3 条路径：

| 类型 | fixture | 测试 | 状态 |
|------|---------|------|------|
| `active_fund` | `active_fund_profile.txt` | `test_extract_profile_outputs_classification_basis_and_anchors_for_active_fund` | ✅ |
| `enhanced_index` | `index_enhanced_profile.txt` | parametrize 第 1 组 | ✅ |
| `bond_fund` | `bond_fund_profile.txt` | parametrize 第 2 组 | ✅ |
| `index_fund` | — | — | ❌ |
| `qdii_fund` | — | — | ❌ |
| `fof_fund` | — | — | ❌ |

`index_fund` 是 `enhanced_index` 的 else 分支（`fund_type.py:170-176`），需要单独 fixture 验证不命中"增强"关键词时走纯指数路径。`qdii_fund` 和 `fof_fund` 有独立的优先级判断逻辑（`fund_type.py:136-150`），也需要 fixture 覆盖。

**建议：** 当前 slice 最低标准（3 只样本）已满足，不阻塞。但在 P1-S5 或 P1-S8 之前补齐 `index_fund`、`qdii_fund`、`fof_fund` 的 fixture 和 parametrize 用例，以关闭分类路径的回归缺口。

---

### N-3 [LOW] `_build_basic_identity` 使用列表索引映射字段值，顺序耦合较脆弱

**严重度：Non-blocking**

**文件与行号：** `profile.py:168-183`

**事实：**

```python
matched_fields = [
    _extract_field(report, "fund_name"),     # [0]
    _extract_field(report, "fund_code"),     # [1]
    _extract_field(report, "fund_category"), # [2]
    _extract_field(report, "fund_scale"),    # [3]
    _extract_field(report, "fund_manager"),  # [4]
]
value = {
    "fund_name": matched_fields[0].value if matched_fields[0] else None,
    "fund_code": matched_fields[1].value if matched_fields[1] else None,
    ...
}
```

字段名与列表索引的对应关系完全靠位置隐式维护。如果未来在列表中间插入或删除一个字段提取调用，value 字典的映射会静默错位，且不会有任何编译期或运行期告警。

**建议：** 当前实现可工作，不阻塞。后续若 `_build_basic_identity` 增加字段，可改为 `dict[str, _MatchedField | None]` 按名字查找，消除顺序耦合。

---

## 残余风险

| 风险 | 影响 | 缓解建议 |
|------|------|---------|
| 真实年报 `§1/§2` 的字段名/格式与 fixture 不一致 | 实际提取失败或字段缺失 | P1-S8 集成时用 3 只真实样本验证；当前 fixture 是最小可测子集，后续需与真实年报对齐 |
| 分类关键词表不够全面 | 新样本基金无法正确分类 | 后续 slice 按需扩充 `_INDEX_NAME_KEYWORDS`、`_BOND_KEYWORDS` 等，同时补齐对应 fixture |
| 无 index_fund / qdii_fund / fof_fund 测试 | 这三条分类路径存在回归风险 | 在 P1-S5 或 P1-S8 补齐 fixture 和测试 |
| `fund_type.py` fallback 到 `active_fund`（`fund_type.py:186-192`） | 非主动权益基金可能被错误归类 | 后续 slice 增加兜底日志或警告，让上层感知"分类低置信度" |

---

## 审查总结

P1-S4 在当前 slice 边界内实现了：
- 基金类型识别模块（`fund_type.py`），6 种类型、关键词驱动、无代码特判
- extractor 数据模型（`models.py`），`EvidenceAnchor` + `ExtractedField` + `ProfileExtractionResult`
- 基础画像抽取器（`profile.py`），§1/§2 only，分类先于字段构造，所有关键字段带 anchor
- 最小 fixture 和测试，4/4 通过

3 条 non-blocking findings 均可在后续 slice 或 refactor 窗口处理，不阻塞当前 gate 前进。
