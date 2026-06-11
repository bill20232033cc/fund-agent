# Runtime Artifact Disposition / Ignore-rule Plan Review - AgentDS

## Scope

- Gate: `Runtime artifact disposition / ignore-rule planning gate`
- Reviewer: AgentDS
- Source pane: `agents:0.2`
- Review type: independent plan review
- Review boundary: no file modification, no artifact creation by reviewer, no stage, no commit, no push, no PR
- Plan under review: `docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-plan-20260611.md`

## Inputs

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`
- `docs/reviews/mvp-long-run-phaseflow-startup-20260611-115345.md`

## Verdict

`ACCEPT`

## Findings

AgentDS accepted the plan and reported only non-blocking findings:

1. `LOW` - `基金年报/` ignore-rule condition was worded differently between §4 and §5. Required controller amendment: unify the condition so the directory may be ignored only if classified as local runtime data that should never enter review as source.
2. `LOW` - untracked `docs/reviews/` artifacts were not split into accepted-gate artifacts versus unclassified historical residue. Required controller amendment: explicitly distinguish the current-gate plan artifact and require exact path-level provenance for any promotion.
3. `LOW` - promote-through-review preconditions risked recursion for plan/review/controller artifacts. Required controller amendment: state that exact controller judgment or accepted artifact index provenance can satisfy the path-level promotion requirement.

## Residuals

- Validation rows such as `git diff --check` and `git diff --name-only` only apply when the eventual implementation gate edits tracked files.
- External Codex skill/memory paths listed in the plan's command log are not project truth inputs and must not become implementation truth.
- The plan artifact itself should be treated as a current-gate plan artifact rather than generic untracked residue.

## Controller Disposition

All DS findings were accepted as amendments. The plan was patched to:

- Add an explicit row for `docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-plan-20260611.md`.
- Update current `docs/reviews` count to 35 including the current plan artifact.
- Add a promotion provenance validation row.
- Require path-level accepted provenance before any promotion.
- Unify the `基金年报/` ignore-rule condition.

## Controller Note

The `PR #22` pane footer was present after the review output. Per user clarification, it is UI footer noise and not evidence that AgentDS is unavailable.
