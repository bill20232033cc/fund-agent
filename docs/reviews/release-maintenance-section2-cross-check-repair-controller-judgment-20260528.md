# Section2 Profile Ending-Share Cross-Check Repair Gate — Controller Judgment

> Date: 2026-05-28
> Controller: MiMo
> Gate: `section2 profile ending-share cross-check repair gate`
> Gate classification: `standard`
> Verdict: **root cause identified, authorized for implementation**

## Preflight

- `git branch --show-current`: `codex/local-reconciliation`
- `git status --short`: dirty implementation diff in `bond_risk_evidence.py` and `test_bond_risk_evidence.py` from previous column-alignment gate (uncommitted, not accepted)
- Previous gate: `redemption share class column alignment repair gate` → `blocked-with-root-cause`
- No accepted implementation commit, no deepreview, no implementation-control update from previous gate

## Dirty Scope Classification

### Reusable Baseline

Current dirty diff contains:

- `credit_risk` holding-rating distribution path: accepted in prior validation
- `drawdown_stress` boundary: qualitative, weak, unchanged
- §2 A/C/E/F mapping dataclass and helpers
- §10 table selection, row matching, Decimal parsing, arithmetic checks
- §2 profile cross-check helpers (`_share_class_ending_cross_check_from_profile_tables`, `_profile_cross_check_rows`, `_profile_ending_values_by_class`, `_validate_share_class_ending_cross_check`)
- Unlabeled positional alignment path
- All existing unit tests (56 passing)

### Failure Evidence

Previous gate validation showed:

- `redemption_share_pressure.status=ambiguous`
- `na_reason=share_class_ending_cross_check_missing`
- Root cause: `_profile_ending_values_by_class()` fails to parse real §2 ending-share cell values

### Unrelated / Out of Scope

- `--help` untracked file
- Unrelated comprehensive/repo review artifacts
- `docs/tmux-agent-memory-store.md`

## Root Cause Analysis

### Real §2 Profile Table Structure (006597 / 2024, page 5 table 0)

```
row[9]:  ('下属分级基金的基金简称', '国泰利享中\n短债债券A', '国泰利享中\n短债债券C', '国泰利享中\n短债债券E', '国泰利享中\n短债债券F')
row[10]: ('下属分级基金的交易代码', '006597', '006598', '014217', '022176')
row[11]: ('报告期末下属分级基金的份\n额总额', '5,711,224,267\n.09份', '4,760,029,01\n5.27份', '25,795,859.1\n2份', '52,531,021.8\n4份')
```

### What Works

- Row label matching (`_profile_cross_check_rows`): `_compact_text` strips `\n`, so `"报告期末下属分级基金的份\n额总额"` → `"报告期末下属分级基金的份额总额"` → contains `"报告期末下属分级基金的份额总额"` → **matches**
- Class label extraction (`_share_class_labels_from_profile_name_cells`): `"国泰利享中\n短债债券A"` → compact → `"国泰利享中短债债券A"` → regex extracts `A` → **correct**
- Fund code extraction: `"006597"` → `re.fullmatch(r"\d{6}", ...)` → **correct**
- Table exclusion: `(5, 0) != (65, 0)` → **correct, not self-certifying**

### What Fails

`_profile_ending_values_by_class` calls `_parse_share_decimal(cell)` on each ending value cell.

For real cell `"5,711,224,267\n.09份"`:

1. `_compact_text(...)` → `"5,711,224,267.09份"` (strips `\n`, keeps `份`)
2. `.replace(",", "")` → `"5711224267.09份"`
3. `Decimal("5711224267.09份")` → `InvalidOperation` → returns `None`

All 4 ending cells return `None` → `_profile_ending_values_by_class` returns `None` → cross-check returns `None` → `_aggregate_share_change` returns `share_class_ending_cross_check_missing`.

### Why Tests Didn't Catch It

Test fixtures use clean numeric values without the `份` unit:

```python
"5,711,224,267.09"  # test fixture — no 份
"5,711,224,267\n.09份"  # real data — has 份
```

The test `_real_profile_cross_check_table` default `ending_row` parameter omits the `份` suffix that appears in real parsed data.

## Fix Design

### Scope

- `fund_agent/fund/extractors/bond_risk_evidence.py` — fix `_parse_plain_decimal` to strip `份` unit
- `tests/fund/extractors/test_bond_risk_evidence.py` — add test with `份` unit in ending values

### Fix: Strip `份` Unit in `_parse_plain_decimal`

In `_parse_plain_decimal`, after removing commas and before Decimal conversion, strip trailing `份` (and optionally other common Chinese unit suffixes like `元`, `万`):

```python
# After comma removal, before Decimal:
normalized = normalized.rstrip("份元万")
```

This is minimal, safe, and matches the real parsed data shape. The `份` suffix is a share-count unit that appears in Chinese fund annual reports.

### Test: Real-Shape §2 Ending With `份` Unit

Add a test that uses the real §2 profile table shape with `份` suffix in ending values, verifying the cross-check passes and `redemption_share_pressure` is accepted.

### No Schema/Score/Gate Changes

The fix only changes Decimal parsing behavior. No schema, score policy, quality gate, or public contract changes.

## Expected Outcome

After fix:

- `_parse_share_decimal("5,711,224,267\n.09份")` → `Decimal("5711224267.09")` ✓
- `_profile_ending_values_by_class` returns valid `ending_by_class` dict
- Cross-check passes: §10 computed endings == §2 profile endings within tolerance
- `redemption_share_pressure.status` = `accepted`
- `bond_risk_satisfied_groups` includes `redemption_share_pressure`
- `bond_risk_ambiguous_groups` no longer includes `redemption_share_pressure`
- `drawdown_stress` remains weak (not in scope)
- `quality_gate` remains `warn` (drawdown residual)

## Constraints Preserved

- No weakening of FQ0-FQ6
- No score policy changes to hide extractor failure
- No accepting unlabeled §10 columns without §2 cross-check
- No A-only acceptance path
- No `drawdown_stress`, NAV, QDII, FOF, 110020, golden, release, Host/Agent/dayu changes
- Production annual report access remains through `FundDocumentRepository`

## Implementation Authorization

Implementation may proceed under this judgment. Implementation worker must stop and return if:

- `份` stripping breaks other Decimal parsing paths
- Real validation fails for any reason
- Any change requires schema, score, snapshot, quality gate, or boundary work
