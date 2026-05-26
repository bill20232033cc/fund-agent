# Code Review (Re-review)

## Scope

- Mode: current changes (Gate B targeted re-review)
- Branch: codex/local-reconciliation
- Base: main
- Output file: docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-rereview-glm-20260526.md
- Prior review: docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-review-glm-20260526.md
- Included scope:
  - Current uncommitted diff in `fund_agent/fund/report_quality_validation.py`
  - Current uncommitted diff in `tests/fund/test_report_quality_validation.py`
  - Current uncommitted diff in `fund_agent/fund/README.md`
- Re-review focus:
  - Prior GLM F1: duplicate-index residual — confirm acceptable as residual
  - Prior GLM F2: front-of-bundle score_issue behavior — confirm resolved
  - New `_ScoreIssueRecordGroup` dataclass — any new blocker?
  - New `RQV_SCORE_ISSUE_ORPHANED` error code — correct and non-conflicting?
- Excluded scope: committed changes, unrelated untracked artifacts, renderer/FQ0-FQ6/Service/CLI
- Parallel review coverage: 无 — 单 reviewer
- Verdict: **PASS_WITH_FINDINGS**

## Diff Since Prior Review

相比首次 GLM review，diff 有三项结构变化：

1. **引入 `_ScoreIssueRecordGroup` dataclass**（行 265-278）：替代匿名 `tuple[_JsonRecord, list[...]]`，使用 `current_group` 引用模式
2. **error code 从 `RQV_RECORD_TYPE_INVALID` 改为 `RQV_SCORE_ISSUE_ORPHANED`**（行 406）：语义更精确
3. **测试更新**：`test_jsonl_score_issue_before_bundle_is_blocking` 断言改为 `RQV_SCORE_ISSUE_ORPHANED`（行 274）

## Findings

### F1-未修复-确认可留为residual-[低]-双重建索引可能产生重复 RQV_DUPLICATE_ID issue

- **入口/函数**: `validate_report_quality_jsonl` → `_validate_bundle_record` + `_validate_score_issue_records_against_bundle`
- **文件(行号)**: `fund_agent/fund/report_quality_validation.py:431`（`_validate_bundle_record` 内 `_build_indexes`）、行 529（`_validate_score_issue_records_against_bundle` 内 `_build_indexes`）
- **输入场景**: 任何含 score_issue 的 bundle 且该 bundle 内有重复 id
- **实际分支**: 两个函数各自独立调用 `_build_indexes`，对同一 bundle 对象执行相同 `_index_ids` 检测
- **预期行为**: 每个 bundle 的重复 id 只报告一次
- **实际行为**: 有 score_issue 的 bundle 可能对同一重复 id 报告两次（pointer 前缀不同：`line:N/bundle/...` vs `/bundle/...`）
- **直接证据**: `_ScoreIssueRecordGroup` 的引入未改变两个调用路径。行 431 的 `_validate_bundle_record(bundle_record, context)` 和行 436-440 的 `_validate_score_issue_records_against_bundle(score_issue_record_group.bundle, ...)` 对同一 `bundle` 对象各自调用 `_build_indexes`（行 529）
- **影响**: 仅冗余 issue，不影响 `failed_closed` 判定、不影响消费方行为。`_ScoreIssueRecordGroup` 未触及此路径
- **确认 residual 可接受**: 原因：(a) 冗余 issue 的 pointer 前缀不同，可区分来源；(b) 仅在 bundle 实际存在重复 id 时才出现，而重复 id 本身已是需修复的异常状态；(c) 修复需要跨函数传递已构建的 indexes 或缓存层，当前 slice 不值得引入这个结构变化
- **建议改法和验证点**: 后续 cleanup 可将 `_build_indexes` 结果缓存到 `_ScoreIssueRecordGroup` 或外层，避免对同一 bundle 重复构建
- **修复风险（低）**: 低
- **严重程度（低）**: 不影响正确性

### F2-已解决-[低]-前置裸 score_issue fail-closed 语义收紧行为确认

- **入口/函数**: `validate_report_quality_jsonl` → `current_group is None` 分支
- **文件(行号)**: `fund_agent/fund/report_quality_validation.py:403-421`
- **输入场景**: score_issue 出现在任何 bundle 之前
- **实际分支**: `current_group is None` → 发出 `RQV_SCORE_ISSUE_ORPHANED` blocking issue
- **预期行为**: 前置裸 score_issue 应 fail-closed
- **实际行为**: 与预期一致
- **直接证据**: 行 406 使用新的 `RQV_SCORE_ISSUE_ORPHANED` error code，比旧 `RQV_RECORD_TYPE_INVALID` 更精确。`RQV_RECORD_TYPE_INVALID` 现在正确保留给真正非法的 record_type（行 381）。两个 error code 语义正交：`RQV_RECORD_TYPE_INVALID` = "record_type 字段值非法"；`RQV_SCORE_ISSUE_ORPHANED` = "合法的 score_issue record 但缺少前置 bundle 归属"。语义分离正确
- **影响**: 无负面影响。行为收紧方向正确
- **测试覆盖**: `test_jsonl_score_issue_before_bundle_is_blocking`（行 251-276）断言 `RQV_SCORE_ISSUE_ORPHANED` 在 `line:1`。`test_jsonl_invalid_record_type_is_blocking`（行 713）断言 `RQV_RECORD_TYPE_INVALID` 仍用于非法 record_type。两个场景独立覆盖
- **建议改法和验证点**: 无需修改
- **修复风险（低）**: 无需修改
- **严重程度（低）**: 已解决

## `_ScoreIssueRecordGroup` Assessment

- **结构**: `@dataclass(slots=True)` 私有类型，两个显式字段无默认值。无 mutable default argument 问题
- **可变性**: `score_issue_records: list[...]` 在循环中被 `.append()` 修改。这是有意设计——`current_group` 引用在 bundle 创建后持续收集后续 score_issue。控制流清晰：bundle → new group；score_issue → append or orphan。无并发风险（单线程同步代码）
- **ownership**: `current_group` 每次遇到 bundle 时重新赋值，旧 group 的引用保存在 `score_issue_record_groups` 列表中。无悬挂引用或共享可变状态问题
- **替代匿名 tuple**: 比首次 review 中的 `(record, [])` tuple 更具可读性。`current_group.score_issue_records.append(...)` 比 `score_issue_records_by_bundle[-1][1].append(...)` 更清晰
- **结论**: 未引入新 blocker

## `RQV_SCORE_ISSUE_ORPHANED` Assessment

- **error code 唯一性**: 文件中 `RQV_RECORD_TYPE_INVALID` 出现在行 381（非法 record_type），`RQV_SCORE_ISSUE_ORPHANED` 出现在行 406（orphaned score_issue）。两个 code 不重叠
- **语义精确性**: `ORPHANED` 准确描述"有合法 record_type 但缺少归属 bundle"的状态。比通用 `INVALID` 更便于消费方区分处理
- **测试断言更新**: 行 274 从 `RQV_RECORD_TYPE_INVALID` 改为 `RQV_SCORE_ISSUE_ORPHANED`，与实现一致
- **结论**: 无新 blocker

## Adversarial Failure Pass

针对 re-review scope 的 adversarial 检查：

1. **`current_group` 跨 bundle 边界**: 第一个 bundle 创建 group A，第二个 bundle 创建 group B。group A 的 score_issue 列表在 group B 创建后不再被修改。第二个 bundle 后的 score_issue 进入 group B。边界正确。

2. **空 JSONL**: `records` 为空 → `bundle_records` 为空 → `score_issue_record_groups` 为空 → 两个 for 循环都不执行 → 返回空 issues + 0 total_records。正确。

3. **仅 bundle 无 score_issue**: 每个 bundle 创建一个空 group → `if score_issue_record_group.score_issue_records` 为 False → 不调用 `_validate_score_issue_records_against_bundle`。正确。

4. **score_issue before any bundle but bundles exist later**: `current_group is None` → `RQV_SCORE_ISSUE_ORPHANED` → continue。后续 bundle 正常处理。score_issue 不被分配到任何 bundle。正确。

5. **`_ScoreIssueRecordGroup.bundle` 与 `bundle_records` 的对象一致性**: 两者从同一 `records` 列表的同一 `parsed` 对象构建。`bundle_records[i][1] is score_issue_record_groups[i].bundle` 应为 True。无 deep copy 或 transformation。一致。

6. **`_ScoreIssueRecordGroup` 的 `_JsonRecord` type alias**: `_JsonRecord = Mapping[str, object]`。`parsed` 来自 `json.loads` 返回 `dict`，`dict` 是 `Mapping` 的子类型。类型一致。

未发现新的 adversarial blocker。

## Test Coverage Re-assessment

| 场景 | 测试 | 覆盖评估 |
|---|---|---|
| 单 bundle + score_issue 后向兼容 | `test_jsonl_accepts_bundle_record_and_score_issue_records` | 充分 |
| 多 bundle 各自 score_issue happy path | `test_jsonl_multi_bundle_score_issue_records_use_nearest_preceding_bundle` | 充分 |
| 跨 bundle 引用阻断 | `test_jsonl_score_issue_after_second_bundle_cannot_reference_first_bundle_ids` | 充分（anchor + gap 两个维度） |
| 前置裸 score_issue | `test_jsonl_score_issue_before_bundle_is_blocking` | 充分 |
| 非法 record_type | `test_jsonl_invalid_record_type_is_blocking` | 充分（与 ORPHANED 正交） |

## Open Questions

- 无

## Residual Risk

- **F1（双重建索引）**: 确认可作为 residual 保留。仅在 bundle 存在重复 id 时产生冗余 issue，不影响校验结论。后续 cleanup 可处理
- **"仅 score_issue 无 bundle" 场景无显式测试**: 与 `test_jsonl_score_issue_before_bundle_is_blocking` 走同一 `current_group is None` 代码路径，结构覆盖等价。显式测试可提高可读性但非必需
- 隐式"最近前置 bundle"归属仍依赖 JSONL 行序，若未来需要非顺序写入则需引入显式 `bundle_id` 字段。当前 slice 无此需求
