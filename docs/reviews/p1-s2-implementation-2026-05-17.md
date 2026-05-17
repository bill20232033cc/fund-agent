# P1-S2 Implementation Artifact

> 日期：2026-05-17
> gate：`P1-S2 implementation`
> slice：`P1-S2 章节定位修复与 §3 冻结`
> 分支：`chore/reconcile-baseline`

## Scope / Non-Goals

### Scope

- 把 `locate_sections()` 从硬编码正则 + 内联目录过滤，改为消费配置化章节目录表。
- 关闭 `BQ-5`：让 `110011/2024` 的 `§3` 标题变体被稳定命中。
- 为目录页误识别和关键章节偏移顺序补上可重复的 fixture 与测试。

### Non-Goals

- 不修改 `FundDocumentRepository` 公开签名。
- 不进入 extractor、缓存层、P1-S3 或上层目录。
- 不引入 OCR / 图像识别。
- 不做基金代码级硬编码特判。

## Changed Files

- `fund_agent/fund/pdf/parser.py`
- `fund_agent/fund/pdf/section_catalog.py`
- `tests/fund/pdf/test_parser.py`
- `tests/fixtures/fund/pdf_sections/110011_2024_excerpt.txt`

## Implemented Items

1. 新增 `fund_agent/fund/pdf/section_catalog.py`
   - 用 `SectionCatalogEntry` 收口章节标题规则。
   - 把 `§1/§2/§3/§4/§5/§8/§9/§10` 的标题变体迁出 `parser.py`。
   - 把目录行识别信号收口为 `TOC_LINE_PATTERNS`，覆盖：
     - 点线 / 省略号类目录引导符
     - 多空格 + 页码结尾的目录行
2. 改造 `fund_agent/fund/pdf/parser.py`
   - 保持 `locate_sections(text) -> dict[str, tuple[int, int]]` 与 `extract_section(...)` 的公开签名不变。
   - 新增 `_iter_text_lines()`、`_is_toc_line()`、`_collect_section_candidates()`、`_select_section_starts()`，把“扫描文本行 -> 过滤目录项 -> 选择正文首命中 -> 生成单调区间”拆成可测试内部步骤。
   - `§3` 规则从原先只接受“§3 后紧跟 基金...”扩展为允许：
     - `§3 主要财务指标、基金净值表现及利润分配情况`
     - `§3 基金主要财务指标...`
     - `§3 基金净值表现...`
3. 新增最小文本 fixture
   - `tests/fixtures/fund/pdf_sections/110011_2024_excerpt.txt`
   - 同时表达：
     - 目录页中的 `§3 主要财务指标、基金净值表现及利润分配情况`
     - 正文中的同名 `§3` 标题
     - `§4` 使用“多空格 + 页码”目录形式
     - `§8` 使用“点线符号 + 页码”目录形式
4. 新增 `tests/fund/pdf/test_parser.py`
   - 覆盖正文 `§3` 命中
   - 覆盖目录误判回归，不再依赖单一 `"..."` 规则
   - 覆盖 `§1/§2/§3/§4/§8/§9/§10` 偏移单调递增

## Validation

执行命令：

```bash
.venv/bin/python -m pytest tests/fund/pdf/test_parser.py -q
```

结果：

```text
3 passed in 0.13s
```

## Root Cause Closure

- 已关闭的 root cause：
  1. `§3` 标题规则写窄，只接受“§3 后紧跟 基金...”。
     - 现已配置化扩展到真实正文标题 `§3 主要财务指标、基金净值表现及利润分配情况`。
  2. 目录过滤耦合在 `locate_sections()` 内，仅依赖 `"..." in line`。
     - 现已升级为可复用规则表 `TOC_LINE_PATTERNS` 与 `_is_toc_line()`。
- 关闭证据：
  - `110011_2024_excerpt.txt` fixture 中正文 `§3` 被稳定命中。
  - 同名目录 `§3`、`§4`、`§8` 条目不会被误当正文。
  - 关键章节 `§1/§2/§3/§4/§8/§9/§10` 偏移单调递增。

## Residual Risks

### Fixed Later Slice

- 当前章节目录表仍只覆盖 P1 直接依赖的主要章节，更多年报标题变体需要在后续样本回归中继续补充。

### Later Phase

- 章节定位目前仍基于纯文本匹配，不包含表格语义、证据锚点或缓存物化逻辑。
- `§3` 定位已冻结，但后续 `§3` 结构化字段提取仍需在 P1-S5 落地。

### User Decision

- 无。

## Completion Status

- `P1-S2` completion signal：`reached`
- 判断依据：
  - `locate_sections()` 已改为消费配置化 `section_catalog`
  - `BQ-5` 已关闭：最小事实夹具可稳定命中 `110011/2024` 的正文 `§3`
  - 目录误识别存在回归测试
  - `§1/§2/§3/§4/§8/§9/§10` 在夹具中定位成功且偏移单调递增
