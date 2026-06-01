# Bond Positive-Risk Evidence Review — MiMo

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Role: independent evidence reviewer (not controller)
> Artifact reviewed: `docs/reviews/release-maintenance-bond-positive-risk-evidence-20260527.md`
> Accepted plan: `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-20260527.md`
> Controller judgment: `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-controller-judgment-20260527.md`

## Verdict

**PASS_WITH_FINDINGS**

## Review Basis

Truth sources consulted:

- `AGENTS.md` (including Gate 轻重分类规则)
- `docs/design.md` current sections (architecture, FundDocumentRepository boundaries, quality gate design)
- `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point
- Accepted plan and controller judgment artifacts
- `fund_agent/fund/extraction_score.py` (bond_risk_evidence.v1 group definitions, issue ID generation)
- Plan review artifacts: AgentDS review, AgentMiMo review and re-review

## Criterion 1: Evidence Collection Scope and Source Boundaries

**PASS**

- Public CLI commands (`extraction-snapshot`, `extraction-score`, `quality-gate`) are exactly those authorized in the accepted plan §3 Step A.
- Repository inspection used `FundDocumentRepository().load_annual_report("006597", 2024)` — the exact shape authorized in the plan §3 Step B.
- No PDF path, cache path, concrete source helper, download helper, Eastmoney helper, EID helper, renderer, extractor, or quality-gate internals were accessed.
- Boundary confirmation in evidence artifact §4 is explicit and complete.
- Output was limited to concise section/table locators and keyword contexts, consistent with the plan's "concise candidate locators" requirement.

## Criterion 2: Command Results and Artifact Sufficiency

**PASS**

- All commands in §2 are listed with exit codes; all returned 0.
- Public artifacts in §3 match the plan's inspection table expectations.
- `errors.jsonl` was empty — no source identity failure masks the evidence decision.
- `score_applicability_issues` confirmed to still contain the expected issue ID with all 7 missing groups.
- Quality gate confirmed `FQ2F/warn` with `reason=bond_risk_evidence_missing`.
- `git diff --check` passed — no hidden code/control changes.

## Criterion 3: Per-Group Table — Evidence-Backed and No Overclaiming

**PASS with findings**

### 3a. Overall group coverage

All 7 `bond_risk_evidence.v1` groups are present in the per-group table (§5). Each group has:
- Observed evidence description
- Anchor/locator referencing specific annual-report sections/pages/tables
- Classification as "positive public annual-report evidence exists" (or variant)
- Reviewer note

### 3b. Finding F1 — `leverage_liquidity` evidence strength is overstated

**Severity: LOW**

The reviewer note says "Text gives direct leverage/liquidity-risk control evidence." However:

- The management text says the fund "flexibly used leverage strategy" — this is a strategy description, not a disclosure of actual leverage level or repo borrowing ratio.
- The asset-allocation table (page 59) shows `buy-back resale financial assets 497,184,300.60 / 3.90%` — this is asset-side repo exposure, not confirmed liability-side leverage.
- The evidence artifact does not confirm whether the annual report discloses actual repo leverage ratio, debt-to-asset ratio, or large-redemption stress scenario.

The classification "positive public annual-report evidence exists" is technically correct (qualitative strategy text does exist), but the reviewer note could overstate the evidence strength for a later extractor gate. The later extractor gate should decide whether qualitative leverage strategy text alone satisfies the `leverage_liquidity` group or requires quantitative repo/leverage data.

**Risk**: If the later extractor gate accepts qualitative strategy text as sufficient, this sets a weaker evidence bar than other groups (e.g., `credit_risk` has concrete rating distribution tables). This is a judgment for the extractor gate, not a blocker for this evidence artifact.

### 3c. Finding F2 — `drawdown_stress` classification boundary is correct but worth explicit note

**Severity: INFO**

The reviewer note correctly states: "This supports drawdown-control intent, not a quantitative max-drawdown metric." The classification says "Limited positive public annual-report risk-control evidence exists." This is honest and appropriately cautious.

The evidence artifact's §6 final state says "The repository-loaded annual report contains candidate public evidence for all seven groups" — this is true but could be read as implying equal evidence strength across groups. The `drawdown_stress` group is materially weaker than `asset_allocation_holdings_mix` or `credit_risk`.

No fix required. The reviewer note already flags this for the later extractor gate.

### 3d. Finding F3 — `redemption_share_pressure` share-class selection issue is correctly identified

**Severity: INFO (confirmed)**

The reviewer note says: "Public snapshot marks `share_change` missing only because current rules cannot reliably select share class." This correctly identifies that the data exists in the annual report but current extraction cannot normalize it. The classification as "extraction/normalization issue" rather than "disclosure gap" is correct and consistent with the final state.

## Criterion 4: Final State Extractor/Evidence-Anchor Classification

**PASS**

The final state is `extractor/evidence anchor issue requiring future gate`.

Reasoning is sound:

1. Same-fund/year public annual-report evidence was accessible through `FundDocumentRepository` — confirmed.
2. The annual report contains candidate evidence for all 7 groups — confirmed by repository inspection locators.
3. Public CLI artifacts still emit `bond_risk_evidence_missing` with `baseline_blocking=true` and all 7 groups — confirmed by score/quality-gate inspection.
4. Current CLI cannot express positive `bond_risk_evidence` records — confirmed.
5. Therefore not a disclosure data gap — correct.

This classification is not a premature blocker解除. It correctly routes to a later extractor/evidence-anchor gate rather than attempting to bypass the blocker in this evidence-only task.

## Criterion 5: Keeping `bond_risk_evidence_missing.baseline_blocking=true`

**PASS**

The evidence artifact correctly maintains `baseline_blocking=true` for the current baseline/golden gate. Reasons:

- No code, extractor, evidence-anchor contract, quality-gate behavior, baseline, or golden fixture change is authorized in this gate.
- The blocker cannot be解除 in a role-scoped evidence task.
- Proper route is a later extractor/evidence-anchor gate that converts repository-confirmed locators into reviewed `bond_risk_evidence.v1` records.
- This does not weaken FQ0-FQ6 or FQ2F semantics.

## Criterion 6: Golden Corpus

**PASS**

Golden corpus v1 remains blocked. The evidence artifact explicitly states:

- This task produced evidence for the bond residual only.
- It did not promote `006597`, did not update baseline/golden fixtures.
- It did not resolve the broader coverage/source/quality/fund-type/fixture-promotion blockers.

No golden promotion occurred or was attempted.

## Criterion 7: Artifact Disposition

**PASS**

- Reports are scratch/untracked under `reports/extraction-snapshots/bond-positive-risk-006597-2024-20260527/`.
- The stray file named `--help` remains untracked and was not staged, deleted, renamed, or inspected for evidence.
- `AGENTS.md` was not modified.
- No other untracked files were staged or promoted.
- `git diff --check` passed.

## Findings Summary

| ID | Severity | Criterion | Description | Requires patch |
|---|---|---|---|---|
| F1 | LOW | §3 | `leverage_liquidity` reviewer note overstates evidence strength; qualitative strategy text ≠ quantitative leverage data | No — judgment for later extractor gate |
| F2 | INFO | §3 | `drawdown_stress` is materially weaker than other groups; "all 7 groups" phrasing implies more uniform coverage than exists | No — reviewer note already flags this |
| F3 | INFO | §3 | `redemption_share_pressure` share-class selection issue correctly identified as extraction gap | No — confirmed correct |

## Patch Requirement

**No patch required before controller judgment.**

All findings are LOW or INFO severity. None challenge the correctness of the final state classification, the blocker decision, or the artifact disposition. F1 is a judgment call for the later extractor gate about evidence strength thresholds. F2 and F3 are informational confirmations.

The evidence artifact is internally consistent: the per-group table locators match the repository inspection output, the final state reasoning follows from the observations, and the blocker decision is correct for a role-scoped evidence task.

## Re-review Required

**No.** No findings require patching. The artifact is ready for controller judgment as-is.

## Summary

The evidence artifact is well-constructed. Repository inspection through `FundDocumentRepository` confirmed that the 006597 2024 annual report contains candidate bond-risk evidence for all 7 `bond_risk_evidence.v1` groups. The final state classification (`extractor/evidence anchor issue requiring future gate`) is correct — this is not a disclosure data gap, but a current CLI contract limitation. Maintaining `baseline_blocking=true` is appropriate. The per-group evidence strength varies (credit_risk and asset_allocation_holdings_mix have concrete tables; drawdown_stress and leverage_liquidity are more qualitative), but this variation is honestly noted and correctly deferred to the later extractor gate.
