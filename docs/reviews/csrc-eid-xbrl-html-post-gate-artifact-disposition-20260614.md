# CSRC EID XBRL HTML Post-gate Artifact Disposition

Date: 2026-06-14

Scope: post-gate disposition for pending commit candidates after `CSRC EID XBRL HTML Structured Render Artifact Evaluation Evidence Gate`.

Readiness state: `NOT_READY`

No files were staged, deleted, moved, archived, pushed, or committed by this disposition.

## 1. Current-gate Acceptable Commit Candidates

These files are acceptable as a narrow local checkpoint for the current route, if the user later authorizes staging/commit.

| Path | Category | Evidence | Decision | Owner | Next gate | Blocker? |
|---|---|---|---|---|---|---|
| `docs/reviews/csrc-eid-fund-xbrl-official-resource-discovery-evidence-20260614.md` | evidence-chain artifact | Official EID XBRL resource discovery input for current route | `promote-through-review` | Controller | Current checkpoint | No |
| `docs/reviews/csrc-eid-xbrl-raw-instance-download-evidence-20260614.md` | evidence-chain artifact | Prior raw-instance availability probe; supports blocked raw XML context only | `promote-through-review` | Controller | Current checkpoint | No |
| `docs/reviews/csrc-eid-xbrl-field-correctness-and-taxonomy-blocked-evidence-20260614.md` | evidence-chain artifact | Explicitly blocks field correctness and taxonomy proof | `promote-through-review` | Controller | Current checkpoint | No |
| `docs/reviews/csrc-eid-xbrl-raw-xml-endpoint-deep-probe-evidence-20260614.md` | evidence-chain artifact | Confirms raw XML endpoint remains not proven | `promote-through-review` | Controller | Current checkpoint | No |
| `docs/reviews/csrc-eid-xbrl-html-render-route-realignment-controller-judgment-20260614.md` | current-gate artifact | Controller route realignment to HTML render artifact evaluation | `stage-current-gate` | Controller | Current checkpoint | No |
| `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-20260614.md` | current-gate artifact | Planning artifact for accepted evidence gate | `stage-current-gate` | Controller | Current checkpoint | No |
| `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-controller-judgment-20260614.md` | current-gate artifact | Plan accepted with binding amendments | `stage-current-gate` | Controller | Current checkpoint | No |
| `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-20260614.md` | current-gate artifact | 12-row official EID HTML render evidence; verdict partly stable, not ready | `stage-current-gate` | Controller | Current checkpoint | No |
| `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-controller-judgment-20260614.md` | current-gate artifact | Controller accepted evidence and stopped before design/implementation | `stage-current-gate` | Controller | Current checkpoint | No |
| `docs/reviews/csrc-eid-xbrl-html-post-gate-artifact-disposition-20260614.md` | current-gate artifact | This disposition record | `stage-current-gate` | Controller | Current checkpoint | No |

## 2. Tracked Diff Disposition

These tracked modifications are coherent with the current route but should be reviewed before any commit because they modify truth/control docs.

| Path | Category | Evidence | Decision | Owner | Next gate | Blocker? |
|---|---|---|---|---|---|---|
| `AGENTS.md` | truth-doc sync candidate | Clarifies EID single-source/no-fallback, parser boundary and document-intermediate non-truth guardrails | `promote-through-review` | Controller + user | Current checkpoint or truth-doc sync checkpoint | No, but high-impact |
| `README.md` | user-doc sync candidate | Clarifies `analyze-annual-period` is deterministic and not Route C LLM | `promote-through-review` | Controller | Current checkpoint or doc sync checkpoint | No |
| `docs/current-startup-packet.md` | control-doc sync candidate | Moves current gate to CSRC EID XBRL HTML render route | `promote-through-review` | Controller | Current checkpoint | No |
| `docs/design.md` | design truth sync candidate | Adds document representation / Docling / EID HTML render candidate boundaries | `promote-through-review` | Controller + user | Current checkpoint or design sync checkpoint | No, but high-impact |
| `docs/implementation-control.md` | control-doc sync candidate | Updates current mainline and residual queue | `promote-through-review` | Controller | Current checkpoint | No |

Suggested commit policy:

- If committing immediately, use one narrow checkpoint for the XBRL HTML route and include only the five tracked docs plus the ten XBRL/post-gate artifacts listed above.
- If wanting stricter separation, split into two local commits: route evidence artifacts first, then truth/control doc sync.
- Do not stage unrelated untracked residue in the same checkpoint.

## 3. Leave-untracked / Deferred Groups

These paths should not be included in the current checkpoint.

| Path / group | Category | Evidence | Decision | Owner | Next gate | Blocker? |
|---|---|---|---|---|---|---|
| `docs/reviews/annual-report-*` | research input / deferred plan chain | Docling benchmark plan and reviews are explicitly deferred behind HTML render route | `leave-untracked` | Parser route owner | Future Docling/document representation gate | No |
| `docs/reviews/provider-llm-*` | evidence-chain artifact | Provider/LLM stabilization history; not current mainline | `leave-untracked` | Provider/LLM route owner | Future stabilization gate | No |
| `docs/reviews/mvp-*`, `release-maintenance-*`, `repo-review-*`, historical `plan-review-*` | historical evidence-chain artifact | Prior gates and reviews; many are not current route scope | `leave-untracked` | Respective gate owners | Separate artifact hygiene/archive gate | No |
| `docs/audit/` and `reviews/` | audit/review input | Repo audits and external review records; review input only, not truth source | `leave-untracked` | Audit owner | Artifact hygiene/archive gate | No |
| `reports/` including `reports/live-evidence/`, `reports/manual-llm-smoke/`, `reports/extraction-snapshots/` | scratch/runtime output | Generated run outputs; current size about 260M | `leave-untracked` | Release/artifact owner | Runtime artifact disposition / ignore gate | Yes for release cleanliness, no for current evidence checkpoint |
| `基金年报/` | user-owned data artifact candidate | Local PDF corpus, about 7.7M; not current route proof | `leave-untracked` | User / data owner | Future parser benchmark or data-corpus gate | No |
| `docs/code-wiki-and-audit-report-20260613.md`, `docs/dayu-*`, `docs/learning-roadmap.md`, `docs/liu-chenggang-*`, `docs/next-development-phaseflow.md`, `docs/tmux-agent-memory-store.md` | research input / planning notes | Useful discussion or coordination notes, not current gate artifacts | `leave-untracked` | User / controller | Separate docs disposition gate | No |
| `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md` | research/design residue | Not current route and not accepted as active truth | `leave-untracked` | Spec owner | Separate spec disposition gate | No |
| `scripts/claude_mimo_simple.py` | source-like residue | Could affect tooling if promoted; no current gate authorization | `leave-untracked` | Tooling owner | Separate tooling/source-residue gate | No |
| `定性分析模板.md` | user-owned unknown | Standalone local document, not current gate artifact | `leave-untracked` | User | User decision | No |

## 4. Ask-before-delete Candidates

No deletion is authorized.

Likely cleanup candidates, if the user later opens a cleanup gate:

- `reports/.DS_Store`
- generated `reports/` runtime outputs already represented by accepted review artifacts;
- obsolete duplicate historical review artifacts after a dedicated archive/delete authorization;
- source-like `scripts/claude_mimo_simple.py` if no longer used.

All require explicit deletion or archive authorization.

## 5. Final Disposition

Current gate closeout can be checkpointed narrowly, but the workspace as a whole is not clean and is not PR-ready.

Acceptable current checkpoint scope:

```text
AGENTS.md
README.md
docs/current-startup-packet.md
docs/design.md
docs/implementation-control.md
docs/reviews/csrc-eid-fund-xbrl-official-resource-discovery-evidence-20260614.md
docs/reviews/csrc-eid-xbrl-raw-instance-download-evidence-20260614.md
docs/reviews/csrc-eid-xbrl-field-correctness-and-taxonomy-blocked-evidence-20260614.md
docs/reviews/csrc-eid-xbrl-raw-xml-endpoint-deep-probe-evidence-20260614.md
docs/reviews/csrc-eid-xbrl-html-render-route-realignment-controller-judgment-20260614.md
docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-20260614.md
docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-controller-judgment-20260614.md
docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-20260614.md
docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-controller-judgment-20260614.md
docs/reviews/csrc-eid-xbrl-html-post-gate-artifact-disposition-20260614.md
```

Everything else should remain untracked until a separate artifact hygiene, archive, cleanup, parser benchmark, provider/LLM stabilization or release-readiness gate accepts it.
