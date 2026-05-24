# Release Maintenance Methodology Coverage Matrix Implementation

> Date: 2026-05-25
> Branch: `codex/v0-release-readiness-plan`
> Gate: `release-maintenance methodology coverage matrix design`
> Status: accepted locally

## Step Self-Check

- Current gate / role: controller docs-only design implementation.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md` Startup Packet, `docs/fund-analysis-template-draft.md`, `docs/reviews/release-maintenance-methodology-coverage-matrix-plan-20260525.md`.
- Scope boundary: design/control documentation only; no source, tests, renderer, Host/Agent package, dependency, report output, golden answer, or external GitHub action.
- Stop conditions: no current renderer rewrite, no 0-10 code implementation, no LLM audit implementation claim, no external `dayu-agent` runtime coupling.
- Evidence and validation: `docs/design.md` and control doc updated; `rg` check and `git diff --check` must pass.
- Next action: report accepted local checkpoint and leave next entry point at report-quality baseline / Fact-Evidence contract plan-review.

## Implemented Design

Added `docs/design.md` §5.4.3 as a true-source methodology coverage matrix.

The matrix connects:

- Morningstar due-diligence dimensions: People, Process, Parent, Price, Performance;
- Youzhiyouxing investor-behavior dimensions: R=A+B-C, fund type first, knowledge / emotion / willingness, four-money suitability, thermometer / valuation-state discipline, next minimal validation question;
- Dayu technical mechanism: CHAPTER_CONTRACT, preferred_lens, ITEM_RULE, chapter audit, repair / regenerate;
- fund-agent four-layer boundary: UI displays, Service selects scene and quality policy, Host remains future lifecycle gate, Agent-layer `fund_agent/fund` owns fund methodology and audit semantics.

## Matrix Content

- Current 8-chapter coverage table:
  - chapter-level decision question;
  - Morningstar coverage;
  - Youzhiyouxing coverage;
  - CHAPTER_CONTRACT emphasis;
  - missing-fact degradation semantics.
- Fund type lens priority table:
  - `active_fund`;
  - `index_fund`;
  - `enhanced_index`;
  - `bond_fund`;
  - `qdii_fund`;
  - `fof_fund`.
- Evidence-source hierarchy:
  - regulatory/fund disclosures;
  - official index/regulatory sources;
  - manager interviews / public letters;
  - third-party ratings / peer data / valuation tools.
- Current 8-chapter to future 0-10 mapping boundary:
  - current renderer remains 8 chapters;
  - future Chapter 0 and Chapter 10 ordering is accepted as design;
  - detailed 0-10 implementation remains a later gate.

## Non-Changes

- No source code changed.
- No tests changed.
- No renderer behavior changed.
- No quality gate semantics changed.
- No Host/Agent package or dependency introduced.
- No `dayu.host` / `dayu.engine` runtime integration added.
- No local report artifact or golden answer added.

## Residual Risks

- Concrete report-quality scoring schema remains the next plan/review gate.
- Small representative baseline corpus remains the next plan/review gate.
- Current 8-chapter to future 0-10 exact chapter split remains a future implementation design gate.
- The two local research notes remain inputs only, not true-source architecture documents unless separately curated.

## Validation

```text
rg -n "Morningstar|有知有行|方法论覆盖矩阵|基金类型|CHAPTER_CONTRACT|0-10" docs/design.md docs/implementation-control.md docs/reviews/release-maintenance-methodology-coverage-matrix-implementation-20260525.md
git diff --check
```

Result: passed.

## Next Entry Point

`release-maintenance report-quality baseline / Fact-Evidence contract candidate selection / plan-review`
