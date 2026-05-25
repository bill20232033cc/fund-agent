# Release Maintenance Report-Quality Scoring JSONL Content Validation Plan Controller Judgment

> Date: 2026-05-25
> Gate: `report-quality scoring JSONL content validation plan`
> Controller status: accepted locally
> Design truth: `docs/design.md` (v2.2)
> Control truth: `docs/implementation-control.md`
> Rules truth: `AGENTS.md`

## Verdict

**ACCEPTED.**

The plan is code-generation-ready after review fixes. It correctly keeps the next slice inside Fund capability report-quality input validation, reuses `ReportEvidenceBundle` / `ReportScoreIssueLink` typed domains, and does not expand into renderer, Service, CLI, FQ0-FQ6, Host/Agent, Dayu, `nav_data`, durable baseline, or fixture promotion.

## Scope Accepted

- Add a pure Fund capability validator module, currently planned as `fund_agent/fund/report_quality_validation.py`.
- Add focused tests in `tests/fund/test_report_quality_validation.py`.
- Validate `ReportEvidenceBundle` serialization / JSONL content for field presence, enum domains, invalid combinations, id references, `N/A`, `chapter_summary`, source boundary / failure category, `scoring_ready` preconditions, and fact/gap/issue/anchor link integrity.
- Keep the validator observational and fail-closed; it may produce structured issues and summaries, but it does not replace `quality_gate.py` FQ0-FQ6 or change product flow.
- Avoid a parallel schema: implementation must import/reuse domains from `fund_agent/fund/report_evidence.py`.

## Review Results

| Reviewer | Artifact | Result | Controller decision |
|---|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-review-mimo-20260525.md` | `PASS_WITH_FINDINGS` | Findings accepted and patched. |
| AgentGLM | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-review-glm-20260525.md` | `PASS_WITH_FINDINGS` | Findings accepted and patched. |
| AgentMiMo re-review | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-rereview-mimo-20260525.md` | `PASS` | Confirms all five MiMo findings closed. |
| AgentGLM re-review | `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-rereview-glm-20260525.md` | `PASS` | Confirms all prior GLM findings closed; final low fallback duplication note was patched by making §4.G canonical. |

## Finding Decisions

| Finding | Decision | Reason |
|---|---|---|
| MiMo F1: missing `ReportSourceDocument` fallback consistency validation | Accepted and fixed | Plan now makes fallback consistency canonical in §4.G and requires `fallback_allowed` / `fallback_used` / `source_failure_category` coherence with `RQV_FALLBACK_CONFLICT/blocking`. |
| MiMo F2: `N/A` severity ambiguity | Accepted and fixed | Plan now treats `N/A` carrying severity as `RQV_NA_SEMANTICS/material`. |
| MiMo F3: nested enum negative case missing | Accepted and fixed | Plan now requires nested enum coverage, including invalid `source_documents[0].source_boundary`. |
| MiMo F4: bidirectional/id reference completeness | Accepted and fixed | Plan now requires non-empty anchor `document_id` to resolve to a source document. |
| MiMo F5: `preferred_lens.chapters` required fields | Accepted and fixed | Plan now requires `chapter_id`, `lens_key`, `used_default`, and `primary_focus`. |
| GLM F1: duplicate `scoring_ready` rule locations | Accepted and fixed | §4.H is now the canonical implementation location and uses `RQV_SCORING_READY_PRECONDITION/blocking`. |
| GLM F2: missing fact `review_status=="reviewed"` precondition | Accepted and fixed | Plan now requires all facts to be reviewed for `scoring_ready`. |
| GLM F3: `N/A` + `chapter_summary` duplicate issue risk | Accepted and fixed | Plan now requires one canonical issue for the same semantic violation, prioritizing `RQV_CHAPTER_SUMMARY_SEMANTICS`. |
| GLM re-review F4: fallback consistency duplicated in §4.C / §4.G | Accepted and fixed | §4.G is now the only canonical fallback consistency implementation location; §4.C references it without duplicate emission. |

## Implementation Handoff

The next implementation agent should follow `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-20260525.md` directly.

Allowed implementation files:

- `fund_agent/fund/report_quality_validation.py`
- `tests/fund/test_report_quality_validation.py`
- `fund_agent/fund/report_evidence.py` and `tests/fund/test_report_evidence.py` only if a minimal serialization helper is truly required
- `fund_agent/fund/README.md` minimal module guide sync is allowed if source changes introduce the validator module

Stop before:

- renderer, Service, CLI, `quality_gate.py` FQ0-FQ6, or `extraction_score.py` scoring semantics changes
- PDF/cache/source helper or `FundDocumentRepository` access
- `extra_payload`, `**kwargs`, Host/Agent packages, `dayu.host`, `dayu.engine`
- `nav_data` projection, derived calculation generation, durable fixtures, baseline promotion, or tracked `reports/` output changes

Required validation after implementation:

- focused validator tests
- adjacent `test_report_evidence.py`, `test_extraction_score.py`, and `test_quality_gate.py`
- coverage for `fund_agent.fund.report_quality_validation` at or above 80%
- `ruff check`
- forbidden boundary `rg`
- `git diff --check`

## Residuals

- `nav_data` mapping remains owned by a future source-contract slice.
- Derived calculations remain shape-only until a calculation source gate.
- Durable baseline / curated fixtures remain future work after validator evidence exists.
- Host/Agent/Dayu runtime remains a future explicit gate.
- Fallback upstream failure recovery and FOF taxonomy/corpus coverage remain under their previously assigned future gates.

## Next Entry Point

`report-quality scoring JSONL content validation implementation`
