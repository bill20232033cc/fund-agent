# Release Maintenance ReportEvidenceBundle Typed Model / Projection Implementation Controller Judgment

> Date: 2026-05-25
> Gate: `ReportEvidenceBundle typed model/projection implementation`
> Controller status: accepted locally
> Design truth: `docs/design.md` (v2.2)
> Control truth: `docs/implementation-control.md`
> Rules truth: `AGENTS.md`

## Verdict

**ACCEPTED.**

The implementation delivers the accepted narrow slice: `fund_agent/fund/report_evidence.py` defines the typed `ReportEvidenceBundle` model/projection over the existing `StructuredFundDataBundle`, `tests/fund/test_report_evidence.py` covers the projection contract, and `fund_agent/fund/README.md` records the current Fund-package behavior without claiming renderer, FQ0-FQ6, Host/Agent, Dayu, fixture, or durable-baseline work.

## Scope Check

- Added `ReportEvidenceBundle` and related frozen slotted dataclasses with explicit `Literal` domains.
- Projection consumes only `StructuredFundDataBundle` and explicit `ReportEvidenceProjectionContext`.
- `classified_fund_type` is read only from `basic_identity.value["classified_fund_type"]`; no heuristic inference was added.
- Preferred-lens projection is serializable and covers template chapters 0-7 when fund type is known.
- Deterministic ids are implemented for bundle, document, fact, gap, anchor, and score issue references.
- `nav_data` remains excluded from initial report facts.
- `DerivedCalculation` is shape-only; `derived_calculations` is not populated.
- `accepted_baseline` is not derived and cannot be forced through the current projection context.
- No repository, PDF/cache/source helper, renderer/FQ0-FQ6, Host/Agent, Dayu, `extra_payload`, fixture promotion, or durable-baseline work was introduced.

## Review Results

| Reviewer | Artifact | Result | Controller decision |
|---|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-review-mimo-20260525.md` | `PASS_WITH_FINDINGS` | Accepted; findings were minor test/design-note residuals. |
| AgentGLM | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-review-glm-20260525.md` | `PASS_WITH_FINDINGS` | Accepted after fixing F1. F2-F4 remain low-priority test coverage residuals. |
| AgentMiMo re-review | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-rereview-mimo-20260525.md` | `PASS` | Confirms GLM F1 is closed and no new blocker exists. |
| AgentGLM re-review | `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-rereview-glm-20260525.md` | `PASS` | Confirms duplicate `classified_fund_type` gap now preserves `related_fact_id`. |

## Finding Decisions

| Finding | Decision | Reason |
|---|---|---|
| GLM F1: duplicate `classified_fund_type` gap lost `related_fact_id` | Accepted and fixed | Bidirectional fact/gap references are part of the evidence contract. `_deduplicate_gaps()` now merges duplicate gap references and the focused test asserts the single missing-type gap keeps `related_fact_id` and is referenced by the fact. |
| MiMo F1 / GLM F2: additional validation guard tests | Deferred | Existing guards are implemented and current coverage is 93%; broader guard hardening is useful but not required to accept this narrow implementation slice. |
| GLM F3: review-status fallback-state tests | Deferred | Fallback states are implemented but not used by the current scoring-ready path; cover them when downstream consumers start depending on those lifecycle states. |
| GLM F4: unknown extraction-mode fallback test | Deferred | Conservative fallback exists; testing can be added in a later robustness slice without changing the current contract. |
| MiMo F2: turnover-rate override path asymmetry | Accepted as non-blocking design note | The override path intentionally uses `manager.turnover_rate` for wording constraints while fact matching bridges back to `turnover_rate`; current tests verify the link. |

## Validation

Controller-rerun validation after the F1 fix:

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest tests/fund/test_report_evidence.py` | 23 passed |
| `.venv/bin/python -m pytest --cov=fund_agent.fund.report_evidence --cov-report=term-missing tests/fund/test_report_evidence.py` | 23 passed; `fund_agent.fund.report_evidence` coverage 93% |
| `.venv/bin/python -m pytest tests/fund/test_report_evidence.py tests/fund/template/test_lens_application.py tests/fund/test_extraction_snapshot.py` | 40 passed |
| `.venv/bin/python -m ruff check fund_agent/fund/report_evidence.py tests/fund/test_report_evidence.py` | passed |
| Boundary `rg` for repository/PDF/cache/source helpers, `extra_payload`, Dayu, and kwargs | production file clean; only negative assertions in tests matched |
| `git diff --check` | clean |

## Residuals

- `nav_data` still requires a future source-contract slice before it can be projected as report facts.
- Fallback upstream failure category recovery for previously noted fallback candidates remains owned by the source-reliability gate.
- Pure FOF corpus coverage remains owned by a future fund-type taxonomy / corpus gate.
- JSONL content validation remains the next logical scoring-validation slice: field presence, enum domains, invalid combinations, id references, `N/A`, `chapter_summary`, and content-level checks.
- Additional defensive tests for projection context guards, fallback review statuses, and unknown extraction mode are useful hardening work but not blockers for this accepted slice.

## Next Entry Point

Advance the control document to a follow-up planning gate for report-quality scoring/content validation, with current suggested entry point:

`report-quality scoring JSONL content validation plan`
