# Release Maintenance Next Candidate Plan Review Controller Judgment - 2026-05-24

## Gate

- Current phase: `release maintenance`
- Current gate: `release maintenance Host/Agent boundary decision plan review`
- Plan: `docs/reviews/release-maintenance-next-candidate-plan-20260524.md`
- Reviews:
  - `docs/reviews/release-maintenance-next-candidate-plan-review-mimo-20260524.md`
  - `docs/reviews/release-maintenance-next-candidate-plan-review-glm-20260524.md`
- Controller conclusion: `fix required before plan acceptance`

## Truth Sources

- `AGENTS.md`
- `docs/design.md` current design sections
- `docs/implementation-control.md` Startup Packet / current gate
- Current repo facts checked by the planning/review artifacts

Historical `docs/reviews/` and implementation-control archive wording about six-layer, Application, Runtime, or Engine is historical evidence only and is not current architecture truth.

## Reviewer Conclusions

| Reviewer | Conclusion | Findings | Blocking Questions |
|---|---|---:|---|
| MiMo | `PASS_WITH_FINDINGS` | 5 | 0 |
| GLM | `PASS_WITH_FINDINGS` | 4 | 0 |

Both reviewers accepted the candidate choice: choose `Host/Agent boundary decision` over `Host/Agent dependency gate`, narrowed to a document-only boundary decision artifact with no package, dependency, source, test, README, design, or control-doc changes.

## Controller Finding Decisions

### C1-accepted-MiMo-F1 / dayu-agent pyproject baseline definition is too vague

- **Decision**: accepted
- **Reason**: Based on the design goal of reproducible engineering baseline and first principles, a future dependency gate must know whether the baseline is local `docs/design.md` / `pyproject.toml` or an external Dayu commit; leaving this vague would make implementation agents invent criteria.
- **Required fix**: Clarify in the plan that the local baseline is `docs/design.md` §9.1 plus current `pyproject.toml`; if an external `dayu-agent` pyproject is used, the future gate must record the exact source URL or commit and the fetched content/provenance. Add concrete validation commands such as `rg -n "dayu" pyproject.toml`, `uv lock --check`, and package-data/package-discovery checks where applicable.

### C2-accepted-MiMo-F2 / decision artifact skeleton missing

- **Decision**: accepted
- **Reason**: The work unit is intentionally document-only; a precise artifact skeleton reduces reviewer/controller parsing cost without expanding scope.
- **Required fix**: Add a minimal required section outline for `docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`.

### C3-accepted-MiMo-F3 / validation should distinguish existence checks from semantic review

- **Decision**: accepted
- **Reason**: For a document-only gate, `rg` checks are useful but not sufficient; the plan must assign semantic correctness to review gates to avoid false confidence.
- **Required fix**: State that `rg` commands are existence checks and semantic correctness is covered by plan/review gates.

### C4-accepted-MiMo-F4 / accepted decision absorption path missing

- **Decision**: accepted
- **Reason**: A boundary decision that never reaches control tracking can be forgotten; the plan should define how accepted decisions are tracked without prematurely editing truth documents.
- **Required fix**: Add `Decision absorption path` to completion/reporting: controller records accepted decision in control tracking or opens a separate docs/control update only if the decision changes current truth.

### C5-accepted-MiMo-F5 / stop-condition report format missing

- **Decision**: accepted
- **Reason**: Stop conditions are useful only if the worker returns enough context for controller scope裁决.
- **Required fix**: Add a minimal stop report format: triggered condition, context/evidence, suggested scope adjustment, and whether user decision is required.

### C6-accepted-GLM-F1 / code-generation-ready wording misstates a document-only deliverable

- **Decision**: accepted
- **Reason**: The selected work unit does not generate code; accurate language prevents future agents from treating a document-only decision as implementation authorization.
- **Required fix**: Replace or qualify `code-generation-ready` with `plan-review-ready decision plan` for this work unit.

### C7-accepted-GLM-F2 / Slice 2 validation lacks executable command

- **Decision**: accepted
- **Reason**: Slice validation should be mechanically repeatable where practical.
- **Required fix**: Add an `rg` validation command for dependency-gate-blocked, no placeholder packages, and no `extra_payload` parameters.

### C8-accepted-GLM-F3 / completion validation field lacks pass criteria

- **Decision**: accepted
- **Reason**: Completion reports should carry commands and pass/fail evidence, not a vague label.
- **Required fix**: Specify that `Validation run` records each command, expected assertion, and exit code or observed pass signal.

### C9-accepted-GLM-F4 / design.md §12 checklist incomplete

- **Decision**: accepted
- **Reason**: Even if this work unit does not touch annual-report access or license metadata, plan review templates must preserve the project-wide boundary checklist.
- **Required fix**: Add review checklist items for production annual-report access staying through `FundDocumentRepository` / `FundDataExtractor`, and License/repo hygiene remaining unchanged.

## Rejected / Deferred Findings

None. All reviewer findings are accepted as low-risk plan fixes before acceptance.

## Next Gate

Dispatch a plan-fix worker to update only `docs/reviews/release-maintenance-next-candidate-plan-20260524.md` and create a fix artifact. Then dispatch MiMo and GLM re-review against the accepted findings only.
