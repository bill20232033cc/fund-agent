# Release Maintenance Methodology Coverage Matrix Plan

> Date: 2026-05-25
> Branch: `codex/v0-release-readiness-plan`
> Gate: `release-maintenance methodology coverage matrix design`
> Plan status: accepted by controller for immediate docs-only implementation

## Step Self-Check

- Current gate / role: controller-scoped docs-only design gate.
- Source of truth: `AGENTS.md`, `docs/design.md` §5.4, `docs/implementation-control.md` Startup Packet, `docs/fund-analysis-template-draft.md`.
- Scope boundary: design/control documentation only; no source, tests, renderer, Host/Agent package, dependency, report output, golden answer, or GitHub action.
- Stop conditions: stop if the matrix would require rewriting current renderer, claiming LLM audit is implemented, changing current 8-chapter output, or introducing external Dayu runtime.
- Evidence and validation: completion requires `docs/design.md` matrix, control-doc gate bookkeeping, implementation artifact, `rg` verification, and `git diff --check`.
- Next action: implement matrix in true-source docs.

## Goal

Add a methodology coverage matrix that connects:

- Morningstar fund research pillars;
- Youzhiyouxing investor-behavior methodology;
- fund type specific `preferred_lens`;
- current 8-chapter `CHAPTER_CONTRACT` design;
- future Dayu-style chapter-writing / audit / repair pipeline.

The matrix must make the report template less like prose scaffolding and more like a decision-safety contract.

## Design Decisions

1. Keep current v0 report at 8 chapters.
   The matrix maps the current 0-7 chapter template and records future 0-10 expansion as a separate gate.

2. Treat Morningstar as professional due-diligence coverage.
   Use People / Process / Parent / Price / Performance as coverage lenses. Do not encode Morningstar medals or ratings as product output.

3. Treat Youzhiyouxing as investor behavior and holding-suitability coverage.
   Use R=A+B-C, fund type first, knowledge / emotion / willingness, four-money suitability, thermometer/valuation-state discipline, and next minimal validation question.

4. Treat Dayu as execution mechanics, not an external runtime dependency.
   Adopt CHAPTER_CONTRACT / preferred_lens / ITEM_RULE / chapter audit / repair semantics; do not call external `dayu-agent` runtime or bypass this repository's four-layer boundary.

5. Fund type controls chapter priority.
   Active funds prioritize People / Process / willingness. Index funds prioritize Process / Price / tracking. Bond funds prioritize risk controls. QDII and FOF require explicit cross-border or allocator-specific lenses.

6. Missing facts must degrade explicitly.
   The matrix must specify when a chapter writes `未披露 / 数据不足 / 下一步最小验证问题` instead of fabricating insight.

## Implementation Slice

Allowed files:

- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/release-maintenance-methodology-coverage-matrix-implementation-20260525.md`

Required changes:

- Add `docs/design.md` subsection after §5.4.2 for the methodology coverage matrix.
- Add chapter-to-methodology coverage table for current 8 chapters.
- Add fund-type lens priority matrix.
- Add evidence-source hierarchy and missing-fact degradation rules.
- Add future 0-10 mapping boundary.
- Update `docs/implementation-control.md` Startup Packet and Active Gate Ledger.

## Validation

```text
rg -n "Morningstar|有知有行|方法论覆盖矩阵|fund type|CHAPTER_CONTRACT|0-10" docs/design.md docs/implementation-control.md docs/reviews/release-maintenance-methodology-coverage-matrix-implementation-20260525.md
git diff --check
```

No pytest or ruff is required because this is documentation-only and changes no source/test/runtime behavior.
