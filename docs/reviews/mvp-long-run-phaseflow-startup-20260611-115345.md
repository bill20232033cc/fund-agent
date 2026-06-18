# MVP Long-run Phaseflow Startup

日期：2026-06-11 11:53:45

状态：phaseflow controller startup artifact；不进入 implementation。

Design truth: `docs/design.md`

Control truth: `docs/implementation-control.md`

Review input: `docs/reviews/repo-review-20260611-114133.md`

## Controller Judgment

本 phaseflow 只把当前 accepted control truth、untracked residue disposition 和最新 repository deepreview findings 整合为后续 gate 队列。它不接受任何 source/test/runtime 行为变更，不授权 live EID/provider/PDF/FDR/LLM/analyze/checklist/golden/readiness/release 命令，也不授权删除、移动、归档、清理、忽略、stage、commit、push 或 PR。

当前主线入口保持 `Source-like residue ownership gate for fund_agent/tools`。deepreview 新增 finding 不覆盖当前 control truth；它们作为后续 gate 输入，按风险与依赖顺序排队。

## Source Classification

| Input | Status in this artifact |
|---|---|
| `AGENTS.md` | execution rule truth |
| `docs/design.md` | design truth |
| `docs/implementation-control.md` | control truth |
| `docs/current-startup-packet.md` | short startup control packet |
| `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md` | accepted residue disposition input |
| `docs/reviews/repo-review-20260611-114133.md` | review input, not truth source |
| untracked workspace residue | not proof; only disposition target when exact gate authorizes it |

## Integrated Gate Queue

### 1. Source-like residue ownership gate for `fund_agent/tools`

Classification: `standard`

Reason: current control truth already sets this as active gate. `fund_agent/tools/` is visible under product package namespace and contains source-like tooling residue; release/readiness remains blocked until ownership/disposition is accepted.

Allowed next action: planning worker only.

Required inputs:

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`
- `docs/reviews/repo-review-20260611-114133.md`

Hard boundaries:

- Do not import, stage, promote, clean, delete, move or archive `fund_agent/tools/`.
- Do not use residue contents as product proof.
- Do not modify source/tests/runtime behavior in planning.

Expected output:

- code-generation-ready disposition plan for `fund_agent/tools/`
- explicit ownership decision candidates: delete, archive outside product namespace, move to local tooling, or promote-none
- direct validation matrix for whichever implementation gate follows

Agent routing:

- Planning: one planning worker.
- Review: AgentMiMo + AgentDS independent plan reviews.
- Controller: accepts, rewrites or rejects plan; records next implementation gate only after review.

### 2. EID source provenance truth alignment gate

Classification: `standard`

Reason: deepreview found public provenance still emits `source_strategy=primary_then_fallback` while current design/control truth and runtime source policy are EID single-source with fallback disabled.

Dependency: after source-like residue ownership planning is accepted, unless controller explicitly decides provenance mismatch is more urgent.

Expected scope:

- Align public source provenance fields with EID single-source truth.
- Include stale EID source orchestrator docstring correction.
- Update focused tests for provenance/snapshot/score consumers.

Non-goals:

- No Eastmoney, fund-company/CDN or CNINFO fallback re-entry.
- No new source acquisition.
- No live EID/network/PDF/FDR execution unless separately authorized.

### 3. LLM execution request validation ordering gate

Classification: `standard`

Reason: deepreview found `--use-llm` currently reads provider env and constructs clients before full request / ExecutionContract validation, so request-contract errors can be masked by missing provider configuration.

Expected scope:

- Plan then implement validation ordering: normalize request and validate business/contract constraints before provider env/client construction.
- Add targeted tests for invalid request plus missing provider env error priority.

Non-goals:

- No provider default/config change.
- No live provider call.
- No deterministic fallback for LLM failure.

### 4. UI-Service-Host boundary reconciliation gate

Classification: `heavy`

Reason: `AGENTS.md` and `docs/design.md` state UI must depend on Service, but current Route C implementation/design wording also records CLI handing operation closure to Host runner. This is an architecture boundary conflict, not a local code cleanup.

Expected first step:

- Controller design/control reconciliation judgment before implementation.

Preferred direction:

- Service-owned Host facade; UI passes explicit request/progress sink and does not directly own Host runner.

Non-goals:

- No full Agent tool-loop/runtime expansion.
- No durable Host session/resume/memory/outbox unless a separate future gate authorizes it.

### 5. Runtime artifact disposition / ignore-rule planning gate

Classification: `standard`

Reason: manual smoke reports, `docs/audit/`, duplicate `reviews/`, user PDFs and other untracked runtime/research residue remain unclassified for release/readiness.

Expected scope:

- Artifact-specific disposition plan.
- Decide preserve-as-reviewed-evidence, ignore, archive, leave-user-owned, or delete-candidate.
- `.gitignore` changes only after a reviewed implementation gate authorizes exact patterns.

Non-goals:

- No deletion or archival during planning.
- No treating arbitrary untracked files as accepted evidence.

### 6. Release-readiness cleanliness gate

Classification: `heavy`

Reason: release/readiness evidence is meaningful only after source-like residue, provenance mismatch, validation ordering and runtime artifact disposition have accepted outcomes or explicit residual owners.

Expected scope:

- deterministic release/readiness matrix
- tracked/untracked hygiene checks
- accepted residual owner table
- no live command unless separately authorized

Non-goals:

- No mark-ready, merge, external PR state, push or public comments without separate authorization.

## Deferred Entries

These are not part of the mainline until separately authorized:

- controlled live EID evidence gate
- live provider / LLM acceptance gate
- extractor/golden/readiness promotion gates
- fallback/source expansion design gate
- full Agent tool-loop/runtime expansion gate
- durable Host session/resume/memory/outbox gate

## Phaseflow Operating Rules

1. Each gate starts with plan, review, controller judgment and accepted checkpoint before implementation.
2. Review inputs are not truth sources; design/control truth wins unless a controller judgment updates them through an authorized gate.
3. MiMo and DS are usable. PR #22 residue is pane/context hygiene only, not agent availability evidence.
4. Specialist implementation/review work must be delegated unless the user explicitly authorizes controller to do it directly.
5. Missing direct evidence means the gate cannot be accepted.
6. Live/network/provider/PDF/FDR/release/PR operations require separate reviewed authorization.

## Recommended Next Entry

`Source-like residue ownership gate for fund_agent/tools` planning worker.

This is the only recommended mainline entry. All other gates remain queued or deferred until this gate has an accepted plan and controller judgment.
