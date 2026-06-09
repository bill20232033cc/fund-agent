# EID Single Source Operational Hardening Truth-Doc Revision Plan — AgentDS Review

## Gate

| Item | Value |
|---|---|
| Gate | `EID Single Source Operational Hardening Gate` — truth-doc revision plan review |
| Reviewer | AgentDS (plan review worker, not controller) |
| Review target | `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md` |
| Date | 2026-06-09 |
| Classification | `heavy` (per steering judgment) |

## Source Evidence Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md`
- `docs/reviews/repo-review-20260609-165959.md`
- `docs/reviews/mvp-eid-single-source-operational-hardening-steering-judgment-20260609.md`
- Target plan (this review's subject)

## Scope Self-Check

- This review is a read-only artifact under `docs/reviews/`.
- No source code, tests, README, truth docs, or other files were modified.
- No live EID/network/PDF/FDR/fallback/provider commands were run.
- No commit, push, or PR was performed.

---

## Findings

### [BLOCKING] Implementation-control.md explicit conflicts not inventoried in plan conflict table or Slice change lists

**File**: `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md`
**Location**: §Current Control Truth vs Target Conflict Inventory (lines 50–58), §Slice 2 (lines 284–299), §Slice 3 (lines 301–313)

**Evidence**:

The plan's conflict inventory table (lines 50–58) covers design.md source policy, Eastmoney, fund-company-site, live/source acquisition, and boundary — but **only cites design.md conflicts**. Two critical conflicts in `docs/implementation-control.md` are not explicitly listed:

1. **Line 9** of `docs/implementation-control.md` states:
   > "EID is preferred official registry locator, **not a mandatory automatic extraction source or exclusive source truth**; official_document_url may come from EID, fund-company official website/CDN PDF, CNINFO PDF or another official/first-party disclosure platform under the recorded anchor rules."

   This directly contradicts the steering target `selected_source=eid`, `mode=single_source_only`. EID under single-source mode IS the exclusive source truth; fund-company/CDN/CNINFO are NOT valid production source routes. A revision worker who only follows Slice 2/3 change lists may miss this line and leave it in place as standing policy.

2. **Line 63** of `docs/implementation-control.md` states:
   > "年报来源 fallback 继续按 `not_found` / `unavailable` eligible，`schema_drift` / `identity_mismatch` / `integrity_error` fail-closed。"

   This asserts fallback IS eligible for `not_found`/`unavailable`, which contradicts `fallback_enabled=false`. Under single-source mode, even `not_found`/`unavailable` do not authorize fallback — they are terminal EID source failures. A revision worker following the current Slice 2 change list may not recognize this as a required revision target.

**Impact**: A truth-doc revision worker executing this plan could leave both conflicting statements in `docs/implementation-control.md` unchanged, resulting in post-revision docs that internally contradict themselves (e.g., control doc simultaneously says "single_source_only, fallback_enabled=false" AND "EID is not exclusive source truth" / "fallback eligible for not_found/unavailable"). This would fail the Slice 4 consistency check but only after wasted revision work.

**Why BLOCKING**: The plan's stated goal is to "make source-policy truth unambiguous." Leaving specific conflicting lines unidentified in the plan means the plan is not code-generation-ready for the truth-doc revision worker — the worker would need to discover these conflicts independently, which is exactly what the plan is supposed to prevent.

**Minimum fix**: Add two rows to the conflict inventory table (or two bullet items to Slice 2 exact changes):
- Implementation-control line 9 (EID-not-exclusive-source-truth statement) → rewrite to EID single-source target
- Implementation-control line 63 (fallback-eligible statement) → rewrite to fallback_enabled=false, single_source_only terminal EID failures

Also add corresponding revision targets in Slice 2 (control doc) and Slice 3 (startup packet, which inherits from control doc).

---

### [BLOCKING] No-live validation matrix does not check `fallback_enabled` across all three target docs nor verify cross-document EID policy consistency

**File**: `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md`
**Location**: §No-Live Validation Matrix (lines 337–343)

**Evidence**:

The validation matrix at line 339 checks:
```
rg -n "selected_source|single_source_only|fallback_enabled" docs/design.md docs/implementation-control.md docs/current-startup-packet.md
```
with expected result: "Finds EID policy in all relevant truth docs after revision."

However, the `rg` alternation `selected_source|single_source_only|fallback_enabled` can match any ONE of these three terms. A false-pass could occur if:
- `docs/design.md` contains `selected_source=eid` but omits `fallback_enabled=false`
- `docs/current-startup-packet.md` contains `single_source_only` but omits `selected_source=eid`
- Any doc mentions one term without the others

The expected result description is qualitative ("Finds EID policy in all relevant truth docs") without specifying WHAT constitutes a valid match. A revision worker could pass this check with incomplete policy wording.

Additionally, the matrix checks for `FundDocumentRepository|extra_payload|dayu-agent|dayu.host|dayu.engine` as a combined grep (line 342), which correctly verifies these terms appear (for FDR) or don't appear as production authorization (for dayu/extra_payload). But the matrix has no explicit check that `fallback_enabled=false` appears in every doc that mentions `selected_source=eid`.

**Why BLOCKING**: For a heavy gate changing source policy, the validation must be falsifiable — a reviewer should be able to look at the output and unambiguously determine pass/fail. The current matrix leaves ambiguity that could let incomplete revisions pass validation.

**Minimum fix**: Split the EID policy check into at least two independent checks:
1. `rg -c "selected_source=eid"` per doc — assert count ≥ 1 in each
2. `rg -c "fallback_enabled=false"` per doc — assert count ≥ 1 in each
Or define a more precise pattern like `rg -n "selected_source.*eid|single_source_only|fallback_enabled.*false"` and document that all three terms must appear in each target doc.

---

### [NON-BLOCKING] Slice 0 baseline does not require recording exact conflicting line numbers before revision

**File**: `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md`
**Location**: §Slice 0 (lines 252–265)

**Evidence**: Slice 0 step 1 says "Re-read branch/status and the six required files." It doesn't require the worker to record exact line numbers of conflicting statements (e.g., design.md:650, 655, 707, 961, 1092; implementation-control.md:9, 63). Without a concrete baseline, a re-reviewer cannot confirm that all conflicts were addressed without re-reading entire files.

**Impact**: Minor — a competent revision worker should find all conflicts. But for a heavy gate, the extra specificity reduces re-review burden.

**Recommendation**: Add to Slice 0: "Record exact line numbers of every current statement that conflicts with EID single-source policy in a baseline evidence artifact."

---

### [NON-BLOCKING] Plan's Slice 1 §6.1 reference assumes design.md section numbering without verifying current structure

**File**: `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md`
**Location**: §Slice 1 (lines 269–282), sub-bullet "§6.1 document repository layer"

**Evidence**: The plan references `§6.1 document repository layer` as the target section in design.md. The current `docs/design.md` does have a §6.1 (line 640: "### 6.1 文档仓库层"). However, the related fallback strategy table (lines 653–667) is under the same §6.1 but the external data table (§6.3, line 703) and decision comparison table (line 1092) also contain source-policy wording that needs revision. These are correctly identified in the plan's broader Slice 1 scope, so the §6.1 reference is accurate but incomplete as a standalone reference.

**Impact**: Low — the plan's broader Slice 1 description covers all needed sections. A revision worker reading the full Slice 1 scope will find all targets.

**Recommendation**: No fix required; this is an observation only.

---

### [INFO] Eastmoney finding disposition is correctly scoped as deferred risk

**File**: `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md`
**Location**: §Eastmoney Finding Disposition (lines 189–200)

**Confirmation**: The plan correctly:
- Marks the repo-review Eastmoney integrity-classification finding as `deferred-with-owner`
- Assigns owner as "future source-candidate or fallback implementation gate"
- Uses it only as risk evidence for why Eastmoney must not appear as production fallback
- Does NOT authorize Eastmoney code repair, tests, or live validation
- Does NOT treat it as current implementation scope

This aligns with steering judgment and review scope requirement #5.

---

### [INFO] Row-shape residual gate disposition is correctly preserved

**File**: `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md`
**Location**: §Row-Shape Residual Gate Disposition (lines 202–215)

**Confirmation**: The plan correctly:
- Marks row-shape gate as `queued / paused by steering`
- Explicitly says "not rejected, deleted, or converted into this source-policy gate"
- Preserves the four specific residuals: `manager`, retained `risk`, `006597` bond top holding, `110020` target ETF holding
- This aligns with steering judgment and review scope requirement #6.

---

## Pass Items (Confirmed by Direct Evidence)

| Review scope item | Plan location | Verdict |
|---|---|---|
| `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false` | Lines 36–38, 64–68, 89–98 | PASS — policy wording is exact |
| No Eastmoney production fallback | Lines 55 (Eastmoney row), 89–98 (forbidden wording), 189–200 | PASS — explicitly deferred |
| No fund-company-site production path | Lines 56, 89–98 | PASS — deferred candidate only |
| FundDocumentRepository single entry preserved | Lines 58, 94, 117–118 | PASS — boundary kept |
| UI/Service/Host/renderer/quality gate not calling sources directly | Lines 94, 117, 185 | PASS — prohibition preserved |
| Current code fact vs accepted target separation | Lines 72–86 (separation rules), 88–98 (required/forbidden wording) | PASS — explicit labelling discipline |
| Eastmoney repo-review finding not scope-drifted to implementation | Lines 189–200 | PASS — deferred-with-owner only |
| Row-shape residual queued/paused | Lines 202–215 | PASS — queued, not deleted |
| No-live/no-FDR/no-fallback/no-code/no-test/no-commit/no-PR | Lines 33–46 (non-goals), 345–350 (forbidden validation) | PASS — complete |
| No dayu runtime dependency introduced | Lines 45, 96 | PASS — prohibition preserved |
| No extra_payload authorization | Lines 46, 96 | PASS — prohibition preserved |
| Allowed/forbidden files explicit | Lines 219–247 | PASS — explicit and complete |
| Stop conditions defined | Lines 387–396 | PASS — covers all scope-violation scenarios |
| Residual risks inventoried | Lines 398–406 | PASS — with owners and destinations |
| Direct evidence matrix present | Lines 352–361 | PASS — each evidence source mapped to plan consequence |

---

## Verdict

**Verdict: BLOCKED**

Two blocking findings:
1. Implementation-control.md explicit conflicts (lines 9, 63) not inventoried in conflict table or Slice change lists
2. No-live validation matrix allows false-pass on incomplete EID policy wording

Both have minimal fixes (add ~4 lines to conflict inventory, split one grep check into two). No architectural or scope-level issues found.

## Acceptance Recommendation

**accept-with-fixes** — address the two blocking findings above, then re-submit for targeted re-review. No plan-level redesign needed. The plan's architecture, scope boundaries, slice decomposition, stop conditions, and residual risk inventory are all sound.

---

## Targeted Re-Review Criteria

If the plan is revised, targeted re-review should confirm:

1. Implementation-control.md line 9 and line 63 conflicts are explicitly listed in the conflict inventory table.
2. Slice 2 and Slice 3 exact changes include rewriting or removing these specific statements.
3. Validation matrix EID policy check is split to independently verify `selected_source=eid` and `fallback_enabled=false` per target doc, OR the expected-result description is tightened to define a falsifiable pass condition.
4. No new authorization (live/source/test/code/fallback/commit/PR) was introduced.
5. Allowed/forbidden files remain unchanged.
6. Eastmoney and row-shape dispositions remain aligned with steering.
