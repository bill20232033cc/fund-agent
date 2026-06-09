# EID Single Source Operational Hardening Truth-Doc Revision Plan — AgentDS Targeted Re-Review

## Gate

| Item | Value |
|---|---|
| Gate | `EID Single Source Operational Hardening Gate` — truth-doc revision plan targeted re-review |
| Reviewer | AgentDS (plan review worker, not controller) |
| Review target | `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md` (revised) |
| Prior DS review | `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-review-ds-20260609.md` |
| MiMo review | `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-review-mimo-20260609.md` |
| Controller judgment | `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-review-controller-judgment-20260609.md` |
| Date | 2026-06-09 |
| Classification | `heavy` (per steering judgment) |

## Source Evidence Read

- Revised plan (this re-review's subject)
- Prior DS review (source of accepted blocking findings)
- MiMo review
- Controller judgment (source of required fixes)

## Scope

Targeted re-review only. Checks restricted to the 6 controller-accepted required fix dimensions listed in the prior DS review targeted re-review criteria (lines 191–198) and the controller judgment's required revision list (lines 35–51).

No source code, tests, README, truth docs, or other files were modified. No live commands were run.

---

## Finding-by-Finding Verification

### Fix 1: Control doc EID-not-exclusive / multi-official-url conflict inventoried

**Required**: Add explicit conflict inventory entry for the statement that EID is preferred locator but not exclusive source truth, and that `official_document_url` may come from fund-company website/CDN, CNINFO, or other platforms.

**Revised plan**: Line 55 — new row `Control doc source-truth policy` in the conflict inventory table.

> "`docs/implementation-control.md` currently says EID is a preferred official registry locator but not a mandatory automatic extraction source or exclusive source truth, and says `official_document_url` may come from EID, fund-company website/CDN PDF, CNINFO PDF, or another official/first-party disclosure platform"

Target stance: "Rewrite to `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`; relabel non-EID routes as deferred candidates or historical evidence-intake routes only."

**Verdict**: FIXED. Conflict is explicitly inventoried with exact current wording and exact revision target.

---

### Fix 2: Control doc `not_found` / `unavailable` fallback-eligible conflict inventoried

**Required**: Add explicit conflict inventory entry for the statement that `not_found` / `unavailable` remain fallback-eligible.

**Revised plan**: Line 56 — new row `Control doc fallback eligibility` in the conflict inventory table.

> "`docs/implementation-control.md` currently says `not_found` / `unavailable` remain fallback-eligible while `schema_drift` / `identity_mismatch` / `integrity_error` fail closed"

Target stance: "Rewrite `not_found` / `unavailable` as terminal EID source failures that do not authorize fallback in this gate; preserve fail-closed semantics for `schema_drift`, `identity_mismatch`, and `integrity_error`."

**Verdict**: FIXED. Conflict is explicitly inventoried with exact current wording and exact revision target.

---

### Fix 3: Slice 2 and Slice 3 both have corresponding revision targets

**Required**: Slice 2 (control doc) and Slice 3 (startup packet) must both include explicit revision targets for the two new conflicts.

**Revised plan — Slice 2** (lines 305–307):
- Line 305: "Replace the current control-doc statement that EID is a preferred locator but not exclusive source truth; the revised target must state `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`."
- Line 306: "Replace the current control-doc statement that `official_document_url` may come from EID, fund-company website/CDN PDF, CNINFO PDF, or other official/first-party platforms; the revised target must make non-EID routes deferred candidates or historical evidence-intake routes only."
- Line 307: "Replace the current control-doc statement that `not_found` / `unavailable` are fallback-eligible; the revised target must state they are terminal EID source failures under `single_source_only` and do not authorize fallback."

**Revised plan — Slice 3** (lines 324–325):
- Line 324: "If the startup packet mirrors or summarizes the old control-doc policy, replace any statement that EID is non-exclusive or that `official_document_url` may currently come from fund-company website/CDN, CNINFO, or other first-party routes; these routes must be deferred/historical evidence only."
- Line 325: "If the startup packet mirrors or summarizes fallback eligibility, replace any statement that `not_found` / `unavailable` authorize fallback; under `single_source_only` they are terminal EID source failures."

**Verdict**: FIXED. Both slices have explicit, falsifiable revision targets tied to the two new conflicts. Slice 3 appropriately uses conditional language ("If the startup packet mirrors or summarizes...") since the startup packet is a shorter document and may not duplicate all control-doc policy statements.

---

### Fix 4: No-live validation matrix falsifiable per doc for all three policy values

**Required**: Make the validation matrix independently verify `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false` for each target doc — no loose OR false-pass.

**Revised plan** (lines 360–368): 9 independent rows:

| Check | Command | Doc |
|---|---|---|
| selected source | `rg -n "selected_source=eid" docs/design.md` | design |
| mode | `rg -n "mode=single_source_only" docs/design.md` | design |
| fallback disabled | `rg -n "fallback_enabled=false" docs/design.md` | design |
| selected source | `rg -n "selected_source=eid" docs/implementation-control.md` | control |
| mode | `rg -n "mode=single_source_only" docs/implementation-control.md` | control |
| fallback disabled | `rg -n "fallback_enabled=false" docs/implementation-control.md` | control |
| selected source | `rg -n "selected_source=eid" docs/current-startup-packet.md` | startup |
| mode | `rg -n "mode=single_source_only" docs/current-startup-packet.md` | startup |
| fallback disabled | `rg -n "fallback_enabled=false" docs/current-startup-packet.md` | startup |

Each row uses exact string matching against a single file. Missing any one value in any one doc produces zero hits for that row — unambiguously falsifiable. The remaining rows (lines 369–373) preserve the original cross-cutting checks for fallback wording, row-shape, FDR boundary, dayu/extra_payload, and formatting.

**Verdict**: FIXED. The matrix is now fully falsifiable. A revision worker cannot pass validation if any target doc is missing any of the three policy values.

---

### Fix 5: No new authorization introduced

**Check**: Compare non-goals, forbidden files, and authorization boundaries with the accepted baseline (original plan before revision).

- Non-goals (lines 33–46): unchanged — no source/test/README/live/FDR/fallback/commit/PR.
- Forbidden files (lines 244–258): unchanged — same explicit list.
- No live/network/PDF/FDR/fallback/provider commands authorized.
- No implementation, commit, push, or PR authorized.
- The revision added only conflict inventory rows, slice change bullets, and validation matrix rows — none of which authorize new actions.

**Verdict**: NO REGRESSION. All authorization boundaries remain intact.

---

### Fix 6: Eastmoney deferred risk and row-shape queued/paused preserved

**Eastmoney disposition** (lines 197–210): unchanged from accepted baseline — `deferred-with-owner`, owner "future source-candidate or fallback implementation gate," not current implementation target.

**Row-shape disposition** (lines 212–225): unchanged — "queued / paused by steering," "not rejected, deleted, or converted," four specific residuals preserved.

**Current code fact vs accepted target separation** (lines 74–88): unchanged — four label types and required/fobidden wording discipline preserved.

**Verdict**: NO REGRESSION. All dispositions remain aligned with steering.

---

## Regression Check Summary

| Area | Status |
|---|---|
| Conflict inventory completeness | 2 new rows added; 7 total rows covering all known conflicts |
| Slice 2 revision targets | 8 steps (was 8, 3 made more specific per controller fix) |
| Slice 3 revision targets | 6 steps (was 4, 2 added per controller fix) |
| Validation matrix | 13 rows (was 5, now 9 per-doc-per-value + 4 cross-cutting) |
| Non-goals | unchanged |
| Forbidden files | unchanged |
| Eastmoney disposition | unchanged |
| Row-shape disposition | unchanged |
| Direct evidence matrix | unchanged |
| Stop conditions | unchanged |
| Residual risks | unchanged |

---

## Verdict

**Verdict: PASS**

All six targeted re-review criteria are met:
1. ✅ Control doc EID-not-exclusive / multi-official-url conflict explicitly inventoried (line 55)
2. ✅ Control doc `not_found`/`unavailable` fallback-eligible conflict explicitly inventoried (line 56)
3. ✅ Slice 2 (lines 305–307) and Slice 3 (lines 324–325) both have corresponding revision targets
4. ✅ Validation matrix (lines 360–368) independently verifies all three policy values per target doc — fully falsifiable
5. ✅ No new authorization introduced — non-goals, forbidden files, and boundaries unchanged
6. ✅ Eastmoney deferred risk and row-shape queued/paused preserved

Zero blocking findings. Zero non-blocking findings. No regression from accepted baseline.

## Acceptance Recommendation

**Accept.** The revised plan is code-generation-ready for truth-doc revision. Proceed to controller judgment for plan acceptance and authorization of truth-doc revision.
