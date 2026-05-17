# P1-S5 Code Review (AgentGLM)

> 日期：2026-05-17
> Reviewer：AgentGLM
> gate：`P1-S5 code review`
> 审查输入：baseline reconciliation、implementation artifact、plan、design.md、implementation-control.md、AGENTS.md
> 审查范围：P1-S5 允许文件共 7 个

## 结论：PASS — 无 blocking finding

P1-S5 实现严格留在 §3 边界内，`investor_return` 三态（direct / estimated / missing）清晰且无静默空字符串，所有直接命中与估算口径命中均带 `EvidenceAnchor`，未越界到 `documents/pdf/data_extractor/nav_data` 或其他 extractor，`estimated` 仅读取 §3 中已显式标注估算口径的文本，未偷跑 P2 分析公式。

以下为 non-blocking findings 和 residual risk。

---

## 逐项审查

### 1. 是否严格只处理 §3 的 nav_benchmark_performance 与 investor_return

**PASS。**

- `performance.py:16` 定义 `_SECTION_ID: Final[str] = "§3"`，全文唯一章节入口。
- `_FIELD_PATTERNS`（`performance.py:17-35`）仅包含 `nav_growth_rate`、`benchmark_return_rate`、`investor_return_rate`、`estimated_investor_return_rate` 四个字段，全部属于 §3 范围。
- `extract_performance()`（`performance.py:213-229`）返回 `PerformanceExtractionResult`，仅含 `nav_benchmark_performance` 和 `investor_return` 两个 `ExtractedField`。
- 未发现任何对 §4/§8/§9/§10 的引用或 fallback 逻辑。

### 2. investor_return 是否明确区分 direct / estimated / missing，且未披露时没有静默空字符串

**PASS。**

`_build_investor_return()`（`performance.py:162-210`）明确三分支：

| 分支 | 行号 | `extraction_mode` | `disclosure_status` | `fallback_status` | value |
|------|------|-------------------|---------------------|--------------------|-------|
| 直接披露 | 175-186 | `"direct"` | `"direct"` | `"not_needed"` | 具体数值 |
| 估算口径披露 | 188-199 | `"estimated"` | `"estimated"` | `"applied_in_section"` | 具体数值 |
| 未披露 | 201-210 | `"missing"` | `"missing"` | `"pending_later_slice"` | `None` |

未披露路径返回 `value=None`，不是空字符串 `""`。`note` 字段（`performance.py:209`）显式说明"后续再接入 fallback"，不存在静默空字符串风险。

三分支优先级正确：先查 `investor_return_rate`（直接），再查 `estimated_investor_return_rate`（估算），最后 fallback missing。正则匹配不会交叉误命——`performance.py:27` 的 `r"加权平均投资者收益率\s*[：:]\s*(.+)"` 要求 `收益率` 后紧跟 `\s*[：:]`，不会匹配 `收益率（估算）：` 格式，因此估算口径文本不会误入直接披露分支。

### 3. 所有直接命中或估算口径命中是否都带 EvidenceAnchor

**PASS。**

- `_build_anchor()`（`performance.py:83-105`）为每个命中字段构造 `EvidenceAnchor`，包含 `source_kind="annual_report"`、`document_year`、`section_id="§3"`、`row_locator`（字段名）和 `note`（原始命中行）。
- `_build_nav_benchmark_performance()`（`performance.py:144-148`）为 nav_growth_rate 和 benchmark_return_rate 各自构造 anchor，至少有一个命中即返回。
- `_build_investor_return()` 直接披露路径（`performance.py:183`）和估算口径路径（`performance.py:196`）均有 `anchors=(_build_anchor(...),)`。
- missing 路径 `anchors=()`（`performance.py:206`）正确表示无可锚定的证据。

### 4. 是否未越界到 documents/pdf/data_extractor/nav_data/其他 extractor

**PASS。**

经边界检查：

- `performance.py` 仅 import `re`、`dataclasses`、`ParsedAnnualReport`（from `documents.models`）和 extractors 内部 models——全部在允许范围内。
- 无 `data_extractor`、`pdf`、`nav_data` 或其他 extractor 的 import。
- `__init__.py` 新增的 `PerformanceExtractionResult` 和 `extract_performance` 导出是 `__init__.py` 的职责，未引起外部消费——经 grep 确认，`fund_agent/` 目录内除 `extractors/__init__.py` 外无任何文件引用 `PerformanceExtractionResult` 或 `extract_performance`。
- `models.py` 的变更仅为追加 `PerformanceExtractionResult` dataclass，不影响已有 `ProfileExtractionResult`。

### 5. 当前 estimated 是否仍停留在 P1 允许边界内，没有偷跑 P2 分析公式

**PASS。**

`estimated` 路径（`performance.py:188-199`）仅执行以下操作：

1. 调用 `_extract_field(report, "estimated_investor_return_rate")` 从 §3 文本中用正则匹配已标注"估算"口径的文本行。
2. 返回匹配到的原始值（如 `"6.66%"`），不做任何计算或转换。

未发现 R=A+B-C、份额变动估算、跨章节计算或任何 P2 分析公式。`note`（`performance.py:198`）明确写"当前按 estimated 返回"，不存在偷跑。

### 6. 中文 docstring、Capability 边界、测试是否满足 AGENTS.md

**PASS（含 non-blocking observation）。**

| AGENTS.md 要求 | 代码证据 | 判定 |
|---|---|---|
| 完整中文 docstring（参数、返回值、异常） | 所有公开/私有函数均有中文 docstring 含 Args/Returns/Raises | PASS |
| 模块级概览中文 docstring | `performance.py:1`、`models.py:1`、`test_performance.py:1` | PASS |
| 测试覆盖证据锚点格式 | test_performance 断言 `anchor.row_locator` | PASS |
| 测试覆盖审计规则触发 | N/A——P1-S5 不涉及审计规则 | N/A |
| 单文件测试覆盖率 ≥80% | 4 个测试覆盖主路径 4/4 分支，但见 finding N-1/N-2 | 大致满足 |

### 7. 测试是否足以锁定当前 slice 的正确性，是否有明显漏测

**PASS（含 non-blocking findings）。**

4 个测试用例覆盖三态完整路径：

| 测试 | fixture | 覆盖路径 |
|---|---|---|
| `test_extract_performance_outputs_nav_and_benchmark_with_anchors` | with_investor_return | nav/benchmark direct + anchor |
| `test_extract_performance_outputs_direct_investor_return_when_disclosed` | with_investor_return | investor_return direct |
| `test_extract_performance_outputs_estimated_investor_return_when_marked_in_section` | with_estimated_investor_return | investor_return estimated |
| `test_extract_performance_marks_missing_investor_return_without_silent_blank` | without_investor_return | investor_return missing |

三态全覆盖，无遗漏。但存在以下非关键测试间隙（见 Non-blocking Findings）。

---

## Non-blocking Findings

### N-1：缺少 §3 章节整体缺失时的测试

- **严重度**：non-blocking
- **文件/行号**：`tests/fund/extractors/test_performance.py`（无对应测试）
- **现象**：当前 4 个测试均通过 `_build_report_from_fixture()` 构造 `ParsedAnnualReport`，其中 `sections` 必然包含 `"§3"` 且 `get_section_text("§3")` 必然返回非空文本。未测试 `sections` 不含 `"§3"` 或 `get_section_text("§3")` 返回空字符串的场景。
- **代码行为**：`_extract_field()` 在 `section_text` 为 falsy 时返回 `None`（`performance.py:68-69`），进而 `_build_nav_benchmark_performance()` 会走 `_missing_field()` 路径（`performance.py:149-150`），`_build_investor_return()` 会走 missing 路径（`performance.py:201-210`）。**行为正确，但未被测试锁定。**
- **建议**：deferred 到 P1-S8 集成测试或 P1-S6 补充。在 `_build_report_from_fixture` 中增加一个 `include_section: bool = True` 参数即可最小成本覆盖。

### N-2：缺少 nav/benchmark 部分命中的测试

- **严重度**：non-blocking
- **文件/行号**：`tests/fund/extractors/test_performance.py`（无对应测试）
- **现象**：未测试"nav_growth_rate 命中但 benchmark_return_rate 缺失"或反之的场景。此时 `_build_nav_benchmark_performance()`（`performance.py:151-158`）会返回 `extraction_mode="direct"` 但 value dict 中有一个 `None` 字段。
- **代码行为**：当前返回 `extraction_mode="direct"` + 部分为 `None` 的 value。这不是 bug（至少有一个 anchor 就不算完全 missing），但属于未测试的边界行为。
- **建议**：deferred 到后续 fixture 补充阶段。可新增一个只有 nav_growth_rate 的最小 fixture。

### N-3：`performance_without_investor_return.txt` 的 nav_benchmark_performance 未被显式断言

- **严重度**：non-blocking
- **文件/行号**：`tests/fund/extractors/test_performance.py:155-166`
- **现象**：`test_extract_performance_marks_missing_investor_return_without_silent_blank` 只断言了 `result.investor_return`，没有断言 `result.nav_benchmark_performance.extraction_mode == "direct"`。该 fixture 包含 `nav_growth_rate: 6.54%` 和 `benchmark_return_rate: 5.43%`，所以 `nav_benchmark_performance` 应为 direct，但未被显式验证。
- **建议**：在 test 4 中追加一行 `assert result.nav_benchmark_performance.extraction_mode == "direct"` 即可。成本极低，可在下次 fix pass 中补入。

---

## Residual Risks

| ID | 风险 | 影响 | 缓解建议 |
|---|---|---|---|
| RR-S5-1 | `estimated` 仅覆盖 §3 内显式标注"估算"口径的文本，不支持跨章节 fallback 计算（如 §10 份额变动推算） | P1-S5 范围内无影响；P2 需要 `investor_return.py` 分析模块接管 | 由 P1-S8 或 P2 对应 slice 接手，当前 `fallback_status="pending_later_slice"` 已显式标记 |
| RR-S5-2 | §3 整体缺失场景行为正确但未测试 | 若后续 refactor `_extract_field` 可能意外改变 missing 路径 | P1-S8 集成测试应包含 §3 缺失样本 |
| RR-S5-3 | `PerformanceExtractionResult` 尚未通过 `data_extractor.py` façade 对外装配 | 上层无法直接消费 | 由 P1-S8 façade 集成 slice 负责，当前 slice 不应触碰 |

---

## 审查清单总结

| 检查项 | 判定 | Blocking? |
|--------|------|-----------|
| 1. 严格只处理 §3 的 nav_benchmark_performance 与 investor_return | PASS | No |
| 2. investor_return 明确区分 direct/estimated/missing，无静默空字符串 | PASS | No |
| 3. 所有直接命中或估算口径命中都带 EvidenceAnchor | PASS | No |
| 4. 未越界到 documents/pdf/data_extractor/nav_data/其他 extractor | PASS | No |
| 5. estimated 停留在 P1 允许边界内，未偷跑 P2 分析公式 | PASS | No |
| 6. 中文 docstring、Capability 边界、测试满足 AGENTS.md | PASS | No |
| 7. 测试足以锁定当前 slice 正确性，无严重漏测 | PASS（含 3 项 non-blocking） | No |

**总判定：PASS — 0 blocking finding，3 non-blocking findings（N-1/N-2/N-3），均建议 deferred。**

---

*AgentGLM code review completed. Stop condition reached.*
