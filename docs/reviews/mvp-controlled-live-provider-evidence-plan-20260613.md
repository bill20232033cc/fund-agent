# Controlled Live/Provider Evidence Planning Gate

Date: 2026-06-13

Gate: `Controlled Live/Provider Evidence Planning Gate`

Classification: `heavy` planning-only

Status: `PLANNING_ONLY_NOT_EXECUTED`

Release/readiness: `NOT_READY`

## Goal

Define a bounded, execution-ready plan for a future separately authorized
`Controlled Live/Provider Evidence Execution Gate`.

The future execution gate may collect live/provider evidence only inside the
accepted source policy and current architecture boundary, with explicit sample
scope, command logging, timeout limits, redaction rules, failure classification
and stop conditions.

This planning gate does not execute the future matrix.

## Non-goals

- Do not run live/provider/LLM/network/PDF/FDR/analyze/checklist/readiness/release/PR commands.
- Do not modify source, tests, runtime behavior, prompt manifests, golden
  answers, fixtures, promotion manifests, README, design docs or release state.
- Do not clean, delete, move, archive, ignore, import, push, merge, open PR or
  mark ready.
- Do not stage or commit unrelated files; local accepted gate checkpoints may
  stage and commit only this gate's reviewed artifacts and post-acceptance
  control-doc sync.
- Do not treat untracked residue, reports, PDFs, manual smoke output or
  historical review artifacts as truth source.
- Do not change EID single-source policy, fallback policy, provider defaults,
  runtime budgets or retry semantics.
- Do not convert any future evidence result into release/readiness approval.

## Accepted Inputs

| Input | Role |
|---|---|
| `AGENTS.md` | Rule truth, gate classification and source policy guardrails. |
| `docs/current-startup-packet.md` | Startup truth for current active gate and `NOT_READY` posture. |
| `docs/implementation-control.md` | Control truth for accepted inputs, current residuals and next entry. |
| `docs/reviews/mvp-release-readiness-non-live-verification-matrix-refresh-evidence-controller-judgment-20260613.md` | Accepted refreshed V0-V15 non-live matrix judgment. |
| `docs/reviews/mvp-release-readiness-ready-state-disposition-refresh-controller-judgment-20260613.md` | Accepted ready-state disposition refresh and next-entry recommendation. |

Accepted current facts:

- Refreshed V0-V15 deterministic non-live matrix is accepted as
  `PASS_ACCEPTED_NON_LIVE`.
- Accepted golden scope is exact `004393 / 2025` seven tracked rows only.
- Fixture promotion manifest is exact `004393 / 2025` only.
- Fee rows, `turnover_rate`, skipped/deferred rows and other funds/years remain
  residual.
- Live/provider/LLM remains `DEFERRED_UNPROVEN`.
- PR/push/merge/mark-ready remains `DEFERRED_EXTERNAL_STATE`.
- Release/readiness remains `NOT_READY`.

## Allowed Write Set

This planning gate may write only:

- `docs/reviews/mvp-controlled-live-provider-evidence-plan-20260613.md`
- DS/MiMo or equivalent plan review artifacts under `docs/reviews/`
- controller judgment for this planning gate under `docs/reviews/`

After acceptance only:

- minimal control-doc sync in `docs/current-startup-packet.md`
- minimal control-doc sync in `docs/implementation-control.md`

No other write path is authorized.

## Forbidden Commands And Actions In This Planning Gate

This planning gate must not execute:

- live/provider/network commands
- LLM/provider calls
- PDF/FDR/FundDocumentRepository access commands
- `fund-analysis analyze`
- `fund-analysis analyze-annual-period`
- `fund-analysis checklist`
- readiness/release/PR/push/merge/mark-ready commands
- cleanup/archive/ignore/import commands
- source/test/runtime/golden/manifest/fixture mutation commands

Allowed validation is limited to static artifact checks such as `git status`,
`git diff --check`, targeted `rg` over this plan and file-existence checks for
accepted input artifacts.

## Future Execution Gate Candidate Matrix

The following matrix is a planning output only. It is not executed by this gate.
Only L0-L2 and L5 are execution-ready for the next controlled execution gate.
L3 and L4 are explicitly deferred sub-plan candidates until exact sample,
command/input identity and redaction scope are accepted by a separate plan or
plan amendment.

Hard execution limits for the next execution gate:

- global timeout: 15 minutes total;
- per-command timeout: L0 60 seconds, L1 180 seconds, L2 300 seconds, L5 60
  seconds;
- retry count: zero retries by default; any retry requires a separately
  reviewed plan amendment;
- stdout/stderr retention: maximum 80 lines or 12 KiB per command, whichever is
  smaller;
- raw PDF body, raw provider payload, credentials, headers, tokens, API keys,
  local cache paths and sensitive query parameters must not be stored.

| ID | Command category | Sample scope | Success criteria | Failure classification | Timeout / redaction | Stop condition |
|---|---|---|---|---|---|---|
| L0 | Preflight metadata/status only | accepted execution artifact paths and exact configured sample list | Confirms exact sample list, write targets under `docs/reviews/`, no residue promoted as input | `preflight_blocked`, `scope_mismatch` | 60s timeout; retain <=80 lines / 12 KiB; redact env, tokens, provider keys | Stop if sample list differs from accepted plan |
| L1 | Controlled EID annual-report source evidence | exact `004393 / 2021-2025` | all requested years available through production repository boundary; source is EID only; `fallback_used=False`; no Eastmoney/CNINFO/CDN/fallback invocation | `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`, `fallback_violation` | 180s timeout; retain <=80 lines / 12 KiB; redact sensitive query params, local cache paths and credentials | Stop on first `schema_drift`, `identity_mismatch`, `integrity_error` or fallback attempt |
| L2 | Controlled product-path live evidence | exact `004393 / 2021-2025`, current accepted product path only | command exits 0; annual-period report emitted; EID provenance lines present for every year; `fallback_year_count=0`; quality status recorded without readiness promotion | `execution_error`, `quality_warn`, `quality_block`, `missing_provenance`, `fallback_violation` | 300s timeout; retain <=80 lines / 12 KiB; retain command, exit code and key metadata lines only | Stop if output lacks provenance or uses non-EID source |
| L3 | Provider/LLM explicit opt-in evidence | DEFERRED; no sample, prompt or command is accepted by this plan | Not executable under this plan; requires separate provider/LLM evidence sub-plan with exact sample, prompt/command identity and redaction surface | `provider_subplan_required` | No timeout accepted; no raw payload may be stored | Stop: do not execute L3 under this plan |
| L4 | Negative/fail-closed source behavior evidence | DEFERRED; no wrong-year or invalid-identity sample is accepted by this plan | Not executable under this plan; requires separate negative-case sub-plan with exact sample and command/input identity | `negative_case_subplan_required` | No timeout accepted; no raw PDF/cache/provider payload may be stored | Stop: do not execute L4 under this plan |
| L5 | Evidence packaging only | future execution artifact under `docs/reviews/` | records exact commands, exit statuses, sample scope, source policy, failure table, residuals and `NOT_READY` | `evidence_incomplete`, `log_missing`, `scope_drift` | 60s timeout for packaging checks; no raw PDF body, no full provider payload, no secrets | Stop if evidence would require source/test/runtime/golden/manifest/fixture mutation |

## EID Single-source / No Fallback / NOT_READY Protection

- Future annual-report execution must use EID single-source as the only accepted
  annual-report source policy.
- Eastmoney, fund-company/CDN, CNINFO, fixture projection, cache bypass or
  fallback invocation is failure unless a separate source-expansion gate
  authorizes it.
- `not_found` and `unavailable` may be classified as eligible operational
  failures, but must not silently invoke fallback in this gate.
- `schema_drift`, `identity_mismatch` and `integrity_error` are fail-closed and
  must stop the matrix.
- Evidence may prove only bounded live/provider facts for the exact sample and
  command run.
- Evidence must not promote golden content, fixture state, readiness state,
  release state or PR state.
- Every artifact must state: release/readiness remains `NOT_READY`.

## Future Execution Evidence Artifact Requirements

The future execution artifact must include:

- exact commands and timestamps;
- exit status for every command;
- bounded sample list and source policy statement;
- redacted stdout/stderr excerpts sufficient for review;
- source provenance table by year and source;
- fallback-used table;
- quality status table without readiness promotion;
- failure classification table;
- accepted / rejected / residual fact table;
- explicit `NOT_READY` conclusion;
- next-entry recommendation that separates execution evidence from
  release/readiness and PR/external-state gates.

The future execution artifact must also explicitly state that L3 and L4 were
not executed unless a later accepted sub-plan replaces their deferred status.

## Reviewer Checklist

- Scope matches accepted inputs and current control truth.
- Write set is limited to `docs/reviews/` planning/review/controller artifacts,
  with only post-acceptance control sync.
- Future matrix is bounded by exact sample scope and command category.
- EID single-source/no-fallback policy is explicit and testable.
- Failure categories distinguish operational failure from fail-closed source
  integrity failure.
- Timeout and log redaction rules protect credentials, provider payloads and
  local cache paths.
- Stop conditions prevent fallback, source expansion, readiness promotion and
  external-state actions.
- Untracked residue is not used as truth source.
- `PASS_ACCEPTED_NON_LIVE` is not rewritten as live/provider/readiness proof.
- Final recommendation preserves `NOT_READY`.

## Next Entry Recommendation

Next entry:

`Controlled Live/Provider Evidence Execution Gate`

This execution gate requires separate explicit authorization before any
live/provider/network/LLM command is run.

Deferred entries:

- release/readiness execution or claim;
- PR/push/merge/mark-ready;
- cleanup/archive/ignore disposition;
- golden-answer promotion;
- fixture or manifest expansion;
- source expansion or fallback design;
- fee-row clarification;
- `turnover_rate` policy/scoring changes;
- other fund/year sample expansion.
