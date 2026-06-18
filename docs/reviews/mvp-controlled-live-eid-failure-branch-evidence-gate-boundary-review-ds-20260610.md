# DS Boundary Review: Controlled Live EID Failure-Branch Evidence Gate — 2026-06-10

## Verdict

**BLOCKED_FOR_PLAN**. This gate must not proceed directly to live execution. A controller-authorized controlled-live plan artifact with independent review is required first.

## Review Questions

### 1. Minimum controlled live evidence that adds value beyond accepted no-live evidence

**Classification: reviewer opinion.**

Accepted no-live evidence (`ac6bbe9`) already proves all five failure categories through `httpx.MockTransport`, fake sources, and direct parser/helper tests — 35 passing, zero production code changes. The no-live boundary is fully characterized.

The only live evidence that adds value: observe what happens when EID is **actually** unavailable or **actually** misbehaves. But a controlled gate **cannot and must not induce** real EID failures (network sabotage, DNS manipulation, config corruption). Therefore:

- If exactly one unchanged-default live EID acquisition runs for a known-good `(fund_code, year)` and **succeeds**: the live evidence adds zero new information. It confirms the no-live boundary holds but proves no failure branch.
- If it **naturally fails**: classify the actual failure against the five categories, document it, and stop. Do not retry, probe, or induce more failures.
- No multi-row sweep, no parameter fuzzing, no `not_found` induction via fake fund codes.

The residual is: live failure branches remain unprovable by controlled live evidence unless EID naturally fails during the window. This must be explicitly accepted as a residual in any live plan.

### 2. Failure branches realistically observable live vs residual only

**Classification: truth-doc fact + reviewer opinion.**

| Category | Observable live? | Basis |
|---|---|---|
| `unavailable` | **Possibly** — if EID servers are down, network blips, or timeouts occur naturally | design.md §P8-S3: `unavailable` = network/timeout/service temporary; this is the one category that can happen without EID schema/code change |
| `not_found` | **Only with parameter manipulation** — would require querying a known-nonexistent fund code, which is not a production-path failure branch but a parameter-driven test | No-live evidence already covers this via MockTransport; using a fake fund code in a live command is scope creep, not failure-branch observation |
| `schema_drift` | **Residual only** — requires EID to change API response shape. Cannot trigger from client side | design.md: fail-closed; no client-side induction possible |
| `identity_mismatch` | **Residual only** — requires EID to return wrong fund/year. Cannot trigger without EID bug | design.md: fail-closed |
| `integrity_error` | **Residual only** — requires EID to serve corrupt PDF bytes. Cannot trigger without EID infrastructure corruption | design.md: fail-closed |

Accepted residual: `schema_drift`, `identity_mismatch`, and `integrity_error` live branches are **not realistically observable** under controlled conditions. Any live plan must explicitly accept this and not attempt to induce them.

### 3. Forbidden actions to prevent fallback/weekly-CI reintroduction

**Classification: repo fact.** Source: `AGENTS.md`, `docs/design.md` §P8-S3, `docs/implementation-control.md` §Prohibited Actions, `docs/current-startup-packet.md` §6.

Must forbid:

| Forbidden action | Truth source |
|---|---|
| `fallback_enabled=true` or multi-source construction without a separate `heavy` gate | design.md: current production default is `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false` |
| Eastmoney, CNINFO, fund-company official website/CDN source activation, import, or construction in production path | design.md: "仅保留为 deferred source candidate / historical evidence route" |
| Any scheduled, periodic, recurring, or automated live EID command (weekly CI, cron, watchdog) | implementation-control.md next entry: "only with separate explicit live authorization" — each live run must be individually authorized |
| Provider/default/runtime/budget/config change | implementation-control.md §Prohibited Actions: "Do not modify runtime code outside the active MVP gate scope" |
| `not_found` / `unavailable` reclassification as multi-source-fallback-eligible in production | design.md §P8-S3: under `single_source_only`, these are terminal EID source failures |
| Relaxing fail-closed for `schema_drift` / `identity_mismatch` / `integrity_error` | AGENTS.md: "必须 fail-closed，禁止被 Eastmoney fallback 静默掩盖" |
| More than one live command per authorization | Consistent precedent: all accepted provider live evidence gates limit to exactly one unchanged-default command |
| Fixture projection, golden/readiness promotion, downstream implementation | implementation-control.md and startup packet non-goals |

### 4. Stop conditions that must block live execution

**Classification: repo fact + truth-doc fact.**

| Stop condition | Rationale |
|---|---|
| E1 typed config readiness check fails | Precedent from provider live evidence: readiness must pass before any live command |
| Any code, config, source-policy, or test change is required before running the live command | The gate scope is evidence, not implementation |
| The live command cannot be expressed as exactly one `fund-analysis analyze --use-llm` or exactly one `FundDocumentRepository.load_annual_report()` call with unchanged defaults | Precedent: all accepted live evidence uses exactly one unchanged-default command |
| The live command would induce failure (network disruption, DNS manipulation, config corruption, fake fund codes) | design.md non-goals: no source-policy change; inducing failure is not the same as observing natural failure |
| stdout cannot be independently captured and measured | Precedent from provider live evidence: `stdout byte count` must be independently measured |
| The run would change provider/default/runtime/budget | implementation-control.md: provider/runtime defaults unchanged |
| The run would produce partial accepted evidence that could be misread as live failure-branch proof | Fail-closed: incomplete = not accepted |
| Any fallback source construction or activation | design.md §P8-S3: single_source_only |
| More than one run is attempted | Precedent: one run per authorization |

### 5. Direct live execution vs controller plan artifact and review first

**Classification: reviewer opinion. Finding: BLOCKER.**

This gate must NOT proceed directly to live execution. It must first produce a **controlled-live plan artifact** with independent review and controller judgment.

Basis:

- **Gate classification is `heavy`**: source policy, `FundDocumentRepository`/PDF/network/source access, and failure-branch semantics all trigger `heavy` per `AGENTS.md` gate classification rules. `heavy` gates require plan/review/implementation/validation matrix.
- **Consistent precedent**: every prior live evidence gate (provider smoke, provider runtime, post-operator rerun, post-config live smoke) followed plan → plan review → controller judgment → evidence → evidence review → controller judgment → control sync. No prior live gate skipped the plan phase.
- **Three risks that a plan must explicitly address**:
  1. **Observer effect risk**: a live command that succeeds may be misread as "failure branches don't exist" rather than "failure didn't happen to occur." The plan must define what success means and what it does NOT prove.
  2. **Scope creep risk**: without a reviewed plan, a live gate could drift into multi-row sweeps, parameter fuzzing, or retry loops. The plan must pin the exact command and stop conditions.
  3. **Fallback reauthorization risk**: any language about "observing EID unavailability" could be misread as justification for fallback. The plan must explicitly reaffirm that Eastmoney/CNINFO/fund-company remain forbidden.

**Required plan contents** (minimum):
- Exact single live command (fund code, year, full CLI invocation or repository call)
- E1 readiness pre-check command
- Expected outcomes matrix: succeed / `unavailable` / other natural failure
- Explicit statement: success proves nothing about failure branches
- Explicit statement: all five no-live categories remain proven only no-live
- Explicit reaffirmation of all §3 prohibitions
- Stop conditions from §4
- Residual acceptance: `schema_drift`, `identity_mismatch`, `integrity_error` live observation is not realistically achievable
- Minimum two independent reviews before controller judgment authorizes live execution

## Summary

| Point | Classification |
|---|---|
| Minimum live evidence is one unchanged-default command; success proves nothing | Reviewer opinion |
| Only `unavailable` is realistically observable; `schema_drift`/`identity_mismatch`/`integrity_error` are residual only | Truth-doc fact + reviewer opinion |
| Eastmoney/CNINFO/fund-company activation, multi-source, weekly CI, and fail-closed relaxation must be forbidden | Repo fact |
| Stop conditions: readiness fail, code/config change needed, induced failure, uncaptured stdout, partial evidence, >1 run | Repo fact + truth-doc fact |
| BLOCKED_FOR_PLAN: controller plan artifact with independent review required before live execution | Reviewer opinion — **BLOCKER** |
