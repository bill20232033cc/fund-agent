# Controller Judgment: Release-readiness Non-live Verification Matrix Refresh Planning Gate

Date: 2026-06-13

Gate: `Release-readiness Non-live Verification Matrix Refresh Planning Gate`

Controller verdict: `ACCEPT_WITH_NONBLOCKING_AMENDMENTS_NOT_READY`

## Scope

This judgment accepts only the non-live verification matrix refresh plan. It
does not execute the matrix and does not prove release/readiness. It does not
authorize source, tests, runtime, golden-answer content, fixture, manifest,
README, design, readiness, release, PR, push, merge, cleanup, live/provider/LLM,
analyze or checklist changes/actions.

Release/readiness remains `NOT_READY`.

## Inputs Reviewed

| Input | Role |
|---|---|
| `AGENTS.md` | Rule truth and gate classification boundary. |
| `docs/current-startup-packet.md` | Startup truth: current gate and `NOT_READY` posture. |
| `docs/implementation-control.md` | Control truth for accepted checkpoints and next entry. |
| `docs/reviews/mvp-release-readiness-residual-rollup-after-fixture-manifest-evidence-controller-judgment-20260613.md` | Latest accepted rollup at `4590e3b`. |
| `docs/reviews/mvp-release-readiness-non-live-verification-repaired-evidence-controller-judgment-20260612.md` | Prior accepted repaired V0-V10 matrix evidence. |
| `docs/reviews/mvp-release-readiness-non-live-verification-matrix-refresh-plan-20260613.md` | Plan under review. |
| `docs/reviews/mvp-release-readiness-non-live-verification-matrix-refresh-plan-review-ds-20260613.md` | DS review. |
| `docs/reviews/mvp-release-readiness-non-live-verification-matrix-refresh-plan-review-mimo-20260613.md` | MiMo review. |

## Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| DS | `PASS_WITH_FINDINGS` | ACCEPT_WITH_AMENDMENTS. F1 was accepted and V13 was expanded to include flat-record and `record_count` checks. F2 is accepted as a non-blocking maintainability residual. |
| MiMo | `PASS_WITH_FINDINGS` | ACCEPT_WITH_AMENDMENTS. F1 was accepted and V13 now asserts exact count plus record-level `fund_code/report_year`. F2 is accepted as a non-blocking maintainability residual. |

## Finding Disposition

| Finding | Disposition | Resolution |
|---|---|---|
| DS F1: V13 should check top-level `records` and `record_count`, not only nested fund records. | ACCEPT | V13 now checks `payload["records"]`, `record_count`, exact flat-record count and flat identities for `004393 / 2025`. |
| MiMo F1: V13 should assert `len(records)==7` and every nested record has `fund_code=004393`, `report_year=2025`. | ACCEPT | V13 now asserts nested and flat counts are both seven and every row has the exact record-level identity. |
| DS/MiMo F2: V13/V14 long one-line commands are harder to maintain. | ACCEPT_AS_NONBLOCKING_RESIDUAL | The commands remain accepted as bounded read-only evidence commands for the next gate. Future matrix refactors may move them to a temporary script form, but this plan does not write scripts or source/tests. |

No re-review is required because the accepted amendment only strengthens V13
assertions and does not add new scope, mutate files, run commands, or weaken
`NOT_READY`.

## Accepted Matrix Refresh

The accepted next evidence matrix preserves prior V0-V10 and adds:

| ID | Purpose | Accepted assertion |
|---|---|---|
| V11 | Year-aware golden identity tests | Same fund across years remains distinct; missing same-year golden is `year_not_covered`, not cross-year comparison. |
| V12 | Manifest JSON syntax | Accepted manifest parses as JSON without mutation. |
| V13 | Static generated-JSON row-scope assertion | Exact nested and flat `004393 / 2025` rows are seven; record-level identity is `fund_code=004393` and `report_year=2025`; no fee rows, `turnover_rate` or skipped fields are accepted. |
| V14 | Manifest parser identity assertion | Manifest has exact `004393 / 2025` fund-year state and no legacy fund-code-only promotion state. |
| V15 | Downstream preflight exactness tests | Exact-year promotion passes; wrong-year, legacy, duplicate, unknown-field and wrong-identity cases fail closed. |

## Boundary Verification

Planning-gate static checks were limited to:

```text
rg -n "<V11/V15 test node names>" tests/fund
test -f docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json
test -f reports/golden-answers/golden-answer.json
test -f tests/fund/test_golden_answer.py
test -f tests/fund/test_golden_readiness_preflight.py
test -f tests/fund/test_extraction_score.py
git status --branch --short
git diff --check
```

These checks verify referenced paths/test nodes exist. They do not execute the
refresh matrix and do not prove readiness.

## Residuals

| Residual | Owner | Next handling |
|---|---|---|
| Matrix has not been executed. | Release verification owner / controller | Next evidence gate only. |
| V13/V14 are long read-only one-line commands. | Matrix maintainer | Accepted as bounded evidence commands; future refactor may improve readability without expanding scope. |
| Release/readiness remains unproven. | Release owner / controller | Separate readiness/release gate only. |
| PR/push/merge/mark-ready remains external state. | User / controller | Separate external-state authorization only. |
| Live/provider/LLM/analyze/checklist remains deferred. | Evidence owner / controller | Separate controlled-live/provider gate only. |
| Fee rows, `turnover_rate`, skipped/deferred rows and other funds/years remain residual. | Golden/readiness owners | Separate reviewed gates only. |
| Existing untracked residue remains untouched. | Controller / artifact owners | Existing disposition route only; no cleanup here. |

## Rejected Claims

| Claim | Judgment |
|---|---|
| This plan proves release/readiness. | REJECT |
| This plan authorizes executing the matrix now. | REJECT |
| Static path/test-node checks prove readiness. | REJECT |
| `004393 / 2025` exact acceptance applies to other funds/years. | REJECT |
| The next evidence gate may mutate source/tests/runtime/golden/manifest/fixture/design/README. | REJECT |
| The next evidence gate may run live/provider/LLM/analyze/checklist/readiness/release/PR commands. | REJECT |

## Next Entry

After accepted checkpoint and control-doc sync, the exact next mainline entry is:

`Release-readiness Non-live Verification Matrix Refresh Evidence Gate`

Purpose: execute the refreshed deterministic non-live matrix V0-V15, record
direct evidence for accepted `004393 / 2025` seven-row scope, year-aware
parser/manifest identity and downstream exact-year preflight behavior, while
preserving `NOT_READY`.

Deferred entries:

- release/readiness execution or release claim;
- PR/push/merge/mark-ready;
- live/provider/LLM/analyze/checklist commands;
- fee-row clarification;
- `turnover_rate` policy changes;
- other fund/year sample expansion;
- cleanup/archive/ignore disposition.
