# Post-P14 Follow-up Planning / Next Phase Selection（2026-05-22）

## Verdict

`ACCEPTED_CANDIDATE: P15-S1 production tracking_error golden evidence plan-review`

P14 已把 P13 新增的 `index_profile` / `tracking_error` 结构化字段纳入条件化 P1 质量分母，并补齐了 `index_profile` 的生产 golden correctness；但生产 `tracking_error` golden correctness 仍没有证据支持的真实基金行。下一阶段第一优先级应先关闭这个最小、同源、可验证的正确性缺口，而不是继续扩大到外部指数序列、指数方法论 / 成份股、QDII subtype 或 E1-E3 / Evidence Confirm 架构。

推荐下一 gate：

```text
P15-S1 production tracking_error golden evidence plan-review
```

推荐下一份 plan artifact：

```text
docs/reviews/p15-s1-production-tracking-error-golden-evidence-plan-20260522.md
```

该 gate 是 plan/review，不是 implementation。plan 通过前不得修改生产代码、测试、golden 文件、CSV、README、`docs/design.md`、`docs/implementation-control.md`、`docs/repo-audit-20260521.md`。

## Current Baseline

| Item | Baseline |
|---|---|
| Branch | `docs/post-p14-follow-up-planning` |
| Base | `main` at `fb68b17 docs: close P14 on main` |
| Current gate | `post-P14 follow-up planning / next phase selection` |
| P14 merge | PR 9 squash-merged at `746bfda7975e7c6922e80ab8c7a3e89cba3c6822`; closeout recorded in `docs/reviews/p14-main-branch-closeout-20260522.md` |
| P14 accepted behavior | `index_profile` / `tracking_error` are conditional P1 fields for `index_fund` / `enhanced_index`; non-index funds are excluded from these denominators; unknown / conflicting fund type remains conservative |
| P14 quality coverage | stable comparable sub-fields exist for `index_profile` / `tracking_error`; dataclass comparable / golden prefill uses Fund Capability value helper |
| P14 production golden | reviewed `001548` `index_profile` golden rows were added; no production `tracking_error` golden rows were added |
| P14 deterministic fixture | `161725` enhanced-index fixture covers classification, `index_profile`, and direct `tracking_error` disclosure |
| Last validation | P14 local full suite `428 passed`, ruff passed, PR CI passed, aggregate and PR reviews accepted |
| Open residuals | production `tracking_error` golden correctness; enhanced-index production golden expansion; methodology / constituents extraction; calculated tracking error / external index series adapter; QDII tracking-error subtype applicability; E1-E3 / Evidence Confirm; evidence-display / ITEM_RULE cleanup; repo-hygiene D-1/D-8-C5/C-9; RR-13 duplicate `016492` |

First-principles baseline: P13/P14 have already created the deterministic extraction and quality denominator path for a core index-fund metric. The remaining root-cause gap closest to that path is not missing calculation or audit architecture; it is that no production reviewed golden row currently proves the direct `tracking_error` value from a real selected fund.

## Candidate Comparison

| Candidate | Product value | Scope / boundary risk | Decision |
|---|---|---|---|
| production `tracking_error` golden correctness / golden evidence slice | High. It closes the exact P14 residual for the core index / enhanced-index `preferred_lens` metric and makes future regressions visible in strict golden correctness. | Low-medium if limited to reviewed annual-report evidence through existing Fund Capability/golden mechanisms; plan must stop if evidence cannot be proven. | **Select as next plan-review gate.** |
| index methodology / constituents extraction or source-contract phase | Medium-high for Chapter 1 product explanation and index risk context. | Higher. It introduces new extraction semantics and source contracts; current reviewed benchmark evidence explicitly did not prove methodology / constituents. | Defer until `tracking_error` production golden evidence is closed or proven unavailable. |
| calculated tracking error / external index series adapter | High long-term, especially when direct disclosure is absent. | High. Requires fund/index time series identity, external adapter, cache/provenance, failure taxonomy, and calculation validation. | Defer to dedicated data-source/calculation phase. |
| QDII tracking-error subtype applicability | Medium. Prevents misapplying index tracking-error logic to QDII variants. | Medium-high. Requires subtype design and applicability policy; not a golden correctness follow-up. | Defer to subtype-design phase. |
| E1-E3 / Evidence Confirm / audit architecture | High long-term for evidence-to-claim correctness. | High. Design truth keeps E1-E3, semantic audit, repair, and Evidence Confirm as future architecture; must not import Dayu runtime or LLM execution here. | Defer to future audit architecture design phase. |
| evidence-display / ITEM_RULE cleanup | Medium. Improves report readability and reduces known display/C2 noise. | Low-medium, but less directly tied to P14’s accepted residuals. | Defer. |
| repo-hygiene candidates from `docs/repo-audit-20260521.md` | Maintenance value for D-1, D-8/C-5, C-9 names already recorded in control doc. | Excluded input. This planning task must not read or include `docs/repo-audit-20260521.md`; only public candidate names from control doc may be mentioned. | Exclude from this product follow-up; future repo-hygiene phase only if explicitly selected. |
| RR-13 duplicate `016492` | Source data correctness value. | Human-owned identity conflict; unsafe for agent inference and explicitly not auto-fixed. | Exclude; remains User / App source owned. |

## Recommended Next Gate

Proceed to:

```text
P15-S1 production tracking_error golden evidence plan-review
```

Scope of the recommended plan-review gate:

- identify whether an existing selected-fund / strict-golden production case has reviewed direct `tracking_error` disclosure evidence;
- specify the exact fund code, year, annual-report section/table/row evidence anchor, `field_name`, `sub_field`, `expected_value`, confidence, and source text for any proposed production golden rows;
- define whether the rows should be added to `reports/golden-answers/golden-answer-prefill-reviewed.md`, rebuilt into `reports/golden-answers/golden-answer.json`, and reflected in `docs/golden-answer-template.md`;
- verify the same value is already extracted through the P13 direct-disclosure path and appears in P14 comparable sub-fields;
- define tests for golden prefill, strict golden schema, correctness match/mismatch/unavailable, extraction score, and sample matrix regression;
- stop before implementation if no production reviewed direct `tracking_error` evidence can be proven from current repository artifacts.

This is intentionally narrower than a new source-contract phase. It asks: “Can the current deterministic path be locked by production evidence?” It does not ask the implementation agent to create new tracking-error sources or infer values.

## Why Now

The design goal is an auditable, deterministic MVP report where index fund analysis prioritizes tracking error. P13 made direct annual-report `tracking_error` extractable; P14 made it part of quality scoring and comparable values. Without production golden correctness, the core metric is still protected mostly by deterministic fixtures rather than a real selected-fund reviewed evidence row.

That is the smallest next step that directly serves the design:

- it strengthens evidence-auditable correctness for an already implemented field;
- it keeps root cause and evidence source同源, using annual-report evidence rather than an external adapter;
- it does not introduce new source boundaries, LLM audit, Dayu runtime, or calculation semantics;
- it turns a known P14 residual into either a closed golden row or a durable “no reviewed evidence available” blocker for the next source-contract phase.

By contrast, methodology / constituents extraction, calculated tracking error, external index series, QDII subtype rules, and Evidence Confirm all require new architecture or broader business policy. Starting them before closing the production golden gap would add moving parts while the current deterministic path still lacks a real golden anchor.

## Non-goals

- Do not implement this phase in the selection artifact.
- Do not add calculated tracking error, fund/index time series, or external index series adapter.
- Do not add index methodology extraction, constituents extraction, or new document source contracts.
- Do not redesign QDII subtype applicability.
- Do not introduce E1/E2/E3, Evidence Confirm execution, LLM writing, semantic audit, RepairContract, Dayu runtime, Host, Engine, tool loop, or external Dayu API.
- Do not change `ExtractionMode`, snapshot schema, quality gate severity, Service/UI/API contract, or renderer behavior as part of this selection.
- Do not use benchmark-only evidence as proof of a `tracking_error` value.
- Do not modify RR-13 duplicate `016492` or any source CSV.
- Do not read, edit, publish, stage, or include `docs/repo-audit-20260521.md`; repo-hygiene candidate names are only acknowledged because they are already public in the control doc.
- Do not update `docs/design.md` or `docs/implementation-control.md` during this planning artifact.

## Risks / Owners

| Risk | Owner / destination | Handling |
|---|---|---|
| No current production selected fund has reviewed direct `tracking_error` disclosure evidence | P15-S1 plan-review / controller | Plan must stop and record blocker; then next candidate may become source-contract or evidence-acquisition planning. |
| Proposed `tracking_error` expected value is supported only indirectly by benchmark text | P15-S1 plan-review | Reject; benchmark identity can support `index_profile`, not `tracking_error` value. |
| Golden row confidence is overstated | P15-S1 plan-review / implementation review | Require section/table/row evidence and confidence aligned to reviewed source precision. |
| Golden update drifts beyond evidence slice into extractor or scoring redesign | Controller / code review | Reject as scope creep; those paths were completed in P13/P14 unless a targeted bug is proven. |
| Enhanced-index production golden remains absent | Future selected-fund/golden expansion | Deferred; P15-S1 may mention but should not require inventing a production enhanced-index case. |
| Methodology / constituents remain benchmark-only or unavailable | Future index source-contract phase | Deferred; do not encode unsupported availability as correctness. |
| Calculated tracking error remains absent | Future data-source/calculation phase | Deferred. |
| QDII applicability remains unmodeled | Future subtype-design phase | Deferred. |
| E1-E3 / Evidence Confirm remains absent | Future audit architecture phase | Deferred. |
| Repo-hygiene D-1, D-8/C-5, C-9 | Future repo-hygiene phase if explicitly selected | Excluded here; do not read unpublished repo-audit input. |
| RR-13 duplicate `016492` | User / App source | Human-owned; do not modify CSV automatically. |

## Success Signals

P15-S1 plan-review should pass only if the plan gives implementation agents code-generation-ready instructions for:

- the exact evidence source for each proposed production `tracking_error` golden row, including fund code, year, report section/table/row or reviewed artifact location;
- exact golden records: `field_name=tracking_error`, sub-field names, expected values, confidence, and source strings;
- proof that selected values are produced by the current P13/P14 extraction and comparable-value path;
- file ownership for later implementation, likely limited to golden reviewed markdown/JSON/template, golden prefill or tests only if needed, and docs/tests artifacts;
- stop condition when evidence is unavailable or indirect;
- validation commands and expected signals:
  - targeted golden prefill / golden answer tests;
  - targeted extraction snapshot or extraction score tests if comparable correctness assertions change;
  - sample matrix regression for direct disclosure fixture;
  - strict golden JSON schema validation;
  - `ruff check fund_agent tests`;
  - full `pytest` with no regression from P14 `428 passed`, unless test count changes are explained;
  - `git diff --check HEAD`.

Implementation success later should mean one of two outcomes:

- accepted evidence-backed production `tracking_error` golden rows are added and validated; or
- plan/review proves no such evidence is currently available, records the blocker, and routes the next phase to source-contract / evidence acquisition without editing golden files.

## Handoff For Plan-review

Suggested next prompt:

```text
Gate: P15-S1 production tracking_error golden evidence plan-review.

Use docs/reviews/post-p14-follow-up-planning-20260522.md as the accepted next-phase selection input.

Create docs/reviews/p15-s1-production-tracking-error-golden-evidence-plan-20260522.md.
Do not modify source code, tests, golden files, README, docs/design.md, docs/implementation-control.md, docs/repo-audit-20260521.md, RR-13 data, commit, push, or PR.

The plan must decide whether a production selected-fund strict-golden case has reviewed direct tracking_error disclosure evidence. If yes, specify exact fund/year/evidence anchors, golden rows, expected values, confidence, source strings, files to change in a later implementation gate, tests, validation commands, and stop conditions. If no, produce a blocker record and recommend the next source-contract/evidence-acquisition gate.

Keep all annual-report/source access behind FundDocumentRepository in any future implementation. Do not introduce calculated tracking error, external index adapters, methodology/constituents extraction, QDII subtype redesign, E1-E3, Evidence Confirm, LLM writing, Dayu runtime, Host, Engine, tool loop, repo-hygiene, or RR-13 work.
```

Plan-review rejection criteria:

- the plan starts implementation or edits files beyond the plan artifact;
- it relies on indirect benchmark evidence for `tracking_error`;
- it proposes new external sources, calculated series, methodology/constituents extraction, QDII subtype rules, or Evidence Confirm execution;
- it bypasses Fund Capability / `FundDocumentRepository` boundaries;
- it touches `docs/repo-audit-20260521.md`, RR-13 data, Service/UI/Engine, or Dayu runtime;
- it lacks exact evidence anchors, expected values, confidence, validation commands, or stop conditions.

## Validation For This Artifact

This is a docs-only controller planning artifact.

Pre-write checks:

- current branch: `docs/post-p14-follow-up-planning`;
- `HEAD`: `fb68b17 docs: close P14 on main`;
- `docs/reviews/post-p14-follow-up-planning-20260522.md` did not exist;
- existing untracked `docs/repo-audit-20260521.md` was observed and left unread/untouched.

Expected final state:

- only `docs/reviews/post-p14-follow-up-planning-20260522.md` is added;
- `docs/repo-audit-20260521.md` may remain untracked and excluded;
- no production code, tests, README, design/control docs, source CSV, golden files, commits, pushes, or PR actions are performed.
