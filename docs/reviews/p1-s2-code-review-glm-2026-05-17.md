# P1-S2 Code Review (GLM)

> 日期：2026-05-17
> Reviewer：AgentGLM
> Phase / Slice：P1 / P1-S2 章节定位修复与 `§3` 冻结
> 分支：`chore/reconcile-baseline`
> Review scope 裁决：`docs/reviews/p1-s2-baseline-reconciliation-2026-05-17.md`
> 已接受 plan：`docs/reviews/p1-plan-2026-05-17.md`
> 设计/总控真源：`docs/design.md`、`docs/implementation-control.md`

---

## 1. Review 结论

**PASS** — P1-S2 核心目标全部达成，无 blocking finding。

Root cause（`§3` 标题正则写窄 + 目录过滤单一 `"..."` 规则）已被真正修复，不是样本特判。章节规则已配置化迁出到 `section_catalog.py`，目录误判过滤已升级为可复用规则表，`110011/2024` 的 `§3` 定位被 fixture + test 稳定覆盖。

存在 3 项 non-blocking findings（0 medium / 1 low / 2 informational），均不影响当前 slice 正确性。

---

## 2. 审查范围

| 文件 | 状态 |
|------|------|
| `fund_agent/fund/pdf/parser.py` | 修改 |
| `fund_agent/fund/pdf/section_catalog.py` | 新增 |
| `tests/fund/pdf/test_parser.py` | 新增 |
| `tests/fixtures/fund/pdf_sections/110011_2024_excerpt.txt` | 新增 |

---

## 3. Root Cause 修复验证

### 3.1 Root Cause 1：`§3` 标题正则写窄

**原始缺陷**（baseline reconciliation 3.2）：
- `SECTION_PATTERNS["§3"]` 要求 `§3` 后紧跟 `基金…`，但真实正文标题是 `§3 主要财务指标、基金净值表现及利润分配情况`，不匹配。

**修复证据**：
- `section_catalog.py:42-48`：`§3` 现有 3 条 heading_patterns：
  - `r"^§3\s+主要财务指标.*基金净值表现.*$"` — 直接匹配 110011/2024 真实正文标题
  - `r"^§3\s+基金主要财务指标.*$"` — 覆盖"基金"开头的变体
  - `r"^§3\s+基金净值表现.*$"` — 覆盖简化标题
- 规则是**基于标题格式变体的配置化扩展**，不是 `if fund_code == "110011"` 特判。✅
- 不依赖 OCR / 图像识别。✅

**判定**：root cause 已修复。

### 3.2 Root Cause 2：目录过滤仅依赖 `"..." in line`

**原始缺陷**（baseline reconciliation 3.2）：
- 目录过滤只检查 `"..." in line`，无法处理无点线的目录条目。

**修复证据**：
- `section_catalog.py:83-86`：`TOC_LINE_PATTERNS` 收口为两条可复用规则：
  - `r"[\.·•…⋯]{2,}\s*\d+\s*$"` — 点线/中点/省略号引导符 + 页码
  - `r"\s{2,}\d+\s*$"` — 多空格 + 页码结尾
- `parser.py:110-123`：`_is_toc_line()` 消费 `TOC_LINE_PATTERNS`，可扩展。
- Fixture 中 `§4` 使用多空格+页码目录格式（`:7`），`§8` 使用中点引导符（`:8`），覆盖了两种 TOC 模式。✅

**判定**：root cause 已修复。

---

## 4. 逐项合规核查

### 4.1 章节规则已从 parser.py 迁到 section_catalog

| 检查项 | 结果 | 证据 |
|--------|------|------|
| parser.py 无内联硬编码章节字典 | ✅ | `parser.py:13` 仅 import `SECTION_CATALOG` 和 `TOC_LINE_PATTERNS`；`parser.py:17-20` 从 catalog 编译 |
| section_catalog.py 承载所有规则 | ✅ | `§1/§2/§3/§4/§5/§8/§9/§10` 共 8 个 `SectionCatalogEntry`（`:26-81`） |
| 规则可扩展 | ✅ | 新增章节变体只需在 catalog 中加条目或加 pattern |

### 4.2 目录误判过滤不依赖单一规则

| 检查项 | 结果 | 证据 |
|--------|------|------|
| TOC 规则覆盖点线引导 | ✅ | `section_catalog.py:84`，fixture `§3`/`§8`/`§9`/`§10` 使用此格式 |
| TOC 规则覆盖多空格+页码 | ✅ | `section_catalog.py:85`，fixture `§4` 使用此格式 |
| `_is_toc_line()` 可复用 | ✅ | `parser.py:110-123`，独立函数，消费配置化 pattern 列表 |
| 不再存在 `"..." in line` 旧逻辑 | ✅ | grep 确认 parser.py 无旧代码残留 |

### 4.3 110011/2024 §3 回归覆盖

| 检查项 | 结果 | 证据 |
|--------|------|------|
| Fixture 存在且表达"目录+正文同名" | ✅ | `110011_2024_excerpt.txt` 第 6 行（目录 §3）与第 19 行（正文 §3）同名 |
| 测试断言 §3 命中 | ✅ | `test_parser.py:47-55`，`_REQUIRED_SECTION_IDS` 包含 `§3` 且顺序断言 |
| 测试断言 §3 偏移指向正文 | ✅ | `test_parser.py:76`，`sections["§3"][0] == text.index("§3 主要财务指标...")` 精确匹配正文位置 |

### 4.4 偏移单调递增

| 检查项 | 结果 | 证据 |
|--------|------|------|
| 公开签名不变 | ✅ | `locate_sections(text) -> dict[str, tuple[int, int]]`（`:245`），`extract_section(text, section_id) -> str | None`（`:271`） |
| 偏移单调测试存在 | ✅ | `test_parser.py:81-103`，遍历 `_REQUIRED_SECTION_IDS` 断言 `start < end` 且 `start > previous_start` |

### 4.5 无越界

| 检查项 | 结果 | 证据 |
|--------|------|------|
| parser.py 无 repository/extractor/cache 引用 | ✅ | grep 确认无相关 import |
| section_catalog.py 无外部依赖 | ✅ | 仅依赖 `dataclass`、`typing` |
| 无上层目录依赖 | ✅ | 所有 import 限 `fund_agent.fund.pdf` 内部 |
| `documents/models.py` 未修改 | ✅ | 非 P1-S2 允许文件，无 diff |

### 4.6 AGENTS.md 合规

| 检查项 | 结果 | 证据 |
|--------|------|------|
| 所有公共/私有函数有中文 docstring | ✅ | 逐函数检查 `parser.py` 和 `section_catalog.py` |
| Docstring 包含 Args/Returns/Raises | ✅ | 所有函数均包含三段式 |
| 无嵌套函数 | ✅ | 所有辅助函数为模块级（`_iter_text_lines`、`_is_toc_line`、`_collect_section_candidates`、`_select_section_starts`） |
| 章节规则配置化，非硬编码 | ✅ | `SectionCatalogEntry` dataclass + `SECTION_CATALOG` tuple |

---

## 5. Findings

### 5.1 F1-未修复-Low-_collect_section_candidates 嵌套 break/continue 逻辑可读性差

**文件与行号**：`fund_agent/fund/pdf/parser.py:143-161`

**直接证据**：
```python
for section_id, patterns in _COMPILED_SECTION_PATTERNS.items():
    for pattern in patterns:
        if not pattern.match(line.normalized_text):
            continue
        if _is_toc_line(line.normalized_text):
            break
        candidates.append(...)
        break
    else:
        continue
    break
```

该段使用 `for-else` + 嵌套 `break` 控制流：外层遍历 section_id，内层遍历 pattern；匹配后根据是否为 TOC 行决定 append 或跳过，并通过 `for-else` + 外层 `break` 确保每行最多匹配一个 section。

逻辑正确，但可读性差。需要读者完全理解 Python `for-else` 语义才能验证正确性。

**影响**：后续维护者修改章节匹配逻辑时容易引入 bug（如误删 `else: continue` 导致 TOC 行泄漏为正文候选）。

**建议改法**：
- 将内层匹配逻辑提取为独立函数 `_match_line_to_section(line) -> _SectionCandidate | None`，将控制流从双层循环中解耦。
- 或在当前代码处加一行注释说明意图。

**验证点**：
- 重构后 fixture 测试应全部通过。
- 新增测试用例：正文标题行匹配后不再尝试匹配其它 section。

---

### 5.2 F2-未修复-Informational-测试未覆盖负向与边界场景

**文件与行号**：`tests/fund/pdf/test_parser.py`

**直接证据**：

当前 3 条测试全部基于同一份正面 fixture：
- `test_locate_sections_finds_required_sections_for_110011_2024_fixture`
- `test_locate_sections_skips_toc_entries_without_relying_on_dot_leader_only`
- `test_locate_sections_returns_monotonic_offsets_for_required_sections`

未覆盖的负向/边界场景：
- 空文本输入
- 仅含目录条目、无正文标题的文本
- 同一章节在正文中出现多次（如"回溯"或"引用"场景）
- 未在 catalog 中定义的章节编号

**影响**：
- P1-S2 完成信号（`§3` 命中 + TOC 过滤 + 偏移单调）已被充分验证。
- 但负向场景缺失意味着后续修改可能在边界处引入回归而不被发现。

**建议改法**：
- P1-S3 或后续 slice 中补充最小负向测试，至少覆盖空输入和纯目录文本。

**验证点**：
- `locate_sections("")` 应返回空 dict。
- `locate_sections(纯目录文本)` 应返回空 dict。

---

### 5.3 F3-未修复-Informational-§3 heading_patterns 使用 .* 贪婪通配

**文件与行号**：`fund_agent/fund/pdf/section_catalog.py:43`

**直接证据**：
```python
r"^§3\s+主要财务指标.*基金净值表现.*$",
```

`.*` 可匹配任意中间文本。理论上存在误匹配风险（如正文中出现 `§3 主要财务指标备注：本基金净值表现说明...` 之类的非标题行）。

**影响**：极低。`^`/`$` 锚定 + `§3` 前缀 + 关键词约束已足够窄，实际年报格式中几乎不会触发误匹配。

**建议改法**：
- 当前可接受。若后续样本回归中出现误匹配，可将 `.*` 收窄为 `[^,\n]*` 或类似约束。

**验证点**：
- 无需立即行动，记录为已知 residual risk。

---

## 6. 残余风险

| ID | 风险 | 影响范围 | 建议处理时机 |
|----|------|---------|-------------|
| RR-S2-1 | 更多年报标题变体未在当前 catalog 中覆盖 | 后续样本回归 | P1-S4~S7 提取阶段遇到时补充 |
| RR-S2-2 | 负向/边界测试缺失 | 回归保护力 | P1-S3 补充 |

---

## 7. 汇总

| Finding 编号 | 严重程度 | Blocking? | 建议处理 |
|-------------|---------|-----------|---------|
| F1 | Low | 否 | 后续重构时改善可读性 |
| F2 | Informational | 否 | P1-S3 补充负向测试 |
| F3 | Informational | 否 | 记录为已知 risk |

**总 findings 数量**：3（0 blocking / 0 medium / 1 low / 2 informational）
**Blocking accepted candidate**：无
**Artifact path**：`docs/reviews/p1-s2-code-review-glm-2026-05-17.md`
