# Release Maintenance Chapter-Audit Report Pipeline Design Plan

> Date: 2026-05-24
> Branch: `codex/v0-release-readiness-plan`
> Gate: `release-maintenance chapter-audit report pipeline design plan/review`
> Plan status: ready for plan review

## Step Self-Check

- Current gate / role: current gate is design plan/review; this artifact is the planning deliverable for a future document-only design implementation.
- Source of truth: `AGENTS.md`, `docs/design.md` §5.4/§12, `docs/implementation-control.md` Startup Packet, and `docs/reviews/release-maintenance-chapter-audit-report-pipeline-candidate-20260524.md`.
- Scope boundary: design artifacts only; no source, tests, CLI, renderer, Host/Agent package, dependency, quality gate, golden answer, or run-output changes in this gate.
- Stop conditions: no blocking open question found; PR #15 disposition and external GitHub actions remain separate user-authorized work.
- Evidence and validation: completion requires a reviewed design plan artifact, plan review artifact, controller judgment, control-doc update, and `git diff --check`.
- Next action: plan review, then controller judgment; if accepted, next entry point is `release-maintenance chapter-audit report pipeline design implementation`.

## Goal

Turn the accepted report-quality candidate into a concrete design implementation plan for a future chapter-level writing / audit / repair report pipeline.

The design target is to improve report quality without weakening the current v0 deterministic production path:

```text
Evidence / Fact Store
  -> Chapter 1-9 writing
  -> chapter rule audit
  -> chapter LLM audit
  -> patch / regenerate / accept
  -> Chapter 10 final judgment from accepted Chapter 1-9 conclusions
  -> Chapter 0 summary from accepted Chapter 1-10 conclusions
  -> report assembly audit
  -> report output
```

## Direct Evidence

- `docs/design.md` §5.4 already captures the chapter-level writing audit loop as a design candidate and explicitly says current `fund-analysis analyze` remains the v0 deterministic 8-chapter renderer.
- `docs/design.md` §12 requires every future plan review to check four-layer boundaries, `FundDocumentRepository` access, no hidden `extra_payload`, Host=`dayu.host`, Agent engine=`dayu.engine`, pyproject baseline, coverage policy, and verifiable success signals.
- `AGENTS.md` requires fund-document access through the document repository, Agent-layer ownership for CHAPTER_CONTRACT / preferred_lens / ITEM_RULE / audit rules, and no direct buy/sell or unsupported future-return claims.
- `docs/reviews/release-maintenance-chapter-audit-report-pipeline-candidate-20260524.md` accepts this as the next design candidate and forbids changing the v0 renderer, Host/Agent packages, Dayu runtime, quality gate semantics, or run artifacts.

## Scope

Allowed next implementation files:

- `docs/design.md`
- `docs/implementation-control.md`
- `fund_agent/fund/README.md`, only if needed to document the Fund package boundary between current v0 renderer and future chapter-audit pipeline
- `docs/reviews/` gate artifacts

The design implementation must promote §5.4 from a candidate direction into an accepted design contract for future work. It should make implementation agents able to distinguish:

- what is current v0 behavior;
- what is accepted future design;
- what remains blocked behind later code gates.

## Non-Goals

- Do not modify `fund_agent/`, `tests/`, `pyproject.toml`, `uv.lock`, `.github/`, `reports/golden-answers/`, or runtime configuration in this design gate.
- Do not rewrite current 8-chapter renderer into a 0-10 chapter pipeline.
- Do not declare LLM audit, Evidence Confirm, repair loop, or chapter-level regenerate implemented.
- Do not create `fund_agent/host` or `fund_agent/agent` placeholder packages.
- Do not add `dayu.host`, `dayu.engine`, LLM SDKs, prompt manifests, queues, or new production dependencies.
- Do not change quality gate `block/warn/off`, final judgment derivation, golden answer policy, or 004393 smoke scope.
- Do not submit local report/run artifacts.

## Design Decisions To Implement

1. Current v0 path remains authoritative production behavior.
   `fund-analysis analyze` continues to use UI -> Service -> `fund_agent/fund`, deterministic structured extraction, deterministic template rendering, programmatic audit, and quality gate.

2. The future chapter-audit pipeline is Agent-layer fund capability design.
   It may later be invoked by Service, but its fund-domain facts, CHAPTER_CONTRACT handling, ITEM_RULE handling, evidence anchoring, audit rules, and report-writing semantics belong in `fund_agent/fund`.

3. Host/Agent runtime stays behind a separate gate.
   If future work needs session/run/cancel/resume/outbox, chapter task concurrency, tool loop, runner, ToolRegistry, ToolTrace, or context budget, that future gate must introduce Host=`dayu.host` and Agent engine=`dayu.engine` explicitly.

4. Facts must be repository-derived.
   LLM writing, LLM audit, repair, and assembly must not read PDF files, caches, concrete source helpers, or external adapters directly. They may only consume structured facts and evidence derived through `FundDocumentRepository` / existing extractor boundaries.

5. Chapter state machine is fail-closed.
   A chapter cannot become accepted until both rule audit and LLM audit pass. Missing facts produce explicit data gaps, not fabricated prose. Repair must classify patch vs regenerate and must re-run audit.

6. Chapter dependency order is fixed.
   Chapters 1-9 write independently from facts/evidence. Chapter 10 consumes only accepted Chapter 1-9 structured conclusions plus quality gate state. Chapter 0 is generated last and consumes only accepted Chapter 1-10 conclusions.

7. Assembly audit is required.
   Final report output must have a whole-report consistency audit that can route failures back to a specific chapter or assembly rule.

8. Current 8-chapter to future 0-10 mapping remains a design implementation topic, not a code change.
   The next document-only implementation should record the mapping boundary and identify the first future code gate that may prototype contracts.

## Proposed Next Implementation Slice

### S1: Promote Design Candidate To Accepted Design Contract

Allowed files:

- `docs/design.md`
- `docs/implementation-control.md`
- optional: `fund_agent/fund/README.md`
- `docs/reviews/`

Required changes:

- Update `docs/design.md` §5.4 wording from candidate-only to accepted future design direction while preserving the explicit current-v0 disclaimer.
- Add concise invariants for chapter inputs, audit pass conditions, repair decisions, accepted chapter locking, final judgment ordering, and assembly audit.
- Add a boundary note that code implementation requires later gates and may not be smuggled into current renderer maintenance.
- If `fund_agent/fund/README.md` is updated, only document the current/future boundary; do not claim new APIs exist.
- Update `docs/implementation-control.md` with artifacts, current gate, next entry point, and archive row.

Validation:

```text
rg -n "chapter-audit|Chapter 10|Chapter 0|LLM audit|RepairDecision|dayu.host|dayu.engine|FundDocumentRepository" docs/design.md docs/implementation-control.md fund_agent/fund/README.md
git diff --check
```

No pytest is required unless production code, tests, runtime config, or README user commands change.

## Review Gates

Plan review must explicitly check:

- four-layer boundary and no hidden Host/Agent runtime introduction;
- `FundDocumentRepository`-only document access;
- no claim that LLM audit / Evidence Confirm / repair loop is currently implemented;
- no direct renderer rewrite or quality gate semantics change;
- no unsupported 0-10 chapter mapping decision presented as implementation fact;
- no hidden explicit parameters in `extra_payload`;
- no package/dependency baseline change.

## Residual Risks

- The exact 8-chapter to 0-10 mapping remains unresolved by design; the next implementation should record it as a future code-gate input rather than solve it prematurely.
- Current environment policy does not allow spawning sub-agents unless the user explicitly asks for sub-agents/parallel agent work; this gate uses controller fallback planning/review and records that limitation.
- Future LLM audit quality requires prompt, model, evidence bundle, and deterministic replay design that is intentionally out of scope for this plan/review gate.

## Completion Report Format

The next implementation artifact must report:

- changed files;
- design decisions implemented;
- current-v0 disclaimers preserved;
- future-code-gate boundaries;
- validation commands and results;
- residual risks and owners;
- next entry point.
