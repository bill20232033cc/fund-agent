# Gate C First Report-Quality Improvement Slice Plan Controller Judgment - 2026-05-26

## Scope

This judgment closes Gate C: `first improvement slice selection plan/review`.

Accepted plan:

- `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-20260526.md`

Independent reviews:

- `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-review-mimo-20260526.md`
- `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-review-glm-20260526.md`
- `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-rereview-mimo-20260526.md`
- `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-rereview-glm-20260526.md`

No source, tests, README, renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, fixture, report output, push, PR, or destructive git work is authorized by this judgment.

## Review Disposition

| Reviewer | Round | Verdict | Controller disposition |
|---|---|---|---|
| AgentMiMo | Plan review | `PASS_WITH_FINDINGS` | Material findings F1-F3 and minor F4 required plan patch before implementation. |
| AgentGLM | Plan review | `PASS_WITH_FINDINGS` | Informational findings accepted as implementation guidance. |
| AgentMiMo | Targeted re-review | `PASS` | All MiMo F1-F4 findings closed by patched plan. |
| AgentGLM | Targeted re-review | `PASS_WITH_FINDINGS` | MiMo material findings closed; new F6 accepted as mandatory implementation preflight. |

## Accepted Slice

Accepted first improvement slice:

`active_fund` Chapter 3 turnover / style-consistency data-gap wording contract.

Rationale:

- Gate A identified `004393` / 2024 / `active_fund` as the clean near-term evaluation candidate and recorded the Chapter 3 turnover/style-consistency gap as the main active-fund risk.
- Gate B classified the active-fund case as Chapter 3 manager-holding traceability pass plus turnover/style-consistency gap issue, with `chapter_contract` as the next owner.
- The quasi-real evidence run produced no validator schema/content issues, so schema is not the current blocker.
- The accepted issue is a same-source claim-safety problem: without reviewed turnover or style-change evidence, the report-quality contract must not allow style-stability, style-consistency, or言行一致 claims.

## Accepted Plan Patch Decisions

The patched plan is accepted as code-generation-ready because it now fixes the review gaps:

- exact Chinese wording is specified for two modified `must_answer` entries, one new `must_not_cover` entry, one new `required_output_items` entry, and `ReportDataGapOverride.required_report_wording`;
- audit route is fixed to `ContractMustNotCoverCoverageRule` in `_MUST_NOT_COVER_COVERAGE_RULES` with `coverage_kind="narrative_guidance"`, not `ContractForbiddenContentRule`;
- modify/add decisions are explicit;
- update order is explicit: `docs/fund-analysis-template-draft.md` first, then `fund_agent/fund/template/contracts.py`, then `fund_agent/fund/audit/contract_rules.py`.

## Mandatory Gate D Preflight

AgentGLM F6 is accepted as a mandatory preflight check for Gate D implementation.

Before adding any new `ContractRequiredItemRule`, the implementation agent must verify the runtime audit behavior:

1. Check whether `covered_by_required_item` with multiple required item references behaves as AND or OR.
2. Check whether adding a new unconditional Chapter 3 `ContractRequiredItemRule` would make current renderer output fail `run_programmatic_audit()` in default `fund-analysis analyze`.
3. If adding the rule would change default product behavior or require renderer changes, stop and return to controller. Do not silently widen scope.
4. Prefer the safe option if needed: keep the wording contract and `narrative_guidance` coverage, but defer any runtime `ContractRequiredItemRule` that current renderer cannot satisfy to a later renderer/report-writing gate.

This preflight preserves the hard boundary: Gate D must not modify renderer, FQ0-FQ6, Service/CLI default behavior, Host/Agent/dayu, production extraction, or durable baseline unless a new reviewed plan explicitly proves it is the minimum necessary scope.

## Residuals

| Residual | Owner / next gate | Blocking Gate D? |
|---|---|---|
| Renderer may not emit the new wording yet. | future renderer/report-writing gate | No, unless the chosen audit rule would make default analyze fail. |
| Turnover/style-change extraction may still be incomplete. | future data/source extraction gate, only after same-source evidence requires it | No |
| Fallback-blocked index/QDII candidates remain unresolved. | source recovery or replacement gate | No |
| Pure FOF coverage remains `data_gap`. | corpus selection / fund-type taxonomy gate | No |
| Durable baseline remains blocked. | curated-fixture gate after reviewed facts and clean validation | No |

## Next Entry Point

Enter Gate D implementation only for the accepted minimal slice:

`active_fund Chapter 3 turnover/style-consistency data-gap wording contract implementation`

Gate D must use the accepted plan and mandatory preflight above, run focused tests / ruff / `git diff --check`, obtain at least two independent code reviews and re-reviews as needed, update `docs/implementation-control.md`, and form a local accepted commit if no blockers remain.
