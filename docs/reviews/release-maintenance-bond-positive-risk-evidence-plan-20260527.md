# release-maintenance bond positive-risk evidence plan

> Date: 2026-05-27
> Role: planning agent
> Gate: `release-maintenance bond positive-risk evidence gate`
> Gate classification: `standard`
> Target: `006597` / report_year `2024`
> Target residual: `bond_risk_evidence_missing.baseline_blocking=true`
> Scope: plan artifact only. No evidence CLI run, production code change, extractor work, renderer work, quality-gate behavior change, commit, push, PR, or GitHub mutation.

## 1. Startup Packet Replay And Scope

### Startup Packet replay

| Item | Current state |
|---|---|
| Branch observed during plan preflight | `codex/local-reconciliation` |
| Current phase | `release maintenance` |
| Current accepted gate | `release-maintenance consolidation / QDII post-021539 disposition accepted locally` |
| Next entry point | `bond positive-risk evidence gate; must use init-agents / tmux multi-agent flow` |
| Next gate classification | `standard` |
| Current truth sources | `AGENTS.md`; `docs/design.md` current sections; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point; current accepted artifacts |
| Evidence-chain-only sources | `docs/reviews/`; `docs/archive/` |
| Target blocker | `006597` / `2024` has `bond_risk_evidence_missing.baseline_blocking=true` |

Current accepted control state says bond `006597` remains blocked by `bond_risk_evidence_missing.baseline_blocking=true`. The previous bond-lens score applicability implementation accepted that exact `bond_fund` can exclude equity-shaped `holdings_snapshot` from stock-holdings denominator only when it emits a replacement `bond_risk_evidence.v1` issue. That issue currently projects to warn-level `FQ2F` and remains baseline/golden blocking.

### Allowed scope

- Plan/review first; no evidence collection until this plan has at least two independent reviews and controller judgment.
- Scope only to `006597` / `2024` positive bond-risk public evidence and whether it resolves, maintains, data-gaps, or reroutes `bond_risk_evidence_missing.baseline_blocking=true`.
- Use public CLI outputs where possible: `fund-analysis extraction-snapshot`, `fund-analysis extraction-score`, and `fund-analysis quality-gate`.
- If annual-report content inspection is necessary, access must go through `FundDocumentRepository.load_annual_report(...)`; do not read PDFs, caches, concrete source helpers, download helpers, EID helpers, Eastmoney helpers, or local cache paths directly.
- Preserve `FundDocumentRepository` source/fallback semantics. Source failure classification remains fail-closed for `schema_drift`, `identity_mismatch`, and `integrity_error`.
- Preserve existing FQ0-FQ6 semantics, severity thresholds, renderer output, Service/CLI behavior, source strategy, and baseline/golden non-promotion.

### Non-goals

- Do not enter golden corpus, QDII probing, FOF taxonomy, release readiness, renderer, quality gate, extractor implementation, Service/CLI changes, Host/Agent/dayu, GitHub mutation, baseline/golden promotion, fixture promotion, or source/fallback semantic changes.
- Do not implement `bond_risk_evidence` extraction or evidence-anchor schema in this gate.
- Do not suppress `bond_risk_evidence_missing` merely because `holdings_snapshot` is inapplicable to bond funds.
- Do not infer bond risk from category labels, fund name, generic bond-fund knowledge, market history, or unlabeled PDF text outside repository-returned annual-report sections/tables.

## 2. Acceptable Public Evidence Definition

The evidence contract is grounded in current `bond_risk_evidence.v1` concepts in `fund_agent/fund/extraction_score.py`: `duration_rate_risk`, `credit_risk`, `leverage_liquidity`, `asset_allocation_holdings_mix`, `drawdown_stress`, `redemption_share_pressure`, and `convertible_bond_equity_exposure`.

### What can satisfy positive-risk evidence

Positive-risk evidence is sufficient only if all conditions below are met:

| Requirement | Acceptance criterion |
|---|---|
| Same fund/year | Evidence is from `006597` 2024 annual report loaded through public CLI output or `FundDocumentRepository`. |
| Public disclosure | Evidence comes from annual-report sections/tables, or from public CLI artifacts derived from that same repository-loaded annual report. |
| Traceability | Each accepted fact has a section/table/row-style locator or existing CLI evidence anchor sufficient to reconstruct the disclosure source. |
| Bond-risk relevance | Evidence maps to at least one `bond_risk_evidence.v1` group and describes actual portfolio risk exposure, risk control, or explicit absence of exposure. |
| Reviewed status | The evidence-run artifact records reviewer confirmation that the public text/table actually supports the classified group. |
| No risk suppression | Evidence does not erase or weaken risk. It records either concrete exposure, concrete low/absent exposure, or explicit disclosure gap. |

Concrete satisfying examples:

- `duration_rate_risk`: annual report discloses portfolio duration, average remaining maturity, interest-rate sensitivity, or a specific interest-rate risk management description.
- `credit_risk`: annual report discloses bond rating distribution, credit-bond exposure, default/impairment risk, financial-bond / non-policy-bank exposure, or issuer concentration.
- `leverage_liquidity`: annual report discloses leverage, repo/financing exposure, liquidity risk, large redemption impact, or holder concentration pressure.
- `asset_allocation_holdings_mix`: annual report discloses bond/cash/other instrument structure, top bond holdings, issuer concentration, industry concentration, or portfolio composition.
- `drawdown_stress`: annual report or accepted public output discloses maximum drawdown, volatility, stress metric, or enough anchored data for a reviewed calculation.
- `redemption_share_pressure`: annual report discloses share changes, subscription/redemption trends, holder concentration, large redemption events, or explicit share-class ambiguity.
- `convertible_bond_equity_exposure`: annual report discloses convertible-bond exposure, stock/equity exposure, secondary-bond/hybrid-bond equity allocation, or explicit absence of such exposure.

### What cannot satisfy positive-risk evidence

- Existing `bond_risk_evidence_missing` / `FQ2F/warn` alone. It proves the replacement issue exists, not that positive evidence exists.
- Generic `bond_fund` classification, fund name containing "债券", or app category "国内债券类".
- Equity-shaped `holdings_snapshot` inapplicability by itself.
- A quality-gate status of `warn` by itself. Current accepted implementation intentionally warns, not passes, while `baseline_blocking=true`.
- Unanchored prose, copied markdown without annual-report locator, or claims derived from experience / usually / fund-type common sense.
- Direct PDF/cache/manual source-helper inspection outside `FundDocumentRepository`.
- Evidence from another fund code, another report year, a report summary where the full annual report identity is unverified, or an external website not tied back to repository-verified annual-report facts.

### What is `data_gap`

Classify as `evidence unavailable/disclosure gap` only when the evidence run proves the repository-verified 2024 annual report was accessible and inspected for the relevant `bond_risk_evidence.v1` groups, but the public annual report does not disclose enough information to support positive evidence for the missing groups. A repository/source failure is not a disclosure gap unless the failure classification proves a valid public annual report is unavailable under current source semantics.

### What is extractor/evidence-anchor issue

Classify as `extractor/evidence anchor issue requiring future gate` when public annual-report evidence exists for one or more required groups but current public CLI artifacts cannot express it as a positive `bond_risk_evidence` record with durable anchors. This is the expected route if repository inspection finds sections/tables supporting bond-risk groups, because current accepted code only emits the fail-closed `bond_risk_evidence_missing` replacement issue and does not implement positive `bond_risk_evidence` extraction/input.

## 3. Evidence Collection Plan

No command in this section is authorized until plan review by at least two independent reviewers and controller judgment are complete.

### Step A: public CLI evidence run

Run only after review approval:

```bash
uv run fund-analysis extraction-snapshot --run-id bond-positive-risk-006597-2024-20260527 --fund-code 006597 --report-year 2024
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/bond-positive-risk-006597-2024-20260527/snapshot.jsonl --errors-path reports/extraction-snapshots/bond-positive-risk-006597-2024-20260527/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json
uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/bond-positive-risk-006597-2024-20260527/score.json
```

Inspect only the generated public artifacts:

| Artifact | Required inspection |
|---|---|
| `reports/extraction-snapshots/bond-positive-risk-006597-2024-20260527/snapshot.jsonl` | Confirm `classified_fund_type=bond_fund`; inspect fields and anchors that may imply current public extraction already exposes bond-risk facts. |
| `reports/extraction-snapshots/bond-positive-risk-006597-2024-20260527/summary.md` or equivalent summary path printed by CLI | Confirm run completed for `006597` and source identity did not fail. |
| `reports/extraction-snapshots/bond-positive-risk-006597-2024-20260527/errors.jsonl` | Confirm no annual-report identity/source failure masks the evidence decision. |
| `reports/extraction-snapshots/bond-positive-risk-006597-2024-20260527/score.json` | Inspect `field_applicability_decisions` and `score_applicability_issues`; confirm whether issue id `score-applicability:006597:2024:holdings_snapshot:bond_risk_evidence_missing:bond_risk_evidence.v1` remains and which `missing_evidence_groups` are listed. |
| quality-gate output path printed by CLI | Confirm whether `FQ2F/warn` with `reason=bond_risk_evidence_missing` remains. |

If Step A shows malformed score-applicability data, wrong fund type, wrong report year, annual-report identity mismatch, source fail-closed category, or missing expected public output files, stop and classify according to the matrix in section 4. Do not patch code in this gate.

### Step B: read-only repository inspection if public CLI cannot decide evidence existence

Only if Step A cannot determine whether public annual-report evidence exists, use a read-only repository inspection script. The script must instantiate `FundDocumentRepository` and call `load_annual_report("006597", 2024)`. It may print section ids, section titles, table page/index identifiers, table headers, row labels, and short snippets needed to locate candidate bond-risk evidence. It must not read PDF/cache paths, call source adapters directly, force source fallback behavior, mutate cache, or write production files.

Permitted command shape after review approval:

```bash
uv run python - <<'PY'
import asyncio
from fund_agent.fund.documents import FundDocumentRepository

KEYWORDS = (
    "久期", "剩余期限", "利率风险", "信用风险", "评级", "债券投资",
    "金融债", "企业债", "资产支持证券", "回购", "杠杆", "流动性风险",
    "前五名债券", "债券持仓", "可转债", "股票投资", "赎回", "持有人",
    "回撤", "最大回撤", "波动率", "压力测试", "波动"
)

async def main() -> None:
    report = await FundDocumentRepository().load_annual_report("006597", 2024)
    print({"fund_code": report.key.fund_code, "year": report.key.year, "section_count": len(report.sections)})
    for section_id, section in report.sections.items():
        title = section.title or ""
        text = report.raw_text[section.start_offset:section.end_offset]
        haystack = title + "\n" + text
        if any(keyword in haystack for keyword in KEYWORDS):
            print({"section_id": section_id, "title": title, "snippet": text[:500]})
    for table in report.tables:
        headers = str(table.headers)
        rows_preview = str(table.rows[:8])
        if any(keyword in headers + rows_preview for keyword in KEYWORDS):
            print({
                "page_number": table.page_number,
                "table_index": table.table_index,
                "headers": headers,
                "rows_preview": rows_preview[:1200],
            })

asyncio.run(main())
PY
```

The evidence artifact must copy only concise candidate locators and summaries, not full report text. If the script output is too broad, rerun with narrower keywords rather than dumping the annual report.

### Step C: classification artifact

Write the evidence-run result to:

- `docs/reviews/release-maintenance-bond-positive-risk-evidence-20260527.md`

Required contents:

- Startup Packet replay and exact commands run.
- Public artifact paths produced by CLI.
- Repository inspection command, if used, and confirmation it used `FundDocumentRepository`.
- Per-group table for all `bond_risk_evidence.v1` groups: observed evidence, anchor/locator, classification, reviewer note.
- Final state from section 4 matrix.
- Explicit statement whether `bond_risk_evidence_missing.baseline_blocking=true` can be解除, must be维持, is data gap, or routes to later extractor/evidence-anchor gate.
- Residual risks and next owner.

## 4. Evidence Classification Matrix

| Final state | Required evidence | Controller action after reviews |
|---|---|---|
| `positive-risk evidence sufficient` | Public CLI or repository inspection finds anchored, same-fund/year, reviewed evidence covering every missing `bond_risk_evidence.v1` group enough to replace `bond_risk_evidence_missing`; no source identity/fallback issue; no remaining baseline-blocking bond-risk groups. | Mark this blocker eligible to解除 only as a disposition. Do not promote baseline/golden in this gate. If current code cannot consume the positive evidence, route implementation to a later extractor/evidence-anchor gate rather than editing code here. |
| `evidence insufficient` | Some public evidence exists but does not cover required groups, lacks anchors, is ambiguous, belongs to wrong year/fund, or only proves generic bond classification. | Maintain `bond_risk_evidence_missing.baseline_blocking=true`; record exact missing groups and evidence weaknesses. |
| `evidence unavailable/disclosure gap` | Repository-verified 2024 annual report is accessible and inspected, but relevant required groups are not publicly disclosed or are explicitly unavailable in the report; no extractor failure can be proven from same-source evidence. | Maintain blocker as disclosure/data gap; assign revisit condition to future disclosure/source or baseline-disposition gate. |
| `extractor/evidence anchor issue requiring future gate` | Public evidence exists in the repository-loaded annual report, but current CLI artifacts cannot express positive `bond_risk_evidence` records or durable anchors; current score still emits `bond_risk_evidence_missing`. | Keep current blocker for now; open later extractor/evidence-anchor contract gate with anchored examples. Do not weaken FQ2F/FQ4 or suppress the replacement issue. |

Stop-condition classifications:

| Stop condition | Handling |
|---|---|
| Evidence run requires code/test changes | Stop and report. Do not implement. Route to a new implementation plan gate. |
| Evidence run requires direct PDF/cache/source-helper access | Stop and report boundary violation risk. Use `FundDocumentRepository` or classify as unavailable under allowed evidence. |
| Annual-report source returns `schema_drift`, `identity_mismatch`, or `integrity_error` | Stop and classify as source fail-closed issue, not disclosure gap. |
| Annual-report source returns only `not_found` or `unavailable` after allowed fallback exhaustion | Classify as public evidence unavailable due to source availability, with source category preserved. |
| CLI output contradicts accepted design truth | Stop and route to controller for truth reconciliation; do not patch code. |

## 5. Artifact Paths

| Purpose | Path |
|---|---|
| This plan | `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-20260527.md` |
| Plan review 1 | `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-review-<reviewer1>-20260527.md` |
| Plan review 2 | `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-review-<reviewer2>-20260527.md` |
| Plan re-review, if findings are fixed | `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-rereview-<reviewer>-20260527.md` |
| Controller judgment for plan | `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-controller-judgment-20260527.md` |
| Evidence-run artifact | `docs/reviews/release-maintenance-bond-positive-risk-evidence-20260527.md` |
| Evidence review 1 | `docs/reviews/release-maintenance-bond-positive-risk-evidence-review-<reviewer1>-20260527.md` |
| Evidence review 2 | `docs/reviews/release-maintenance-bond-positive-risk-evidence-review-<reviewer2>-20260527.md` |
| Evidence controller judgment | `docs/reviews/release-maintenance-bond-positive-risk-evidence-controller-judgment-20260527.md` |
| Scratch/public CLI outputs | `reports/extraction-snapshots/bond-positive-risk-006597-2024-20260527/` and quality-gate output path printed by CLI |

## 6. Current Untracked File Disposition

Preflight status observed before writing this plan:

```text
 M AGENTS.md
?? --help
?? docs/reviews/release-maintenance-bond-positive-risk-truth-preflight-20260527.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md
?? docs/reviews/repo-review-20260526-231040.md
?? docs/tmux-agent-memory-store.md
```

Disposition for this plan gate:

- `AGENTS.md`: user/controller-added docs-only gate classification rule section; do not modify in this plan.
- `docs/reviews/release-maintenance-bond-positive-risk-truth-preflight-20260527.md`: current gate evidence-chain artifact; leave unmodified.
- `--help`: stray untracked file; do not delete, stage, rename, inspect for evidence, or promote. Cleanup requires explicit user authorization or accepted artifact disposition.
- Other untracked review/audit/memory artifacts: unrelated to this plan gate unless controller later classifies them; do not stage or modify.
- This plan adds only `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-20260527.md`.

## 7. Validation Matrix

| Validation | Required for this plan artifact | Expected result / handling |
|---|---|---|
| `git diff --check` | Yes, docs-only whitespace validation. | Must pass before reporting plan complete, or report failure without patching unrelated files. |
| `uv run ruff check ...` | Not required for docs-only plan. | If any code/test change becomes necessary, stop condition: do not implement in this gate. |
| `uv run pytest ...` | Not required for docs-only plan. | If any code/test change becomes necessary, stop condition: do not implement in this gate. |
| Evidence CLI commands | Not allowed before plan review and controller judgment. | This plan lists future commands only; do not run during plan task. |
| Production code diff | Must remain none for this task. | Any proposed code/test modification must be routed to a future implementation plan gate. |

## 8. Required Reviews Before Evidence Run

This is a `standard` evidence gate. Before any evidence CLI or repository inspection run:

1. Obtain at least two independent plan reviews.
2. Fix accepted plan findings or record controller disposition.
3. Obtain re-review where accepted findings were fixed.
4. Write controller judgment accepting the plan and authorizing the evidence run.
5. Only then run the public CLI / repository-inspection steps in section 3.

Reviewer prompts must state that reviewers are not controllers, must not start implementation, must not run evidence CLI, must not commit/push/PR, and must review specifically for evidence sufficiency, source-boundary compliance, `bond_risk_evidence.v1` group coverage, data-gap classification, and risk of silently suppressing `bond_risk_evidence_missing`.

## 9. Completion Signal For This Plan Task

This role-scoped planning task is complete when:

- This artifact exists at the path above.
- It contains Startup Packet replay, acceptable evidence definition, exact future evidence commands/inspection steps, classification matrix, artifact paths, untracked-file disposition, validation matrix, and two-review requirement.
- `git diff --check` has been run or its failure is reported.
- No evidence CLI, production code, test, commit, push, PR, or GitHub mutation occurred.
