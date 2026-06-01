# MVP truth pivot and context compaction gate plan

## 0. Gate metadata

- Gate: `MVP truth pivot and context compaction gate`
- Role: planning specialist only; not controller
- Date: 2026-05-30
- Classification: `heavy`
- Classification reason: this is docs-only, but it changes the control truth entry point and adds an accepted future route for MVP LLM report generation. It must protect architecture boundaries, Host/Agent/dayu policy, golden/promotion status, and future implementation sequencing.
- Output of this planning task: this plan artifact only.
- Controller-provided branch/status baseline: branch `codex/local-reconciliation`; no tracked dirty changes; unrelated untracked artifacts exist and must not be staged, deleted, referenced as evidence, or modified.

## 1. Goal

Pivot the repository truth surface from release-maintenance / golden-promotion blockers back to the MVP fund analysis report generation mainline, without changing runtime behavior, schema, score, snapshots, quality gates, golden fixtures, golden answers, or promotion state.

The gate must leave the next implementation agent with a short, unambiguous startup path:

- `docs/implementation-control.md` becomes a compact control plane.
- `docs/design.md` records Route C as accepted future design, not current implementation.
- `docs/current-startup-packet.md` becomes the short phaseflow startup entry.
- Release-maintenance and golden/coverage blockers remain preserved as residuals, not active blockers for MVP report generation.
- The next entry becomes `MVP Gate 1: facet_recognizer + ChapterFactProvider/FundToolService contract gate`.

## 2. Source truths already read

- `AGENTS.md`: execution rules, four-layer boundary, gate classification rules, document truth rules, FundDocumentRepository boundary, fallback taxonomy, explicit-parameter discipline, and report-analysis constraints.
- `docs/design.md`: current deterministic `fund-analysis analyze/checklist` path, UI -> Service -> `fund_agent/fund` transition path, no Host/Agent/dayu runtime, 8-chapter template, CHAPTER_CONTRACT, preferred_lens, ITEM_RULE, current deterministic renderer/audit/quality gate facts, and existing future LLM chapter-writing direction.
- `docs/implementation-control.md`: current control doc still points at release maintenance and `006597 same-fund unavailable field review / extractor projection gate`; release-maintenance artifacts and golden residuals are currently overrepresented in the startup surface.
- `docs/fund-analysis-template-draft.md`: template has 8 chapters, CHAPTER_CONTRACT, preferred_lens, ITEM_RULE-oriented instructions, and the facet catalog that Route C must consume.

## 3. Non-goals and hard boundaries

Do not modify:

- runtime code;
- schema, public API, score behavior, snapshot outputs, FQ0-FQ6 quality gate semantics, final judgment logic, renderer behavior, or CLI behavior;
- golden fixtures, golden-answer corpus, fixture promotion state, or promotion manifests;
- `AGENTS.md`;
- `docs/fund-analysis-template-draft.md`, unless the implementer proves the MVP route cannot be described without changing template truth; if so, stop instead of editing it;
- unrelated untracked files, historical artifacts, or stray files.

Do not:

- commit, push, create PR, stage files, delete files, or clean workspace;
- treat Route C as implemented;
- create `fund_agent/host` or `fund_agent/agent`;
- introduce `dayu.host` or `dayu.engine` dependencies before the explicit future Host/Agent/dayu gate;
- run promotion, fixture promotion, strict correctness reruns, snapshot refreshes, or full release-readiness workflows.

## 4. Accepted route decision to encode

User has accepted Route C:

1. Gate 1: `facet_recognizer + ChapterFactProvider/FundToolService contract and implementation`.
2. Gate 2: `chapter_writer + chapter_auditor`.
3. Gate 3: `chapter_orchestrator`, with a Service-layer write-audit-repair loop.
4. Gate 4: `final_chapter_assembler + chapter_0 + CLI --use-llm`.
5. Gate 5: optional `dayu.host` / `dayu.engine` integration that replaces the orchestrator concurrency layer.

Implementation framing:

- Route C is accepted future design for MVP LLM report generation.
- Current implementation remains deterministic `fund-analysis analyze/checklist`.
- Current CLI path remains UI -> Service, and Service directly calls `fund_agent/fund` public capabilities as a transition path.
- No LLM chapter writer, chapter auditor, chapter orchestrator, final LLM assembler, `--use-llm`, Host scheduling, Agent tool loop, or dayu runtime is currently implemented.
- Future Host must use `dayu.host`; future Agent execution kernel / tool loop / runner / ToolRegistry / ToolTrace must use `dayu.engine`.

## 5. Files to modify in implementation

The implementation agent for this gate may modify only:

- `docs/implementation-control.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- the implementation evidence artifact for this gate under `docs/reviews/`
- the controller judgment artifact for this gate under `docs/reviews/`, if and only if the controller specifically assigns that artifact creation to the implementation step

No other file is in scope.

## 6. Implementation slice A: compress `docs/implementation-control.md`

Replace the current long startup surface with a short control plane. Preserve historical traceability by linking to existing release-maintenance artifacts and archives, but remove long embedded ledgers from the active control surface.

Required front matter / header state:

- Current phase: `MVP fund analysis report generation phase`
- Current gate: `MVP truth pivot and context compaction gate`
- Current gate classification: `heavy`
- Next entry point: `MVP Gate 1: facet_recognizer + ChapterFactProvider/FundToolService contract gate`
- Next gate classification: `heavy` or `standard` only after controller classification; default to `heavy` if uncertain because Gate 1 defines a public contract between Service and Agent/Fund.
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Short startup entry: `docs/current-startup-packet.md`

Required Current Truth Guardrails:

- `AGENTS.md` remains highest-priority execution truth.
- Current implementation remains deterministic `fund-analysis analyze/checklist`.
- Current production path remains UI -> Service -> `fund_agent/fund` transition path.
- Route C is accepted future design only.
- Host/Agent/dayu is not implemented; future Host must use `dayu.host`; future Agent engine/tool loop must use `dayu.engine`.
- Service may assemble use cases, prompt/contract semantics, report generation strategy, and the write-audit-repair loop; Fund owns fund-type recognition, CHAPTER_CONTRACT/preferred_lens/ITEM_RULE, fact extraction, audit rules, and evidence anchoring.
- All explicit parameters must remain typed/declared; no `extra_payload` workaround.
- Production annual report access must remain through `FundDocumentRepository`.

Required Current Accepted Artifacts section:

- Keep this as a short table with only the artifacts needed to resume the MVP pivot.
- Include this plan path.
- Include the future implementation evidence and controller judgment paths as placeholders until produced.
- Include links to the existing release-maintenance roadmap / closeout / residual disposition artifacts only as evidence-chain summaries, not active gate truth.
- Do not paste long release-maintenance ledgers into the active control plane.

Required Open Residuals:

- `golden / strict correctness / QDII / FOF / 110020 / fixture promotion`: residual, not blocking MVP LLM report generation, and no promotion allowed without a separate future gate.
- `release maintenance long ledger`: preserved by archive/review links only.
- `Host/Agent/dayu runtime integration`: deferred to Route C Gate 5.
- `current deterministic renderer quality`: remains current production behavior until `--use-llm` is explicitly implemented.
- `untracked unrelated workspace files`: not part of accepted evidence unless a later controller gate explicitly accepts them.

Required Recent Active Gate Ledger:

- Keep only a compact ledger of this pivot gate plus a single summarized row for release-maintenance closeout.
- The ledger must not imply release maintenance is the current phase after this gate.

## 7. Implementation slice B: update `docs/design.md`

Add or update a clearly labeled section:

`已接受的未来设计：MVP LLM report generation route`

Required content:

- State that Route C is accepted future design.
- State that the current implementation is still deterministic `fund-analysis analyze/checklist`.
- State that current deterministic rendering is not being removed or redefined by this docs gate.
- State that no LLM chapter writing, LLM audit, write-audit-repair loop, `--use-llm`, Host scheduling, Agent runner/tool loop, or dayu runtime is implemented yet.
- Reaffirm UI -> Service -> Host -> Agent.
- Reaffirm current transition path: UI -> Service -> `fund_agent/fund`.
- Reaffirm Host/Agent/dayu discipline:
  - future Host must use `dayu.host`;
  - future Agent engine/tool loop/runner/ToolRegistry/ToolTrace must use `dayu.engine`;
  - Gate 5 is the only Route C step that may replace the custom orchestrator concurrency layer with dayu Host/Agent integration.

Route C design details to encode:

- Gate 1 creates `facet_recognizer` and the `ChapterFactProvider` / `FundToolService` contract and implementation.
- Gate 1 must consume existing template truth: 8 chapters, CHAPTER_CONTRACT, preferred_lens, ITEM_RULE, and facet catalog.
- Gate 1 must stay in Agent/Fund for fund-type/facet recognition and fact/evidence semantics; Service owns use-case orchestration and typed invocation.
- Gate 2 introduces `chapter_writer` and `chapter_auditor`, using only structured facts, derived calculations, explicit data gaps, and evidence anchors; it must not read PDFs/cache/source helpers directly.
- Gate 3 introduces `chapter_orchestrator`; Service owns the write-audit-repair loop policy and calls Agent/Fund capabilities through explicit contracts.
- Gate 4 introduces `final_chapter_assembler`, chapter 0 assembly, and CLI `--use-llm` as an opt-in path; deterministic `analyze/checklist` remains available unless a later gate explicitly changes it.
- Gate 5 optionally replaces or delegates the orchestrator concurrency layer through `dayu.host` / `dayu.engine`, after a separate architecture gate.

Design wording requirements:

- Use status labels such as `当前已实现` and `已接受的未来设计`.
- Do not write future Route C pieces as current code facts.
- Do not claim quality gate, LLM audit, Evidence Confirm, repair loop, Host, Agent runtime, or dayu integration is implemented.
- Keep release-maintenance/golden blockers as residual product-quality work, not as blockers for the MVP report-generation route.

## 8. Implementation slice C: create/update `docs/current-startup-packet.md`

Create or update `docs/current-startup-packet.md` as the short phaseflow startup entry. Target length: about 100-150 lines.

Required structure:

1. Title and purpose.
2. Read order:
   - `AGENTS.md`
   - `docs/design.md`
   - `docs/implementation-control.md`
   - `docs/fund-analysis-template-draft.md`
3. Current mainline:
   - `MVP fund analysis report generation phase`
   - next entry `MVP Gate 1: facet_recognizer + ChapterFactProvider/FundToolService contract gate`
4. Current implementation facts:
   - deterministic `fund-analysis analyze/checklist`
   - UI -> Service -> `fund_agent/fund`
   - no LLM writing/audit/orchestrator/`--use-llm`
   - no Host/Agent/dayu runtime
5. Route C accepted future route, listing Gates 1-5.
6. Boundary guardrails:
   - UI -> Service -> Host -> Agent
   - Service vs Agent/Fund responsibilities
   - `FundDocumentRepository` for production annual reports
   - no `extra_payload`
   - no direct source/cache/PDF helper access outside Fund documents boundary
7. Current residuals:
   - golden / strict correctness / QDII / FOF / `110020` / fixture promotion residuals do not block MVP report generation
   - release-maintenance long ledger preserved by links only
   - Host/Agent/dayu deferred to Gate 5
8. Prohibited actions:
   - no runtime/schema/score/snapshot/quality/golden/promotion change
   - no `AGENTS.md` or template modification
   - no Host/Agent package creation before explicit gate
   - no commit/push/PR unless controller later authorizes
9. Resume checklist:
   - confirm branch/status
   - confirm current gate/role
   - read short startup packet and current control doc
   - classify next gate
   - ensure plan/review/implementation artifacts are in scope

Keep it compact. It is a startup packet, not another historical ledger.

## 9. Implementation evidence artifact requirements

Create the implementation evidence artifact after slices A-C, unless the controller assigns a different path. Recommended path:

`docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md`

Required content:

- Gate name, role, date, branch, and scope.
- Exact files changed.
- A before/after summary:
  - previous control phase and next entry;
  - new control phase and next entry;
  - design future-route section added/updated;
  - startup packet created/updated and approximate line count.
- Evidence that Route C is marked as accepted future design, not current implementation.
- Evidence that current deterministic `analyze/checklist` remains current implementation.
- Evidence that golden/strict correctness/QDII/FOF/110020/fixture promotion are residuals and not MVP blockers.
- Evidence that Host/Agent/dayu remains deferred and correctly constrained.
- Validation commands and results:
  - `git diff --check`
  - path-existence checks for modified and referenced docs
  - docs-only rationale for not running full ruff/pytest
- Residual risk section with owners and next gates.
- No claims of runtime, schema, score, snapshot, quality gate, golden, or promotion changes.

## 10. Controller judgment artifact requirements

The controller judgment artifact, if requested after implementation and reviews, should use a path like:

`docs/reviews/mvp-truth-pivot-context-compaction-controller-judgment-20260530.md`

Required content:

- Controller decision: accepted / accepted with residuals / blocked.
- Confirmed current phase and next entry point.
- Reviewed evidence artifacts and review artifacts.
- Scope audit:
  - only allowed docs changed;
  - no runtime/schema/score/snapshot/quality/golden/promotion changes;
  - unrelated untracked files ignored.
- Design/control consistency judgment:
  - Route C accepted future design only;
  - current implementation remains deterministic;
  - four-layer boundary preserved;
  - dayu Host/Agent deferred correctly.
- Validation judgment:
  - `git diff --check` result;
  - path checks;
  - why full ruff/pytest were not required for docs-only changes.
- Residuals and next gate owner:
  - next owner is `MVP Gate 1: facet_recognizer + ChapterFactProvider/FundToolService contract gate`;
  - golden/coverage/promotion residuals remain separately owned future work.

## 11. Validation plan

Run:

```bash
git diff --check
```

Run path-existence checks for:

```text
AGENTS.md
docs/design.md
docs/implementation-control.md
docs/fund-analysis-template-draft.md
docs/current-startup-packet.md
docs/reviews/mvp-truth-pivot-context-compaction-plan-20260530.md
docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md
```

If the controller judgment artifact is created in the same gate, also check:

```text
docs/reviews/mvp-truth-pivot-context-compaction-controller-judgment-20260530.md
```

Do not run full ruff or pytest for this gate unless the implementation unexpectedly changes code, generated schemas, fixtures, tests, CLI behavior, or runtime-visible docs examples. The intended gate is docs/control-plane only; `git diff --check` plus path-existence checks are sufficient for whitespace and artifact integrity.

## 12. Required reviews

Because this is classified `heavy`, the controller should obtain at least two independent reviews unless reviewer unavailability is explicitly recorded.

Reviewers should check:

- Route C is not described as implemented.
- The active control plane no longer points at the release-maintenance `006597` extractor gate.
- Golden/strict correctness/QDII/FOF/110020/fixture promotion are residuals, not deleted and not active MVP blockers.
- Long release-maintenance history is linked/summarized, not embedded as active truth.
- `docs/current-startup-packet.md` is short enough to work as a phaseflow startup packet.
- UI -> Service -> Host -> Agent boundary remains intact.
- Host/Agent/dayu is deferred to Gate 5 and constrained to `dayu.host` / `dayu.engine`.
- No unrelated untracked artifact is referenced as accepted evidence.

## 13. Stop conditions

Stop and return to controller if any of these occur:

- Accepted artifacts materially conflict on whether Route C is accepted, current, or merely candidate.
- `docs/fund-analysis-template-draft.md` must be changed to make the route coherent.
- MVP route sequencing needs a new user business decision.
- The implementation would require runtime, schema, score, snapshot, quality gate, golden fixture, golden-answer, or promotion changes.
- The dirty scope cannot be attributed to this gate.
- The only way to compact control truth is to delete historical artifacts instead of linking them.
- A required referenced path is missing and cannot be treated as a future artifact placeholder.

## 14. Completion report format

The implementation agent should report only:

- changed files;
- validation results;
- whether Route C is recorded as accepted future design;
- whether the next entry is now `MVP Gate 1: facet_recognizer + ChapterFactProvider/FundToolService contract gate`;
- residuals left for future gates.

No commit, push, PR, promotion, or cleanup action should be reported as performed.
