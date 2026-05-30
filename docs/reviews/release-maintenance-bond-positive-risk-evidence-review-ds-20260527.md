# Bond Positive-Risk Evidence — Review (AgentDS)

> Date: 2026-05-27
> Reviewer: AgentDS
> Role: independent evidence reviewer (not controller)
> Target: `docs/reviews/release-maintenance-bond-positive-risk-evidence-20260527.md`
> Accepted plan: `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-20260527.md`
> Controller judgment: `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-controller-judgment-20260527.md`
> Verdict: **PASS_WITH_FINDINGS**

## Review Scope

This review assesses the evidence artifact against the 7 criteria specified in the review task. It does not re-run evidence, re-inspect the annual report, implement code, or make controller decisions.

## Criterion-by-Criterion Assessment

### C1: Evidence run obeyed plan and boundaries

**PASS**

- Target scope 006597 / 2024 only: confirmed. All commands reference `--fund-code 006597 --report-year 2024` or `load_annual_report("006597", 2024)`.
- Public CLI outputs used: confirmed. `extraction-snapshot`, `extraction-score`, `quality-gate` were the only CLI tools invoked.
- FundDocumentRepository only for repository inspection: confirmed. Both inspection scripts instantiate `FundDocumentRepository()` and call `load_annual_report("006597", 2024)`. The artifact explicitly states no PDF path, cache path, concrete source helper, download helper, Eastmoney helper, EID helper, renderer, extractor, quality-gate internals, or fallback override was used.
- No code/control changes: confirmed. `git diff --check` exited 0; no production code, test, or control doc was modified.
- Command set matches accepted plan Step A and Step B shapes: confirmed. CLI commands and repository inspection scripts follow the plan's authorized command templates, including the narrower second inspection pass.

### C2: Generated artifact paths and command exit codes are credible and sufficient

**PASS**

- All 15 commands exited with code 0.
- Public artifact paths under `reports/extraction-snapshots/bond-positive-risk-006597-2024-20260527/` are internally consistent: `snapshot.jsonl`, `summary.md`, `errors.jsonl`, `score.json`, `score.md`, `golden_set.json`, `quality_gate.json`, `quality_gate.md`.
- `errors.jsonl` is empty (`wc -l` returned 0), confirming no source identity failure contaminated the evidence decision.
- CLI output summary (section 3) is consistent with the described artifact inspection results: `classified_fund_type=bond_fund`, 8 template chapters resolved, empty errors, `bond_risk_evidence_missing` still present with all 7 groups, `baseline_blocking=true`, quality gate `warn` with `FQ2F/warn` and `reason=bond_risk_evidence_missing`.

### C3: Per bond_risk_evidence.v1 group classifications are evidence-backed and not overclaimed

**PASS_WITH_FINDINGS**

Each group reviewed against plan section 2 evidence definitions:

| Group | Evidence-backed? | Overclaimed? | Notes |
|---|---|---|---|
| `duration_rate_risk` | Yes. §2 product strategy, §4 duration strategy keywords, §5 interest-rate risk disclosure. | No. Locators cite specific sections and table. | Solid textual evidence for duration/rate-risk management. |
| `credit_risk` | Yes. §2 credit-bond strategy, §4 medium-high-grade positioning and credit-risk control, page 53/54 rating distribution tables. | No. Rating tables are concrete portfolio-risk evidence. | Rating distributions (AAA / AAA-below / unrated) for both short-term and long-term instruments are the strongest credit-risk anchors. |
| `leverage_liquidity` | Yes. §4 leverage/liquidity keywords, page 59 table 1 allocation, repo locators. | Minor: repo locators at "pages 49-50 and financial statement tables" lack specific table indices (see F2). | Not blocking; future extractor gate needs to pin precise table anchors. |
| `asset_allocation_holdings_mix` | Yes. §8, page 59-61 tables with bond category mix, top bonds, top ABS. | No. Multiple tables expose actual holdings with percentages. | Strongest evidence group. |
| `drawdown_stress` | Partially. §4 keyword "控制回撤" confirms drawdown-control intent, but this is qualitative, not quantitative (see F1). | No — artifact honestly classifies as "Limited positive" with explicit note about the qualitative/quantitative gap. | See finding F1 below. |
| `redemption_share_pressure` | Yes. §9 page 63 table 1 (holder structure), §10 page 65 table 0 (share changes). | No. Artifact correctly notes this is an extraction/normalization issue for multi-share-class tables. | A share redemptions > subscriptions; ending shares < beginning shares. |
| `convertible_bond_equity_exposure` | Yes. §8 page 59 table 1 (equity/stock = `-`), page 61 table 0 (convertible/exchangeable bonds = `-`). | No. Accepted plan explicitly permits explicit absence as evidence. | Absence evidence is correctly classified, not ignored. |

**F1 (INFO): `drawdown_stress` evidence is qualitative intent, not quantitative metric**

The accepted plan (section 2) defines acceptable drawdown_stress evidence as: "annual report or accepted public output discloses maximum drawdown, volatility, stress metric, or enough anchored data for a reviewed calculation."

The evidence found is:
- §4 keyword "控制回撤" — management states it seeks stable NAV while controlling drawdown.
- Public snapshot `nav_benchmark_performance` anchor — NAV growth versus benchmark data exists.

This is qualitative drawdown-control intent, not a maximum-drawdown figure, volatility metric, or stress-test result. The NAV benchmark performance data could theoretically support a reviewed calculation, but no such calculation was performed in this evidence run (and none was authorized).

The artifact's self-classification as "Limited positive public annual-report risk-control evidence exists" and its reviewer note are honest. However, the classification still maps to the "Positive public annual-report evidence exists; current CLI cannot express it" bucket in the per-group table, which overstates the type of evidence relative to the plan's quantitative threshold.

**Severity**: INFO. Does not change the final state classification or blocker decision. The future extractor gate must resolve whether qualitative drawdown-control intent satisfies `bond_risk_evidence.v1:drawdown_stress` or whether a quantitative metric is required.

**F2 (INFO): `leverage_liquidity` repo locators are imprecise**

The evidence artifact describes repo-related locators as "observed at pages 49-50 and financial statement tables" without specific table indices or row locators. All other locators cite specific sections, tables, or page/table combinations (e.g., "page 53 table 0", "page 59 table 1").

The artifact's reviewer note acknowledges: "Repo table locators are candidates and should be normalized in a later extractor gate."

**Severity**: INFO. Does not undermine the leverage_liquidity classification, which also relies on direct §4 keyword evidence. The future extractor gate needs to pin precise repo table anchors.

### C4: Final state classification is correct vs alternatives

**PASS**

The artifact classifies final state as `extractor/evidence anchor issue requiring future gate`.

Comparison against the plan's classification matrix (section 4):

| Alternative | Why rejected | Evidence |
|---|---|---|
| `positive-risk evidence sufficient` | Current CLI still emits `bond_risk_evidence_missing` with all 7 groups and `baseline_blocking=true`. No code path exists to consume positive bond_risk_evidence records. | CLI score.json confirms the replacement issue is unchanged. |
| `evidence insufficient` | Repository inspection found candidate public evidence for all 7 groups in the annual report. The problem is not insufficient disclosure; it's that the extractor cannot express positive evidence. | Per-group table shows anchored evidence for every group. |
| `evidence unavailable/disclosure gap` | The repository-verified 2024 annual report is accessible and contains relevant sections/tables for all groups. No source failure occurred. | `errors.jsonl` is empty; repository inspection returned 8 sections with matching content. |

The chosen classification is correct: public evidence exists in the repository-loaded annual report, but current CLI artifacts cannot express positive `bond_risk_evidence` records or durable anchors. This matches the plan's definition exactly.

### C5: Blocker decision maintains bond_risk_evidence_missing.baseline_blocking=true without weakening

**PASS**

Section 7 explicitly states: `bond_risk_evidence_missing.baseline_blocking=true` **must be维持 for the current baseline/golden gate**.

The reasoning is sound:
- No code, extractor, evidence-anchor contract, quality-gate behavior, baseline, or golden fixture change is authorized in this role-scoped evidence task.
- The proper route is a later extractor/evidence-anchor gate.
- The blocker is explicitly **not** classified as `data_gap`.

No weakening of FQ0-FQ6 semantics: the artifact confirms FQ2F/warn remains with `reason=bond_risk_evidence_missing`, and the quality gate status remains `warn` with 7 issues. The evidence does not suppress or erase any risk evidence.

### C6: Golden corpus remains blocked; no promotion

**PASS**

Section 8 explicitly states golden corpus v1 remains blocked. The artifact confirms:
- No promotion of 006597.
- No baseline/golden fixture update.
- The task produced evidence for the bond residual only.
- It did not resolve broader coverage/source/quality/fund-type/fixture-promotion blockers.

### C7: Artifact disposition is safe

**PASS**

- Generated `reports/extraction-snapshots/bond-positive-risk-006597-2024-20260527/` is scratch/untracked.
- The stray file `--help` remains untracked and was not staged, deleted, renamed, or inspected for evidence.
- `git diff --check` passed with exit code 0.
- No files were staged, committed, or pushed.

## Cross-Cutting Observations

**O1**: The annual report for 006597/2024 is disclosure-rich for bond risk. All 7 `bond_risk_evidence.v1` groups have at least candidate evidence. No group falls into "evidence unavailable/disclosure gap." This confirms the issue is purely on the extractor/evidence-anchor side.

**O2**: The two-pass repository inspection (broad keyword scan, then narrower focus) followed the plan's instruction to "rerun with narrower keywords rather than dumping the annual report." The concise candidate locators in section 4 are appropriate — they provide enough context for a reviewer to assess evidence quality without reproducing full report text.

**O3**: The artifact's §4 keyword citations rely on Chinese keyword matching (久期策略, 中高等级, 信用风险, 杠杆策略, 流动性风险, 控制回撤). The plan authorized keyword-based inspection. The artifact does not reproduce the full matched text, only concise summaries. This is appropriate for an evidence artifact that must not dump annual report content.

## Required Actions Before Controller Judgment

- **F1 and F2 are INFO severity.** They do not require artifact patching before controller judgment. The artifact already self-documents both limitations (drawdown_stress reviewer note, leverage_liquidity reviewer note).
- The controller may choose to record F1 as a specific requirement for the future extractor/evidence-anchor gate (i.e., whether qualitative drawdown-control intent is acceptable or a quantitative metric is required).
- No re-review is required. Findings are non-blocking and the artifact's self-awareness of its limitations is adequate.

## Verdict

**PASS_WITH_FINDINGS**

The evidence artifact faithfully executes the accepted plan under controller-authorized boundaries. All 7 `bond_risk_evidence.v1` groups are assessed with specific annual-report locators. The final state classification as `extractor/evidence anchor issue requiring future gate` is the correct choice among the four alternatives. The blocker is maintained without weakening. Golden corpus remains blocked. Artifact disposition is safe.

Two INFO findings (F1: drawdown_stress qualitative/quantitative gap; F2: leverage_liquidity repo locator precision) do not block acceptance and are already self-documented in the artifact.
