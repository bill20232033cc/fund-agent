# Evidence: Quality Warning Issue Identity Evidence Gate

Date: 2026-06-12

Role: controller evidence owner

Gate: `Quality warning issue identity evidence gate`

Classification: `standard`

Verdict target: establish accepted identity for the three quality-gate issues observed in the controlled live annual-period narrative evidence chain. This artifact does not implement a fix and does not change source, tests, runtime behavior, source acquisition policy, release state, PR state, cleanup state or readiness state.

## 1. Accepted Inputs And Boundaries

Accepted inputs:

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-quality-warning-issue-root-cause-plan-controller-judgment-20260612.md`
- checkpoint `56c71d9`
- control-sync checkpoint `2c973c9`
- user live authorization for this gate

Boundary:

- no source/test/runtime behavior modification
- no fallback/source expansion
- no provider/LLM/readiness/release/PR action
- no cleanup/delete/move/archive/import/ignore
- no use of arbitrary pre-existing untracked `reports/` residue as proof
- one controlled live reproduction command only after no-live lineage failed

## 2. E0 Workspace And Diff Guard

| Check | Result |
|---|---|
| Branch | `feat/mvp-llm-incomplete-run-artifacts` |
| `git status --short` | Exit `0`; only pre-existing unrelated untracked residue before this evidence artifact |
| `git status --branch --short` | Exit `0`; branch ahead of origin; only pre-existing unrelated untracked residue before this evidence artifact |
| `git diff --name-only` | Exit `0`; no tracked diff before this evidence artifact |
| `git diff --check` | Exit `0`; no whitespace errors before this evidence artifact |

## 3. E1 No-live Durable Lineage Check

Command:

```bash
rg -n "quality_gate_status|quality_gate_issues|quality_gate_json|quality_gate_md|rule_code|field_name|hash|size|run_id" docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-20260612.md docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-controller-judgment-20260612.md docs/reviews/mvp-live-evidence-ready-state-disposition-controller-judgment-20260612.md docs/reviews/mvp-quality-warning-issue-root-cause-plan-controller-judgment-20260612.md
```

Result:

- accepted artifacts contain `quality_gate_status=warn`, `quality_gate_issues=3` and accepted live `run_id`
- accepted artifacts do not contain the three issue rows
- accepted artifacts do not contain `quality_gate_json` / `quality_gate_md` path plus hash/size/run identity sufficient to accept issue rows

Disposition:

`BLOCKED_BY_ARTIFACT_LINEAGE_GAP`.

No-live evidence proves the warning count, not the warning identities. Per the accepted root-cause plan, path-exists-only use of mutable `reports/` residue is rejected.

## 4. E3 Controlled Live Reproduction

Because E1 could not establish durable issue identities and the user authorized this live gate, the controller ran the accepted one-command live reproduction.

Temp capture directory:

`/tmp/fund-agent-quality-warning-identity-20260612-F2MCCQ`

Command:

```bash
uv run fund-analysis analyze-annual-period 004393 --target-year 2025 --start-year 2021 --valuation-state unavailable --quality-gate-policy warn --force-refresh > /tmp/fund-agent-quality-warning-identity-20260612-F2MCCQ/stdout.md 2> /tmp/fund-agent-quality-warning-identity-20260612-F2MCCQ/stderr.txt
```

Result:

| Field | Value |
|---|---|
| Exit code | `0` |
| stdout size | `46287` bytes |
| stderr size | `257` bytes |
| `quality_gate_status` | `warn` |
| `quality_gate_issues` | `3` |
| `quality_gate_json` | `reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/quality_gate.json` |
| `quality_gate_md` | `reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/quality_gate.md` |

Header facts captured from stdout:

| Field | Value |
|---|---|
| `fund_code` | `004393` |
| `target_year` | `2025` |
| `canonical_years` | `2025,2024,2023,2022,2021` |
| `available_years` | `2025,2024,2023,2022,2021` |
| `gap_years` | empty |
| `fail_closed_years` | empty |
| `cross_year_fact_count` | `3` |
| `fallback_year_count` | `0` |
| 2025-2021 source lines | all `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`, `fallback_used=false` |

The command generated current-gate artifacts. These paths are not staged and are not promoted as source truth or release evidence; they are used here only with hash/size lineage for the issue identity evidence gate.

## 5. Artifact Identity

| Artifact | Size | SHA-256 |
|---|---:|---|
| `reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/quality_gate.json` | `3302` | `a63e7a82d47cce6de1208e7aa4684895a72556f4474733e5121fdb23cdca665d` |
| `reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/quality_gate.md` | `1460` | `be3082051b8d28f7d00454fb5a539723a5754db8cb90030cf7e0ce1a42a5d503` |
| `reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/score.json` | `147520` | `bb66ed889d10aca62a5a11a7e58fd9752f77562cc3c7e2850efbc20dc9ac14b5` |
| `reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/snapshot.jsonl` | `26925` | `f5e0fd3783f0ede807d1f9797644e2a81c48b214d831325baf75f497b0e8230f` |

`quality_gate.json` metadata:

- `score_path`: `reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/score.json`
- `output_dir`: `None`
- `gate_json_path`: `None`
- `gate_markdown_path`: `None`
- `rule_results_count`: `1`

## 6. Accepted Issue Identity Candidates

| # | Rule | Severity | Fund | Field | Reason | Coverage scope | Message |
|---:|---|---|---|---|---|---|---|
| 1 | `FQ2` | `warn` | `None` | `turnover_rate` | `None` | `None` | `P1 关键字段 \`turnover_rate\` coverage/traceability 未达标，报告应提示数据不足` |
| 2 | `FQ2F` | `warn` | `004393` | `None` | `None` | `None` | `基金 \`004393\` 存在 P1 字段失败；失败字段：turnover_rate` |
| 3 | `FQ0` | `info` | `004393` | `None` | `year_not_covered` | `year_not_covered` | `基金 \`004393\` 已有 strict golden answer 记录，但当前年报年份尚未覆盖；本次 correctness oracle 不使用其它年份 golden answer。` |

Status interpretation:

- `quality_gate_issues=3` counts all issues, including the `FQ0/info` issue.
- `quality_gate_status=warn` because there is at least one warn issue and no block issue in this reproduction.
- The two warn issues are `FQ2` and `FQ2F`; the third issue is informational `FQ0`.

## 7. Minimal Score Evidence

`score.json` field/fund summaries:

| Evidence row | Value |
|---|---|
| `turnover_rate` field score | `coverage_rate=0.0`, `covered_records=0`, `field_group=manager`, `field_name=turnover_rate`, `priority=P1`, `records=1`, `status=fail`, `traceability_rate=0.0`, `traceable_records=0` |
| `004393` fund score | `app_category=国内股票类`, `fund_code=004393`, `fund_name=安信企业价值优选混合A`, `p0_failed_fields=[]`, `p0_status=pass`, `p1_failed_fields=["turnover_rate"]`, `p1_status=fail`, `records=16`, `status=fail` |
| correctness summary | `coverage_reason=year_not_covered`, `coverage_scope=year_not_covered`, `coverage_required=false`, `golden_answer_path=reports/golden-answers/golden-answer.json`, `missing_fund_codes=["004393"]`, `total_records=150`, `unavailable_records=150`, `comparable_records=0` |

The large `correctness.record_results` body was intentionally not copied into this artifact; the accepted issue identity only requires the summary fields above.

## 8. Static Code/Test Mapping

| Evidence | Location | Interpretation |
|---|---|---|
| `turnover_rate` is a P1 quality field | `fund_agent/fund/extraction_score.py:51` | A `turnover_rate` extraction/traceability miss maps to P1 severity |
| P1 field fail creates `FQ2` warn | `fund_agent/fund/quality_gate.py:600` to `fund_agent/fund/quality_gate.py:606` | Explains issue 1 severity and field |
| P1 fund fail creates `FQ2F` warn | `fund_agent/fund/quality_gate.py:650` to `fund_agent/fund/quality_gate.py:656` | Explains issue 2 as aggregate derivative of P1 field failure |
| correctness coverage creates `FQ0/info` | `fund_agent/fund/quality_gate.py:469` to `fund_agent/fund/quality_gate.py:478` | Explains issue 3 severity/reason path |
| missing turnover remains warn, not block | `tests/services/test_fund_analysis_service.py:1399` to `tests/services/test_fund_analysis_service.py:1426` | Existing deterministic test covers FQ2/FQ2F warn semantics |
| `year_not_covered` remains `FQ0/info` | `tests/fund/test_quality_gate.py:634` to `tests/fund/test_quality_gate.py:697` | Existing deterministic test covers FQ0/info semantics |

## 9. Root-cause Candidate Disposition

| Issue | Direct evidence | Candidate owner | Next handling |
|---|---|---|---|
| `FQ2/warn` `turnover_rate` | score row says P1 `turnover_rate` has `coverage_rate=0.0`, `traceability_rate=0.0`, `status=fail` | Fund extractor / traceability owner | `Turnover rate extraction/traceability root-cause planning gate`; do not implement in this evidence gate |
| `FQ2F/warn` `004393` | fund score says `p1_failed_fields=["turnover_rate"]`, `p1_status=fail` | Quality gate + Fund extractor owner | Same next gate; derivative aggregate, not a separate root cause |
| `FQ0/info` `year_not_covered` | correctness summary says current year is not covered by strict golden answer | golden/readiness owner | Deferred `Strict golden 2025 coverage/promotion planning gate`; not an extractor issue and not a live extraction failure |

## 10. Residuals

| Residual | Owner | Blocks readiness? | Next gate |
|---|---|---|---|
| `turnover_rate` P1 coverage/traceability failure | Fund extractor / traceability owner | Yes | `Turnover rate extraction/traceability root-cause planning gate` |
| `FQ2F` aggregate fund-level warning | Quality gate + Fund extractor owner | Yes, until underlying P1 failure is dispositioned | `Turnover rate extraction/traceability root-cause planning gate` |
| strict golden current-year coverage gap | golden/readiness owner | Yes for readiness/promotion | `Strict golden 2025 coverage/promotion planning gate` |
| broader live sample coverage not proven | release/evidence owner | Yes for broader readiness | separate controlled live sample gate |
| PR/release/readiness state unchanged | release owner/controller | Yes | separate PR/release/readiness gate |

## 11. Gate Result

This evidence establishes current-gate accepted issue identity candidates for review:

- `FQ2/warn` on P1 `turnover_rate`
- `FQ2F/warn` for fund `004393`, derived from `turnover_rate`
- `FQ0/info` with `reason=year_not_covered`

Release/readiness remains **`NOT_READY`**.

Recommended next mainline after review/controller acceptance:

`Turnover rate extraction/traceability root-cause planning gate`

Deferred entries:

- `Strict golden 2025 coverage/promotion planning gate`
- additional controlled live sample gate
- provider/LLM readiness gate
- cleanup/delete/archive/import/ignore gate
- PR/push/merge/mark-ready/release external-state gate
