# Release Maintenance Report-Quality Validator Dry-Run Evidence Controller Judgment

> Date: 2026-05-25
> Gate: `report-quality validator dry-run evidence implementation`
> Controller status: accepted locally
> Design truth: `docs/design.md` (v2.2)
> Control truth: `docs/implementation-control.md`
> Rules truth: `AGENTS.md`

## Verdict

**ACCEPTED.**

The dry-run evidence proves the accepted validator can be consumed as a synthetic `ReportEvidenceBundle` / single-bundle JSONL contract and returns stable structured results. It does not integrate the validator into Service, CLI, renderer, FQ0-FQ6, tracked reports, fixtures, durable baseline, Host/Agent, Dayu, repository/PDF/cache/source helpers, or real data acquisition.

## Scope Check

- Tracked implementation output is limited to `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-20260525.md`.
- Scratch files are under `/tmp/fund-agent-report-quality-validator-dry-run-20260525/` and are not tracked.
- The positive path calls `validate_report_quality_bundle()` on an in-memory valid bundle and records zero issues.
- The JSONL path calls `validate_report_quality_jsonl()` on one scratch JSONL with exactly one `record_type="bundle"` record and one linked `record_type="score_issue"` record.
- Evidence records `bundle_record_count == 1`, bundle / score issue line numbers, summary counts, `error_code_counts`, run id, schema version, source path, pointers, expected values, actual values, and interpretation.
- Representative issues cover `RQV_FALLBACK_CONFLICT`, `RQV_FAIL_CLOSED_SOURCE`, `RQV_CHAPTER_SUMMARY_SEMANTICS`, `RQV_NA_SEMANTICS`, `RQV_REF_MISSING`, `RQV_GAP_LINK_INCOMPLETE`, and `RQV_SCORING_READY_PRECONDITION`.
- The artifact explicitly states that the dry run proves consumer-contract behavior only and does not prove product-flow readiness, extraction correctness, annual-report identity, durable baseline readiness, or multi-bundle JSONL aggregation.

## Review Results

| Reviewer | Artifact | Result | Controller decision |
|---|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-review-mimo-20260525.md` | `PASS_WITH_FINDINGS` | Accepted after targeted re-review rejected the material finding as invalid and closed the two minor findings. |
| AgentGLM | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-review-glm-20260525.md` | `PASS` | Accepted; no blocker/material/minor findings. |
| AgentMiMo re-review | `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-rereview-mimo-20260525.md` | `PASS` | Confirms `rg` exit code was recorded correctly, `test` commands were present in the validation table, and `/tmp/result.json` is acceptable scratch intermediate output. |

## Finding Decisions

| Finding | Decision | Reason |
|---|---|---|
| MiMo F1: boundary `rg` exit code recorded incorrectly | Rejected as invalid | `rg` returns exit code 0 when matches are found. The evidence recorded matches only in non-goal / validation sections and exit code 0, which is factually correct. |
| MiMo F2: `/tmp/result.json` not listed in plan temporary inputs | Accepted as non-blocking residual | `result.json` is an untracked `/tmp` intermediate output used for inspection; it is not a fixture, report, baseline, package resource, or repo-local scratch file. |
| MiMo F3: validation table missing `test` commands | Rejected as invalid | The evidence validation table includes the `test -f` and repo-local absence checks. |

## Validation

Controller-rerun validation:

| Command | Result |
|---|---|
| `git diff --check` | clean |
| Boundary `rg` over the evidence artifact | matches only in non-goal and validation sections; these are boundary assertions, not integration claims |
| `git ls-files \| rg -n "fund-agent-report-quality-validator-dry-run-20260525\|input\\.jsonl\|result\\.json"` | no tracked scratch files |
| `test -f /tmp/fund-agent-report-quality-validator-dry-run-20260525/input.jsonl` | scratch JSONL exists under `/tmp` |

## Residuals

- Multi-bundle JSONL aggregation remains deferred.
- Exact message assertions for `unknown_upstream_failure_category` remain deferred.
- Non-scoring-ready `chapter_summary/report_level` policy remains current stricter behavior unless a later hardening gate changes it.
- `nav_data` mapping, derived-calculation population, durable baseline / curated fixtures, fallback-source recovery, FOF taxonomy/corpus coverage, real corpus evidence, extraction correctness, annual-report identity proof, and Host/Agent/Dayu runtime remain owned by future gates.

## Next Entry Point

`report-quality validator integration decision planning`
