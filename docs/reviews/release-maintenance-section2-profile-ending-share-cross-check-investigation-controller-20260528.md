# Section2 Profile Ending-Share Cross-Check Investigation — Controller Report

> Date: 2026-05-28
> Role: Gateflow controller (investigation, not implementation)
> Gate: `section2 profile ending-share cross-check repair gate`
> Branch: `codex/local-reconciliation`
> Status: root-cause confirmed; ready for plan/review/implementation cycle

## Self-Check

- Role confirmed: controller investigation only. No code changes, no review, no controller judgment on implementation, no commit, no PR, no push, no merge, no golden promotion.
- Dirty scope inventoried below.
- All annual report data accessed through `FundDocumentRepository` only; no direct PDF/cache/source helper access.

## Dirty Scope Inventory

### Branch

`codex/local-reconciliation`

### Modified Files (uncommitted diff from previous gates)

| File | Origin | Assessment |
|---|---|---|
| `fund_agent/fund/extractors/bond_risk_evidence.py` | narrow false-negative gate + column alignment repair gate | **Partially reusable**: credit_risk fix and leverage_liquidity changes accepted; redemption cross-check code present but broken due to `份` parsing bug |
| `tests/fund/extractors/test_bond_risk_evidence.py` | same gates | **Partially reusable**: credit_risk/leverage tests valid; redemption cross-check tests use synthetic fixtures that don't expose the real `份` suffix |

### Untracked Review Artifacts

From narrow false-negative gate:
- `release-maintenance-bond-risk-evidence-narrow-false-negative-*.md` (plan, reviews, rereviews, implementation, validation-failure controller judgment)

From column alignment repair gate:
- `release-maintenance-redemption-share-class-column-alignment-repair-*.md` (implementation, code reviews DS/MiMo, validation-failure controller judgment)

From earlier sessions:
- repo-review, comprehensive-audit-report, tmux-agent-memory-store, `--help` stray file

All untracked artifacts are evidence only; none are staged or committed.

### Dirty Scope Verdict

The uncommitted diff contains a working credit_risk fix and a structurally sound redemption cross-check framework, but the cross-check's value parsing fails on real data. The diff is reusable as a base — this gate only needs to fix the `份` suffix parsing issue within the existing cross-check path.

---

## Root Cause Analysis

### Symptom

`_extract_redemption_share_pressure` on real `006597 / 2024` produces:

```
status=ambiguous
strength=ambiguous
na_reason=share_class_ending_cross_check_missing
```

The unlabeled §10 column alignment logic works (finds Table #78, maps 4 columns by position), but the independent §2 profile ending-share cross-check returns `None`, preventing the aggregate from being accepted.

### Root Cause

`_parse_plain_decimal` in the current diff handles:
1. Whitespace compaction via `_compact_text`
2. Comma removal via `.replace(",", "")`
3. Dash-as-zero handling
4. Percentage rejection

It does **NOT** strip the Chinese `份` (shares/units) suffix.

Real §2 profile Table #0 row[11] (ending-share row) cells contain:

| Cell | Raw Value | After compact+comma-strip | `Decimal()` result |
|---|---|---|---|
| cell[1] | `5,711,224,267\n.09份` | `5711224267.09份` | `InvalidOperation` → `None` |
| cell[2] | `4,760,029,01\n5.27份` | `4760029015.27份` | `InvalidOperation` → `None` |
| cell[3] | `25,795,859.1\n2份` | `25795859.12份` | `InvalidOperation` → `None` |
| cell[4] | `52,531,021.8\n4份` | `52531021.84份` | `InvalidOperation` → `None` |

All four cells fail → `_profile_ending_values_by_class` returns `None` → `_share_class_ending_cross_check_from_profile_tables` returns `None` → unlabeled path fails with `share_class_ending_cross_check_missing`.

### Why Unit Tests Didn't Catch This

The unit test fixtures use clean numeric strings like `"5,711,224,267.09"` without the `份` suffix, because synthetic `ParsedTable` construction doesn't replicate the PDF parser's newline-split+unit-suffix behavior. The real annual report's PDF parser emits cells with embedded newlines and `份` suffix that synthetic fixtures don't model.

### Call Chain

```
_extract_redemption_share_pressure
  → _align_share_change_columns (unlabeled path)
    → _aggregate_share_class_changes
      → _share_class_ending_cross_check_from_profile_tables
        → _profile_ending_values_by_class
          → _parse_share_decimal → _parse_plain_decimal
            ← returns None for all cells containing "份"
          ← returns None
        ← returns None
      ← returns None (cross_check_missing)
    ← na_reason="share_class_ending_cross_check_missing"
```

---

## Fix Strategy

The fix is a single localized change: strip the `份` suffix (and optionally other known Chinese unit suffixes like `元`) before `Decimal()` parsing.

### Option A (Recommended): Fix in `_parse_plain_decimal`

Add a regex or suffix strip to remove trailing `份` after compact+comma-strip:

```python
normalized = re.sub(r"份$", "", normalized)
```

This makes `_parse_plain_decimal` tolerant of Chinese unit suffixes everywhere it's used (§10 values, §2 values, credit_risk tables). The suffix is always terminal after compact, so a simple endswith check or regex is safe.

### Option B: Fix only in `_profile_ending_values_by_class`

Pre-strip `份` from cells before calling `_parse_share_decimal`. More targeted but leaves the general parser fragile for other callers that may encounter `份`.

### Recommendation

Option A is preferred because `份` is a standard Chinese disclosure unit that can appear in any share-related table cell. It doesn't weaken parsing — it removes a known non-numeric suffix that would never be part of a valid `Decimal`.

---

## Evidence

### Real §2 Profile Table Structure (Table #0, page 5)

Three rows in the same table provide the cross-check:

| Row | Label Cell | Value Cells |
|---|---|---|
| row[9] | `下属分级基金的基金简称` | `国泰利享中\n短债债券A` \| `国泰利享中\n短债债券C` \| `国泰利享中\n短债债券E` \| `国泰利享中\n短债债券F` |
| row[10] | `下属分级基金的交易代码` | `006597` \| `006598` \| `014217` \| `022176` |
| row[11] | `报告期末下属分级基金的份\n额总额` | `5,711,224,267\n.09份` \| `4,760,029,01\n5.27份` \| `25,795,859.1\n2份` \| `52,531,021.8\n4份` |

Keyword matching works correctly for all three rows (`_compact_text` resolves embedded newlines). Class label extraction returns `('A', 'C', 'E', 'F')`. Fund code extraction returns `('006597', '006598', '014217', '022176')`.

### Expected Cross-Check Values (after fix)

| Class | §2 Profile Ending | §10 Ending | Match? |
|---|---|---|---|
| A | 5,711,224,267.09 | 5,711,224,267.09 | Yes |
| C | 4,760,029,015.27 | 4,760,029,015.27 | Yes |
| E | 25,795,859.12 | 25,795,859.12 | Yes |
| F | 52,531,021.84 | 52,531,021.84 | Yes |

### Expected Result After Fix

```
redemption_share_pressure:
  status=accepted
  strength=quantitative_direct
  measurement_kind=actual_exposure
  contract_status: partial (drawdown_stress still weak)
```

Score will emit `bond_risk_evidence_missing` only for `drawdown_stress`, not `redemption_share_pressure`.

---

## Required Test Coverage

The fix must add at least one test that replicates the real cell format:

1. **Real-shaped §2 profile ending-share cells**: cells contain `\n` line breaks and `份` suffix — must parse correctly.
2. **Cross-check pass**: §2 profile ending shares match §10 A/C/E/F ending shares.
3. **Cross-check mismatch**: §2 and §10 values differ → fail-closed with `share_class_ending_cross_check_mismatch`.
4. **No `份` suffix**: clean numeric cells still work (backward compatibility).
5. **Other unit suffixes**: `元`, `万元` etc. should also be handled or documented as out of scope.
6. **Missing `份` but with newline**: cells with newlines but no `份` should still parse if numeric.

---

## Non-Goals

- Do not modify score policy, quality gate semantics, FQ0-FQ6.
- Do not modify schema, snapshot projection, Service/UI/Host/Agent boundaries.
- Do not fix `drawdown_stress` — genuine data absence, correctly weak.
- Do not touch `credit_risk` — already accepted in the existing diff.
- Do not do golden-readiness, release, PR, push, merge, or promotion.
- Do not modify `docs/implementation-control.md` until accepted implementation passes full validation.
- Do not bypass `FundDocumentRepository` for annual report access.

---

## Validation Commands

After implementation:

```bash
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
uv run python -c 'import asyncio; from fund_agent.fund.documents import FundDocumentRepository; r = asyncio.get_event_loop().run_until_complete(FundDocumentRepository().load_annual_report("006597", 2024)); print(r.key.fund_code, r.key.year, len(r.sections), len(r.tables))'
uv run fund-analysis extraction-snapshot --run-id section2-cross-check-006597-2024-20260528 --fund-code 006597 --report-year 2024
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/section2-cross-check-006597-2024-20260528/snapshot.jsonl --errors-path reports/extraction-snapshots/section2-cross-check-006597-2024-20260528/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json
uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/section2-cross-check-006597-2024-20260528/score.json
```

Expected assertions:
- `redemption_share_pressure` in `satisfied_groups`, NOT in `ambiguous_groups`
- Score `missing_evidence_groups` contains only `drawdown_stress`
- Quality gate status `warn` (not `block` for bond risk — though other FQ2F issues may remain)

---

## Completion Statement

Root cause confirmed: `_parse_plain_decimal` does not strip the `份` Chinese unit suffix present in real §2 profile ending-share cells. Fix is a single-line addition to strip `份` before `Decimal()` parsing. The existing cross-check framework is structurally correct; only the value parsing is broken. No code was modified during this investigation.
