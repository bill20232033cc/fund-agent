# 基金行为教练 Agent —— 实施总控文档

> **版本**: v1.0
> **日期**: 2026-05-16
> **设计真源**: `docs/design.md`
> **MVP 计划书**: `fund-agent-mvp-plan.md`
> **定性模板**: `fund-analysis-template-draft.md`

---

## Startup Packet

| Field | State |
|---|---|
| Branch | `docs/post-p13-follow-up-planning` |
| Current gate | `P14-S1 aggregate deepreview` |
| Next entry point | `P14-S1 aggregate deepreview` |
| Current phase | `P14 quality-denominator coverage for P13 structured fields` |
| Design truth | `docs/design.md` |
| Control truth | `docs/implementation-control.md` |
| Latest accepted planning artifact | `docs/reviews/post-p12-planning-20260522.md` |
| Latest follow-up planning artifact | `docs/reviews/post-p11-follow-up-planning-20260521.md` |
| Latest post-P11 planning artifact | `docs/reviews/post-p11-second-follow-up-planning-20260522.md` |
| Latest P11-S2 plan artifact | `docs/reviews/p11-s2-historical-summary-dedupe-plan-20260521.md` |
| Latest P12-S1 plan artifact | `docs/reviews/p12-s1-item-rule-renderer-audit-compliance-plan-20260522.md` |
| Latest P12-S2 plan artifact | `docs/reviews/post-p12-s1-follow-up-planning-20260522.md` |
| Plan reviews | `docs/reviews/p12-s1-plan-review-mimo-20260522.md`, `docs/reviews/p12-s1-plan-review-glm-20260522.md`, `docs/reviews/p12-s1-plan-rereview-mimo-20260522.md`, `docs/reviews/p12-s1-plan-rereview-glm-20260522.md` |
| Implementation artifact | `docs/reviews/p12-s1-implementation-20260522.md` |
| Code review artifacts | `docs/reviews/p12-s1-code-review-mimo-20260522.md`, `docs/reviews/p12-s1-code-review-glm-20260522.md`, `docs/reviews/p12-s1-code-review-controller-judgment-20260522.md` |
| Latest P12-S2 implementation artifact | `docs/reviews/p12-s2-implementation-20260522.md` |
| Latest P12-S2 code review artifacts | `docs/reviews/p12-s2-code-review-mimo-20260522.md`, `docs/reviews/p12-s2-code-review-glm-20260522.md`, `docs/reviews/p12-s2-code-review-controller-judgment-20260522.md` |
| Latest post-P12-S2 planning artifact | `docs/reviews/post-p12-s2-follow-up-planning-20260522.md` |
| Latest P12 aggregate artifacts | `docs/reviews/p12-aggregate-deepreview-mimo-20260522.md`, `docs/reviews/p12-aggregate-deepreview-glm-20260522.md`, `docs/reviews/p12-aggregate-deepreview-controller-judgment-20260522.md` |
| Latest P12 closeout artifact | `docs/reviews/p12-main-branch-closeout-20260522.md` |
| Latest post-P12 planning artifacts | `docs/reviews/post-p12-planning-20260522.md`, `docs/reviews/post-p12-plan-review-mimo-20260522.md`, `docs/reviews/post-p12-plan-review-glm-20260522.md`, `docs/reviews/post-p12-plan-rereview-mimo-20260522.md`, `docs/reviews/post-p12-plan-rereview-glm-20260522.md`, `docs/reviews/post-p12-plan-review-controller-judgment-20260522.md` |
| Latest release/maintenance closeout artifacts | `docs/reviews/post-p12-release-maintenance-closeout-20260522.md`, `docs/reviews/post-p12-release-maintenance-closeout-review-mimo-20260522.md` |
| Latest next-phase selection artifacts | `docs/reviews/next-phase-selection-20260522.md`, `docs/reviews/next-phase-selection-plan-review-mimo-20260522.md`, `docs/reviews/next-phase-selection-plan-review-glm-20260522.md`, `docs/reviews/next-phase-selection-controller-judgment-20260522.md` |
| Latest P13-S1 plan artifacts | `docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md`, `docs/reviews/p13-s1-plan-review-mimo-20260522.md`, `docs/reviews/p13-s1-plan-review-glm-20260522.md`, `docs/reviews/p13-s1-plan-rereview-mimo-20260522.md`, `docs/reviews/p13-s1-plan-rereview-glm-20260522.md`, `docs/reviews/p13-s1-plan-review-controller-judgment-20260522.md` |
| Latest P13 implementation artifacts | `docs/reviews/p13-tracking-error-direct-disclosure-implementation-20260522.md`, `docs/reviews/p13-tracking-error-code-review-mimo-20260522.md`, `docs/reviews/p13-tracking-error-code-review-glm-20260522.md`, `docs/reviews/p13-tracking-error-code-rereview-mimo-20260522.md`, `docs/reviews/p13-tracking-error-code-rereview-glm-20260522.md`, `docs/reviews/p13-tracking-error-code-review-controller-judgment-20260522.md` |
| Latest P13 aggregate artifacts | `docs/reviews/p13-aggregate-deepreview-mimo-20260522.md`, `docs/reviews/p13-aggregate-deepreview-glm-20260522.md`, `docs/reviews/p13-aggregate-deepreview-controller-judgment-20260522.md` |
| Latest P13 PR artifacts | `https://github.com/bill20232033cc/fund-agent/pull/7`, `docs/reviews/p13-pr-review-mimo-20260522.md`, `docs/reviews/p13-pr-review-glm-20260522.md`, `docs/reviews/p13-pr-review-controller-judgment-20260522.md` |
| Latest P13 closeout artifact | `docs/reviews/p13-main-branch-closeout-20260522.md` |
| Latest post-P13 planning artifacts | `docs/reviews/post-p13-follow-up-planning-20260522.md`, `docs/reviews/post-p13-follow-up-plan-review-mimo-20260522.md`, `docs/reviews/post-p13-follow-up-plan-review-glm-20260522.md`, `docs/reviews/post-p13-follow-up-plan-rereview-mimo-20260522.md`, `docs/reviews/post-p13-follow-up-plan-rereview-glm-20260522.md`, `docs/reviews/post-p13-follow-up-plan-review-controller-judgment-20260522.md` |
| Latest P14-S1 plan artifacts | `docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-plan-20260522.md`, `docs/reviews/p14-s1-plan-review-mimo-20260522.md`, `docs/reviews/p14-s1-plan-review-glm-20260522.md`, `docs/reviews/p14-s1-plan-rereview-mimo-20260522.md`, `docs/reviews/p14-s1-plan-rereview-glm-20260522.md`, `docs/reviews/p14-s1-plan-review-controller-judgment-20260522.md` |
| Latest P14-S1 implementation artifacts | `docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-implementation-20260522.md`, `docs/reviews/p14-s1-code-review-mimo-20260522.md`, `docs/reviews/p14-s1-code-review-glm-20260522.md`, `docs/reviews/p14-s1-code-rereview-mimo-20260522.md`, `docs/reviews/p14-s1-code-rereview-glm-20260522.md`, `docs/reviews/p14-s1-code-review-controller-judgment-20260522.md` |
| Last merged PR | PR 7, merge commit `e2d8d381b93c8d1f547836a921ea8991f1a055d8` |
| Product baseline | P10 release-readiness merged; P11 control-doc recovery accepted; P12 closed on main; post-P12 release lane maintenance-ready; P13 direct tracking-error disclosure merged |
| Open residuals | RR-13 duplicate `016492`, excluded `docs/repo-audit-20260521.md`, future P13 tracking-error/index-data candidates, future E1-E3/Evidence Confirm, repo-hygiene candidates D-1/D-8-C5/C-9 |
| Non-goal reminder | do not introduce Dayu Host/Engine/tool loop, LLM writing, or external runtime dependency |

Resume checklist: confirm current gate and next entry point; next specialist work is P14-S1 aggregate deepreview following `docs/reviews/p14-s1-code-review-controller-judgment-20260522.md`; do not delete branches, comment externally, create/modify external issues, or touch RR-13 / `docs/repo-audit-20260521.md` without explicit user authorization; preserve deterministic MVP boundaries and do not introduce LLM audit, Host, Engine, tool loop, Evidence Confirm execution, calculated index series, methodology extraction, constituents extraction, or QDII subtype redesign.

## Active Gate Ledger

| Gate | Status | Artifact | Commit / PR | Validation | Residual owner | Next action |
|---|---|---|---|---|---|---|
| `post-P10 follow-up planning accepted` | accepted | `docs/reviews/post-p10-follow-up-planning-20260521.md` | PR #6 merge `acc692c7e84c855398de86497b0d05f30b6f5ca5` | P10 CI/review pass recorded in archive | P11-S1 | closed by P11 plan |
| `P11-S1 control doc hygiene and recovery plan/review` | accepted | `docs/reviews/p11-s1-control-doc-hygiene-recovery-plan-20260521.md` | n/a | plan reviews PASS_WITH_FINDINGS; findings folded into plan | P11-S1 implementation | completed |
| `P11-S1 implementation/code review` | accepted | `docs/reviews/p11-s1-implementation-20260521.md`, `docs/reviews/p11-s1-code-review-controller-judgment-20260521.md` | local docs-only change | diff check and artifact reference check passed; MiMo PASS, GLM PASS_WITH_FINDINGS accepted | post-P11 planning | follow-up planning |
| `post-P11 follow-up planning` | accepted | `docs/reviews/post-p11-follow-up-planning-20260521.md` | `5f5331b` | P11-S1 recovery accepted; remaining archive duplicate rows scoped to docs-only cleanup | P11-S2 | plan/review |
| `P11-S2 historical summary dedupe plan/review` | accepted | `docs/reviews/p11-s2-historical-summary-dedupe-plan-20260521.md`, `docs/reviews/p11-s2-plan-review-controller-judgment-20260521.md` | local docs-only plan | MiMo/GLM initial PASS_WITH_FINDINGS; targeted re-reviews PASS | P11-S2 implementation | implementation |
| `P11-S2 implementation/code review` | accepted | `docs/reviews/p11-s2-implementation-20260521.md`, `docs/reviews/p11-s2-code-review-controller-judgment-20260521.md` | local docs-only change | MiMo/GLM PASS_WITH_FINDINGS; Startup Packet residual bookkeeping fixed | post-P11 planning | follow-up planning |
| `post-P11 follow-up planning accepted` | accepted | `docs/reviews/post-p11-second-follow-up-planning-20260522.md` | `ba77e02` | P11 recovery accepted; ITEM_RULE deterministic compliance selected as next product slice | P12-S1 | plan/review |
| `P12-S1 ITEM_RULE renderer/audit compliance plan/review` | accepted | `docs/reviews/p12-s1-item-rule-renderer-audit-compliance-plan-20260522.md`, `docs/reviews/p12-s1-plan-review-controller-judgment-20260522.md` | local docs-only plan | MiMo/GLM initial PASS_WITH_FINDINGS; targeted re-reviews PASS | P12-S1 implementation | implementation |
| `P12-S1 ITEM_RULE renderer/audit compliance implementation/code review` | accepted | `docs/reviews/p12-s1-implementation-20260522.md`, `docs/reviews/p12-s1-code-review-controller-judgment-20260522.md` | `c757036` | controller verified diff check, targeted `81 passed`, adjacent `43 passed`, ruff passed, full `401 passed`; MiMo PASS; GLM PASS | post-P12-S1 planning | follow-up planning |
| `P12-S2 ITEM_RULE multi-anchor evidence boundary plan/review` | accepted | `docs/reviews/post-p12-s1-follow-up-planning-20260522.md`, `docs/reviews/p12-s2-plan-review-controller-judgment-20260522.md` | local docs-only plan | MiMo/GLM initial PASS_WITH_FINDINGS; targeted re-reviews PASS | P12-S2 implementation | implementation |
| `P12-S2 ITEM_RULE multi-anchor evidence boundary implementation/code review` | accepted | `docs/reviews/p12-s2-implementation-20260522.md`, `docs/reviews/p12-s2-code-review-controller-judgment-20260522.md` | `24a35b4` | controller verified renderer `35 passed`, item_rules+audit `48 passed`, ruff passed, diff check passed, full `403 passed`; MiMo PASS; GLM PASS | post-P12-S2 planning | follow-up planning |
| `post-P12-S2 follow-up planning` | accepted | `docs/reviews/post-p12-s2-follow-up-planning-20260522.md`, `docs/reviews/post-p12-s2-follow-up-plan-review-controller-judgment-20260522.md` | local docs-only plan | MiMo PASS; GLM PASS_WITH_FINDINGS accepted; aggregate base verified as `ba77e02..HEAD` | P12 aggregate deepreview | aggregate review |
| `P12 aggregate deepreview` | accepted | `docs/reviews/p12-aggregate-deepreview-mimo-20260522.md`, `docs/reviews/p12-aggregate-deepreview-glm-20260522.md`, `docs/reviews/p12-aggregate-deepreview-controller-judgment-20260522.md` | local review artifacts | aggregate range `ba77e02..HEAD`; MiMo PASS; GLM PASS; controller verified diff check, targeted `83 passed`, adjacent `43 passed`, ruff passed, full `403 passed` | P12 main-branch closeout | closeout reconciliation |
| `P12 main-branch closeout reconciliation` | accepted | `docs/reviews/p12-main-branch-closeout-20260522.md` | local closeout artifact | P12 commits already on `main`; no retroactive draft PR gate applicable | post-P12 planning | follow-up planning |
| `post-P12 planning` | accepted | `docs/reviews/post-p12-planning-20260522.md`, `docs/reviews/post-p12-plan-review-controller-judgment-20260522.md` | local docs-only plan | MiMo/GLM initial `PASS_WITH_FINDINGS`; targeted re-reviews `PASS`; all 7 findings closed | release/maintenance closeout | closeout |
| `post-P12 release/maintenance closeout` | accepted | `docs/reviews/post-p12-release-maintenance-closeout-20260522.md`, `docs/reviews/post-p12-release-maintenance-closeout-review-mimo-20260522.md` | local docs-only closeout | controller validation passed: branch `main`, `pytest` 403 passed, ruff passed, diff check passed; MiMo closeout review PASS | maintenance-ready / next phase selection | next phase selection |
| `next phase selection` | accepted | `docs/reviews/next-phase-selection-20260522.md`, `docs/reviews/next-phase-selection-controller-judgment-20260522.md` | local docs-only selection | MiMo `pass-with-risks`; GLM `PASS`; risks assigned to P13-S1 plan constraints | P13-S1 tracking-error / index-data source contract plan-review | plan/review |
| `P13-S1 tracking-error / index-data source contract plan-review` | accepted | `docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md`, `docs/reviews/p13-s1-plan-review-controller-judgment-20260522.md` | local docs-only plan | MiMo/GLM initial reviews found 9 findings; revised plan re-reviews PASS/PASS; all findings closed | P13 tracking-error direct-disclosure implementation | implementation |
| `P13 tracking-error direct-disclosure implementation/code review` | accepted | `docs/reviews/p13-tracking-error-direct-disclosure-implementation-20260522.md`, `docs/reviews/p13-tracking-error-code-review-controller-judgment-20260522.md` | `2172691` | full suite `424 passed`; ruff passed; diff check passed; MiMo PASS then rereview PASS; GLM PASS_WITH_FINDINGS then rereview PASS | P13 aggregate deepreview | aggregate review |
| `P13 aggregate deepreview` | accepted | `docs/reviews/p13-aggregate-deepreview-mimo-20260522.md`, `docs/reviews/p13-aggregate-deepreview-glm-20260522.md`, `docs/reviews/p13-aggregate-deepreview-controller-judgment-20260522.md` | `ffa8eff` | MiMo PASS; GLM PASS; controller verified full suite `424 passed`, ruff passed, diff check passed | ready-to-open-draft-PR | draft PR gate |
| `P13 draft PR gate / PR review` | accepted | `https://github.com/bill20232033cc/fund-agent/pull/7`, `docs/reviews/p13-pr-review-mimo-20260522.md`, `docs/reviews/p13-pr-review-glm-20260522.md`, `docs/reviews/p13-pr-review-controller-judgment-20260522.md` | `cd2ad31` | PR 7 CI `test` passed; MiMo PASS; GLM PASS; controller `git diff --check HEAD` passed | P13 residuals assigned to future phases / user | draft-PR-pass |
| `P13 main-branch closeout` | accepted | `docs/reviews/p13-main-branch-closeout-20260522.md` | PR 7 merge `e2d8d381b93c8d1f547836a921ea8991f1a055d8` | PR 7 merged; CI and PR reviews passed before merge | P13 residuals assigned to future phases / user | post-P13 follow-up planning / next phase selection |
| `post-P13 follow-up planning / next phase selection` | accepted | `docs/reviews/post-p13-follow-up-planning-20260522.md`, `docs/reviews/post-p13-follow-up-plan-review-controller-judgment-20260522.md` | `1908a4f` | MiMo/GLM initial `PASS_WITH_FINDINGS`; targeted re-reviews `PASS`; controller `git diff --check HEAD` passed | P14-S1 plan/review | plan/review |
| `P14-S1 index_profile / tracking_error quality-denominator plan-review` | accepted | `docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-plan-20260522.md`, `docs/reviews/p14-s1-plan-review-controller-judgment-20260522.md` | `c7d0ec8` | MiMo/GLM initial `PASS_WITH_FINDINGS`; targeted re-reviews `PASS`; controller `git diff --check HEAD` passed | P14-S1 implementation | implementation |
| `P14-S1 index_profile / tracking_error quality-denominator implementation/code review` | accepted | `docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-implementation-20260522.md`, `docs/reviews/p14-s1-code-review-controller-judgment-20260522.md` | local accepted implementation commit pending | controller verified snapshot `5 passed`, score/quality `46 passed`, golden `5 passed`, sample matrix `1 passed`, service/quality integration `9 passed`, ruff passed, full suite `428 passed`, diff check passed; MiMo PASS; GLM PASS_WITH_FINDINGS then targeted re-review PASS/PASS | P14-S1 aggregate deepreview | aggregate review |

## Phase History Index

| Phase / sequence | Status | Archive | Primary artifacts | Merge / accepted commit | Last validation | Open residuals |
|---|---|---|---|---|---|---|
| P0 | done | [Archive: P0](#archive-p0) | original control record | n/a | environment baseline recorded | none active |
| P1 | done | [Archive: P1](#archive-p1) | P1 slice artifacts, `docs/reviews/p1-aggregate-review-2026-05-17.md` | multiple slice commits | P1 matrix `36/36` | none active |
| P2 | done | [Archive: P2](#archive-p2) | P2 implementation/review artifacts | `07fe0d0` accepted deepreview | analysis/audit tests recorded | none active |
| P3 | done / PR #2 merged | [Archive: P3](#archive-p3) | PR #2 review artifacts | `0be218f28ea7d26c7ad1e55963ca907217f5dede` | `116 passed / 90.07%` coverage matrix | none active |
| P4 | done / PR #3 merged | [Archive: P4](#archive-p4) | `docs/implementation-control-p4.md`, P4 review artifacts | `7596c5ece4894166d5479ee764fc8641a23cfc0d` | targeted/full suites recorded | RR-13 remains human-owned |
| P5 | done / PR #4 merged | [Archive: P5](#archive-p5) | P5 quality gate artifacts, `docs/reviews/p5-s6-user-app-source-reconciliation-20260520.md` | `d33b901fd1bee9f85206df461cc6419a813bcbae` | full suite `206 passed` | RR-13 human-owned |
| P6 | done | [Archive: P6](#archive-p6) | P6 contract manifest and renderer alignment artifacts | slice commits recorded | full suite up to `221 passed` | template typo cleanup deferred |
| P7 | done | [Archive: P7](#archive-p7) | source migration/reconciliation artifacts | post-P7 commits recorded | full suite `322 passed` baseline | none active |
| P8 | done | [Archive: P8](#archive-p8) | P8-S1/S2/S3 plan and review artifacts | `90bb9d2`, `b4aaaaa` recorded | full suite `347 passed` | none active |
| P9 | done | [Archive: P9](#archive-p9) | P9 product contract and aggregate deepreview artifacts | `2bacdb3`, `ce603a0` recorded | full suite `377 passed` | review limitation documented |
| P10 | merged | [Archive: P10](#archive-p10) | P10 plan/code/aggregate/PR artifacts | PR #6 merge `acc692c7e84c855398de86497b0d05f30b6f5ca5` | full suite `388 passed`, CI pass | `docs/repo-audit-20260521.md` excluded |
| P11 | accepted | [Archive: P11](#archive-p11) | P11 plan/review/implementation/code-review/follow-up/P11-S2 artifacts | `5f5331b` | P11-S2 docs-only validation passed | closed |
| P12 / next selection | accepted | [Archive: P12](#archive-p12) | `docs/reviews/post-p11-second-follow-up-planning-20260522.md`, `docs/reviews/p12-s1-plan-review-controller-judgment-20260522.md`, `docs/reviews/p12-s1-code-review-controller-judgment-20260522.md`, `docs/reviews/p12-s2-plan-review-controller-judgment-20260522.md`, `docs/reviews/p12-aggregate-deepreview-controller-judgment-20260522.md`, `docs/reviews/p12-main-branch-closeout-20260522.md`, `docs/reviews/post-p12-release-maintenance-closeout-20260522.md`, `docs/reviews/next-phase-selection-controller-judgment-20260522.md` | `69d5b3e` | full suite `403 passed`; aggregate PASS/PASS; release closeout review PASS; next selection reviews pass-with-risks/PASS | P13-S1 plan/review |
| P13 | merged | [Archive: P13](#archive-p13) | `docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md`, `docs/reviews/p13-s1-plan-review-controller-judgment-20260522.md`, `docs/reviews/p13-tracking-error-code-review-controller-judgment-20260522.md`, `docs/reviews/p13-aggregate-deepreview-controller-judgment-20260522.md`, `docs/reviews/p13-pr-review-controller-judgment-20260522.md`, `docs/reviews/p13-main-branch-closeout-20260522.md`, `docs/reviews/post-p13-follow-up-plan-review-controller-judgment-20260522.md` | PR 7 merge `e2d8d381b93c8d1f547836a921ea8991f1a055d8` | full suite `424 passed`; code re-reviews PASS/PASS; aggregate PASS/PASS; PR reviews PASS/PASS; PR CI passed; post-P13 planning re-reviews PASS/PASS | P14-S1 plan/review |
| P14-S1 | implementation accepted | [Archive: P14](#archive-p14) | `docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-plan-20260522.md`, `docs/reviews/p14-s1-plan-review-controller-judgment-20260522.md`, `docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-implementation-20260522.md`, `docs/reviews/p14-s1-code-review-controller-judgment-20260522.md` | local accepted implementation commit pending | full suite `428 passed`; ruff passed; code re-reviews PASS/PASS | P14-S1 aggregate deepreview |

## P12 Current Phase Notes

P12 goal: make ITEM_RULE deterministic compliance observable in the final renderer/audit path while preserving Fund Capability ownership and deterministic MVP boundaries. P12-S1 is accepted: renderer produces ITEM_RULE decisions/context from classified fund type, deterministic segments render only in target chapter bodies, and programmatic C2 audits renderer-produced decisions. P12-S2 is accepted: ITEM_RULE local evidence boundary renders all deduped relevant anchors in one bullet without changing evidence sufficiency semantics.

Post-P12-S1 guardrails:

- Do not modify RR-13 source data or include `docs/repo-audit-20260521.md` unless a future scope explicitly accepts it.
- Do not auto-resolve RR-13 duplicate `016492`.
- Do not introduce Dayu runtime, Host, Engine, tool loop, prompt scene registry, or LLM writing as part of follow-up planning.
- Keep ITEM_RULE evidence/extractor follow-ups separate from renderer/audit compliance unless a future plan explicitly owns those inputs.

Success signals for the next step: P14-S1 plan defines exact FQ2 priority, comparable sub-field, golden correctness, not-applicable, fixture, and validation behavior for `index_profile` / `tracking_error` without reopening P13 extraction scope or introducing new sources.

## Active Residuals

| Risk | Owner | Required handling |
|---|---|---|
| RR-13 duplicate `016492` | User / App source | Preserve as human-owned; do not modify CSV automatically; if unresolved before the next product phase, treat as that phase planning's explicit blocking input |
| `docs/repo-audit-20260521.md` | Controller / user | Keep excluded unless later scope explicitly accepts publication |
| Future tracking-error / index methodology / constituents extraction | Future P13 Fund Capability documents/extractor/calculation phase | Must be designed through `FundDocumentRepository`; do not let Service/UI read source internals |
| Future E1-E3 / Evidence Confirm | Future audit architecture phase | Keep separate from deterministic closeout and do not introduce LLM/Dayu runtime without a dedicated design |
| Future evidence-display / ITEM_RULE cleanup | Future evidence-display or rule-addition slice | Long-anchor truncation/grouping, future ITEM_RULE expansion, and duplicate chapter-mismatch C2 noise remain out of P12 scope |
| Repo-hygiene candidates D-1, D-8/C-5, C-9 | Future repo-hygiene phase if selected | Keep as open candidates from `docs/repo-audit-20260521.md`; do not mark them fully covered by P10/P11/P12 |
| P13-S1 planning constraints | P13-S1 plan/review | Resolve tracking-error authority, service override migration, external index adapter upper bound, methodology/constituents availability, positive acceptance criteria, and index fixture strategy before implementation |
| P13 implementation residuals | P13 implementation / future P13 follow-up | Direct disclosure may proceed; calculated tracking error, external index series, methodology extraction, constituents extraction, and golden-answer promotion remain out of first implementation unless explicitly re-scoped |

## Evidence Preservation Rules

Every accepted gate archive entry must preserve available artifact paths, plan review paths, code review paths, controller judgment paths, re-review paths, implementation artifact paths, accepted local commit hashes, PR URLs, PR branch/head/merge commits, CI run IDs and status, validation commands and exact pass counts, residual risk IDs and owners, and reviewer limitations or availability caveats.

If an old entry lacks one of these fields, do not invent it. Use `not recorded` only when the historical record truly lacks it. Missing local artifact references must be marked and assigned to controller reconciliation; do not silently replace them with nearby artifacts.

## Archive / Summarize Strategy

Use three levels of detail:

1. Active startup packet: current gate, next entry point, latest artifacts, open residuals, and immediate next action.
2. Phase history index: one row per phase or major sequence, with anchors and primary artifacts.
3. Historical evidence archive: detailed historical gate log retained in the same file.

Duplicated prose may be summarized only when exact facts remain in a table or archive entry. Do not delete artifact paths, commit hashes, PR links, validation results, or residual owners. If a future slice splits history into a separate file, this control doc must still identify that file as part of the control record.

## Design / Control Alignment Rules

1. `docs/design.md` remains the design truth for architecture, boundaries, product behavior, Dayu non-dependency, and `FundDocumentRepository` source boundaries.
2. `docs/implementation-control.md` remains the control truth for phase state, gates, artifacts, commits, validation, residual risks, and next entry point.
3. A control-doc hygiene pass may reorganize implementation history but may not change design facts.
4. If control history contradicts `docs/design.md`, create a reconciliation artifact before changing either document.
5. Current design facts that must not regress during P11: `fund-analysis analyze` remains deterministic UI -> Service -> Fund Capability; Dayu remains methodology/reference only; `FundDocumentRepository` remains the production annual-report entry point; fallback taxonomy remains `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`; no prompt scene registry, Host session, Engine tool loop, or LLM writing is introduced.

## Historical Evidence Archive

The archive headings below are unique phase-prefixed anchors for `Phase History Index`. Detailed historical evidence remains in the original control record that follows these anchors.

## Archive: P0

P0 environment and architecture skeleton evidence is preserved in the original control record below, including the P0 phase definition and status log entries.

## Archive: P1

P1 document access, parsing, extraction, cache, and façade evidence is preserved below, including slice artifacts, accepted commits, and P1 aggregate review paths.

## Archive: P2

P2 analysis, checklist, stress test, renderer, evidence anchor, and programmatic audit evidence is preserved below, including implementation/review artifacts and accepted deepreview commit.

## Archive: P3

P3 CLI, integration tests, README, coverage, performance, PR #2 review, and merge evidence is preserved below.

## Archive: P4

P4 selected fund pool, extraction snapshot, scoring, quality gate, correctness, RR-13, PR #3, and merge evidence is preserved below and in `docs/implementation-control-p4.md`.

## Archive: P5

P5 analyze quality gate integration, quality rules, snapshot sub-fields, failure accounting, share change hardening, thermometer, RR-13, PR #4, and merge evidence is preserved below.

## Archive: P6

P6 CHAPTER_CONTRACT manifest and renderer contract alignment evidence is preserved below, including plan/review artifacts and validation results.

## Archive: P7

P7 annual-report source migration and post-P7 follow-up evidence is preserved below, including repository review reconciliation and full-suite baselines.

## Archive: P8

P8 must_answer routing, preferred_lens deterministic rendering, source fallback taxonomy, aggregate closure, and post-P8 planning evidence is preserved below.

## Archive: P9

P9 analyze product contract, developer override separation, golden coverage calibration, aggregate reviews, and reviewer limitation evidence is preserved below.

## Archive: P10

P10 repo hygiene, release readiness, PR #6 draft/merge gate, CI, excluded repo-audit input, and merge commit evidence is preserved below.

## Archive: P11

P11 control doc hygiene plan/review, implementation, code review, post-P11 planning, and P11-S2 implementation/code-review evidence is preserved in the startup packet, active ledger, this archive heading, `docs/reviews/p11-s1-implementation-20260521.md`, `docs/reviews/p11-s1-code-review-controller-judgment-20260521.md`, `docs/reviews/post-p11-follow-up-planning-20260521.md`, `docs/reviews/p11-s2-plan-review-controller-judgment-20260521.md`, and `docs/reviews/p11-s2-code-review-controller-judgment-20260521.md`.

## Archive: P12

P12 ITEM_RULE deterministic compliance planning starts from `docs/reviews/post-p11-second-follow-up-planning-20260522.md`. P12-S1 plan/review is accepted in `docs/reviews/p12-s1-plan-review-controller-judgment-20260522.md`; implementation/code review is accepted in `docs/reviews/p12-s1-code-review-controller-judgment-20260522.md`. P12-S2 plan/review is accepted in `docs/reviews/p12-s2-plan-review-controller-judgment-20260522.md`; implementation/code review is accepted in `docs/reviews/p12-s2-code-review-controller-judgment-20260522.md`. P12 aggregate deepreview is accepted in `docs/reviews/p12-aggregate-deepreview-controller-judgment-20260522.md`; main-branch closeout is recorded in `docs/reviews/p12-main-branch-closeout-20260522.md`. Post-P12 planning is accepted in `docs/reviews/post-p12-plan-review-controller-judgment-20260522.md` and selects release/maintenance closeout before any P13 product phase. Release/maintenance closeout is accepted in `docs/reviews/post-p12-release-maintenance-closeout-20260522.md`; next phase selection is accepted in `docs/reviews/next-phase-selection-controller-judgment-20260522.md` and selects P13-S1 tracking-error / index-data source contract plan-review. P12 keeps ITEM_RULE ownership in Fund Capability and preserves deterministic MVP boundaries.

## Archive: P13

P13 starts with source-contract planning for direct tracking-error disclosure, selected in `docs/reviews/next-phase-selection-controller-judgment-20260522.md`. P13-S1 plan/review is accepted in `docs/reviews/p13-s1-plan-review-controller-judgment-20260522.md`. Direct tracking-error disclosure implementation is accepted in `docs/reviews/p13-tracking-error-code-review-controller-judgment-20260522.md`: Fund Capability now has typed `index_profile` and `tracking_error` fields, direct annual-report tracking-error extraction, Service risk-check authority migration to resolved structured data, renderer/audit consumption, snapshot observability without FQ2/comparable/golden denominator promotion, deterministic fixtures, and synced Fund/test docs. Aggregate deepreview is accepted in `docs/reviews/p13-aggregate-deepreview-controller-judgment-20260522.md`. PR 7 (`https://github.com/bill20232033cc/fund-agent/pull/7`) is accepted in `docs/reviews/p13-pr-review-controller-judgment-20260522.md` and squash-merged to `main` at `e2d8d381b93c8d1f547836a921ea8991f1a055d8`; closeout is recorded in `docs/reviews/p13-main-branch-closeout-20260522.md`. Post-P13 follow-up planning is accepted in `docs/reviews/post-p13-follow-up-plan-review-controller-judgment-20260522.md` and selects P14-S1 `index_profile` / `tracking_error` quality-denominator plan-review. Calculated index series, methodology extraction, constituents extraction, E1/E2/E3, Evidence Confirm, Dayu runtime, RR-13 data, and `docs/repo-audit-20260521.md` remain out of first implementation scope.

## Archive: P14

P14 starts with `index_profile` / `tracking_error` quality-denominator coverage for P13 structured fields. P14-S1 plan/review is accepted in `docs/reviews/p14-s1-plan-review-controller-judgment-20260522.md`: the approved implementation keeps `ExtractionMode` unchanged, makes `index_profile` and `tracking_error` conditional P1 quality fields for `index_fund` / `enhanced_index`, excludes non-index fund types from the denominator for these fields, adds scalar comparable sub-fields, and gates production golden correctness on existing reviewed evidence. P14-S1 implementation/code review is accepted in `docs/reviews/p14-s1-code-review-controller-judgment-20260522.md`: `index_profile` / `tracking_error` now enter quality denominator only for index and enhanced-index funds, unknown/conflicting fund type stays conservative, dataclass comparable/golden prefill paths share a Fund Capability value helper, reviewed `001548` `index_profile` golden rows were added, and `161725` enhanced-index fixture covers the direct disclosure path. Non-goals remain calculated tracking error, external index adapters, methodology/constituents extraction, QDII subtype redesign, E1/E2/E3, Evidence Confirm, Dayu runtime, RR-13 data, and `docs/repo-audit-20260521.md`.

## Original Detailed Control Record

### Historical Snapshot Before P11-S1 Implementation（2026-05-21）

This snapshot records the pre-P11-S1 implementation state only. It is not current gate truth; use `Startup Packet` and `Active Gate Ledger` for current state.

| 项目 | 历史状态 |
|------|----------|
| 当时分支 | `main` |
| 当时 gate | `P11-S1 plan accepted` |
| 当时下一 entry point | `P11-S1 implementation` |
| 设计真源 | `docs/design.md`，已按 `docs/design-update.md` reconciliation 收口 |
| 近期设计裁决 | `docs/reviews/design-update-reconciliation-20260521.md`、`docs/reviews/implementation-control-update-reconciliation-20260521.md` |
| P8 交付物 | `must_answer` audit routing、renderer `preferred_lens` deterministic application、source fallback taxonomy |
| 当时残余风险 | repo hygiene、control doc hygiene、RR-13 精选池 CSV 重复待人工裁决 |

本历史快照所在控制文档仍是 phaseflow 的总控真源：详细 gate、artifact、review、commit、验证和 residual risk 记录保留在后文，不用摘要替代。`docs/implementation-control-update.md` 仅作为摘要候选输入；经 reconciliation 后只融合稳定 summary，不替换本文件。

### 1.1 Phase 列表

| Phase | 名称 | 周期 | 状态 | 依赖 |
|-------|------|------|------|------|
| P0 | 环境搭建与架构骨架 | Week 1 | ✅ done | 无 |
| P1 | 数据层（PDF 下载 + 解析 + 提取） | Week 2-3 | ✅ done | P0 |
| P2 | 分析引擎（R=A+B-C + 检验 + 审计） | Week 3-4 | ✅ done | P1 |
| P3 | CLI 入口 + 整合测试 + 验证 | Week 4-5 | ✅ done | P2 |
| P4 | 精选基金池质量闭环（snapshot + score + quality gate） | Post-MVP | ✅ done | P3 |
| P5 | 报告主链路质量保护（quality gate integration） | Post-P4 | ✅ done | P4 |
| P6 | 模板契约机器化（CHAPTER_CONTRACT / ITEM_RULE） | Post-P5 | ✅ done | P5 |
| P7 | 年报来源迁移（EID 主源 + Eastmoney fallback） | Post-P6 | ✅ done | P6 |
| P8 | 模板契约与来源策略加固（must_answer audit / preferred_lens / source fallback） | Post-P7 | ✅ done | P7 |
| P9 | Analyze 产品契约加固（用户最小输入 + dev override 分离） | Post-P8 | ✅ done | P8 |
| P10 | Repo hygiene / release readiness | Post-P9 | ✅ merged | P9 |
| P11 | Control doc hygiene / recovery ergonomics | Post-P10 | 🟡 in progress | P10 |

### 1.1.1 能力域摘要

| 能力域 | 当前状态 | 稳定入口 / 归属 |
|--------|----------|----------------|
| CLI / UI | 已实现用户入口和开发辅助命令 | `fund_agent/ui/cli.py` |
| Service 编排 | 已实现主分析、快照、评分、quality gate、golden answer、温度计等 use case | `fund_agent/services/` |
| 文档仓库 | 统一仓库入口、PDF/parsed cache、source metadata、EID 主源 + Eastmoney fallback | `fund_agent/fund/documents/` |
| 结构化抽取 | P1 数据 façade 与 profile/performance/manager/holdings extractors | `fund_agent/fund/data_extractor.py`、`fund_agent/fund/extractors/` |
| 分析引擎 | R=A+B-C、alpha nature、言行一致性、投资者获得感、风险、压力测试、检查清单 | `fund_agent/fund/analysis/` |
| 模板系统 | CHAPTER_CONTRACT、ITEM_RULE、preferred_lens、renderer、chapter blocks | `fund_agent/fund/template/` |
| 程序审计 | P1/P2/P3/C2/L1/R1/R2 确定性子集 | `fund_agent/fund/audit/` |
| 质量门控 | snapshot / score / quality gate / golden answer correctness | `fund_agent/fund/quality_gate*.py`、`fund_agent/fund/extraction_*` |
| 外部数据 | NAV 与有知有行温度计 read-only 查询 | `fund_agent/fund/data/` |

### 1.1.2 当前技术债与后续规划摘要

| 类别 | 状态 | Owner / Destination |
|------|------|---------------------|
| Product contract | P9-S1 已接受：用户最小输入、developer override 分离、final judgment 派生与 R2 审计已收口 | closed by P9-S1 |
| Repo hygiene | P10 已通过 PR #6 squash merge 到 `main`；`docs/repo-audit-20260521.md` 继续排除，除非后续 scope 明确接受发布 | closed by P10 / repo-audit remains excluded |
| Control doc hygiene | P11-S1 recovery 已接受；P11-S2 historical summary dedupe 以 documentation-only 方式清理旧摘要重复和陈旧 gate 表述，证据链保留 | closed by P11-S2 implementation |
| Dependency strategy | Dayu 裁决为方法论参考，生产依赖移除；后续 runtime 能力必须项目内化 | closed by 2026-05-21 reconciliation |
| Quality gate ROI | P9-S2 已接受：区分 gate not-run 与 correctness coverage gap；精选池成员缺 strict golden 覆盖输出 FQ0/info | closed by P9-S2 |
| P9 aggregate review coverage | P9 aggregate deepreview 已接受；AgentDS 独立 PASS，AgentMiMo 补充 PASS 但记录 P9-S2 reviewer limitation | closed by P9 aggregate |
| RR-13 duplicate `016492` | 精选基金池 CSV 源数据身份冲突保持人工裁决，不由代码或文档清理自动修复 | User / App source |

### 1.2 里程碑

| 里程碑 | 目标日期 | 关联 Phase | 验收标准 |
|--------|---------|-----------|---------|
| M1: 架构就绪 | Week 1 结束 | P0 | 四层骨架可运行，样本基金 PDF 可下载解析 |
| M2: 数据管道可用 | Week 3 中 | P1 | 12 项关键数据提取准确率 > 90% |
| M3: 分析引擎可用 | Week 4 中 | P2 | R=A+B-C 计算正确，言行一致性检验输出信号 |
| M4: MVP 交付 | Week 5 结束 | P3 | `fund-analysis <code>` 输出完整 8 章报告 |

### 1.3 P11-S1 前历史 Gate 与基线裁决（2026-05-21）

- 当时分支：`main`
- 当时 gate：`P11-S1 plan accepted`
- 当时下一 gate：`P11-S1 implementation`
- Repo findings 收口：003（QDII basis 记录并发指数证据）已修复；005（CSV ValueError/FNFE 分离）已修复；006（alpha 空 observations MVP 注释）已文档化；004/008/009/010 低严重度保持 deferred。
- P4 执行控制文档：`docs/implementation-control-p4.md`
- 当前裁决：
  - P7 已完成并直接集成到 `main`。当前年报来源顺序为 EID/证监会资本市场统一信息披露平台主源，Eastmoney/akshare fallback，经 `FundDocumentRepository` 统一封装；source metadata/cache provenance 和 legacy cache compatibility 已接入。
  - repo-level `deepreview --all` 已完成，MiMo/DS artifacts 已入库；controller 已完成 aggregate fix，commit=`58bba13`。已修复 PDF 内容校验/原子写入、parsed report JSON cache crash loop、quality gate `block + not_run` 结构化阻断和 `analyze` fund_code 校验；全量测试 `299 passed`。
  - Post-P7 follow-up planning 已接受，commit=`26adce7`。`CLAUDE.md` 已从旧 `zhixing` 项目说明重写为当前 `fund-agent` 指南；旧项目关键词检查无命中；全量测试 `299 passed`。
  - Post-P7 code findings 已全部收口并提交；当前 tracked worktree clean，full suite baseline `322 passed`。DS repo review reconciliation 已更新到当前 HEAD，artifact=`docs/reviews/repo-review-ds-20260520.md`。
  - Post-P7 residual design slice planning 已形成，artifact=`docs/reviews/post-p7-residual-design-slice-planning-20260521.md`。剩余项均为后续 design slice：`must_answer` 审计消费、renderer `preferred_lens` 应用、EID schema fallback 策略、preflight quality gate 性能优化、C2 marker 粒度；均不阻塞当前代码基线。
  - P8-S1 must_answer audit contract design 已通过 plan/review，commit=`f3bbfc9`。实现已完成并通过 controller code review，implementation commit=`5f5a7a6`，review artifact=`docs/reviews/code-review-20260521-043045.md`。新增独立 `ContractAuditCoverageManifest` 逐条路由 45 条 `must_answer`，保持 `ProgrammaticContractRules` 只代表确定性 C2 marker 规则；当前内置映射为 44 条 `covered_by_required_item`、1 条 `narrative_guidance`、0 条 `programmatic_marker`。验证：targeted `30 passed`、full suite `329 passed`、ruff passed、diff check passed。
  - Post-P8-S1 follow-up planning 已接受，artifact=`docs/reviews/post-p8-s1-follow-up-planning-20260521.md`。P8-S1 已关闭 `must_answer` 确定性 contract-routing residual；下一优先级裁决为 `P8-S2 renderer preferred_lens application design`，目标是在 Capability template 层定义 lens 如何影响确定性 renderer 输出，禁止简单把 raw lens statements 粘贴进报告 Markdown。
  - P8-S2 renderer preferred_lens application design plan/review 已通过，plan artifact=`docs/reviews/p8-s2-renderer-preferred-lens-application-plan-20260521.md`，review artifact=`docs/reviews/plan-review-20260521-052601.md`，re-review artifact=`docs/reviews/plan-review-20260521-052707.md`。计划裁决为：新增 Capability-owned `LensApplicationPlan`，renderer 只在第 0/1 章确定性 slot 应用 normalized lens labels，不渲染 raw `TemplateLensRule.statements`，不改变 Service/UI/Engine、quality gate 或 `ProgrammaticAuditInput`；下一 gate 为 `P8-S2 implementation`。
  - P8-S2 renderer preferred_lens application implementation 已完成并通过 controller code review，implementation commit=`6dbf6ca`，review artifact=`docs/reviews/code-review-20260521-060057.md`。实现新增 Capability-owned `LensApplicationPlan`，renderer 仅在第 0/1 章确定性 slot 应用 normalized lens labels，不渲染 raw `TemplateLensRule.statements`，并保持 `ProgrammaticAuditInput` 形状不变；当前验证 targeted `67 passed`、full suite `344 passed`、ruff passed、diff check passed；下一 gate 为 `post-P8-S2 follow-up planning`。
  - Post-P8-S2 follow-up planning 已接受，artifact=`docs/reviews/post-p8-s2-follow-up-planning-20260521.md`。P8-S1/P8-S2 已分别关闭 `must_answer` contract-routing 与 renderer `preferred_lens` deterministic application residual；下一优先级裁决为 `P8-S3 source fallback policy design`，目标是在 Fund Capability document source 层显式定义 EID/Eastmoney 来源错误分类、fallback eligibility 与 fallback-blocked provenance，避免官方来源 schema drift / identity mismatch / integrity error 被商业站 fallback 静默掩盖。
  - P8-S3 source fallback policy design plan/review 已通过，plan artifact=`docs/reviews/p8-s3-source-fallback-policy-plan-20260521.md`，review artifact=`docs/reviews/plan-review-20260521-060952.md`。计划裁决为：在 Fund Capability document source 层新增五类来源失败 taxonomy、table-driven fallback eligibility 和 fallback-blocked structured exception；`not_found/unavailable` 可 fallback，`schema_drift/identity_mismatch/integrity_error` 必须 fail closed 并保留 source/category/message provenance；下一 gate 为 `P8-S3 implementation`。
  - Post-P8 planning 已接受，artifact=`docs/reviews/post-p8-planning-20260521.md`。P9 第一优先级裁决为 `analyze` 产品契约加固：区分普通用户最小输入与 developer override，设计最终判断派生策略，并保持 UI / Service / Capability 边界；当前 gate 为 `post-P8 planning accepted`，下一 gate 为 `P9-S1 analyze product contract plan/review`。
  - P9-S1 analyze product contract plan/review 已接受，plan artifact=`docs/reviews/p9-s1-analyze-product-contract-plan-20260521.md`，controller judgment=`docs/reviews/p9-s1-plan-review-controller-judgment-20260521.md`，re-review artifacts=`docs/reviews/p9-s1-plan-rereview-mimo-20260521.md`,`docs/reviews/p9-s1-plan-rereview-ds-20260521.md`。计划裁决为：默认 `analyze` 仅暴露普通用户最小输入，developer-only 参数必须经 `--dev-override` 进入 nested override；最终判断在 Fund Capability 派生，renderer/audit/service 只 import 单一定义点；quality gate block/not_run 由 Service 状态机在派生前处理。当前 gate 为 `P9-S1 implementation`，下一 gate 为 `P9-S1 code review`。
  - P9-S1 implementation/code review 已接受，implementation commit=`2bacdb3`，implementation artifact=`docs/reviews/p9-s1-implementation-20260521.md`，controller judgment=`docs/reviews/p9-s1-code-review-controller-judgment-20260521.md`，review artifacts=`docs/reviews/p9-s1-code-review-mimo-20260521.md`,`docs/reviews/p9-s1-code-review-ds-20260521.md`。实现新增 Capability-owned final judgment policy、product 最小请求契约、nested developer override、Service quality gate 状态机、renderer/audit selected/derived/source 契约和 R2 冲突审计；当前验证 full suite `365 passed`、ruff passed、diff check passed；当前 gate 为 `P9-S1 accepted`，下一 gate 为 `post-P9-S1 follow-up planning`。
  - Post-P9-S1 follow-up planning 已接受，artifact=`docs/reviews/post-p9-s1-follow-up-planning-20260521.md`。P9-S1 让 product mode 更严格依赖 quality gate fail-closed，而当前 golden answer 覆盖集中在 `004393`，默认精选池更广；下一优先级裁决为 `P9-S2 quality gate / golden coverage calibration plan/review`，目标是校准 product 默认 quality gate 与 golden coverage 的可用性边界，不放松 `--dev-override` 隔离。
  - P9-S2 quality gate / golden coverage calibration plan/review 已接受，plan artifact=`docs/reviews/p9-s2-quality-gate-golden-coverage-plan-20260521.md`，controller judgment=`docs/reviews/p9-s2-plan-review-controller-judgment-20260521.md`，review artifacts=`docs/reviews/p9-s2-plan-review-mimo-20260521.md`,`docs/reviews/p9-s2-plan-review-ds-20260521.md`,`docs/reviews/p9-s2-plan-rereview-mimo-20260521.md`,`docs/reviews/p9-s2-plan-rereview-ds-20260521.md`。计划裁决为：product mode 继续 `block` 且不暴露 `warn/off`；精选池成员缺 strict golden coverage 不等同 gate not-run，而以带 metadata 的 `FQ0/info` 暴露；explicit correctness mismatch 仍为 `FQ1/block`；当前 gate 为 `P9-S2 implementation`，下一 gate 为 `P9-S2 code review`。
  - P9-S2 implementation/code review 已接受，implementation commit=`ce603a0`，implementation artifact=`docs/reviews/p9-s2-implementation-20260521.md`，controller judgment=`docs/reviews/p9-s2-code-review-controller-judgment-20260521.md`。实现校准 quality gate 与 strict golden coverage 边界：`CorrectnessSummary.status` 保持 `available/unavailable`，新增 `coverage_scope` / `coverage_reason` / covered-missing fund codes / `coverage_required=false`；精选池成员缺 strict golden 覆盖或无可比字段输出带 metadata 的 `FQ0/info`，不再等同 `gate_not_run`；explicit correctness mismatch 仍为 `FQ1/block`；unknown unavailable coverage metadata fail closed；CLI 输出 fund-scoped `quality_gate_info` 且不改变退出码。当前验证 targeted `78 passed`、full suite `377 passed`、ruff passed、diff check passed。独立 Agent code review 未产出 durable artifact：AgentDS pane 卡在 compacting，AgentGLM 401，AgentCodex/AgentMiMo 参与实现不适合作为独立 reviewer；该 review limitation 已记录在 controller judgment。当前 gate 为 `P9-S2 accepted`，下一 gate 为 `post-P9-S2 follow-up planning`。
  - Post-P9-S2 follow-up planning 已接受，artifact=`docs/reviews/post-p9-s2-follow-up-planning-20260521.md`。P9-S1/P9-S2 已分别关闭 product analyze 最小输入/dev override 分离和 quality gate/golden coverage 校准；不再启动新的 P9 功能 slice。下一步为 `P9 aggregate readiness reconciliation`，随后进入 P9 aggregate deepreview；P9-S2 缺独立 Agent code review artifact 的限制必须作为 aggregate review 输入风险。
  - P9 aggregate readiness reconciliation 已接受，artifact=`docs/reviews/p9-aggregate-readiness-reconciliation-20260521.md`。P9 功能态已可进入 aggregate deepreview，但 reviewer availability 阻塞：AgentDS pane 在 P9-S2 review compacting 后未产出 artifact，AgentGLM 401，AgentCodex/AgentMiMo 参与 P9-S2 implementation 不适合作为独立 P9-S2 reviewer。下一步必须先恢复 AgentDS/AgentGLM 并取得两份独立 aggregate review，或由用户明确接受单 reviewer / controller-only 风险例外。
  - P9 aggregate deepreview 已接受，controller judgment=`docs/reviews/p9-aggregate-deepreview-controller-judgment-20260521.md`，review artifacts=`docs/reviews/p9-aggregate-deepreview-ds-20260521.md`,`docs/reviews/p9-aggregate-deepreview-mimo-20260521.md`。AgentDS 独立 aggregate review 为 `PASS`；AgentMiMo 补充 review 为 `PASS`，但因参与 P9-S2 implementation 仍记录 reviewer limitation。Controller 复核后拒绝 DS 的 README `coverage_scope` LOW finding（当前 README 已包含 `no_comparable_fields`），拒绝 MiMo 的 `AuditRuleCode` C2 info finding（真实 `AuditRuleCode` 已包含 `C2`）。P9 无阻断 finding，当前 gate 为 `P9 aggregate deepreview accepted`，下一 gate 为 `post-P9 follow-up planning`。
  - Post-P9 follow-up planning 已接受，artifact=`docs/reviews/post-p9-follow-up-planning-20260521.md`。P9 已关闭产品契约主风险；不继续启动新的产品功能 slice。下一阶段优先做 `P10 repo hygiene / release readiness`，首个 gate 为 `P10-S1 repo hygiene and release readiness plan/review`，规划范围包括 LICENSE、CI、`.gitignore` / artifact policy、默认路径配置策略和当前未跟踪文件处置；control doc hygiene 后置，RR-13 `016492` 重复保持 human-owned。
  - P10-S1 repo hygiene and release readiness plan/review 已接受，plan artifact=`docs/reviews/p10-s1-repo-hygiene-release-readiness-plan-20260521.md`，controller judgment=`docs/reviews/p10-s1-plan-review-controller-judgment-20260521.md`，review artifacts=`docs/reviews/p10-s1-plan-review-ds-20260521.md`,`docs/reviews/p10-s1-plan-review-mimo-20260521.md`。计划裁决为：只做仓库级发布就绪，不改变基金分析行为；新增 MIT LICENSE/CI/`.gitignore` 策略、静态 `fund_agent.config.paths` 默认路径、路径迁移守卫测试和 README 同步；`.docx` 源审计文件保持本地忽略，`docs/reviews/code-review-p8-s3-ds-20260521.md` 作为 durable review artifact 纳入。MIT holder 已由用户确认为 `bill20232033cc`。
  - P10-S1 implementation/code review 已接受，implementation artifact=`docs/reviews/p10-s1-implementation-20260521.md`，controller judgment=`docs/reviews/p10-s1-code-review-controller-judgment-20260521.md`，review artifacts=`docs/reviews/p10-s1-code-review-mimo-20260521.md`,`docs/reviews/p10-s1-code-review-glm-20260521.md`。实现新增 MIT LICENSE、GitHub Actions CI、窄口径 `.gitignore`、静态 `fund_agent.config.paths`、默认路径别名迁移、repo hygiene/path guard tests 和 README 同步；`golden-build` 默认输入修正为人工审核后的 reviewed Markdown。当前验证 full suite `388 passed`、ruff passed、diff check passed、`uv lock --check` passed；当前 gate 为 `P10-S1 code review accepted`，下一 gate 为 `P10 aggregate readiness reconciliation`。
  - P10 aggregate readiness reconciliation 已接受，artifact=`docs/reviews/p10-aggregate-readiness-reconciliation-20260521.md`。P10-S1 可进入 aggregate deepreview；`docs/repo-audit-20260521.md` 建议已逐条裁决，`fund_agent/fund/tools/` 空目录、repo-audit artifact inclusion、reviews 目录体量、RR-13 duplicate `016492` 均有后续 owner；当前 gate 为 `P10 aggregate readiness accepted`，下一 gate 为 `P10 aggregate deepreview`。
  - P10 aggregate deepreview 已接受，controller judgment=`docs/reviews/p10-aggregate-deepreview-controller-judgment-20260521.md`，review artifacts=`docs/reviews/p10-aggregate-deepreview-mimo-20260521.md`,`docs/reviews/p10-aggregate-deepreview-glm-20260521.md`。MiMo/GLM 均 PASS，无阻断 finding；确认 P10 release-readiness diff 未改变 `fund-analysis analyze`、quality gate、renderer、audit 或 Fund Capability 规则；残余风险均有 owner。当前 gate 为 `P10 aggregate deepreview accepted`，下一 gate 为 `ready-to-open-draft-PR reconciliation`。
  - P10 acceptance / ready-to-open-draft-PR reconciliation 已接受，artifact=`docs/reviews/p10-acceptance-ready-to-open-draft-pr-reconciliation-20260521.md`。PR inclusion/exclusion set 已明确；`docs/repo-audit-20260521.md` 和本地 `.docx` 审计输入排除，P10 release-readiness 代码、文档和 review artifacts 纳入；accepted local commit=`e9b622d`；当前 gate 为 `ready-to-open-draft-PR`，下一 gate 为 `draft PR gate（需用户授权）`。
  - P10 draft PR gate 已接受，artifact=`docs/reviews/p10-draft-pr-gate-reconciliation-20260521.md`。Draft PR #6 已创建：`https://github.com/bill20232033cc/fund-agent/pull/6`，branch=`p10-release-readiness`，head=`eb43dc3`；GitHub state=`OPEN`、draft=`true`、mergeable=`MERGEABLE`，Actions run `26234941272` pass；PR-level reviews `docs/reviews/pr-6-review-mimo-20260521.md` 和 `docs/reviews/pr-6-review-glm-20260521.md` 均无阻断 finding。初始 CI dev override 输出不稳定已由 `eb43dc3` 修复；`docs/repo-audit-20260521.md` 继续排除。当前 gate 为 `draft-PR-pass`，下一 gate 为 `merge gate（需用户额外授权）`。
  - P10 merge gate 已接受，artifact=`docs/reviews/p10-merge-gate-reconciliation-20260521.md`。PR #6 已 squash merge 到 `main`：`https://github.com/bill20232033cc/fund-agent/pull/6`；merge commit=`acc692c7e84c855398de86497b0d05f30b6f5ca5`，mergedAt=`2026-05-21T15:39:33Z`；本地 `main` 已对齐 `origin/main`。因远端 squash merge 与本地 pre-squash 线性历史分叉，controller 先保留备份分支 `backup/p10-pre-squash-main` 指向 `469a268`，再将本地 `main` 对齐到 `origin/main`。当前 gate 为 `P10 merged`，下一 gate 为 `post-P10 follow-up planning`。
  - Post-P10 follow-up planning 已接受，artifact=`docs/reviews/post-p10-follow-up-planning-20260521.md`。P10 已关闭 repo release-readiness 风险；下一阶段不继续扩产品功能，优先进入 `P11 control doc hygiene / recovery ergonomics`，目标是降低 phaseflow resume / handoff 成本并保留全部 gate 证据。RR-13 duplicate `016492` 继续 human-owned，`docs/repo-audit-20260521.md` 继续本地排除，`fund_agent/fund/tools/` 空目录 concerns 不启动代码 phase，因 design truth 已声明当前无 Fund tool runtime。当前 gate 为 `post-P10 follow-up planning accepted`，下一 gate 为 `P11-S1 control doc hygiene and recovery plan/review`。
  - P11-S1 control doc hygiene and recovery plan/review 已接受，plan artifact=`docs/reviews/p11-s1-control-doc-hygiene-recovery-plan-20260521.md`，controller judgment=`docs/reviews/p11-s1-plan-review-controller-judgment-20260521.md`，review artifacts=`docs/reviews/p11-s1-plan-review-mimo-20260521.md`,`docs/reviews/p11-s1-plan-review-glm-20260521.md`。MiMo/GLM 初审均为 `PASS_WITH_FINDINGS`，targeted re-review 均 `PASS`；计划接受 same-file control doc hygiene：Startup Packet + Active Gate Ledger <= 80 行、phase-prefixed unique archive anchors、artifact existence check 作为一次性 implementation acceptance gate、保留所有 artifact/commit/PR/validation/residual owner 证据。当前 gate 为 `P11-S1 plan accepted`，下一 gate 为 `P11-S1 implementation`。
  - Agent routing 补充：Procodex / AgentCodex 为 planning / implementation 首选；如遇网络或环境问题，AgentMiMo 可作为替补。但 MiMo 若参与某 slice 的 planning / implementation，则不得担任同 slice 独立 reviewer，应改用 AgentDS + AgentGLM。
  - P0 维持 `done`。历史上曾验证 `dayu` 依赖可导入；2026-05-21 架构裁决改为不保留外部 Dayu 生产依赖，相关 Host/Engine/tool-loop 能力如后续需要必须在项目内化实现。当前 `fund-agent` 处于 editable install，`fund-analysis --help` 可用，样本基金 `110011` 年报可下载，`pdfplumber` 可提取全文文本和表格。
  - P1 已完成并通过 aggregate review。
  - P2 已完成并通过 aggregate deepreview。
  - P3 已完成并合入 `main`。
  - P4 已完成并通过 PR 3 合入 `main`。本 phase 建立精选基金池真实年报提取质量闭环；`004393` 类型误判已修复为 `active_fund`，5 个高影响 extractor 缺口已由 snapshot/score 证明改善，P4-S4 已落地 golden answer 标注前链路与只消费 `score.json` 的质量 gate 骨架；P4 aggregate deepreview 的 per-fund blocking finding 已修复并通过 MiMo/GLM re-review；correctness golden answer 已补全并生成 strict JSON，P4-R10 最小 correctness 自动比对已实现并通过 MiMo/GLM code review；P4 final aggregate deepreview、PR inclusion set、PR-level review 均已接受；PR 3 squash merge commit=`7596c5ece4894166d5479ee764fc8641a23cfc0d`，mergedAt=`2026-05-19T18:51:24Z`。
  - Post-P4 follow-up planning 已接受，artifact=`docs/reviews/post-p4-follow-up-planning-20260520.md`。P5 第一优先级裁决为 `P5-S1 quality gate integration`：把 P4 已建立的 quality gate 接入 `fund-analysis analyze` 主链路，避免用户正常报告入口静默绕过低质量输入阻断。
  - P5-S1 quality gate integration plan 已通过 controller review/fix/re-review，plan artifact=`docs/reviews/p5-s1-quality-gate-integration-plan-20260520.md`，review artifact=`docs/reviews/p5-s1-plan-review-controller-20260520.md`，re-review artifact=`docs/reviews/p5-s1-plan-rereview-controller-20260520.md`。计划裁决为：在 Service 层把 quality gate 作为输入质量预检接入 `analyze`，复用已抽取的 `StructuredFundDataBundle` 生成 score/gate，不在 CLI 层串跑完整 snapshot 命令，不把 quality gate 合并进程序审计结果；block 路径必须使用结构化 `QualityGateBlockedError`，默认质量产物目录必须避免覆盖上一轮自动运行。
  - P5-S1 implementation 已完成，artifact=`docs/reviews/p5-s1-implementation-20260520.md`。实现新增 Capability 层 bundle-to-gate adapter，`analyze` Service 显式接入 quality gate，CLI 支持 `--quality-gate-policy/source-csv/output-dir/run-id/golden-answer-path`；当前验证 targeted `19 passed`、full suite `179 passed`、ruff passed、diff check passed。
  - P5-S1 controller code review 已通过 after fix，artifact=`docs/reviews/code-review-20260520-0350.md`。已修复 adapter 复用 `run_extraction_score()` 导致单基金合法 CSV 被 minimal golden set 前置条件误伤的问题；当前验证 related `26 passed`、full suite `179 passed`、ruff passed、diff check passed。
  - P5-S1 acceptance reconciliation 已接受，artifact=`docs/reviews/p5-s1-acceptance-reconciliation-20260520.md`。RR-15 / P4-R8 已关闭：P4 quality gate 已通过 `analyze` Service 主链路显式接入，CLI 和 Service 均支持 `off/warn/block` 策略与结构化阻断结果；下一 gate 为 `P5-S2 quality gate rules plan/review`。
  - P5-S2 quality gate rules plan 已 drafted，artifact=`docs/reviews/p5-s2-quality-gate-rules-plan-20260520.md`。计划裁决输入为 `score.json` 新增 `fund_quality`，在 Capability 层补齐 FQ1 App 类别冲突、FQ4 snapshot 缺失率、FQ5 preferred_lens mismatch；下一 gate 为 `P5-S2 plan review`。
  - P5-S2 controller plan review 已完成并修订 plan，review artifact=`docs/reviews/p5-s2-plan-review-controller-20260520.md`。已补充 `fund_quality` 基金级字段一致性检查、FQ5 首版 `preferred_lens_resolvability` 定义、`QualityGateIssue` metadata schema；下一 gate 为 `P5-S2 plan re-review`。
  - P5-S2 plan re-review 已通过，artifact=`docs/reviews/p5-s2-plan-rereview-controller-20260520.md`。3 个 plan finding 均关闭；下一 gate 为 `P5-S2 implementation`。
  - P5-S2 implementation 已完成，artifact=`docs/reviews/p5-s2-implementation-20260520.md`。实现新增 `score.json.fund_quality`、FQ1 App 类别冲突、FQ4 snapshot 缺失率、FQ5 preferred_lens resolvability 与结构化 issue metadata；当前验证 targeted `36 passed`、full suite `184 passed`、ruff passed、diff check passed；下一 gate 为 `P5-S2 code review`。
  - P5-S2 controller code review 已通过 after fix，artifact=`docs/reviews/code-review-p5-s2-20260520.md`。已修复 FQ5 派生路径没有随 App 类别冲突变成 mismatch 的问题；当前验证 targeted `37 passed`、ruff passed、diff check passed。
  - P5-S2 acceptance reconciliation 已接受，artifact=`docs/reviews/p5-s2-acceptance-reconciliation-20260520.md`。P4-R9 已关闭：FQ1 App 类别冲突、FQ4 snapshot 缺失率、FQ5 preferred_lens resolvability 均已接入 quality gate；当前验证 full suite `185 passed`、ruff passed、diff check passed；下一 gate 为 `P5-S3 snapshot sub-field exposure plan/review`。
  - P5-S3 snapshot sub-field exposure plan 已 drafted，artifact=`docs/reviews/p5-s3-snapshot-sub-field-exposure-plan-20260520.md`。计划通过 snapshot `comparable_values` 白名单扩大 correctness denominator，首版只覆盖结构化稳定 P0 子字段；下一 gate 为 `P5-S3 plan review`。
  - P5-S3 controller plan review 已完成并修订 plan，review artifact=`docs/reviews/p5-s3-plan-review-controller-20260520.md`。已明确只有白名单字段/子字段的明确缺失才能 mismatch，并补充 `benchmark_name` 从 `benchmark_text` 的字段内 alias 策略；下一 gate 为 `P5-S3 plan re-review`。
  - P5-S3 plan re-review 已通过，artifact=`docs/reviews/p5-s3-plan-rereview-controller-20260520.md`。2 个 plan finding 均关闭；下一 gate 为 `P5-S3 implementation`。
  - P5-S3 implementation 已完成，artifact=`docs/reviews/p5-s3-implementation-20260520.md`。实现新增 snapshot `comparable_values` 白名单子字段、correctness 索引扩展、`benchmark_name` 字段内 alias、旧 snapshot 分类兼容和白名单缺失语义；当前验证 targeted `43 passed`、full suite `187 passed`、ruff passed、diff check passed；下一 gate 为 `P5-S3 code review`。
  - P5-S3 controller code review 已通过，artifact=`docs/reviews/code-review-p5-s3-20260520.md`。未发现 blocking finding；P5-S3 按计划扩大 correctness denominator，但 RR-16 只部分关闭，真实分母仍依赖 extractor 覆盖和 strict golden answer 内容；下一 gate 为 `P5-S4 snapshot failure accounting plan/review`。
  - P5-S4 snapshot failure accounting plan 已 drafted 并通过 controller review/rereview，plan artifact=`docs/reviews/p5-s4-snapshot-failure-accounting-plan-20260520.md`，review artifact=`docs/reviews/p5-s4-plan-review-controller-20260520.md`，re-review artifact=`docs/reviews/p5-s4-plan-rereview-controller-20260520.md`。计划裁决为：`run_extraction_score(...)` 显式接收 `errors_path` 并解析 `SnapshotErrorRecord`，`write_extraction_score_records(...)` 只接结构化 `failed_funds`，quality gate 对 `score.json.failed_funds` 触发 FQ6 block；下一 gate 为 `P5-S4 implementation`。
  - P5-S4 implementation 已完成，artifact=`docs/reviews/p5-s4-implementation-20260520.md`。实现新增 `FailedFundRow`、`load_snapshot_error_records(...)`、`score.json.failed_funds`、`extraction-score --errors-path` 和 quality gate `FQ6/block`；当前验证 targeted `36 passed`、full suite `191 passed`、ruff passed、diff check passed；下一 gate 为 `P5-S4 code review`。
  - P5-S4 controller code review 已通过，artifact=`docs/reviews/code-review-p5-s4-20260520.md`。未发现 blocking finding；完全失败基金 accounting 已通过显式 `--errors-path` 进入 `score.json.failed_funds` 并由 FQ6 阻断；下一 gate 为 `P5-S5 share_change hardening plan/review`。
  - P5-S5 share_change hardening plan 已 drafted 并通过 controller review/rereview，plan artifact=`docs/reviews/p5-s5-share-change-hardening-plan-20260520.md`，review artifact=`docs/reviews/p5-s5-plan-review-controller-20260520.md`，re-review artifact=`docs/reviews/p5-s5-plan-rereview-controller-20260520.md`。计划裁决为：拒绝 fund_code 尾号推断 A/C 类，只允许单值列、表头精确基金代码、严格 A 类 fallback；歧义多列表必须 fail closed；下一 gate 为 `P5-S5 implementation`。
  - P5-S5 implementation 已完成，artifact=`docs/reviews/p5-s5-implementation-20260520.md`。实现新增显式份额列选择、稳定 `share_class_selection_reason` metadata、总份额列处理和歧义多列表 missing；controller code review 发现并修复 A 类 fallback 忽略其他代码表头的问题，review artifact=`docs/reviews/code-review-p5-s5-20260520.md`；当前验证 targeted `31 passed`、full suite `195 passed`、ruff passed、diff check passed；下一 gate 为 `P5-S6 user/App source reconciliation`。
  - P5-S6 user/App source reconciliation 已形成 artifact=`docs/reviews/p5-s6-user-app-source-reconciliation-20260520.md`。当前事实为 `docs/code_20260519.csv` 第 26 行和第 35 行均使用 `016492`，但对应不同基金名称；该问题需要用户/App 源确认，controller 不自动改 CSV；RR-13 保持 human-owned，不阻断 P5-S7 plan。
  - P5-S7 post-MVP infra validation plan 已 drafted 并通过 controller review/rereview，plan artifact=`docs/reviews/p5-s7-post-mvp-infra-validation-plan-20260520.md`，review artifact=`docs/reviews/p5-s7-plan-review-controller-20260520.md`，re-review artifact=`docs/reviews/p5-s7-plan-rereview-controller-20260520.md`。计划裁决为：温度计只做 read-only Service/CLI 查询能力，不自动映射 `valuation_state`；真实 PDF/network smoke 保持显式 `--run`，并用 `--quality-gate-policy warn` 避免质量 gate 掩盖基础设施信号；下一 gate 为 `P5-S7 implementation`。
  - P5-S7 implementation 已完成并通过 controller code review，implementation artifact=`docs/reviews/p5-s7-implementation-20260520.md`，review artifact=`docs/reviews/code-review-p5-s7-20260520.md`。实现新增 `ThermometerService`、`fund-analysis thermometer` plain/JSON 输出、unavailable exit 0、smoke 显式 `--quality-gate-policy warn` 和 README/tests 同步；当前验证 targeted `32 passed`、full suite `200 passed`、ruff passed、diff check passed；下一 gate 为 `P5 aggregate readiness reconciliation`。
  - P5 aggregate readiness reconciliation 已接受，artifact=`docs/reviews/p5-aggregate-readiness-reconciliation-20260520.md`。P5-S1/S2/S3/S4/S5/S7 均已 accepted，P5-S6 duplicate `016492` 保持 human-owned 且不阻断 aggregate deepreview；当前验证 full suite `200 passed`、ruff passed、diff check passed；下一 gate 为 `P5 aggregate deepreview`。
  - P5 aggregate deepreview 已完成并修复所有 accepted findings，controller judgment artifact=`docs/reviews/p5-aggregate-deepreview-controller-judgment-20260520.md`。接受并修复 5 个问题：block 策略 gate not-run 成功出报告、显式 golden 路径 typo 静默降级、present parent 下白名单子字段缺失变 unavailable、share_change A 类 fallback 误伤非 A 份额、smoke PASS 隐藏 gate block；当前验证 full suite `206 passed`、ruff passed、diff check passed；下一 gate 为 `P5 aggregate re-review / acceptance`。
  - P5 aggregate targeted re-review 已通过，acceptance artifact=`docs/reviews/p5-aggregate-rereview-controller-acceptance-20260520.md`。AgentCodex/AgentDS 均确认 accepted findings 已关闭；当前验证 targeted `53 passed`、full suite `206 passed`、ruff passed、diff check passed；下一 gate 为 `P5 acceptance / ready-to-open-draft-PR reconciliation`。
  - P5 acceptance / ready-to-open-draft-PR reconciliation 已接受，artifact=`docs/reviews/p5-acceptance-ready-to-open-draft-pr-reconciliation-20260520.md`。P5 inclusion set 已明确，旧 review artifacts、runtime reports、launchd 和本地 helper scripts 明确排除。
  - P5 draft PR gate 已接受，artifact=`docs/reviews/p5-draft-pr-gate-reconciliation-20260520.md`，PR-level review artifact=`docs/reviews/pr-4-review-20260520-0625.md`。
  - P5 已通过 PR 4 合入 `main`：`https://github.com/bill20232033cc/fund-agent/pull/4`；squash merge commit=`d33b901fd1bee9f85206df461cc6419a813bcbae`，mergedAt=`2026-05-19T22:51:32Z`。当前 gate 为 `P5 merged`，下一 gate 为 `post-P5 follow-up planning`。
  - Post-P5 follow-up planning 已接受，artifact=`docs/reviews/post-p5-follow-up-planning-20260520.md`。controller 裁决下一阶段第一优先级为 P6-S1 template contract manifest：把 `docs/fund-analysis-template-draft.md` 中的 `CHAPTER_CONTRACT` / `ITEM_RULE` 推进为 Capability 层可消费的机器契约；当前 gate 为 `post-P5 follow-up planning accepted`，下一 gate 为 `P6-S1 template contract manifest plan/review`。
  - P6-S1 template contract manifest plan 已 drafted 并通过 controller review/rereview，plan artifact=`docs/reviews/p6-s1-template-contract-manifest-plan-20260520.md`，review artifact=`docs/reviews/p6-s1-plan-review-controller-20260520.md`，re-review artifact=`docs/reviews/p6-s1-plan-rereview-controller-20260520.md`。计划裁决为首版在 Capability 层维护 typed Python manifest，不在运行时解析 Markdown 注释，且 production code 不依赖 renderer 私有 `_CHAPTER_TITLES`；下一 gate 为 `P6-S1 implementation`。
  - P6-S1 template contract manifest implementation 已完成并通过 MiMo/GLM code review，controller 裁决=`docs/reviews/p6-s1-code-review-controller-judgment-20260520.md`，review artifacts=`docs/reviews/code-review-20260520-125906.md`,`docs/reviews/code-review-20260520-130008.md`。实现新增 Capability 层 typed `CHAPTER_CONTRACT` manifest、公开 accessor、preferred_lens 解析和 fail-closed validation；已修复 lens key / `fund_type` mismatch 测试覆盖缺口；当前验证 targeted `7 passed`、full suite `213 passed`、ruff passed、diff check passed；下一 gate 为 `P6-S2 plan/review`。
  - P6-S2 renderer contract alignment plan 已 drafted 并通过 controller review/rereview，plan artifact=`docs/reviews/p6-s2-renderer-contract-alignment-plan-20260520.md`，review artifact=`docs/reviews/p6-s2-plan-review-controller-20260520.md`，re-review artifact=`docs/reviews/p6-s2-plan-rereview-controller-20260520.md`。计划裁决为让 renderer 使用 P6-S1 manifest 标题真源，新增 `RenderedChapterBlock` 与 Markdown chapter split helper，保持报告 Markdown、audit input、Service/UI 行为不变；下一 gate 为 `P6-S2 implementation`。
  - P6-S2 renderer contract alignment implementation 已完成并通过 MiMo/GLM code review，controller 裁决=`docs/reviews/p6-s2-code-review-controller-judgment-20260520.md`，review artifacts=`docs/reviews/code-review-20260520-134023.md`,`docs/reviews/code-review-20260520-134053.md`。实现让 renderer 标题来源收口到 `CHAPTER_CONTRACT` manifest，新增 `RenderedChapterBlock`、`get_template_chapter_heading(...)`、`split_rendered_chapter_blocks(...)` 和 `TemplateRenderResult.chapter_blocks`；已补混入非法一级标题的 splitter fail-closed 测试；当前验证 targeted `29 passed`、full suite `221 passed`、ruff passed、diff check passed；下一 gate 为 `P6-S3 plan/review`。
  - `P3-S1 CLI 入口封装` 已完成，通过 Typer CLI 和 Service 层输出单只基金 8 章 Markdown 报告；下一 gate 为 `P3-S2 implementation + review`。
  - `P3-S2 温度计数据爬取` 已完成并通过 GLM/MiMo code review；当前实现范围仅限 Capability data adapter，不接入 CLI/Service。
  - `P3-S3 端到端整合测试` 已完成实现与 GLM/MiMo/controller code review：新增 3 只样本基金 CLI 端到端矩阵，闭合真实 `§2` 表格字段抽取、parsed report 低质量缓存门槛和模板 `benchmark_text` 契约错配。
  - `P3-S4 程序审计集成` 已完成实现与 controller code review：P3 CLI 端到端矩阵现在记录真实 Service 返回值，并断言 P1/P2/P3/L1/R1/R2 全部程序审计规则执行通过；下一 gate 为 `P3-S5 implementation + review`。
  - `P3-S5 证据锚点集成` 已完成实现与 controller code review：P3 CLI 端到端矩阵现在逐份报告断言 8 章正文证据行、附录年报章节/表格/行定位和无缺证占位；下一 gate 为 `P3-S6 implementation + review`。
  - `P3-S6 编写 README.md` 已完成实现与 controller code review：根 README 已按当前 CLI 成功路径更新为用户手册，并移除过期的端到端矩阵未实现表述；下一 gate 为 `P3-S7 implementation + review`。
  - `P3-S7 编写单元测试` 已完成实现与 controller code review：dev 依赖和测试手册新增覆盖率 gate，当前 `fund_agent` 总覆盖率 90.07%，超过 50% 目标；下一 gate 为 `P3-S8 implementation + review`。
  - `P3-S8 性能优化` 已完成实现与 controller code review：Service 层新增不含 PDF 下载的单只基金分析性能 gate，验证完整编排低于 30 秒。
  - `P3 aggregate deepreview` 已通过 controller deepreview：未发现 blocking finding；当前验证 `27 passed`、覆盖率矩阵 `116 passed / 90.07%`、`git diff --check` 通过。
  - PR 2 已完成 PR-level deepreview、mark ready 和 merge：`https://github.com/bill20232033cc/fund-agent/pull/2`；merge commit=`0be218f28ea7d26c7ad1e55963ca907217f5dede`，mergedAt=`2026-05-18T15:30:34Z`。
  - `P2-S1` 至 `P2-S8` 已收口为 accepted baseline commit `a6b1516`。收口范围仅包含 P2 analysis/audit 实现、测试、README 同步与 review artifact；本地运行辅助文件 `launchd/`、`scripts/` 和旧 P1 review artifact 未纳入该基线。
  - `P1-S1 文档访问契约收口` 已完成：对外唯一仓库入口收口为 `FundDocumentRepository.load_annual_report(...) -> ParsedAnnualReport`，公共契约已迁入 `fund_agent/fund/documents/*`，`fund_agent/fund/pdf/*` 降为仓库内部 helper / adapter。
  - `P1-S2 章节定位修复与 §3 冻结` 已完成：
    - `§3` root cause 已直接关闭，不是基金代码特判
    - 章节规则已迁出到 `fund_agent/fund/pdf/section_catalog.py`
    - 目录过滤已从单一 `"..."` 升级为可复用规则表
    - `110011/2024` 的正文 `§3` 已由 fixture + test 稳定覆盖
  - `P1-S3 两级缓存与仓库内解析物化` 已完成：
    - raw PDF 元信息缓存与 parsed report 物化缓存均已落在 `documents` 层内部
    - repository 已优先命中缓存，避免重复下载 / 重复全文解析
    - `force_refresh=True` 已正确穿透 parsed report 与已记录的 PDF 路径
    - 本 slice 未创建 `structured_data` 表，也未冻结其 schema
  - `P1-S4 基础画像与基金类型识别` 已完成：
    - `fund_agent/fund/fund_type.py` 已承载稳定的基金类型识别输出 `classified_fund_type` / `classification_basis`
    - `fund_agent/fund/extractors/profile.py` 已落地 `basic_identity`、`product_profile`、`benchmark`、`fee_schedule`
    - 基金类型识别已显式先于通用字段构造执行，并由测试锁定
    - 费率、基准、规模、经理信息均已带 `EvidenceAnchor`
  - `P1-S5 §3 表现提取与投资者收益 fallback` 已完成：
    - `fund_agent/fund/extractors/performance.py` 已落地 `nav_benchmark_performance` 与 `investor_return`
    - `investor_return` 已稳定区分 `direct / estimated / missing`
    - `§3` 直接披露与估算披露命中均带 `EvidenceAnchor`
    - 未披露路径不再静默返回空字符串，而是显式标记 `missing`
    - `nav_benchmark_performance` 在部分命中时不再伪装成完整 `direct`
  - `P1-S6 管理人文本、换手率、利益一致性与持有人结构` 已完成：
    - `fund_agent/fund/extractors/manager_ownership.py` 已落地 `manager_strategy_text`、`turnover_rate`、`manager_alignment`、`holder_structure`
    - `§4/§8/§9` 命中字段均带 `EvidenceAnchor`
    - `manager_alignment` 仅输出原始披露，未引入利益一致性判断
    - 未披露路径显式标记 `missing`
  - `P1-S7 持仓快照与份额变动` 已完成：
    - `fund_agent/fund/extractors/holdings_share_change.py` 已落地 `holdings_snapshot` 与 `share_change`
    - 前十大重仓与份额变动可结构化输出
    - 行业分布未披露时显式标记 `missing`
    - 表格命中路径均带页码、表 ID 和行定位
  - `P1-S8 façade 集成、净值数据适配器与 P1 验收矩阵` 已完成：
    - `fund_agent/fund/data_extractor.py` 已落地 `FundDataExtractor` 与 `StructuredFundDataBundle`
    - `fund_agent/fund/data/nav_data.py` 已落地 `FundNavDataAdapter` 与 `nav_cache`
    - 3 只样本基金 12 项矩阵达到 `36/36`
    - P1 全量测试当前通过
  - `P2-S1 R=A+B-C 计算模块` 已完成：
    - `fund_agent/fund/analysis/r_abc.py` 已落地 `RabcInput`、`RabcAttribution`、`calculate_r_abc(...)`、`calculate_r_abc_series(...)` 与 `calculate_r_abc_from_bundle(...)`
    - 计算公式按 `docs/design.md` 第 4.1 节实现：`B=业绩比较基准收益率×股票仓位`，`A=R-B`，`C=管理费+托管费+换手率×0.3%`，`净超额=A-C`
    - 当前只消费 P1 `StructuredFundDataBundle`，不直接读取 PDF、文档仓库或文件系统
    - P1 尚未稳定抽取股票仓位，当前要求调用方显式传入 `equity_position`；缺失时返回 `missing`，不静默假设
    - 单元测试已覆盖手工公式闭合、P1 字段解析、证据锚点传递、关键字段缺失和子字段缺失
  - `P2-S2 超额收益性质判断` 已完成：
    - `fund_agent/fund/analysis/alpha_judge.py` 已落地 `AlphaObservation`、`AlphaJudgmentRule`、`AlphaJudgment`、`judge_alpha_nature(...)` 与 `observations_from_attributions(...)`
    - 默认规则按 MVP 规则引擎实现：多年度为正、牛熊环境都为正、来源可解释
    - 输出 `structural / partial_structural / cyclical / not_applicable / insufficient_data`
    - 市场环境与来源解释强度必须由调用方显式提供，模块不从收益结果中反推
    - 单元测试已覆盖结构性、部分结构性、阶段性、不适用、样本不足和缺少显式环境输入
  - `P2-S3 言行一致性检验` 已完成：
    - `fund_agent/fund/analysis/consistency_check.py` 已落地 `ConsistencyRule`、`ConsistencyDimensionResult`、`ConsistencyCheckResult` 与 `check_consistency(...)`
    - 已输出投资风格、行业偏好、仓位管理、换手水平 4 维度信号
    - 实际持仓风格和股票仓位必须由调用方显式传入，缺失时返回 `insufficient_data`
    - 行业偏好只在 §4 行业宣称和 §8 行业分布都存在时判断
    - `fund_agent/fund/analysis/_ratios.py` 已收口 P2 分析模块内重复比例解析逻辑
    - 单元测试已覆盖 4 维度一致、风格/行业不一致、缺少显式实际证据、高换手冲突和行业分布缺失
  - `P2-S4 投资者获得感分析` 已完成：
    - `fund_agent/fund/analysis/investor_return.py` 已落地 `BehaviorGapResult`、`FundFlowResult`、`InvestorExperienceResult`、`analyze_investor_experience(...)`、`calculate_behavior_gap(...)` 与 `judge_fund_flow(...)`
    - 行为损益按 `投资者实际收益率 - 基金产品收益率` 计算
    - 资金流向基于 §10 份额净变动和产品收益方向输出 `chasing_performance / bottom_fishing / outflow / normal / missing`
    - 投资者收益率缺失时返回 `missing`，不在分析层静默估算
    - 单元测试已覆盖行为损益、投资者收益缺失、追涨/抄底资金流向、获得感负向和份额字段缺失
  - `P2-S5 否决项检查` 已完成：
    - `fund_agent/fund/analysis/risk_check.py` 已落地 `RiskCheckRule`、`RiskCheckItem`、`RiskCheckResult` 与 `run_risk_checks(...)`
    - 已执行 5 项否决检查：清盘风险、基金经理任期、严重风格漂移、费率远超同类、指数基金跟踪误差
    - 基金经理任期、同类费率中位数和跟踪误差必须由调用方显式提供，缺失时返回 `insufficient_data`
    - 单元测试已覆盖安全路径、5 项否决触发和显式输入缺失路径
  - `P2-S6 压力测试` 已完成：
    - `fund_agent/fund/analysis/risk_check.py` 已落地 `StressTestRule`、`StressScenarioResult`、`StressTestResult` 与 `run_stress_test(...)`
    - 固定模拟 `-20% / -40% / -60%` 三个场景
    - 按基金类型应用模板第 6 章 `preferred_lens` 压力阈值
    - 最大可承受亏损比例必须显式提供；缺失时只输出浮亏，不猜测用户承受能力
    - 单元测试已覆盖主动基金、债券基金、缺少承受能力、非法输入和自定义阈值配置
    - controller code review 已通过；MiMo/GLM 外部 review 因 Claude hook/思考状态卡住未产出 artifact，不能作为独立 review 依据
  - `P2-S7 检查清单引擎` 已完成：
    - `fund_agent/fund/analysis/checklist.py` 已落地 `ChecklistRule`、`ChecklistItem`、`ChecklistResult` 与 `run_checklist(...)`
    - 已输出 7 问题 `green / yellow / red / gray` 与 `pass / watch / block / insufficient_data`
    - 检查清单消费 R=A+B-C、§9 利益一致性披露、投资者获得感、言行一致性、否决项检查、估值状态和用户资金期限
    - 估值和资金期限必须由调用方显式提供；缺失时输出灰灯，不默认通过
    - 单元测试已覆盖全绿、红灯阻断、灰灯缺失、黄灯跟踪、资金年限阈值配置、异常否决项输入和 7 问题顺序
    - controller code review 已通过
  - `P2-S8 程序审计` 已完成：
    - `fund_agent/fund/audit/audit_programmatic.py` 已落地 `ProgrammaticAuditInput`、`AuditIssue`、`ProgrammaticAuditResult` 与 `run_programmatic_audit(...)`
    - 已执行 P1/P2/P3/L1/R1/R2 程序审计
    - P1/P2/P3 消费报告 Markdown，L1/R1/R2 消费结构化 P2 结果和显式最终判断
    - 缺少报告、R=A+B-C 结构化结果、检查清单或最终判断时返回失败，不把未执行规则伪装成通过
    - 单元测试已覆盖必需输入缺失、章节缺失、内容过短、证据缺失、R=A+B-C 不闭合、检查清单规则错误和最终判断冲突
    - controller code review 已通过
  - `P2-S9 模板渲染器` 已完成：
    - `fund_agent/fund/template/renderer.py` 已落地 `TemplateRenderInput`、`TemplateRenderResult`、`render_template_report(...)` 与 `build_programmatic_audit_input(...)`
    - 渲染器固定输出 `docs/design.md` 第 3.1 节 0-7 共 8 章 Markdown，并附带 `证据与出处`
    - 渲染器只消费 P1/P2 结构化结果与显式输入，不读取年报、PDF、缓存、文档仓库、UI、Service、Runtime 或 Engine
    - `TemplateRenderResult.audit_input` 可直接传给 `run_programmatic_audit(...)`，携带报告 Markdown、R=A+B-C 结果、检查清单和最终判断
    - 缺失数据显式渲染为“未披露”或“数据不足”
    - 最终判断限制为 `worth_holding / needs_attention / suggest_replace`，报告不输出买入、卖出、收益预测或仓位比例
    - code review 接受并修复了 `dict_values(...)` 可见输出、重复句号和 README 过期条目问题
    - 验证命令 `.venv/bin/python -m pytest tests/fund/template tests/fund/audit -q` 当前通过（`18 passed`），`.venv/bin/python -m pytest tests/fund/analysis -q` 当前通过（`40 passed`）
  - `P2-S10 证据锚点标注` 已完成：
    - 正文证据行已按年报年份、章节和描述输出；非年报来源显式标注来源类型
    - 附录年报锚点按 `年报{年份}§{章节}表{编号}行{行号}` 输出
    - 表格、行定位、章节缺失时显式降级为 `未定位`，不静默丢失年份或章节
    - 页码作为附加位置元数据保留
    - 缺少章节证据时，正文和附录均显式输出数据不足
    - `ProgrammaticAuditInput` 兼容性保持不变
    - 验证命令 `.venv/bin/python -m pytest tests/fund/template tests/fund/audit -q` 当前通过（`23 passed`），`.venv/bin/python -m pytest tests/fund/analysis -q` 当前通过（`40 passed`）
- 下一 entry point：
  - 进入 `P5-S7 post-MVP infra validation plan/review`
  - `004393` 类型误判已在 P4-S3a 修复为 `active_fund`
  - `004393` 的 `nav_benchmark_performance`、`manager_strategy_text`、`manager_alignment`、`holder_structure`、`share_change` 已在 P4-S3b 修复并由 snapshot/score 验证
  - P4-S4 的 `golden-prefill`、`golden-build` 与 `quality-gate` 骨架已由 control-doc reconciliation 接受；per-fund score / quality gate fix 已通过 aggregate re-review；`reports/golden-answers/golden-answer-prefill-reviewed.md` 已补全并构建 `reports/golden-answers/golden-answer.json`；P4-R10 已把 correctness 自动比对接入 score / quality gate 并通过 code review；P4 final aggregate deepreview、PR scope hygiene、PR-level review 与 merge 均已接受
  - P5-S6 artifact 已形成，artifact=`docs/reviews/p5-s6-user-app-source-reconciliation-20260520.md`；`016492` 重复保持 human-owned，下一步进入 P5-S7 plan
- 当前 artifact：
  - plan: `docs/reviews/p1-plan-2026-05-17.md`
  - plan review: `docs/reviews/p1-plan-review-2026-05-17.md`
  - `P1-S1`:
    - baseline reconciliation: `docs/reviews/p1-s1-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s1-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s1-code-review-mimo-2026-05-17.md`
      - `docs/reviews/p1-s1-code-review-glm-2026-05-17.md`
      - controller judgment: `docs/reviews/p1-s1-code-review-controller-judgment-2026-05-17.md`
    - fix: `docs/reviews/p1-s1-fix-2026-05-17.md`
    - re-review:
      - `docs/reviews/p1-s1-rereview-mimo-2026-05-17.md`
      - `docs/reviews/p1-s1-rereview-glm-2026-05-17.md`
      - controller confirmation: `docs/reviews/p1-s1-rereview-controller-2026-05-17.md`
    - accepted slice commit: `e772dae`
  - `P1-S2`:
    - baseline reconciliation: `docs/reviews/p1-s2-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s2-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s2-code-review-mimo-2026-05-17.md`
      - `docs/reviews/p1-s2-code-review-glm-2026-05-17.md`
      - controller judgment: `docs/reviews/p1-s2-code-review-controller-judgment-2026-05-17.md`
    - accepted slice commit: `c3bd264`
  - `P1-S3`:
    - baseline reconciliation: `docs/reviews/p1-s3-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s3-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s3-code-review-mimo-2026-05-17.md`
      - `docs/reviews/p1-s3-code-review-glm-2026-05-17.md`
      - controller judgment: `docs/reviews/p1-s3-code-review-controller-judgment-2026-05-17.md`
    - accepted slice commit: `d92eef7`
  - `P1-S4`:
    - baseline reconciliation: `docs/reviews/p1-s4-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s4-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s4-code-review-mimo-2026-05-17.md`
      - `docs/reviews/p1-s4-code-review-glm-2026-05-17.md`
      - `docs/reviews/p1-s4-code-review-controller-judgment-2026-05-17.md`
    - fix: `docs/reviews/p1-s4-fix-2026-05-17.md`
    - re-review:
      - `docs/reviews/p1-s4-rereview-glm-2026-05-17.md`
      - `docs/reviews/p1-s4-rereview-controller-2026-05-17.md`
    - accepted slice commit: `22a1a7a`
  - `P1-S5`:
    - baseline reconciliation: `docs/reviews/p1-s5-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s5-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s5-code-review-mimo-2026-05-17.md`
      - `docs/reviews/p1-s5-code-review-glm-2026-05-17.md`
      - `docs/reviews/p1-s5-code-review-controller-judgment-2026-05-17.md`
    - fix: `docs/reviews/p1-s5-fix-2026-05-17.md`
    - re-review:
      - `docs/reviews/p1-s5-rereview-controller-2026-05-17.md`
    - accepted slice commit: `8102944`
  - `P1-S6`:
    - baseline reconciliation: `docs/reviews/p1-s6-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s6-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s6-code-review-controller-judgment-2026-05-17.md`
    - accepted slice commit: `18566f9`
  - `P1-S7`:
    - baseline reconciliation: `docs/reviews/p1-s7-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s7-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s7-code-review-controller-judgment-2026-05-17.md`
    - accepted slice commit: `3167754`
  - `P1-S8`:
    - baseline reconciliation: `docs/reviews/p1-s8-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s8-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s8-code-review-controller-judgment-2026-05-17.md`
    - accepted slice commit: `d398bc2`
  - `P1 aggregate review`: `docs/reviews/p1-aggregate-review-2026-05-17.md`
  - `P2-S1`:
    - implementation: `docs/reviews/p2-s1-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s1-code-review-controller-judgment-2026-05-17.md`
  - `P2-S2`:
    - implementation: `docs/reviews/p2-s2-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s2-code-review-controller-judgment-2026-05-17.md`
  - `P2-S3`:
    - implementation: `docs/reviews/p2-s3-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s3-code-review-controller-judgment-2026-05-17.md`
  - `P2-S4`:
    - implementation: `docs/reviews/p2-s4-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s4-code-review-controller-judgment-2026-05-17.md`
  - `P2-S5`:
    - implementation: `docs/reviews/p2-s5-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s5-code-review-controller-judgment-2026-05-17.md`
  - `P2-S6`:
    - implementation: `docs/reviews/p2-s6-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s6-code-review-controller-judgment-2026-05-17.md`
  - `P2-S7`:
    - implementation: `docs/reviews/p2-s7-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s7-code-review-controller-judgment-2026-05-17.md`
  - `P2-S8`:
    - implementation: `docs/reviews/p2-s8-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s8-code-review-controller-judgment-2026-05-18.md`
  - P2 baseline risk review: `docs/reviews/code-review-20260518-0547.md`
  - P2-S1 至 P2-S8 accepted baseline commit: `a6b1516`
  - `P2-S9`:
    - implementation: `docs/reviews/p2-s9-implementation-2026-05-18.md`
    - code review:
      - `docs/reviews/p2-s9-code-review-mimo-2026-05-18.md`
      - `docs/reviews/p2-s9-code-review-glm-2026-05-18.md`
      - controller judgment: `docs/reviews/p2-s9-code-review-controller-judgment-2026-05-18.md`
    - fix: `docs/reviews/p2-s9-fix-2026-05-18.md`
    - re-review:
      - `docs/reviews/p2-s9-rereview-glm-2026-05-18.md`
    - accepted slice commit: `bf64b0f`
  - `P2-S10`:
    - implementation: `docs/reviews/p2-s10-implementation-2026-05-18.md`
    - code review:
      - `docs/reviews/p2-s10-code-review-mimo-2026-05-18.md`
      - `docs/reviews/p2-s10-code-review-glm-2026-05-18.md`
      - controller judgment: `docs/reviews/p2-s10-code-review-controller-judgment-2026-05-18.md`
    - accepted slice commit: `2d041ae`
  - `P2 aggregate deepreview`:
    - review:
      - `docs/reviews/p2-aggregate-review-mimo-2026-05-18.md`
      - `docs/reviews/p2-aggregate-review-glm-2026-05-18.md`
      - controller judgment: `docs/reviews/p2-aggregate-review-controller-judgment-2026-05-18.md`
    - fix: `docs/reviews/p2-aggregate-fix-2026-05-18.md`
    - accepted deepreview commit: `07fe0d0`
  - `Draft PR #1`:
    - URL: `https://github.com/bill20232033cc/fund-agent/pull/1`
    - base: `main` (`a6b1516`)
    - head: `chore/reconcile-baseline`
    - PR review:
      - `docs/reviews/pr-1-review-glm-2026-05-18.md`
      - controller judgment: `docs/reviews/pr-1-review-controller-judgment-2026-05-18.md`
    - PR fix: `docs/reviews/pr-1-fix-2026-05-18.md`
    - PR re-review: `docs/reviews/pr-1-rereview-glm-2026-05-18.md`
    - accepted PR review commit: `8f5029c`
  - `P3-S1`:
    - implementation: `docs/reviews/p3-s1-implementation-2026-05-18.md`
    - code review:
      - `docs/reviews/p3-s1-code-review-glm-2026-05-18.md`
      - controller judgment: `docs/reviews/p3-s1-code-review-controller-judgment-2026-05-18.md`
    - fix: `docs/reviews/p3-s1-fix-2026-05-18.md`
    - re-review:
      - `docs/reviews/p3-s1-rereview-glm-2026-05-18.md`
    - accepted slice commit: `c5a240c`
  - `P3 Draft PR #2`:
    - URL: `https://github.com/bill20232033cc/fund-agent/pull/2`
    - base: `main`
    - head: `feat/p3-cli-integration`
    - PR-level deepreview: `docs/reviews/pr-2-review-20260518-2307.md`
    - PR review validation: `27 passed`，覆盖率矩阵 `116 passed / 90.07%`，`git diff --check main..HEAD` passed
    - merge commit: `0be218f28ea7d26c7ad1e55963ca907217f5dede`
    - mergedAt: `2026-05-18T15:30:34Z`

---

## 2. Phase 详细定义

### P0: 环境搭建与架构骨架

**目标**

完成开发环境搭建，建立四层架构骨架，验证数据提取可行性。

**进入条件**

- [x] 设计真源文档 `docs/design.md` 已冻结
- [x] 实施总控文档 `docs/implementation-control.md` 已创建
- [x] Python 3.11+ 可用

**退出条件**

- [x] 历史 P0 曾验证 `dayu-agent` 包可安装；2026-05-21 裁决为移除外部 Dayu 生产依赖，能力按需内化
- [x] 四层架构目录结构就位（ui/services/fund/config）
- [x] `pyproject.toml` 配置完成且 `pip install -e .` 无报错
- [x] 选定 3-5 只样本基金并记录分析基准
- [x] 能从巨潮资讯网下载至少 1 只样本基金的年报 PDF
- [x] 能用 pdfplumber 提取 PDF 文本和表格
- [x] `fund-analysis` CLI 命令可运行且输出帮助信息

**任务切片**

| Slice | 任务 | 验证方式 |
|-------|------|---------|
| P0-S1 | 历史验证 dayu-agent 依赖可用；后续裁决为不保留生产依赖 | 2026-05-21 dependency reconciliation 移除外部 Dayu 依赖 |
| P0-S2 | 创建项目骨架目录结构（ui/services/fund/config） | `ls fund_agent/` 输出符合 design.md |
| P0-S3 | 编写 `pyproject.toml`（pdfplumber/httpx/akshare/typer/rich 等生产依赖） | `pip install -e .` 无报错 |
| P0-S4 | 选定样本基金（从有知有行严选基金池） | 记录基金代码和手动分析结果 |
| P0-S5 | 实现 `fund/pdf/downloader.py` 基础版 | 能下载巨潮网年报 PDF |
| P0-S6 | 实现 `fund/pdf/parser.py` 基础版 | 能读取 PDF 文本和表格 |
| P0-S7 | 编写 CLI 入口（`fund-analysis` 命令） | `fund-analysis --help` 输出帮助信息 |

**验证要求**

- P0-S4：下载 3 只不同类型基金的年报 PDF，确认均可获取
- P0-S5：对 1 只基金年报执行 pdfplumber 提取，确认能读取 §2/§3/§4/§8/§9/§10 的文本

**风险与追踪**

| 风险 | 概率 | 缓解措施 | 追踪状态 |
|------|------|---------|---------|
| 巨潮网反爬 | 低 | 改用东方财富 akshare API + pdf.dfcfw.com | ✅ 已缓解：改用 akshare + eastmoney PDF |
| pdfplumber 对中文 PDF 支持差 | 中 | 备选 PyPDF2 + pdfminer.six | ✅ 已验证：中文提取正常，70K 字文本可提取 |

**当前实现裁决（2026-05-17）**

- 已验证 `fund-agent==0.1.0` 以 editable install 方式安装在当前虚拟环境中，`fund-analysis --help` 可直接运行。
- 已验证样本基金基线存在：`docs/sample-funds.md` 已记录主动权益、指数、债券三类样本。
- 已验证样本年报下载与解析链路：`110011` 的 2024 年年报可下载，且可提取约 70K 字全文与 99 个表格。
- 2026-05-21 已移除外部 `dayu-agent` 生产依赖，`pip install -e .` 不再需要下载该 wheel。

---

### P1: 数据层（PDF 下载 + 解析 + 提取）

**目标**

完成 PDF 下载、解析和数据提取功能，能从基金年报中提取 12 项关键数据。

**进入条件**

- [x] P0 退出条件全部满足
- [x] 样本基金 PDF 已下载到本地

**退出条件**

- [ ] `fund/pdf/downloader.py` 能下载任意基金年报 PDF（输入基金代码）
- [ ] `fund/pdf/parser.py` 能解析 PDF 并提取文本和表格
- [ ] `fund/data_extractor.py` 能提取 12 项关键数据（准确率 > 90%）
- [ ] `fund/pdf/cache.py` 两级缓存（文件 + SQLite）可用
- [ ] 对 3 只样本基金的数据提取结果与人工核对一致

**任务切片**

| Slice | 任务 | 验证方式 |
|-------|------|---------|
| P1-S1 | 文档访问契约收口 | `FundDocumentRepository.load_annual_report(...)` 成为唯一公开入口 |
| P1-S2 | 章节定位修复与 `§3` 冻结 | `110011/2024` 年报稳定命中 `§3` 正文 |
| P1-S3 | 两级缓存与仓库内解析物化 | 重复加载同一年报不重复下载/不重复全文解析 |
| P1-S4 | 基础画像与基金类型识别 | 3 只样本都输出 `classified_fund_type` 与 `classification_basis` |
| P1-S5 | `§3` 表现提取与投资者收益 fallback | 净值增长率、基准收益率、投资者收益三态输出 |
| P1-S6 | 管理人文本、换手率、利益一致性与持有人结构 | `§4/§8/§9` 直接披露字段可结构化提取 |
| P1-S7 | 持仓快照与份额变动 | 前十大重仓、份额期初/期末/净变动可回归 |
| P1-S8 | façade 集成、净值数据适配器与 P1 验收矩阵 | 3 只样本 36 格矩阵至少 `33/36` 通过 |

**验证要求**

- 对 3 只样本基金（指数/主动/债券各 1 只）执行全量数据提取
- 每只基金提取 12 项数据，与人工核对准确率 > 90%
- 缓存命中时提取时间 < 1 秒

**风险与追踪**

| 风险 | 概率 | 缓解措施 | 追踪状态 |
|------|------|---------|---------|
| 不同基金公司年报格式差异大 | 高 | 设计兜底策略：解析失败显示"数据获取失败" | ⬜ 待验证 |
| 2026 新规"投资者收益率"尚未落地 | 中 | 先用份额变动估算，新规落地后切换 | ⬜ 待验证 |
| akshare API 不稳定 | 中 | 备选天天基金直接 API | ⬜ 待验证 |

**当前实现基线（2026-05-17）**

- 已有 `fund_agent/fund/pdf/downloader.py` 原型，可通过 akshare 查找公告并下载样本基金 `110011` 的 2024 年年报。
- 已有 `fund_agent/fund/pdf/parser.py` 原型，可提取全文文本、表格，并提供 `locate_sections()` / `extract_section()` 的初版章节定位能力。
- 当前章节定位尚不稳定：在样本基金 `110011` 上仅定位到 `§1/§2/§4/§5/§8/§9/§10`，漏掉 `§3`，还不能支撑后续 12 项结构化提取。
- 结构化数据提取模块、SQLite 缓存层和测试套件尚未落地。

**P1-S1 当前状态（2026-05-17）**

- `P1-S1 文档访问契约收口`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/documents/*` 已承载稳定公共契约与唯一仓库入口
  - `FundDocumentRepository.load_annual_report(...)` 不再向上层暴露本地 `Path`
  - `fund_agent/fund/pdf/downloader.py` 已明确降级为内部 helper，并去除目标年份缺失时的 silent fallback
  - downloader / adapter 中的同步阻塞调用已通过 `asyncio.to_thread(...)` 隔离
  - 相关测试命令 ` .venv/bin/python -m pytest tests/fund/documents/test_repository.py tests/fund/pdf/test_downloader.py ` 当前通过（`11 passed`）
- 当前 residual risks：
  - `P1-S2` owner：`parser.py` 章节定位原型仍未稳定，`§3` 漏识别尚未关闭
  - `P1-S3` owner：缓存根路径策略与 SQLite 物化尚未落地
  - 后续 phase owner：当前只支持 `annual_report`，未扩展到其它文档类型

**P1-S2 当前状态（2026-05-17）**

- `P1-S2 章节定位修复与 §3 冻结`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/pdf/section_catalog.py` 已承载 `§1/§2/§3/§4/§5/§8/§9/§10` 的标题规则和目录信号规则
  - `fund_agent/fund/pdf/parser.py` 已从硬编码字典改为消费配置化 catalog
  - `tests/fixtures/fund/pdf_sections/110011_2024_excerpt.txt` 已固定“目录行 + 正文行同名”的 `§3` 事实
  - `tests/fund/pdf/test_parser.py` 已覆盖：
    - 正文 `§3` 命中
    - 目录误判回归
    - `§1/§2/§3/§4/§8/§9/§10` 偏移单调递增
  - 验证命令 `.venv/bin/python -m pytest tests/fund/pdf/test_parser.py -q` 当前通过（`3 passed`）
- 当前 residual risks：
  - `P1-S3` owner：负向/边界测试仍偏少，可在缓存阶段一并补强
  - 后续样本回归 owner：`§5` 当前规则已存在，但 fixture 尚未覆盖
  - 后续样本回归 owner：`§3` 模式仍使用 `.*` 贪婪通配，需由更多样本决定是否收窄

**P1-S3 当前状态（2026-05-17）**

- `P1-S3 两级缓存与仓库内解析物化`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/documents/cache.py` 已提供 `AnnualReportDocumentCache`
  - `documents` 表与 `parsed_reports` 表已在 `documents` 层内部落地
  - parsed report 已物化到 `cache/documents/parsed_reports/*.json`
  - repository 已支持：
    - parsed report 缓存命中
    - 已记录 PDF 路径复用
    - `force_refresh=True` 穿透 parsed report 与 PDF 路径缓存
  - `tests/fund/documents/test_cache.py` 与 `tests/fund/documents/test_repository.py` 已覆盖缓存最小闭环
  - 验证命令 `.venv/bin/python -m pytest tests/fund/documents -q` 当前通过（`10 passed`）
- 当前 residual risks：
  - 后续性能优化 owner：缓存 `initialize()` 每次操作都会重复执行，当前正确但不够高效
  - 后续性能优化 owner：默认缓存实例不做复用，当前单仓库场景无正确性风险
  - 后续缓存治理 owner：缓存根目录仍使用相对路径，后续若要统一根路径策略再单独裁决

**P1-S4 当前状态（2026-05-17）**

- `P1-S4 基础画像与基金类型识别`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/fund_type.py` 已提供 6 类标准基金类型标签和 `FundTypeClassification`
  - `fund_agent/fund/extractors/models.py` 已提供 `EvidenceAnchor`、`ExtractedField`、`ProfileExtractionResult`
  - `fund_agent/fund/extractors/profile.py` 已落地：
    - `basic_identity`
    - `product_profile`
    - `benchmark`
    - `fee_schedule`
  - `extract_profile(report)` 已显式先调用 `classify_fund_type(report)`，再构造通用画像字段
  - `basic_identity.value` 已稳定包含：
    - `classified_fund_type`
    - `classification_basis`
  - `tests/fund/extractors/test_profile.py` 已覆盖：
    - 分类先于通用字段构造
    - 主动权益 / 增强指数 / 债券三类样本识别
    - 费率、基准、规模、经理 anchor 存在
  - 验证命令 `.venv/bin/python -m pytest tests/fund/extractors/test_profile.py -q` 当前通过（`4 passed`）
- 当前 residual risks：
  - 后续 extractor refactor owner：`fund_type.py` 与 `profile.py` 之间仍有部分字段 pattern 重复定义
  - 后续样本回归 owner：`index_fund` / `qdii_fund` / `fof_fund` 仍缺 fixture 与测试覆盖
  - 后续可维护性优化 owner：`_build_basic_identity()` 当前使用列表索引映射字段，后续若继续扩字段建议改为按名字组织

**P1-S5 当前状态（2026-05-17）**

- `P1-S5 §3 表现提取与投资者收益 fallback`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/extractors/models.py` 已补充 `PerformanceExtractionResult`
  - `fund_agent/fund/extractors/performance.py` 已落地：
    - `nav_benchmark_performance`
    - `investor_return`
  - `investor_return` 当前已稳定区分：
    - `direct`
    - `estimated`
    - `missing`
  - `tests/fund/extractors/test_performance.py` 已覆盖：
    - 净值增长率 / 基准收益率提取与 anchor
    - 投资者收益率直接披露路径
    - 投资者收益率估算披露路径
    - 投资者收益率未披露时显式 `missing`
    - `nav_benchmark_performance` 部分命中时显式保留 `missing`
  - `tests/fixtures/fund/extractors/performance/` 已固定最小 `§3` 文本夹具
  - 验证命令 `.venv/bin/python -m pytest tests/fund/extractors/test_performance.py -q` 当前通过（`5 passed`）
- 当前 residual risks：
  - 后续 fallback owner：当前 `estimated` 仅覆盖 `§3` 中显式标记“估算”的披露，不包含依赖 `§10` 或净值序列的后续 fallback
  - 后续集成测试 owner：`§3` 整体缺失路径仍需在真实样本矩阵或单独 fixture 中补强
  - 后续样本回归 owner：当前以最小文本夹具锁定三态输出，真实样本覆盖仍需在 `P1-S8` 验收矩阵阶段继续扩展

**P1-S6 当前状态（2026-05-17）**

- `P1-S6 管理人文本、换手率、利益一致性与持有人结构`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/extractors/models.py` 已补充 `ManagerOwnershipExtractionResult`
  - `fund_agent/fund/extractors/manager_ownership.py` 已落地：
    - `manager_strategy_text`
    - `turnover_rate`
    - `manager_alignment`
    - `holder_structure`
  - `manager_alignment.value["judgment"]` 当前固定为 `None`，确保 P1 只输出原始披露
  - `tests/fund/extractors/test_manager_ownership.py` 已覆盖：
    - 完整披露路径
    - 未披露 `missing` 路径
    - 部分披露路径
    - 换手率口径命中但数值缺失路径
    - 换手率与持有人信息 anchor
  - `tests/fixtures/fund/extractors/manager_ownership/` 已固定最小 `§4/§8/§9` 文本夹具
  - 验证命令 `.venv/bin/python -m pytest tests/fund/extractors/test_manager_ownership.py -q` 当前通过（`4 passed`）
- 当前 residual risks：
  - 后续样本回归 owner：真实年报 `§4/§8/§9` 可能使用表格或不同字段名称，需在 `P1-S8` 验收矩阵阶段继续扩展
  - 后续估算 owner：换手率未披露时的同类中位数估算尚未接入，当前只能显式返回 `missing`

**P1-S7 当前状态（2026-05-17）**

- `P1-S7 持仓快照与份额变动`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/extractors/models.py` 已补充 `HoldingsShareChangeExtractionResult`
  - `fund_agent/fund/extractors/holdings_share_change.py` 已落地：
    - `holdings_snapshot`
    - `share_change`
  - `tests/fund/extractors/test_holdings_share_change.py` 已覆盖：
    - 前十大重仓表
    - 行业分布表
    - 份额变动表
    - 行业分布缺失路径
    - 表格整体缺失路径
  - 验证命令 `.venv/bin/python -m pytest tests/fund/extractors/test_holdings_share_change.py -q` 当前通过（`3 passed`）
- 当前 residual risks：
  - 后续样本回归 owner：真实年报表头差异仍需在 `P1-S8` 验收矩阵阶段继续扩展
  - 后续 schema owner：当前表格行按原表头输出，最终标准字段名需在 façade 集成前裁决

**P1-S8 当前状态（2026-05-17）**

- `P1-S8 façade 集成、净值数据适配器与 P1 验收矩阵`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/data_extractor.py` 已落地：
    - `StructuredFundDataBundle`
    - `FundDataExtractor`
  - `fund_agent/fund/data/nav_data.py` 已落地：
    - `FundNavDataAdapter`
    - `NavDataResult`
    - `nav_cache` SQLite 表
  - `tests/fund/integration/test_p1_sample_matrix.py` 已覆盖 3 只样本基金 12 项矩阵，当前结果 `36/36`
  - `tests/fund/data/test_nav_data.py` 已覆盖净值缓存命中和强制刷新
  - 验证命令 `.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_parser.py tests/fund/extractors tests/fund/data/test_nav_data.py tests/fund/integration/test_p1_sample_matrix.py -q` 当前通过（`32 passed`）
- 当前 residual risks：
  - 后续端到端 owner：当前 P1 矩阵使用 fake repository 和 fixture report，真实 PDF 样本矩阵需在端到端验证中继续扩展
  - 后续网络验证 owner：默认 akshare fetcher 已封装，本轮测试未访问真实网络

---

### P2: 分析引擎（R=A+B-C + 检验 + 审计）

**目标**

完成收益归因计算、言行一致性检验、投资者获得感分析、否决项检查、程序审计功能。

**进入条件**

- [x] P1 退出条件全部满足
- [x] 12 项关键数据可从缓存获取

**退出条件**

- [x] `fund/analysis/r_abc.py` 能计算近 1/3/5 年 R=A+B-C 归因
- [x] `fund/analysis/alpha_judge.py` 能区分结构性 vs 阶段性超额
- [x] `fund/analysis/consistency_check.py` 能输出言行一致性 4 维度信号
- [x] `fund/analysis/investor_return.py` 能计算行为损益
- [x] `fund/analysis/risk_check.py` 能执行 5 项否决检查 + 压力测试
- [x] `fund/analysis/checklist.py` 能输出 7 问题红/黄/绿灯
- [x] `fund/audit/audit_programmatic.py` 能执行 P1/P2/P3/L1/R1/R2 规则检查
- [x] `fund/template/renderer.py` 能将数据填充到定性模板 v2

**任务切片**

| Slice | 任务 | 验证方式 |
|-------|------|---------|
| P2-S1 | 实现 R=A+B-C 计算模块 | 对样本基金计算，与手动计算一致 |
| P2-S2 | 实现超额收益性质判断 | 对已知基金判断结果合理 |
| P2-S3 | 实现言行一致性检验 | 对样本基金输出 4 维度信号 |
| P2-S4 | 实现投资者获得感分析 | 计算行为损益 + 资金流向判断 |
| P2-S5 | 实现否决项检查 | 5 项否决条件检查正确 |
| P2-S6 | 实现压力测试 | 模拟 -20%/-40%/-60% 场景 |
| P2-S7 | 实现检查清单引擎 | 7 问题输出红/黄/绿灯 |
| P2-S8 | 实现程序审计（P1/P2/P3/L1/R1/R2） | 能检测到故意注入的错误 |
| P2-S9 | 实现模板渲染器 | 输出 8 章报告 Markdown |
| P2-S10 | 实现证据锚点标注 | 每个数据标注来源 |

**验证要求**

- R=A+B-C 计算结果与手动计算误差 < 0.01%
- 程序审计能检测到以下注入错误：
  - 章节缺失（P1）
  - 关键字段为空（P2）
  - R=A+B-C 计算不闭合（L1）
  - 检查清单信号与规则不一致（R1）
- 模板渲染输出包含 8 章完整内容

**P2-S1 当前状态（2026-05-17）**

- `P2-S1 实现 R=A+B-C 计算模块`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/analysis/r_abc.py` 已提供纯计算入口 `calculate_r_abc(...)` 与多周期入口 `calculate_r_abc_series(...)`
  - `calculate_r_abc_from_bundle(...)` 已支持从 P1 `StructuredFundDataBundle` 适配计算
  - `RabcAttribution` 已输出 `R/B/A/C/turnover_cost/net_excess_return` 与参与计算字段的 `EvidenceAnchor`
  - 缺少股票仓位、关键字段或关键子字段时返回 `missing`，不使用默认仓位或间接假设
  - `tests/fund/analysis/test_r_abc.py` 已覆盖公式闭合、P1 字段解析、证据锚点和缺失路径
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis/test_r_abc.py -q` 当前通过（`6 passed`）
- 当前 residual risks：
  - `P2-S2` owner：当前只输出数值归因，不判断结构性/阶段性超额
  - `P2-S8` owner：L1 公式审计尚未接入
  - 后续 extractor refinement owner：股票仓位仍需显式输入，尚未由 P1 稳定抽取

**P2-S2 当前状态（2026-05-17）**

- `P2-S2 实现超额收益性质判断`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/analysis/alpha_judge.py` 已提供 `judge_alpha_nature(...)`
  - `observations_from_attributions(...)` 已支持从 P2-S1 `RabcAttribution` 适配判断样本
  - `AlphaJudgment` 已输出性质判断、正 Alpha 期数、环境覆盖、来源解释计数、判断依据和风险
  - 纯指数基金返回 `not_applicable`
  - 样本不足返回 `insufficient_data`，不强行判断结构性或阶段性
  - 市场环境和来源解释强度必须显式传入，缺失时报错
  - `tests/fund/analysis/test_alpha_judge.py` 已覆盖核心判断路径
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis/test_alpha_judge.py -q` 当前通过（`7 passed`）
- 当前 residual risks：
  - `P2-S3` owner：来源解释强度后续应由言行一致性和持仓行为检查提供更强证据
  - `P3-S2 or later market-state adapter` owner：市场环境标签后续应由温度计或市场状态模块显式传入
  - `P2-S8` owner：性质判断与报告文字一致性审计尚未接入

**P2-S3 当前状态（2026-05-17）**

- `P2-S3 实现言行一致性检验`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/analysis/consistency_check.py` 已提供 `check_consistency(...)`
  - 4 维度输出：
    - 投资风格：§4 风格宣称 vs 显式实际持仓风格
    - 行业偏好：§4 行业宣称 vs §8 行业分布
    - 仓位管理：§4 仓位策略 vs 显式实际股票仓位
    - 换手水平：§4 持有周期/换手宣称 vs §8 换手率
  - `ConsistencyCheckResult` 已输出整体状态和信号
  - 缺少实际风格或股票仓位时返回 `insufficient_data`，不使用默认假设
  - `tests/fund/analysis/test_consistency_check.py` 已覆盖核心信号路径
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis/test_consistency_check.py -q` 当前通过（`5 passed`）
- 当前 residual risks：
  - 后续 extractor refinement owner：实际持仓风格和股票仓位仍需显式输入，尚未由 P1 稳定抽取
  - 后续 multi-period behavior analysis owner：跨期风格稳定性尚未实现
  - `P2-S8` owner：言行一致性信号与报告文字一致性审计尚未接入

**P2-S4 当前状态（2026-05-17）**

- `P2-S4 实现投资者获得感分析`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/analysis/investor_return.py` 已提供 `analyze_investor_experience(...)`
  - `calculate_behavior_gap(...)` 已计算行为损益：投资者实际收益率减基金产品收益率
  - `judge_fund_flow(...)` 已基于 §10 份额净变动和产品收益方向判断资金流向
  - `InvestorExperienceResult` 已输出获得感状态、行为损益和资金流向
  - 投资者收益率缺失时返回 `missing`，不静默估算
  - 份额变动子字段缺失时资金流向返回 `missing`
  - `tests/fund/analysis/test_investor_return.py` 已覆盖核心路径
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis/test_investor_return.py -q` 当前通过（`6 passed`）
- 当前 residual risks：
  - 后续 investor_return fallback refinement owner：投资者收益率缺失 fallback 尚未实现
  - later monthly flow adapter owner：高点/低点追涨抄底无法仅凭年度份额净变动精细定位
  - `P2-S8` owner：行为损益和报告文字一致性审计尚未接入

**P2-S5 当前状态（2026-05-17）**

- `P2-S5 实现否决项检查`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/analysis/risk_check.py` 已提供 `run_risk_checks(...)`
  - 5 项否决检查已覆盖：
    - 清盘风险：基金规模 `< 5000 万元`
    - 基金经理任期：管理本基金 `< 6 个月`
    - 严重风格漂移：言行一致性检验红灯
    - 费率远超同类：总费率 `> 同类中位数 × 2`
    - 跟踪误差过大：指数基金跟踪误差 `> 2%`
  - `RiskCheckResult` 已输出汇总状态、否决项、跟踪项和下一步最小验证问题
  - 缺少经理任期、同类费率中位数或跟踪误差时返回 `insufficient_data`，不强行判安全
  - `tests/fund/analysis/test_risk_check.py` 已覆盖核心否决路径和缺失输入路径
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis/test_risk_check.py -q` 当前通过（`10 passed`）
- 当前 residual risks：
  - `P2-S6` owner：压力测试需在同一风险模块内接入
  - later external metrics adapter owner：经理任期、同类费率中位数和跟踪误差仍由调用方显式提供
  - `P2-S8` owner：否决项与报告结论一致性审计尚未接入

**P2-S6 当前状态（2026-05-17）**

- `P2-S6 实现压力测试`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/analysis/risk_check.py` 已提供 `run_stress_test(...)`
  - 固定模拟 `-20% / -40% / -60%` 三个场景，符合 `docs/design.md` 第 4.5 节
  - `StressTestRule` 已配置模板第 6 章 `preferred_lens` 的基金类型阈值
  - `StressScenarioResult` 已输出账户余额、浮亏金额、压力等级、承受能力状态和判断依据
  - 最大可承受亏损比例缺失时返回 `not_provided`，不猜测用户能否承受
  - `tests/fund/analysis/test_risk_check.py` 已覆盖固定场景、主动/债券基金阈值、缺失承受能力、非法输入和自定义阈值配置
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis/test_risk_check.py -q` 当前通过（`10 passed`）
  - controller code review artifact：`docs/reviews/p2-s6-code-review-controller-judgment-2026-05-17.md`
- 当前 residual risks：
  - `P3` owner：压力测试输出已进入 P2-S9 模板渲染，端到端用户流程尚未验证
  - `P2-S8` owner：压力测试和报告文字一致性审计尚未接入
  - later user-profile input owner：投入金额和最大可承受亏损比例当前由调用方显式提供
  - `P2 aggregate review` owner：本 slice 外部 reviewer 未产出可采纳 artifact，aggregate review 前需重新取得两份独立 review 或记录用户接受单 reviewer 风险

**P2-S7 当前状态（2026-05-17）**

- `P2-S7 实现检查清单引擎`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/analysis/checklist.py` 已提供 `run_checklist(...)`
  - 检查清单已覆盖 `docs/design.md` 第 4.6 节 7 个问题：
    - 超额收益能覆盖成本吗？
    - 基金经理跟我一条心吗？
    - 投资者真的赚到钱了吗？
    - 说的和做的一样吗？
    - 这只基金不死吗？
    - 当前估值处于什么位置？
    - 这笔钱 3-4 年内不会用吗？
  - `ChecklistResult` 已输出 7 项结果、红/黄/灰分组、汇总信号和下一步最小验证问题
  - 估值状态和用户资金期限必须由调用方显式提供；缺失时返回灰灯
  - `tests/fund/analysis/test_checklist.py` 已覆盖核心规则路径
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis -q` 当前通过（`40 passed`）
  - controller code review artifact：`docs/reviews/p2-s7-code-review-controller-judgment-2026-05-17.md`
- 当前 residual risks：
  - `P2-S8` owner：R1/R2 审计尚未验证检查清单信号与规则一致性
  - later thermometer adapter owner：估值状态当前由调用方显式传入，尚未接入温度计
  - later user-profile input owner：资金期限当前由调用方显式传入，尚未接入用户问答或画像

**P2-S8 当前状态（2026-05-18）**

- `P2-S8 实现程序审计（P1/P2/P3/L1/R1/R2）`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/audit/audit_programmatic.py` 已提供 `run_programmatic_audit(...)`
  - 已覆盖 MVP 程序审计规则：
    - `P1`：报告章节结构不匹配
    - `P2`：章节内容过短
    - `P3`：缺少证据与出处或证据锚点
    - `L1`：R=A+B-C 数值计算不闭合
    - `R1`：检查清单信号与规则不一致
    - `R2`：最终判断与检查清单信号矛盾
  - `ProgrammaticAuditInput` 明确区分报告 Markdown、R=A+B-C 结构化结果、检查清单结果和最终判断
  - 缺少报告、R=A+B-C 结构化结果、检查清单或最终判断时返回失败，不把未执行规则伪装成通过
  - `tests/fund/audit/test_audit_programmatic.py` 已覆盖必需输入缺失、故意注入错误和未知检查清单信号防御
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis tests/fund/audit -q` 当前通过（`49 passed`）
  - controller code review artifact：`docs/reviews/p2-s8-code-review-controller-judgment-2026-05-18.md`
- 当前 residual risks：
  - `P2-S9` owner：模板渲染器已接入程序审计输入
  - `P3-S4` owner：端到端报告通过程序审计尚未验证
  - v2 audit owner：E1/E2/E3/C1/C2 和 LLM/证据复核层尚未实现

**P2-S9 当前状态（2026-05-18）**

- `P2-S9 实现模板渲染器`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/template/renderer.py` 已提供 8 章 Markdown 模板渲染器
  - `TemplateRenderInput` 显式聚合 P1 `StructuredFundDataBundle`、P2 分析结果、检查清单、压力测试、最终判断和可选当前阶段说明
  - `TemplateRenderResult` 输出 `report_markdown`、`audit_input` 和去重后的 `evidence_anchors`
  - `audit_input` 可直接用于 `run_programmatic_audit(...)`
  - 章节内证据行使用 `> 📎 证据：年报§...`，附录输出 `## 证据与出处`
  - 缺失数据显式输出“未披露”或“数据不足”
  - 最终判断限制为 `worth_holding / needs_attention / suggest_replace`
  - 已修复 code review 发现的 `dict_values(...)` 泄漏、重复句号和 README 过期条目
  - `tests/fund/template/test_renderer.py` 已覆盖 8 章完整性、证据锚点格式、审计兼容、缺失路径、禁用交易措辞和 review 回归
  - 验证命令 `.venv/bin/python -m pytest tests/fund/template tests/fund/audit -q` 当前通过（`18 passed`）
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis -q` 当前通过（`40 passed`）
  - code review artifacts：
    - `docs/reviews/p2-s9-code-review-mimo-2026-05-18.md`
    - `docs/reviews/p2-s9-code-review-glm-2026-05-18.md`
    - `docs/reviews/p2-s9-code-review-controller-judgment-2026-05-18.md`
    - `docs/reviews/p2-s9-rereview-glm-2026-05-18.md`
- 当前 residual risks：
  - `P2-S10` owner：证据锚点正文和附录格式已专项收口
  - `P3-S4` owner：端到端 CLI 报告通过程序审计尚未验证
  - later template refinement owner：`_validate_report_wording()` 使用 substring 匹配禁用词，未来模板若引入合法分析短语“买入前检查清单”可能误报

**P2-S10 当前状态（2026-05-18）**

- `P2-S10 实现证据锚点标注`：✅ completed
- 当前完成内容：
  - 正文证据行对年报来源输出年份、章节和证据描述
  - 附录年报锚点按 `年报{年份}§{章节}表{编号}行{行号}` 输出
  - 表格、行定位、章节缺失时显式写 `未定位`
  - 页码以附加位置元数据保留
  - 非年报来源输出 `外部数据(external_api)`、`计算(derived)` 或未知来源标签，不伪装成年报
  - 缺少章节证据时，正文输出数据不足证据行，附录输出章节级缺证条目
  - `tests/fund/template/test_renderer.py` 已覆盖正文证据格式、附录表格/行定位、缺失定位降级、页码保留、非年报来源、缺证章节和审计兼容
  - 验证命令 `.venv/bin/python -m pytest tests/fund/template tests/fund/audit -q` 当前通过（`23 passed`）
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis -q` 当前通过（`40 passed`）
  - code review artifacts：
    - `docs/reviews/p2-s10-code-review-mimo-2026-05-18.md`
    - `docs/reviews/p2-s10-code-review-glm-2026-05-18.md`
    - `docs/reviews/p2-s10-code-review-controller-judgment-2026-05-18.md`
- 当前 residual risks：
  - `P2 aggregate deepreview` owner：已验证 P2-S1 至 P2-S10 组合后无跨 slice 回归
  - `P3-S4` owner：端到端 CLI 报告通过程序审计尚未验证
  - later evidence confirm owner：缺证附录当前为章节级，不是 item 级证据确认
  - later template refinement owner：`_validate_report_wording()` 使用 substring 匹配禁用词，未来模板若引入合法分析短语“买入前检查清单”可能误报

**P2 aggregate deepreview 当前状态（2026-05-18）**

- `P2 aggregate deepreview`：✅ completed
- 当前完成内容：
  - 审查范围为 `a6b1516...HEAD`，覆盖 `P2-S9` 模板渲染器、`P2-S10` 证据锚点标注、相关测试、README 与 gate artifact
  - AgentMiMo aggregate review 结论为 PASS，无 blocking finding
  - AgentGLM aggregate review 结论为 PASS，无 blocking finding；接受 1 个 doc-sync info finding：P2 退出条件中模板渲染器 checkbox 未勾选
  - 已完成 doc-sync fix，将 P2 进入条件、退出条件、phase 状态和下一 gate 同步到当前真实状态
  - 验证命令 `.venv/bin/python -m pytest tests/fund/template tests/fund/audit tests/fund/analysis -q` 当前通过（`63 passed`）
  - aggregate review artifacts：
    - `docs/reviews/p2-aggregate-review-mimo-2026-05-18.md`
    - `docs/reviews/p2-aggregate-review-glm-2026-05-18.md`
    - `docs/reviews/p2-aggregate-fix-2026-05-18.md`
    - `docs/reviews/p2-aggregate-review-controller-judgment-2026-05-18.md`
  - accepted deepreview commit：`07fe0d0`
- 当前 residual risks：
  - `P3-S4` owner：端到端 CLI 报告通过程序审计尚未验证
  - later evidence confirm owner：缺证附录当前为章节级，不是 item 级证据确认
  - later template refinement owner：`_validate_report_wording()` 使用 substring 匹配禁用词，未来模板若引入合法分析短语“买入前检查清单”可能误报
  - v2 audit owner：`_EVIDENCE_MARKER_PATTERN` 和审计章节标题匹配依赖当前模板措辞，未来模板措辞调整时需同步测试

**Draft PR gate 当前状态（2026-05-18）**

- `Draft PR #1`：✅ draft-PR-pass
- 当前完成内容：
  - 已将 `a6b1516` 推送为远端 `main`
  - 已将 `chore/reconcile-baseline` 推送到远端并创建 draft PR：`https://github.com/bill20232033cc/fund-agent/pull/1`
  - PR review 接受 1 个 info finding：aggregate review artifact 存在 trailing whitespace
  - 已移除 trailing whitespace，并记录修复 artifact
  - AgentGLM re-review 结论为 PASS
  - accepted PR review commit：`8f5029c`
  - follow-up push 已完成
- 当前验证：
  - `.venv/bin/python -m pytest tests/fund/template tests/fund/audit tests/fund/analysis -q`：`63 passed`
  - `git diff --check`：通过
  - PR merge state：`CLEAN`
- 未执行动作：
  - 未 merge PR
  - 未 mark ready for review
  - 未 request reviewers
  - 未 delete branch

**风险与追踪**

| 风险 | 概率 | 缓解措施 | 追踪状态 |
|------|------|---------|---------|
| 业绩基准计算复杂（多指数加权） | 中 | MVP 先用简化计算，v2 精确实现 | ⬜ 待验证 |
| 超额收益性质判断主观性强 | 中 | MVP 用规则引擎（多年度为正 + 不同环境），v2 引入 LLM | ⬜ 待验证 |

---

### P3: CLI 入口 + 整合测试 + 验证

**目标**

完成 CLI 入口封装，整合所有功能，实现端到端验证。

**进入条件**

- [x] P2 退出条件全部满足
- [x] 单只基金分析可本地运行

**退出条件**

- [x] `fund-analysis analyze <fund_code>` 命令可用
- [x] 输出完整 8 章分析报告（Markdown 格式）
- [x] 报告通过程序审计
- [x] 3 只样本基金端到端测试通过
- [x] 单只基金分析时间 < 30 秒（不含 PDF 下载）
- [x] 包含 README.md（安装 + 使用说明）
- [x] 单元测试覆盖率 > 50%

**任务切片**

| Slice | 任务 | 验证方式 |
|-------|------|---------|
| P3-S1 | CLI 入口封装（Typer，与当前 `pyproject.toml` 入口对齐） | `fund-analysis analyze 110011` 输出报告 |
| P3-S2 | 温度计数据爬取（有知有行） | 能获取全市场和指数温度 |
| P3-S3 | 端到端整合测试 | 3 只样本基金完整流程 |
| P3-S4 | 程序审计集成 | 报告通过 P1/P2/P3/L1/R1/R2 |
| P3-S5 | 证据锚点集成 | 每个数据标注来源 |
| P3-S6 | 编写 README.md | 包含安装、使用、示例 |
| P3-S7 | 编写单元测试 | pytest 覆盖率 > 50% |
| P3-S8 | 性能优化 | 单只基金 < 30 秒 |

**验证要求**

- 端到端测试：输入 3 只样本基金代码，输出 3 份完整报告
- 每份报告包含 8 章内容 + 证据锚点
- 程序审计全部通过
- `pytest` 覆盖率 > 50%

**风险与追踪**

| 风险 | 概率 | 缓解措施 | 追踪状态 |
|------|------|---------|---------|
| 有知有行页面结构变更 | 中 | 异常处理 + 24h 缓存 | ⬜ 待验证 |
| 整合测试发现数据层 bug | 高 | 预留 2 天 buffer | ⬜ 待验证 |

**P3-S1 当前状态（2026-05-18）**

- `P3-S1 CLI 入口封装`：✅ completed
- 当前完成内容：
  - `fund_agent/services/fund_analysis_service.py` 新增 `FundAnalysisService`、`FundAnalysisRequest` 和 `FundAnalysisResult`
  - Service 通过显式请求字段编排 `FundDataExtractor.extract(...)`、P2 分析、8 章模板渲染和程序审计
  - UI 层 `fund_agent/ui/cli.py` 保持 Typer，与当前 `pyproject.toml` 脚本入口一致
  - `fund-analysis analyze FUND_CODE` 输出完整 Markdown 到 stdout，失败时输出 `分析失败：...` 并非零退出
  - `fund-analysis checklist FUND_CODE` 不再输出误导性成功文本，当前非零退出并提示使用 `analyze`
  - `README.md` 和 `tests/README.md` 已同步当前 CLI 和测试边界
  - 验证命令 `.venv/bin/python -m pytest tests/services tests/ui tests/fund/template tests/fund/audit tests/fund/analysis -q` 当前通过（`68 passed`）
  - `git diff --check` 当前通过
  - code review artifacts：
    - `docs/reviews/p3-s1-code-review-glm-2026-05-18.md`
    - `docs/reviews/p3-s1-code-review-controller-judgment-2026-05-18.md`
    - `docs/reviews/p3-s1-fix-2026-05-18.md`
    - `docs/reviews/p3-s1-rereview-glm-2026-05-18.md`
  - accepted slice commit：`c5a240c`
- 当前 residual risks：
  - `P3-S2` owner：Service 当前没有市场环境和来源解释输入，`judge_alpha_nature(())` 会显式返回 `insufficient_data`
  - `P3-S3` owner：真实 PDF/网络路径和 3 只样本基金 CLI 端到端矩阵尚未验证
  - later CLI UX owner：程序审计失败信息当前直接透出审计消息，MVP 可接受但后续可优化用户文案

**P3-S2 当前状态（2026-05-18）**

- `P3-S2 温度计数据爬取（有知有行）`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/data/thermometer.py` 新增 `FundThermometerAdapter`
  - 输出 `ThermometerSnapshot`、`MarketTemperature`、`IndexTemperature`、`MacroTemperature`
  - 默认读取 `https://youzhiyouxing.cn/data` 与 `https://youzhiyouxing.cn/data/macro`
  - 支持 24h fresh cache、7 天 stale fallback、无缓存失败 `unavailable=True`
  - 支持当前真实页面布局：全市场 `70°`/`70℃`、指数代码位于名称单元格、前置非指数表跳过、`10年期国债到期收益率`
  - 缓存写入失败不阻断已成功抓取和解析的数据
  - 当前只提供 Capability data adapter，尚未接入 Service、CLI 或检查清单估值状态
  - live-response smoke 验证可解析全市场温度、11 行指数数据、沪深300温度/内在收益率/股息率、债市温度和 10 年期国债到期收益率
  - 验证命令 `.venv/bin/python -m pytest tests/fund/data/test_thermometer.py -q` 当前通过（`13 passed`）
  - 验证命令 `.venv/bin/python -m pytest tests/fund/data tests/fund/analysis tests/services tests/ui -q` 当前通过（`60 passed`）
  - `git diff --check` 当前通过
  - code review artifacts：
    - `docs/reviews/p3-s2-implementation-2026-05-18.md`
    - `docs/reviews/p3-s2-code-review-glm-2026-05-18.md`
    - `docs/reviews/p3-s2-code-review-mimo-2026-05-18.md`
    - `docs/reviews/p3-s2-code-review-controller-judgment-2026-05-18.md`
    - `docs/reviews/p3-s2-fix-2026-05-18.md`
    - `docs/reviews/p3-s2-rereview-glm-2026-05-18.md`
    - `docs/reviews/p3-s2-rereview-mimo-2026-05-18.md`
  - accepted slice commit：`1747aaf`
- 当前 residual risks：
  - `P3-S3/P3-S4` owner：温度计 adapter 尚未接入 Service/CLI/checklist valuation_state
  - `P3-S3/P3-S4` owner：有知有行页面结构仍可能变化，后续集成测试和运行监控需覆盖 unavailable/stale 输出
  - later integration owner：Service/CLI 接入时应显式传入运行期 cache root，避免依赖进程 cwd

**P3-S3 当前状态（2026-05-18）**

- `P3-S3 端到端整合测试`：✅ completed
- 当前完成内容：
  - `tests/fund/integration/test_p3_cli_e2e_matrix.py` 新增 3 只样本基金 CLI 端到端矩阵
  - 矩阵覆盖 `110011 -> qdii_fund`、`510300 -> index_fund`、`000171 -> bond_fund`
  - CLI 矩阵通过 fake repository / fake nav provider 隔离网络与 PDF 副作用，但仍经过真实 Typer CLI、Service、`FundDataExtractor`、extractors、P2 analysis、模板渲染和程序审计
  - 修复真实 `§2` 表格键值字段抽取、低质量 parsed report cache 复用和模板 `benchmark_text` 契约错配
  - 验证命令 `.venv/bin/python -m pytest tests/fund/data tests/fund/documents tests/fund/extractors tests/fund/integration tests/fund/template tests/fund/audit tests/fund/analysis tests/services tests/ui -q` 当前通过（`115 passed`）
  - `git diff --check` 当前通过
  - code review artifacts：
    - `docs/reviews/p3-s3-code-review-controller-judgment-2026-05-18.md`
    - `docs/reviews/p3-s3-code-review-glm-2026-05-18.md`
    - `docs/reviews/p3-s3-code-review-mimo-2026-05-18.md`
  - accepted slice commit：`e0b1b93`
- 当前 residual risks：
  - classifier cleanup owner：基金简称中的 QDII 标识仍建议后续作为独立字段参与分类，避免仅依赖 investment_scope 的理论漏判
  - later integration owner：真实 PDF/网络路径仍应保留人工 smoke 或独立运行监控

**P3-S4 当前状态（2026-05-18）**

- `P3-S4 程序审计集成`：✅ completed
- 当前完成内容：
  - P3 CLI 端到端矩阵新增 `_RecordingService` 测试代理，记录真实 `FundAnalysisService.analyze(...)` 返回值
  - 对 3 只样本基金逐一断言 `audit_result.passed`
  - 对 3 只样本基金逐一断言 `audit_result.checked_rules == ("P1", "P2", "P3", "L1", "R1", "R2")`
  - 对 3 只样本基金逐一断言 `audit_result.issues == ()`
  - 验证命令 `.venv/bin/python -m pytest tests/fund/integration/test_p3_cli_e2e_matrix.py tests/services/test_fund_analysis_service.py tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_renderer.py -q` 当前通过（`26 passed`）
  - 验证命令 `.venv/bin/python -m pytest tests/fund/data tests/fund/documents tests/fund/extractors tests/fund/integration tests/fund/template tests/fund/audit tests/fund/analysis tests/services tests/ui -q` 当前通过（`115 passed`）
  - `git diff --check` 当前通过
  - artifacts：
    - `docs/reviews/p3-s4-implementation-2026-05-18.md`
    - `docs/reviews/p3-s4-code-review-controller-judgment-2026-05-18.md`
  - accepted implementation commit：`caf5b31`
- 当前 residual risks：
  - P3-S4 使用 fake repository / fake nav provider 隔离网络与 PDF，不替代真实运行 smoke

**P3-S5 当前状态（2026-05-18）**

- `P3-S5 证据锚点集成`：✅ completed
- 当前完成内容：
  - `tests/fund/integration/test_p3_cli_e2e_matrix.py` 新增 `_body_evidence_lines(...)`、`_appendix_evidence_lines(...)` 和 `_assert_complete_evidence_contract(...)`
  - 3 只样本基金每份 CLI 报告均断言正文 `> 📎 证据：` 行数量为 8，覆盖模板 0-7 章
  - 3 只样本基金每份 CLI 报告均断言正文证据行包含 `年报2024§`，且不出现“当前章节未携带证据锚点”
  - 3 只样本基金每份 CLI 报告均断言附录不出现 `- [M...]` 缺证占位
  - 附录断言覆盖关键数据来源：`§2` 基金身份/产品/基准、`§3` 净值与投资者收益、`§4` 管理人策略、`§8` 重仓和行业、`§9` 基金经理持有、`§10` 份额变动
  - 验证命令 `.venv/bin/python -m pytest tests/fund/integration/test_p3_cli_e2e_matrix.py tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py -q` 当前通过（`24 passed`）
  - `git diff --check` 当前通过
  - artifacts：
    - `docs/reviews/p3-s5-implementation-2026-05-18.md`
    - `docs/reviews/p3-s5-code-review-controller-judgment-2026-05-18.md`
  - accepted slice commit：`46432c0`
- 当前 residual risks：
  - P3-S5 当前验证的是 deterministic fake repository 输出的报告证据契约，不替代真实 PDF/network smoke

**P3-S6 当前状态（2026-05-18）**

- `P3-S6 编写 README.md`：✅ completed
- 当前完成内容：
  - 根目录 `README.md` 已重写为用户手册，覆盖安装、5 分钟跑通、常用命令、常用参数、报告输出、当前能力、本地验证和文档导航
  - README 当前命令与 Typer CLI 对齐：`fund-analysis --help`、`fund-analysis analyze --help`、`fund-analysis analyze FUND_CODE`
  - README 明确 `fund-analysis checklist` 仍是占位命令，避免误导用户认为独立检查清单已接入
  - README 已移除“3 只样本基金端到端 CLI 矩阵尚未实现”的过期表述
  - README 文档导航仅保留当前仓库真实存在的文档路径
  - 验证命令 `.venv/bin/fund-analysis --help` 当前通过
  - 验证命令 `.venv/bin/fund-analysis analyze --help` 当前通过
  - `git diff --check` 当前通过
  - artifacts：
    - `docs/reviews/p3-s6-implementation-2026-05-18.md`
    - `docs/reviews/p3-s6-code-review-controller-judgment-2026-05-18.md`
  - accepted slice commit：`8904588`
- 当前 residual risks：
  - README 示例命令未在本 slice 执行真实 PDF/network smoke，后续仍需独立验证真实数据路径

**P3-S7 当前状态（2026-05-18）**

- `P3-S7 编写单元测试`：✅ completed
- 当前完成内容：
  - `pyproject.toml` 的 dev 依赖新增 `pytest-cov>=7.1`
  - `tests/README.md` 新增覆盖率 gate 命令和 P3-S7 覆盖率目标说明
  - 验证命令 `.venv/bin/python -m pytest tests/fund/data tests/fund/documents tests/fund/extractors tests/fund/integration tests/fund/template tests/fund/audit tests/fund/analysis tests/services tests/ui --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` 当前通过
  - 当前结果：`115 passed`，`Required test coverage of 50% reached. Total coverage: 90.07%`
  - artifacts：
    - `docs/reviews/p3-s7-implementation-2026-05-18.md`
    - `docs/reviews/p3-s7-code-review-controller-judgment-2026-05-18.md`
  - accepted slice commit：`d1d506b`
- 当前 residual risks：
  - 覆盖率是广度信号，不替代语义 review；真实 PDF/network smoke 仍需独立验证

**P3-S8 当前状态（2026-05-18）**

- `P3-S8 性能优化`：✅ completed
- 当前完成内容：
  - `tests/services/test_fund_analysis_service.py` 新增 `test_fund_analysis_service_completes_single_fund_under_p3_s8_limit_without_pdf_download`
  - 测试使用 `_FakeExtractor` 排除网络和 PDF 下载，符合 P3 退出条件“不含 PDF 下载”
  - 测试仍经过真实 Service 编排、P2 分析、8 章模板渲染和程序审计
  - 显式阈值 `_P3_S8_MAX_ANALYSIS_SECONDS = 30.0`
  - `tests/README.md` 新增性能 gate 说明
  - 验证命令 `.venv/bin/python -m pytest tests/services/test_fund_analysis_service.py -q` 当前通过（`3 passed`）
  - artifacts：
    - `docs/reviews/p3-s8-implementation-2026-05-18.md`
    - `docs/reviews/p3-s8-code-review-controller-judgment-2026-05-18.md`
  - accepted slice commit：`7845add`
- 当前 residual risks：
  - 该 gate 不覆盖真实 PDF 下载、PDF 解析、网络波动或冷缓存墙钟时间

**P3 Aggregate Deepreview 当前状态（2026-05-18）**

- `P3 aggregate deepreview`：✅ completed
- 当前完成内容：
  - controller aggregate deepreview artifact：`docs/reviews/code-review-20260518-2223.md`
  - review scope：`main..feat/p3-cli-integration`
  - 结论：PASS，无 blocking finding
  - 验证命令 `.venv/bin/python -m pytest tests/fund/integration/test_p3_cli_e2e_matrix.py tests/services/test_fund_analysis_service.py tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py -q` 当前通过（`27 passed`）
  - 覆盖率命令 `.venv/bin/python -m pytest tests/fund/data tests/fund/documents tests/fund/extractors tests/fund/integration tests/fund/template tests/fund/audit tests/fund/analysis tests/services tests/ui --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` 当前通过（`116 passed`，总覆盖率 `90.07%`）
  - `git diff --check` 当前通过
- reviewer availability：
  - 本轮 aggregate review 未取得可用 MiMo/GLM 独立新 artifact：MiMo pane 被用户 `.tmux.conf` 输入污染，GLM pane 保留旧的长运行 review context
  - controller 已在 aggregate artifact 中记录该风险；如进入 draft PR gate 前仍需要双外部 reviewer，可重新清 pane 后派发
- 当前 residual risks：
  - 真实 PDF/network smoke 仍未自动化，owner：ready-to-open-draft-PR gate 或后续 PR review
  - 温度计 adapter 尚未接入 CLI/Service 报告，owner：后续 phase / issue
  - 基金简称 QDII 标识可作为独立分类字段继续清理，owner：后续 classifier cleanup

**P3 Draft PR 当前状态（2026-05-18）**

- `draft PR gate`：✅ completed
- PR：`https://github.com/bill20232033cc/fund-agent/pull/2`
- PR 状态：MERGED
- base：`main`
- head：`feat/p3-cli-integration`
- checks：GitHub 当前返回 no checks reported
- merge commit：`0be218f28ea7d26c7ad1e55963ca907217f5dede`
- mergedAt：`2026-05-18T15:30:34Z`
- PR-level deepreview：✅ PASS
- PR review artifact：`docs/reviews/pr-2-review-20260518-2307.md`
- PR review validation：
  - `.venv/bin/python -m pytest tests/fund/integration/test_p3_cli_e2e_matrix.py tests/services/test_fund_analysis_service.py tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py -q`：`27 passed`
  - coverage matrix：`116 passed`，总覆盖率 `90.07%`
  - `git diff --check main..HEAD`：passed
- 当前 residual risks：
  - 真实 PDF/network smoke 未自动化，owner：post-MVP follow-up planning
  - 温度计 adapter 尚未接入 Service/CLI 报告，owner：post-MVP follow-up planning

**运维提醒当前状态（2026-05-18）**

- 用户级 launchd job `com.fund-agent.agentcontroller-reminder` 仍已加载：`StartInterval=1800`，`runs=38`，`last exit code=0`。
- launchd 调用脚本：`/Users/maomao/fund-agent/scripts/remind-agentcontroller.sh 继续推进`。
- 脚本不是固定发送到 `ai:coding.1`，而是按当前仓库路径和 pane title `controller` 自动发现目标 pane。
- 当前 tmux 中存在 `ai:coding.1`，但当前多 Agent 总控 pane title 为 `AgentController`；如果需要定时提醒继续打到当前 `agents` session 总控，应同步调整脚本的 pane title 匹配规则或重命名目标 pane。

---

## 3. 依赖关系

```
P0（环境搭建）
  └── P1（数据层）
        └── P2（分析引擎）
              └── P3（整合测试）
```

- 所有 Phase 串行执行，无并行 Phase
- P1 内部的 Slice 可部分并行（P1-S4~P1-S7 在 P1-S3 被接受后可并行）
- P2 内部的 Slice 可部分并行（P2-S1~S7 与 P2-S8~S10 可并行）

---

## 4. 阻塞问题追踪

| ID | 问题 | 影响 Phase | 状态 | 决议 |
|----|------|-----------|------|------|
| BQ-1 | 公募基金年报下载主源选择 | P0/P1/P7 | 🟡 reopened for source strategy | 当前实现已不直接访问巨潮，而是 akshare + Eastmoney PDF；AgentCodex 建议 EID/证监会资本市场电子化信息披露平台作为主源、天天基金/Eastmoney fallback，controller 已记录为 P7 data-source migration，artifact=`docs/reviews/annual-report-source-strategy-reconciliation-20260520.md` |
| BQ-2 | 2026 新规"投资者收益率"披露时间表 | P2 | ⬜ open | P1 已提供 `investor_return` 三态和 `share_change` 输入，P2 再实现行为损益 |
| BQ-3 | 有知有行温度数据页面结构 | P3 | ✅ closed | P3-S2 已用真实响应 smoke 验证 `/data` 与 `/data/macro` 当前布局，并以 fake HTML 单测锁定关键解析路径 |
| BQ-4 | akshare 基金净值 API 稳定性 | P1/P3 | 🟡 partially closed | P1-S8 已封装可注入 fetcher 与 `nav_cache`，真实网络验证移交 P3 |
| BQ-5 | 当前章节定位规则无法稳定识别 `§3` 正文 | P1 | ✅ closed | 已由 P1-S2 章节定位修复与 `§3` 冻结关闭 |

---

## 5. 残余风险追踪

| ID | 风险 | Phase | 缓解状态 | 需要人类裁决？ |
|----|------|-------|---------|--------------|
| RR-1 | PDF 格式不统一导致解析失败 | P1 | 已设计兜底策略 | 否 |
| RR-2 | 超额收益性质判断主观性强 | P2 | MVP 用规则引擎 | 否 |
| RR-3 | 审计规则过严导致频繁阻断 | P2 | MVP 仅启用程序审计 | 否 |
| RR-4 | 温度计爬虫被封锁 | P3/v2 | P5-S7 已提供 read-only Service/CLI、24h 缓存、7 天 stale fallback 与 `unavailable=True`；自动映射为 `valuation_state` 仍 deferred，除非先有同源估值规则 | 是（如被封锁且无可用缓存需人工确认） |
| RR-5 | `dayu-agent` wheel 下载受 GitHub 可达性影响 | P0/P1 | 已关闭：2026-05-21 裁决移除外部 Dayu 生产依赖；后续 Host/Engine/tool-loop 能力必须项目内化 | 否 |
| RR-6 | 模板禁用交易措辞使用 substring 匹配，未来合法短语可能误报 | P3/v2 | P2 当前输出已测试通过；P3 若调整模板措辞需同步审查 | 否 |
| RR-7 | 缺证附录当前为章节级，不是 item 级证据确认 | v2 | MVP 先保证章节级可追溯，Evidence Confirm 层后续细化 | 否 |
| RR-8 | CLI 端到端真实 PDF/网络路径尚未覆盖 | P3/v2 | P3-S3 用 3 只样本基金 deterministic 端到端矩阵验证 Service/CLI/Capability 主链路；真实 PDF/network smoke 移交 P5-S7 / post-MVP infra validation | 否 |
| RR-9 | 真实 `§2` 字段主要位于表格而非冒号文本行 | P3 | P3-S3 已让 profile extractor / fund type classifier 读取键值型表头与数据行，并以 3 只样本基金矩阵覆盖 | 否 |
| RR-10 | 历史低质量 parsed report 缓存污染真实端到端输出 | P3 | P3-S3 已在 parsed report 缓存命中前检查正文长度与关键章节集合，不合格缓存回退为未命中 | 否 |
| RR-11 | 精选基金池真实年报提取质量不可量化 | P4 | 已关闭；P4 已建立 extraction snapshot、score、quality gate、per-fund blocking 与最小 correctness 链路 | 否 |
| RR-12 | `004393` 被误判为 `index_fund` | P4 | 已关闭；P4-S3a 已修复为 `active_fund` 并通过真实 snapshot 验证 | 否 |
| RR-13 | 精选基金池 CSV 中 `016492` 重复 | P4/P5 | P5-S6 artifact 已形成：`docs/code_20260519.csv` 第 26 行 `南方均衡成长混合A,016492` 与第 35 行 `易方达逆向投资混合A,016492` 冲突；需用户/App 源确认，不由代码自动裁决 | 是 |
| RR-14 | P4 quality gate 缺少 per-fund 阻断粒度 | P4 | 已关闭；P4 aggregate re-review MiMo/GLM 均 PASS，controller 裁决=`docs/reviews/p4-aggregate-rereview-controller-judgment-20260519.md` | 否 |
| RR-15 | P4 quality gate 未接入 `analyze` 主链路 | P4/P5 | 已关闭；P5-S1 accepted，quality gate 已通过 `analyze` Service 显式接入，CLI/Service 支持 `off/warn/block` 和结构化阻断结果；裁决=`docs/reviews/p5-s1-acceptance-reconciliation-20260520.md` | 否 |
| RR-16 | correctness 可比字段覆盖面窄 | P4/P5/P6 | 部分关闭；P5-S3 已新增 snapshot `comparable_values` 白名单并让 correctness 比较 `basic_identity`、`benchmark`、`nav_benchmark_performance`、`classified_fund_type` 的稳定子字段；P6-S1/S5 将先补机器化 contract 基础，再决定是否升级 contract-aware correctness / FQ5 | 否 |
| RR-17 | P4 draft PR 前工作树范围不清 | P4 | 已关闭；PR inclusion set 已在 `docs/reviews/p4-pr-scope-hygiene-reconciliation-20260520.md` 明确，draft PR 必须按 include / exclude 清单准备 | 否 |
| RR-18 | 年报下载主源不是监管披露主源 | P7 | 当前实现通过 akshare + Eastmoney PDF 下载年报；已接受 EID/证监会资本市场电子化信息披露平台作为后续主源方向，天天基金/Eastmoney 作为 fallback，需独立 P7 plan/review/implementation，不阻塞 P6-S1 | 否 |
| RR-19 | 模板源文档第 7 章 `危级/降级阈值` 疑似 typo | P6 | P6-S1 保持 manifest 与 `docs/fund-analysis-template-draft.md` 源文档忠实一致，未单边改成 `升级/降级阈值`；后续模板源文档清理时应同步修正 source template 与 manifest | 否 |

---

## 6. 后续迭代（非 MVP 范围）

### v2（Week 6-9）

| 功能 | 说明 |
|------|------|
| 严选基金池内横向比较 | 同类型基金择优 |
| LLM 审计 | 证据充分性（E1/E2/E3）+ 内容合规性（C1/C2） |
| 证据复核 | 对 E1/E2 类违规执行二次确认（supported/confirmed_missing） |
| 修复闭环 | patch（局部修补）+ regenerate（整章重建）+ 锚点重写 |
| LLM 写作 | 从模板填充升级为 LLM 生成差异化分析 |

### v3（Week 10-13）

| 功能 | 说明 |
|------|------|
| 组合管理 | 再平衡引擎 + 目标市值策略 |
| 温度计自建 | AKShare + 自行计算 PE/PB 百分位 |
| Web UI | FastAPI + 前端 |
| 微信入口 | 微信消息适配 |

---

## 7. 状态更新日志

| 日期 | Phase | 状态变更 | 备注 |
|------|-------|---------|------|
| 2026-05-16 | 全部 | 创建 | 初始版本 |
| 2026-05-17 | P0 | ✅ done | 全部退出条件满足；项目更名为 fund-agent；数据源改用 akshare + eastmoney |
| 2026-05-17 | P1 | 🟡 in progress | 完成 Git 基线初始化与 baseline reconciliation；下一 gate 为 P1 plan |
| 2026-05-17 | P1 | 🟡 in progress | P1 计划通过 re-review；accepted artifacts 为 `docs/reviews/p1-plan-2026-05-17.md`、`docs/reviews/p1-plan-review-2026-05-17.md`；下一 gate 为 `P1-S1 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S5` code review / fix / re-review 已收口，accepted slice commit=`8102944`；下一 gate 为 `P1-S6 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S6` implementation 已完成，`§4/§8/§9` 管理人/持有人 extractor 与测试已落地；当前 gate 维持 `P1-S6 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S6` controller review 已通过；下一 gate 为 `P1-S7 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S6` 已接受，accepted commit 为 `18566f9`；下一 gate 为 `P1-S7 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S7` implementation 已完成，`§8/§10` 持仓/份额 extractor 与测试已落地；当前 gate 维持 `P1-S7 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S7` controller review 已通过；下一 gate 为 `P1-S8 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S7` 已接受，accepted commit 为 `3167754`；下一 gate 为 `P1-S8 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S8` implementation 已完成，façade、净值适配器与 `36/36` 样本矩阵已落地；当前 gate 维持 `P1-S8 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S8` controller review 已通过；下一 gate 为 `P1 aggregate review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S8` 已接受，accepted commit 为 `d398bc2`；下一 gate 为 `P1 aggregate review` |
| 2026-05-17 | P1 | ✅ done | P1 aggregate review 通过，artifact 为 `docs/reviews/p1-aggregate-review-2026-05-17.md`；下一 gate 为 `P2-S1 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | 进入 `P2-S1 implementation + review`，优先实现 R=A+B-C 计算模块 |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S1` implementation 与 controller review 已通过；下一 gate 为 `P2-S2 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S2` implementation 与 controller review 已通过；下一 gate 为 `P2-S3 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S3` implementation 与 controller review 已通过；下一 gate 为 `P2-S4 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S4` implementation 与 controller review 已通过；下一 gate 为 `P2-S5 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S5` implementation 与 controller review 已通过；下一 gate 为 `P2-S6 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S6` implementation 已完成，压力测试固定场景与基金类型阈值已落地；当前 gate 为 `P2-S6 code review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S6` controller review 已通过；外部 reviewer 未产出可采纳 artifact，风险追踪到 `P2 aggregate review`；下一 gate 为 `P2-S7 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S7` implementation 已完成，7 问题检查清单引擎与测试已落地；当前 gate 为 `P2-S7 code review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S7` controller review 已通过；下一 gate 为 `P2-S8 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S8` implementation 已完成，P1/P2/P3/L1/R1/R2 程序审计与测试已落地；当前 gate 为 `P2-S8 code review` |
| 2026-05-18 | P2 | 🟡 in progress | `P2-S8` controller review 已通过并修复缺少必需输入时静默通过的问题；下一 gate 为 `P2-S9 implementation + review` |
| 2026-05-18 | P2 | 🟡 in progress | `P2-S1` 至 `P2-S8` 已收口为 accepted baseline commit `a6b1516`；`launchd/`、`scripts/` 和旧 P1 review artifact 保持在 P2 基线外；当前 gate 维持 `P2-S9 implementation + review` |
| 2026-05-18 | P2 | 🟡 in progress | `P2-S9` implementation / review / fix / re-review 已通过，8 章模板渲染器和程序审计输入已落地，accepted commit=`bf64b0f`；下一 gate 为 `P2-S10 implementation + review` |
| 2026-05-18 | P2 | 🟡 in progress | `P2-S10` implementation / code review 已通过，证据锚点正文和附录格式已收口，accepted commit=`2d041ae`；下一 gate 为 `P2 aggregate deepreview` |
| 2026-05-18 | P2 | ✅ done | `P2 aggregate deepreview` 已通过，MiMo/GLM 均 PASS；已修复 P2 exit checkbox 文档同步问题；accepted deepreview commit=`07fe0d0`；当前 gate 为 `ready-to-open-draft-PR` |
| 2026-05-18 | P3 | ⬜ pending | P2 退出条件已满足；下一步需用户授权 draft PR gate 后 push 并创建 draft PR，随后再进入 P3 实施 |
| 2026-05-18 | P2 | ✅ done | Draft PR #1 已创建并通过 PR review/fix/re-review；accepted PR review commit=`8f5029c` 已 push；当前 gate 为 `draft-PR-pass` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S1 implementation + review` 已进入实现；当前代码入口为 Typer，因此 P3-S1 按 current-code alignment 保留 `fund-analysis analyze FUND_CODE` 子命令并通过 Service 层编排 Capability。 |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S1` implementation / code review / fix / re-review 已通过；CLI 通过 Service 层输出 8 章 Markdown，当前验证 `68 passed`；accepted commit=`c5a240c`；下一 gate 为 `P3-S2 implementation + review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S2 implementation + review` 已进入实现；温度计 adapter 目标为读取有知有行 `/data` 与 `/data/macro`，提供 24h fresh cache、7 天 stale fallback 和 unavailable 状态，暂不接入 CLI/Service。 |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S2` implementation / code review / controller fix 已通过；温度计 adapter 当前验证 `60 passed` 且真实响应 smoke 可解析全市场、指数、债市与 10 年期国债到期收益率；accepted commit=`1747aaf`；下一 gate 为 `P3-S3 implementation + review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S3 implementation` 已完成；新增 3 只样本基金 CLI 端到端矩阵并修复真实表格抽取、低质量 parsed cache 复用和模板基准字段契约错配；当前验证 `33 passed`；下一 gate 为 `P3-S3 code review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S3` implementation / controller code review 已通过；新增 3 只样本基金 CLI 端到端矩阵并修复真实表格抽取、低质量 parsed cache 复用和模板基准字段契约错配；当前验证 `115 passed` 且 `git diff --check` 通过；accepted commit=`e0b1b93`；下一 gate 为 `P3-S4 implementation + review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S4 implementation` 已完成；P3 CLI 端到端矩阵现在显式记录真实 Service 返回值，并断言 P1/P2/P3/L1/R1/R2 全部程序审计规则执行通过；当前验证 `26 passed`；下一 gate 为 `P3-S4 code review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S4` implementation / controller code review 已通过；P3 CLI 端到端矩阵已验证 3 只样本基金的 `audit_result.passed`、`checked_rules == P1/P2/P3/L1/R1/R2` 和空 issues；当前验证 `115 passed` 且 `git diff --check` 通过；accepted implementation commit=`caf5b31`；下一 gate 为 `P3-S5 implementation + review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S5 implementation` 已完成；P3 CLI 端到端矩阵现在断言每份报告 8 章正文证据行、关键附录来源锚点和无缺证占位；当前验证 `1 passed`；下一 gate 为 `P3-S5 code review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S5` implementation / controller code review 已通过；P3 CLI 端到端矩阵已验证每份报告 8 章正文证据行、关键附录来源锚点和无缺证占位；当前验证 `24 passed` 且 `git diff --check` 通过；accepted commit=`46432c0`；下一 gate 为 `P3-S6 implementation + review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S6 implementation` 已完成；根 README 已按当前 CLI 成功路径更新为用户手册，并移除过期端到端矩阵状态；当前验证 `fund-analysis --help`、`fund-analysis analyze --help` 和 `git diff --check` 通过；下一 gate 为 `P3-S6 code review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S6` implementation / controller code review 已通过；根 README 已按当前 CLI 成功路径更新为用户手册，文档导航均指向真实文件；当前验证 `fund-analysis --help`、`fund-analysis analyze --help` 和 `git diff --check` 通过；accepted commit=`8904588`；下一 gate 为 `P3-S7 implementation + review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S7 implementation` 已完成；dev 依赖和测试手册新增覆盖率 gate，当前 `fund_agent` 总覆盖率 `90.07%`，超过 50% 目标；当前验证 `115 passed`；下一 gate 为 `P3-S7 code review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S7` implementation / controller code review 已通过；dev 依赖和测试手册新增覆盖率 gate，当前 `fund_agent` 总覆盖率 `90.07%`，超过 50% 目标；当前验证 `115 passed`；accepted commit=`d1d506b`；下一 gate 为 `P3-S8 implementation + review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S8 implementation` 已完成；Service 层新增不含 PDF 下载的单只基金分析性能 gate，验证完整编排低于 30 秒；当前验证 `3 passed`；下一 gate 为 `P3-S8 code review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S8` implementation / controller code review 已通过；Service 层新增不含 PDF 下载的单只基金分析性能 gate，验证完整编排低于 30 秒；当前验证 `3 passed`；accepted commit=`7845add`；下一 gate 为 `P3 aggregate deepreview` |
| 2026-05-18 | P3 | 🟡 in progress | `P3 aggregate deepreview` 已通过 controller review，无 blocking finding；当前验证 `27 passed`、覆盖率矩阵 `116 passed / 90.07%` 且 `git diff --check` 通过；review artifact=`docs/reviews/code-review-20260518-2223.md`；下一 gate 为 `ready-to-open-draft-PR` |
| 2026-05-18 | P3 | 🟡 in progress | Draft PR 2 已创建并保持 draft 状态；URL=`https://github.com/bill20232033cc/fund-agent/pull/2`；GitHub 当前 no checks reported；当前 gate 为 `draft-PR-pass` |
| 2026-05-18 | P3 | 🟡 in progress | PR 2 level deepreview 已通过，无 blocking finding；review artifact=`docs/reviews/pr-2-review-20260518-2307.md`；当前验证 `27 passed`、覆盖率矩阵 `116 passed / 90.07%` 且 `git diff --check main..HEAD` 通过；PR 仍为 draft，mark ready / merge 需用户额外授权 |
| 2026-05-18 | P3 | 🟡 in progress | PR 2 已标记 ready for review；PR 状态 OPEN / ready，mergeable=`MERGEABLE`，GitHub 当前 no checks reported；merge 需用户额外授权 |
| 2026-05-18 | P3 | ✅ done | PR 2 已合入 `main`；merge commit=`0be218f28ea7d26c7ad1e55963ca907217f5dede`，mergedAt=`2026-05-18T15:30:34Z`；当前 gate 为 `P3 closed / PR 2 merged`，下一 gate 为 `post-MVP follow-up planning` |
| 2026-05-19 | P4 | 🟡 in progress | 用户提供 `docs/code_20260519.csv` 作为有知有行 App 精选基金池；人工测试 `004393` 暴露基金类型误判和核心字段大量缺失；已形成 `docs/post-mvp-p4-first-principles-plan.md` 与 controller 裁决 `docs/reviews/p4-audit-input-controller-judgment-20260519-0144.md`；`docs/implementation-control-p4.md` 已通过 MiMo/GLM plan review 与 controller 裁决；当前 gate 为 `P4-S1 implementation` |
| 2026-05-19 | P4-S1 | 🟡 code review | Selected Fund Extraction Snapshot + Quality Gate MVP implementation 已完成；artifact=`docs/reviews/p4-s1-implementation-20260519.md`；当前验证 `17 passed`、CLI help passed、dry-run smoke passed；当前 gate 为 `P4-S1 code review` |
| 2026-05-19 | P4-S1 | ✅ accepted | MiMo/GLM code review 均 PASS；controller 裁决=`docs/reviews/p4-s1-code-review-controller-judgment-20260519.md`；accepted commit=`c8a47f6`；当前验证 `17 passed`、CLI help passed、dry-run smoke passed；下一 gate 为 `P4-S2 plan / implementation` |
| 2026-05-19 | P4-S2 | 🟡 implementation | 当前进入字段级 coverage / traceability scoring；实现产物为 `score.json`、`score.md`、`golden_set.json`；Correctness 和人工 golden answer 留到 P4-S2 后半段；货币基金先作为 edge case 不纳入最小 golden set |
| 2026-05-19 | P4-S2 | 🟡 code review | 字段级 coverage / traceability scoring 与最小 golden set selection 已完成；artifact=`docs/reviews/p4-s2-implementation-20260519.md`；当前验证 `17 passed`、ruff passed、CLI help passed、diff check passed |
| 2026-05-19 | P4-S2 | ✅ accepted | MiMo/GLM code review 均 PASS；controller 裁决=`docs/reviews/p4-s2-code-review-controller-judgment-20260519.md`；accepted commit=`47f2656`；当前验证 `17 passed`、ruff passed、CLI help passed、diff check passed；下一 gate 为 `P4-S3 implementation` |
| 2026-05-19 | P4-S3a | ✅ accepted | `004393` 类型误判已修复为 `active_fund`；MiMo/GLM code review 与 targeted re-review 均 PASS；controller 裁决=`docs/reviews/p4-s3a-code-review-controller-judgment-20260519.md`；accepted commit=`0b3fbc6`；当前验证 `15 passed`、ruff passed、diff check passed；下一 gate 为 `P4-S3b implementation` |
| 2026-05-19 | P4-S3b | ✅ accepted | `004393` 的 5 个高影响 extractor 缺口已修复；MiMo/GLM code review 与 targeted re-review 均 PASS，controller 裁决=`docs/reviews/p4-s3b-code-review-controller-judgment-20260519.md`；当前验证 `24 passed`、ruff passed、diff check passed；真实 snapshot/score 显示本 slice 5 字段 coverage / traceability 均为 `100.0%`；下一 gate 为 `P4-S4 implementation` |
| 2026-05-19 | P4-S4 | ✅ accepted by reconciliation | control-doc reconciliation 裁决 P4-S4 的 golden answer 标注前链路与 quality gate skeleton 已落地；裁决=`docs/reviews/p4-s4-control-doc-reconciliation-20260519.md`；下一 gate 为 `P4 aggregate deepreview` |
| 2026-05-19 | P4 aggregate deepreview | ❌ failed | MiMo/Codex/DS 三份 aggregate deepreview 已完成；controller 裁决=`docs/reviews/p4-aggregate-deepreview-controller-judgment-20260519.md`；blocking finding 为 score / quality gate 仅按字段聚合，缺少 per-fund 阻断粒度；下一 gate 为 `P4 aggregate fix` |
| 2026-05-19 | P4 aggregate fix | ✅ implemented | 已新增 `fund_scores` 单基金质量汇总与 quality gate 单基金 P0 阻断；新增测试覆盖“字段聚合 pass 但单基金 P0 fail 仍 block”；三方 reconciliation artifact=`docs/reviews/p4-design-control-code-reconciliation-20260519.md`；当前验证 `20 passed`、ruff passed、diff check passed；下一 gate 为 `P4 aggregate re-review` |
| 2026-05-19 | P4 aggregate re-review | ✅ accepted | MiMo/GLM re-review 均 PASS；controller 裁决=`docs/reviews/p4-aggregate-rereview-controller-judgment-20260519.md`；P4-R7/RR-14 per-fund blocking 已关闭；下一 gate 为 `correctness golden answer completion` |
| 2026-05-19 | correctness golden answer completion | ✅ accepted | 用户完成 004393 第一张表；AgentCodex 补全后续 5 张表；`reports/golden-answers/golden-answer-prefill-reviewed.md` 已通过 strict build，输出 `reports/golden-answers/golden-answer.json`；artifact=`docs/reviews/correctness-golden-answer-completion-20260519.md`；下一 gate 为 `correctness slice implementation` |
| 2026-05-19 | correctness slice implementation | 🟡 completed | AgentCodex 已实现 P4-R10 最小 correctness 自动比对；strict `golden-answer.json` 通过显式 `--golden-answer-path` 接入 extraction-score，`score.json/score.md` 输出 correctness，quality gate 对明确 mismatch 触发 `FQ1/block`；artifact=`docs/reviews/correctness-slice-implementation-20260519.md`；当前验证 `28 passed`、ruff passed、diff check passed，真实 004393 smoke 中 `classified_fund_type.fund_type` match；下一 gate 为 `correctness slice code review` |
| 2026-05-19 | correctness slice code review | ✅ accepted | MiMo/GLM code review 均 PASS；MiMo low finding `ruff format` 已修复；controller 裁决=`docs/reviews/correctness-slice-code-review-controller-judgment-20260519.md`；当前验证 `28 passed`、ruff check passed、ruff format check passed、diff check passed；P4-R10 关闭，下一 gate 为 `P4 readiness reconciliation` |
| 2026-05-20 | P4 readiness reconciliation | ✅ accepted | controller 裁决 P4 功能态已可进入 final aggregate deepreview；P4-R8/R9/RR-15/RR-16 均有后续 owner，不阻断当前 P4 skeleton；artifact=`docs/reviews/p4-readiness-reconciliation-20260520.md`；下一 gate 为 `P4 final aggregate deepreview` |
| 2026-05-20 | P4 final aggregate deepreview | ✅ accepted after cleanup | MiMo/GLM final aggregate deepreview 均接受 P4 功能态；MiMo blocking `ruff format` 与 GLM info `F541` 已修复；controller 裁决=`docs/reviews/p4-final-aggregate-deepreview-controller-judgment-20260520.md`；当前验证 targeted `73 passed`、full suite `171 passed`、ruff check passed、ruff format check passed、diff check passed；下一 gate 为 `P4 PR scope hygiene / inclusion-set reconciliation` |
| 2026-05-20 | P4 PR scope hygiene | ✅ accepted | PR inclusion set 已裁决，artifact=`docs/reviews/p4-pr-scope-hygiene-reconciliation-20260520.md`；RR-17/P4-R11 范围不清关闭；`reports/golden-answers/*` 作为 curated correctness fixture 纳入，`reports/extraction-snapshots/**`、`scripts/**`、`launchd/**`、旧 P2/PR1 artifacts 排除；当前 gate 为 `ready-to-open-draft-PR` |
| 2026-05-20 | P4 draft PR gate | ✅ draft-PR-pass | Draft PR 3 已创建：`https://github.com/bill20232033cc/fund-agent/pull/3`；MiMo/GLM PR-level review 均 PASS，controller 裁决=`docs/reviews/pr-3-review-controller-judgment-20260520.md`；PR body scope wording info 已修正；GitHub 当前 no checks reported，PR mergeable=`MERGEABLE`；PR 已标记 ready for review，merge 需用户额外授权 |
| 2026-05-20 | P4 merge | ✅ done | PR 3 已 squash merge 到 `main`；merge commit=`7596c5ece4894166d5479ee764fc8641a23cfc0d`；mergedAt=`2026-05-19T18:51:24Z`；当前 gate 为 `P4 closed / PR 3 merged`，下一 gate 为 `post-P4 follow-up planning` |
| 2026-05-20 | post-P4 follow-up planning | ✅ accepted | controller 裁决下一阶段第一优先级为 P5-S1 quality gate integration；artifact=`docs/reviews/post-p4-follow-up-planning-20260520.md`；当前 gate 为 `post-P4 follow-up planning accepted`，下一 gate 为 `P5-S1 quality gate integration plan/review` |
| 2026-05-20 | P5-S1 quality gate integration plan | 🟡 drafted | plan artifact=`docs/reviews/p5-s1-quality-gate-integration-plan-20260520.md`；计划要求 Service 复用已抽取 bundle 生成 quality gate，不在 CLI 层串跑 snapshot；当前 gate 为 `P5-S1 quality gate integration plan drafted`，下一 gate 为 `P5-S1 plan review` |
| 2026-05-20 | P5-S1 plan review/fix | 🟡 patched | controller plan review artifact=`docs/reviews/p5-s1-plan-review-controller-20260520.md`；已回写结构化 `QualityGateBlockedError` 与非覆盖默认 run id 要求；当前 gate 为 `P5-S1 plan patched after controller review`，下一 gate 为 `P5-S1 plan re-review` |
| 2026-05-20 | P5-S1 plan re-review | ✅ passed | controller re-review artifact=`docs/reviews/p5-s1-plan-rereview-controller-20260520.md`；两个 plan blocker 均关闭；当前 gate 为 `P5-S1 implementation`，下一 gate 为 `P5-S1 code review` |
| 2026-05-20 | P5-S1 implementation | 🟡 completed | implementation artifact=`docs/reviews/p5-s1-implementation-20260520.md`；新增 bundle-to-gate adapter、Service/CLI quality gate 接入、结构化阻断异常和测试/README 同步；当前验证 targeted `19 passed`、full suite `179 passed`、ruff passed、diff check passed；当前 gate 为 `P5-S1 implementation completed`，下一 gate 为 `P5-S1 code review` |
| 2026-05-20 | P5-S1 code review/fix | ✅ passed after fix | controller code review artifact=`docs/reviews/code-review-20260520-0350.md`；已修复单基金合法 CSV 被 `select_minimal_golden_set()` 误伤的问题；当前验证 related `26 passed`、full suite `179 passed`、ruff passed、diff check passed；当前 gate 为 `P5-S1 code review passed after fix`，下一 gate 为 `P5-S1 acceptance / aggregate readiness` |
| 2026-05-20 | P5-S1 acceptance reconciliation | ✅ accepted | controller 裁决=`docs/reviews/p5-s1-acceptance-reconciliation-20260520.md`；P4 quality gate 已接入 `fund-analysis analyze` 主链路，RR-15/P4-R8 关闭；当前 gate 为 `P5-S1 accepted`，下一 gate 为 `P5-S2 quality gate rules plan/review` |
| 2026-05-20 | P5-S2 quality gate rules plan | 🟡 drafted | plan artifact=`docs/reviews/p5-s2-quality-gate-rules-plan-20260520.md`；计划在 Capability 层新增 `score.json.fund_quality` 并补齐 FQ1 App 类别冲突、FQ4 snapshot 缺失率、FQ5 preferred_lens mismatch；当前 gate 为 `P5-S2 quality gate rules plan drafted`，下一 gate 为 `P5-S2 plan review` |
| 2026-05-20 | P5-S2 plan review/fix | 🟡 patched | controller plan review artifact=`docs/reviews/p5-s2-plan-review-controller-20260520.md`；已修订 FQ5 为 `preferred_lens_resolvability`、补充 `fund_quality` 字段一致性检查和 issue metadata schema；当前 gate 为 `P5-S2 plan patched after controller review`，下一 gate 为 `P5-S2 plan re-review` |
| 2026-05-20 | P5-S2 plan re-review | ✅ passed | controller re-review artifact=`docs/reviews/p5-s2-plan-rereview-controller-20260520.md`；3 个 plan finding 均关闭；当前 gate 为 `P5-S2 implementation`，下一 gate 为 `P5-S2 code review` |
| 2026-05-20 | P5-S2 implementation | 🟡 completed | implementation artifact=`docs/reviews/p5-s2-implementation-20260520.md`；新增 `score.json.fund_quality`、FQ1 App 类别冲突、FQ4 snapshot 缺失率、FQ5 preferred_lens resolvability 与结构化 issue metadata；当前验证 targeted `36 passed`、full suite `184 passed`、ruff passed、diff check passed；当前 gate 为 `P5-S2 implementation completed`，下一 gate 为 `P5-S2 code review` |
| 2026-05-20 | P5-S2 code review/fix | ✅ passed after fix | controller code review artifact=`docs/reviews/code-review-p5-s2-20260520.md`；已修复 FQ5 派生路径没有随 App 类别冲突变成 mismatch 的问题；当前验证 targeted `37 passed`、ruff passed、diff check passed；当前 gate 为 `P5-S2 code review passed after fix`，下一 gate 为 `P5-S2 acceptance / aggregate readiness` |
| 2026-05-20 | P5-S2 acceptance reconciliation | ✅ accepted | controller 裁决=`docs/reviews/p5-s2-acceptance-reconciliation-20260520.md`；P4-R9 关闭，FQ1 App 类别冲突、FQ4 snapshot 缺失率、FQ5 preferred_lens resolvability 已接入 quality gate；当前验证 full suite `185 passed`、ruff passed、diff check passed；当前 gate 为 `P5-S2 accepted`，下一 gate 为 `P5-S3 snapshot sub-field exposure plan/review` |
| 2026-05-20 | P5-S3 snapshot sub-field exposure plan | 🟡 drafted | plan artifact=`docs/reviews/p5-s3-snapshot-sub-field-exposure-plan-20260520.md`；计划通过 snapshot `comparable_values` 白名单扩大 correctness denominator，首版覆盖结构化稳定 P0 子字段；当前 gate 为 `P5-S3 snapshot sub-field exposure plan drafted`，下一 gate 为 `P5-S3 plan review` |
| 2026-05-20 | P5-S3 plan review/fix | 🟡 patched | controller plan review artifact=`docs/reviews/p5-s3-plan-review-controller-20260520.md`；已明确只有白名单字段/子字段的明确缺失才能 mismatch，并补充 `benchmark_name` 从 `benchmark_text` 的字段内 alias 策略；当前 gate 为 `P5-S3 plan patched after controller review`，下一 gate 为 `P5-S3 plan re-review` |
| 2026-05-20 | P5-S3 plan re-review | ✅ passed | controller re-review artifact=`docs/reviews/p5-s3-plan-rereview-controller-20260520.md`；2 个 plan finding 均关闭；当前 gate 为 `P5-S3 implementation`，下一 gate 为 `P5-S3 code review` |
| 2026-05-20 | P5-S3 implementation | 🟡 completed | implementation artifact=`docs/reviews/p5-s3-implementation-20260520.md`；新增 snapshot `comparable_values` 白名单子字段与 correctness 索引扩展，保留旧 snapshot 分类兼容并区分白名单缺失和 unavailable；当前验证 targeted `43 passed`、full suite `187 passed`、ruff passed、diff check passed；当前 gate 为 `P5-S3 code review`，下一 gate 为 `P5-S3 acceptance / aggregate readiness` |
| 2026-05-20 | P5-S3 code review | ✅ passed | controller code review artifact=`docs/reviews/code-review-p5-s3-20260520.md`；无 blocking finding；RR-16 部分关闭，后续不再阻断 failure accounting；当前 gate 为 `P5-S3 acceptance / aggregate readiness`，下一 gate 为 `P5-S4 snapshot failure accounting plan/review` |
| 2026-05-20 | P5-S4 snapshot failure accounting plan | 🟡 drafted | plan artifact=`docs/reviews/p5-s4-snapshot-failure-accounting-plan-20260520.md`；计划把 `errors.jsonl` 中的 failed funds 显式带入 `score.json.failed_funds` 并由 quality gate FQ6 阻断；当前 gate 为 `P5-S4 plan review`，下一 gate 为 `P5-S4 plan re-review` |
| 2026-05-20 | P5-S4 plan review/fix | 🟡 patched | controller plan review artifact=`docs/reviews/p5-s4-plan-review-controller-20260520.md`；已补充 writer 不读文件、loader 校验和 `--errors-path` 文档要求；当前 gate 为 `P5-S4 plan patched after controller review`，下一 gate 为 `P5-S4 plan re-review` |
| 2026-05-20 | P5-S4 plan re-review | ✅ passed | controller re-review artifact=`docs/reviews/p5-s4-plan-rereview-controller-20260520.md`；3 个 plan finding 均关闭；当前 gate 为 `P5-S4 implementation`，下一 gate 为 `P5-S4 code review` |
| 2026-05-20 | P5-S4 implementation | 🟡 completed | implementation artifact=`docs/reviews/p5-s4-implementation-20260520.md`；新增 `score.json.failed_funds` 与 quality gate `FQ6/block`，`extraction-score` 显式支持 `--errors-path`；当前验证 targeted `36 passed`、full suite `191 passed`、ruff passed、diff check passed；当前 gate 为 `P5-S4 code review`，下一 gate 为 `P5-S4 acceptance / aggregate readiness` |
| 2026-05-20 | P5-S4 code review | ✅ passed | controller code review artifact=`docs/reviews/code-review-p5-s4-20260520.md`；无 blocking finding；完全失败基金 accounting 已由 `failed_funds` / FQ6 收口；当前 gate 为 `P5-S5 share_change hardening plan/review`，下一 gate 为 `P5-S5 plan review` |
| 2026-05-20 | P5-S5 share_change hardening plan | 🟡 drafted | plan artifact=`docs/reviews/p5-s5-share-change-hardening-plan-20260520.md`；计划显式选择 share_change 份额列，拒绝 fund_code 尾号推断；当前 gate 为 `P5-S5 plan review`，下一 gate 为 `P5-S5 plan re-review` |
| 2026-05-20 | P5-S5 plan review/fix | 🟡 patched | controller plan review artifact=`docs/reviews/p5-s5-plan-review-controller-20260520.md`；已移除 A/C 尾号推断、补充 total-column 行为和稳定 metadata reason；当前 gate 为 `P5-S5 plan patched after controller review`，下一 gate 为 `P5-S5 plan re-review` |
| 2026-05-20 | P5-S5 plan re-review | ✅ passed | controller re-review artifact=`docs/reviews/p5-s5-plan-rereview-controller-20260520.md`；3 个 plan finding 均关闭；当前 gate 为 `P5-S5 implementation`，下一 gate 为 `P5-S5 code review` |
| 2026-05-20 | P5-S5 implementation | 🟡 completed | implementation artifact=`docs/reviews/p5-s5-implementation-20260520.md`；新增 share_change 显式份额列选择，拒绝尾号推断和歧义首列 fallback；当前验证 targeted `30 passed`、full suite `194 passed`、ruff passed、diff check passed；当前 gate 为 `P5-S5 code review`，下一 gate 为 `P5-S5 acceptance / aggregate readiness` |
| 2026-05-20 | P5-S5 code review/fix | ✅ passed after fix | controller code review artifact=`docs/reviews/code-review-p5-s5-20260520.md`；已修复 A 类 fallback 忽略其他代码表头的问题；当前验证 targeted `31 passed`、full suite `195 passed`、ruff passed、diff check passed；当前 gate 为 `P5-S6 user/App source reconciliation`，下一 gate 为 `P5-S7 post-MVP infra validation plan/review` |
| 2026-05-20 | P5-S6 user/App source reconciliation | 🟡 blocked-on-human | artifact=`docs/reviews/p5-s6-user-app-source-reconciliation-20260520.md`；确认 `016492` 重复需要用户/App 源裁决，当前不自动修改 `docs/code_20260519.csv`；RR-13 保持 human-owned；当前 gate 为 `P5-S7 post-MVP infra validation plan/review`，下一 gate 为 `P5-S7 plan review` |
| 2026-05-20 | P5-S7 post-MVP infra validation plan | ✅ passed | plan artifact=`docs/reviews/p5-s7-post-mvp-infra-validation-plan-20260520.md`；controller review/rereview artifacts=`docs/reviews/p5-s7-plan-review-controller-20260520.md`, `docs/reviews/p5-s7-plan-rereview-controller-20260520.md`；计划接受 read-only thermometer Service/CLI、`--json` 输出、unavailable exit 0、smoke 显式 `--quality-gate-policy warn`；当前 gate 为 `P5-S7 implementation`，下一 gate 为 `P5-S7 code review` |
| 2026-05-20 | P5-S7 implementation/code review | ✅ passed | implementation artifact=`docs/reviews/p5-s7-implementation-20260520.md`；controller code review artifact=`docs/reviews/code-review-p5-s7-20260520.md`；新增 read-only thermometer Service/CLI，真实 smoke 显式 warn 策略；当前验证 targeted `32 passed`、full suite `200 passed`、ruff passed、diff check passed；当前 gate 为 `P5 aggregate readiness reconciliation`，下一 gate 为 `P5 aggregate deepreview` |
| 2026-05-20 | P5 aggregate readiness reconciliation | ✅ accepted | artifact=`docs/reviews/p5-aggregate-readiness-reconciliation-20260520.md`；P5 可进入 aggregate deepreview；RR-13 duplicate `016492` 保持 human-owned；当前 gate 为 `P5 aggregate deepreview`，下一 gate 为 `P5 aggregate review judgment` |
| 2026-05-20 | P5 aggregate deepreview/fix | ✅ passed after fix | controller judgment=`docs/reviews/p5-aggregate-deepreview-controller-judgment-20260520.md`；AgentCodex/AgentDS findings 均已裁决并修复；当前验证 targeted `53 passed`、full suite `206 passed`、ruff passed、diff check passed；当前 gate 为 `P5 aggregate re-review / acceptance`，下一 gate 为 `P5 acceptance / ready-to-open-draft-PR reconciliation` |
| 2026-05-20 | P5 aggregate targeted re-review | ✅ accepted | artifact=`docs/reviews/p5-aggregate-rereview-controller-acceptance-20260520.md`；AgentCodex/AgentDS targeted re-review 均 PASS；当前验证 full suite `206 passed`、ruff passed、diff check passed；当前 gate 为 `P5 acceptance / ready-to-open-draft-PR reconciliation`，下一 gate 为 `ready-to-open-draft-PR` |
| 2026-05-20 | P5 acceptance / ready-to-open-draft-PR reconciliation | ✅ accepted | artifact=`docs/reviews/p5-acceptance-ready-to-open-draft-pr-reconciliation-20260520.md`；PR inclusion/exclusion set 已明确；当前 gate 为 `ready-to-open-draft-PR`，下一 gate 为 `draft PR gate（需用户授权）` |
| 2026-05-20 | P5 draft PR gate | ✅ draft-PR-pass | Draft PR 4 已创建：`https://github.com/bill20232033cc/fund-agent/pull/4`；controller reconciliation=`docs/reviews/p5-draft-pr-gate-reconciliation-20260520.md`；PR-level review=`docs/reviews/pr-4-review-20260520-0625.md`；GitHub state=`OPEN`、draft=`true`、mergeable=`MERGEABLE`、no checks reported；下一 gate 为 `merge gate（需用户额外授权）` |
| 2026-05-20 | P5 merge gate | ✅ merged | PR 4 已 squash merge 到 `main`：`https://github.com/bill20232033cc/fund-agent/pull/4`；merge commit=`d33b901fd1bee9f85206df461cc6419a813bcbae`，mergedAt=`2026-05-19T22:51:32Z`；本地 `main` 已 fast-forward 到 `origin/main`；下一 gate 为 `post-P5 follow-up planning` |
| 2026-05-20 | post-P5 follow-up planning | ✅ accepted | controller 裁决下一阶段第一优先级为 P6-S1 template contract manifest；artifact=`docs/reviews/post-p5-follow-up-planning-20260520.md`；当前 gate 为 `post-P5 follow-up planning accepted`，下一 gate 为 `P6-S1 template contract manifest plan/review` |
| 2026-05-20 | P6-S1 template contract manifest plan | 🟡 drafted | plan artifact=`docs/reviews/p6-s1-template-contract-manifest-plan-20260520.md`；计划首版在 Capability 层维护 typed Python manifest，覆盖 0-7 章 CHAPTER_CONTRACT，不运行时解析 Markdown 注释，不实现 ITEM_RULE / contract audit / FQ5 upgrade；当前 gate 为 `P6-S1 template contract manifest plan drafted`，下一 gate 为 `P6-S1 plan review` |
| 2026-05-20 | P6-S1 plan review/fix/rereview | ✅ passed | controller plan review=`docs/reviews/p6-s1-plan-review-controller-20260520.md` 发现 renderer 私有标题常量耦合风险；plan 已修订并由 re-review=`docs/reviews/p6-s1-plan-rereview-controller-20260520.md` 确认关闭；当前 gate 为 `P6-S1 implementation`，下一 gate 为 `P6-S1 code review` |
| 2026-05-20 | annual report source strategy reconciliation | 🟡 tracked | 接受 AgentCodex 建议方向：EID/证监会资本市场电子化信息披露平台作为后续主源，天天基金/Eastmoney fallback，巨潮不作为公募基金年报主源；artifact=`docs/reviews/annual-report-source-strategy-reconciliation-20260520.md`；新增 RR-18 / P7 data-source migration，不阻塞 P6-S1 |
| 2026-05-20 | P6-S1 implementation/code review | ✅ passed after fix | implementation owner=AgentCodex；controller 裁决=`docs/reviews/p6-s1-code-review-controller-judgment-20260520.md`；MiMo/GLM reviews=`docs/reviews/code-review-20260520-130008.md`,`docs/reviews/code-review-20260520-125906.md`；新增 `fund_agent/fund/template/contracts.py`、template contract public exports、contract tests 和 README 同步；lens key / `fund_type` mismatch 测试覆盖缺口已修复；当前验证 targeted `7 passed`、full suite `213 passed`、ruff passed、diff check passed；当前 gate 为 `P6-S1 acceptance / next slice planning`，下一 gate 为 `P6-S2 plan/review` |
| 2026-05-20 | P6-S2 renderer contract alignment plan | ✅ passed | plan artifact=`docs/reviews/p6-s2-renderer-contract-alignment-plan-20260520.md`；controller review/rereview=`docs/reviews/p6-s2-plan-review-controller-20260520.md`,`docs/reviews/p6-s2-plan-rereview-controller-20260520.md`；计划限定本 slice 只做 renderer 标题真源收口、`RenderedChapterBlock` 和 Markdown chapter split helper，不做 ITEM_RULE / contract audit / FQ5 upgrade；当前 gate 为 `P6-S2 implementation`，下一 gate 为 `P6-S2 code review` |
| 2026-05-20 | P6-S2 implementation/code review | ✅ passed after fix | implementation owner=AgentCodex；controller 裁决=`docs/reviews/p6-s2-code-review-controller-judgment-20260520.md`；MiMo/GLM reviews=`docs/reviews/code-review-20260520-134053.md`,`docs/reviews/code-review-20260520-134023.md`；renderer 标题来源已收口到 `CHAPTER_CONTRACT` manifest，新增 `RenderedChapterBlock`、public heading helper、fail-closed chapter splitter 和 `TemplateRenderResult.chapter_blocks`；混入非法一级标题测试覆盖缺口已修复；当前验证 targeted `29 passed`、full suite `221 passed`、ruff passed、diff check passed；当前 gate 为 `P6-S2 acceptance / next slice planning`，下一 gate 为 `P6-S3 plan/review` |
| 2026-05-21 | P8-S3 source fallback policy implementation | ✅ accepted | controller self-review 通过；五类 taxonomy、table-driven fallback eligibility、结构化阻断异常、PDF 完整性异常、provenance 保留均符合计划验收标准；当前验证 `347 passed`、ruff passed；implementation commit=`93ae6ea` |
| 2026-05-21 | post-P8-S3 follow-up planning | ✅ accepted | P8 三个核心交付物（must_answer audit / preferred_lens / source fallback）均已完成；artifact=`docs/reviews/post-p8-s3-follow-up-planning-20260521.md`；P8-S4 preflight quality gate 和 open repo findings (003/005/006) deferred 到 post-P8；当前 gate 为 `P8 aggregate readiness reconciliation`，下一 gate 为 `P8 closed` |
| 2026-05-21 | P8 closed | ✅ done | P8 三个核心交付物全部完成；AgentController 后续提交 audit hardening (`90bb9d2`)、fund_type bond guard (`90bb9d2`)、preflight quality gate (`90bb9d2`)、docs/infra sync；controller 修复 finding 005（CSV ValueError/FNFE 分离）和 finding 006（alpha observations MVP 注释），commit=`b4aaaaa`；当前验证 `347 passed`、ruff passed；当前 gate 为 `P8 closed`，下一 gate 为 `post-P8 planning` |
| 2026-05-21 | post-P8 planning | ✅ accepted | controller 裁决 P9 第一优先级为 `analyze` 产品契约加固，artifact=`docs/reviews/post-p8-planning-20260521.md`；近期收口包括移除外部 `dayu-agent` 依赖、刷新 `uv.lock`、对齐 `AGENTS.md`/`CLAUDE.md`、明确第 5/6 章模板边界；Procodex/AgentCodex 网络问题时 AgentMiMo 可作为 planning/implementation 替补，但同 slice review 改用 AgentDS + AgentGLM；当前 gate 为 `post-P8 planning accepted`，下一 gate 为 `P9-S1 analyze product contract plan/review` |
| 2026-05-21 | P9-S1 analyze product contract plan/review | ✅ accepted | plan artifact=`docs/reviews/p9-s1-analyze-product-contract-plan-20260521.md`；controller judgment=`docs/reviews/p9-s1-plan-review-controller-judgment-20260521.md`；MiMo/DS re-review artifacts 均 PASS；计划接受 product 最小输入、developer override nested contract、Capability-owned final judgment policy、Service quality gate state machine 和 R2 audit conflict contract；当前 gate 为 `P9-S1 implementation`，下一 gate 为 `P9-S1 code review` |
| 2026-05-21 | P9-S1 implementation/code review | ✅ accepted | implementation commit=`2bacdb3`；implementation artifact=`docs/reviews/p9-s1-implementation-20260521.md`；MiMo/DS code review 均为 `PASS_WITH_FINDINGS` 且无阻断；controller judgment=`docs/reviews/p9-s1-code-review-controller-judgment-20260521.md`；当前验证 full suite `365 passed`、ruff passed、diff check passed；当前 gate 为 `P9-S1 accepted`，下一 gate 为 `post-P9-S1 follow-up planning` |
| 2026-05-21 | post-P9-S1 follow-up planning | ✅ accepted | controller 裁决下一阶段第一优先级为 P9-S2 quality gate / golden coverage calibration；artifact=`docs/reviews/post-p9-s1-follow-up-planning-20260521.md`；当前 gate 为 `post-P9-S1 follow-up planning accepted`，下一 gate 为 `P9-S2 quality gate / golden coverage calibration plan/review` |
| 2026-05-21 | P9-S2 quality gate / golden coverage plan/review | ✅ accepted | plan artifact=`docs/reviews/p9-s2-quality-gate-golden-coverage-plan-20260521.md`；controller judgment=`docs/reviews/p9-s2-plan-review-controller-judgment-20260521.md`；MiMo/DS reviews and re-reviews all accepted；当前 gate 为 `P9-S2 implementation`，下一 gate 为 `P9-S2 code review` |
| 2026-05-21 | P9-S2 implementation/code review | ✅ accepted with review limitation | implementation commit=`ce603a0`；implementation artifact=`docs/reviews/p9-s2-implementation-20260521.md`；controller judgment=`docs/reviews/p9-s2-code-review-controller-judgment-20260521.md`；实现将 strict golden coverage absence 校准为 `FQ0/info` 而非 `gate_not_run`，保留 mismatch `FQ1/block`，并补齐 unavailable coverage metadata fail-closed 测试；当前验证 targeted `78 passed`、full suite `377 passed`、ruff passed、diff check passed；独立 Agent code review artifact 未产出，原因已记录为 DS compacting 卡住、GLM 401、Codex/MiMo 参与实现；当前 gate 为 `P9-S2 accepted`，下一 gate 为 `post-P9-S2 follow-up planning` |
| 2026-05-21 | post-P9-S2 follow-up planning | ✅ accepted | artifact=`docs/reviews/post-p9-s2-follow-up-planning-20260521.md`；P9-S1/P9-S2 已关闭产品契约核心缺口；不再开新 P9 功能 slice，下一步进入 P9 aggregate readiness/deepreview；P9-S2 review limitation 作为 aggregate risk 输入；当前 gate 为 `post-P9-S2 follow-up planning accepted`，下一 gate 为 `P9 aggregate readiness reconciliation` |
| 2026-05-21 | P9 aggregate readiness reconciliation | 🟡 ready but blocked | artifact=`docs/reviews/p9-aggregate-readiness-reconciliation-20260521.md`；P9 功能态可进入 aggregate deepreview，但 reviewer availability 阻塞：AgentDS 未产出 durable review artifact，AgentGLM 401，AgentCodex/AgentMiMo 参与实现；下一步需恢复 AgentDS/AgentGLM 或用户接受单 reviewer / controller-only 风险例外 |
| 2026-05-21 | P9 aggregate deepreview | ✅ accepted | controller judgment=`docs/reviews/p9-aggregate-deepreview-controller-judgment-20260521.md`；AgentDS review=`docs/reviews/p9-aggregate-deepreview-ds-20260521.md` 为独立 PASS；AgentMiMo review=`docs/reviews/p9-aggregate-deepreview-mimo-20260521.md` 为 PASS with reviewer limitation；controller 拒绝两个非阻断 finding（README 已含 `no_comparable_fields`，`AuditRuleCode` 已含 `C2`）；当前 gate 为 `P9 aggregate deepreview accepted`，下一 gate 为 `post-P9 follow-up planning` |
| 2026-05-21 | post-P9 follow-up planning | ✅ accepted | artifact=`docs/reviews/post-p9-follow-up-planning-20260521.md`；P9 关闭后不继续扩产品功能，下一阶段进入 P10 repo hygiene / release readiness；首个 gate 为 `P10-S1 repo hygiene and release readiness plan/review`；control doc hygiene 后置，RR-13 仍需人工裁决 |
| 2026-05-21 | P10-S1 repo hygiene / release readiness plan/review | ✅ accepted with blocker | plan artifact=`docs/reviews/p10-s1-repo-hygiene-release-readiness-plan-20260521.md`；controller judgment=`docs/reviews/p10-s1-plan-review-controller-judgment-20260521.md`；AgentDS/AgentMiMo plan reviews 均为 pass-with-risks；中风险项已通过 plan revision 收口为 implementation guardrails；当前 gate 为 `P10-S1 plan/review accepted with implementation blocker`，下一 gate 为 `P10-S1 implementation`，实施前必须确认 MIT License copyright holder |
| 2026-05-21 | P10-S1 implementation/code review | ✅ accepted | implementation artifact=`docs/reviews/p10-s1-implementation-20260521.md`；controller judgment=`docs/reviews/p10-s1-code-review-controller-judgment-20260521.md`；MiMo/GLM code reviews 均 PASS；新增 MIT LICENSE、CI、`.gitignore` artifact policy、`fund_agent.config.paths`、路径迁移守卫测试和 README 同步；当前验证 full suite `388 passed`、ruff passed、diff check passed、`uv lock --check` passed；当前 gate 为 `P10-S1 code review accepted`，下一 gate 为 `P10 aggregate readiness reconciliation` |
| 2026-05-21 | P10 aggregate readiness reconciliation | ✅ accepted | artifact=`docs/reviews/p10-aggregate-readiness-reconciliation-20260521.md`；P10-S1 可进入 aggregate deepreview；repo-audit suggestions 已裁决为 closed/deferred/follow-up，`fund_agent/fund/tools/` 空目录和 repo-audit artifact inclusion 留给 aggregate/follow-up；当前 gate 为 `P10 aggregate readiness accepted`，下一 gate 为 `P10 aggregate deepreview` |
| 2026-05-21 | P10 aggregate deepreview | ✅ accepted | controller judgment=`docs/reviews/p10-aggregate-deepreview-controller-judgment-20260521.md`；MiMo/GLM aggregate reviews 均 PASS；无阻断 finding，确认 release-readiness diff 不改变 analyze / quality gate / renderer / audit / Fund Capability 规则；当前 gate 为 `P10 aggregate deepreview accepted`，下一 gate 为 `ready-to-open-draft-PR reconciliation` |
| 2026-05-21 | P10 acceptance / ready-to-open-draft-PR reconciliation | ✅ accepted | artifact=`docs/reviews/p10-acceptance-ready-to-open-draft-pr-reconciliation-20260521.md`；P10 PR inclusion/exclusion set 已明确，repo-audit 输入和本地 `.docx` 排除；accepted local commit=`e9b622d`；当前 gate 为 `ready-to-open-draft-PR`，下一 gate 为 `draft PR gate（需用户授权）` |
| 2026-05-21 | P10 draft PR gate | ✅ draft-PR-pass | Draft PR 6 已创建：`https://github.com/bill20232033cc/fund-agent/pull/6`；branch=`p10-release-readiness`，head=`eb43dc3`；controller reconciliation=`docs/reviews/p10-draft-pr-gate-reconciliation-20260521.md`；PR-level reviews `docs/reviews/pr-6-review-mimo-20260521.md`、`docs/reviews/pr-6-review-glm-20260521.md` 均无阻断 finding；GitHub state=`OPEN`、draft=`true`、mergeable=`MERGEABLE`，Actions run `26234941272` pass；初始 CI failure 已由 `eb43dc3` 修复；下一 gate 为 `merge gate（需用户额外授权）` |
| 2026-05-21 | P10 merge gate | ✅ merged | PR 6 已 squash merge 到 `main`：`https://github.com/bill20232033cc/fund-agent/pull/6`；merge commit=`acc692c7e84c855398de86497b0d05f30b6f5ca5`，mergedAt=`2026-05-21T15:39:33Z`；controller reconciliation=`docs/reviews/p10-merge-gate-reconciliation-20260521.md`；本地 `main` 已对齐 `origin/main`；pre-squash 本地线性历史保留在 `backup/p10-pre-squash-main`；当前 gate 为 `P10 merged`，下一 gate 为 `post-P10 follow-up planning` |
| 2026-05-21 | post-P10 follow-up planning | ✅ accepted | artifact=`docs/reviews/post-p10-follow-up-planning-20260521.md`；controller 裁决下一阶段优先做 P11 control doc hygiene / recovery ergonomics，先进入 plan/review，不改产品主链路；RR-13 继续 human-owned，`docs/repo-audit-20260521.md` 继续本地排除；当前 gate 为 `post-P10 follow-up planning accepted`，下一 gate 为 `P11-S1 control doc hygiene and recovery plan/review` |
| 2026-05-21 | P11-S1 control doc hygiene and recovery plan/review | ✅ accepted | plan artifact=`docs/reviews/p11-s1-control-doc-hygiene-recovery-plan-20260521.md`；controller judgment=`docs/reviews/p11-s1-plan-review-controller-judgment-20260521.md`；MiMo/GLM initial reviews 均为 `PASS_WITH_FINDINGS`，targeted re-review 均 `PASS`；计划接受 documentation-only same-file restructure，要求 Startup Packet + Active Gate Ledger <= 80 行、phase-prefixed unique archive anchors、artifact existence check 作为一次性 implementation acceptance gate；当前 gate 为 `P11-S1 plan accepted`，下一 gate 为 `P11-S1 implementation` |
| 2026-05-21 | P11-S1 implementation/code review | ✅ accepted | implementation artifact=`docs/reviews/p11-s1-implementation-20260521.md`；controller judgment=`docs/reviews/p11-s1-code-review-controller-judgment-20260521.md`；MiMo code review PASS，GLM code review PASS_WITH_FINDINGS；GLM F1 archive heading ambiguity 已修复为 historical snapshot，GLM F2 historical duplicate summary rows deferred；docs-only reorg 增加 Startup Packet、Active Gate Ledger、Phase History Index、Evidence Preservation Rules 和 Archive P0-P11 anchors；当前验证 diff check passed、artifact reference check passed、first-screen budget under 80 lines；当前 gate 为 `P11-S1 accepted`，下一 gate 为 `post-P11 follow-up planning` |
| 2026-05-21 | post-P11 follow-up planning | ✅ accepted | artifact=`docs/reviews/post-p11-follow-up-planning-20260521.md`；controller 裁决 P11-S1 已达成恢复目标，但历史 archive summary rows 仍有重复/陈旧表述，会降低后续 resume clarity；下一阶段继续保持 documentation-only，进入 `P11-S2 historical summary dedupe plan/review`；RR-13 duplicate `016492` 继续 human-owned，`docs/repo-audit-20260521.md` 继续排除，不启动产品功能 phase |
| 2026-05-21 | P11-S2 historical summary dedupe plan/review | ✅ accepted | plan artifact=`docs/reviews/p11-s2-historical-summary-dedupe-plan-20260521.md`；controller judgment=`docs/reviews/p11-s2-plan-review-controller-judgment-20260521.md`；MiMo/GLM initial reviews 均为 `PASS_WITH_FINDINGS`，targeted re-review 均 `PASS`；计划接受 documentation-only cleanup，限定清理 stale summary rows 和旧 current-gate wording，保护 `docs/implementation-control.md:234` 到 `docs/implementation-control.md:264` 详细证据链不被压缩；mandatory reference check 纳入 implementation acceptance；当前 gate 为 `P11-S2 historical summary dedupe plan accepted`，下一 gate 为 `P11-S2 implementation` |
| 2026-05-21 | P11-S2 implementation/code review | ✅ accepted | implementation artifact=`docs/reviews/p11-s2-implementation-20260521.md`；controller judgment=`docs/reviews/p11-s2-code-review-controller-judgment-20260521.md`；MiMo/GLM code reviews 均为 `PASS_WITH_FINDINGS`，唯一低风险 finding 为 Startup Packet 与 Active Residuals 对 historical duplicate summary rows 的临时不一致，controller 已在 acceptance bookkeeping 中移除 Startup Packet 残余项；docs-only cleanup 未压缩 `docs/implementation-control.md:234` 到 `docs/implementation-control.md:264` 证据链；当前验证 diff check passed、artifact reference check passed、mandatory reference check passed；当前 gate 为 `P11-S2 accepted`，下一 gate 为 `post-P11 follow-up planning` |
| 2026-05-22 | post-P11 follow-up planning | ✅ accepted | artifact=`docs/reviews/post-p11-second-follow-up-planning-20260522.md`；P11 control-doc recovery 已关闭，RR-13 duplicate `016492` 与 `docs/repo-audit-20260521.md` 均为非阻断 residual；controller 裁决下一阶段进入 P12 ITEM_RULE deterministic compliance，首个 gate 为 `P12-S1 ITEM_RULE renderer/audit compliance plan/review`；P12 非目标包括 LLM audit、Evidence Confirm、RepairContract、Host/Engine/tool loop、RR-13 自动修复和 repo-audit 发布 |
| 2026-05-22 | P12-S1 ITEM_RULE renderer/audit compliance plan/review | ✅ accepted | plan artifact=`docs/reviews/p12-s1-item-rule-renderer-audit-compliance-plan-20260522.md`；controller judgment=`docs/reviews/p12-s1-plan-review-controller-judgment-20260522.md`；MiMo/GLM initial reviews 均为 `PASS_WITH_FINDINGS`，targeted re-review 均 `PASS`；计划接受 renderer 产生 `item_rule_decisions` 与 `item_rule_audit_context`、audit 消费同一 tuple/context、FQ5 语义不扩张、固定 Markdown 段落和 evidence 边界；当前 gate 为 `P12-S1 ITEM_RULE renderer/audit compliance plan accepted`，下一 gate 为 `P12-S1 implementation` |
