# Release Maintenance Report-Quality Validator Dry-Run Evidence

> Date: 2026-05-25
> Gate: `report-quality validator dry-run evidence implementation`
> Role: implementation specialist
> Status: evidence-only; no product-flow integration
> Rules truth: `AGENTS.md`
> Control truth: `docs/implementation-control.md` Startup Packet and Next Entry Point
> Accepted plan: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-20260525.md`
> Controller judgment: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-controller-judgment-20260525.md`

## Scope

This artifact records a synthetic dry run of the accepted report-quality validator as a consumer contract over a minimal in-memory bundle and one scratch JSONL artifact.

Allowed tracked output for this gate is this Markdown file only. Scratch inputs are under:

- `/tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl`
- `/tmp/fund-agent-report-quality-validator-dry-run-20260525/result.json`

The scratch JSONL is outside the repository and outside tracked `reports/` or fixture paths.

## Commands

| Step | Command | Exit code | Result |
|---|---|---:|---|
| Environment probe | `python - <<'PY' ... PY` | 1 | Failed before validator execution because the non-venv interpreter lacked `httpx`, which is imported by the accepted module import chain. No repository, PDF, cache, source helper, downloader, extractor, or fetch function was called. |
| Dry-run execution | `.venv/bin/python - <<'PY' ... PY` | 0 | Constructed synthetic bundles, wrote `/tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl`, called `validate_report_quality_bundle(valid_bundle, run_id="dry-run:report-quality-validator:20260525")`, called `validate_report_quality_jsonl(Path("/tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl"), run_id="dry-run:report-quality-validator:20260525")`, and wrote summarized output to `/tmp/fund-agent-report-quality-validator-dry-run-20260525/result.json`. |
| Result inspection | `jq . /tmp/fund-agent-report-quality-validator-dry-run-20260525/result.json` | 0 | Confirmed run id, schema version, input shape, summary counts, and representative issue pointers below. |

The dry-run script imported only the accepted validator API and typed schema version constant:

- `fund_agent.fund.report_quality_validation.validate_report_quality_bundle`
- `fund_agent.fund.report_quality_validation.validate_report_quality_jsonl`
- `fund_agent.fund.report_evidence.REPORT_EVIDENCE_SCHEMA_VERSION`

## Input Shape

The JSONL artifact is a single-bundle artifact:

| Field | Value |
|---|---:|
| `jsonl_path` | `/tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl` |
| `bundle_record_count` | 1 |
| `bundle_record_lines` | `[1]` |
| `score_issue_record_count` | 1 |
| `score_issue_record_lines` | `[2]` |
| line 1 record | `record_type="bundle"`, `bundle_id="bundle:004393:2024:dry-run:malformed"` |
| line 2 record | `record_type="score_issue"`, `issue_id="issue:external-linked"` |

The optional score issue record on line 2 is linked to the single bundle and validates against the same bundle-local anchor id. No second bundle record was written.

## Valid Bundle Result

Call:

```text
validate_report_quality_bundle(valid_bundle, run_id="dry-run:report-quality-validator:20260525")
```

| Field | Value |
|---|---:|
| `run_id` | `dry-run:report-quality-validator:20260525` |
| `schema_version` | `report_evidence_bundle.v0` |
| `issue_count` | 0 |
| `summary.total_records` | 1 |
| `summary.scoring_ready_record_count` | 1 |
| `summary.blocking_count` | 0 |
| `summary.material_count` | 0 |
| `summary.minor_count` | 0 |
| `summary.failed_closed` | `false` |
| `summary.error_code_counts` | `[]` |

Interpretation: the accepted validator can consume the minimal valid bundle shape from the focused tests and returns a zero-issue `ReportQualityValidationResult`.

## JSONL Result

Call:

```text
validate_report_quality_jsonl(Path("/tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl"), run_id="dry-run:report-quality-validator:20260525")
```

| Field | Value |
|---|---:|
| `source_path` | `/tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl` |
| `run_id` | `dry-run:report-quality-validator:20260525` |
| `schema_version` | `report_evidence_bundle.v0` |
| `issue_count` | 19 |
| `summary.total_records` | 2 |
| `summary.scoring_ready_record_count` | 1 |
| `summary.blocking_count` | 14 |
| `summary.material_count` | 5 |
| `summary.minor_count` | 0 |
| `summary.failed_closed` | `true` |

`summary.total_records == 2` because the JSONL intentionally contains one bundle record plus one optional linked `score_issue` record. The single-bundle assertion is `bundle_record_count == 1`.

Error code counts:

| Error code | Count |
|---|---:|
| `RQV_CHAPTER_SUMMARY_SEMANTICS` | 4 |
| `RQV_FAIL_CLOSED_SOURCE` | 1 |
| `RQV_FALLBACK_CONFLICT` | 1 |
| `RQV_FIELD_MISSING` | 1 |
| `RQV_GAP_LINK_INCOMPLETE` | 3 |
| `RQV_NA_SEMANTICS` | 3 |
| `RQV_REF_MISSING` | 5 |
| `RQV_SCORING_READY_PRECONDITION` | 1 |

## Representative Issues

| Expected coverage | Code | Severity | Pointer | Record id | Expected | Actual | Interpretation |
|---|---|---|---|---|---|---|---|
| fallback conflict | `RQV_FALLBACK_CONFLICT` | blocking | `line:1/bundle/source_documents/0/fallback_allowed` | `doc:004393:2024:fallback_conflict` | `fallback_allowed must be True for not_found` | `failure_category=not_found, fallback_allowed=False, fallback_used=False` | A fallback-eligible upstream failure cannot claim fallback flags inconsistent with `source_failure_category`. |
| fail-closed source | `RQV_FAIL_CLOSED_SOURCE` | blocking | `line:1/bundle/source_documents/1/source_failure_category` | `doc:004393:2024:fail_closed` | `none, not_found, unavailable` | `schema_drift` | A fail-closed source is rejected as blocking. The same source document produced no `RQV_FALLBACK_CONFLICT`; the only fallback conflict in the result is for `source_documents/0`. |
| chapter summary semantics | `RQV_CHAPTER_SUMMARY_SEMANTICS` | blocking | `line:1/bundle/score_issue_links/0/status` | `issue:chapter-summary` | `skipped` | `N/A` | `chapter_summary` has canonical semantics and must use `skipped`, not `N/A`. |
| chapter summary concrete chapter | `RQV_CHAPTER_SUMMARY_SEMANTICS` | blocking | `line:1/bundle/score_issue_links/0/chapter_id` | `issue:chapter-summary` | `chapter_0..chapter_7` | `report_level` | `chapter_summary` must point to a concrete template chapter. |
| chapter summary explanation | `RQV_CHAPTER_SUMMARY_SEMANTICS` | material | `line:1/bundle/score_issue_links/0/reviewer_note` | `issue:chapter-summary` | `reviewer_note or problem` | `missing` | A skipped chapter summary must explain why it was skipped. |
| chapter summary severity | `RQV_CHAPTER_SUMMARY_SEMANTICS` | material | `line:1/bundle/score_issue_links/0/severity` | `issue:chapter-summary` | `None` | `minor` | A skipped chapter summary must not carry issue severity. |
| N/A reason | `RQV_NA_SEMANTICS` | material | `line:1/bundle/score_issue_links/1/na_reason` | `issue:na` | `na_reason or reviewer_note` | `missing` | Plain `N/A` records require an explicit reason or reviewer note. |
| N/A severity | `RQV_NA_SEMANTICS` | material | `line:1/bundle/score_issue_links/1/severity` | `issue:na` | `None` | `minor` | `N/A` is not an issue severity carrier. |
| N/A blocking gap | `RQV_NA_SEMANTICS` | blocking | `line:1/bundle/score_issue_links/1/data_gap_refs` | `issue:na` | `no blocking gap refs` | `gap:turnover` | A blocking data gap must be represented as an issue or blocked state, not hidden as `N/A`. |
| forward anchor ref | `RQV_REF_MISSING` | blocking | `line:1/bundle/facts/0/source_anchor_ids/0` | n/a | `existing id` | `anchor:missing` | Missing bundle-local anchor refs are localizable. |
| forward document ref | `RQV_REF_MISSING` | blocking | `line:1/bundle/facts/0/source_document_ids/0` | n/a | `existing id` | `doc:missing` | Missing bundle-local document refs are localizable. |
| forward issue gap ref | `RQV_REF_MISSING` | blocking | `line:1/bundle/score_issue_links/2/data_gap_refs/0` | n/a | `existing id` | `gap:missing` | Missing bundle-local data gap refs are localizable. |
| forward issue anchor ref | `RQV_REF_MISSING` | blocking | `line:1/bundle/score_issue_links/2/evidence_anchor_refs/0` | n/a | `existing id` | `anchor:missing` | Missing score issue evidence anchor refs are localizable. |
| anchor document ref | `RQV_REF_MISSING` | blocking | `line:1/bundle/evidence_anchors/0/document_id` | `anchor:004393:2024:annual_report:sec2:abc12345` | `existing document_id` | `doc:004393:2024:annual_report` | An anchor cannot point at a document absent from `source_documents`. |
| backlink gap to N/A issue | `RQV_GAP_LINK_INCOMPLETE` | blocking | `line:1/bundle/data_gaps/0/score_issue_ids` | `gap:turnover` | `issue:na` | empty | If an issue references a gap, the gap must back-link that issue. |
| backlink gap to material issue | `RQV_GAP_LINK_INCOMPLETE` | blocking | `line:1/bundle/data_gaps/0/score_issue_ids` | `gap:turnover` | `issue:gap` | empty | The same gap must back-link every score issue that references it. |
| blocked fact backlink | `RQV_GAP_LINK_INCOMPLETE` | blocking | `line:1/bundle/facts/0/data_gap_refs` | `fact:basic_identity` | `gap:turnover` | empty | A fact blocked by a related data gap must include the corresponding `data_gap_refs`. |
| scoring-ready precondition | `RQV_SCORING_READY_PRECONDITION` | blocking | `line:1/bundle/review_status` | `bundle:004393:2024:dry-run:malformed` | `all scoring_ready preconditions satisfied` | `corpus_id must not be ad_hoc; classified_fund_type must not be unknown; type_slot_membership_status must be matches_slot; annual report source_failure_category must be none; blocking data gaps must be resolved; quality_context.fq_gate_status must not be block; all facts must have review_status=reviewed` | Non-ready content cannot silently pass as `scoring_ready`. |

Two masking checks were confirmed from the result:

1. Fail-closed source masking: `doc:004393:2024:fail_closed` produced exactly `RQV_FAIL_CLOSED_SOURCE` at `source_documents/1/source_failure_category`; it did not also produce `RQV_FALLBACK_CONFLICT` for the same source document.
2. Chapter-summary masking: `issue:chapter-summary` produced only `RQV_CHAPTER_SUMMARY_SEMANTICS` rows; `RQV_NA_SEMANTICS` rows were emitted only for the separate `issue:na` record.

## Boundary Interpretation

This dry run proves only the consumer-contract behavior of the accepted validator:

- The public validator APIs can be called from a one-off command.
- A minimal valid bundle returns zero issues and stable summary fields.
- A single-bundle JSONL artifact returns structured issues with stable error codes, severities, record pointers, record ids, expected values, actual values, run id, schema version, source path, and summary counts.
- Representative negative cases route fallback consistency, fail-closed source handling, `chapter_summary`, `N/A`, forward refs, backlinks, and `scoring_ready` preconditions into localizable issues.

It does not prove extraction correctness, annual-report identity, report writing quality, durable baseline readiness, multi-bundle aggregation semantics, or product-flow integration.

## Insufficient Evidence / Non-Goals

The following were intentionally not performed:

- No real `FundDocumentRepository` call.
- No PDF/cache/source helper access, downloader, extractor, new fetch, or annual-report parsing.
- No Service, CLI, renderer, `quality_gate.py` FQ0-FQ6, `extraction_score.py`, tracked report, fixture, curated baseline, report writer, or user-facing command integration.
- No `fund_agent/host`, `fund_agent/agent`, `dayu.host`, `dayu.engine`, runner, ToolRegistry, ToolTrace, session/run lifecycle, memory, or outbox work.
- No `extra_payload`, `nav_data` projection, derived-calculation generation, fallback recovery, FOF taxonomy decision, or baseline corpus selection.

Boundary-check keyword hits in this artifact are expected only in this non-goal section and the validation section below. They are not implementation claims.

## Validation

Validation commands run after writing this artifact:

| Command | Exit code | Result |
|---|---:|---|
| `git status --short` | 0 | Shows this artifact as `?? docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md`. It also shows pre-existing unrelated untracked files: `docs/dayu-agent-timeline-analysis.md`, `docs/dayu-agent模板技术机制深度解析.md`, `docs/基金分析模板方法论对比.md`, and `review_report_20260525.md`. No source, tests, README, report, fixture, Service, CLI, renderer, config, Host/Agent, or Dayu file was modified by this gate. |
| `git diff --check` | 0 | Clean. |
| `rg -n "FundDocumentRepository|AnnualReportDocumentCache|AnnualReportPdfAdapter|documents\\.sources|annual_report_pdf|extra_payload|dayu\\.host|dayu\\.engine|nav_data|quality_gate|extraction_score|fund-analysis|reports/scoring-runs" docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md` | 0 | Matches occurred only in the non-goal list and this validation command table. These hits are boundary assertions, not product integration claims. |
| `git ls-files /tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md` | 128 | Git rejected the `/tmp` path as outside the repository, confirming the scratch JSONL is not inside the worktree. |
| `git ls-files \| rg -n "fund-agent-report-quality-validator-dry-run-20260525\|input\\.jsonl\|result\\.json"` | 1 | No tracked repo file matches the scratch directory or scratch JSON/JSONL filenames. |
| `test -f /tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl` | 0 | Scratch JSONL exists under `/tmp` for review. |
| `test ! -e /Users/maomao/fund-agent/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl` | 0 | No repo-local scratch JSONL exists at that path. |

Boundary-check keyword hits from `rg`:

```text
155:- No real `FundDocumentRepository` call.
157:- No Service, CLI, renderer, `quality_gate.py` FQ0-FQ6, `extraction_score.py`, tracked report, fixture, curated baseline, report writer, or user-facing command integration.
158:- No `fund_agent/host`, `fund_agent/agent`, `dayu.host`, `dayu.engine`, runner, ToolRegistry, ToolTrace, session/run lifecycle, memory, or outbox work.
159:- No `extra_payload`, `nav_data` projection, derived-calculation generation, fallback recovery, FOF taxonomy decision, or baseline corpus selection.
171:| `rg -n "FundDocumentRepository|AnnualReportDocumentCache|AnnualReportPdfAdapter|documents\\.sources|annual_report_pdf|extra_payload|dayu\\.host|dayu\\.engine|nav_data|quality_gate|extraction_score|fund-analysis|reports/scoring-runs" docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md` | 0 | Matches occurred only in the non-goal list and this validation command table. These hits are boundary assertions, not product integration claims. |
```

This satisfies the plan's boundary check because every hit appears only where the artifact explicitly records non-goals or the boundary-validation command itself.
