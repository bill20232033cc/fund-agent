# Release Maintenance Report-Quality Baseline S0 Corpus-Selection Evidence Controller Judgment

> Date: 2026-05-25
> Branch: `codex/v0-release-readiness-plan`
> Gate: `report-quality-baseline S0 corpus-selection evidence`
> Controller status: accepted locally; next gate is `report-quality-baseline S1 score-schema fixture draft`

## Step Self-Check

- Current role: controller. This artifact records review disposition, acceptance rationale, residual ownership, and gate bookkeeping only.
- Source of truth: `AGENTS.md`, `docs/design.md` current architecture / report-quality / Fact-Evidence / fund-type sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, and accepted report-quality baseline plan artifacts.
- Reviewed S0 evidence: `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md`.
- Independent reviews: `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-review-mimo-20260525.md`, `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-review-ds-20260525.md`.
- Re-reviews after the S0 evidence patch: `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-rereview-mimo-20260525.md`, `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-rereview-ds-20260525.md`.
- Scope boundary: no source code, tests, renderer, FQ0-FQ6 quality gate, Host/Agent package, Dayu runtime, push, PR, or external state change.

## Verdict

**ACCEPTED FOR NEXT GATE.**

S0 satisfied the control-doc entry criteria: it produced a reviewed candidate table with fund type slot, fund code, report year, repository verification status, review state, source failure category, and ignored run path; it defined transition trigger, actor, and minimum evidence for the review-state chain; and it preserved the `FundDocumentRepository` boundary.

Both initial reviews returned `PASS_WITH_FINDINGS`. The material fallback finding was fixed before acceptance, then both re-reviews returned `PASS`. Based on `docs/design.md` and first principles, accepting S0 is the best current choice because it makes report-quality work observable without pretending the corpus is more complete than the evidence supports.

## Accepted S0 Corpus State

| fund type slot | accepted S0 state | Controller disposition |
|---|---|---|
| `active_fund` | `004393`, 2024, `repository_verified` | Accepted as a candidate for later fact prefill review. |
| `index_fund` | `110020`, 2024, `repository_verified`; Eastmoney fallback with unknown upstream failure category | Accepted only as S0 repository evidence. Before durable baseline selection, S1 must recover the original upstream failure category or exclude this candidate. |
| `enhanced_index` | `004194`, 2024, `repository_verified` | Accepted as a candidate for later fact prefill review. |
| `bond_fund` | `006597`, 2024, `repository_verified` | Accepted as a candidate for later fact prefill review. |
| `qdii_fund` | `017641`, 2024, `repository_verified`; Eastmoney fallback with unknown upstream failure category | Accepted only as S0 repository evidence. Before durable baseline selection, S1 must recover the original upstream failure category or exclude this candidate. |
| `fof_fund` | `007721` and `017970`, 2024, annual reports load but current classifier returns `qdii_fund` | Accepted as `data_gap`, not as fulfilled `fof_fund` coverage. A second pass must find a pure `fof_fund` or open a QDII-FOF taxonomy / precedence gate. |

## Finding Disposition

| Finding | Source | Disposition | Owner / gate |
|---|---|---|---|
| Fallback records hid unknown upstream failure category behind `n/a` | MiMo F-1 and DS residual | Accepted and fixed. S0 now uses `unknown_upstream_failure_category` for fallback records whose repository metadata preserves only fallback result/source. | S1 entry gate must recover category or exclude candidate before durable baseline selection. |
| QDII-FOF classifier precedence is not explicitly resolved in design | MiMo F-2 | Accepted as a real residual but outside S0. S0 correctly records QDII-FOF as `data_gap` and does not treat it as pure `fof_fund`. | Future fund-type taxonomy gate or S1 second-pass corpus coverage. |
| Review-state transition lacks terminal / rollback states | MiMo F-3 | Deferred. S0 was required to define forward transitions; terminal states are schema/state-machine work. | S1/S2 state model extension. |
| `rg` validation is broad | MiMo F-4 | Accepted as non-blocking. It is sufficient for a document evidence gate; more exact checks belong to future scripted gates. | S1 validation design. |
| Async repository call description was ambiguous | DS F-1 | Fixed. S0 now states the probe enters `asyncio.run(...)` and awaits `FundDocumentRepository.load_annual_report(...)`. | Closed. |
| `repository verification status` mixes document identity with type-slot membership | DS F-2 | Deferred. S0 disclosed the gap through `review state` and `source failure category`; S1 must split document identity from type-slot membership in schema. | S1 score-schema fixture draft. |
| `DocumentKey` shorthand was not dataclass-like | DS F-3 | Fixed. S0 now uses explicit `DocumentKey(fund_code="...", year=2024, document_kind="annual_report")` wording where applicable. | Closed. |

## Controller Decisions

1. S0 is accepted as repository evidence, not as a scoring baseline.
2. FOF remains a deliberate `data_gap`; QDII-FOF is not accepted as pure `fof_fund`.
3. Fallback candidates with `unknown_upstream_failure_category` cannot enter durable baseline selection until S1 recovers the original upstream failure category or excludes them.
4. S1 must split document identity verification from fund-type slot membership. This prevents `verified_as_annual_report_but_type_gap` from being misread as scoring-ready FOF evidence.
5. Local probe outputs under `reports/data-source-runs/s0-corpus-selection-20260525/` remain ignored scratch evidence and are not promoted to tracked fixtures.

## Boundary Confirmation

- Annual-report identity probing used `FundDocumentRepository` / public Fund boundary and did not call PDF cache, download helper, EID helper, or Eastmoney helper directly.
- No renderer behavior or v0 8-chapter report output changed.
- No FQ0-FQ6 quality-gate behavior changed.
- No LLM audit, Evidence Confirm, repair loop, patch/regenerate, or chapter writer was claimed as implemented.
- No `fund_agent/host` or `fund_agent/agent` package was created.
- No `dayu.host` or `dayu.engine` dependency was introduced.
- No tracked fixture was promoted from local run outputs.

## Residual Risks

| Residual | Owner / next gate | Required handling |
|---|---|---|
| Fallback upstream failure category unknown for `110020`, `017641`, and `017970` | S1 entry gate / source reliability evidence | Recover the original upstream failure category through source-boundary evidence, or exclude the candidate before durable baseline selection. |
| FOF coverage is not fulfilled | S1 second pass or fund-type taxonomy gate | Find a pure repository-verified `fof_fund`, or explicitly decide QDII-FOF precedence before treating QDII-FOF as satisfying FOF coverage. |
| Document identity and type-slot membership are currently collapsed in prose | S1 score schema | Separate these fields before scoring input is frozen. |
| Review-state machine has no terminal states | S1/S2 | Add rejected / deferred / expired or equivalent terminal states if the schema needs lifecycle closure. |

## Validation

```text
rg -n "unknown_upstream_failure_category|asyncio.run|durable baseline selection|DocumentKey|data_gap|S1 entry gate precondition" docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-rereview-mimo-20260525.md docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-rereview-ds-20260525.md
git diff --check
git check-ignore -v reports/data-source-runs/s0-corpus-selection-20260525/ reports/data-source-runs/s0-corpus-selection-20260525/repository-probe.jsonl reports/data-source-runs/s0-corpus-selection-20260525/repository-probe-summary.md reports/data-source-runs/s0-corpus-selection-20260525/probe_repository_candidates.py
```

Result: passed.

## Next Entry Point

`report-quality-baseline S1 score-schema fixture draft`
