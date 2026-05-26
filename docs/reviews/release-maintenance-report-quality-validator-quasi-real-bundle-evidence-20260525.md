# Release Maintenance Report-Quality Validator Quasi-Real Bundle Evidence

> Date: 2026-05-25
> Gate: `report-quality validator quasi-real bundle evidence run`
> Role: release-maintenance evidence-run worker
> Status: evidence-only; no product-flow integration
> Rules truth: `AGENTS.md`
> Design truth: `docs/design.md`
> Control truth: `docs/implementation-control.md` Startup Packet / Current Truth Guardrails / Current gate / Next entry point
> Accepted plan: `docs/reviews/release-maintenance-report-quality-validator-integration-decision-plan-20260525.md`
> Plan review: `docs/reviews/plan-review-20260525-235520.md`
> Plan re-review: `docs/reviews/plan-rereview-20260525-235615.md`

## Scope

本 artifact 记录一次受限的 report-quality validator 准真实输入 evidence run。唯一 tracked 输出是本文档。

Scratch 输出只写入：

- `/tmp/fund-agent-report-quality-validator-real-bundle-20260525/input.jsonl`
- `/tmp/fund-agent-report-quality-validator-real-bundle-20260525/result.json`

这些 scratch 文件不是 durable fixture、不是 baseline、不是 tracked report，也不是产品功能入口。

## Input Provenance

输入 label 为 `quasi_real_review_evidence`。

手工组装依据：

| Source | Used facts |
|---|---|
| `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md` | `004393` / 2024 是 S0 clean active-fund candidate；FOF 保持 `data_gap`；fallback unknown candidates 不进入本输入 |
| `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md` | issue-oriented score schema、`N/A` / skipped / `chapter_summary` 语义、source boundary 和 review-state 语义 |
| `docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-20260525.md` | `004393` chapter 3 的 manager holding traceability pass；`turnover_rate` 为 current slice not handled 的 localized issue |
| `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md` | current `ReportEvidenceBundle` top-level shape、anchor/gap/issue id 约定、review status progression |
| Current validator serialization shape | `fund_agent.fund.report_quality_validation.validate_report_quality_bundle` / `validate_report_quality_jsonl` and `report_evidence_bundle.v0` |

本输入没有声明 `repository_verified`、`scoring_ready` 或 `accepted_baseline`。bundle-level `review_status` 为 `fact_prefill_reviewed`，用于证明 validator consumer contract 和 issue localization，不用于 durable baseline。

## Commands

| Step | Command | Exit code | Result |
|---|---|---:|---|
| Branch check | `git branch --show-current` | 0 | `codex/local-reconciliation` |
| Evidence run | `.venv/bin/python - <<'PY' ... PY` | 0 | Wrote `/tmp/fund-agent-report-quality-validator-real-bundle-20260525/input.jsonl`; called `validate_report_quality_bundle(...)`; called `validate_report_quality_jsonl(...)`; wrote `/tmp/fund-agent-report-quality-validator-real-bundle-20260525/result.json` |
| Result inspection | `jq '{run_id, source_path, bundle_record_count, score_issue_record_count, schema_version, record_lines, bundle_summary: .bundle_validation.summary, jsonl_summary: .jsonl_validation.summary, quasi_real_score_issues: [...]}' /tmp/fund-agent-report-quality-validator-real-bundle-20260525/result.json` | 0 | Confirmed values below |
| JSONL line count | `wc -l /tmp/fund-agent-report-quality-validator-real-bundle-20260525/input.jsonl` | 0 | `3` lines |

The evidence-run command imported only:

- `fund_agent.fund.report_quality_validation.validate_report_quality_bundle`
- `fund_agent.fund.report_quality_validation.validate_report_quality_jsonl`
- `fund_agent.fund.report_evidence.REPORT_EVIDENCE_SCHEMA_VERSION`

No annual report was fetched or parsed.

## Input Shape

| Field | Value |
|---|---:|
| `run_id` | `evidence:report-quality-validator-quasi-real-bundle:20260525` |
| `source_path` | `/tmp/fund-agent-report-quality-validator-real-bundle-20260525/input.jsonl` |
| `bundle_source_label` | `quasi_real_review_evidence:accepted-s0-s1-s2-review-artifacts:20260525` |
| `schema_version` | `report_evidence_bundle.v0` |
| `bundle_record_count` | 1 |
| `score_issue_record_count` | 2 |
| `record_lines.bundle` | `[1]` |
| `record_lines.score_issue` | `[2, 3]` |
| `review_status` | `fact_prefill_reviewed` |
| `summary.scoring_ready_record_count` | 0 |

JSONL line 1 is one `record_type="bundle"` record. Lines 2-3 are linked `record_type="score_issue"` records copied from the bundle's `score_issue_links` to exercise the JSONL score-issue consumer path against the same bundle-local ids.

## Validator Results

### Bundle API

Call:

```text
validate_report_quality_bundle(bundle, source_path="quasi_real_review_evidence:accepted-s0-s1-s2-review-artifacts:20260525", run_id="evidence:report-quality-validator-quasi-real-bundle:20260525")
```

| Field | Value |
|---|---:|
| `summary.total_records` | 1 |
| `summary.scoring_ready_record_count` | 0 |
| `summary.blocking_count` | 0 |
| `summary.material_count` | 0 |
| `summary.minor_count` | 0 |
| `summary.failed_closed` | `false` |
| `summary.error_code_counts` | `[]` |

### JSONL API

Call:

```text
validate_report_quality_jsonl(Path("/tmp/fund-agent-report-quality-validator-real-bundle-20260525/input.jsonl"), run_id="evidence:report-quality-validator-quasi-real-bundle:20260525")
```

| Field | Value |
|---|---:|
| `summary.total_records` | 3 |
| `summary.scoring_ready_record_count` | 0 |
| `summary.blocking_count` | 0 |
| `summary.material_count` | 0 |
| `summary.minor_count` | 0 |
| `summary.failed_closed` | `false` |
| `summary.error_code_counts` | `[]` |

Interpretation: the current validator accepts this manually assembled `quasi_real_review_evidence` bundle and the linked score-issue JSONL records without schema/content-validation failures. This proves consumer-contract compatibility for this quasi-real shape only; it does not prove extraction correctness, annual-report identity beyond accepted S0 evidence, durable baseline readiness, report writing quality, or product-flow readiness.

## Top Issue Table

Validator issue table:

| Error code | Severity | Record pointer | Record id | Field | Expected | Actual | Next owner |
|---|---|---|---|---|---|---|---|
| n/a | n/a | n/a | n/a | n/a | n/a | n/a | No validator issue emitted |

Quasi-real score issue table:

| Issue id | Chapter | Dimension | Status | Severity | Field | Evidence / gap refs | Next owner category |
|---|---|---|---|---|---|---|---|
| `issue:004393:2024:chapter_3:evidence_traceability:manager_holding:pass` | `chapter_3` | `evidence_traceability` | `pass` | n/a | `manager_alignment.manager_holding` | `anchor:004393:2024:reviewed_note:s1_dry_run:manager_holding` | `review_acceptance` |
| `issue:004393:2024:chapter_3:fact_coverage:turnover_rate:material` | `chapter_3` | `fact_coverage` | `issue` | `material` | `turnover_rate` | `gap:004393:2024:missing_fact:turnover_rate:not_reviewed_in_current_slice` | `chapter_contract` |

## Failure Classification

| Classification layer | Result | Evidence |
|---|---|---|
| Validator schema/content failure | none | `error_code_counts=[]`, `failed_closed=false` |
| Source fail-closed failure | none in this input | `source_failure_category=none`, no fallback candidate included |
| Scoring readiness | intentionally not claimed | `review_status=fact_prefill_reviewed`, `scoring_ready_record_count=0` |
| Quasi-real report-quality issue | `turnover_rate` gap | accepted S1 dry-run says current slice did not handle turnover; issue remains material and localized to `chapter_3` / `fact_coverage` |
| Dominant next gate category | `chapter_contract` first | current control decision says turnover stability wording must be constrained before deciding whether data extraction is required |

## Root Cause Hypothesis

Root cause hypothesis, limited to this evidence chain: the validator contract is not the blocker for this quasi-real input. The observable material issue is content readiness around active-fund chapter 3 wording: accepted S1 evidence has a reviewed `turnover_rate` gap, so a stable-process or style-consistency claim cannot be made unless the chapter explicitly states the gap or later review accepts turnover / style-change evidence.

This is a hypothesis from the same evidence used in the bundle. It does not infer production extractor behavior, because this gate did not call the extractor or annual-report repository.

## Fixable Items

| Item | Owner / future gate | Why |
|---|---|---|
| Add explicit chapter 3 gap wording constraint for active-fund stability / style-consistency claims | `chapter_contract` | Current accepted decision already says chapter-contract first |
| Decide whether turnover / style-change evidence is required for the exact claim | `chapter_contract`, then possibly `data_extraction` | Do not open extraction work until the accepted chapter contract requires the evidence |
| Keep manager holding traceability as a narrow accepted reviewed-row pass candidate | review acceptance / future scoring evidence | It passed validator refs and can remain a localized positive evidence example |

## Non-Fixable / Needs Decision

| Item | Required decision |
|---|---|
| FOF coverage | Need pure FOF evidence or QDII-FOF taxonomy / precedence gate; not resolved here |
| Fallback candidates `110020`, `017641`, `017970` | Need source reliability evidence to recover upstream failure category before durable baseline consideration |
| Durable fixture or accepted baseline promotion | Requires later curated-fixture / baseline gate |
| Service / CLI / renderer / FQ0-FQ6 integration | Requires separate boundary-reviewed product-flow gate |
| Host / Agent / Dayu runtime | Requires independent architecture gate |

## Boundary Proof

This run stayed inside Fund public validator APIs and scratch `/tmp` files.

Not performed:

- No `FundDocumentRepository` call.
- No annual-report fetch or parse.
- No PDF cache, source helper, downloader, source adapter, or production extractor call.
- No source, tests, README, renderer, Service, CLI, `quality_gate.py`, `extraction_score.py`, fixtures, tracked reports, Host/Agent/dayu, pyproject, or lockfile modification.
- No push, PR, GitHub mutation, file deletion, or durable baseline promotion.
- No `repository_verified`, `scoring_ready`, or `accepted_baseline` claim.

Boundary-sensitive keyword hits in this artifact are boundary assertions, non-goals, or validation command text, not integration claims.

## Scratch Non-Durable Fixture Statement

`/tmp/fund-agent-report-quality-validator-real-bundle-20260525/input.jsonl` and `/tmp/fund-agent-report-quality-validator-real-bundle-20260525/result.json` are scratch evidence only. They are not durable fixtures, not accepted baseline material, not renderer input, and not product-flow output. Reuse requires a later reviewed gate.

## Validation

Validation commands run after writing this artifact:

| Command | Exit code | Result |
|---|---:|---|
| `git diff --check` | 0 | Clean; no whitespace errors. |
| `git ls-files \| rg -n "report-quality-validator-real-bundle\|input\\.jsonl\|result\\.json"` | 1 | No tracked repo file matches the scratch directory or scratch JSON/JSONL filenames. |
| `git status --short` | 0 | Shows only `?? docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-evidence-20260525.md`. |
| `test -f /tmp/fund-agent-report-quality-validator-real-bundle-20260525/input.jsonl` | 0 | Scratch JSONL exists under `/tmp`. |
| `test -f /tmp/fund-agent-report-quality-validator-real-bundle-20260525/result.json` | 0 | Scratch result JSON exists under `/tmp`. |

`git ls-files | rg ...` returning exit code 1 is the expected no-match result for this check.
