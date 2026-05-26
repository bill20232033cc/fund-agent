# Code Review (Re-review)

## Scope

- Mode: current changes (Gate B uncommitted diff, targeted re-review after follow-up)
- Branch: `codex/local-reconciliation`
- Base: `main`
- Output file: `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-rereview-mimo-20260526.md`
- Included scope:
  - `fund_agent/fund/report_quality_validation.py` (current workspace diff)
  - `tests/fund/test_report_quality_validation.py` (current workspace diff)
  - `fund_agent/fund/README.md` (current workspace diff)
  - `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-20260526.md` (Gate B artifact)
- Excluded scope: none relevant
- Parallel review coverage: 无
- Prior review: `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-review-mimo-20260526.md`

## Verdict

**PASS**

## Findings

未发现实质性问题。

### Prior Finding Resolution

**001-low-RQV_RECORD_TYPE_INVALID reuse** → **已修复**

- `RQV_SCORE_ISSUE_ORPHANED` 新增为 orphaned score_issue 的专用 error code（`report_quality_validation.py:406`）
- `RQV_RECORD_TYPE_INVALID` 现在只用于 `record_type not in {"bundle", "score_issue"}` 的真正非法值场景（line:378-391）
- 测试 `test_jsonl_score_issue_before_bundle_is_blocking` 已更新为断言 `RQV_SCORE_ISSUE_ORPHANED`（test file line:274）
- Gate B artifact line:25 和 line:37 正确记录了新 error code

**002-low-tuple-with-mutable-list grouping** → **已修复**

- `_ScoreIssueRecordGroup` dataclass（line:265-279）替代了 `tuple[_JsonRecord, list[tuple[int, _JsonRecord]]]` 模式
- 使用 `@dataclass(slots=True)` 声明，字段语义明确：`bundle: _JsonRecord` 和 `score_issue_records: list[tuple[int, _JsonRecord]]`
- `score_issue_record_groups` 变量名替代了 `score_issue_records_by_bundle`（line:396）
- `current_group` 变量名替代了 `current_bundle`（line:397）
- Gate B artifact line:29 正确记录了此次 cleanup

## Open Questions

无。

## Residual Risk

- `_ScoreIssueRecordGroup` 不是 frozen dataclass（缺少 `frozen=True`），`score_issue_records` 仍为 mutable list。当前用法正确（只在构建阶段 append，消费阶段只读），但如果未来在同一 dataclass 实例上做并发写入需注意。当前无并发场景，不构成 finding。
- Gate B artifact 的 residual risk 声明仍然有效：nearest-preceding-bundle ownership 是合理的默认行为，未来若引入显式 ownership 字段需同步更新。

## Reviewer Verification

- [x] 测试全部通过：28 passed
- [x] ruff lint 通过
- [x] Gate A combined JSONL 验证：total_records=9, blocking=0, failed_closed=false
- [x] `RQV_SCORE_ISSUE_ORPHANED` 专用 code 正确隔离，`RQV_RECORD_TYPE_INVALID` 不再用于 orphan 场景
- [x] `_ScoreIssueRecordGroup` dataclass 替代 tuple-with-mutable-list，语义清晰
- [x] README 多 bundle 描述与代码行为一致
- [x] 单 bundle JSONL 向后兼容（现有测试覆盖）
- [x] 边界合规：validator 仍只消费 Mapping/JSONL，不越界依赖
