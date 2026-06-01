# Release Maintenance QDII Replacement Candidate Evidence - 096001 / 2024

## Startup Packet Replay

- Role: evidence worker, not controller.
- Current phase: release maintenance.
- Current gate from Startup Packet: QDII replacement candidate evidence plan accepted locally.
- Current next entry point: QDII replacement candidate evidence gate.
- Latest accepted checkpoint before this task: `fe2ea65 docs: accept qdii replacement evidence plan`.
- Accepted plan: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-20260527.md`.
- Accepted plan controller judgment: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-controller-judgment-20260527.md`.
- Scope executed here: bounded public evidence gate for exactly `fund_code=096001`, `report_year=2024`.
- This follows the accepted next entry point. It is not a gate switch.

## Review-Block Fix History

- Initial evidence artifact incorrectly treated CLI stdout as the only public snapshot output and stopped with a non-matrix terminal classification.
- Independent evidence reviews both blocked that artifact:
  - `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-review-ds-20260527.md`
  - `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-review-glm-20260527.md`
- Accepted controller continuation action: fix this same evidence artifact and complete the same bounded evidence gate.
- Fix applied here: read only the public generated files from this evidence run, record the correct provenance tuple, continue through the accepted score and quality-gate commands, and classify by the accepted plan matrix.

## Guardrails Followed

- No fallback candidates were run.
- No promotion was attempted.
- `096001` was not promoted to source-safe, scoring-ready, baseline, golden, or accepted replacement.
- No direct PDF, cache, source-helper, downloader, source-adapter, or external web inspection was used.
- No code, tests, README, design doc, control doc, fixtures, golden files, baseline corpus, renderer, FQ0-FQ6, Service/CLI defaults, FundDocumentRepository, taxonomy, extractor, Host/Agent/dayu files were changed.
- Only this tracked evidence artifact was created/updated.

## Candidate Identity

- `fund_code`: `096001`
- `fund_name`: `大成标普500等权重指数(QDII)A人民币`
- `app_category`: `海外股票类`
- `report_year`: `2024`
- `classified_fund_type`: `qdii_fund`
- Snapshot result: `succeeded_funds=1`, `failed_funds=0`, `snapshot_records=16`.
- `errors.jsonl`: empty.

## Commands

| # | Command | Exit Code | Result |
|---|---|---:|---|
| 1 | `uv run fund-analysis extraction-snapshot --help` | 0 | Help succeeded. Required flags matched the accepted command shape. |
| 2 | `uv run fund-analysis extraction-score --help` | 0 | Help succeeded. Required flags matched the accepted command shape. |
| 3 | `uv run fund-analysis quality-gate --help` | 0 | Help succeeded. Required flags matched the accepted command shape. |
| 4 | `uv run fund-analysis extraction-snapshot --run-id qdii-replacement-candidate-096001-2024-20260527 --report-year 2024 --fund-code 096001 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527 --force-refresh` | 0 | Snapshot generation succeeded. |
| 5 | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/snapshot.jsonl --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527 --errors-path reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/errors.jsonl` | 0 | Score generation succeeded. |
| 6 | `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/score.json --output-dir reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527` | 0 | Quality gate generation succeeded with `status: block`, `issues: 10`. |
| 7 | `git diff --check` | 0 | Passed. |
| 8 | `git status --short` | 0 | Reports directory did not appear in status output; generated report outputs remain ignored/not tracked by this evidence run. |

## Generated Scratch Outputs

The snapshot command printed these output paths:

- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/snapshot.jsonl`
- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/summary.md`
- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/errors.jsonl`

The score command printed these output paths:

- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/score.json`
- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/score.md`
- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/golden_set.json`

The quality-gate command printed these output paths:

- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/quality_gate.json`
- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/quality_gate.md`

`git status --short` output after completing score and quality-gate:

```text
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md
?? docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-20260527.md
?? docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-review-ds-20260527.md
?? docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-review-glm-20260527.md
?? docs/reviews/repo-review-20260526-231040.md
?? docs/tmux-agent-memory-store.md
```

Interpretation:

- No `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527` path appeared in `git status --short`.
- Existing unrelated untracked docs and the two review artifacts were observed and left untouched.
- The only tracked-intended artifact updated by this evidence continuation is `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-20260527.md`.

## CLI Mismatch Check

- `extraction-snapshot --help`: no flag mismatch observed.
- `extraction-score --help`: no flag mismatch observed.
- `quality-gate --help`: no flag mismatch observed.
- `terminal_classification` is not `cli_flag_mismatch_not_run`.

## Public Source Provenance

Public provenance was read only from generated snapshot outputs:

- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/summary.md`
- `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/snapshot.jsonl`

Recorded provenance tuple:

| Field | Value |
|---|---|
| `source_provenance_schema_version` | `repository_source_provenance.v1` |
| `source_strategy` | `primary_then_fallback` |
| `resolved_source` / `resolved_source_name` | `eastmoney` |
| `fallback_used` | `true` |
| `primary_failure_category` | `unavailable` |
| `fallback_eligibility` | `eligible` |
| `source_provenance_status` | `complete` |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` |

Interpretation:

- The public generated `summary.md` Source Provenance table shows `resolved_source_name=eastmoney`, `fallback_used=true`, `fallback_eligibility=eligible`, `source_provenance_status=complete`.
- The public generated `snapshot.jsonl` records show `primary_failure_category=unavailable` and the same complete provenance tuple.
- This is eligible under the accepted plan because fallback was used only after `primary_failure_category=unavailable`, with public `fallback_eligibility=eligible` and complete provenance.
- No public provenance value showed `schema_drift`, `identity_mismatch`, or `integrity_error`.
- Therefore the run correctly continued to score and quality-gate after this fix.

## Score Summary

- `field_count`: 14
- `fund_count`: 1
- `failed_fund_count`: 0
- `p0_status`: `fail`
- `status_counts`: `pass=7`, `fail=7`
- Correctness oracle: `unavailable`; strict golden answer was not configured.
- Fund score for `096001`: `p0_status=fail`, `p1_status=fail`, `status=fail`.
- P0 failed fields: `nav_benchmark_performance`.
- P1 failed fields: `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`.
- Fund quality: `app_category_status=match`, `preferred_lens_status=resolved`, `preferred_lens_key=qdii_fund`, `missing_field_rate=42.9%`.

## Quality Gate

- `quality_gate_status`: `block`
- `issue_count`: 10
- `rule_result_count`: 1

P0/blocking issues:

| Rule | Severity | Fund | Field | Message |
|---|---|---|---|---|
| `FQ2` | `block` |  | `nav_benchmark_performance` | P0 required field coverage/traceability did not meet threshold. |
| `FQ3` | `block` |  | `nav_benchmark_performance` | P0 required field evidence anchors were insufficient. |
| `FQ2F` | `block` | `096001` |  | Single-fund report usability blocked because P0 field failed: `nav_benchmark_performance`. |
| `FQ4` | `block` | `096001` |  | Snapshot missing-field rate was too high for report usability. |

P1/warn issues:

| Rule | Severity | Fund | Field(s) | Message |
|---|---|---|---|---|
| `FQ2` | `warn` |  | `turnover_rate` | P1 key field coverage/traceability did not meet threshold. |
| `FQ2` | `warn` |  | `holder_structure` | P1 key field coverage/traceability did not meet threshold. |
| `FQ2` | `warn` |  | `holdings_snapshot` | P1 key field coverage/traceability did not meet threshold. |
| `FQ2` | `warn` |  | `share_change` | P1 key field coverage/traceability did not meet threshold. |
| `FQ2F` | `warn` | `096001` | `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change` | Single fund has P1 field failures. |

Informational issue:

- `FQ0`: strict golden answer was not configured, so correctness oracle was not executed.

Rule result:

- `FQ5`: `resolved`; App category `海外股票类` matches fund type `qdii_fund`; 8 template chapters resolved preferred_lens and ITEM_RULE deterministic applicability evaluation completed.

## Manager Strategy Text

- `manager_strategy_text` status in score: `pass`.
- Coverage: `100.0%`.
- Traceability: `100.0%`.
- It is not the P0 blocker in this evidence run.

## False-Positive Suspicion

- No false-positive suspicion is asserted from this evidence worker pass.
- The public outputs show a real quality block caused by missing/anchor-insufficient fields, especially P0 `nav_benchmark_performance`, plus high missing-field rate.
- Because this worker did not inspect PDFs or internal source/cache/downloader details, the artifact does not claim whether the missing fields are disclosure gaps or extractor gaps.

## Required Next Action

Controller should treat `096001 / 2024` as public-provenance eligible but not baseline-ready. Before any promotion or replacement acceptance, a separate authorized gate must resolve or explicitly accept the P0 `nav_benchmark_performance` failure and FQ4 missing-field-rate block, and address P1 residuals for `turnover_rate`, `holder_structure`, `holdings_snapshot`, and `share_change`.

## Terminal Classification

- `terminal_classification`: `quality_blocked_after_provenance`
- `promotion_disposition`: `not_promoted`
