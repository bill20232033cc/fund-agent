# P1-S2 Code Review — AgentMiMo

> 日期：2026-05-17
> Reviewer：AgentMiMo
> Branch：`chore/reconcile-baseline`
> Target：P1-S2 章节定位修复与 §3 冻结
> Scope：仅 review 当前 worktree 中属于 P1-S2 的文件

## 审查输入

- Baseline：`docs/reviews/p1-s2-baseline-reconciliation-2026-05-17.md`
- Implementation：`docs/reviews/p1-s2-implementation-2026-05-17.md`
- Plan：`docs/reviews/p1-plan-2026-05-17.md`
- 设计真源：`docs/design.md`
- 总控真源：`docs/implementation-control.md`

## 审查范围

| 文件 | 类型 | 状态 |
|------|------|------|
| `fund_agent/fund/pdf/parser.py` | 修改 | 章节定位逻辑重写 |
| `fund_agent/fund/pdf/section_catalog.py` | 新增 | 配置化章节目录表 |
| `tests/fund/pdf/test_parser.py` | 新增 | 章节定位测试 |
| `tests/fixtures/fund/pdf_sections/110011_2024_excerpt.txt` | 新增 | 最小文本 fixture |

**排除确认**：
- `fund_agent/fund/documents/models.py` 未被修改（`git diff HEAD` 无输出），满足 P1-S2 禁止修改公开签名约束。
- 无 extractor / cache / repository / 上层目录文件变更。

## Review Checklist 逐项审查

### 1. 是否真正修复了 root cause，而不是样本特判

**结论：是，root cause 已修复。**

baseline 确认的两层 root cause：

1. **§3 标题规则写窄** — 旧规则 `^§3\\s+基金(?:主要财务指标|净值表现)` 只接受 "§3 后紧跟 基金…"，真实正文标题 "§3 主要财务指标、基金净值表现及利润分配情况" 不匹配。
   - 修复证据：`section_catalog.py:43-47` 新增三条 §3 模式，第一条 `r"^§3\s+主要财务指标.*基金净值表现.*$"` 直接匹配真实标题。
   - 不是特判：模式使用 `.*` 通配中间内容，可覆盖标题变体（如 "§3 主要财务指标、基金净值表现" 或 "§3 主要财务指标、基金净值表现及利润分配情况"）。

2. **目录过滤耦合在 `locate_sections()` 内部，仅依赖 `"..." in line`** — 无法配置化回归。
   - 修复证据：`section_catalog.py:83-86` 的 `TOC_LINE_PATTERNS` 收口了两种目录信号：点线/省略号类（`r"[\.·•…⋯]{2,}\s*\d+\s*$"`）和多空格+页码类（`r"\s{2,}\d+\s*$"`）。`parser.py:110-123` 的 `_is_toc_line()` 消费该配置。
   - 不是特判：规则表可扩展，不绑定特定基金代码或特定目录格式。

### 2. 章节规则是否已从 parser.py 逻辑内联迁到 section_catalog

**结论：是。**

- `parser.py:17-24`：`_COMPILED_SECTION_PATTERNS` 和 `_COMPILED_TOC_PATTERNS` 均从 `section_catalog.py` 的 `SECTION_CATALOG` 和 `TOC_LINE_PATTERNS` 编译而来，parser.py 内部不再有硬编码的章节正则。
- `section_catalog.py`：用 `SectionCatalogEntry` dataclass 收口 `§1/§2/§3/§4/§5/§8/§9/§10` 的标题变体模式。
- parser.py 中无残留的旧 `SECTION_PATTERNS` 字典。

### 3. 目录误判过滤是否从单一 "..." 规则升级为可复用规则

**结论：是。**

- 旧实现：`"..." in line` 单一字符串匹配。
- 新实现：`_is_toc_line()`（parser.py:110-123）消费 `_COMPILED_TOC_PATTERNS`，支持两种正则：
  - `[\.·•…⋯]{2,}\s*\d+\s*$` — 覆盖英文省略号、中文间隔号、数学省略号等点线类目录引导符 + 页码
  - `\s{2,}\d+\s*$` — 覆盖多空格对齐 + 页码的目录行格式
- fixture 中 §3 使用 `…`、§4 使用多空格、§8 使用 `·`，三种目录格式均被正确过滤（测试验证 offset 指向正文而非目录行）。

### 4. 110011/2024 的 §3 回归是否被 fixture + test 稳定覆盖

**结论：是。**

- Fixture `tests/fixtures/fund/pdf_sections/110011_2024_excerpt.txt` 同时表达：
  - 目录页中的 "§3 主要财务指标、基金净值表现及利润分配情况 ………………… 7"
  - 正文中的同名 "§3 主要财务指标、基金净值表现及利润分配情况"
  - §4 使用"多空格 + 页码"目录形式
  - §8 使用"点线符号 + 页码"目录形式
- 测试覆盖：
  - `test_locate_sections_finds_required_sections_for_110011_2024_fixture`：断言 §1-§10 全部命中，且 `extract_section(text, "§3")` 返回正确正文内容。
  - `test_locate_sections_skips_toc_entries_without_relying_on_dot_leader_only`：断言 §3/§4/§8 的 offset 指向正文行而非目录行。
  - `test_locate_sections_returns_monotonic_offsets_for_required_sections`：断言 §1-§10 偏移严格单调递增。
- 测试结果：3 passed in 0.12s。

### 5. 偏移单调递增、公开签名不变、无越界

**结论：全部满足。**

- **偏移单调递增**：`test_locate_sections_returns_monotonic_offsets_for_required_sections` 断言 `start_offset > previous_start` 且 `start_offset < end_offset`。
- **公开签名不变**：
  - `locate_sections(text: str) -> dict[str, tuple[int, int]]` — 未变
  - `extract_section(text: str, section_id: str) -> str | None` — 未变
  - `extract_text(pdf_path: Path) -> str` — 未变
  - `extract_tables(pdf_path: Path) -> list[dict[str, object]]` — 未变
  - `models.py` 无 diff 输出
- **无越界**：
  - 无 extractor / cache / repository / 上层目录文件变更
  - `grep -rn "from fund_agent.fund.pdf" fund_agent/fund/documents/ fund_agent/fund/extractors/` 无输出（仅 adapter 按设计依赖 pdf）

### 6. 是否满足 AGENTS.md 的中文 docstring、边界、测试约束

**结论：满足。**

- **中文 docstring**：`parser.py` 所有函数（`_normalize_text`、`_iter_text_lines`、`_is_toc_line`、`_collect_section_candidates`、`_select_section_starts`、`extract_text`、`extract_tables`、`locate_sections`、`extract_section`）和内部 dataclass（`_TextLine`、`_SectionCandidate`）均有完整中文 docstring。`section_catalog.py` 的 `SectionCatalogEntry` 和模块级 docstring 均为中文。
- **边界**：parser.py 仍属 Capability 内部 PDF helper，未越界到上层。
- **测试**：3 个测试覆盖了核心场景（§3 命中、目录误判过滤、偏移单调递增），与 fixture 配合形成稳定回归。

## Findings

### 1-未修复-低-§5 章节规则缺失但不在 P1-S2 验收标准内

- **文件(行号)**：`fund_agent/fund/pdf/section_catalog.py:55-59`
- **直接证据**：`SECTION_CATALOG` 包含 §5 条目（`r"^§5\s+托管人报告\s*$"`），但 fixture `110011_2024_excerpt.txt` 中未包含 §5 正文行。测试 `_REQUIRED_SECTION_IDS` 也不包含 §5。
- **影响**：§5 在 P1 直接依赖章节列表（`docs/design.md:311`）中出现，但当前 fixture 未验证其定位。不过 §5 的定位逻辑与 §4/§8 一致（单模式匹配），风险极低。
- **建议改法**：后续样本回归时补充 §5 到 fixture 和 `_REQUIRED_SECTION_IDS`。不阻塞 P1-S2。
- **验证点**：fixture 中增加 §5 目录行和正文行。
- **严重程度**：低 — §5 规则已存在，仅缺 fixture 覆盖。

## P1-S2 计划符合性检查

| 完成信号 | 状态 | 证据 |
|---|---|---|
| 章节规则从 parser.py 内联迁到 section_catalog | ✓ | `section_catalog.py` 承载 `SECTION_CATALOG` + `TOC_LINE_PATTERNS`，parser.py 无残留硬编码正则 |
| `110011/2024` §3 稳定命中 | ✓ | fixture + `test_locate_sections_finds_required_sections_for_110011_2024_fixture` 验证 |
| 目录误判过滤升级为可复用规则 | ✓ | `TOC_LINE_PATTERNS` 覆盖点线类和多空格+页码类目录格式 |
| 偏移单调递增 | ✓ | `test_locate_sections_returns_monotonic_offsets_for_required_sections` 验证 |
| 公开签名不变 | ✓ | 4 个公开函数签名均未变，`models.py` 无 diff |
| 无基金代码级硬编码特判 | ✓ | 所有规则基于标题模式匹配，不绑定基金代码 |

## Residual Risk

1. **更多年报标题变体**：当前 `SECTION_CATALOG` 覆盖了已知的主要标题变体，但不同基金公司可能使用不同的 § 编号格式或标题措辞。需在后续样本回归中持续补充。不阻塞 P1-S2。
2. **目录过滤误判边界**：当前 `TOC_LINE_PATTERNS` 覆盖了点线类和多空格+页码类目录格式，但若年报使用其他目录格式（如制表符对齐），可能需要扩展。当前 3 种目录格式的 fixture 覆盖已足够。
3. **§5 fixture 缺失**：§5 已有规则但无 fixture 覆盖（Finding 1），风险极低。

## 结论

**结论：pass，无 blocking finding。**

P1-S2 的核心目标（root cause 修复、规则配置化、目录误判升级、§3 回归冻结）全部达成。实现质量良好：职责拆分清晰（`section_catalog` 配置 + `parser` 算法）、测试覆盖了关键场景、fixture 表达了真实的目录+正文同名边界情况。

1 个低严重程度 finding（§5 fixture 缺失），不阻塞 gate。
