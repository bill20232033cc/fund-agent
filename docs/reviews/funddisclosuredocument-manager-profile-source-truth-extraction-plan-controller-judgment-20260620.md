# FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Plan Controller Judgment

## Metadata

- Work unit: `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction`
- Gate: `Planning Gate`
- Classification: `standard`
- Plan artifact: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-plan-20260620.md`
- AgentCodex role: planning worker only
- AgentDS review: `docs/reviews/plan-review-20260620-083543.md`
- AgentMiMo review: `docs/reviews/plan-review-20260620-083605.md`
- Controller verdict: `ACCEPT_PLAN_WITH_BINDING_AMENDMENTS_READY_FOR_IMPLEMENTATION_GATE_NOT_READY`

## Decision

Accept the plan as code-generation-ready for the next gate:

`FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Implementation Gate`

The plan is scoped to exactly one field family, `manager_profile.v1`, and stays inside the Fund layer `FundDisclosureDocumentProcessor` / Extractor boundary. It reuses the accepted source-truth admission proof mechanism, existing public `manager_profile.v1` value keys, existing public `EvidenceAnchor` shape, existing gap taxonomy, and existing facade projection path. It does not authorize parser replacement, repository/source behavior changes, `EvidenceSourceKind` expansion, upper-layer candidate consumption, real-report correctness, golden/readiness, release, or any other field-family implementation.

## Review Disposition

### AgentDS Findings

| Finding | Disposition | Controller binding |
|---|---|---|
| F1 MEDIUM: direct-route-missing candidate evidence suppression test gap | accepted | Implementation must include a proof-positive direct-route missing case asserting `manager_profile.v1.candidate_evidence == ()` and no fallback to S6-D candidate evidence. |
| F2 LOW: `holdings_snapshot` source tables are portfolio/accounting tables | deferred-with-owner | Implementation evidence must record this semantic tension as residual; future `current_stage.v1` / `core_risk.v1` gates own interpretation. |
| F3 LOW: holdings snapshot shape narrower than parsed annual extractor output | deferred-with-owner | Implementation must keep the plan's narrow shape and evidence artifact must state broader holdings shapes are future refinement. |
| F4 LOW: strategy text concatenation may include disclosed-text artifacts | accepted as implementation note | Use normalized disclosed text where available; do not add broad text-cleaning or semantic rewriting in this gate. |
| F5 LOW: `主要人员情况` heading broadness | accepted | Implementation must require strict row/role context containing `基金经理`; broad heading alone cannot emit a manager row. |
| F6 INFO: cross-family anchor dedupe out of scope | rejected-with-reason | Not needed because this gate emits only `manager_profile.v1` source-truth values. |
| F7 INFO: existing regression coverage adequate | accepted as support | Keep existing S6-D and source-truth regression tests passing. |

### AgentMiMo Findings

| Finding | Disposition | Controller binding |
|---|---|---|
| 001 MEDIUM: `holdings_snapshot` cross-family ownership | accepted as residual and implementation guard | Implementation must not leak `holdings_snapshot` into `current_stage.v1` or `core_risk.v1`; add or preserve a regression proving those families remain missing for FDD source-truth in this gate. Future field-family gates own independent extraction or explicit route decision. |
| 002 LOW: facade divergence risk | accepted | Slice 4 facade regression must use the exact Section 4 value shapes and assert projection into `StructuredFundDataBundle` fields. |
| 003 LOW: paragraph block `section_id` availability | accepted | Paragraph-backed anchor construction must either use an available section id or explicitly fall back to `None` / heading-derived value without schema expansion, and record the choice in evidence. |

## Binding Implementation Amendments

1. Implement exactly `manager_profile.v1`; do not implement or partially enable `investor_experience.v1`, `current_stage.v1`, or `core_risk.v1`.
2. Keep source-truth extraction behind existing `FundDisclosureSourceTruthAdmissionProof` validation and existing base admission checks.
3. In proof-positive direct route, suppress `manager_profile.v1.candidate_evidence` even when no direct value is found.
4. Add explicit test coverage for proof-positive direct-route missing with `candidate_evidence == ()`.
5. Add or preserve regression that `current_stage.v1` and `core_risk.v1` remain public missing and do not receive `holdings_snapshot` from this gate.
6. Treat `holdings_snapshot` and `turnover_rate` as disclosed data only; do not emit concentration, style drift, current-stage, core-risk, or manager-quality conclusions.
7. Keep `manager_alignment.judgment` as `None`.
8. Use existing public `EvidenceAnchor` and `FundExtractionGapCode` only.
9. If existing facade projection proves insufficient, stop and return to controller; do not patch `fund_agent/fund/data_extractor.py` production code under this accepted plan.
10. Update `docs/design.md` and `fund_agent/fund/README.md` only after implementation and tests pass, preserving `NOT_READY`, candidate-only, and not-proven boundaries.

## Residual Risks

| Risk | Owner | Destination |
|---|---|---|
| Real-report manager-profile field correctness remains unproven | Future evidence worker | Separate evidence gate |
| `holdings_snapshot` shared relevance to `current_stage.v1` and `core_risk.v1` | Future field-family gates | `current_stage.v1` / `core_risk.v1` source-truth planning gates |
| Broader holdings shapes such as all-stock details, bond holdings, QDII/FOF holdings | Future refinement gate | Later field-family refinement |
| Manager tenure normalization and current-manager inference | Future refinement gate | Later manager-profile refinement |
| Manager alignment judgment | Future analysis/template gate | Later CHAPTER_CONTRACT / analysis gate |

## Validation

Controller reviewed:

- `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-plan-20260620.md`
- `docs/reviews/plan-review-20260620-083543.md`
- `docs/reviews/plan-review-20260620-083605.md`
- `git status --short`

No implementation validation was run in this planning gate. Source, tests, README, design docs, repository/source code, external state and PR state were not modified by reviewers. Controller updates are limited to this judgment and control/startup bookkeeping.

## Next Entry Point

`FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Implementation Gate`

Release/readiness remains `NOT_READY`.
