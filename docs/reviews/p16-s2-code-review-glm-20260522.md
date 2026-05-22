# P16-S2 Code/Evidence Review — AgentGLM（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

Implementation artifact `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md` 正确触发了 stop condition 并在 golden 编辑前停止。阻断有效，未修改任何 production 文件。Artifact 可被 controller 接受。

## Inputs

| Artifact | Role |
|---|---|
| `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md` | Implementation artifact under review |
| `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md` | Accepted plan |
| `docs/reviews/p16-s2-plan-review-controller-judgment-20260522.md` | Accepted controller judgment |
| `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md` | Accepted P16-S1 evidence |
| `docs/reviews/p16-s1-code-review-controller-judgment-20260522.md` | Accepted P16-S1 evidence judgment |
| `docs/design.md` | Design truth |
| `docs/implementation-control.md` | Control truth |
| `AGENTS.md` | Agent execution rules |

Excluded inputs not read or cited: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`, excluded audit inputs.

## Review Focus 1: Blocker Validity Under Accepted Stop Conditions

Plan stop condition (plan artifact line 309):

> 当前 extractor 输出不同于 P16-S1 accepted values for any candidate → must stop before golden edits.

Implementation artifact 复核命令使用 `FundDocumentRepository` + `extract_profile()` 读取 2024 年报，直接比较五只基金的 `benchmark_text`。结果：

| fund_code | status | 差异性质 |
|---|---|---|
| `004194` | `TEXT_OK` | — |
| `005313` | `TEXT_OK` | — |
| `017644` | `TEXT_DIFF` | 当前 extractor 输出含嵌入 `\n`：`...活期存款利\n率(税后)...`，P16-S1 计划值为 `...活期存款利率(税后)...` |
| `019918` | `TEXT_DIFF` | 当前 extractor 输出含嵌入 `\n`：`...利率（税后）\n*5%`，P16-S1 计划值为 `...利率（税后）*5%` |
| `019923` | `TEXT_OK` | — |

**代码验证**：`fund_agent/fund/extractors/profile.py` line 441 将 `matched_field.value` 直接存入 `benchmark_text`；line 571 仅做 `str(value).strip()` 清理首尾空白，**不处理嵌入换行**。PDF 表格文本跨行时，extractor 保留原始换行符是符合代码行为的预期结果。

**结论**：blocker 有效。两处 text diff 均为真实的 extractor 输出差异，触发 plan 的 stop condition 是正确的第一性原理判断。

**严重性**：`medium`。不是实现错误，而是 extractor 对 PDF 表格跨行文本的处理方式与 P16-S1 计划中记录的值存在差异。需要决定：normalize extractor 输出还是更新 golden 预期值。

## Review Focus 2: Evidence Check Stayed Through FundDocumentRepository/extract_profile Boundary

复核命令（implementation artifact lines 31-69）：

```python
repo = FundDocumentRepository()
report = await repo.load_annual_report(code, 2024, force_refresh=False)
profile = extract_profile(report).index_profile
value = profile.value
```

- 使用 `FundDocumentRepository.load_annual_report()` — 符合 `AGENTS.md` 对年报访问的硬约束（文档仓库接口）。
- 使用 `extract_profile()` 从 `ParsedAnnualReport` 提取 `index_profile` — 符合 Capability 层边界。
- `force_refresh=False` — 不触发外部重下载，符合 evidence 复核语义。
- 未注入空 `nav_provider`（与 P16-S1 evidence gate 不同），但 `extract_profile` 不依赖净值数据，所以不影响结果正确性。
- 读取 `profile.anchors[0]` 做 source provenance 检查 — 正确使用 extractor 输出结构。

**结论**：evidence check 完全在 `FundDocumentRepository` / `extract_profile` 边界内完成，未绕过或直接访问 PDF cache / source adapters / 下载 helpers。符合 `AGENTS.md` 模块边界规则。

## Review Focus 3: Text Diffs Are Real and Material

**真实性验证**：

1. Extractor 代码路径确认 `benchmark_text` 来自 `_extract_field(report, "benchmark")` 的 `matched_field.value`，仅做 `.strip()` 处理。
2. PDF 年报表格在渲染"业绩比较基准"时跨行是常见的 PDF 排版行为（017644 和 019918 的 page-6 / page-5 benchmark 行）。
3. P16-S1 evidence artifact 中记录的 `benchmark_text` 不含换行——说明 P16-S1 可能是在不同的 PDF 解析缓存状态或人工整理时去除了换行。

**实质性验证**：

- `017644`：`利\n率` → 纯排版换行，语义内容完全一致。
- `019918`：`（税后）\n*5%` → 纯排版换行，语义内容完全一致。

两处差异均为 PDF 表格跨行导致的嵌入换行，**语义等价但字符串不等**。因为 golden correctness 比对是精确字符串匹配，这个差异在 golden 上下文中是 material 的——如果不解决，strict golden 行的 `expected_value` 会与 extractor 实际输出不匹配，导致 correctness 误报。

**结论**：text diffs 真实且在 golden correctness 上下文中 material。

## Review Focus 4: No Golden/Source/Test Changes Were Made

验证命令（implementation artifact lines 147-181）：

| 检查 | 结果 |
|---|---|
| conflict marker grep (`rg -n "^(<<<<<<<|=======|>>>>>>>)"`) | exit 1, 无输出 — 无 conflict marker |
| trailing whitespace grep (`rg -n "[ \t]+$"`) | exit 1, 无输出 — 无行尾空白 |
| `git diff --check HEAD` | exit 0, 无输出 |
| `git diff --name-only HEAD` | 无输出 — 无 tracked file 变更 |
| `git status --short` | 仅四个 untracked 文件（三个 pre-existing excluded + 本 artifact） |
| `git diff -- reports/golden-answers/ tests/fund/test_golden_answer.py ...` | exit 0, 无输出 — golden 和 targeted tests 未被修改 |

**结论**：确认未修改任何 golden Markdown、strict JSON、source code、tests、README、selected CSV、RR-13、design.md 或 implementation-control.md。

## Review Focus 5: Validation Adequacy

### 已执行的验证

| 验证项 | 充分性 |
|---|---|
| Plan/controller review | 充分 — 读取完整 plan 和 controller judgment |
| Code inspection（golden-build、comparable、snapshot、score、quality-gate、extractor） | 充分 — 确认了 golden-build 命令形态、comparable 白名单、extractor 行为 |
| Extractor stop-condition check（五只基金实际输出） | 充分 — 命中了 blocker |
| Conflict marker / trailing whitespace / `git diff --check` | 充分 — 满足 controller judgment 要求的显式 artifact 检查 |
| `git diff --name-only HEAD` + `git status` | 充分 — 确认无 production 变更 |

### 未执行但合理跳过的验证

| 验证项 | 跳过理由 | 评判 |
|---|---|---|
| `golden-build` | blocker 后未编辑 golden Markdown，不需要 rebuild | 合理 |
| Targeted tests (`test_golden_answer.py` 等) | 未添加/修改 tests，不改变 test baseline | 合理 |
| `ruff check` | 未修改 source code | 合理 |
| Full `pytest` | 未修改任何代码或测试 | 合理 |

**结论**：验证充分。所有 blocker 前的验证步骤执行完整，blocker 后跳过的验证步骤有合理理由。

## Findings

### F1 — Blocker 有效且 stop condition 执行正确

**Severity**: info（正面确认）

Implementation artifact 正确识别了两处 `benchmark_text` 嵌入换行差异，并按 plan stop condition 在 golden 编辑前停止。这是 fail-closed 行为的预期结果。

### F2 — 嵌入换行差异需要明确的 resolution 策略

**Severity**: medium

**Impact**：阻断 P16-S2 golden 实施进度。

**Evidence**：
- `017644` 当前输出 `...活期存款利\n率(税后)...` vs 计划值 `...活期存款利率(税后)...`
- `019918` 当前输出 `...利率（税后）\n*5%` vs 计划值 `...利率（税后）*5%`
- Extractor 代码 (`profile.py:571`) 仅做 `.strip()`，不 collapse 内部换行

**Disposition**：需要下一个 reviewed plan 决定以下之一：
1. 在 extractor profile path 中 normalize `benchmark_text`（collapse 内部 whitespace/newlines），然后重新复核五只基金输出，确认与 P16-S1 计划值一致后继续 golden 实施。
2. 更新 P16-S2 plan 中的 `benchmark_text` expected values 为含换行的当前 extractor 输出，并确认 golden correctness 路径能处理含换行的 `expected_value`。
3. 如果 normalize，需确认 normalize 行为不会影响其他 `benchmark_text` 的语义（例如包含有意换行的 benchmark text）。

### F3 — P16-S1 与 P16-S2 evidence 记录的 benchmark_text 值需对齐

**Severity**: low

**Impact**：如果选择 normalize extractor，需要同步更新 P16-S1 evidence artifact 中的记录以反映 normalize 后的值，避免 future review 出现 evidence chain 不一致。

**Evidence**：P16-S1 evidence artifact 记录的 `017644` benchmark_text 为 `中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%`（无换行），但当前 extractor 输出含换行。两份 artifact 记录的是同一 extractor 在（可能）不同时间/缓存状态下的输出。

### F4 — 实现范围约束完全遵守

**Severity**: info（正面确认）

Implementation artifact 正确遵守了所有 scope 约束：
- 未添加任何 golden rows（包括 `benchmark_index_name`、`tracking_error` 等 plan 明确禁止的行）
- 未修改 source code、tests、README、design.md、implementation-control.md
- 未执行 commits、push、PR、外部状态变更
- 未读取或引用排除输入

## Residual Verification

| Plan Residual | Artifact 处置 | 评判 |
|---|---|---|
| `benchmark_component_text` tuple golden 语义 | 正确 deferred | 符合 plan |
| `benchmark_index_name=null` golden 语义 | 正确 deferred | 符合 plan |
| `tracking_error` 禁止 | 正确遵守，未添加任何 tracking_error 行 | 符合 plan |
| `004194`、`005313`、`019923` 三只基金 TEXT_OK | 正确记录，但未部分实施 | 正确 — plan 要求 all-or-nothing |
| Extractor 嵌入换行 normalize 决策 | 正确记录为 residual | 需要下一个 reviewed plan |

## Next Gate Recommendation

下一个 gate 应为：

```text
P16-S2.1 benchmark_text newline normalization decision
```

必须是一个 reviewed plan gate，明确决定：
1. 是否在 extractor profile path 中 normalize `benchmark_text` 的内部 whitespace/newlines。
2. 如果 normalize，需确认对其他 fund `benchmark_text` 的影响范围。
3. 如果不 normalize，需更新 P16-S2 plan 中的 expected values 并确认 golden Markdown/JSON 路径对含换行值的支持。

决策后可重新进入 P16-S2 golden implementation gate，继续添加 25 个 scalar rows。

在 resolution 之前，不得修改 golden Markdown、source code 或 tests。

## Summary

Implementation artifact 正确触发了 stop condition 并在 golden 编辑前停止。Blocker 有效：`017644` 和 `019918` 的当前 extractor `benchmark_text` 含嵌入换行，与 P16-S1 计划值不一致。Evidence check 完全在 `FundDocumentRepository`/`extract_profile` 边界内完成。未修改任何 production 文件。验证充分。下一个 gate 需要决定是否 normalize extractor benchmark_text 中的嵌入换行。

---

**Reviewer**: AgentGLM
**Date**: 2026-05-22
**Artifact under review**: `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md`
