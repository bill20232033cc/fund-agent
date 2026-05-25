# Release Maintenance Chapter-Audit Report Pipeline Design Implementation

> Date: 2026-05-24
> Branch: `codex/v0-release-readiness-plan`
> Gate: `release-maintenance chapter-audit report pipeline design implementation`
> Status: accepted locally

## Step Self-Check

- Current gate / role: controller design implementation; this gate updates true-source documents only.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md` Startup Packet, `docs/reviews/release-maintenance-chapter-audit-report-pipeline-design-plan-20260524.md`, `docs/reviews/release-maintenance-chapter-audit-report-pipeline-design-plan-review-controller-judgment-20260524.md`.
- Scope boundary: design/control documentation only; no source, tests, renderer, Host/Agent package, dependency, quality gate, golden answer, report artifact, or GitHub state change.
- Stop conditions: if the design would require current renderer behavior changes, external `dayu-agent` runtime, Host/Agent package creation, or direct PDF/cache access outside `FundDocumentRepository`, stop and open a later gate.
- Evidence and validation: completion requires design/control diff review and `git diff --check`.
- Next action: finish docs update, run diff checks, then mark this design implementation accepted or record blockers.

## User Question

The user asked what `docs/dayu-agent-timeline-analysis.md` implies for current true-source design, and whether the project should first polish the fund-analysis template, iterate data acquisition scripts, or do something else.

## First-Principles Decision

Do not choose template polishing or data-source scripting as the first move.

The first move is to make report quality measurable and reproducible:

1. Define a small representative report-quality baseline corpus.
2. Define a report-quality scoring schema that can identify whether failures come from facts, extraction, evidence anchors, chapter contracts, final judgment, wording boundaries, or readability.
3. Define the Fact / Evidence input contract that chapter writing and auditing must consume.
4. Use the scoring results to decide whether the next code gate should prioritize data acquisition/extraction or template/writing improvements.

This follows the Dayu lesson that better report quality comes from clean, structured, low-noise facts and measurable evaluation, not from giving a model more raw documents or polishing prose blindly.

## Design Changes Implemented

- Promoted `docs/design.md` §5.4 from a design candidate to an accepted future design direction while preserving the explicit disclaimer that current `fund-analysis analyze` remains the v0 deterministic 8-chapter renderer.
- Added an explicit quality-improvement sequence: score/report baseline first, then data or template iteration based on observed failure categories.
- Added report-quality scoring dimensions:
  - fact coverage;
  - extraction correctness;
  - evidence traceability;
  - chapter contract completeness;
  - final judgment consistency;
  - investment-advice boundary;
  - readability and next minimal validation question.
- Added Fact / Evidence input contract for future chapter writing:
  - `facts`;
  - `derived_calculations`;
  - `evidence_anchors`;
  - `data_gaps`;
  - `quality_context`.
- Reaffirmed that LLM writing and audit may only consume structured facts and evidence derived through `FundDocumentRepository` boundaries.
- Updated `docs/implementation-control.md` Startup Packet, residual tracking, resume checklist, and active gate ledger to show this design implementation is in progress.

## External Dayu Runtime Boundary

This design intentionally learns from Dayu methodology but does not directly wire external `dayu-agent` runtime into fund-agent.

Direct external runtime coupling would mean calling an external Dayu runner, tool loop, Host/session manager, document parser, or report writer from fund-agent business paths in a way that bypasses this repository's `UI -> Service -> Host -> Agent` boundaries, `FundDocumentRepository`, quality gate, evidence anchors, and audit rules.

Accepted future integration shape remains:

- Host functionality, if needed, must be introduced through an explicit gate and use `dayu.host`.
- Agent execution/tool-loop functionality, if needed, must be introduced through an explicit gate and use `dayu.engine`.
- Fund-domain facts, evidence, CHAPTER_CONTRACT, preferred_lens, ITEM_RULE, audit rules, and report-writing semantics remain owned by this project's Agent-layer fund capability.

## Non-Changes

- No source code was changed.
- No tests were changed.
- No renderer behavior was changed.
- No quality gate semantics were changed.
- No Host/Agent package was created.
- No `dayu.host`, `dayu.engine`, LLM SDK, queue, prompt manifest, or production dependency was added.
- No local run artifact or golden answer was added.

## Residual Risks

- The exact 8-chapter to 0-10 mapping still needs a later design/code gate.
- The concrete report-quality score schema and sample-corpus rows are accepted as future implementation work, not implemented in this gate.
- LLM audit prompt/model/replay/repair semantics remain a later gate.
- PR #15 stale disposition remains user-authorized only and outside this gate.

## Validation

```text
rg -n "章节级写作审计闭环|报告质量评分|Fact / Evidence|dayu-agent runtime|FundDocumentRepository|dayu.host|dayu.engine" docs/design.md docs/implementation-control.md docs/reviews/release-maintenance-chapter-audit-report-pipeline-design-implementation-20260524.md
git diff --check
```

Result: passed.

## Next Entry Point

`release-maintenance report-quality baseline / Fact-Evidence contract candidate selection / plan-review`
