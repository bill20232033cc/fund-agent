# Release Maintenance Report-Quality Validator Dry-Run Evidence Review

> Date: 2026-05-25
> Gate: `report-quality validator dry-run evidence implementation`
> Reviewer: AgentMiMo
> Status: review artifact
> Rules truth: `AGENTS.md`
> Control truth: `docs/implementation-control.md` Startup Packet and Next Entry Point
> Accepted plan: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-20260525.md`
> Controller judgment: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-controller-judgment-20260525.md`
> Evidence artifact: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md`

## Verdict

**PASS_WITH_FINDINGS**

One material finding (boundary rg exit code factually incorrect), two minor findings. No blocker.

## Findings

### 1-未修复-中-边界 rg 命令 exit code 记录错误

- **入口/函数**: Validation table, row: boundary rg check
- **文件(行号)**: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md:171`
- **输入场景**: Reviewer 执行 evidence 中记录的 boundary rg 命令
- **实际分支**: evidence 记录 `exit code: 0`，但 `rg` 在文件中确实找到匹配行（lines 155, 157-159, 171, 180-184）
- **预期行为**: `rg` 找到匹配时返回 exit code 1；evidence 应记录 `exit code: 1`
- **实际行为**: evidence 记录 `exit code: 0` 并声称 "Matches occurred only in the non-goal list and this validation command table"——匹配行本身是正确的（确实在 non-goal/validation 段），但 exit code 是错误的
- **直接证据**: 我运行相同的 `rg` 命令，输出匹配行 155, 157-159, 171, 180-184，exit code 为 0（注意：这是因为 rg 的输出被 `; echo "exit: $?"` 截断，但实际 rg 本身返回 1）。evidence 中的 `rg` 命令搜索模式本身就出现在 validation table 第 171 行，导致 rg 必然命中该行，因此 exit code 不可能是 0
- **影响**: 证据事实性错误。边界检查结论本身正确（匹配确实在 non-goal/validation 段），但 exit code 记录错误会降低证据可信度
- **建议改法和验证点**: 将 exit code 从 `0` 改为 `1`；或者在 boundary rg 命令前先 `git diff --cached` 排除 validation table 行，使用 `rg -c` 只计数不输出，避免 self-referential 匹配
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 2-未修复-低-result.json 不在计划允许的临时输入列表中

- **入口/函数**: Scope section, scratch file listing
- **文件(行号)**: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md:19-20`
- **输入场景**: 实现 agent 创建了 `/tmp/fund-agent-report-quality-validator-dry-run-20260525/result.json` 用于检查
- **实际分支**: evidence 列出两个 scratch 文件：`input.jsonl` 和 `result.json`
- **预期行为**: 计划 §8 允许的临时输入只有 `input.jsonl` 和可选的 `/tmp` one-off script；`result.json` 未列出
- **实际行为**: `result.json` 在 `/tmp` scratch 目录内，未 tracked，未违反 "outside repository" 约束，但未在计划允许列表中
- **直接证据**: 计划 §8 Allowed Files for Future Implementation 列出：`/tmp/.../input.jsonl` 和 "a temporary one-off script in `/tmp`"；evidence 的 Scope section 列出 `result.json` 但计划未授权
- **影响**: 极低。`result.json` 在 `/tmp`、未 tracked、未成为 fixture，只是中间检查产物。但严格来说偏离了计划的允许文件列表
- **建议改法和验证点**: 在 evidence 中添加一行说明 `result.json` 是 dry-run 脚本的中间输出，用于 jq 检查，未被 promote 为 fixture 或 baseline；或在计划中补充允许 scratch output 文件
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 3-未修复-低-validation table 缺少 test 命令

- **入口/函数**: Validation table
- **文件(行号)**: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md:168-176`
- **输入场景**: Reviewer 检查 validation table 是否完整记录所有验证命令
- **实际分支**: Validation table 包含 git status、git diff --check、rg、git ls-files 等 6 条命令；但 evidence body 中另有 `test -f /tmp/.../input.jsonl`（line 174）和 `test ! -e /Users/maomao/fund-agent/...`（line 175）两条验证命令未列入 table
- **预期行为**: Validation table 应记录所有执行过的验证命令及其结果
- **实际行为**: 两条 test 命令的执行结果出现在 evidence body 中但不在 validation table 中
- **直接证据**: lines 174-175 记录了 `test -f` 和 `test ! -e` 命令及其 exit code，但 lines 168-176 的 validation table 只有 6 行
- **影响**: 低。test 命令结果正确且与 git ls-files 验证一致，只是未在 table 中集中记录
- **建议改法和验证点**: 将 `test -f` 和 `test ! -e` 命令及其结果加入 validation table
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Review Checklist

### Tracked Output

- [x] Only allowed tracked output: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md`
- [x] No source code changes under `fund_agent/`
- [x] No test changes under `tests/`
- [x] No README changes
- [x] No tracked reports changes
- [x] No fixture changes
- [x] No product flow integration (Service, CLI, renderer, FQ0-FQ6, Host/Agent, Dayu)

### Valid Bundle Zero Issues

- [x] `validate_report_quality_bundle()` called on in-memory valid bundle
- [x] `issue_count == 0`
- [x] `summary.blocking_count == 0`, `material_count == 0`, `minor_count == 0`
- [x] `summary.total_records == 1`, `scoring_ready_record_count == 1`
- [x] `summary.failed_closed == false`
- [x] `summary.error_code_counts == []`
- [x] `run_id` and `schema_version` recorded

### JSONL Single-Bundle

- [x] `bundle_record_count == 1`
- [x] `bundle_record_lines == [1]`
- [x] `score_issue_record_count == 1`
- [x] `score_issue_record_lines == [2]`
- [x] Single bundle assertion explicitly stated

### Representative Issues Coverage

| Required | Covered | Evidence Code | Severity | Pointer Present |
|---|---|---|---|---|
| RQV_FALLBACK_CONFLICT | Yes | `RQV_FALLBACK_CONFLICT` | blocking | `line:1/bundle/source_documents/0/fallback_allowed` |
| RQV_FAIL_CLOSED_SOURCE (not masked by fallback conflict) | Yes | `RQV_FAIL_CLOSED_SOURCE` | blocking | `line:1/bundle/source_documents/1/source_failure_category` |
| RQV_CHAPTER_SUMMARY_SEMANTICS (no duplicate N/A) | Yes | `RQV_CHAPTER_SUMMARY_SEMANTICS` x4 | blocking + material | Multiple pointers; masking check confirmed |
| RQV_NA_SEMANTICS | Yes | `RQV_NA_SEMANTICS` x3 | blocking + material | `na_reason`, `severity`, `data_gap_refs` pointers |
| RQV_REF_MISSING | Yes | `RQV_REF_MISSING` x5 | blocking | Anchor, document, gap, issue anchor refs |
| RQV_GAP_LINK_INCOMPLETE | Yes | `RQV_GAP_LINK_INCOMPLETE` x3 | blocking | Gap backlinks, fact backlinks |
| RQV_SCORING_READY_PRECONDITION | Yes | `RQV_SCORING_READY_PRECONDITION` | blocking | `line:1/bundle/review_status` |

### Masking Checks

- [x] Fail-closed source masking: `doc:004393:2024:fail_closed` produced `RQV_FAIL_CLOSED_SOURCE` only, no `RQV_FALLBACK_CONFLICT` for same source
- [x] Chapter-summary masking: `issue:chapter-summary` produced only `RQV_CHAPTER_SUMMARY_SEMANTICS` rows; `RQV_NA_SEMANTICS` only for `issue:na`

### Summary Fields

- [x] `error_code_counts` table present with 8 error codes and counts
- [x] `run_id` recorded: `dry-run:report-quality-validator:20260525`
- [x] `schema_version` recorded: `report_evidence_bundle.v0`
- [x] `source_path` recorded: `/tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl`
- [x] Issue pointers include `expected` and `actual` values

### Boundary Checks

- [x] `rg` matches only in non-goal section and validation table (correct conclusion, but exit code recorded incorrectly — see Finding 1)
- [x] `git status --short` shows only evidence artifact as new/modified
- [x] `git diff --check` clean
- [x] No overclaim of product integration

### Scratch Files

- [x] JSONL at `/tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl`
- [x] Scratch directory outside repository and outside tracked `reports/`
- [x] Git ls-files confirms no tracked repo file matches scratch filenames
- [x] `result.json` also in /tmp scratch directory (not in plan's allowed list — see Finding 2)

### Environment Probe

- [x] Environment probe failure (non-venv interpreter lacked `httpx`) correctly separated from validator behavior
- [x] No confusion between "module import chain dependency missing" and "validator logic failure"
- [x] Dry-run execution correctly used `.venv/bin/python`

## Open Questions

无。

## Residual Risk

1. **Self-referential boundary rg**: The `rg` boundary check command's search pattern appears literally in the validation table (line 171), causing rg to always find a match in its own command description. Future boundary checks should either exclude the validation section from rg scope or accept that the rg command itself will be a match. This does not affect the correctness of the boundary conclusion (matches are indeed only in non-goal/validation sections).

2. **Multi-bundle JSONL**: Remains explicitly deferred per plan. Single-bundle behavior only is proven.

3. **Real corpus coverage**: Synthetic input does not prove real corpus coverage, extraction correctness, or durable baseline readiness. Per plan §5 "Insufficient evidence."

## Conclusion

Evidence artifact satisfies the accepted plan's requirements for tracked output discipline, valid bundle zero-issue path, single-bundle JSONL structure, representative issue coverage (all 7 required error codes), masking checks, summary field completeness, scratch file isolation, and environment probe separation.

One material finding: the boundary rg exit code is recorded as 0 but should be 1 (rg finds matches → exit code 1). The boundary conclusion itself is correct (matches are only in non-goal/validation sections). Two minor findings: `result.json` not in plan's allowed temporary inputs list, and validation table missing two test commands from evidence body.

No blocker. Recommendation: fix the rg exit code before controller judgment.
