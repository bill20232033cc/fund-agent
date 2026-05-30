# Bond Risk Evidence Extractor / Anchor Hardening — Aggregate Deepreview

> Date: 2026-05-28
> Worker: AgentMiMo
> Role: aggregate deepreview worker
> Work unit: `bond risk evidence extractor / anchor hardening`
> Branch: `codex/local-reconciliation` vs `main`
> Conclusion: **PASS_WITH_FINDINGS**

---

## Scope

Review the full `bond risk evidence extractor / anchor hardening` work unit on `codex/local-reconciliation` relative to `main`. Covers:

- Slice 1: Model contract (`extractors/models.py`)
- Slice 2: Extractor (`extractors/bond_risk_evidence.py`)
- Slice 3: Bundle integration (`data_extractor.py`)
- Slice 4: Snapshot projection (`extraction_snapshot.py`)
- Slice 5: Score applicability (`extraction_score.py`)
- Slice 6: Real `006597` / `2024` validation (blocked-with-reason)
- Tests across all slices

Required reading completed: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, plan artifact, plan controller judgment, slice 1-5 controller judgments, slice 6 real validation, slice 6 controller judgment.

---

## Gate Checklist

### FQ0-FQ6 Weakening

**PASS — no weakening detected.**

- `quality_gate.py` has no diff in this work unit. FQ0-FQ6 rules, thresholds, severities, and semantics are unchanged.
- Score applicability logic adds `bond_risk_evidence_missing` as a replacement issue, but `baseline_blocking=True` remains for any emitted issue.
- `derive_score_applicability_issues()` correctly gates on `classified_fund_type == "bond_fund"` and `holdings_snapshot` replacement applicability before emitting the bond risk issue.
- Non-bond funds are excluded from bond risk score logic entirely.
- `_record_is_covered()` only special-cases `holdings_snapshot` (top holdings status); `bond_risk_evidence` coverage follows standard `value_present` semantics, which is correct because `value_present` is derived from `contract_status != "missing"`.

### FundDocumentRepository Boundary

**PASS — boundary preserved.**

- `extract_bond_risk_evidence()` receives `ParsedAnnualReport` already loaded through `FundDocumentRepository` by `FundDataExtractor.extract()`.
- The extractor module (`bond_risk_evidence.py`) imports only from `fund_agent.fund.documents.models` and `fund_agent.fund.extractors.models`. It does not import `FundDocumentRepository`, PDF adapters, cache, or source helpers.
- `FundDataExtractor.extract()` continues to call `self._repository.load_annual_report()` exactly once. The bond risk extractor is invoked after existing extractors, consuming the same loaded report.
- No `extra_payload` usage detected. `classified_fund_type` is passed explicitly.

### Weak / Ambiguous Evidence Not Pseudo-Passed

**PASS — evidence-strength distinctions are preserved.**

- `drawdown_stress`: qualitative "控制回撤" text → `status="weak"`, `strength="qualitative_control_intent"`. Does NOT enter `satisfied_group_ids`. Correct.
- `credit_risk`: when rating distribution tables are missed by row keyword logic → falls back to text match → `status="weak"`, `strength="qualitative_direct"`. Does NOT satisfy the group. Correct.
- `leverage_liquidity`: flexible leverage strategy text alone → `status="weak"`. Repo table row + liquidity text → `status="accepted"`. Strength distinction preserved.
- `redemption_share_pressure`: ambiguous share class selection → `status="ambiguous"`, `strength="ambiguous"`. Does NOT satisfy the group. Correct.
- `convertible_bond_equity_exposure`: explicit `-` rows → `status="accepted_absence"`, `strength="quantitative_absence"`. Correct positive evidence of absence.

### Score Blocker Only Removed When Seven Groups Satisfied

**PASS — gating logic is correct.**

- `_bond_risk_unsatisfied_groups()` checks:
  1. Record existence and `value_present`
  2. `anchor_present`
  3. `contract_status` parseable and not `missing`
  4. Structured group fields parseable
  5. Known group IDs
  6. Union of `missing_groups ∪ weak_groups ∪ ambiguous_groups ∪ (required - satisfied)`
  7. Only returns `()` when `contract_status == "satisfied"` AND no unsatisfied groups
- This is a conservative multi-layer gate. Missing/malformed records default to all seven groups unsatisfied.
- `required_evidence_groups` in the emitted issue always equals all seven `BOND_RISK_EVIDENCE_GROUPS` ids (contract-level invariant). `missing_evidence_groups` is the dynamic unsatisfied subset. Correct.
- Non-bond funds skip bond risk issue emission entirely.

### Slice 6 Blocked Conclusion Sufficiency

**PASS — blocked conclusion is sufficient and well-evidenced.**

- Real `006597` / `2024` validation shows:
  - `bond_risk_evidence` row present with `contract_status=partial`
  - 4 groups satisfied: `duration_rate_risk`, `leverage_liquidity`, `asset_allocation_holdings_mix`, `convertible_bond_equity_exposure`
  - 0 missing, 2 weak (`credit_risk`, `drawdown_stress`), 1 ambiguous (`redemption_share_pressure`)
  - Score emits `bond_risk_evidence_missing` with `baseline_blocking=true` for 3 unsatisfied groups
- Controller correctly stops as blocked-with-reason. No false unblocking.
- Two independent workers (DS, GLM) confirmed root causes are consistent.

### Code Defects That Could Undermine Blocked Conclusion

**PASS — no defects that could cause false unblocking.**

The identified code issues are all false-negative direction (missing real evidence), which is the safe direction for a blocked conclusion:

1. **`credit_risk` row keyword precision**: `_first_row_anchor_draft()` uses `row_keywords=("信用", "评级")` to match data rows. Rating distribution tables typically have "信用评级分布" in headers and "AAA", "AA", "A" etc. in data rows. The `table_keywords` match the table, but `row_keywords` don't match any data row → table evidence is missed → falls back to text → weak. This is a false negative (misses real evidence), not a false positive. The blocker stays. **Safe direction.**

2. **`redemption_share_pressure` column disambiguation**: `_select_share_change_column()` tries fund_code in header → share class label in header → single column. When the share change table has multi-class columns without fund codes and `_share_class_evidence()` fails to extract §2 mapping (e.g., §2 text doesn't contain the expected "基金简称"/"交易代码" pattern), it returns `None` → ambiguous. This is a false negative. The blocker stays. **Safe direction.**

3. **`drawdown_stress` inherent limitation**: Annual report contains only qualitative "控制回撤" text. No max drawdown, volatility, or stress metric exists in the parsed report. The extractor correctly returns weak. Full blocker removal requires NAV-derived evidence, which is out of scope. **Correct behavior.**

No defects found that could cause false acceptance of weak/ambiguous evidence.

---

## Findings

### F1: `credit_risk` extractor misses rating distribution tables (extractor improvement)

**Severity**: medium — does not affect blocked conclusion reliability
**Direction**: false negative (safe)

The `_first_row_anchor_draft()` function requires `row_keywords` to match in data rows. For rating distribution tables (e.g., "短期债券信用评级分布", "长期债券信用评级分布"), the header contains "信用" and "评级" but data rows contain "AAA", "AA+", "AA", "A" etc. without those keywords. The extractor falls back to text match → weak.

**Fix direction**: Accept table-level rating distribution evidence when `table_keywords` match and the table has rating-category rows (AAA, AA, A, BBB etc.) or absence values. This is valid future extractor-hardening work.

### F2: `redemption_share_pressure` §2 share-class mapping incomplete (extractor improvement)

**Severity**: medium — does not affect blocked conclusion reliability
**Direction**: false negative (safe)

`_share_class_evidence()` tries two strategies:
1. `_share_class_evidence_from_profile_lines()`: looks for "基金简称" line followed by "交易代码" line with 6-digit codes
2. `_section_two_contains_class_mapping()`: proximity check (≤80 chars) between fund code and class label

For `006597` / 2024, the §2 text format may not match either pattern precisely, causing `_select_share_change_column()` to return `None` → ambiguous.

**Fix direction**: Harden §2 parsing to handle additional share-class mapping patterns (e.g., table-based subordinate fund listings). Valid future extractor-hardening work.

### F3: `drawdown_stress` cannot be satisfied from annual report alone (design residual)

**Severity**: low — correctly handled as residual
**Direction**: inherent limitation, not a defect

The annual report for `006597` / 2024 contains qualitative "控制回撤" text but no max drawdown, volatility, or stress metric. Under the current `bond_risk_evidence.v1` contract, `drawdown_control_intent` alone is `weak` and does not satisfy the group. This is the correct safe behavior.

**Residual owner**: future NAV-derived max drawdown / volatility evidence design gate.

### F4: Snapshot `extraction_mode` for bond_risk_evidence uses `estimated` for partial (minor)

**Severity**: info
**Direction**: cosmetic

The snapshot shows `extraction_mode=estimated` for partial `bond_risk_evidence`. The plan specified `partial` for "at least one group has usable evidence but one or more required groups remain missing/weak/ambiguous." The `_extraction_mode()` function maps contract status to extraction mode. Checking the code:

- `satisfied` → `direct`
- `partial` → `estimated` (plan says `partial` but `ExtractionMode` Literal only has `direct/derived/estimated/missing`)
- `missing` → `missing`

Since `ExtractionMode` doesn't have a `partial` value, `estimated` is a reasonable fallback. The snapshot exposes `bond_risk_contract_status=partial` as a structured field, so consumers can distinguish. No functional impact.

### F5: `_record_is_covered()` does not special-case `bond_risk_evidence` (non-issue)

**Severity**: info — confirmed non-issue after analysis

Initial concern: `bond_risk_evidence` with `contract_status=partial` would have `value_present=true`, counting as "covered" in FQ4 missing rate. After analysis: this is correct behavior. `value_present=true` means the field has been extracted and has some evidence. FQ4 measures field-level coverage, not contract-level satisfaction. The score applicability layer handles contract-level blocking separately through `bond_risk_evidence_missing`. No semantic conflict.

---

## Residual Risks

| Risk | Severity | Owner | Mitigation |
|---|---|---|---|
| `credit_risk` rating table extraction precision | medium | future extractor-hardening amendment | False negative only; blocker stays active |
| `redemption_share_pressure` §2 mapping completeness | medium | future extractor-hardening amendment | False negative only; blocker stays active |
| `drawdown_stress` quantitative evidence gap | high | future NAV-derived evidence design gate | Cannot be resolved within annual-report-only scope |
| Snapshot `extraction_mode=estimated` for partial bond evidence | info | accepted as-is | Structured `bond_risk_contract_status` field provides precise semantics |
| Real network/PDF smoke is source-dependent | low | unit tests deterministic | Smoke results are validation evidence, not fixture promotion |

---

## Verification Suggestions

1. **Extractor-hardening amendment for `credit_risk`**: Accept rating distribution tables at table-header level when `table_keywords` match and rows contain rating-category tokens (AAA, AA, A, BBB, etc.) or absence values. Verify with real `006597` / 2024 tables.

2. **Extractor-hardening amendment for `redemption_share_pressure`**: Harden §2 parsing to handle table-based subordinate fund listings (not just "基金简称"/"交易代码" line pairs). Verify share-class column selection with real `006597` / 2024 §10 table.

3. **NAV-derived `drawdown_stress` design gate**: Define a separate contract for NAV-derived max drawdown / volatility evidence, including source anchors and score applicability semantics. This is the only path to full blocker解除 without weakening the current contract.

4. **No golden corpus promotion**: Confirmed. No golden answer, baseline fixture, or release readiness work was performed in this gate.

---

## Validation Evidence

| Check | Result |
|---|---|
| `uv run ruff check .` | pass |
| `uv run pytest` | 834 passed; coverage 92.22% |
| `FundDocumentRepository` real smoke `006597`/`2024` | pass |
| `extraction-snapshot` | pass; positive `bond_risk_evidence` row present |
| `extraction-score` | pass; `bond_risk_evidence_missing` with 3 unsatisfied groups |
| `quality-gate` | pass; FQ2F bond issue remains |
| FQ0-FQ6 semantics changed | no |
| FundDocumentRepository boundary violated | no |
| Weak evidence pseudo-passed | no |
| Score blocker falsely removed | no |
| Golden corpus promoted | no |

---

## Conclusion

**PASS_WITH_FINDINGS**

The work unit correctly implements positive `bond_risk_evidence.v1` records with stable group-level anchors, preserves evidence-strength distinctions, maintains FQ0-FQ6 semantics, respects `FundDocumentRepository` boundaries, and correctly keeps the baseline blocker active because three groups remain unsatisfied. The Slice 6 blocked conclusion is reliable: no code defects were found that could cause false unblocking.

Five findings identified: two are extractor precision improvements (F1, F2) that are valid future work; one is an inherent design limitation requiring a separate gate (F3); two are non-issues confirmed after analysis (F4, F5). All findings are in the safe direction (false negatives, not false positives).
