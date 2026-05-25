# Release Maintenance Report-Quality Validator Dry-Run Evidence Plan Controller Judgment

> Date: 2026-05-25
> Gate: `report-quality validator dry-run evidence planning`
> Controller status: accepted locally
> Design truth: `docs/design.md` (v2.2)
> Control truth: `docs/implementation-control.md`
> Rules truth: `AGENTS.md`

## Verdict

**ACCEPTED.**

The plan is code-generation-ready after review fixes. It keeps the next gate as dry-run evidence only: prove the accepted validator can be consumed over synthetic `ReportEvidenceBundle` / single-bundle JSONL content and returns stable issues, pointers, counts, run id, and schema version, without integrating into Service, CLI, renderer, FQ0-FQ6, tracked reports, durable fixtures, Host/Agent, Dayu, data sources, or repository/PDF/cache paths.

## Scope Accepted

- Default implementation output is one Markdown evidence artifact under `docs/reviews/`.
- Scratch JSONL, if needed, must live under `/tmp` or an untracked temporary directory and must not be promoted to a fixture, report, baseline, or package resource.
- The positive path uses an in-memory valid bundle through `validate_report_quality_bundle()`.
- JSONL evidence uses a single-bundle artifact: exactly one `record_type="bundle"` record plus optional linked `record_type="score_issue"` records.
- Dry-run evidence must record `bundle_record_count == 1`, bundle record line numbers, score issue record count / line numbers, summary counts, `error_code_counts`, run id, schema version, and representative issue rows.
- Representative issues must cover fallback conflict, fail-closed source, `chapter_summary`, `N/A`, forward reference integrity, backlink completeness, and `scoring_ready` precondition.

## Review Results

| Reviewer | Artifact | Result | Controller decision |
|---|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-review-mimo-20260525.md` | `PASS_WITH_FINDINGS` | Accepted after adding explicit single-bundle count / line-number assertions. |
| AgentGLM | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-review-glm-20260525.md` | `PASS_WITH_FINDINGS` | Accepted after adding `RQV_FAIL_CLOSED_SOURCE` coverage and splitting link integrity into forward-ref and backlink checks. |
| AgentMiMo re-review | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-rereview-mimo-20260525.md` | `PASS` | Confirms single-bundle assertion finding is closed. |
| AgentGLM re-review | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-rereview-glm-20260525.md` | `PASS` | Confirms fail-closed and link-integrity findings are closed; no new blocker/material issue. |

## Finding Decisions

| Finding | Decision | Reason |
|---|---|---|
| MiMo F1: single-bundle JSONL constraint lacked explicit verification | Accepted and fixed | The plan now requires parsed `bundle_record_count == 1`, bundle record lines, and score issue count / lines in the evidence. |
| GLM F1: `RQV_FAIL_CLOSED_SOURCE` missing from representative issue coverage | Accepted and fixed | Fail-closed source handling is now required in input construction, evidence issue table, and acceptance criteria, including proof that fallback conflict does not mask it. |
| GLM F2: link integrity used ambiguous `or` semantics | Accepted and fixed | The plan now separately requires `RQV_REF_MISSING` for forward references and `RQV_GAP_LINK_INCOMPLETE` for backlink completeness. |

## Validation

Controller validation for the planning gate:

| Command | Result |
|---|---|
| `git diff --check docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-20260525.md` | clean |
| Plan review loop | MiMo and GLM initial reviews `PASS_WITH_FINDINGS`; both re-reviews `PASS` |

No source, test, README, tracked report, fixture, product-flow, repository/PDF/cache/source helper, Host/Agent, or Dayu file was modified in this planning gate.

## Residuals

- Multi-bundle JSONL aggregation remains explicitly deferred.
- Exact message assertion for `unknown_upstream_failure_category` remains deferred until consumer-visible text matters.
- Non-scoring-ready `chapter_summary/report_level` policy remains current stricter behavior unless a future hardening gate changes it.
- `nav_data` mapping, derived-calculation population, durable baseline / curated fixtures, fallback-source recovery, FOF taxonomy/corpus coverage, real corpus evidence, extraction correctness, annual-report identity proof, and Host/Agent/Dayu runtime remain owned by future gates.

## Implementation Handoff

The next implementation gate may create only:

- `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md`

It may use untracked `/tmp` scratch JSONL / scripts. It must stop before any source, test, README, tracked report, fixture, Service, CLI, renderer, FQ0-FQ6, `extraction_score.py`, repository/PDF/cache/source helper, `FundDocumentRepository`, `extra_payload`, Host/Agent/dayu, `nav_data`, derived-calculation generation, durable-baseline, or real-data acquisition work.

Required validation for that implementation is the plan's boundary / hygiene checks plus `git diff --check`.

## Next Entry Point

`report-quality validator dry-run evidence implementation`
