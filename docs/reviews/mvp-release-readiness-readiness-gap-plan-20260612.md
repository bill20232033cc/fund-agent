# MVP Release-readiness Readiness-gap Plan — 2026-06-12

Role: AgentDS planning worker (final); AgentCodex prior attempt was stale/failed and its output was discarded. Not controller.

Gate: `Release-readiness readiness-gap planning gate`.

Target artifact: `docs/reviews/mvp-release-readiness-readiness-gap-plan-20260612.md`.

Classification: `standard`; evidence only, non-live, non-cleanup, no candidate body reads, no source/test/runtime behavior change, no PR/release external state.

## 1. Read Boundary

Required reads completed:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-release-readiness-cleanliness-re-evidence-controller-judgment-20260612-104851.md`
- `docs/reviews/mvp-release-readiness-cleanliness-re-evidence-postwrite-amendment-controller-judgment-20260612-105200.md`
- `docs/reviews/mvp-release-readiness-cleanliness-re-evidence-20260612.md`
- `docs/reviews/mvp-release-readiness-residual-ownership-evidence-controller-judgment-20260612-102336.md`

Forbidden reads not performed: candidate residue bodies, `docs/audit/` bodies, reports bodies, PDFs, scripts, user-owned document bodies.

## 2. Input Checkpoint Reconciliation

| Checkpoint | Gate | Verdict | Controller judgment |
|---|---|---|---|
| `0571d39` | `Release-readiness cleanliness re-evidence gate` | `ACCEPT_WITH_RESIDUALS_NOT_READY` | `docs/reviews/mvp-release-readiness-cleanliness-re-evidence-controller-judgment-20260612-104851.md` |
| `414da06` | Post-write metadata amendment (same parent gate) | `ACCEPT_METADATA_AMENDMENT_WITHOUT_READINESS_CHANGE` | `docs/reviews/mvp-release-readiness-cleanliness-re-evidence-postwrite-amendment-controller-judgment-20260612-105200.md` |

Reconciliation result:

- Both checkpoints belong to the same parent gate (`Release-readiness cleanliness re-evidence gate`).
- `0571d39` is the evidence acceptance checkpoint; `414da06` is a metadata-only post-write correction to the same evidence artifact.
- No contradiction: `414da06` changed only status markers produced by `0571d39` itself (`?? after write` → `M`, ahead count 150 → 151). Classification, owner routing, non-proof flags, deferred authorizations and `NOT_READY` are identical across both checkpoints.
- The reconciled state: cleanliness re-evidence accepted with non-blocking worker-channel process residuals; zero current `UNCOVERED_BLOCKER`; release/readiness remains `NOT_READY`; no path accepted as source truth, release evidence or readiness proof.

## 3. Current Readiness Gap

### 3.1 What cleanliness re-evidence proved

- Every current status-visible residue path maps to an accepted ownership-routing row or is `CLEAN`.
- Zero `UNCOVERED_BLOCKER` is visible from allowed metadata commands.
- All rows carry `body_read=false` and all non-proof flags.
- No tracked source/test/runtime/README/design/control mutations are visible.

### 3.2 What cleanliness re-evidence did not prove

- That any accepted exception does not hide a substantive blocker beneath its metadata surface.
- That the historical review/audit artifact corpus forms a coherent, accepted evidence chain.
- That the current implementation checkpoint set is internally consistent (no design/control drift, no missing evidence links).
- That the accepted product path has been exercised beyond the single sample `004393 / 2021-2025`.
- That the `--use-llm` path has any accepted live acceptance evidence.
- That any residue family is safe to clean, archive, ignore, promote, or import.

### 3.3 The gap

Release readiness requires affirmative evidence that the current implementation is correct, complete within its accepted scope, and free of known blockers. Cleanliness metadata proves only that no _new_ blocker path is visible from `git status --short`. It does not prove that the accepted evidence chain is coherent, that accepted exceptions are safe, or that the implementation is ready for external release state.

## 4. Non-live Next Gates (Recommended Mainline Order)

These gates require no live EID/network/PDF/FDR/provider/LLM commands, no candidate body reads beyond accepted review artifacts, and no cleanup/PR/release external state. They close the readiness gap from metadata cleanliness toward affirmative readiness evidence.

### Gate A: Release-readiness Evidence-chain Coherence Gate

- **Purpose**: Prove that the accepted evidence chain from `Control-doc compression` through `Cleanliness re-evidence` forms a coherent, gapless, internally consistent record. _Coherence_ means every gate's declared inputs are traceable to a prior accepted artifact or checkpoint, no two accepted verdicts contradict each other on the same fact, and no gate claims an input that was rejected or superseded by a later judgment. _Internal consistency_ means the chain contains no missing links: every artifact cited as input by a controller judgment exists in the accepted index, and every accepted checkpoint has a corresponding controller judgment.
- **Inputs**: Accepted artifact index (`docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md`), historical ledger index, all accepted controller judgments in the current mainline, `docs/current-startup-packet.md`, `docs/implementation-control.md`.
- **Output**: Coherence matrix mapping every accepted gate to its inputs, outputs, reviews, controller judgment and checkpoint; identification of any missing links, un-reviewed artifacts, or contradictory verdicts.
- **Classification**: `standard`; non-live, reads accepted review artifacts only, no candidate body reads.
- **Primary owner**: Controller.
- **DS/MiMo review criteria**: Confirm every gate has complete input/output/review/judgment/checkpoint records; flag any gap where a controller judgment references an artifact not in the accepted index; flag any verdict that contradicts a later gate's input claim.

### Gate B: Review/audit Historical Artifact Provenance Mapping Gate

- **Purpose**: Classify each untracked `docs/reviews/` artifact into one of: (a) accepted into current evidence chain, (b) superseded by later accepted artifact, (c) orphan (no accepted chain membership), (d) duplicate/redundant.
- **Inputs**: Accepted artifact index, all untracked `docs/reviews/` paths from cleanliness re-evidence matrix, accepted controller judgments.
- **Output**: Provenance map with one row per untracked historical review artifact, chain-membership classification, and routing to next gate.
- **Classification**: `standard`; non-live, metadata-only, no body reads of candidate residue.
- **Primary owner**: Controller.
- **DS/MiMo review criteria**: Confirm every untracked path is classified; confirm chain-membership rationale references accepted controller judgments, not conjecture; flag any artifact whose classification requires body-read to resolve.

### Gate C: Review/audit Residual Acceptance Evidence Gate

- **Purpose**: For each artifact classified as orphan or superseded in Gate B, either accept it as non-proof historical evidence chain material or explicitly reject it as not part of the current evidence chain.
- **Inputs**: Provenance map from Gate B.
- **Output**: Acceptance/rejection matrix; accepted artifacts join the evidence chain as historical-only (not design/control/readiness truth); rejected artifacts are routed to optional cleanup/archive policy gate.
- **Classification**: `standard`; non-live, metadata-only, no body reads.
- **Primary owner**: Controller.
- **DS/MiMo review criteria**: Confirm every acceptance/rejection has explicit rationale; confirm no rejected artifact is later cited as evidence; confirm acceptance does not promote any artifact to design/control/readiness truth.

### Gate D: Release-readiness Accepted-exception Safety Gate

- **Purpose**: For each `ACCEPTED_EXCEPTION` row in the cleanliness re-evidence matrix, provide explicit rationale for why the exception is safe (does not hide a substantive blocker) without reading candidate bodies.
- **Inputs**: Cleanliness re-evidence matrix, residual ownership evidence, accepted controller judgments for each exception family.
- **Output**: Safety rationale matrix; each exception either (a) confirmed safe by accepted controller judgment chain, or (b) escalated to `UNCERTAIN` requiring future body-read or live-evidence gate.
- **Classification**: `standard`; non-live, reads only accepted review/controller artifacts, no candidate body reads.
- **Primary owner**: Controller.
- **DS/MiMo review criteria**: Confirm each safety rationale is grounded in an accepted controller judgment, not worker inference; flag any exception whose safety cannot be confirmed from accepted artifacts alone.

### Gate E: Release-readiness Implementation-scope Completeness Gate

- **Purpose**: Prove that all implementation artifacts accepted in the current phase are internally consistent and complete within their accepted scope.
- **Inputs**: `docs/design.md` (current-implementation sections only), `docs/implementation-control.md`, all accepted implementation evidence artifacts, current source tree (read-only).
- **Output**: Completeness matrix: accepted scope item → implementation artifact → test coverage → design-doc alignment → verdict (complete / residual / drift).
- **Classification**: `heavy`; reads source/test files but does not modify them; no live/network commands. Classified `heavy` (not `standard`) because it crosses the read boundary from accepted review/controller artifacts into the live source tree — scope-to-implementation tracing requires opening source and test files, which carries higher risk of unintended behavioral inference or scope creep compared to metadata-only gates A–D.
- **Primary owner**: Controller + implementation owner.
- **DS/MiMo review criteria**: Confirm every accepted scope item is traced to implementation; flag any implementation without test coverage; flag any design/implementation mismatch; flag any accepted scope item with zero evidence.

### Gate F: Release-readiness Readiness Rollup Gate

- **Purpose**: Aggregate outputs of Gates A–E into a single readiness assessment. If all upstream gates pass without blocking findings, produce affirmative readiness evidence. If any gate has residual blockers, preserve `NOT_READY` and route remaining gaps. **No gate other than F may output `READY` or claim release readiness; doing so triggers the `NOT_READY` stop condition (Section 8).**
- **Inputs**: Coherence matrix (A), provenance map (B), acceptance matrix (C), exception safety matrix (D), completeness matrix (E).
- **Output**: Readiness rollup artifact; either `READY` (all upstream gates clean) or `NOT_READY` with explicit residual blocker map.
- **Classification**: `heavy`; synthesizes upstream gates only; no new body reads, no live commands.
- **Primary owner**: Release owner + controller.
- **DS/MiMo review criteria**: Confirm rollup does not claim readiness if any upstream gate has unresolved residuals; confirm every `READY` sub-claim is traceable to an upstream accepted artifact.

## 5. Explicit Live / PR / Release / Cleanup Gates (Separate Authorization Required)

These gates are explicitly separated from the non-live readiness gap route. Each requires its own reviewed authorization and must not be entered from the non-live planning path without explicit user instruction.

| Gate | Why separate | Required authorization |
|---|---|---|
| Controlled live annual-period narrative evidence | Requires live EID network access; current accepted live evidence is single-sample only (`004393 / 2021-2025`) | Explicit live authorization from user |
| Live provider / LLM acceptance gate | Requires live LLM provider calls; current `--use-llm` path has no live acceptance evidence | Explicit live authorization from user |
| Runtime report-body provenance gate | Requires reading report bodies under `reports/live-evidence/` and `reports/manual-llm-smoke/` | Explicit body-read + live authorization |
| PDF corpus ingestion/disposition gate for `基金年报/` | User-owned PDF corpus; requires body reads and user disposition decision | Explicit user authorization |
| Source-like tooling ownership gate for `scripts/claude_mimo_simple.py` | Requires script body read and ownership decision | Explicit tooling-owner authorization |
| Template/spec truth-source decision gate for `定性分析模板.md` | Requires body read and template-authority decision | Explicit template-owner authorization |
| Cleanup/archive/delete/ignore/import/promote policy gate | Destructive or organizational actions on workspace residue | Explicit path-level authorization per action |
| PR/push/merge/mark-ready/release gate | External state changes (GitHub PR, remote push, merge, release tag) | Explicit external-state authorization after readiness evidence accepted |

## 6. Verifier Matrix

| Gate | Input artifacts | Output artifact | Verifier | Verification method | Pass criteria |
|---|---|---|---|---|---|
| A: Evidence-chain coherence | Accepted artifact index, all controller judgments, startup/control docs | Coherence matrix | DS, MiMo, then controller | Cross-reference every gate's input/output/judgment/checkpoint; flag gaps | Zero missing links; all verdicts consistent |
| B: Historical provenance mapping | Accepted index, untracked `docs/reviews/` paths, controller judgments | Provenance map | DS, MiMo, then controller | Classify every path; verify rationale against accepted judgments | Every path classified; no unclassified orphan |
| C: Residual acceptance evidence | Provenance map (B) | Acceptance/rejection matrix | DS, MiMo, then controller | Verify every acceptance/rejection has explicit rationale | Zero un-routed artifacts; accepted artifacts join evidence chain as historical-only |
| D: Exception safety | Cleanliness matrix, ownership evidence, controller judgments | Safety rationale matrix | DS, MiMo, then controller | Confirm each rationale grounded in accepted judgment | Zero `UNCERTAIN` without explicit next gate |
| E: Implementation completeness | design.md, implementation evidence, source tree (read-only) | Completeness matrix | DS, MiMo, then controller | Trace scope→impl→test→design alignment | Every scope item traced; zero untested implementation |
| F: Readiness rollup | A–E outputs | Readiness rollup | DS, MiMo, then controller | Aggregate upstream verdicts; flag residual blockers | All upstream clean → `READY`; else `NOT_READY` + blocker map |

## 7. Residual Owners

| Residual | Owner | Current status | Next handling |
|---|---|---|---|
| Worker-channel process residuals from cleanliness re-evidence | Controller / worker-channel owner | Accepted non-blocking residual | Re-run init-agents before next tmux-pane handoff; suppress memory lookup when gate read boundary is closed |
| Historical review/audit artifact corpus (untracked `docs/reviews/`) | Controller | Classified as `ACCEPTED_EXCEPTION`; no chain membership accepted | Routed to Gate B (provenance mapping) |
| `docs/audit/` visible root | Controller | `ACCEPTED_EXCEPTION` | Routed to audit residue disposition or provenance mapping gate (separate from current mainline) |
| Research/planning docs (`docs/learning-roadmap.md`, `docs/next-development-phaseflow.md`, `docs/superpowers/specs/`, `docs/tmux-agent-memory-store.md`) | Controller | `ACCEPTED_EXCEPTION` | Routed to research/spec/tooling ownership gate (separate from current mainline) |
| `reports/live-evidence/` and `reports/manual-llm-smoke/` | Runtime evidence owner | `ACCEPTED_EXCEPTION` | Requires explicit live + body-read authorization |
| `reviews/` top-level residue | Controller | `ACCEPTED_EXCEPTION` | Routed to top-level review/audit residual ownership evidence gate (separate from current mainline) |
| `scripts/claude_mimo_simple.py` | Tooling owner | `ACCEPTED_EXCEPTION` | Requires explicit tooling-owner + body-read authorization |
| `基金年报/` PDF corpus | User | `ACCEPTED_EXCEPTION` | Requires explicit user authorization |
| `定性分析模板.md` | Template owner | `ACCEPTED_EXCEPTION` | Requires explicit template-owner + body-read authorization |
| Release/readiness meta-blocker | Release owner / controller | `NOT_READY` | This plan's non-live gate sequence (A→F); do not claim readiness until Gate F passes |

## 8. Stop Conditions

| Condition | Trigger | Action |
|---|---|---|
| Current control truth does not name `Release-readiness readiness-gap planning gate` | Gate/checkpoint mismatch in startup packet or control doc | Stop; do not proceed to evidence worker |
| `NOT_READY` cannot be preserved | Any gate output attempts to claim readiness before Gate F passes | Stop; reject the claiming artifact |
| Non-F gate outputs `READY` | Any gate other than F outputs `READY`, `mark-ready`, `release` or equivalent readiness claim | Stop; reject the artifact; only Gate F is authorized to transition posture |
| Classification requires candidate body reads | Any gate in A–F needs to open untracked residue bodies | Stop; escalate to controller for re-scoping or explicit body-read authorization |
| Unauthorized command requested or needed | Live EID/network/PDF/FDR/provider/LLM command appears necessary | Stop; route to explicit live authorization gate |
| Tracked source/test/runtime/README/design/control mutation appears | `git status --short` shows tracked modifications outside current gate's write set | Stop; investigate and either revert or open separate gate |
| Cleanup/archive/delete/move/ignore/import/promote/stage/commit/push/PR/merge/mark-ready/release requested | Any destructive or external-state action | Stop; route to explicit authorization gate |
| DS or MiMo review returns blocking finding | Either reviewer rejects a gate output | Stop; address finding and re-review before controller judgment |
| Controller judgment rejects a gate output | Controller finds unresolved blocker | Stop; plan amendment or re-evidence required |
| Coherence matrix reveals missing evidence link | Gate A finds a gap in the accepted chain | Stop; open targeted evidence gate to fill the gap before proceeding to Gate B |
| Exception safety cannot be confirmed from accepted artifacts | Gate D finds an exception with no accepted controller judgment grounding | Stop; flag as `UNCERTAIN`; either accept as residual or open body-read gate |

## 9. DS / MiMo Review Criteria

For each gate A–F, reviewers must independently verify:

1. **Input completeness**: All declared input artifacts are read and correctly cited.
2. **Read-boundary compliance**: No candidate residue body was read; no forbidden command was run.
3. **Output completeness**: Output artifact covers all rows/items promised in the gate purpose.
4. **Rationale grounding**: Every classification, acceptance, rejection, or safety claim is grounded in an accepted controller judgment or accepted artifact, not worker inference.
5. **NOT_READY preservation**: The output does not claim release readiness, PR readiness, mark-ready eligibility, or external release state.
6. **Non-proof preservation**: No metadata row is promoted to source truth, design truth, control truth, template truth, release evidence or readiness proof.
7. **Stop-condition compliance**: No stop condition was triggered or silently bypassed.
8. **Cross-gate consistency**: The output does not contradict any upstream accepted artifact or controller judgment.

Additional per-gate criteria are listed in Section 4 under each gate's DS/MiMo review criteria.

## 10. Recommended Next Non-live Entry

**Gate A: Release-readiness Evidence-chain Coherence Gate.**

Rationale:

- Cleanliness re-evidence proved zero `UNCOVERED_BLOCKER` at the metadata surface but did not prove the underlying evidence chain is coherent.
- Before classifying historical artifacts (Gate B) or accepting exceptions (Gate D), the chain itself must be verified: every accepted gate must have complete input/output/review/judgment/checkpoint records, and no contradictory verdicts may exist.
- Gate A is the lowest-risk, highest-value next step: it reads only already-accepted artifacts, requires no body reads, and its output (coherence matrix) is a prerequisite for informed decisions in Gates B–E.
- If Gate A reveals missing links, those become targeted follow-up gates before the rest of the sequence proceeds.

## 11. Command Validation

Allowed commands run exactly:

| Command | Result |
|---|---|
| `git status --short` | Untracked residue visible as expected; zero tracked source/test/runtime/README/design/control modifications |
| `git status --branch --short` | Branch `feat/mvp-llm-incomplete-run-artifacts` ahead 153; no external state change |
| `git diff --check` | Pass (no output) |

## 12. Plan Conclusion

This plan defines six non-live readiness-gap gates (A–F) that close the distance from metadata cleanliness to affirmative readiness evidence without live commands, candidate body reads, cleanup actions, or external release state. Live, PR, release, and cleanup gates are explicitly separated in Section 5 and require independent reviewed authorization.

The plan preserves `NOT_READY` throughout. No gate in this plan claims release readiness; that claim belongs to Gate F only after all upstream gates pass without blocking residuals.

Release/readiness remains `NOT_READY`.
