# Code Review

## Scope

- Mode: current changes (Gate B uncommitted diff)
- Branch: `codex/local-reconciliation`
- Base: `main`
- Output file: `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-review-mimo-20260526.md`
- Included scope:
  - `fund_agent/fund/report_quality_validation.py` (uncommitted workspace diff)
  - `tests/fund/test_report_quality_validation.py` (uncommitted workspace diff)
  - `fund_agent/fund/README.md` (uncommitted workspace diff)
  - `docs/reviews/release-maintenance-small-baseline-real-evaluation-run-20260526.md` (Gate A artifact)
  - `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-20260526.md` (Gate B artifact)
- Excluded scope: none relevant
- Parallel review coverage: 无

## Verdict

**PASS_WITH_FINDINGS**

## Findings

### 001-unfixed-low-`RQV_RECORD_TYPE_INVALID` error code reuse for orphaned score_issue

- **入口/函数**: `validate_report_quality_jsonl()`
- **文件(行号)**: `fund_agent/fund/report_quality_validation.py:388-404`
- **输入场景**: JSONL 中 `score_issue` 出现在任何 `bundle` 之前
- **实际分支**: `current_bundle is None` 分支命中，生成 `RQV_RECORD_TYPE_INVALID` issue
- **预期行为**: orphaned score_issue 是顺序/归属错误，而非 record_type 本身非法。error code 应区分"record_type 字段值非法"和"record_type 合法但出现位置不合法"
- **实际行为**: 复用了与 line:362 `record_type not in {"bundle", "score_issue"}` 相同的 `RQV_RECORD_TYPE_INVALID` error code，但语义不同（一个是字段值非法，一个是顺序/归属非法）
- **直接证据**: line:362-376 用 `RQV_RECORD_TYPE_INVALID` 标记非法 record_type 值；line:388-404 用相同 code 标记合法 record_type 但顺序错误的 orphaned score_issue
- **影响**: 消费方按 error_code 聚合或报警时，无法区分"JSONL 含非法 record_type"和"score_issue 缺少前置 bundle"。当前无消费方按此 code 做自动化分支，影响低
- **建议改法和验证点**: 可考虑新增 `RQV_SCORE_ISSUE_ORPHANED` 或 `RQV_RECORD_ORDERING_INVALID` 专用 code；但若当前无消费方依赖此区分，也可保持现状并在 README/注释中说明复用理由
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 002-unfixed-low-mutable list append 用于 score_issue 归属跟踪

- **入口/函数**: `validate_report_quality_jsonl()`
- **文件(行号)**: `fund_agent/fund/report_quality_validation.py:380-406`
- **输入场景**: 所有多 bundle JSONL 解析路径
- **实际分支**: 每遇到 bundle record 时 append 新 tuple；遇到 score_issue 时 append 到 `score_issue_records_by_bundle[-1][1]`
- **预期行为**: 归属跟踪结构应清晰表达 bundle → score_issues 的一对多关系
- **实际行为**: `score_issue_records_by_bundle` 使用 `list[tuple[_JsonRecord, list[tuple[int, _JsonRecord]]]]`，外层 tuple 不可变但内层 `list` 可变。通过 `[-1][1].append()` 追加 score_issue 到当前 bundle 的可变 list。代码正确但结构不够直观——tuple 内嵌 mutable list 是一种不太常见的模式
- **直接证据**: line:380 声明 `score_issue_records_by_bundle: list[tuple[_JsonRecord, list[tuple[int, _JsonRecord]]]]`；line:385 `score_issue_records_by_bundle.append((record, []))`；line:406 `score_issue_records_by_bundle[-1][1].append((line_number, record))`
- **影响**: 当前行为正确。如果后续重构者误以为 tuple 内元素不可变，可能引入 bug。不影响当前 correctness
- **建议改法和验证点**: 可改为 `list[tuple[_JsonRecord, tuple[tuple[int, _JsonRecord], ...]]]` 并在 bundle 切换时冻结前一组，或保持现状并在注释中说明 mutable list 的使用意图
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

无。

## Residual Risk

- **ownership 语义**: Gate B artifact 正确指出此 fix 使用 nearest-preceding-bundle 语义而非显式 ownership 字段。当前 `score_issue` record 结构中没有 `bundle_id` 或类似显式归属字段，nearest-preceding 是合理的默认行为。未来若引入显式 ownership 字段，此逻辑需要同步更新。
- **bundle validation 与 score_issue assignment 的执行顺序**: 当前代码先遍历所有 records 做 score_issue 归属（line:382-406），再遍历 bundle_records 做 bundle 级校验（line:408-415），最后遍历 score_issue_records_by_bundle 做 score_issue 校验（line:417-425）。三遍遍历保证了正确的执行顺序，但若后续合并为单遍遍历需注意依赖关系。
- **test coverage**: 新增 3 个测试覆盖多 bundle 正常、跨 bundle 引用阻断和 orphaned score_issue 阻断。现有单 bundle 测试（`test_jsonl_accepts_bundle_record_and_score_issue_records`）确认向后兼容。28 个测试全部通过，ruff 通过。

## Reviewer Verification

- [x] 测试全部通过：28 passed
- [x] ruff lint 通过
- [x] Gate A combined JSONL（9 records, 原 4 blocking）现在 0 blocking，failed_closed=false
- [x] README 多 bundle 描述与代码行为一致
- [x] fail-closed 行为：orphaned score_issue → blocking
- [x] 单 bundle JSONL 向后兼容
- [x] 边界合规：validator 仍只消费 Mapping/JSONL，不读取文档仓库、PDF/cache/source helper、renderer、Service 或 FQ0-FQ6
- [x] 未引入 dayu.host / dayu.engine / FundDocumentRepository / nav_data 等越界依赖
