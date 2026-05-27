# Bond Risk Evidence Narrow False-Negative Plan — Re-Review (DS)

> Date: 2026-05-28
> Role: plan re-review worker DS
> Re-review target:
> - amended plan: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-20260528.md`
> - plan-fix: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-fix-20260528.md`
> Prior reviews:
> - DS plan review: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-review-ds-20260528.md`
> - MiMo plan review: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-review-mimo-20260528.md`
> Verdict: **PASS** — all mandatory and advisory findings from both DS and MiMo reviews are closed; no new blocking gaps introduced.

## Worker Self-Check

- Role confirmed: plan re-review worker DS only; not controller, not implementation worker.
- No gateflow started. No production code, tests, reports, or git state modified.
- All four input artifacts read and cross-referenced.

---

## Mandatory Finding Closure (DS)

### M1: async FundDocumentRepository smoke — CLOSED

Plan-fix correctly rewrote the validation command to wrap `load_annual_report` in `asyncio.run()`.

Amended plan line 415:
```
uv run python -c 'import asyncio; from fund_agent.fund.documents import FundDocumentRepository; repo = FundDocumentRepository(); report = asyncio.run(repo.load_annual_report("006597", 2024, force_refresh=True)); ...'
```

No residual risk. The `asyncio.run()` wrapper is the correct pattern for Python 3.11+ with no running event loop.

### M2: ExtractionMode.estimated vs contract_status partial — CLOSED

Plan-fix added an explicit Extraction Mode Decision section (amended plan lines 104–105):

> `extraction_mode` has no `partial` enum value. When `bond_risk_contract_status=partial`, keep `extraction_mode=ExtractionMode.estimated`; the structured `bond_risk_contract_status` field remains authoritative for partial contract status. Do not change extractor model schema in this gate.

This resolves the contradiction. No schema change needed. The `bond_risk_contract_status` field carries the authoritative partial/complete signal for downstream consumers.

### M3: share table best-match / fail-closed — CLOSED

Plan-fix replaced the ambiguous first-match behavior with explicit scan-all + scoring rules (amended plan lines 177–183):

> Scan all parsed tables; do not return the first table matching `期初` / `期末` / `申购` / `赎回`. Score candidates and select the best §10 share-change table: prefer section/header/table text containing `§10` / `基金份额` / `份额总额` / `总申购份额` / `总赎回份额` / `期初` / `期末`. Explicitly reject or heavily downgrade financial-statement tables with `实收基金`, `未分配利润`, `净资产合计`… If multiple non-rejected candidates survive with no unique best candidate, fail closed as `ambiguous` instead of guessing.

The corresponding test `test_redemption_share_pressure_rejects_net_asset_statement_table` covers the financial-statement rejection scenario.

### M4: rating table numeric shape — CLOSED

Plan-fix added numeric shape requirements (amended plan lines 141–144):

> Require numeric shape: at least one data row must have a recognized rating category label and a parseable current-period numeric amount. Tables with no numeric current-period amount, no row/table anchor, or fewer than two data rows must not be accepted. Prefer tables where the first semantic column contains rating category labels and the current-period column contains numeric amounts. Percentage-only or text-description-only tables are not sufficient for `accepted`.

And fund-own-rating rejection (lines 138–139):

> Explicitly reject fund-own-rating semantics. If header/table text contains `本基金评级`, `基金评级信息`, `基金自身评级`, or `本基金` + `评级` without held-position qualifiers (`持有` / `持仓` / `证券`), do not accept the table.

These two constraints together close the false-positive risk identified in M4.

---

## Advisory Finding Closure (DS)

### A1: Decimal tolerance — CLOSED

Plan now specifies `Decimal("0.01")` absolute tolerance (line 206), comma/whitespace stripping before parsing (line 202), dash variants as zero (line 203), and `InvalidOperation` → fail-closed with `na_reason="non_parseable_share_value"` (line 205).

### A2: §2 mapping test — CLOSED

Plan now includes `test_share_class_evidence_from_section_two_table` in the required tests (lines 344–346), isolating §2 table-based mapping from synthetic `下属分级基金的基金简称` / `下属分级基金的交易代码` rows.

### A3: _trim_note reference — ACKNOWLEDGED

Helper exists in current codebase (`bond_risk_evidence.py:1295-1311`). No plan change needed. The plan correctly references an existing utility.

---

## MiMo Finding Closure

### F1 (P0): fund-own-rating table false positive — CLOSED

Addressed together with M4 above. Amended plan now explicitly rejects `本基金评级` / `基金评级信息` / `基金自身评级` headers and requires held-position qualifiers or §8 portfolio context (lines 138–139).

### F2 (P1): multiple rating tables — CLOSED

Amended plan lines 151–152:

> When multiple valid held-rating tables exist, retain anchors for all matching tables. Do not accept only the first table and discard the other anchors.

`metric_value` summarizes the first representative table (line 153); prior-period values go in anchor notes (line 155).

### F3 (P1): rating metric_value underspecified — CLOSED

Amended plan lines 153–155:

> `metric_value` should summarize current-period values from the first representative matching table as holding distribution, for example `长期信用评级: AAA=..., AAA以下=..., 未评级=..., 合计=...`; keep it concise with `_trim_note`. Include `合计` in `metric_value` when present. Prior-period values are supplementary and may be included in anchor notes, but they are not required in `metric_value`.

### F4 (P0): Decimal parsing contract gap — CLOSED

Amended plan includes a complete Share Value Parsing Contract (lines 200–206):

- Strip commas and all surrounding/internal whitespace before `Decimal()` conversion
- Treat `-`, `－`, `—`, and `--` as `Decimal(0)`
- Do not set a custom Decimal context precision
- `InvalidOperation` → fail closed with `na_reason="non_parseable_share_value"`
- Absolute tolerance `abs(computed - stated) <= Decimal("0.01")`

### F5 (P1): A/C/E/F column alignment fragile — CLOSED

Amended plan lines 180–183:

> Exclude row-label columns and total/合计 columns from class-column matching. If the mapping has four classes but the §10 table cannot align exactly four class value columns, fail closed as `ambiguous` with `na_reason="share_class_column_count_mismatch"`.

Plus §2 mapping or §10 header-label alignment as the matching mechanism (line 180).

### F6 (P1): zero beginning class — CLOSED

Amended plan lines 198–199:

> per-class net change ratio: if a class beginning is zero, set the class ratio to `None` and include note `class_beginning_zero`. This is not a failure for F 类期初 `-`; only aggregate beginning zero fails closed.

F class with dash-beginning will have `net_change_ratio=None` with `class_beginning_zero` note, not division by zero, and not omitted from class breakdown.

### F7 (P1): missing import smoke — CLOSED

Amended plan line 414:

```bash
uv run python -c "from fund_agent.fund.extractors.bond_risk_evidence import extract_bond_risk_evidence; print('import OK')"
```

Positioned before the full extraction pipeline so import-time errors are caught quickly.

---

## New Run-ID Check

Amended plan uses `bond-risk-narrow-006597-2024-20260528` as the new run-id (lines 416–418), distinct from the previous `bond-risk-evidence-006597-2024-20260528`. Output directories are correspondingly separated. No artifact collision risk. **PASS.**

---

## Cross-Cutting Invariant Re-Verification

| Invariant | Status |
|---|---|
| No FQ0-FQ6 weakening | PASS — quality gate unchanged, scope excludes `quality_gate.py` |
| No direct PDF/cache/source helper | PASS — extractor consumes `ParsedAnnualReport` only |
| No fund-own-rating confusion | PASS — explicit rejection rules + forbidden wording list |
| A/C/E/F all-class, not A-only | PASS — fail-closed on count mismatch, A-only test required |
| Drawdown remains weak | PASS — explicit hard boundary, no NAV-derived calculation |
| No schema/score/snapshot scope creep | PASS — only `bond_risk_evidence.py` + test file in scope |
| Validation command correctness | PASS — async wrapper, import smoke, new run-id all fixed |
| Test coverage sufficient | PASS — 10+ tests covering positive, negative, fail-closed, regression |

---

## Implementation Risk Notes (Non-Blocking)

These are implementation-level concerns, not plan defects. The plan as specified is sufficient; these notes are for the implementation worker and controller:

1. **§2 table-based mapping**: The plan prefers parsed §2 table mapping over raw text proximity. If the current `ParsedAnnualReport` does not expose §2 tables in a readily queryable form, the implementation will need to locate the correct table programmatically. The text-line fallback provides a safety net.

2. **§10 table scoring heuristic**: The plan's "score candidates" approach for table selection relies on keyword weighting. If the scoring function is not tuned carefully, edge cases with similarly-scored tables could trigger unnecessary fail-closed. The rejection rules for financial-statement tables are the primary defense; scoring is secondary.

3. **force_refresh=True parameter**: The validation command passes `force_refresh=True` to `load_annual_report`. Implementation should verify this parameter exists on the method signature; if named differently, adjust the smoke command accordingly.

---

## Conclusion

All 4 DS mandatory findings (M1–M4), all 3 DS advisory findings (A1–A3), and all 7 MiMo findings (F1–F7) are closed in the amended plan. The plan-fix traceability matrix (lines 34–66 of plan-fix) accurately reflects each amendment. No new blocking gaps were introduced by the amendments.

The plan is code-generation ready for the implementation worker.

## Re-Review Signature

- Re-reviewer: DS (plan re-review worker)
- Re-review type: adversarial plan re-review — mandatory finding closure verification
- Prior DS review: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-review-ds-20260528.md`
- Prior MiMo review: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-review-mimo-20260528.md`
- Plan-fix: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-fix-20260528.md`
- Artifact: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-rereview-ds-20260528.md`
- Verdict: **PASS** — 14/14 findings closed; plan is implementation-ready.
