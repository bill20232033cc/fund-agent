# Audit Disposition & Phaseflow Reconciliation Controller Judgment - 2026-06-10

## Gate

`Audit Disposition & Phaseflow Reconciliation Gate`

## Controller Scope

This is a controller-only disposition gate under `$phaseflow design_doc=docs/design.md control_doc=docs/implementation-control.md`.

No implementation, source changes, test changes, runtime behavior changes, staging, commit, push, PR, live EID, network, PDF/FDR, fallback, provider, curl, DNS or socket action is authorized or performed by this gate.

## Source Hierarchy

This gate treats `docs/audit/fund-agent-repo-deepreview-20260610.md` as review input only, not a truth source.

Truth precedence for this judgment:

1. `AGENTS.md`
2. `docs/design.md`
3. `docs/implementation-control.md`
4. `docs/current-startup-packet.md`
5. `docs/audit/fund-agent-repo-deepreview-20260610.md` as reviewer opinion / evidence prompts only

## Current Truth Baseline

### Repo facts

- An untracked audit report exists at `docs/audit/fund-agent-repo-deepreview-20260610.md`.
- The current branch is `feat/mvp-llm-incomplete-run-artifacts`.
- The workspace has untracked residue; this gate does not delete, move, archive or promote any residue.

### Truth-doc facts

- Current operational annual-report source remains EID single-source MVP: `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`.
- Eastmoney, fund-company/CDN, CNINFO and other non-EID routes are deferred source candidates / historical evidence routes, not active fallback design.
- Small-golden rows `004393`, `004194`, `006597`, `110020`, `017641` for 2024 have accepted live EID/FDR acquisition proof for EID metadata, PDF integrity and parser viability.
- Live EID failure branches remain unproven and require a separately authorized controlled live evidence gate.
- No-live EID implementation and no-live EID failure-branch evidence are accepted and must not be overwritten by stale audit wording.
- Current Host/Agent implementation is explicitly partial: current code facts are minimum Host runtime governance and no-live Agent body-chapter mechanics; full durable Host and full production Agent tool-loop are future scope.

## Disposition Table

| ID | Audit claim / suggestion | Type | Decision | Basis | Controller disposition |
|---|---|---|---|---|---|
| A1 | "live end-to-end evidence is zero" / production happy path is not live-proven | Reviewer opinion mixed with stale wording | `ACCEPT_WITH_REWRITE` | `docs/design.md` states five small-golden rows have accepted live EID/FDR acquisition proof, while live failure branches and full live acceptance remain unproven; `docs/current-startup-packet.md` preserves separate live evidence authorization | Accept as residual only after rewriting: live failure branches and broader live end-to-end readiness are not proven; do not state "no EID live evidence" or erase accepted live EID/FDR acquisition proof |
| A2 | Add weekly scheduled live CI / default live smoke | Reviewer recommendation | `REJECT` | User boundary rejects weekly live CI as default; `AGENTS.md` requires explicit authorization for live/network/source actions; control truth requires separately authorized live EID evidence gate | Reject default/scheduled live CI. If live work is needed, use a controlled live EID evidence gate with explicit scope, commands and stop conditions |
| A3 | Current operational source should account for EID failure branches | Reviewer concern | `ACCEPT_WITH_REWRITE` | Current design accepts EID single-source MVP; no-live five-category evidence is accepted; live failure branches remain unproven | Accept only as controlled live evidence residual. Do not reintroduce Eastmoney/fund-company/CNINFO fallback |
| A4 | Eastmoney / CNINFO / fund-company fallback should be reconsidered through source availability concerns | Reviewer implication | `REJECT` | `docs/design.md` and `docs/implementation-control.md` keep non-EID routes as deferred candidates / historical routes; current source policy is EID single-source | Reject for current phase. Any future non-EID source strategy would require a new source-policy gate, not this disposition gate |
| A5 | Host/Agent are "interface placeholders" and incomplete | Reviewer opinion based on repo scan | `ACCEPT_WITH_REWRITE` | `docs/design.md` explicitly says current Host is minimal governance and Agent is no-live body-chapter mechanics; full tool-loop/durable runtime is future scope | Accept as future-scope observation, reject as current blocker. Only becomes blocker if truth docs present future Host/Agent capabilities as current facts; current truth docs do not |
| A6 | `docs/implementation-control.md` is too long and control/archive boundary is risky | Reviewer opinion aligned with rules | `ACCEPT` | `AGENTS.md` says control doc should prioritize compression and move historical logs to review/archive artifacts; current control doc is long | Accept as residual. Route to `control-doc compression / artifact hygiene gate`; do not compress or move files in this gate |
| A7 | review artifact / manifest / residue hygiene needs better disposition | Reviewer opinion | `ACCEPT` | `AGENTS.md` requires control doc to keep current truth concise and historical artifacts indexed; current workspace has untracked residue including audit output | Accept as artifact hygiene residual. Do not delete/move/archive without separate authorization |
| A8 | Add mypy / black checks in CI, initially warn-only | Reviewer recommendation | `DEFER` | `docs/design.md` says pytest/ruff/black are configured; CI currently blocks on ruff and global coverage; user requested CI quality warn-only planning gate only | Defer to `CI quality warn-only planning gate`. Do not modify CI in this gate |
| A9 | Single-file coverage 80 percent is not CI-enforced | Reviewer observation | `ACCEPT_WITH_REWRITE` | `AGENTS.md` states single-file 80 percent is review target, not current CI blocker; `docs/design.md` states global 50 percent is current CI gate | Accept as reporting/planning residual, not a CI failure. Route to CI quality warn-only planning, not immediate enforcement |
| A10 | Missing extractor coverage for some annual-report sections | Reviewer opinion / possible repo fact | `DEFER` | `docs/design.md` current chapter mapping uses selected annual-report sections; user explicitly scoped extractor coverage to disposition only | Defer to future extractor coverage planning. Do not implement or modify extractor coverage now |
| A11 | Fund type registry should replace `if/elif` classification | Reviewer recommendation | `DEFER` | `AGENTS.md` prefers configurable rules; current design documents fund type classification as current code fact | Defer as fund-type registry candidate. It is not a current blocker unless a future gate changes fund type contracts |
| A12 | Canonical template JSON should migrate out of Markdown | Reviewer recommendation | `DEFER` | `docs/design.md` says current authored template contract truth source is the canonical JSON block in `docs/fund-analysis-template-draft.md`; changing it is a truth-source migration | Defer to template truth-source migration candidate. Do not disturb current accepted truth-source replacement |
| A13 | README should include dry-run / fake-first guidance | Reviewer recommendation | `DEFER` | `AGENTS.md` README updates are tied to implementation or user-facing entry changes; user scoped README dry-run to disposition only | Defer to README dry-run/docs planning gate. Do not change README in this gate |
| A14 | `fund_agent/tools/claude_mimo.py` and local scripts are repo hygiene concerns | Reviewer opinion | `DEFER` | Current task forbids delete/move/archive without separate authorization; audit report is not truth source | Defer to artifact hygiene gate. No file movement or deletion here |
| A15 | QDII/FOF/golden coverage gaps | Reviewer observation | `DEFER` | `docs/design.md` lists QDII/FOF fund types; golden/readiness promotion is explicitly out of current authorization | Defer to coverage/golden planning. Not a blocker for EID downstream integration |
| A16 | Tracking-error P13/P14/P15 promise vs production default gap | Reviewer concern | `DEFER` | This gate did not read or validate P13/P14/P15 artifacts enough to make a code-level root-cause finding; user scoped this gate to disposition only | Defer as needs-more-evidence candidate. Future gate must use same-source design/control/code evidence before accepting |
| A17 | Default route looks production-ready while external dependencies remain live-bound | Reviewer opinion | `ACCEPT_WITH_REWRITE` | `docs/design.md` distinguishes deterministic default, EID source, thermometer data source and `--use-llm`; current startup warns live gates need authorization | Accept as docs/README risk candidate, rewritten to avoid "zero proof" and to preserve accepted live EID/FDR acquisition proof |

## Accepted Residuals

- Live EID failure-branch evidence remains unproven and should be handled only by a controlled live evidence gate.
- Control doc length and artifact hygiene are valid process residuals.
- CI quality reporting can be improved through warn-only planning, without changing blocking CI semantics in this gate.
- README dry-run/fake-first guidance is a useful docs candidate, but not implemented here.

## Rejected Findings

- Reject any audit interpretation that says there is "no EID live evidence at all"; current truth docs accept five-row live EID/FDR acquisition proof.
- Reject default weekly live CI and any always-on live/network test proposal.
- Reject reintroducing Eastmoney, fund-company/CDN, CNINFO or other non-EID routes into current fallback design.
- Reject treating future Host/Agent full runtime scope as a current blocker when design/control docs already label it as future scope.

## Deferred Candidates

- Extractor coverage expansion.
- Fund type registry/configuration refactor.
- Template JSON migration out of Markdown.
- README dry-run / fake-first documentation.
- Tool/script residue disposition.
- Single-file coverage reporting and mypy/black warn-only planning.
- P13/P14/P15 tracking-error truth reconciliation.

## Phaseflow Recommendations

Recommended future sequence:

1. `EID single-source downstream integration gate`
2. `controlled live EID evidence gate`
3. `control-doc compression / artifact hygiene gate`
4. `CI quality warn-only planning gate`

## Recommended Next Entry

Recommended mainline next entry: `EID single-source downstream integration gate`.

Reasoning: this is already the accepted control-doc next entry, it advances currently accepted extractor surfaces into downstream bundle/snapshot/report/chapter-fact surfaces, and it does not require live/network/source/fallback/provider work.

Deferred entries:

- `controlled live EID evidence gate`
- `control-doc compression / artifact hygiene gate`
- `CI quality warn-only planning gate`
- extractor coverage planning
- fund type registry planning
- template JSON migration planning
- README dry-run planning

## Patch Plan If Later Authorized

No immediate `docs/design.md` or `docs/implementation-control.md` edits are required to complete this disposition gate.

If the user later authorizes control-truth updates, proposed write locations:

- `docs/implementation-control.md` Startup Packet: add a short accepted disposition summary and next-entry confirmation.
- `docs/current-startup-packet.md` Current Mainline: keep recommended next entry as `EID single-source downstream integration gate`.
- `docs/design.md` only if a future gate accepts a new design fact, for example CI quality policy, source policy, template truth-source migration or Host/Agent runtime expansion.

## Validation

Required validation for this gate:

```bash
git status --short
git status --branch --short
git diff --check
```

This gate intentionally does not run tests or live commands.
