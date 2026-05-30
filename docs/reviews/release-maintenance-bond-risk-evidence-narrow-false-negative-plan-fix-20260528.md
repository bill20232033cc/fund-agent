# Bond Risk Evidence Narrow False-Negative Plan Fix

> Date: 2026-05-28
> Role: planning-fix worker, not controller, not implementation worker
> Target plan: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-20260528.md`
> Review inputs:
> - `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-review-ds-20260528.md`
> - `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-review-mimo-20260528.md`
> Status: complete

## Worker Self-Check

- Role confirmed: planning-fix worker only.
- No gateflow was started.
- No production code, tests, generated reports, control doc, README, score, snapshot, quality gate, git state, PR, or external state was modified.
- Only the narrow gate plan artifact was updated and this plan-fix artifact was created.
- No implementation validation commands were run.

## Fix Summary

The plan was amended to absorb the accepted DS and MiMo plan-review findings. The main changes are:

- Clarified `contract_status=partial` vs `extraction_mode=ExtractionMode.estimated`.
- Tightened held-rating table acceptance so fund-own-rating semantics are rejected.
- Added numeric shape and multi-table anchor requirements for rating distribution evidence.
- Replaced first-match §10 share table selection with scan-all best-candidate selection.
- Added explicit Decimal parsing, tolerance, and fail-closed contracts.
- Tightened A/C/E/F column alignment and F-class zero-beginning handling.
- Added targeted tests and corrected validation commands, including async repository smoke and import smoke.
- Changed the real-path run-id/output directories to `bond-risk-narrow-006597-2024-20260528`.

## Findings Disposition

| Finding | Source | Disposition | Plan amendment |
|---|---|---|---|
| M1: repository smoke command missing async wrapper | DS | Accepted and fixed | Validation command now uses `asyncio.run(repo.load_annual_report(...))`. |
| M2: `extraction_mode` has no `partial` value | DS | Accepted and fixed | Added extraction-mode decision: keep `ExtractionMode.estimated` when `bond_risk_contract_status=partial`; no schema change. |
| M3: share table first-match risk | DS | Accepted and fixed | §10 table selection now requires scanning all parsed tables, rejecting/downgrading net-asset tables, selecting a unique best candidate, or failing closed. |
| M4: rating table numeric shape too loose | DS | Accepted and fixed | Rating distribution detection now requires rating category rows plus parseable current-period numeric amount and row/table anchors. |
| A1: Decimal tolerance unspecified | DS | Accepted and fixed | Reconciliation tolerance set to `Decimal("0.01")`. |
| A2: missing §2 parsed mapping helper test | DS | Accepted and fixed | Added required test `test_share_class_evidence_from_section_two_table`. |
| A3: `_trim_note` reference | DS | No plan change needed | Review confirmed helper already exists; plan keeps concise metric formatting requirement. |
| F1: fund-own-rating table false positive | MiMo | Accepted and fixed | Detection now rejects `本基金评级` / `基金评级信息` / `基金自身评级` and requires held-position qualifiers or §8 portfolio context. |
| F2: multiple rating tables unspecified | MiMo | Accepted and fixed | Plan now requires preserving anchors for all valid held-rating tables. |
| F3: rating `metric_value` underspecified | MiMo | Accepted and fixed | Plan now says `metric_value` summarizes current-period values from a representative table and includes `合计` when present; prior-period values may go in notes. |
| F4: Decimal parsing contract gap | MiMo | Accepted and fixed | Plan now specifies comma/whitespace removal, dash variants as zero, `InvalidOperation` fail-closed with `non_parseable_share_value`, and default Decimal precision. |
| F5: A/C/E/F column alignment fragile | MiMo | Accepted and fixed | Plan now requires §2 mapping or §10 header-label alignment, excludes total columns, and fails closed with `share_class_column_count_mismatch` on count mismatch. |
| F6: F-class zero beginning edge case | MiMo | Accepted and fixed | Plan now allows per-class beginning zero by setting ratio to `None` and noting `class_beginning_zero`; only aggregate beginning zero fails closed. |
| F7: missing targeted import smoke | MiMo | Accepted and fixed | Added `uv run python -c "from fund_agent.fund.extractors.bond_risk_evidence import extract_bond_risk_evidence; print('import OK')"`. |

## Explicit User-Required Items

| Required item | Status |
|---|---|
| 1. `FundDocumentRepository` smoke uses `asyncio.run` for async `load_annual_report` | Fixed |
| 2. No `ExtractionMode.partial`; partial contract status maps to `ExtractionMode.estimated` without schema change | Fixed |
| 3. Share table scans all tables, selects §10/基金份额/份额总额 best candidate, rejects/downgrades financial-statement tables, fails closed without unique survivor | Fixed |
| 4. Credit rating table must be held portfolio/security semantic and rejects fund-own-rating semantic | Fixed |
| 5. Rating table requires rating category plus current-period numeric amount and anchors | Fixed |
| 6. Multiple held-rating tables retain all anchors; `metric_value` may summarize first representative current-period table with `合计`; prior-period can go in note | Fixed |
| 7. Decimal parsing contract, dash-as-zero, `InvalidOperation` fail-closed, and `Decimal("0.01")` tolerance | Fixed |
| 8. A/C/E/F alignment uses §2 mapping or §10 headers, excludes total columns, count mismatch fails closed with `share_class_column_count_mismatch`, no A-only acceptance | Fixed |
| 9. F-class beginning zero does not fail; per-class ratio is `None` with `class_beginning_zero`; aggregate beginning zero fails closed | Fixed |
| 10. Targeted import smoke added | Fixed |
| 11. §2 parsed mapping helper test requirement added | Fixed |
| 12. New real-path run-id/output dirs use `bond-risk-narrow-006597-2024-20260528` | Fixed |

## Remaining Risks

- The plan is not implementation-reviewed after these amendments; controller or a later plan review may still request wording or test refinements.
- The exact private helper names remain illustrative. Implementation may choose equivalent names as long as the contract is preserved.
- Real `006597` validation remains an implementation/controller responsibility. This planning-fix worker did not run validation.
- `drawdown_stress` remains intentionally unsatisfied under the current contract, so `bond_risk_evidence_missing.baseline_blocking=true` is still expected after this narrow fix unless a future drawdown metric gate changes the contract.
