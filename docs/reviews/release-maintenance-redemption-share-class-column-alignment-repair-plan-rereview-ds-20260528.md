# Redemption Share Class Column Alignment Repair Plan — DS Re-Review

> Date: 2026-05-28
> Reviewer: DS (plan re-review worker)
> Gate: `redemption share class column alignment repair gate`
> Re-reviewed artifacts:
> - `release-maintenance-redemption-share-class-column-alignment-repair-plan-20260528.md` (plan, post-fix)
> - `release-maintenance-redemption-share-class-column-alignment-repair-plan-fix-20260528.md` (plan-fix)
> - `release-maintenance-redemption-share-class-column-alignment-repair-plan-review-ds-20260528.md` (DS review)
> - `release-maintenance-redemption-share-class-column-alignment-repair-plan-review-mimo-20260528.md` (MiMo review)
> Conclusion: **PASS**

## Scope

This is a strict plan re-review. No code changes, no gateflow, no implementation. The sole question is whether the DS and MiMo review findings have been closed in the plan-fix.

## DS Findings — Closure Status

### DS F1 [CRITICAL] §2 Ending Cross-Check Circularity Risk

**Original finding**: §2 cross-check could scan §10 tables and self-certify.

**Plan-fix changes verified**:
- §2 cross-check now requires a same-source profile table containing all three row labels: `下属分级基金的基金简称`, `下属分级基金的交易代码`, `报告期末下属分级基金的份额总额` (plan lines 158–159).
- §10 share-change table excluded by `(page_number, table_index)` (plan line 162).
- Generic `期末基金份额总额` / `报告期末基金份额总额` candidates outside the profile-table shape explicitly prohibited (plan lines 163–164).
- Implementation must retain/report the cross-check table through anchor or implementation report (plan line 165).
- Plan-fix F1 disposition (plan-fix lines 142–153) correctly documents the resolution.

**Verdict**: CLOSED. The three-row profile-table contract plus §10 exclusion eliminates the circularity risk. Future reports with different §2 disclosure layouts will fail closed rather than silently self-certify.

### DS F2 [HIGH] Real §2 Table Shape Not Verified in Plan

**Original finding**: Plan relied on hypothetical row patterns without confirming real 006597 §2 data.

**Plan-fix changes verified**:
- New "Real §2 Profile Table Evidence" section added (plan lines 128–164).
- Real evidence: `page_number=5`, `table_index=0`.
- Row 9: A/C/E/F fund short names written into plan.
- Row 10: `006597 / 006598 / 014217 / 022176` written into plan.
- Row 11: `5,711,224,267.09 / 4,760,029,015.27 / 25,795,859.12 / 52,531,021.84` written into plan.
- Per-class ending values explicitly stated (plan lines 149–153).
- Plan-fix F2 disposition (plan-fix lines 157–167) correctly notes residual: plan-fix didn't run extraction; implementation validation must still prove the coded helper finds this table.

**Verdict**: CLOSED. The real §2 table shape is concrete evidence in the plan. The residual (plan-fix didn't re-run extraction) is acceptable — it transfers correctly to implementation validation responsibility.

### DS F3 [HIGH] headers[0] Row-Label Identification Too Permissive

**Original finding**: Unconditional `headers[0]` as row-label was over-fitted; a malformed table with numeric `headers[0]` could pass through.

**Plan-fix changes verified**:
- `_share_change_value_columns()` now has explicit preconditions (plan lines 222–226):
  - At least one required row's `row[0]` must match row-label semantics: `期初`, `申购`, `赎回`, `期末`, `拆分`, `变动`, `份额`, or `项目`.
  - `headers[0]` must fail strict ordinary-number parsing; if it parses as numeric, return empty tuple and fail closed.
- If row-label column cannot be confirmed, return empty tuple and fail closed (plan line 227).
- Tests added: Test 8 (numeric `headers[0]`) and Test 9 (non-standard body shape) cover these preconditions (plan lines 475–486).

**Verdict**: CLOSED. The dual precondition (row-label semantics on body + numeric rejection on header) adequately guards against over-fitting. The exact `na_reason` is allowed to vary between `share_class_column_alignment_ambiguous` and `share_class_column_count_mismatch` — acceptable because both are `ambiguous`.

### DS F4 [MEDIUM] `_share_change_value_columns` Semantics Underspecified

**Original finding**: Return contract didn't specify what happens when row-label can't be identified.

**Plan-fix changes verified**:
- Return contract now explicitly defined (plan lines 219–228):
  - Return indexes that are neither row-label nor total/aggregate columns.
  - Index 0 default is valid only after row-label precondition passes.
  - Unknown row-label → empty tuple → caller fails closed.
  - Total column exclusion reuses `_is_total_share_header`.
- Plan-fix F4 disposition (plan-fix lines 82–93) confirms.

**Verdict**: CLOSED. Contract is precise and fail-closed.

### DS F5 [MEDIUM] Missing Test: Non-Standard headers[0]

**Original finding**: No test for unrecognizable `headers[0]`.

**Plan-fix changes verified**:
- Test 8: numeric `headers[0]` like `"123,456.78"` → fail-closed (plan lines 475–481).
- Test 9: non-standard body shape where `row[0]` cells lack required row-label semantics → fail-closed (plan lines 483–486).

**Verdict**: CLOSED. Both edge cases are covered.

### DS F6 [MEDIUM] Missing Test: All-Zero Value Columns

**Original finding**: No test for all class columns being dash/zero.

**Plan-fix changes verified**:
- Test 10: all class value columns are dash/zero in all required rows → `aggregate_beginning_zero` (plan lines 487–494).
- Plan explicitly preserves: per-class zero beginning allowed only when aggregate beginning is non-zero.

**Verdict**: CLOSED.

### DS F7 [INFO] Split-Line Class Labels

**Original disposition**: No plan change required; normalization already handles it.

**Plan-fix**: Confirmed no change required. Existing `_normalized_header_text()` and `_header_has_explicit_share_class()` already cover this through `_compact_text`.

**Verdict**: CORRECTLY DEFERRED. Implementation review should verify the explicit path still normalizes line breaks, but no plan gap.

### DS F8 [INFO] Per-Class Zero vs Aggregate Zero Assertion

**Original disposition**: No plan change required; existing code already has the guard.

**Plan-fix**: Added Test 10 as explicit coverage for aggregate beginning zero. Correctly preserved the per-class-vs-aggregate distinction.

**Verdict**: CORRECTLY RESOLVED. Test coverage now matches the semantic distinction.

## MiMo Findings — Closure Status

### MiMo F-1 [HIGH] Positional Fallback Not In Current Diff

**Original finding**: Implementation worker could assume the dirty diff already covers the repair.

**Plan-fix changes verified**:
- "Important implementation gap" note added (plan lines 63–65):
  - "the current dirty diff does **not** contain the unlabeled positional alignment path"
  - "does **not** contain the §2 ending-share cross-check"
  - "Slices 2 and 4 below are new code that the implementation worker must add"
- Plan-fix F-1 disposition (plan-fix lines 246–255) confirms.

**Verdict**: CLOSED. The gap is explicit and unambiguous. Implementation review must still verify these are actually added, but the plan no longer leaves room for misinterpretation.

### MiMo F-2 [MEDIUM] §2 Ending Cross-Check Source Unverified

**Original finding**: Same concern as DS F2 — §2 table shape unverified.

**Plan-fix changes verified**: Same resolution as DS F2 above — real §2 profile table shape and values added.

**Verdict**: CLOSED.

### MiMo F-3 [LOW] `_format_decimal` Output Mismatch

**Original finding**: Test assertions using `beginning=12982005127.50` would fail because `_format_decimal` strips trailing zeroes.

**Plan-fix changes verified**:
- Aggregate metric assertion changed from `beginning=12982005127.50` to `beginning=12982005127.5` (plan lines 417–418).
- `net_change_ratio` tests now require stable prefix (`net_change_ratio=-0.18737`) or parse-and-compare approach rather than exact long-string assertion (plan lines 422–423).

**Verdict**: CLOSED. Assertion format now matches `_format_decimal` output behavior.

### MiMo F-4 [LOW] Mixed Header Detection Logic Imprecise

**Original finding**: "Signal" definition was ambiguous.

**Plan-fix changes verified**:
- Slice 2 step 5 now defines signal explicitly (plan lines 249–252): "mapped fund code appears in compact header text; or `_contains_share_class_label(header, class_label)` is true."
- Test 3 (plan lines 433–445) covers mixed-signal case: one column with fund code, others numeric → fail closed.
- Plan-fix F-4 disposition (plan-fix lines 283–293) confirms.

**Verdict**: CLOSED. Signal criteria are now the same as the explicit matching loop, and the mixed-signal test enforces fail-closed.

### MiMo F-5 [NO ISSUE] Redemption Sign Handling

**Original**: Confirmed correct. §10 redemption values are positive under `减：` label.

**Plan-fix**: Added explicit note (plan lines 291–292): "§10 redemption row values are positive numbers under a row label beginning with `减：`; compute `subscription - redemption + split`. Do not import negative-number semantics from balance-sheet or cash-flow statement contexts."

**Verdict**: CONFIRMED. Arithmetic semantics are correct and fully documented.

### MiMo F-6 [LOW] Preferred Keyword Fallback Limitation

**Original**: Accepted as known limitation for narrow repair scope.

**Plan-fix**: Accepted residual — no plan change. Real 006597 should match preferred keywords.

**Verdict**: ACCEPTED RESIDUAL. Correctly scoped for this gate. Future funds with weaker labels like `本期申购份额` may still fail closed; that belongs in a separate rule-expansion gate.

### MiMo F-7 [INFORMATIONAL] Commit/Validation Boundary

**Original**: No action needed.

**Plan-fix**: No change required.

**Verdict**: CORRECTLY DEFERRED.

### MiMo F-8 [NO ISSUE] Score/Quality Gate Expectations

**Original**: Confirmed consistent.

**Plan-fix**: No change required.

**Verdict**: CONFIRMED.

## Focused Re-Check Against Required Questions

### 1. §2 ending cross-check 是否限定同源 profile table 并排除 §10 自证

**PASS**. Plan lines 158–165:
- Requires three same-table row labels (`基金简称`, `交易代码`, `报告期末下属分级基金的份额总额`).
- Requires `(page_number, table_index)` exclusion of the §10 table.
- Prohibits generic `期末基金份额总额` matching outside the profile-table shape.
- Requires implementation to retain/report the cross-check table for reviewer verification.

### 2. 真实 §2 page 5 table 0 row 9/10/11 是否写入

**PASS**. Plan lines 130–153:
- Full `page_number=5, table_index=0` captured.
- Row 9: A/C/E/F fund short names.
- Row 10: 006597/006598/014217/022176 fund codes.
- Row 11: Per-class ending share values.
- Per-class breakdown values explicitly stated.

### 3. 当前 dirty diff gap 是否明确

**PASS**. Plan lines 63–65:
- "the current dirty diff does **not** contain the unlabeled positional alignment path and does **not** contain the §2 ending-share cross-check."
- "Slices 2 and 4 below are new code that the implementation worker must add."
- "Do not treat the current dirty diff as already having repaired the real 006597 failure."

### 4. headers[0]/value columns precondition 是否足够

**PASS**. Plan lines 222–228:
- Dual precondition: (a) at least one row's `row[0]` matches row-label semantics, (b) `headers[0]` fails strict numeric parsing.
- If either fails: empty tuple → fail-closed.
- Total/aggregate column exclusion reuses existing `_is_total_share_header`.
- Tests 8 and 9 cover both precondition failures.

### 5. 测试断言格式和新增 fail-closed tests 是否覆盖

**PASS**:
- `_format_decimal` output corrected: `beginning=12982005127.5` (plan line 418).
- `net_change_ratio` uses stable prefix or parse-and-compare (plan lines 422–423).
- Fail-closed tests now cover:
  - Mixed header signals (Test 3)
  - §2 cross-check missing (Test 4)
  - §2 cross-check mismatch (Test 5)
  - Numeric headers[0] (Test 8)
  - Non-standard body shape (Test 9)
  - All-zero/dash aggregate (Test 10)
  - §2 self-certification prevention (Test 11, two variants)

## Residual Risks (Post Plan-Fix)

These are the residual risks that remain after plan-fix and are acceptable for this gate:

1. **Plan-fix didn't run extraction validation**: The real §2 table shape is written into the plan as controller-mandated evidence. The implementation worker must still prove the coded helper discovers this table through `ParsedAnnualReport`. If the parsed representation differs, the helper will fail closed — which is safe but means the gate may not achieve its primary goal.

2. **Narrow §2 profile-table contract**: Future annual reports with materially different §2 disclosure layouts will fail closed with `share_class_ending_cross_check_missing`. This is correct fail-closed behavior and belongs in a separate rule-expansion gate.

3. **Na_reason flexibility**: The exact na_reason for row-label precondition failure may be either `share_class_column_alignment_ambiguous` or `share_class_column_count_mismatch`. Both are ambiguous and fail-closed, so there is no safety gap, but implementation review should verify the reason is distinctive enough for debugging.

4. **Preferred keyword fallback limitation** (MiMo F-6): Real 006597 matches preferred keywords, but future funds without `总申购`/`总赎回` labels may fail closed. This is acceptable for this gate.

## Verdict

**PASS** — All 16 findings (8 DS + 8 MiMo) are closed or correctly accepted as residual. No DS or MiMo finding remains unaddressed. The plan-fix accurately identifies each finding, correctly disposes it, and honestly reports residual risks. The plan is code-generation-ready.

No blocker.
