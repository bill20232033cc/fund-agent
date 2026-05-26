# Code Review (Final Aggregate)

## Scope

- Mode: current changes (Gate A/B/C/D final aggregate)
- Branch: codex/local-reconciliation
- Base: main
- Output file: docs/reviews/release-maintenance-small-baseline-real-evaluation-final-review-glm-20260526.md
- Prior reviews:
  - Gate B initial: `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-review-glm-20260526.md`
  - Gate B re-review: `docs/reviews/release-maintenance-small-baseline-real-evaluation-validator-fix-rereview-glm-20260526.md`
- Included scope:
  - Gate B: `fund_agent/fund/report_quality_validation.py`, `tests/fund/test_report_quality_validation.py`, `fund_agent/fund/README.md`
  - Gate C: `scripts/report_quality_eval.py`, `tests/scripts/test_report_quality_eval.py`, `tests/README.md`
  - Gate D: `docs/implementation-control.md`
  - Artifacts: Gate A run, Gate B fix evidence + reviews/re-reviews (MiMo + GLM), Gate C dev-tool, Gate D controller judgment, evidence-chain deepreview controller judgment
- Excluded scope:
  - Committed changes already on branch
  - Renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, FundDocumentRepository, nav_data, extractor, source helpers
  - Scratch outputs under `/tmp/fund-agent-small-baseline-real-eval-20260526/`
- Parallel review coverage: 无 — 单 reviewer 覆盖全部 Gate A/B/C/D scope
- Verdict: **PASS_WITH_FINDINGS**

## Gate Summary

| Gate | Scope | Status |
|---|---|---|
| A | Small baseline real evaluation run — 3 clean fund-type slots | Accepted (controller judgment) |
| B | Multi-bundle JSONL validator fix + `_ScoreIssueRecordGroup` + `RQV_SCORE_ISSUE_ORPHANED` | Accepted (MiMo + GLM review/re-review) |
| C | `scripts/report_quality_eval.py` dev-only wrapper + tests | Accepted (controller judgment) |
| D | Control doc reconciliation + next escalation decision | Accepted (controller judgment) |

## Findings

### F1-未修复-确认residual-[低]-双重建索引可能产生重复 RQV_DUPLICATE_ID issue

- **入口/函数**: `validate_report_quality_jsonl` → `_validate_bundle_record` + `_validate_score_issue_records_against_bundle`
- **文件(行号)**: `fund_agent/fund/report_quality_validation.py:431`, `fund_agent/fund/report_quality_validation.py:529`
- **输入场景**: 任何含 score_issue 的 bundle 且该 bundle 内有重复 id
- **实际分支**: 两个函数各自独立调用 `_build_indexes`
- **预期行为**: 每个 bundle 的重复 id 只报告一次
- **实际行为**: 有 score_issue 的 bundle 可能对同一重复 id 报告两次
- **直接证据**: 行 431 `_validate_bundle_record(bundle_record, context)` 内部调用 `_build_indexes`；行 436-440 `_validate_score_issue_records_against_bundle(score_issue_record_group.bundle, ...)` 内部也调用 `_build_indexes`（行 529）。两次调用的 pointer 前缀不同（`line:N/bundle/...` vs `/bundle/...`）
- **影响**: 仅冗余 issue，不影响 `failed_closed` 判定或消费方行为
- **确认 residual**: (a) 仅在 bundle 实际存在重复 id 时出现，重复 id 本身已是异常状态；(b) pointer 前缀可区分来源；(c) 修复需跨函数传递 indexes，当前 slice 不值得引入结构变化
- **建议改法和验证点**: 后续 cleanup 可将 `_build_indexes` 结果缓存到 `_ScoreIssueRecordGroup`
- **修复风险（低）**: 低
- **严重程度（低）**: 不影响正确性

## Acceptance Criteria Assessment

逐项对照 controller judgment 的 10 项 readiness check：

| # | Readiness Item | Evidence | GLM Assessment |
|---|---|---|---|
| 1 | ≥3 fund_type_slot 覆盖 | Gate A artifact: `active_fund` (004393), `enhanced_index` (004194), `bond_fund` (006597) | PASS |
| 2 | 每个样本有 bundle/JSONL/validator summary/failure categories | Gate A artifact scratch output tables + validator summary tables | PASS |
| 3 | 至少一个 concrete quality fix | Gate B: multi-bundle JSONL validator ownership fix | PASS |
| 4 | Fix 直接对应 Gate A failure category | Gate A combined JSONL `RQV_REF_MISSING=4` → Gate B validator consumer fix | PASS |
| 5 | Focused tests / adjacent tests / ruff / diff check | 32 passed (28 validator + 4 dev-tool); ruff all passed; `git diff --check` passed | PASS |
| 6 | ≥2 independent review / re-review | MiMo + GLM initial review + re-review (4 artifacts total) | PASS |
| 7 | `docs/implementation-control.md` update | Current diff includes control doc reconciliation | PASS (in diff, pending commit) |
| 8 | Workspace clean | Pending commit of current diff; untracked review artifacts need disposition | PRE-COMMIT |
| 9 | Uncommitted scratch/report output | All scratch under `/tmp/...`, not in git status | PASS |
| 10 | Next path recommendation | Controller judgment: chapter contract + report writing quality upgrade design gate | PASS |

Items 1-7, 9-10 pass at code level. Item 8 is a pre-commit requirement, not a code review finding.

## Boundary Compliance

### No Product Default Behavior Changes

- `pyproject.toml`: no diff. Dev tool NOT registered as product CLI entry point.
- `fund_agent/ui/`: no diff. Product Typer CLI unchanged.
- `fund_agent/services/`: no diff. Service defaults unchanged.
- `fund_agent/fund/template/renderer.py`: no diff. Renderer unchanged.
- `fund_agent/fund/quality_gate.py`: no diff. FQ0-FQ6 unchanged.
- `fund_agent/fund/extraction_score.py`: no diff.

**Verified by**: `git diff -- pyproject.toml fund_agent/ui/ fund_agent/services/ fund_agent/fund/quality_gate.py fund_agent/fund/extraction_score.py fund_agent/fund/template/renderer.py` → empty output.

### Dev-Only Tool Boundary

`scripts/report_quality_eval.py`:

- Imports only `fund_agent.fund.report_quality_validation` (two public validator functions). No forbidden imports.
- `grep` verification: no import of renderer, service, quality_gate, extraction_score, document repository, nav_data, or dayu.
- Uses `if __name__ == "__main__": raise SystemExit(main())` — not registered in `pyproject.toml` `[project.scripts]`.
- Requires explicit `--jsonl` or `--bundle` input paths; no auto-discovery of reports, cache, or fixtures.
- Writes to caller-chosen `--output` path only; no implicit file creation.
- Exit code is always 0 after writing summary; validator issues are expressed in the summary payload, not as process exit codes. This prevents misuse in CI gates.

### Validator Boundary

`fund_agent/fund/report_quality_validation.py`:

- Module docstring explicitly states: "只消费内存对象或 JSONL Mapping，不读取基金文档、不调用仓库、不改变模板渲染、不替代 FQ0-FQ6 质量门控"
- No new import added in this diff. All imports from `report_evidence.py` (types/schema version only).
- `RQV_SCORE_ISSUE_ORPHANED` is a new error code within the existing error code space, not a new validator concern.

### Scratch Outputs Not Tracked

- All Gate A scratch under `/tmp/fund-agent-small-baseline-real-eval-20260526/`.
- `git status --short` shows no tracked scratch outputs.
- `reports/` directory outputs are `.gitignore` excluded (confirmed by evidence-chain artifact).

## Dev Tool Walkthrough

### Entry: `main(argv)`

1. `_parse_args(argv)` → requires `--output`, at least one `--jsonl` or `--bundle`. argparse validates.
2. `_run_validations(jsonl_paths, bundle_paths, run_id)` → iterates explicit paths, calls existing validator APIs. Each call is independent.
3. `_build_output_payload(results)` → aggregates counts, serializes results.
4. `_write_output(output_path, payload)` → creates parent dirs, writes JSON.
5. Returns 0.

### Error paths:

- Missing input files: `FileNotFoundError` from validator or `_load_bundle_json` — propagates to caller.
- Invalid bundle JSON (non-object): `TypeError` from `_load_bundle_json` line type check — propagates.
- Invalid JSON syntax: `json.JSONDecodeError` from `json.load` — propagates.
- Missing args: `SystemExit(2)` from argparse.

All error paths are explicit exceptions that propagate to the caller. No silent failure, no swallowed errors. The script is dev-only and these exceptions are appropriate for a maintainer tool.

### `_build_output_payload` aggregation logic:

- `failed_closed = failed_closed or summary.failed_closed` — correct OR semantics. If any input failed closed, aggregate is failed closed.
- `issue_counts.update(dict(summary.error_code_counts))` — Counter update with dict. If two inputs have the same error code, counts are summed. Correct for aggregate summary.
- Per-input results are preserved in `inputs` array for drill-down.

## Control Doc Assessment

`docs/implementation-control.md` diff:

- Current gate updated to reflect Gate A/B/C completion.
- Next entry point updated to "escalation readiness check; if complete, chapter contract implementation + report writing quality upgrade design gate".
- Artifact table extended with 9 new entries covering all Gate A/B/C/D artifacts.
- Current Decisions section adds 3 new decision records (baseline evaluation, validator fix, dev tool).
- Next Entry Point section updated with readiness check questions and stop conditions.
- Accepted Evidence Index updated with new gate row.
- Historical Evidence Index unchanged (appropriate — new entries go to current index).

All updates are factual and match the artifacts reviewed. No architectural commitment beyond what the artifacts support.

## Test Coverage Assessment

### Gate B (validator fix): 28 tests

Previously reviewed and confirmed adequate:
- Single-bundle backward compatibility
- Multi-bundle happy path
- Cross-bundle reference rejection
- Pre-bundle score_issue fail-closed
- Existing fail-closed, enum, schema, scoring-ready tests unchanged

### Gate C (dev tool): 4 tests

| Test | Path Covered | Assessment |
|---|---|---|
| `test_eval_writes_summary_for_jsonl_and_bundle_inputs` | Happy path: JSONL + bundle → summary JSON | Validates output structure, record counts, run_id passthrough |
| `test_eval_reports_validator_issues_without_nonzero_exit` | Bundle with missing field → exit 0 + blocking issue in summary | Validates fail-closed issues are expressed in payload, not exit code |
| `test_eval_requires_explicit_input_path` | No input paths → SystemExit(2) | Validates argparse guard |
| `test_eval_rejects_non_object_bundle_json` | `[]` → TypeError | Validates JSON type guard |

Covered dimensions:
- Explicit input requirement
- Happy path aggregation
- Validator issue expression without nonzero exit
- Invalid JSON type rejection

Not covered but low risk:
- Multiple JSONL inputs with mixed pass/fail: aggregation logic is straightforward (Counter OR + list append)
- Missing file (FileNotFoundError): this is a standard Python exception, no custom logic to test
- `--run-id` passthrough to individual results: covered by first test asserting `run_id` in output

## Evidence Chain Integrity

Controller judgment references 9+ artifacts in a traceable chain:

```
Gate A run → Gate B fix evidence → MiMo review → GLM review → MiMo re-review → GLM re-review → Gate C dev-tool → Controller judgment
```

Each artifact records scope, boundary, validation commands, and results. The evidence-chain deepreview controller judgment covers committed-to-HEAD state and confirms no scope drift in committed changes.

The current uncommitted diff adds the Gate B/C/D production code, tests, and control doc updates. This final review covers that diff.

## Adversarial Failure Pass

1. **Dev tool in CI gate**: `report_quality_eval.py` always returns 0. Cannot be misused as a CI quality gate because it never fails the process. Validator issues are in the JSON payload only. Correct design.

2. **Dev tool auto-discovery**: No. Requires explicit `--jsonl` or `--bundle` paths. No glob, no directory scan, no default search paths. Cannot accidentally process unintended files.

3. **Dev tool writes to tracked paths**: Only writes to explicit `--output` path chosen by caller. No implicit writes. Parent dir creation (`mkdir -p`) is appropriate for scratch paths.

4. **`_ScoreIssueRecordGroup` mutation in loop**: `current_group` is reassigned per bundle. Previous groups are preserved in list. No dangling reference or shared state mutation across iterations. Correct.

5. **Control doc claims exceeding evidence**: Control doc claims "three clean fund-type slots" — matches Gate A artifact. Claims "multi-bundle validator fix" — matches Gate B artifact + reviews. Claims "dev-only tool not registered as product CLI" — verified by `pyproject.toml` no-diff. No claim exceeds evidence.

6. **Untracked review artifacts**: Controller judgment item 8 flags pre-existing untracked `docs/reviews/release-maintenance-deepreview-controller-judgment-20260526.md` as needing disposition. This is a pre-commit concern, not a code review finding.

No new blocker found.

## Open Questions

- 无

## Residual Risk

- **F1（双重建索引）**: 确认 residual。仅冗余 issue，不影响校验结论。后续 cleanup 可缓存 indexes
- **Index/QDII fallback recovery**: Gate A localized as `data/source extraction` failure category. Not addressed in this gate. Blocked until source recovery or candidate replacement
- **FOF data-gap**: Accepted as corpus selection / fund-type taxonomy residual. Not addressed in this gate
- **Durable baseline**: Blocked by non-`scoring_ready` samples, incomplete fact coverage, and fallback-blocked slots
- **Active-fund Chapter 3 renderer/report-writing emission**: Accepted contract wording exists but renderer does not yet emit it. Next gate must decide scope
- **"仅 score_issue 无 bundle" 无显式测试**: 结构覆盖等价（同一 `current_group is None` 代码路径），显式测试可提高可读性
