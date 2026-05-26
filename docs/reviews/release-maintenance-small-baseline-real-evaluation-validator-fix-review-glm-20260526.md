# Code Review

## Scope

- Mode: current changes (Gate B)
- Branch: codex/local-reconciliation
- Base: main
- Output file: docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-review-glm-20260526.md
- Included scope:
  - Uncommitted diff in `fund_agent/fund/report_quality_validation.py`
  - Uncommitted diff in `tests/fund/test_report_quality_validation.py`
  - Uncommitted diff in `fund_agent/fund/README.md`
  - Artifact: `docs/reviews/release-maintenance-small-baseline-real-evaluation-run-20260526.md`
  - Artifact: `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-20260526.md`
  - Context: `AGENTS.md`, `fund_agent/fund/report_evidence.py` (schema version, types)
- Excluded scope:
  - Committed changes already merged to `main`
  - Unrelated untracked docs/reviews artifacts
  - `report_evidence.py` implementation (not changed, only imported)
  - Renderer, FQ0-FQ6, Service/CLI, Host/Agent, FundDocumentRepository
- Parallel review coverage: 无 — 单 reviewer 覆盖全部 diff 路径
- Verdict: **PASS_WITH_FINDINGS**

## Change Intent

Gate A 发现 combined multi-bundle JSONL 中，`validate_report_quality_jsonl()` 将所有独立 `score_issue` 记录针对第一个 bundle 的 id 索引校验，导致后续 bundle 的 `score_issue` 因引用不在首个 bundle 中的 anchor/gap 而产生 `RQV_REF_MISSING`。本改动将独立 `score_issue` 归属到最近前置 bundle，使 multi-bundle JSONL 可通过校验。

## Findings

### F1-未修复-[低]-双重建索引可能产生重复 RQV_DUPLICATE_ID issue

- **入口/函数**: `validate_report_quality_jsonl` → `_validate_bundle_record` + `_validate_score_issue_records_against_bundle`
- **文件(行号)**: `fund_agent/fund/report_quality_validation.py:472`（`_validate_bundle_record` 内调用 `_build_indexes`）、`fund_agent/fund/report_quality_validation.py:513`（`_validate_score_issue_records_against_bundle` 内调用 `_build_indexes`）
- **输入场景**: 任何包含 score_issue 的 bundle 且该 bundle 内存在重复 id（如重复 `anchor_id`）
- **实际分支**: bundle 通过 `_validate_bundle_record` 校验时，`_build_indexes` 检测到重复 id 并发出 `RQV_DUPLICATE_ID` issue；随后 `_validate_score_issue_records_against_bundle` 再次对同一 bundle 调用 `_build_indexes`，发出相同内容的 `RQV_DUPLICATE_ID` issue
- **预期行为**: 每个 bundle 的重复 id 只应报告一次
- **实际行为**: 有 score_issue 的 bundle 的重复 id 被报告两次（pointer 前缀不同：`line:N/bundle/...` vs `/bundle/...`）
- **直接证据**: `_validate_bundle_record` 在行 472 调用 `_build_indexes(bundle, pointer, context, issues)`；`_validate_score_issue_records_against_bundle` 在行 513 调用 `_build_indexes(bundle, "/bundle", context, issues)`。两者对同一 bundle 对象执行相同的 `_index_ids` 逻辑
- **影响**: 仅产生冗余 issue，不影响校验结论（`failed_closed` 状态不受影响）。是预存在问题——旧代码对 primary bundle 也有同样的双重建索引。本改动将其从仅首个 bundle 扩展到所有含 score_issue 的 bundle
- **建议改法和验证点**: 后续可在 `_validate_score_issue_records_against_bundle` 中复用 `_validate_bundle_record` 已构建的 indexes，或将 indexes 缓存到外层循环避免重复构建。当前不影响正确性，可作为 follow-up
- **修复风险（低）**: 低。重构不影响外部 API
- **严重程度（低）**: 冗余 issue 不影响校验结论或消费方行为

### F2-行为收紧-[低]-bundle 前裸 score_issue 的 fail-closed 语义变严

- **入口/函数**: `validate_report_quality_jsonl` → 单遍扫描 records 列表
- **文件(行号)**: `fund_agent/fund/report_quality_validation.py:387-405`
- **输入场景**: JSONL 中 score_issue 出现在第一个 bundle 之前，且 JSONL 中后续存在 bundle record
- **实际分支**: 新代码在单遍扫描中遇到 `current_bundle is None` 时立即发出 `RQV_RECORD_TYPE_INVALID` blocking issue
- **预期行为**: 旧代码中 `if not bundle_records and score_issue_records` 只在整个 JSONL 无 bundle 时才 fail-closed。如果 JSONL 中既有 bundle 又有前置 score_issue，旧代码会静默将该 score_issue 归入第一个 bundle 校验
- **实际行为**: 新代码严格阻断任何出现在 bundle 之前的 score_issue，无论 JSONL 后续是否存在 bundle
- **直接证据**: 旧代码行 `if not bundle_records and score_issue_records:` 是对整体集合的判断；新代码行 `if current_bundle is None:` 是逐条位置的判断。行为收紧方向正确——前置裸 score_issue 缺乏明确的归属 bundle，fail-closed 是更安全的语义
- **影响**: 行为收紧。旧代码中可能 pass 的前置裸 score_issue 现在会被阻断。这不是回归而是语义修正
- **建议改法和验证点**: 无需修改。测试 `test_jsonl_score_issue_before_bundle_is_blocking` 已覆盖此行为。README 行 104 已更新文档
- **修复风险（低）**: 无需修改
- **严重程度（低）**: 收紧方向正确，有测试和文档覆盖

## Correctness Walkthrough

### 主链路走读：多 bundle JSONL + score_issue 归属

**路径**: `validate_report_quality_jsonl` 行 380-425

1. **records 解析**（行 326-377）：逐行解析 JSONL，过滤空行、非法 JSON、非 Mapping、非法 record_type。合法 record 以 `(line_number, record_type, parsed)` 存入 `records` 列表。

2. **bundle_records 构建**（行 379）：从 `records` 过滤所有 `record_type == "bundle"` 的记录。与旧代码一致。

3. **score_issue 归属扫描**（行 380-406）：单遍遍历 `records`：
   - 遇到 bundle：更新 `current_bundle`，在 `score_issue_records_by_bundle` 中追加 `(record, [])`。
   - 遇到 score_issue 且 `current_bundle is None`：发出 blocking issue，continue。
   - 遇到 score_issue 且 `current_bundle is not None`：追加到最后一个 bundle 的 score_issue 列表。

   **验证**: `score_issue_records_by_bundle` 的长度等于 bundle 数量，顺序与 `bundle_records` 一致。score_issue 按最近前置 bundle 分组。逻辑正确。

4. **bundle 校验循环**（行 408-415）：对 `bundle_records` 中每个 bundle 调用 `_validate_bundle_record`。与旧代码一致。

5. **score_issue 校验循环**（行 417-425）：对 `score_issue_records_by_bundle` 中每个有 score_issue 的 bundle 调用 `_validate_score_issue_records_against_bundle`，传入该 bundle 及其关联的 score_issue 列表。

   **验证**: `_validate_score_issue_records_against_bundle` 内部调用 `_build_indexes` 构建 bundle-local 索引（anchor_ids, gap_ids 等），然后逐条校验 score_issue 的引用是否在索引中。跨 bundle 引用会因索引不包含目标 id 而产生 `RQV_REF_MISSING`。逻辑正确。

### 单 bundle 后向兼容走读

对于仅含一个 bundle 的 JSONL：
- `score_issue_records_by_bundle` 恰好有一个条目 `(bundle, [所有 score_issue])`
- 行为与旧代码等价：所有 score_issue 针对该 bundle 的索引校验
- 现有测试 `test_jsonl_accepts_bundle_record_and_score_issue_records` 覆盖此路径，继续通过

### fail-closed 走读

**无 bundle 场景**: 若 JSONL 中无任何 bundle record，`current_bundle` 始终为 `None`，所有 score_issue 均触发 blocking issue。与旧代码行为一致（旧代码通过 `if not bundle_records and score_issue_records` 处理）。

**前置裸 score_issue 场景**: 若 score_issue 出现在第一个 bundle 之前，新代码阻断。旧代码不阻断。行为收紧（见 F2）。

**跨 bundle 引用**: score_issue 归属到最近前置 bundle 后，引用检查仅针对该 bundle 的索引。跨 bundle 引用产生 `RQV_REF_MISSING`。测试 `test_jsonl_score_issue_after_second_bundle_cannot_reference_first_bundle_ids` 验证此行为。

### Ownership 语义走读

新代码采用"最近前置 bundle"作为隐式归属语义。理由：
- 独立 `score_issue` record 无显式 `bundle_id` 字段
- JSONL 是顺序 artifact，行序自然表达归属
- 旧代码的"全部归首个 bundle"语义在多 bundle 场景下不正确
- "最近前置 bundle"是顺序 artifact 中最不令人意外的归属规则

Gate B artifact 明确记录此设计选择及 trade-off（无显式 ownership 字段）。

## Test Coverage Assessment

| 测试 | 覆盖路径 | 评估 |
|---|---|---|
| `test_jsonl_accepts_bundle_record_and_score_issue_records` | 单 bundle + score_issue 后向兼容 | 覆盖基线行为，断言 total_records、failed_closed、run_id |
| `test_jsonl_multi_bundle_score_issue_records_use_nearest_preceding_bundle` | 多 bundle 各自 score_issue happy path | 覆盖归属正确性，断言 issues == () 且 failed_closed == False |
| `test_jsonl_score_issue_after_second_bundle_cannot_reference_first_bundle_ids` | 跨 bundle 引用阻断 | 覆盖 RQV_REF_MISSING 对 anchor_refs 和 data_gap_refs 两个维度 |
| `test_jsonl_score_issue_before_bundle_is_blocking` | 前置裸 score_issue fail-closed | 覆盖新收紧行为 |

覆盖充分的维度：
- 单 bundle 后向兼容
- 多 bundle 正确归属
- 跨 bundle 引用拒绝
- 前置裸 score_issue 阻断

未覆盖但风险可控的维度：
- 空 JSONL（0 条记录）：不涉及 score_issue 归属逻辑变化
- 仅 bundle 无 score_issue：`if score_issue_records` 跳过，无需专门测试
- 三个以上 bundle 的 JSONL：逻辑是通用的单遍扫描，与两个 bundle 的逻辑无结构差异

## README Accuracy

`fund_agent/fund/README.md` 行 104 更新为：

> JSONL 当前支持 `record_type="bundle"` 与 `record_type="score_issue"`；多 bundle artifact 中，独立 `score_issue` 归属到最近的前置 bundle，bundle 前的裸 `score_issue` 会 fail-closed，并保留稳定行号 / 字段 pointer，供后续 scoring-run artifact 复盘

与实现一致。准确描述了：
- 支持的 record_type
- 多 bundle 归属语义
- 前置裸 score_issue 的 fail-closed 行为
- 行号/pointer 稳定性保证

## Boundary Compliance

- 未引入新的外部依赖
- 未修改 `report_evidence.py` 的 schema 或 type
- 未修改 renderer、FQ0-FQ6、Service/CLI、Host/Agent 行为
- validator 仍只消费内存对象和 JSONL mapping
- 无反向 import
- AGENTS.md 未包含关于 JSONL multi-bundle ownership 的特定规则限制，改动不违反现有约束

## Validation Evidence

- `pytest tests/fund/test_report_quality_validation.py`: 28 passed
- `ruff check`: All checks passed
- Gate B artifact 记录 combined JSONL 修复后 `total_records=9, blocking_count=0, failed_closed=false`

## Open Questions

- 无

## Residual Risk

- F1（双重建索引）可产生冗余 issue，不阻塞当前 gate，可作为后续 cleanup
- 隐式"最近前置 bundle"归属依赖 JSONL 行序。若未来需要非顺序写入或并行产出 score_issue，需要引入显式 `bundle_id` 字段。当前 slice 无此需求
- 未测试三个以上 bundle 的 JSONL，但逻辑是通用的单遍扫描，结构风险低
