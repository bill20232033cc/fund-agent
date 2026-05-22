# P16-S2.1 Benchmark Text Newline Normalization Decision Plan — AgentGLM Plan Review（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

计划从第一性原理正确推导出窄口径 normalization 路径，ownership 归属 profile extractor benchmark 构造边界是正确的，golden Markdown/JSON 不能安全表达嵌入换行的事实已验证，stop conditions 和 prohibitions 与现有 control 约束一致。两条 low/info finding 不阻断 plan 接受。

## Inputs

| Artifact | Role |
|---|---|
| `docs/reviews/p16-s2-1-benchmark-text-newline-normalization-decision-plan-20260522.md` | Reviewed decision plan |
| `AGENTS.md` | Execution constraint truth |
| `docs/design.md` | Design truth |
| `docs/implementation-control.md` | Control truth |
| `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md` | P16-S2 blocker evidence |
| `docs/reviews/p16-s2-code-review-controller-judgment-20260522.md` | P16-S2 controller judgment |
| `fund_agent/fund/extractors/profile.py` | Current code facts |
| `fund_agent/fund/golden_prefill.py` | Golden prefill newline handling |
| `fund_agent/fund/golden_answer.py` | Golden Markdown parsing |
| `fund_agent/fund/extraction_score.py` | Correctness newline handling |

明确未读取、未引用：`docs/design0522.md`、`docs/implementation-control0522.md`、`docs/repo-audit-20260521.md`。

## Review Focus Areas

### Focus 1: First-principles choice — normalize vs preserve raw newlines

**Assessment: CORRECT**

Plan 从四个独立论据推导 normalization 路径，全部与代码事实一致：

1. `benchmark_text` 是被 correctness、snapshot、报告和人工审核共同消费的结构化标量——代码验证：`_build_benchmark()` 输出的 `ExtractedField.value["benchmark_text"]` 被 `_benchmark_text()` 读取后流入 `_build_index_profile()` → `IndexProfileValue.benchmark_text`，再进入 snapshot/score/golden/correctness 链路。

2. PDF 表格单元格中的换行是版面换行而非语义组成——P16-S2 blocker 证据确认：`017644` 的换行在 `存款利\n率` 之间（"利率"是一个词被 PDF 表格宽度截断），`019918` 的换行在 `存款利率（税后）\n*5%` 之间（算术表达式被版面截断）。

3. Strict Markdown active rows 不能安全携带嵌入换行——代码验证：`parse_golden_answer_markdown()` 使用 `splitlines()` 逐行解析，`_escape_markdown_cell()` 在 golden_prefill.py:417 和 extraction_score.py:2424 均将 `\n` 替换为空格。嵌入换行会导致 Markdown 表格行断裂。

4. Golden 比对需要可读、稳定、同源的 expected string——correctness 路径有保守 whitespace normalize（`_normalize_comparable_value`），但 golden rows 和 blocker 检查仍依赖精确字符串比较。

Reject raw newlines 路径的分析同样正确：strict JSON 虽可编码 `\n`，但 golden 真源是 reviewed Markdown（通过 `golden-build` 转换），Markdown 无法安全表达多行 cell，写 raw multiline 进 JSON 会绕过 golden-build 路径。

### Focus 2: Correct ownership — profile extractor only

**Assessment: CORRECT**

Plan 指定 normalization 在 `fund_agent/fund/extractors/profile.py` 的 benchmark 构造边界。代码验证当前调用链：

```
extract_profile()
  → _build_benchmark(report)
    → _extract_field(report, "benchmark")
      → _extract_field_from_section_two_tables() or regex text match
    → ExtractedField(value={"benchmark_text": matched_field.value}, anchors=(...))
  → _build_index_profile(classification, benchmark)
    → _benchmark_text(benchmark) → str | None
    → IndexProfileValue(benchmark_text=benchmark_text, ...)
```

Normalization 应在 `_build_benchmark()` 创建 `ExtractedField` 之前应用，使 `value["benchmark_text"]` 和 anchor note 均消费 normalized 值。归属正确落在 Capability 层 `profile.py`，不涉及 documents/parser/cache/sources，不涉及 Service/UI/Engine/renderer/quality_gate。

### Focus 3: Risk of over-normalization

**Assessment: LOW RISK, well-mitigated**

Plan 明确限制 scope：

- 仅 benchmark_text 路径，不涉及 methodology、constituents、manager narrative、tracking error 或任意 raw section text
- 不改变 punctuation variants（`×` vs `*`、`+` vs `＋`、`（税后）` vs `(税后)`）
- 不全局 normalize 所有 profile fields 或所有 parsed table cells

对三只 unaffected 基金的要求是 byte-for-byte unchanged，这是最强防回归约束。如果 implementation 正确实现了 narrow scope，over-normalization 风险可控。

### Focus 4: Tests for affected/unaffected funds

**Assessment: ADEQUATE**

Plan 要求 deterministic table-fixture tests 覆盖：

- `017644` newline shape → normalize
- `019918` newline shape → normalize
- `004194` no-op
- `005313` no-op
- `019923` no-op
- `benchmark_identity_status` remains `composite`
- `benchmark_index_name` remains `None`
- `benchmark_component_text` behavior unchanged except consuming normalized text
- Anchor fields preserved

测试归属 `tests/fund/extractors/test_profile.py` 是正确的，现有 fixture 目录 `tests/fixtures/fund/extractors/profile/` 已存在。

### Focus 5: Preservation of anchors/composite semantics

**Assessment: CORRECT**

Plan 要求 anchor `section_id`、`page_number`、`table_id`、`row_locator` 保持不变，`benchmark_identity_status=composite` 不受影响。

代码验证：normalization 不改变 `_extract_field()` 的命中逻辑或表格定位，只修改匹配后值的换行字符。`_benchmark_identity_status()` 判断基于 `components` 拆分和关键词检测（"存款"、"债券"、"中债"），换行 removal 不影响这些关键词的存在性。`_benchmark_components()` 拆分基于 `_COMPOSITE_BENCHMARK_SEPARATORS`，换行不在分隔符列表中。

### Focus 6: Future golden resume path

**Assessment: CORRECT**

Plan 规定：

1. Normalization 实施后，five candidates 的 extractor 输出应与 canonical no-newline values 一致
2. Resume P16-S2 golden implementation 使用 same 25 scalar rows
3. Rebuild strict JSON through `golden-build`
4. Verify pre-existing golden records unchanged（especially `001548 index_profile`）

这与 P16-S2 accepted plan 和 controller judgment 一致。

### Focus 7: Stop conditions

**Assessment: CORRECT AND COMPLETE**

Plan 定义两类 stop conditions：

**Before source edits:**
- code facts differ from ownership model
- newline discrepancy cannot be reproduced from table-cell values
- would require changing parser internals, repository fallback, source adapters, snapshot schema, or golden schema

**Before golden edits:**
- normalized output still differs from canonical values
- candidate identity or benchmark anchor changed
- normalization changes `benchmark_identity_status`/`benchmark_index_name`/methodology/constituents/source_tier
- golden-build cannot rebuild without unrelated churn
- correctness reports `no_comparable_fields` or mismatches
- reviewers require active golden rows for `null`/`tuple` semantics

两类 stop conditions 均与 P16-S2 controller judgment 和现有 control constraints 一致。

### Focus 8: Boundary violations

**Assessment: NO VIOLATIONS FOUND**

Plan 的 prohibitions 正确覆盖：

- 不 add `tracking_error` rows
- 不 synthesize `benchmark_index_name`
- 不 add `benchmark_component_text` golden rows
- 不 access PDF/cache/source helpers directly
- 不 bypass `FundDocumentRepository` / `FundDataExtractor`
- 不 edit design/control/CSV/RR-13
- 不 use Dayu/LLM audit/E1-E3/Evidence Confirm

所有 prohibitions 与 `AGENTS.md` 硬约束、`docs/design.md` 边界定义和 `docs/implementation-control.md` open residuals 一致。

## Findings

### F1: Normalization rule 的 CJK/ASCII 分支在实际 five candidates 中不触发 ASCII path

**Severity: LOW**
**Evidence:** Plan normalization rule 要求 "remove newline runs when adjacent to CJK or benchmark punctuation; replace with ASCII space only when removing would merge two ASCII word tokens"。对当前五只候选基金，两个 affected case（`017644` 和 `019918`）的换行均在 CJK 字符或标点邻接处，ASCII word boundary 替换规则不会被触发。对三只 unaffected 基金，无换行需处理。
**Impact:** Implementation 可选择先实现只针对 benchmark text 的简单 newline removal（`re.sub(r'[\r\n]+', '', value)`），或实现完整的 CJK/ASCII 分支。只要 five candidates 测试全部通过且 byte-for-byte unchanged 验证通过，两种实现路径均可接受。
**Disposition:** Informational；不要求 plan 修订。Implementation 可选择最简规则，但须确保未来非 CJK benchmark text 的换行不会意外合并 ASCII 单词。

### F2: Anchor note 的 normalization 需显式处理

**Severity: INFO**
**Evidence:** 当前 `_build_anchor()` (profile.py:262-284) 使用 `matched_field.matched_line` 作为 anchor note。对于表格提取路径，`matched_line` 是 `f"{label}：{value}"` (profile.py:159)，其中 `value` 包含 raw newline。`_MatchedField` 是 frozen dataclass (profile.py:80-96)，不可原地修改。
**Impact:** 如果 implementation 仅 normalize `matched_field.value` 而不同步处理 anchor note，anchor note 仍将包含嵌入换行。虽然 correctness 路径有 whitespace normalize，但 anchor note 中的换行会在 snapshot/score 报告中出现。Plan 第 68-72 行已正确声明 "normalize the matched benchmark value before building both `benchmark.value["benchmark_text"]` and the benchmark evidence anchor note"，implementation 需要在创建 `ExtractedField` 时确保 anchor 也消费 normalized 值——例如新建 `_MatchedField` 或在 `_build_benchmark()` 中单独构造 anchor。
**Disposition:** Informational；plan 已正确声明意图，implementation 需注意 frozen dataclass 的处理方式。

## Evidence Boundary Verification

- 本 review 引用的代码位置均来自 `fund_agent/fund/extractors/profile.py`、`fund_agent/fund/golden_prefill.py`、`fund_agent/fund/golden_answer.py`、`fund_agent/fund/extraction_score.py`，全部在 Capability 层边界内
- 未读取 PDF/cache/source helper 代码
- 未引用 `docs/design0522.md`、`docs/implementation-control0522.md`、`docs/repo-audit-20260521.md`
- P16-S2 blocker 的 embedded newline 事实来自 accepted controller judgment 和 implementation artifact

## Truth Input Alignment

| Truth source | Plan alignment | Conflict |
|---|---|---|
| `AGENTS.md` 第一性原理约束 | Plan 从 raw 需求出发推导 normalize vs preserve 选择 | None |
| `AGENTS.md` 模块边界 | Normalization 归属 Capability 层 profile extractor | None |
| `AGENTS.md` 证据可溯源 | Normalization 不引入外部证据、不合成 `benchmark_index_name` | None |
| `docs/design.md` 6.2 结构化抽取 | Profile extractor ownership 一致 | None |
| `docs/design.md` 7.6 Golden Answer | Markdown 行解析和 `_escape_markdown_cell` 行为验证 | None |
| `docs/implementation-control.md` open residuals | P16-S2 blocker 和 P16-S2.1 gate 状态一致 | None |
| P16-S2 blocker artifact | Text diff facts 引用准确 | None |
| P16-S2 controller judgment | Finding dispositions 和 next gate 指定一致 | None |

## Changed Files

仅创建本 review artifact：

```text
docs/reviews/p16-s2-1-plan-review-glm-20260522.md
```

## Validation

```bash
git diff --check HEAD
```

Result: exit code `0`, no output.

```bash
rg -n "^(<<<<<<<|=======|>>>>>>>)" docs/reviews/p16-s2-1-plan-review-glm-20260522.md
```

Result: exit code `1`, no output; 无 conflict markers.

```bash
rg -n "[ \t]+$" docs/reviews/p16-s2-1-plan-review-glm-20260522.md
```

Result: exit code `1`, no output; 无行尾空白。

```bash
git status --short
```

Expected: only new review artifact and pre-existing excluded files.

## Summary

Plan verdict: `PASS_WITH_FINDINGS` (F1: LOW, F2: INFO). 第一性原理推导正确，ownership 归属 profile extractor benchmark 构造边界已验证，golden Markdown/JSON newline 处理约束已确认，stop conditions 和 prohibitions 与现有 control 一致。两条 finding 不要求 plan 修订，implementation 阶段注意 frozen `_MatchedField` 处理和 anchor note 同步即可。
