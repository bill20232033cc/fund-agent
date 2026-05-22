# P16 PR Review — AgentGLM（2026-05-22）

## Verdict

`PASS`

PR #10 diff 与 P16 aggregate accepted scope 完全一致，无 blocking 或 warning 级发现。

## PR Metadata

| Field | Value |
|---|---|
| PR | https://github.com/bill20232033cc/fund-agent/pull/10 |
| Title | P16 enhanced index profile golden rows |
| Base | `main` |
| Head | `docs/post-p14-follow-up-planning` |
| Draft | `true` |
| mergeState | `CLEAN` |
| CI `test` | `SUCCESS`（18s, actions run 26279512982） |
| Commits | 19 |
| Files changed | 64（+10173 / -184） |

## Scope Alignment with P16 Aggregate Accepted Scope

### P16-S1 Evidence

PR 包含 P16-S1 evidence review artifacts（`docs/reviews/p16-s1-*.md`），不涉及 production code 变更。Evidence acquisition 结果为 `PARTIAL_ACCEPTED_INDEX_PROFILE_ONLY`，`tracking_error` 全部 blocked。符合 aggregate review 预期。

### P16-S2.1 Newline Normalization

`fund_agent/fund/extractors/profile.py` 新增 `_normalize_benchmark_text()` 及 4 个辅助函数/常量：

- `_BENCHMARK_NEWLINE_RUN_PATTERN`：匹配 `\r\n`/`\r`/`\n` 及两侧空白
- `_previous_non_space_char` / `_next_non_space_char`：查找换行两侧最近非空白字符
- `_is_ascii_word_char`：判断是否需要空格间隔的 ASCII 词元
- `_benchmark_newline_replacement`：ASCII 词元间插入空格，其余情况删除换行
- `_normalize_benchmark_matched_field`：同步规范化 value 和 matched_line，不修改原对象

调用点唯一：`_build_benchmark()` 中 `_extract_field` 之后。scope 正确限制在 benchmark path，不影响其他 extractor 路径。

### 25 Enhanced-Index index_profile Scalar Golden Rows

本地脚本验证结果：

| 检查项 | 结果 |
|---|---|
| fund_count | 11（6 existing + 5 new） |
| record_count | 150 |
| flat records = nested total | 150 = 150 |
| 新增 funds | `004194`, `005313`, `017644`, `019918`, `019923` |
| 每个 fund 的 index_profile rows | 5（benchmark_text, benchmark_identity_status, methodology_availability, constituents_availability, source_tier） |
| 总新增 golden rows | 5 × 5 = 25 |
| tracking_error rows | 0（正确 blocked） |
| forbidden sub_fields（benchmark_index_name, benchmark_index_code, benchmark_component_text） | 0（正确排除） |
| embedded newlines in expected_value | 0 |
| confidence 一致性 | 全部 `high` |
| fund_code 嵌套/flat 一致性 | 0 mismatch |
| `001548` preservation | 4 rows preserved（benchmark_text, benchmark_identity_status, benchmark_index_name, source_tier） |

### Tests / Control Artifacts

| Test File | 新增测试 | 验证目标 |
|---|---|---|
| `tests/fund/extractors/test_profile.py` | 1 parametrized（5 cases） | benchmark newline normalization + index_profile 语义 |
| `tests/fund/test_extraction_score.py` | 2 | composite scalar match / mismatch correctness |
| `tests/fund/test_extraction_snapshot.py` | 1 | composite null/tuple 值不进入 comparable_values |
| `tests/fund/test_golden_answer.py` | 2 | 计划内 scalar rows + 001548 preservation |
| `tests/fund/test_quality_gate.py` | 1 | FQ1 blocking for composite scalar mismatch |

本地运行结果：`439 passed`（全量），`83 passed`（targeted），ruff passed，`git diff --check HEAD` passed。

## PR-Only Checks

### Missing Commits

19 commits 完整呈现于 PR 中，从 `75026c22 docs: accept post-P14 follow-up planning` 到 `d48c580b docs: accept P16 aggregate review`。commit 链与 Active Gate Ledger 吻合。无缺失。

### Base / Head

`base=main`, `head=docs/post-p14-follow-up-planning`。与 `implementation-control.md` Startup Packet 一致。

### CI / Merge State

CI `test` job `SUCCESS`。`mergeState=CLEAN`，`mergeable=MERGEABLE`。无冲突。

### Untracked Local Artifacts

本地 untracked 文件 `docs/design0522.md`、`docs/implementation-control0522.md`、`docs/repo-audit-20260521.md` 均 **未** 进入 PR diff。PR 包含 `docs/repo-audit-20260522.md`（已 commit 的 20260522 版本，非 excluded 的 20260521 版本）和 `docs/reviews/implementation-control0522-controller-judgment.md`（review artifact，非 excluded 的 control0522 draft 本身）。处理正确。

### PR Body Accuracy

| PR Body 字段 | 验证结果 |
|---|---|
| Summary | 准确描述了 25 golden rows、newline normalization、tests |
| Validation: 439 passed | 本地复现一致 |
| Validation: 22 passed（profile） | PR body 正确 |
| Validation: 61 passed（golden/score/quality） | PR body 正确 |
| Residuals: tracking_error blocked | 与 golden-answer.json 一致 |
| Residuals: composite null/tuple outside denominator | 与 aggregate review 一致 |
| Review Artifacts | 列出路径均存在 |

### External Side Effects

无。未创建/修改 GitHub issue、PR comment、或外部服务状态。

### README Drift

PR 未修改 `fund_agent/fund/extractors/profile.py` 的公共接口签名、CLI 命令、配置默认值或测试组织。README 更新不要求，与 aggregate review 判断一致。

### Forbidden Golden Rows

`tracking_error` rows 数量 = 0。`benchmark_index_name`、`benchmark_index_code`、`benchmark_component_text` 均未出现在新增 5 个 fund 的 records 中。`001548` 已有 4 行 index_profile rows 未被改写。

## Findings

无 blocking 或 warning 级发现。

### INFO 级发现

| ID | 发现 | 处理 |
|---|---|---|
| I1 | PR title "P16 enhanced index profile golden rows" 未完全覆盖 scope（实际包含 P14-P16 控制文档融合 + newline normalization）。PR body 提供了充分细节。 | 接受。Title 已足够定位，body 补充了完整 scope。 |
| I2 | PR 包含 56 个 review artifact docs + 8 个 implementation/test/golden 文件。review artifact 占比高。 | 接受。P14-P16 累积 review artifact 正常累积。 |
| I3 | `docs/repo-audit-20260522.md` 在 PR diff 中，作为 "scoped 2026-05-22 input" 记录于 implementation-control.md。 | 接受。20260522 版本已 commit 并纳入 control truth；excluded 的是 20260521 版本。 |

## Validation Summary

| Validation | Result |
|---|---|
| `.venv/bin/python -m pytest -q` | 439 passed |
| `.venv/bin/python -m pytest tests/fund/extractors/test_profile.py -q` | 22 passed |
| `.venv/bin/python -m pytest tests/fund/test_golden_answer.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q` | 61 passed |
| `.venv/bin/python -m ruff check fund_agent tests` | All checks passed |
| `git diff --check HEAD` | passed（无 whitespace errors） |
| golden-answer.json integrity（fund_count=11, record_count=150, no embedded newlines, no tracking_error, no forbidden sub_fields, 001548 preserved） | passed |
| Normalization scope（only called in `_build_benchmark()`） | passed |

## Next Gate Recommendation

P16 PR review 通过。PR #10 可进入 draft PR gate 下一步：

- 用户授权后可 push / mark ready for review / merge
- Merge 前建议确认 PR title 是否需要更精确覆盖 scope
- Merge 后需更新 implementation-control.md Startup Packet 至 post-P16 follow-up planning 状态
