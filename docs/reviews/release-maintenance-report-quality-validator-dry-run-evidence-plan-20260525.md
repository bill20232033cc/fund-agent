# Release Maintenance Report-Quality Validator Dry-Run Evidence Plan

> Date: 2026-05-25
> Gate: `report-quality validator dry-run evidence planning`
> Role: planning specialist
> Status: planning-only; not approved for implementation
> Truth sources: `AGENTS.md`, `docs/design.md` §5.4 / §5.4.1 / §5.4.2 / §9.1 / §10, `docs/implementation-control.md` Startup Packet and Next Entry Point, `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-controller-judgment-20260525.md`

## 1. Scope / Non-Goals

This gate is planning-only. It may produce this plan artifact under `docs/reviews/`, but it must not modify source code, tests, README files, tracked reports, curated fixtures, Service, CLI, renderer, FQ0-FQ6, Host/Agent packages, Dayu dependencies, or production configuration.

The next implementation agent may execute the dry-run evidence plan only after controller acceptance of this plan. Until that controller judgment exists, this plan is not an implementation authorization.

The dry run must answer one narrow question from first principles: can the accepted validator be consumed as a report-quality scoring input contract over `ReportEvidenceBundle` / JSONL content, with reproducible issue localization and summary counts, before any product-flow integration?

Non-goals:

1. No Service, CLI, renderer, `quality_gate.py` FQ0-FQ6, `extraction_score.py`, report writer, or user-facing command integration.
2. No tracked `reports/` output, no durable baseline promotion, no golden answer update, no curated JSON fixture.
3. No PDF/cache/source helper access, no new data fetch, no annual-report parsing, and no `FundDocumentRepository` call for this dry run.
4. No `fund_agent/host`, `fund_agent/agent`, `dayu.host`, `dayu.engine`, runner, ToolRegistry, ToolTrace, session/run lifecycle, or outbox work.
5. No `nav_data` mapping, derived-calculation generation, fallback recovery, FOF taxonomy decision, or baseline corpus selection.
6. No `extra_payload`; any one-off helper must pass explicit arguments only.

## 2. Input Selection

Default input should be existing fake/minimal `ReportEvidenceBundle` JSON-like records derived from the already accepted validator test shapes, not production documents. This is the minimum useful input because it exercises the validator's consumer contract without pretending to prove extraction correctness or report-quality scoring readiness.

Recommended default:

1. Build an in-memory minimal valid bundle equivalent to `tests/fund/test_report_quality_validation.py::_valid_bundle_dict()`.
2. Use `validate_report_quality_bundle(valid_bundle)` on that in-memory object to prove the zero-issue positive path. Do not write the valid bundle into the JSONL dry-run artifact by default.
3. Serialize one scratch JSONL file containing exactly one malformed `record_type="bundle"` record. That single bundle may include nested `score_issue_links`, `data_gaps`, `source_documents`, facts, and anchors constructed to exercise representative issue categories.
4. Optional `record_type="score_issue"` lines may be added to the same JSONL only when they are validated against the single bundle record in that artifact. They must not require a second bundle record.
5. Construct representative issues inside that one malformed bundle:
   - fallback inconsistency to produce exactly one canonical `RQV_FALLBACK_CONFLICT`;
   - fail-closed source handling, using `source_failure_category="schema_drift"`, `"identity_mismatch"`, or `"integrity_error"` with conflicting fallback flags to prove `RQV_FAIL_CLOSED_SOURCE/blocking` is emitted and not masked by fallback conflict handling;
   - `chapter_summary` semantics without duplicate `RQV_NA_SEMANTICS`;
   - `N/A` semantics with missing `na_reason` / `reviewer_note`;
   - forward reference integrity, such as missing anchor or missing data gap refs, to produce `RQV_REF_MISSING`;
   - backlink completeness, such as a gap / issue / fact relationship missing its reverse link, to produce `RQV_GAP_LINK_INCOMPLETE`;
   - `scoring_ready` precondition failure.
6. If the implementation needs separate negative variants that cannot coherently fit in one malformed bundle, call `validate_report_quality_bundle()` on additional in-memory variants or write separate `/tmp` JSONL files. Each JSONL file must contain at most one `record_type="bundle"` record. The default evidence path should not put multiple bundle records in one JSONL file.
7. Keep all input values synthetic and small. Fund code `004393` may appear only as a fake identifier already used by tests; the dry run must not imply fresh repository verification or annual-report evidence.

Allowed alternative, only if the implementation agent can do it without new data access:

1. Use an existing in-memory `report_evidence` projection path with deterministic fake `StructuredFundDataBundle` data already present in tests.
2. Write the projection output only to `/tmp` or another untracked scratch directory.
3. Do not call `FundDocumentRepository`, PDF/cache code, source helper, downloader, or extractor over real documents.

Rejected inputs:

1. Newly fetched annual reports.
2. Any production PDF, cache, source helper, Eastmoney/EID fallback, or repository lookup.
3. New durable fixture under `tests/fixtures/`, `docs/fixtures/`, or any curated baseline directory.
4. Existing or new tracked `reports/scoring-runs/` artifacts.

## 3. Output Artifact Policy

The implementation output should be one tracked Markdown evidence artifact:

`docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md`

That artifact must record commands, scratch paths, input shape summaries, validator API calls, summary counts, representative issues, interpretation, and boundary checks. It must not embed a large JSONL fixture; short excerpts are allowed only when needed to explain a specific issue pointer.

Scratch JSONL is allowed only in `/tmp` or an untracked temporary directory, for example:

`/tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl`

The implementation agent must remove or ignore scratch files before final status if they are under the repository. If any scratch directory is created under the repo for debugging, it must remain untracked and must not be under `reports/`, curated fixtures, or package data.

## 4. Dry-Run Verification Steps

The implementation agent should execute the dry run with a one-off Python command or a temporary local script that is not committed. The command may import only `fund_agent.fund.report_quality_validation` and existing typed constants/dataclasses if useful.

Required calls:

1. `validate_report_quality_bundle(valid_bundle, run_id="dry-run:report-quality-validator:20260525")`
2. `validate_report_quality_jsonl(Path("/tmp/.../input.jsonl"), run_id="dry-run:report-quality-validator:20260525")`

The JSONL file used in the second call must be a single-bundle artifact: exactly one `record_type="bundle"` record plus optional `record_type="score_issue"` records linked to that same bundle. It must not contain a valid bundle plus separate malformed bundle variants in the same file.

The Markdown evidence must include:

1. Exact command(s) and exit code.
2. Scratch JSONL location and statement that it is untracked and outside `reports/`.
3. For the valid bundle call:
   - `summary.total_records`
   - `summary.scoring_ready_record_count`
   - `summary.blocking_count`
   - `summary.material_count`
   - `summary.minor_count`
   - `summary.failed_closed`
   - issue count equals zero.
4. For the JSONL call:
   - parsed `bundle_record_count` assertion, with `bundle_record_count == 1`;
   - bundle record line number, for example `bundle_record_lines=[1]`;
   - parsed `score_issue_record_count`; if optional score issue lines exist, record their line numbers;
   - `summary.total_records`
   - `summary.scoring_ready_record_count`
   - `summary.error_code_counts`
   - `summary.blocking_count`, `material_count`, `minor_count`
   - `summary.failed_closed`
   - inferred or explicit `run_id`
   - `schema_version`
5. Representative issue table with at least:
   - fallback conflict: `RQV_FALLBACK_CONFLICT`, blocking, stable pointer under `source_documents`;
   - fail-closed source: `RQV_FAIL_CLOSED_SOURCE`, blocking, using `schema_drift`, `identity_mismatch`, or `integrity_error`; the evidence must show it is not hidden by `RQV_FALLBACK_CONFLICT` for the same source document;
   - `chapter_summary`: `RQV_CHAPTER_SUMMARY_SEMANTICS`, canonical issue only, with no duplicate `RQV_NA_SEMANTICS` for the same malformed `chapter_summary` record;
   - `N/A`: `RQV_NA_SEMANTICS`, material or blocking according to the current validator semantics, with missing `na_reason` / `reviewer_note` pointer;
   - forward reference integrity: `RQV_REF_MISSING`, with pointer to the bad ref;
   - backlink completeness: `RQV_GAP_LINK_INCOMPLETE`, with pointer to the incomplete gap / issue / fact link;
   - `scoring_ready` precondition: `RQV_SCORING_READY_PRECONDITION`, blocking, showing that non-ready content cannot silently pass as scoring-ready.
6. A short note that issue examples prove consumer-contract behavior only: parsing, enum/domain checks, stable pointers, severity counts, and id-link integrity.

The evidence should not assert that the current report pipeline is ready to consume the validator. It may only state that the validator can be invoked over bundle / JSONL content and returns structured, localizable results.

## 5. Acceptance Criteria

Sufficient evidence for "validator is consumable as a contract":

1. Both public APIs run successfully from a one-off command without source or test changes.
2. The valid minimal bundle returns zero issues and stable summary counts.
3. The JSONL dry run uses a single-bundle artifact and returns deterministic `ReportQualityValidationResult` fields: `summary`, `issues`, `run_id`, `schema_version`, and `source_path`.
4. The evidence records blocking/material/minor counts and `error_code_counts`.
5. Representative issues cover fallback consistency, fail-closed source handling, `chapter_summary`, `N/A`, forward reference integrity, backlink completeness, and `scoring_ready` preconditions.
6. Issue records include stable `error_code`, `severity`, `record_pointer`, `record_type` or source path where applicable, and enough `expected` / `actual` detail for a downstream scoring consumer to reject or route the input.
7. Boundary validation proves no tracked reports, durable fixtures, Service/CLI/renderer/FQ0-FQ6 integration, PDF/cache/source helper, `FundDocumentRepository`, Host/Agent/dayu, `nav_data`, or `extra_payload` work occurred.

Insufficient evidence for product-flow integration:

1. Passing this dry run does not prove extraction correctness, annual-report identity, renderer quality, FQ0-FQ6 compatibility, baseline readiness, or scoring-result usefulness.
2. Synthetic input does not prove real corpus coverage or durable baseline quality.
3. A scratch JSONL file does not become a fixture, golden answer, accepted baseline, or user-facing report.
4. A single-bundle JSONL run proves only artifact consumer behavior for one bundle. It does not prove multi-bundle aggregation semantics.
5. Structured issue output does not prove Service, CLI, renderer, or quality gate should call the validator by default.

## 6. Review / Re-Review Strategy

Plan review should be independent and adversarial:

1. AgentMiMo plan review: check scope boundaries, dry-run minimality, artifact policy, and whether the plan avoids hidden product integration.
2. AgentGLM plan review: check validator API coverage, issue examples, acceptance criteria, residual classification, and whether the plan is code-generation-ready.

If either reviewer finds blocker/material ambiguity, patch this plan and request re-review from the same reviewer(s). Controller should accept implementation only after the plan review loop passes or explicitly records accepted residual risk.

Future implementation review scope:

1. Review only the dry-run Markdown evidence and any one-off command transcript summarized there.
2. Confirm no source, test, README, tracked reports, durable fixture, product path, Host/Agent/dayu, or repository/PDF/cache/source helper changes.
3. Confirm scratch JSONL is untracked and outside forbidden paths.
4. Confirm summary counts and issue examples match the current validator semantics.
5. Confirm the implementation report does not overclaim readiness beyond consumer-contract dry-run evidence.

## 7. Residuals

The following remain deferred and must not be solved in this dry-run evidence gate:

1. Multi-bundle JSONL semantics and aggregation; this gate intentionally validates only single-bundle JSONL artifact consumption.
2. Exact message assertion for `unknown_upstream_failure_category`.
3. Whether non-scoring-ready `chapter_summary/report_level` should remain blocking or be relaxed.
4. Non-scoring-ready `chapter_summary` and report-level issue policy beyond current validator behavior.
5. `nav_data` mapping into report facts.
6. Derived-calculation population and validation beyond empty/synthetic records.
7. Durable baseline selection and curated fixture promotion.
8. Host/Agent/dayu integration.
9. Fallback upstream failure category recovery.
10. FOF taxonomy and QDII-FOF precedence.
11. Real corpus evidence, extraction correctness, and annual-report identity proof.

## 8. Allowed Files for Future Implementation

Default allowed tracked file, if this plan is accepted:

1. `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md`

Allowed untracked temporary inputs:

1. `/tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl`
2. A temporary one-off script in `/tmp` if inline Python becomes unreadable.

Not allowed by default:

1. Source code under `fund_agent/`.
2. Tests under `tests/`.
3. README files.
4. Tracked files under `reports/`.
5. Any fixture or curated baseline file.
6. Config, package metadata, Service, CLI, renderer, Host/Agent, or Dayu files.

Optional, not default:

If the one-off command becomes too brittle to reproduce, the implementation agent may propose a tiny untracked `/tmp` script and quote its contents or checksum in the evidence Markdown. Adding a tracked script or test requires a new controller decision explaining why Markdown evidence plus one-off command is insufficient; that would no longer be the default dry-run evidence path.

## 9. Required Validation

Because the planned implementation changes no source or tests, `ruff` is not required by default. If the future implementation changes Python source or tests despite this plan, it must run focused `ruff` on the changed files and explain why source/test change was necessary.

Required boundary and hygiene checks for the future dry-run implementation:

1. `rg -n "FundDocumentRepository|AnnualReportDocumentCache|AnnualReportPdfAdapter|documents\\.sources|annual_report_pdf|extra_payload|dayu\\.host|dayu\\.engine|nav_data|quality_gate|extraction_score|fund-analysis|reports/scoring-runs" docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md`
   - Expected: no forbidden product-integration or data-access claim except if quoted as a boundary check / non-goal. If matches exist only in boundary sections, the evidence must explicitly mark them as non-goals.
2. `git status --short`
   - Expected: only the dry-run Markdown evidence artifact is tracked as a new or modified file for implementation; scratch JSONL is not tracked.
3. `git diff --check`
   - Expected: clean.
4. If a one-off Python command is run:
   - It must not write into production paths.
   - It must not import repository/PDF/cache/source helper modules.
   - It must write scratch JSONL only to `/tmp` or an untracked temporary directory.
   - It must record exit code and key output in the evidence Markdown.

The implementation evidence should also include a short `rg` boundary check over `fund_agent/fund/report_quality_validation.py` only if the reviewer wants to reconfirm the accepted implementation boundary; this is optional because the current gate is not changing validator source.

## 10. Stop Conditions

Stop and return to controller without implementation if any of the following becomes necessary:

1. Real annual-report data is needed.
2. A repository, PDF/cache, source helper, downloader, extractor, or fallback recovery path is needed.
3. A tracked fixture, tracked report output, or durable baseline promotion is needed.
4. Service, CLI, renderer, FQ0-FQ6, Host/Agent/dayu, `nav_data`, or derived-calculation behavior must change.
5. The validator output is ambiguous enough that source changes or tests are required before dry-run evidence can be meaningful.

## 11. Implementation Handoff Summary

After controller acceptance, the implementation agent should:

1. Create synthetic in-memory bundles and a scratch JSONL in `/tmp`.
2. Invoke `validate_report_quality_bundle()` and `validate_report_quality_jsonl()`.
3. Write one Markdown evidence artifact under `docs/reviews/`.
4. Record summary counts, representative issues, boundary checks, and limitations.
5. Run required `rg` boundary check, `git status --short`, and `git diff --check`.
6. Stop for review; do not wire the validator into product flow.
