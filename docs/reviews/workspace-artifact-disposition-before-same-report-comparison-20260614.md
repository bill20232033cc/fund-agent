# Workspace Artifact Disposition Before Same-report Comparison

Date: 2026-06-14

Scope: close out the current dirty workspace before entering `Same-report Document Representation Quality Comparison Planning Gate`.

This artifact is metadata/disposition only. It does not accept readiness, source truth, raw XML availability, field correctness, taxonomy compatibility, production parser replacement, repository behavior change, PR state, release state, cleanup, archive, deletion, staging, commit, push or merge.

## Preflight

| Check | Result |
|---|---|
| Branch | `feat/mvp-llm-incomplete-run-artifacts` |
| Remote relation | `ahead 142` |
| Tracked diff | 5 documentation files: `AGENTS.md`, `README.md`, `docs/current-startup-packet.md`, `docs/design.md`, `docs/implementation-control.md` |
| Tracked code/test diff | none observed |
| `git diff --check` | passed with no output |
| Release/readiness | remains `NOT_READY` |

## Tracked Diff Disposition

| Path | Category | Evidence | Decision | Owner | Next gate | Blocker? |
| --- | --- | --- | --- | --- | --- | --- |
| `AGENTS.md` | current-route guardrail update | Adds parser boundary, document-intermediate non-truth guard, periodic-disclosure corpus boundary, and EID single-source no-fallback wording. | `promote-through-review` with current route artifacts; do not stage alone. | Controller / truth-doc owner | Local accepted checkpoint after user confirms scope. | Blocks clean workspace if left uncheckpointed. |
| `README.md` | user-doc sync | Clarifies deterministic `analyze-annual-period` has no `--use-llm` route. | `promote-through-review` with current route artifacts; do not stage alone. | Controller / docs owner | Local accepted checkpoint after user confirms scope. | Blocks clean workspace if left uncheckpointed. |
| `docs/current-startup-packet.md` | current control truth sync | Switches startup packet from Route C Chapter 3 narrow stabilization to XBRL HTML render route and candidate source planning. | `promote-through-review` with cited route artifacts. | Controller / control-doc owner | Local accepted checkpoint after user confirms scope. | Blocks clean workspace if left uncheckpointed. |
| `docs/design.md` | candidate/future design truth sync | Records document representation gap, Docling as candidate benchmark only, and `eid_xbrl_html_render_candidate` as candidate/research input, not current implementation. | `promote-through-review` with cited design/evidence artifacts. | Controller / design owner | Local accepted checkpoint after user confirms scope. | Blocks clean workspace if left uncheckpointed. |
| `docs/implementation-control.md` | current control truth sync | Records current phase, accepted route artifacts, NOT_READY guardrails and mainline queue. | `promote-through-review` with cited route artifacts. | Controller / control-doc owner | Local accepted checkpoint after user confirms scope. | Blocks clean workspace if left uncheckpointed. |

## Untracked Artifact Disposition

| Path / group | Category | Evidence | Decision | Owner | Next gate | Blocker? |
| --- | --- | --- | --- | --- | --- | --- |
| `docs/reviews/provider-llm-chapter3-missing-required-marker-no-live-diagnostic-evidence-20260614.md` and its DS/MiMo reviews | evidence-chain artifact | Route C closeout input referenced by current startup/control docs. | `promote-through-review` only if committing Route C closeout and route realignment checkpoint. | Controller / Route C stabilization owner | Local accepted checkpoint scope decision. | Blocks clean workspace if cited control docs are committed without it. |
| `docs/reviews/provider-llm-route-stabilization-closeout-controller-judgment-20260614.md` | evidence-chain artifact | Controller closeout verdict `ACCEPT_ROUTE_REALIGNMENT_NOT_READY`. | `promote-through-review` with route realignment checkpoint. | Controller | Local accepted checkpoint scope decision. | Blocks clean workspace if cited control docs are committed without it. |
| `docs/reviews/annual-report-docling-parser-discussion-summary-20260613.md` | research input / cited design support | Discussion summary referenced by `docs/design.md`; supports candidate Docling benchmark framing only. | `promote-through-review` if committing design sync; otherwise `leave-untracked`. | Fund documents/parser owner | Same-report comparison planning or later Docling benchmark gate. | Blocks only if `docs/design.md` citation is committed without the artifact. |
| `docs/reviews/annual-report-document-representation-docling-benchmark-plan-20260614.md` plus DS/MiMo reviews and controller judgment | evidence-chain artifact | Accepted plan checkpoint for deferred Docling benchmark; controller verdict `ACCEPT_WITH_BINDING_AMENDMENTS_NOT_READY`. | `promote-through-review` if committing current route/control sync; otherwise `leave-untracked`. | Fund documents/parser owner | Deferred Docling benchmark evidence gate, after same-report comparison. | Blocks only if cited control docs are committed without artifacts. |
| `docs/reviews/csrc-eid-fund-xbrl-official-resource-discovery-evidence-20260614.md`, `docs/reviews/csrc-eid-xbrl-raw-instance-download-evidence-20260614.md`, `docs/reviews/csrc-eid-xbrl-field-correctness-and-taxonomy-blocked-evidence-20260614.md`, `docs/reviews/csrc-eid-xbrl-raw-xml-endpoint-deep-probe-evidence-20260614.md` | evidence-chain artifact | Accepted input chain for official EID XBRL resources and raw XML blocked status. | `promote-through-review` with XBRL HTML route checkpoint. | Fund documents/source research owner | Local accepted checkpoint scope decision. | Blocks clean route checkpoint if omitted. |
| `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-20260614.md`, plan controller judgment, evidence artifact and evidence controller judgment | current-route artifact | Plan accepted with binding amendments; evidence verdict `HTML_RENDER_ARTIFACT_AVAILABLE_PARTLY_STABLE_NOT_READY`; controller verdict `ACCEPT_EVIDENCE_HTML_RENDER_AVAILABLE_PARTLY_STABLE_NOT_READY`. | `promote-through-review` with XBRL HTML route checkpoint. | Fund documents/source research owner | Local accepted checkpoint scope decision. | Blocks clean route checkpoint if omitted. |
| `docs/reviews/csrc-eid-xbrl-html-render-route-realignment-controller-judgment-20260614.md` | current-route artifact | Controller verdict `ACCEPT_ROUTE_REALIGNMENT_TO_XBRL_HTML_RENDER_EVALUATION_NOT_READY`. | `promote-through-review` with current control/design sync. | Controller | Local accepted checkpoint scope decision. | Blocks clean route checkpoint if omitted. |
| `docs/reviews/csrc-eid-xbrl-html-evidence-closeout-control-sync-controller-judgment-20260614.md` | current-route artifact | Controller verdict `ACCEPT_CLOSEOUT_READY_FOR_FUNDDISCLOSUREDOCUMENT_CANDIDATE_SOURCE_DESIGN_GATE_NOT_READY`. | `promote-through-review` with current control/design sync. | Controller | Local accepted checkpoint scope decision. | Blocks clean route checkpoint if omitted. |
| `docs/reviews/funddisclosuredocument-candidate-source-design-20260614.md` plus DS/MiMo reviews and controller judgment | current-route artifact | Candidate source design accepted; verdict `ACCEPT_DESIGN_READY_FOR_SCHEMA_PLANNING_GATE_NOT_READY`. | `promote-through-review` with current route checkpoint. | Fund documents/source research owner | Local accepted checkpoint scope decision. | Blocks clean route checkpoint if omitted. |
| `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-20260614.md` plus DS/MiMo review, MiMo re-review and controller judgment | current-route artifact | Schema plan accepted; verdict `ACCEPT_WITH_PLAN_FIX_READY_FOR_NO_LIVE_IMPLEMENTATION_PLANNING_GATE_NOT_READY`. | `promote-through-review` with current route checkpoint, unless same-report comparison supersedes next gate before commit. | Fund documents/source research owner | Local accepted checkpoint scope decision. | Blocks clean route checkpoint if omitted. |
| `docs/reviews/csrc-eid-xbrl-html-post-gate-artifact-disposition-20260614.md` | evidence-chain artifact | Existing post-gate disposition for pending XBRL HTML commit candidates. | `promote-through-review` only if used as prior disposition evidence; otherwise superseded by this artifact. | Controller | Local accepted checkpoint scope decision. | Non-blocking. |
| Other `docs/reviews/*.md` / `.json` historical files not cited by current route sync | evidence-chain artifact / historical residue | Older release, audit, golden, provider, repository review or maintenance artifacts. | `leave-untracked`; do not stage in current route checkpoint. | Corresponding historical gate owners | Separate artifact disposition / archive gate only if requested. | Blocks release/readiness cleanliness, not current planning. |
| `docs/audit/fund-agent-repo-deepreview-20260610.md` | historical audit input | Audit report is review input, not truth source. | `leave-untracked` unless an audit disposition gate explicitly promotes it. | Audit artifact owner | Separate audit disposition gate. | Blocks release/readiness cleanliness only. |
| `docs/code-wiki-and-audit-report-20260613.md`, `docs/dayu-agent-architect-gap-analysis-20260613.md`, `docs/dayu-agent-codiwiki-and-development-stage-analysis-20260614.md`, `docs/dayu-fund-agent-mvp-gap-discussion-summary-20260613.md`, `docs/learning-roadmap.md`, `docs/liu-chenggang-dayu-ai-coding-roadmap-20260614.md`, `docs/next-development-phaseflow.md`, `docs/tmux-agent-memory-store.md`, `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md` | research input / user-owned unknown | Exploratory roadmap, external architecture analysis, tmux/process notes or older phaseflow material. | `leave-untracked`; do not stage into current route checkpoint. | User / research owners | Separate research-input disposition gate if needed. | Blocks release/readiness cleanliness only. |
| `reports/live-evidence/controlled-2021-2025-annual-period-20260611-230350/*` and `reports/manual-llm-smoke/*` | scratch/runtime output | Runtime/live evidence outputs; not current XBRL/Docling route source truth. | `leave-untracked`; do not stage. | Runtime evidence owner | Runtime/live report residue disposition gate. | Blocks release/readiness cleanliness only. |
| `reviews/audit-report-2025-05-27*.md` | historical top-level review residue | Top-level review artifacts outside current evidence chain. | `leave-untracked`; do not stage. | Review artifact owner | Top-level review/audit residue disposition gate. | Blocks release/readiness cleanliness only. |
| `scripts/claude_mimo_simple.py` | tooling residue / user-owned unknown | Not referenced by current gate; may be local agent tooling. | `leave-untracked`; do not stage. | Agent/tooling owner | Tooling disposition gate if promotion is desired. | Non-blocking for current planning. |
| `基金年报/*.pdf` | user-owned data artifact candidate | Local PDF corpus; no body-read in this disposition. | `leave-untracked`; do not stage or delete. | User / data artifact owner | Data artifact disposition or same-report sample authorization gate. | Blocks release/readiness cleanliness only. |
| `定性分析模板.md` | user-owned unknown / research input | Not referenced by current gate. | `leave-untracked`; do not stage. | User / docs owner | Separate template disposition gate if promotion is desired. | Non-blocking for current planning. |

## Closeout Decision

Candidate accepted checkpoint set, if the user authorizes a local checkpoint:

1. The 5 tracked truth-doc/user-doc changes.
2. Current Route C closeout artifacts cited by those docs.
3. Deferred Docling benchmark plan/review/controller artifacts cited by those docs.
4. CSRC EID XBRL official/raw-blocked/HTML-render evidence and controller artifacts.
5. FundDisclosureDocument candidate source design/schema artifacts and reviews.
6. This disposition artifact.

Everything else should remain untracked for now. No deletion, archive, ignore-rule change, staging, commit, push, PR or release action is accepted by this artifact.

## Residuals

| Residual | Disposition |
|---|---|
| Same-report comparison now needs Docling in the comparison scope | Insert `Same-report Document Representation Quality Comparison Planning Gate` before candidate source implementation planning. |
| Existing control docs still name `FundDisclosureDocument Candidate Source No-live Implementation Planning Gate` as current next entry | Closed by scoped control sync artifact `docs/reviews/same-report-document-representation-quality-comparison-control-sync-20260614.md`; next entry now points to `Same-report Document Representation Quality Comparison Planning Gate`. |
| Large historical untracked review/report/data residue remains visible | Leave untracked; separate cleanup/archive/delete requires explicit authorization. |
| Release/readiness cleanliness | Still `NOT_READY`; current disposition is not release evidence. |

## Validation

Required before any local checkpoint:

```text
git status --short
git status --branch --short
git diff --check
```

Optional, only if a local checkpoint is authorized:

```text
git add <scoped accepted files only>
git diff --cached --name-only
git commit -m "docs: accept xbrl html route disposition"
```

Do not stage unrelated residue.
