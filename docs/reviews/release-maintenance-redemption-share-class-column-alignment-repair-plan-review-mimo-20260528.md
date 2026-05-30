# Redemption Share Class Column Alignment Repair Plan — Adversarial Review

> Date: 2026-05-28
> Reviewer: MiMo (plan review worker)
> Artifact reviewed: `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-plan-20260528.md`
> Status: **PASS_WITH_FINDINGS**

## Conclusion

Plan is sound in its core diagnosis and repair strategy. The root cause analysis is correct: real §10 headers contain inception-date class totals (numeric), not A/C/E/F labels, so explicit header matching fails with `share_class_column_count_mismatch`. The positional fallback with multi-layer guardrails is a reasonable conservative approach.

However, there are findings that could cause the implementation to fail real 006597 validation or produce incorrect accepted results if not addressed.

## Required Reading Completed

- `AGENTS.md`
- Plan artifact (above)
- Controller judgment: `release-maintenance-bond-risk-evidence-narrow-false-negative-validation-failure-controller-judgment-20260528.md`
- `reports/extraction-snapshots/bond-risk-narrow-006597-2024-20260528/snapshot.jsonl`
- `reports/scoring-runs/bond-risk-narrow-006597-2024-20260528/score.json`
- Current `git diff -- fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py`

## Findings

### F-1: Positional Fallback And §2 Cross-Check Not In Current Diff (HIGH)

**Severity**: HIGH — gate blocker if implementation worker assumes diff already covers the repair.

**Evidence**: The current dirty diff contains the §2 mapping extraction (`_ShareClassMapping`, `_share_class_mapping_from_profile_tables`, `_share_class_mapping_from_profile_lines`), §10 table selection (`_find_share_change_table`, `_share_change_table_score`), row identification (`_find_share_change_rows`, `_find_share_change_row`), arithmetic checks, and metric formatting. But `_align_share_change_columns()` at line 1603 only does **explicit header matching** — it requires each class to match exactly one header by fund code or class label. There is no positional fallback path, no `_share_change_value_columns()` helper, no `no signal → try positional` branch, and no §2 ending-share cross-check.

The real 006597 §10 headers are:

```python
("基金合同生\n效日...", "191,879,496.71", "46,593,432.66", "-", "-")
```

None of these contain `006597`, `006598`, `014217`, `022176`, `A`, `C`, `E`, or `F`. So the current code will still return `share_class_column_count_mismatch` for real 006597 after the diff is applied.

**Risk**: If the implementation worker accepts the current diff as "already implemented" and only adds tests, real validation will still fail.

**Recommendation**: Plan should explicitly state: "Slices 2 and 4 describe new code to be written. The current dirty diff implements Slices 1, 3, 5, 6 partially but does NOT contain the positional fallback or §2 ending cross-check. Implementation worker must add these before running real validation."

### F-2: §2 Ending Share Cross-Check Source Unverified (MEDIUM)

**Severity**: MEDIUM — could cause positional fallback to fail-closed even when data is correct.

**Evidence**: Slice 4 requires searching parsed §2 tables for `报告期末基金份额总额` / `期末基金份额总额` / `下属分级基金的份额总额` rows to cross-check against §10 ending per class. The plan itself notes: "If current parsed §2 table structure does not expose ending shares in a clean row, the implementation worker should stop and report the exact parsed §2 table shape rather than guessing."

The §2 table for 006597 was reproduced in the plan as page 5, table 0, with rows like `本报告期期\n初基金份额\n总额` etc. — but these are from the **§10** table, not §2. The §2 profile table (page 5) contains fund name, inception date, class codes, etc. Whether it also contains ending share totals per class is not verified in the plan.

**Risk**: If §2 doesn't expose ending shares, the positional fallback will always fail with `share_class_ending_cross_check_missing`, making the repair ineffective.

**Recommendation**: Implementation worker must first verify what §2 parsed tables actually contain for 006597. If ending shares are not available, the plan needs an alternative cross-check strategy (e.g., §10 internal consistency only, with a stricter arithmetic tolerance).

### F-3: `_format_decimal` Output May Not Match Plan's Expected Metric Strings (LOW)

**Severity**: LOW — test assertion failures, not logic errors.

**Evidence**: Plan expects metric values like `beginning=12982005127.50`. But `_format_decimal(Decimal("12982005127.50"))` works as:

1. `Decimal("12982005127.50").normalize()` → `Decimal('12982005127.5')` (trailing zero stripped)
2. `normalized.to_integral()` → `Decimal('12982005127')` ≠ `Decimal('12982005127.5')`
3. `format(Decimal('12982005127.5'), "f")` → `"12982005127.5"`

So actual output is `beginning=12982005127.5`, not `beginning=12982005127.50`. The plan's test assertions use exact string matching (`beginning=12982005127.50`), which will fail.

Similarly, `net_change_ratio` for real 006597 will be a long decimal like `-0.18737097435406052...` rather than the plan's `≈-0.18737`. If tests assert the exact string, they'll fail.

**Recommendation**: Plan test assertions should use `in` checks (e.g., `"beginning=12982005127.5" in metric_value`) rather than exact equality. Or clarify that `_format_decimal` behavior determines the exact string format.

### F-4: Mixed Header Detection Logic Not Specified Precisely (LOW)

**Severity**: LOW — could lead to incorrect accepted or incorrect ambiguous.

**Evidence**: Slice 2 step 6 says: "If some but not all headers contain class/fund-code signal, fail closed with `share_class_column_count_mismatch`." But the detection of "signal" is ambiguous. The real §10 headers contain numbers like `191,879,496.71` — these are not fund codes (6-digit pattern) and not class labels. But what if a future table has one header with a class label and three without? The plan says fail closed, which is correct. But the implementation needs to define "signal" precisely: `fund_code in compact_header` or `_contains_share_class_label(header, class_label)`.

The current explicit matching loop already checks both. The question is whether the implementation adds a pre-scan to detect "partial signal" before attempting full matching, or relies on the existing loop returning empty matches for some classes.

**Recommendation**: Implementation should use the same matching criteria as the explicit loop. If any class gets a unique match but another doesn't, that's "mixed" → fail closed. If no class gets any match, try positional. This is clear enough from the plan but should be explicitly stated in the implementation notes.

### F-5: Real §10 Redemption Row Sign Handling Is Correct (NO ISSUE)

**Severity**: N/A — confirming no issue.

**Evidence**: Plan Slice 3 shows:

```text
A: 7,699,969,800.13 + 27,623,952,157.07 - 29,612,697,690.11 + 0 = 5,711,224,267.09
```

The real §10 redemption row label is `减：本报告期基金总赎回份额` with positive values. The code computes `net_change = subscription - redemption + split`. The "减：" prefix is part of the row label, not the numeric value. So the arithmetic is correct — no sign confusion.

The balance sheet showing negative redemption is a different context (cash flow statement convention). The §10 share change table uses positive values with "减" in the label. The plan correctly treats these as positive numbers subtracted in the formula.

### F-6: `_find_share_change_row` Preferred Keyword Fallback Returns None (LOW)

**Severity**: LOW — real 006597 should match, but edge cases could break.

**Evidence**: When `preferred_keyword_groups` is non-empty, the function iterates `matches` and returns the first match whose text contains all keywords of any preferred group. If no preferred match is found, it returns `None` — not the first non-preferred match.

For real 006597:
- Subscription row: `本报告期基金总申购份额` — contains `总申购` → preferred match ✓
- Redemption row: `减：本报告期基金总赎回份额` — contains `总赎回` → preferred match ✓

So real 006597 is fine. But if a fund's §10 uses `本期申购份额` (without `总`), the preferred match fails and returns `None`, causing `incomplete_share_change_rows`. The plan doesn't test this edge case.

**Recommendation**: This is acceptable for the narrow repair scope. Document as a known limitation for future work.

### F-7: Commit/Validation Boundary Clarity (INFORMATIONAL)

**Severity**: INFORMATIONAL — no action needed, but worth noting.

**Evidence**: The plan's "Final Non-Goals" section says "No commit/push/PR/release." The "Real 006597 Validation Plan" section describes running validation commands. The current dirty diff is the baseline.

The question from the review task ("是否需要先接受当前未提交 narrow diff 为 baseline") is answered by the plan: "The current dirty diff in `fund_agent/fund/extractors/bond_risk_evidence.py` and `tests/fund/extractors/test_bond_risk_evidence.py` is the implementation baseline for this repair."

This means:
1. Implementation worker edits on top of the dirty diff.
2. After implementation, validation runs against the full dirty diff (old + new changes).
3. No intermediate commit is required before this gate's implementation.
4. The gate's accepted commit (if validation passes) would be a single commit covering both the old dirty diff and the new positional fallback.

This is clear enough from the plan context. No gap.

### F-8: Score/Quality Gate Expectations Consistent With Drawdown Residual (NO ISSUE)

**Severity**: N/A — confirming consistency.

**Evidence**: Plan expects:
- `missing_evidence_groups` drops to `["drawdown_stress"]` only
- `bond_risk_evidence_missing.baseline_blocking` remains `true`
- Quality gate remains `warn` while drawdown is unresolved

Current `score.json` shows `missing_evidence_groups` includes both `drawdown_stress` and `redemption_share_pressure`. After repair, `redemption_share_pressure` should move to satisfied, leaving only `drawdown_stress`. Since `drawdown_stress` is correctly preserved as weak (not accepted), `baseline_blocking` stays `true` and quality gate stays `warn`. This is consistent.

## Summary

| Finding | Severity | Gate Impact |
|---------|----------|-------------|
| F-1: Positional fallback not in current diff | HIGH | Implementation will fail real validation if not addressed |
| F-2: §2 ending cross-check source unverified | MEDIUM | Positional fallback may always fail-closed |
| F-3: `_format_decimal` output format mismatch | LOW | Test assertions will fail on exact string match |
| F-4: Mixed header detection logic imprecise | LOW | Implementation ambiguity |
| F-5: Redemption sign handling | N/A | Confirmed correct |
| F-6: Preferred keyword fallback returns None | LOW | Known limitation, acceptable |
| F-7: Commit boundary clarity | INFORMATIONAL | Clear from plan context |
| F-8: Score/gate expectations | N/A | Confirmed consistent |

## Verdict

**PASS_WITH_FINDINGS** — Plan is implementable with the identified gaps addressed. F-1 is the most critical: the implementation worker must understand that the current diff does NOT contain the positional fallback or §2 cross-check, and these must be written fresh. F-2 should be verified before implementation proceeds. F-3 should be addressed in test assertions.
