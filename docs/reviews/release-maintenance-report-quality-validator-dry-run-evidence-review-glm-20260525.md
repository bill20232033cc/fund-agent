# Code Review

## Scope

- Mode: current changes（evidence-only artifact review）
- Branch: `codex/v0-release-readiness-plan`
- Base: `main`
- Output file: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-review-glm-20260525.md`
- Included scope:
  - Evidence artifact: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md`
  - Accepted plan: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-20260525.md`
  - Controller judgment: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-controller-judgment-20260525.md`
  - Validator source: `fund_agent/fund/report_quality_validation.py`（只读参照，不改）
  - Evidence model source: `fund_agent/fund/report_evidence.py`（只读参照，不改）
  - Scratch JSONL: `/tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl`（只读验证）
  - Scratch result: `/tmp/fund-agent-report-quality-validator-dry-run-20260525/result.json`（只读验证）
  - Control doc: `docs/implementation-control.md` Startup Packet / Next Entry Point
  - Rules truth: `AGENTS.md`
- Excluded scope: source/tests/README/product flow（本 gate 不允许修改）
- Parallel review coverage: 无，主 reviewer 单独完成

## Review Focus

本 review 按 review focus 逐项验证：

1. tracked 输出是否只有允许的 evidence Markdown
2. evidence 是否证明 valid bundle zero issues
3. JSONL 是否明确 single-bundle
4. representative issues 是否覆盖所有 required error codes
5. summary/error_code_counts/run_id/schema_version/source_path/pointers/expected/actual
6. boundary rg 命中是否只在 non-goal/validation 段
7. scratch JSONL 是否在 /tmp 且未 tracked
8. 环境探测 failure 叙述是否混淆 validator 行为

## Findings

未发现实质性问题。

逐项验证结果：

### 1. Tracked 输出边界

`git status --short` 显示唯一新增 tracked 文件为 `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md`（`??` 状态，未 staged）。无 source、tests、README、tracked reports、fixtures、product flow 文件变更。符合 plan §8 allowed files 约束。

### 2. Valid Bundle Zero Issues

result.json `valid_result` 字段确认：
- `issue_count: 0`
- `summary.blocking_count: 0`, `material_count: 0`, `minor_count: 0`
- `summary.failed_closed: false`
- `summary.error_code_counts: []`
- `summary.scoring_ready_record_count: 1`

证据表格声称与实际 result.json 一致。

### 3. JSONL Single-Bundle

对 `/tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl` 逐行解析确认：
- `bundle_record_count == 1`（line 1, `record_type="bundle"`, `bundle_id="bundle:004393:2024:dry-run:malformed"`）
- `score_issue_record_count == 1`（line 2, `record_type="score_issue"`, `issue_id="issue:external-linked"`）
- 无第二个 bundle record

result.json `input_shape` 字段与直接解析一致。证据表格 `bundle_record_lines=[1]`, `score_issue_record_lines=[2]` 准确。

### 4. Representative Issues Coverage

error_code_counts 与 representative issue table 对照：

| Error code | Count | Representative rows | Verified |
|---|---:|---|---|
| `RQV_FALLBACK_CONFLICT` | 1 | 1 row: source_documents/0, fallback_allowed | ✅ pointer、expected、actual 与 result.json 一致 |
| `RQV_FAIL_CLOSED_SOURCE` | 1 | 1 row: source_documents/1, schema_drift | ✅ fail-closed 不被 fallback conflict 掩盖（见下文 masking check） |
| `RQV_CHAPTER_SUMMARY_SEMANTICS` | 4 | 4 rows: status/chapter_id/reviewer_note/severity | ✅ 不重复 N/A semantics（见下文 masking check） |
| `RQV_NA_SEMANTICS` | 3 | 3 rows: na_reason/severity/blocking gap | ✅ 仅对 issue:na 触发 |
| `RQV_REF_MISSING` | 5 | 5 rows: anchor/doc/gap/anchor/document refs | ✅ 覆盖 forward ref + anchor document ref |
| `RQV_GAP_LINK_INCOMPLETE` | 3 | 3 rows: gap→N/A issue / gap→material issue / blocked fact backlink | ✅ 覆盖双向回链 |
| `RQV_SCORING_READY_PRECONDITION` | 1 | 1 row: review_status, 7 precondition failures | ✅ 全部 failure 可从 JSONL 输入追溯 |
| `RQV_FIELD_MISSING` | 1 | error_code_counts 中列出 | ✅ facts[0] extraction_mode=missing, value=null, 无 failure_category 且无 data_gap_refs |

Plan 要求的 7 类 representative issue 全部覆盖。`RQV_FIELD_MISSING` 不在 plan required list 中，但已在 error_code_counts 中正确计数。

### 5. Masking Checks

**Fail-closed source 不被 fallback conflict 掩盖：**
- JSONL `source_documents[0]`（`doc:004393:2024:fallback_conflict`）：failure_category=not_found, fallback_allowed=false → 触发 `RQV_FALLBACK_CONFLICT`
- JSONL `source_documents[1]`（`doc:004393:2024:fail_closed`）：failure_category=schema_drift → 触发 `RQV_FAIL_CLOSED_SOURCE`
- 验证器代码 `report_quality_validation.py:1060-1074`：fail-closed 检测后 `continue`，跳过 fallback conflict 逻辑
- 结果：同一 fail-closed source 只产生 `RQV_FAIL_CLOSED_SOURCE`，不额外产生 `RQV_FALLBACK_CONFLICT` ✅

**Chapter-summary 不重复 N/A semantics：**
- `issue:chapter-summary`（dimension=chapter_summary, status=N/A）→ 验证器优先走 `_validate_chapter_summary_issue`（`report_quality_validation.py:1389-1390`），产出 `RQV_CHAPTER_SUMMARY_SEMANTICS` 4 条
- `issue:na`（dimension=fact_coverage, status=N/A）→ 走 `_validate_na_issue`（`report_quality_validation.py:1391-1392`），产出 `RQV_NA_SEMANTICS` 3 条
- 两者互不重复 ✅

### 6. Summary / Metadata Fields

result.json `jsonl_result` 字段与证据表格逐项核对：

| Field | Evidence claim | result.json | Match |
|---|---|---|---|
| `source_path` | `/tmp/.../input.jsonl` | `/tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl` | ✅ |
| `run_id` | `dry-run:report-quality-validator:20260525` | `dry-run:report-quality-validator:20260525` | ✅ |
| `schema_version` | `report_evidence_bundle.v0` | `report_evidence_bundle.v0` | ✅ |
| `issue_count` | 19 | 19 | ✅ |
| `summary.total_records` | 2 | 2 | ✅ |
| `summary.scoring_ready_record_count` | 1 | 1 | ✅ |
| `summary.blocking_count` | 14 | 14 | ✅ |
| `summary.material_count` | 5 | 5 | ✅ |
| `summary.minor_count` | 0 | 0 | ✅ |
| `summary.failed_closed` | true | true | ✅ |
| `summary.error_code_counts` | 8 entries, sum 19 | 8 entries, sum 19 | ✅ |

### 7. Boundary rg 检查

```bash
rg -n "FundDocumentRepository|AnnualReportDocumentCache|AnnualReportPdfAdapter|documents\.sources|annual_report_pdf|extra_payload|dayu\.host|dayu\.engine|nav_data|quality_gate|extraction_score|fund-analysis|reports/scoring-runs" docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md
```

命中行 155、157、158、159（Non-Goals 段）和 171、180-184（Validation 段）。所有命中均为 boundary assertion，不是产品集成声明。无 overclaim。✅

### 8. Scratch JSONL 位置与 Tracking

- `/tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl` 存在于 `/tmp` ✅
- `git ls-files` 确认该路径在 repo worktree 外 ✅
- `git ls-files | rg "fund-agent-report-quality-validator-dry-run"` 无匹配 ✅
- 无 repo 内 scratch 目录 ✅

### 9. 环境探测叙述

证据 Commands 表第一行 "Environment probe" 步骤 exit_code=1，记录了系统 Python（非 venv）因缺少 `httpx` 而失败。叙述明确标注 "Failed before validator execution" 和 "No repository, PDF, cache, source helper, downloader, extractor, or fetch function was called"。实际 dry-run 使用 `.venv/bin/python` 成功（exit_code=0）。环境探测 failure 未混淆 validator 行为。✅

### 10. RQV_SCORING_READY_PRECONDITION 详细验证

证据 claims 7 个 precondition failure。逐项从 JSONL 输入追溯：

| Precondition failure | JSONL evidence |
|---|---|
| corpus_id must not be ad_hoc | corpus_id="ad_hoc" |
| classified_fund_type must not be unknown | classified_fund_type="unknown" |
| type_slot_membership_status must be matches_slot | type_slot_membership_status="unknown" |
| annual report source_failure_category must be none | source_documents[0].failure_category="not_found", source_documents[1].failure_category="schema_drift" |
| blocking data gaps must be resolved | data_gaps[0].failure_category="integrity_error" → blocking gap |
| quality_context.fq_gate_status must not be block | fq_gate_status="block" |
| all facts must have review_status=reviewed | facts[0].review_status="not_reviewed" |

验证器代码 `_validate_scoring_ready_preconditions`（`report_quality_validation.py:1803-1901`）逻辑与上述 7 项完全一致。✅

## Conclusion

**PASS。**

Evidence artifact 满足 accepted plan 全部 acceptance criteria：

1. 两个 public API 均可从 one-off command 成功调用，无 source/test 变更 ✅
2. Valid minimal bundle 返回 zero issues 和 stable summary fields ✅
3. JSONL dry run 使用 single-bundle artifact，返回 deterministic fields ✅
4. Evidence 记录 blocking/material/minor counts 和 error_code_counts ✅
5. Representative issues 覆盖 plan 要求的全部 7 类 ✅
6. Issue records 包含 stable error_code、severity、record_pointer、record_id、expected、actual ✅
7. Boundary validation 证明无 tracked reports、durable fixtures、Service/CLI/renderer/FQ0-FQ6、PDF/cache/source helper、FundDocumentRepository、Host/Agent/dayu、nav_data 或 extra_payload work ✅

Evidence 未 overclaim 产品集成就绪，仅证明 consumer-contract dry-run 行为。

## Open Questions

无。

## Residual Risk

- Scratch JSONL `/tmp/fund-agent-report-quality-validator-dry-run-20260525/` 在机器重启后可能消失。证据中的 result.json 摘要和 representative issue table 已足够让 reviewer 无需 scratch 文件即可验证。
- `RQV_FIELD_MISSING` (count 1) 出现在 error_code_counts 但无 representative row。Plan 不要求覆盖该 code，且其来源（facts[0] extraction_mode=missing 无 failure_category 且无 data_gap_refs）可从 validator 代码逻辑直接追溯。
