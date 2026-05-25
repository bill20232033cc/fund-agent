# Release Maintenance Report-Quality Scoring JSONL Content Validation Implementation Controller Judgment

> Date: 2026-05-25
> Gate: `report-quality scoring JSONL content validation implementation`
> Controller status: accepted locally
> Design truth: `docs/design.md` (v2.2)
> Control truth: `docs/implementation-control.md`
> Rules truth: `AGENTS.md`

## Verdict

**ACCEPTED.**

The implementation delivers the accepted narrow validator slice. `fund_agent/fund/report_quality_validation.py` adds a pure Fund capability validator over `ReportEvidenceBundle`, JSON-like mappings, and JSONL records; `tests/fund/test_report_quality_validation.py` covers the accepted positive and negative matrix; `fund_agent/fund/README.md` records the current module boundary without claiming renderer, Service, CLI, FQ0-FQ6, Host/Agent, Dayu, fixture, or durable-baseline work.

## Scope Check

- The validator reuses `report_evidence.py` typed domains and `REPORT_EVIDENCE_SCHEMA_VERSION`; it does not create a parallel score-input schema.
- Public APIs are explicit: `validate_report_quality_bundle()` and `validate_report_quality_jsonl()`.
- Validation covers field presence, enum domains, invalid combinations, id references, evidence-anchor document references, `N/A`, `chapter_summary`, source fallback consistency, `scoring_ready` preconditions, and fact/gap/issue/anchor link integrity.
- JSONL support is limited to `record_type="bundle"` and `record_type="score_issue"` with stable line/field pointers.
- Blocking data-gap semantics are aligned with `report_evidence.py`: any gap whose `gap_kind` and `failure_category` are not `not_applicable` is blocking.
- No renderer, Service, CLI, `quality_gate.py` FQ0-FQ6, `extraction_score.py`, repository/PDF/cache/source helper, Host/Agent/dayu, `extra_payload`, `nav_data`, durable fixture, baseline promotion, or tracked `reports/` output work was introduced.

## Review Results

| Reviewer | Artifact | Result | Controller decision |
|---|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-review-mimo-20260525.md` | `PASS_WITH_FINDINGS` | Accepted after fixing duplicate `chapter_summary/report_level` emission and hardening blocking-gap semantics. |
| AgentGLM | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-review-glm-20260525.md` | `PASS_WITH_FINDINGS` | Accepted after fixing fallback/fail-closed duplicate issue emission and adding focused tests. |
| AgentMiMo re-review | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-rereview-mimo-20260525.md` | `PASS` | Confirms all material concerns are closed; two minor residuals remain non-blocking. |
| AgentGLM re-review | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-rereview-glm-20260525.md` | `PASS` | Confirms no blocker/material finding remains. |

## Finding Decisions

| Finding | Decision | Reason |
|---|---|---|
| Blocking data-gap semantics were too narrow | Accepted and fixed | `_is_blocking_gap()` now mirrors `report_evidence.py` rather than maintaining a narrower parallel set of blocking gap kinds. |
| MiMo F1: `chapter_summary/report_level` duplicate issue | Accepted and fixed | The report-level check now lives only in `_validate_chapter_summary_issue()`; focused test asserts one canonical pointer issue. |
| GLM F1/F2: fallback/fail-closed cascading duplicate issues | Accepted and fixed | Fail-closed source failures short-circuit after `RQV_FAIL_CLOSED_SOURCE`; fallback conflicts are merged into one canonical `RQV_FALLBACK_CONFLICT`. |
| GLM F3-F6: missing negative tests and file-handle helper issue | Accepted and fixed | Added accepted-baseline, skipped outside chapter-summary, invalid record-type, fallback duplicate, chapter-summary duplicate, and blocking-gap tests; `_validator_source()` now uses a context manager. |
| MiMo F2: non-scoring-ready `chapter_summary/report_level` still blocking | Deferred as minor | The behavior is stricter but coherent with the plan's chapter-summary semantics; clarify or test in a later hardening gate if needed. |
| MiMo F3 / GLM M1: unknown-upstream message text not independently asserted | Deferred as minor | The behavior is implemented and included in the consolidated precondition message; add a message-specific assertion in a future test-hardening pass if this text becomes consumer-visible. |

## Validation

Controller-rerun validation after fixes:

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest tests/fund/test_report_quality_validation.py -q` | 25 passed |
| `.venv/bin/python -m pytest tests/fund/test_report_evidence.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q` | 81 passed |
| `.venv/bin/python -m pytest tests/fund/test_report_quality_validation.py --cov=fund_agent.fund.report_quality_validation --cov-report=term-missing --cov-fail-under=80 -q` | 25 passed; `report_quality_validation.py` coverage 92.34% |
| `.venv/bin/python -m ruff check fund_agent/fund/report_quality_validation.py tests/fund/test_report_quality_validation.py` | passed |
| Forbidden boundary `rg` for repository/PDF/cache/source helpers, Dayu, `extra_payload`, `nav_data`, `quality_gate`, and `extraction_score` | no matches |
| `git diff --check` | clean |

## Residuals

- Non-scoring-ready `chapter_summary/report_level` blocking behavior should remain as current stricter semantics unless a future plan explicitly relaxes it.
- Add a narrow assertion for the unknown-upstream failure text if downstream consumers begin depending on exact precondition message contents.
- Multi-bundle JSONL processing remains outside this gate.
- `nav_data` mapping, derived-calculation generation, durable baseline / curated fixtures, fallback-source recovery, FOF taxonomy/corpus coverage, and Host/Agent/Dayu runtime remain owned by their future gates.

## Next Entry Point

Advance the control document to a planning gate for validator dry-run evidence:

`report-quality validator dry-run evidence planning`
