# QDII Replacement Candidate Enumeration Plan — Review (AgentDS)

> Date: 2026-05-27
> Reviewer: AgentDS (plan reviewer, not controller)
> Gate: `QDII replacement candidate enumeration plan gate`
> Plan artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-20260527.md`
> Verdict: **PASS_WITH_FINDINGS**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Startup Packet current gate | `QDII replacement candidate selection plan accepted locally` |
| Startup Packet next entry point | `QDII replacement candidate enumeration plan gate; must use init-agents / tmux multi-agent flow` |
| Plan's claimed gate | `QDII replacement candidate enumeration plan gate` |
| Latest accepted checkpoint | `8526223 docs: accept qdii replacement selection plan` |
| Design truth | `docs/design.md` (v2.2) |
| Control truth | `docs/implementation-control.md` Startup Packet §Next Entry Point |

**Result: PASS.** The plan correctly identifies itself as the Startup Packet next entry point. No gate switch or reconciliation gap.

---

## Findings

### F1 — taxonomy_status field overloads risk flags into a single column (INFO)

The `taxonomy_status` column uses long compound values that encode both eligibility and risk modifiers: `eligible_for_future_evidence_plan`, `eligible_for_future_evidence_plan_with_same-manager-family_risk`, `eligible_for_future_evidence_plan_but_active_equity`. The risk signals (same-manager-family, active-strategy) are substantive and deserve visibility, but embedding them in a status enum rather than a separate `risk_flags` or `notes` column makes the table harder to machine-consume.

**Severity:** Low. The intent is clear to a human reader and the rationale column reinforces each signal. A separate risk column would be cleaner but is not required for controller judgment.

**Recommendation:** No fix needed for this gate. Future enumeration tables may consider a dedicated `risk_flags` or `caveats` column to keep taxonomy status and risk signals separated.

### F2 — Bond QDII candidates ranked but unbounded (INFO)

`007360` and `100050` appear in the table at positions 11-12 with `qdii_bond_lower_priority` taxonomy status. The plan correctly identifies the asset-class mismatch with the failed equity QDII slot and requires controller acceptance before evidence. However, the revisit condition says `Controller / future evidence worker` — this splits ownership in a way that could lead to neither party actioning the decision.

**Severity:** Low. The controller will naturally resolve this during judgment. The plan already correctly assigns `Controller / future evidence worker` as owner, which signals shared responsibility rather than abdication.

**Recommendation:** Controller should explicitly decide in judgment whether bond QDII candidates stay in the table for future gates or are deferred until equity QDII options are exhausted.

### F3 — Row 539003 (建信富时100) classified as `taxonomy_unknown_name_lacks_qdii` while 000614 (华安DAX) has same classification but different underlying signal (POSITIVE)

Both rows lack explicit QDII naming. The plan treats them identically (taxonomy_unknown, controller decision required). This is correct and conservative. However, `539003` has an additional subtlety not flagged: its name contains `指数A` which could trigger the index-fund classification path in `fund_type.py` before QDII detection if parsed by the production classifier. This is not the plan's responsibility to resolve (it correctly defers to controller/taxonomy), but the controller should be aware that name-based classification may produce different results for `539003` and `000614` when processed through production code.

**Severity:** Info only. The plan's conservative approach is correct. The production classifier behavior is a future concern.

---

## Accepted Strengths

1. **Full CSV scan discipline verified.** Independent Python verification confirms all 15 QDII-relevant rows from the 56-row CSV appear in the candidate table. No rows were copied from the selection plan's example list — the enumeration independently derived its universe from the CSV scan.

2. **017641 exclusion is precise and fully anchored.** The plan cites the exact accepted terminal state (`disclosure_data_gap_not_baseline_ready`), provenance tuple (complete eligible fallback), quality disposition (`block`), and promotion disposition (`not_promoted`). This matches the accepted controller judgment at `docs/reviews/release-maintenance-017641-manager-strategy-text-public-evidence-triage-controller-judgment-20260527.md` line 41 and the replacement/exclusion controller judgment at `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-controller-judgment-20260527.md` line 25.

3. **QDII-FOF exclusion is correctly conditional.** `007721` and `017970` are excluded but with an explicit revisit path: "unless a separate taxonomy gate accepts QDII-FOF for this QDII replacement slot." This preserves the accepted FOF disposition (`needs_taxonomy_gate`) from the replacement/exclusion controller judgment.

4. **013308 naming/category conflict is explicitly flagged.** Row 10 carries `naming_category_conflict` taxonomy status with mandatory stop-before-evidence semantics. The plan states it "must not silently enter the evidence path until the controller accepts the conflict handling." This satisfies the mandatory explicit check required by the selection plan controller judgment (§DS F2).

5. **Source provenance discipline is strict.** All non-017641 rows are `provenance_unknown`. The plan explicitly states no candidate is source-safe, scoring-ready, golden-ready, or baseline-ready. §6 clearly enumerates future evidence requirements for proving provenance.

6. **Future evidence gate, not evidence execution.** §7-§8 recommend a future evidence plan gate with explicit requirements, stop conditions, and artifact paths. §9 lists comprehensive stop conditions against running evidence, modifying code, or promoting candidates.

7. **Boundary compliance is thorough.** §9 enumerates 13 forbidden actions covering production code, renderer, FQ0-FQ6, Service/CLI, source strategy, `FundDocumentRepository`, Host/Agent/dayu, taxonomy, extractor, quality policy, promotion, and GitHub mutation. All align with the selection plan controller judgment's non-goals.

8. **Candidate ordering rationale is transparent and defensible.** `096001` (S&P 500 equal-weight) is ranked first for closest thematic fit to the failed `017641` S&P 500 slot; `040046` (Nasdaq-100) and `019172` (Nasdaq-100, same fund family risk) follow; regional/single-market QDII fills later positions; active QDII and bond QDII are deliberately de-prioritized. The rationale for each rank is explicit.

---

## Controller Question: 096001 as Single Candidate

**Question:** May `096001` be used as the single candidate for the next future evidence plan gate, without treating it as source-safe or promoted?

**Answer: YES**, with the following qualifications:

- The plan recommends `096001` as a **planning recommendation only**, subject to controller review and judgment. It does not claim `096001` is source-safe, quality-passing, promoted, or accepted.
- The plan explicitly lists unresolved risks for `096001`: `provenance_unknown`, quality unknown, possible P0 `manager_strategy_text` block, and unverified CLI flags (§7).
- The plan's fallback ordering (§7) names `040046` then `019172` then remaining equity QDII rows if `096001` fails. This ensures the controller's acceptance of `096001` as single candidate does not create a single-point-of-failure deadlock.
- Controller should confirm in judgment that accepting `096001` as the single evidence candidate does **not** constitute accepting it as a QDII replacement, promoting it, or bypassing provenance/quality stop conditions.

---

## Required Fixes Before Acceptance

None. No finding is blocking.

---

## Residual Risks for Controller

| Risk | Severity | Mitigation |
|---|---|---|
| `096001` may fail source provenance or P0 quality at evidence gate, requiring fallback | Medium | Plan provides fallback order (`040046` → `019172` → ...). Controller should ensure this fallback chain is preserved in the judgment. |
| `019172` same-manager-family risk (`摩根`) may indicate shared disclosure template issues with failed `017641` | Low | Plan flags this in taxonomy_status. The evidence gate will test it through public CLI paths regardless. |
| `013308` QDII-name vs domestic-stock CSV category conflict remains unresolved | Low | Plan correctly defers to controller/taxonomy. Risk is contained: no evidence runs on `013308` without resolution. |
| Bond QDII candidates (`007360`, `100050`) may create asset-class scope creep | Low | Plan ranks them last and requires explicit controller acceptance. Controller should decide in judgment whether they remain in-scope. |
| Taxonomy classification of non-QDII-named overseas funds (`539003`, `000614`) may differ from production `classify_fund_type()` output | Low | Deferred to controller/taxonomy gate. Not an enumeration-plan defect. |

---

## Review Matrix Compliance

The plan's §10 Review Matrix correctly identifies this artifact path and review scope. All four review focus items are addressed above:

- Full CSV scan discipline: **confirmed** (Accepted Strength 1)
- `017641` and QDII-FOF exclusions: **confirmed** (Accepted Strengths 2-3)
- `013308` naming/category conflict flag: **confirmed** (Accepted Strength 4)
- Source provenance not invented: **confirmed** (Accepted Strength 5)
- `096001` only recommended, not accepted replacement: **confirmed** (Controller Question answer)
- Future evidence requirements are plan-only: **confirmed** (Accepted Strengths 6-7)

---

## Validation

| Check | Result |
|---|---|
| Plan artifact exists at expected path | Yes |
| `git diff --check` reported in plan §11 | Passed (exit 0) |
| CSV scan Python command reported in plan §11 | Passed (exit 0, 56 rows) |
| This review artifact written to required path | Yes |
| No code, test, design doc, control doc, or GitHub mutation performed | Confirmed |
