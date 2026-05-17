# P1-S2 基线对账裁决

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P1 / P1-S2 章节定位修复与 `§3` 冻结
> 分支：`chore/reconcile-baseline`
> 当前 gate：`P1-S2 implementation + review`
> 上一 accepted slice commit：`e772dae` (`gateflow: accept P1 P1-S1`)

## 1. 触发原因

- `docs/implementation-control.md` 已把 `P1-S1` 标记为完成，下一 entry point 明确切到 `P1-S2 章节定位修复与 §3 冻结`。
- `docs/reviews/p1-plan-2026-05-17.md` 第 8.2 节要求 `P1-S2` 关闭 `BQ-5`：样本基金 `110011` 的 2024 年报必须稳定定位出 `§3`。
- `P1-S2` 是后续 `§3` 表现提取、投资者收益 fallback、结构化提取冻结前的直接前置，不能继续带着章节定位缺陷向后推进。

## 2. 基线事实

### 2.1 当前 worktree 安全状态

当前 `git status --short` 仅剩与本 gate 无关的未跟踪文件：

```text
?? docs/reviews/code-review-20260517-0727.md
?? scripts/
```

裁决：

- 这两项不纳入 `P1-S2` 范围。
- 当前 `P1-S2` 可以安全基于 `HEAD=e232c3d` 继续推进。

### 2.2 当前代码实现事实

当前 `fund_agent/fund/pdf/parser.py` 的直接事实：

- `SECTION_PATTERNS` 仍为单文件硬编码字典，位于 [parser.py](/Users/maomao/fund-agent/fund_agent/fund/pdf/parser.py:12)。
- `SECTION_PATTERNS["§3"]` 当前仅覆盖：
  - `^§3\\s+基金(?:主要财务指标|净值表现)`
  - `^§3\\s+基金净值`
- `locate_sections()` 仍采用：
  - 对每个章节“命中第一个符合 pattern 的非目录行后即 break”
  - 目录过滤只依赖 `"..." in line`

### 2.3 真实样本取证

对 `cache/pdf/110011_2024_annual_report.pdf` 的真实取证结果：

- 当前 `locate_sections()` 返回：

```text
['§1', '§10', '§2', '§4', '§5', '§8', '§9']
```

- `§3` 当前未命中。
- 但提取后的全文中同时存在：
  - 目录行：`§3 主要财务指标、基金净值表现及利润分配情况 ............................................................................... 7`
  - 正文行：`§3 主要财务指标、基金净值表现及利润分配情况`

按章节行序列观察，正文区的 `§3` 位于：

```text
100: §2 基金简介
184: §3 主要财务指标、基金净值表现及利润分配情况
249: §4 管理人报告
```

## 3. Root Cause 裁决

### 3.1 已排除的错误方向

- 不是 OCR / 图像识别问题：
  - 正文标题已被 `pdfplumber` 正常抽出。
- 不是“只有目录没有正文”的 PDF 噪声问题：
  - 正文标题真实存在。
- 不是 `P1-S1` 文档仓库边界问题：
  - `FundDocumentRepository` 已稳定，当前缺陷集中在 `parser.py` 的章节规则与目录过滤。

### 3.2 当前 root cause

当前 `§3` 漏识别的直接 root cause 有两层：

1. `SECTION_PATTERNS["§3"]` 写窄了：
   - 当前规则要求 `§3` 标题在“§3 ”后紧跟“基金…”
   - 真实正文标题是 `§3 主要财务指标、基金净值表现及利润分配情况`
   - 因此正文标题根本不匹配当前正则

2. 章节规则与目录过滤耦合在 `locate_sections()` 内部，无法配置化回归：
   - 目前没有 `section_catalog.py`
   - 没有 `tests/fund/pdf/test_parser.py`
   - 没有 `tests/fixtures/fund/pdf_sections/**`
   - 这意味着即便临时补一个正则，也没有稳定的回归护栏去防止目录误判和后续章节变体回退

## 4. P1-S2 范围裁决

### 4.1 本轮允许文件

按已接受 plan，第 8.2 节 `P1-S2` 的 allowed scope 为：

- `fund_agent/fund/pdf/parser.py`
- `fund_agent/fund/documents/models.py`
- `fund_agent/fund/pdf/section_catalog.py`
- `tests/fund/pdf/test_parser.py`
- `tests/fixtures/fund/pdf_sections/**`

### 4.2 当前建议的最小实现范围

controller 裁决本轮最小必要落地为：

- `fund_agent/fund/pdf/section_catalog.py`
  - 收口章节别名、目录过滤信号、匹配规则
- `fund_agent/fund/pdf/parser.py`
  - 改造 `locate_sections()` 使用配置化 catalog，而非本地硬编码字典
  - 保持公开签名不变
- `tests/fund/pdf/test_parser.py`
  - 覆盖：
    - `110011` 类 `§3` 标题正文命中
    - 目录页误识别回归
    - 偏移单调递增
- `tests/fixtures/fund/pdf_sections/**`
  - 至少提供能复现“目录行 + 正文行同名”的最小文本 fixture

### 4.3 当前不建议触碰

- `fund_agent/fund/documents/models.py`
  - 当前不需要为了 `P1-S2` 修改公共模型
- 任意 extractor / cache / 上层目录
- `FundDocumentRepository` 对外公开签名

## 5. 当前结论

- baseline reconciliation 结论：`pass`
- `P1-S2` 可以直接进入 implementation
- controller 对本轮的额外约束：
  - 不接受基金代码级硬编码特判
  - 不接受“只补一条 `§3` 正则但不落测试 / fixture / section catalog”的半修复
  - `110011`/2024 必须作为回归事实存在于测试证据中，但可以通过最小文本 fixture 表达，不要求测试直接解析真实 PDF

## 6. 后续执行约束

- `AgentCodex` 负责：
  - 只在 `P1-S2` 允许文件内完成实现
  - 输出 durable implementation artifact
  - 不 commit、不 push、不进入下一 gate
- `AgentMiMo` 与 `AgentGLM` 负责：
  - 基于最终 worktree 做独立 code review / re-review
  - 重点检查是否真修 root cause、是否配置化、是否避免目录误判、是否无样本特判
- controller 负责：
  - 对 findings 做 accepted / rejected / deferred 裁决
  - 必要时继续 `fix -> re-review`
  - 通过后再更新 `docs/implementation-control.md`
