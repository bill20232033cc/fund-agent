# Post-P19 Next Phase Selection（2026-05-23）

## 1. Gate / Role

- **Role**: Controller next-phase selection, not implementation.
- **Current branch**: `phase/p19-s5-all-a-pe-source-gate`.
- **Current PR**: PR 13, `ready for review`, CI `test` SUCCESS, mergeState `CLEAN`.
- **Current gate**: `P19-S5 draft-PR-pass`.
- **Design truth**: `docs/design.md` v2.2.
- **Control truth**: `docs/implementation-control.md`.

This artifact selects the next safe work unit after PR 13. It does not merge PR 13, approve PR 13, request reviewers, change external GitHub state, or implement code.

## 2. Decision

Recommended next gate:

```text
P19-S6 production validation and comparison plan-review
```

This gate should start only after PR 13 is merged and a fresh branch is created from updated `main`. Continuing feature work on top of PR 13 would make the PR carry unrelated planning or implementation diff and increase rebase risk.

P19-S6 should be a planning/review gate first. Implementation may start only after the plan defines exact files, fixtures, live-smoke boundaries, success signals, and stop conditions.

## 3. First-Principles Rationale

P19 has already built the core self-owned thermometer path for `000300`, `000905`, and `wind_all_a`, including automatic `valuation_state` integration for exact supported benchmark identities. The remaining highest-value gap is not another broad feature. It is validating the production behavior that now affects `fund-analysis analyze`.

The next phase should therefore prove that the new thermometer integration is stable and observable in realistic user workflows:

- 3 sample fund CLI end-to-end validation remains unchecked in the P19 exit criteria.
- Directional comparison against the transitional public-page thermometer remains unchecked.
- Live `akshare/Legulegu` availability and native dependency behavior now has known production risk after the `libmini_racer` crash report.
- P19-S4 expanded-index coverage is blocked by missing exact PE+PB sources, so pushing it next would likely repeat source-feasibility failure instead of improving shipped confidence.

## 4. Candidate Comparison

| Candidate | Value | Risk | Boundary fit | Decision |
|---|---:|---:|---|---|
| **P19-S6 production validation and comparison** | High: closes remaining P19 exit criteria and hardens real CLI/analyze behavior | Medium: live data can be flaky, so plan must separate deterministic tests from bounded smoke | Strong: uses existing Service/CLI contracts without new architecture | **Selected** |
| P19-S4 expanded-index source gate retry | Medium: adds more index coverage if sources exist | High: previous source feasibility found no exact PE+PB source | Acceptable only as a later source-research gate | Defer |
| P19 production hardening cleanup | Medium: retry-budget harmonization, wording cleanup, legacy adapter cleanup | Low-medium | Good, but less valuable than proving current user workflows | Defer behind validation |
| E1-E3 / Evidence Confirm | High long-term audit value | High architecture risk | Separate v2 audit phase, not thermometer closeout | Defer |
| Repo hygiene / review archive cleanup | Medium maintainability value | Medium process risk | Docs-only phase possible later | Defer |

## 5. Recommended P19-S6 Scope

P19-S6 plan should define a code-generation-ready implementation plan for:

1. **3 sample fund CLI end-to-end validation**
   - Select existing deterministic sample inputs already used in tests.
   - Validate `fund-analysis analyze` completes with explicit or auto `valuation_state` behavior.
   - Preserve exact benchmark identity rules: only `000300` / `000905` supported index identities may call the thermometer automatically.

2. **Thermometer live-smoke contract**
   - Keep deterministic unit/integration tests separate from live smoke.
   - Add or document bounded smoke commands for:
     - `fund-analysis thermometer --json`
     - `fund-analysis thermometer --index 000300 --json`
     - `fund-analysis thermometer --index wind_all_a,000300,000905 --json`
   - Live smoke failures must be reported as environment/source availability signals, not deterministic test failures unless explicitly opted in.

3. **Public-page comparison as non-production signal**
   - Use the legacy public-page adapter only as transitional comparison input.
   - Do not use public-page values as production truth or fallback.
   - Compare direction or broad bucket only; do not require exact value equality.

4. **Known production-risk hardening checks**
   - Verify no new concurrent `akshare/Legulegu/libmini_racer` entry paths are introduced.
   - Preserve all explicit unavailable provenance and user-visible disclaimer behavior.
   - Keep unsupported / ambiguous benchmark mapping fail-closed.

5. **Documentation and residual tracking**
   - Update P19 exit criteria only after validation exists and passes.
   - Keep P19-S4 exact-index PE+PB unresolved items deferred with owner.
   - Keep production `tracking_error` golden residuals outside this phase.

## 6. Non-goals

- Do not merge or alter PR 13 without explicit user authorization.
- Do not implement P19-S6 on the PR 13 branch before PR 13 is merged.
- Do not add new supported index codes without an exact PE+PB source feasibility gate.
- Do not use 有知有行 public-page scraping as production thermometer fallback.
- Do not introduce Dayu Host/Engine/tool loop, LLM writing, Evidence Confirm, or calculated tracking error.
- Do not broaden automatic `valuation_state` mapping to active, bond, QDII, FOF, ambiguous, or multi-index benchmarks.
- Do not put explicit parameters in `extra_payload`.

## 7. Recommended Handoff After PR 13 Merge

```text
Gate: P19-S6 production validation and comparison plan-review.

Start from updated main after PR 13 is merged.
Use `docs/design.md` §11 and `docs/implementation-control.md` P19 exit criteria as truth.
Create `docs/reviews/p19-s6-production-validation-plan-20260523.md`.

The plan must define deterministic tests, optional live smoke, public-page comparison boundaries, exact unsupported benchmark behavior, and doc/control update triggers.
Do not implement source/test changes until plan review passes.
Do not use public-page data as production fallback.
Stop if new index coverage, external data sources, E1-E3/Evidence Confirm, Dayu runtime, or calculated tracking error becomes necessary.
```

## 8. Current Stop Condition

The controller should stop at this selection artifact unless the user explicitly authorizes one of:

- merge PR 13;
- start a stacked planning branch on top of PR 13;
- choose a different next phase.
