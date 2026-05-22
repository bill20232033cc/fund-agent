# P16-S2.1 Benchmark Text Newline Normalization Implementation — AgentGLM Code Review（2026-05-22）

## Verdict

`PASS`

实现完全符合 accepted plan 和 controller judgment 约束。Normalization helper 逻辑正确、scope 严格限定在 benchmark 路径、anchor note 通过 frozen dataclass 新建对象实现同步、测试覆盖全部 five candidates 加上 composite/anchor 语义断言、生产边界验证通过、全量测试 433 passed、无 golden/source-boundary 违规。无需 README 更新。

## Inputs

| Artifact | Role |
|---|---|
| `docs/reviews/p16-s2-1-benchmark-text-newline-normalization-implementation-20260522.md` | Implementation artifact |
| `docs/reviews/p16-s2-1-benchmark-text-newline-normalization-decision-plan-20260522.md` | Accepted decision plan |
| `docs/reviews/p16-s2-1-plan-review-controller-judgment-20260522.md` | Controller judgment |
| `fund_agent/fund/extractors/profile.py` (workspace diff) | Source changes |
| `tests/fund/extractors/test_profile.py` (workspace diff) | Test changes |

明确未读取、未引用：`docs/design0522.md`、`docs/implementation-control0522.md`、`docs/repo-audit-20260521.md`。

## Review Focus Areas

### Focus 1: Correctness of normalization helper

**Assessment: CORRECT**

`_normalize_benchmark_text()` (profile.py:343-363) 使用 `_BENCHMARK_NEWLINE_RUN_PATTERN`（`r"[ \t\f\v]*(?:\r\n|\r|\n)+[ \t\f\v]*"`）匹配换行片段及其紧邻横向空白，逐片段调用 `_benchmark_newline_replacement()` 判断删除或替换为空格。

`_benchmark_newline_replacement()` (profile.py:322-340) 通过 `_previous_non_space_char()` / `_next_non_space_char()` 查找换行片段两侧最近的非空白字符，仅在两侧均为 ASCII 字母或数字时替换为一个空格，否则删除。

边缘案例验证通过：

| 输入 | 输出 | 规则 |
|---|---|---|
| `存款利\n率(税后)×5%` | `存款利率(税后)×5%` | CJK 邻接：删除 |
| `存款利率（税后）\n*5%` | `存款利率（税后）*5%` | 标点邻接：删除 |
| `S&P\n500 index` | `S&P 500 index` | ASCII 词元边界：空格 |
| `A\r\n\r\nB` | `A B` | 多行换行 + ASCII：空格 |
| 无换行的完整 benchmark text | byte-for-byte 不变 | 无匹配 |

### Focus 2: No over-normalization

**Assessment: CORRECT**

Normalization 仅在 `_build_benchmark()` (profile.py:577) 调用 `_normalize_benchmark_matched_field()`，该函数仅对 `_extract_field(report, "benchmark")` 的结果应用，不影响其他任何字段路径：

- `_build_basic_identity()` → 无 normalization
- `_build_product_profile()` → 无 normalization
- `_build_fee_schedule()` → 无 normalization
- `_first_non_empty_after()` → 未修改，仍保留表格单元格内嵌换行
- 表格通用解析层 → 未修改
- snapshot / score / renderer / quality gate → 未修改

Punctuation variants 不受影响：`_BENCHMARK_NEWLINE_RUN_PATTERN` 只匹配换行及紧邻横向空白，不匹配 `×` / `*` / `+` / `＋` / `（` / `(` 等标点。

### Focus 3: Anchor note synchronized despite frozen `_MatchedField`

**Assessment: CORRECT**

`_normalize_benchmark_matched_field()` (profile.py:366-396) 正确处理 frozen dataclass：

1. 计算 `normalized_value = _normalize_benchmark_text(matched_field.value)`
2. 早返回：若 `normalized_value == matched_field.value`（无换行），返回原始对象
3. 对 `matched_field.matched_line` 执行 `str.replace(matched_field.value, normalized_value, 1)` 同步规范化
4. 防御性 fallback：若 replace 未生效（理论上不会发生在当前路径），对整个 `matched_line` 应用 `_normalize_benchmark_text()`
5. 用规范化后的值创建新的 `_MatchedField`，原始对象不被修改

对于表格提取路径：`matched_line = f"{label}：{value}"`，`str.replace(value, normalized_value, 1)` 正确替换锚点备注中的换行值。对于 regex 提取路径：regex `(.+)` 不匹配换行，所以该路径不会产生含换行的值，early-return 分支会直接返回原对象。

### Focus 4: Scope limited to benchmark path

**Assessment: CORRECT**

Diff 确认改动仅涉及：

- `profile.py`：新增 4 个 module-level 私有 helper + 1 个 `_MatchedField` 工厂函数 + `_build_benchmark()` 中 1 行调用
- `test_profile.py`：新增 1 个 parametrized test（5 组参数化用例）
- 无其他 source/test/config/README 变更

新增 helper 函数均在 `profile.py` 模块级定义（`_previous_non_space_char`、`_next_non_space_char`、`_is_ascii_word_char`、`_benchmark_newline_replacement`、`_normalize_benchmark_text`、`_normalize_benchmark_matched_field`），符合 AGENTS.md 规定的模块级私有函数优先原则。

### Focus 5: Tests cover affected/unaffected/composite/no index-name cases

**Assessment: ADEQUATE AND CORRECT**

`test_extract_profile_normalizes_benchmark_text_newlines_only_for_benchmark_path` 使用 `@pytest.mark.parametrize` 覆盖 5 组输入：

| fund_code | Newline in input | Expected behavior |
|---|---|---|
| `017644` | `存款利\n率` | Normalize to `存款利率` |
| `019918` | `存款利率（税后）\n*5%` | Normalize to `存款利率（税后）*5%` |
| `004194` | None | Byte-for-byte unchanged |
| `005313` | None | Byte-for-byte unchanged |
| `019923` | None | Byte-for-byte unchanged |

每组断言覆盖：

- `result.benchmark.value["benchmark_text"]` 等于 expected
- `benchmark_anchor.note` 等于 `f"业绩比较基准：{expected_benchmark_text}"`（anchor note 同步）
- `section_id` / `page_number` / `table_id` / `row_locator` 保持原值
- `index_profile.value.benchmark_text` 等于 expected（index_profile 同源消费规范化值）
- `benchmark_identity_status == "composite"`
- `benchmark_index_name is None`
- `benchmark_component_text` 等于 `_benchmark_components(expected_benchmark_text)`
- `methodology_availability == "benchmark_only"`
- `constituents_availability == "benchmark_only"`
- `source_tier == "benchmark_context"`

### Focus 6: Validation adequate

**Assessment: ADEQUATE**

Implementation artifact 记录并通过：

- Profile tests: `22 passed` ✓（独立验证确认）
- Snapshot/score tests: `32 passed` ✓（独立验证确认）
- ruff: `All checks passed!` ✓（独立验证确认）
- `git diff --check HEAD`: passed ✓（独立验证确认）
- Full suite: `433 passed` ✓（独立验证确认）

Production boundary verification 通过 `FundDataExtractor`（不是直接 PDF/cache）确认五只基金全部 OK，并断言 `composite` / `None` / `benchmark_only` / `benchmark_context` 语义不变。独立验证已复现此结果。

### Focus 7: Production boundary check credible

**Assessment: CREDIBLE**

Production 验证脚本使用 `FundDataExtractor`（`await extractor.extract(code, 2024, force_refresh=False)`），符合 `AGENTS.md` 硬约束和 `docs/design.md` 6.2 节对年报访问必须经过统一文档仓库接口的要求。未直接访问 PDF/cache/source helper。五只基金全部断言通过，已独立复现。

### Focus 8: README update requirements under AGENTS.md

**Assessment: NO UPDATE NEEDED**

AGENTS.md 触发规则：

- `fund_agent/fund/` 修改 → 更新 `fund_agent/fund/README.md`（仅当 extractor behavior description 失准）
- `tests/` 修改 → 更新 `tests/README.md`（仅当 test organization 或 running instructions 变化）

Fund README 当前描述 `extract_profile()` 返回 `benchmark：§2 中的业绩比较基准文本`。Normalization 是内部实现细节，不改变公开契约或字段语义描述。此描述仍然准确。

Tests README 第 14 行描述 `test_profile.py` 覆盖范围。新增的 parametrized test 不改变测试组织或运行方式。此描述仍然准确。

Implementation artifact 正确声明了 "未更新 README，因为本次没有改变公开 Fund 包契约、测试组织或运行方式"。

### Focus 9: No golden/source-boundary violations

**Assessment: NO VIOLATIONS**

- `reports/golden-answers/` 目录未被修改
- `docs/design.md`、`docs/implementation-control.md` 未被修改
- `docs/code_20260519.csv`（selected CSV）未被修改
- RR-13 数据未被修改
- 无 commits、branches、PRs、issues 或外部状态变更
- 无 Dayu Host/Engine/tool loop 依赖
- 无 LLM audit、E1-E3 或 Evidence Confirm 引入

## Validation (Independent)

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py -q
.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q
.venv/bin/python -m ruff check fund_agent tests
git diff --check HEAD
.venv/bin/python -m pytest -q
```

Results: `22 passed` / `32 passed` / `All checks passed!` / exit 0 / `433 passed`。

Production boundary check（five candidates through `FundDataExtractor`）：`004194 OK` / `005313 OK` / `017644 OK` / `019918 OK` / `019923 OK`。

Edge-case normalization tests（ASCII boundary / CJK / multiple newlines / punctuation / no-op）：all passed。

## Changed Files

Only the review artifact was created by this review:

```text
docs/reviews/p16-s2-1-code-review-glm-20260522.md
```

Implementation changes reviewed (not modified by this review):

```text
fund_agent/fund/extractors/profile.py
tests/fund/extractors/test_profile.py
docs/reviews/p16-s2-1-benchmark-text-newline-normalization-implementation-20260522.md
```

## Summary

实现完全符合 accepted plan 的全部 7 条 implementation gate constraints。窄口径 benchmark-only normalization、frozen dataclass 安全处理、anchor note 同步、five-candidate 测试覆盖、生产边界验证、无 README/golden/external 违规——全部通过。P16-S2 golden implementation 可安全恢复。
