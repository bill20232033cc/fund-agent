# Redemption Share Class Column Alignment Repair Plan — Re-Review

> Date: 2026-05-28
> Reviewer: MiMo (plan re-review worker)
> Artifacts reviewed:
> - Plan: `release-maintenance-redemption-share-class-column-alignment-repair-plan-20260528.md`
> - Plan fix: `release-maintenance-redemption-share-class-column-alignment-repair-plan-fix-20260528.md`
> - DS review: `release-maintenance-redemption-share-class-column-alignment-repair-plan-review-ds-20260528.md`
> - MiMo review: `release-maintenance-redemption-share-class-column-alignment-repair-plan-review-mimo-20260528.md`
> Status: **PASS**

## Conclusion

All MiMo and DS findings are closed or accepted as residual. The plan is code-generation-ready. No new planning risks were introduced by the fix.

## Finding Closure Audit

### DS F1 [CRITICAL] §2 cross-check circularity — CLOSED

Fix added: profile-table three-row contract (`下属分级基金的基金简称` + `下属分级基金的交易代码` + `报告期末下属分级基金的份额总额`), explicit `(page_number, table_index)` exclusion of §10 table, removal of generic `期末基金份额总额` candidates. Plan line 158-163 now states the anti-circularity requirement precisely. No residual risk beyond future table-shape drift (accepted).

### DS F2 [HIGH] Real §2 table shape not verified — CLOSED

Fix added: real 006597/2024 §2 profile table at `page_number=5, table_index=0` with rows 9/10/11 containing fund short names, codes, and ending shares. Plan lines 130-164. The plan-fix worker did not re-run extraction; the plan explicitly notes this and requires the implementation worker to prove the helper discovers the table through `ParsedAnnualReport`. This is an accepted residual, not a blocker.

### DS F3 [HIGH] `headers[0]` row-label identification too permissive — CLOSED

Fix added: `_share_change_value_columns` precondition requires (a) at least one required row's `row[0]` matches row-label semantics and (b) `headers[0]` must fail strict numeric parsing. Plan lines 222-227. Tests 8 and 9 cover numeric `headers[0]` and non-standard body shape.

### DS F4 [MEDIUM] `_share_change_value_columns` contract underspecified — CLOSED

Fix added: return contract explicitly defined as indexes neither row-label nor total/aggregate. Index 0 as default row-label only after precondition passes. Empty tuple / fail-closed when row-label unconfirmed. Plan lines 219-228.

### DS F5 [MEDIUM] Missing test: non-standard `headers[0]` — CLOSED

Test 8 added: numeric `headers[0]` fail-closed. Test 9 added: non-standard body shape fail-closed.

### DS F6 [MEDIUM] Missing test: all-zero dash value columns — CLOSED

Test 10 added: all-zero/dash aggregate beginning returns `aggregate_beginning_zero`.

### DS F7 [INFO] Split-line class labels — NO CHANGE NEEDED

Existing `_compact_text` normalization handles newline-split labels. Plan retained.

### DS F8 [INFO] Per-class zero vs aggregate zero — CLOSED

Test 10 covers aggregate zero fail-closed. Plan preserves per-class zero allowed when aggregate non-zero.

### MiMo F-1 [HIGH] Positional fallback not in current diff — CLOSED

Fix added: explicit "Important implementation gap" note at plan line 64 stating dirty diff does not contain positional fallback or §2 ending cross-check, and Slices 2/4 are new work.

### MiMo F-2 [MEDIUM] §2 ending cross-check source unverified — CLOSED

Same resolution as DS F2. Real §2 table shape added. Implementation worker must verify discoverability.

### MiMo F-3 [LOW] `_format_decimal` output mismatch — CLOSED

Fix added: metric assertions use `_format_decimal` output (`12982005127.5` not `12982005127.50`). `net_change_ratio` assertion uses stable prefix or parse-and-compare. Plan lines 417-423.

### MiMo F-4 [LOW] Mixed header detection imprecise — CLOSED

Fix added: signal defined as same criteria as explicit matching (fund code in compact header or `_contains_share_class_label`). Mixed fund-code/numeric signal test required. Plan line 252-258, Test 3.

### MiMo F-5 — Confirmed correct, no action.

### MiMo F-6 — Accepted residual, documented as narrow-scope limitation.

### MiMo F-7 — No change needed.

### MiMo F-8 — No change needed.

## Specific Task Verification

### Positional fallback explicit?

**Yes.** Plan line 64: "the current dirty diff does **not** contain the unlabeled positional alignment path and does **not** contain the §2 ending-share cross-check. Slices 2 and 4 below are new code that the implementation worker must add." Unambiguous.

### §2 cross-check source non-circular?

**Yes.** Three-row profile-table contract with `(page_number, table_index)` exclusion. Generic `期末基金份额总额` prohibited. Real 006597 evidence at `(5, 0)` with values matching §10 ending. Not circular.

### Metric format tests adjusted?

**Yes.** Plan lines 417-423 use `_format_decimal` output (trailing zero stripped). `net_change_ratio` uses prefix check, not exact long decimal.

### Mixed signal / headers[0] / all-zero / cross-check tests planned?

**Yes.** Tests 3 (mixed signal), 8 (numeric headers[0]), 9 (non-standard body), 10 (all-zero dash), 11 (cross-check self-certify). Coverage is complete for the required behaviors.

### Score/gate expectations consistent with drawdown residual?

**Yes.** Plan lines 533-547: `redemption_share_pressure` moves to satisfied, `drawdown_stress` stays weak, quality gate stays `warn`, `baseline_blocking` stays `true`. No score/gate semantic change attempted.

## New Risk Assessment

No new planning risks introduced. The fix is strictly additive to the plan artifact — it narrowed §2 cross-check scope, added real evidence, clarified preconditions, expanded tests, and made the dirty-diff gap explicit. No production code was changed. The plan's "Final Non-Goals" and "Worker Boundary" sections are intact.

## Residual Risks (Acceptable)

1. Plan-fix did not re-run extraction; implementation worker must prove §2 table discoverability through `ParsedAnnualReport`.
2. Future annual reports with different §2 profile table shapes will fail closed until a separately reviewed rule is added.
3. `_find_share_change_row` preferred keyword fallback (`总申购`/`总赎回`) may miss weaker labels like `本期申购份额` — acceptable for narrow scope.

## Verdict

**PASS** — All findings from MiMo and DS reviews are closed or accepted as residual. Plan is code-generation-ready.
