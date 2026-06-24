# Evidence Confirm Productionization RR-09 R5a Quality-gate Static Evidence

Verdict token:

`RR_09_R5A_STATIC_EVIDENCE_MANAGER_STRATEGY_P0_BLOCK_NOT_READY`

## Scope

Gate: `RR-09 R5a - 017641 / 2024 Quality-gate Block Static / No-live Evidence Gate`.

This artifact investigates only R5a from the accepted RR-09 residual plan:

- `017641 / 2024` product `analyze` exits 2 with `quality_gate_status=block`.
- The question is whether this can be accepted as expected QDII product behavior, a quality-gate defect, or a narrower field/extraction residual.

No live/PDF/provider/LLM command, repository load, source/cache/parser read, code change, PR mutation, tag, release, checklist support, report-body rendering, provider-backed semantic default-on, or release/readiness promotion was performed.

## Direct Evidence

### RR-S2 product CLI output

Accepted RR-S2 evidence records:

- Product CLI `017641 / 2024` exited `2`.
- CLI emitted `quality_gate_status: block`.
- CLI linked the generated quality gate artifact:
  - `reports/quality-gate-runs/analyze-017641-2024-20260623T052502739090Z/quality_gate.json`
  - `reports/quality-gate-runs/analyze-017641-2024-20260623T052502739090Z/score.json`

The RR-S2 repository runner separately passed for the same sample with EID `single_source_only`, fallback disabled/unused, and no repository failure. Therefore R5a is a product quality-gate residual, not a source/PDF pathway failure.

### Quality-gate issue facts

The generated `quality_gate.json` shows `status=block`.

Blocking issues are:

| Rule | Severity | Field / fund | Meaning |
|---|---|---|---|
| `FQ2` | `block` | `manager_strategy_text` | P0 coverage/traceability failed. |
| `FQ3` | `block` | `manager_strategy_text` | P0 evidence anchor traceability failed. |
| `FQ2F` | `block` | `017641` | Single-fund P0 failure; failed field is `manager_strategy_text`. |

Non-blocking or informational issues:

| Rule | Severity | Meaning |
|---|---|---|
| `FQ2` | `warn` | P1 `holdings_snapshot` failed. |
| `FQ2F` | `warn` | Single-fund P1 failed field is `holdings_snapshot`. |
| `FQ0` | `info` | Strict golden answer does not cover `017641`; correctness oracle not run for this fund. |
| `FQ4` | `warn` | Missing field rate is `0.26666666666666666`, above warn threshold `0.2` but below block threshold `0.35`. |
| `ECQ1` | `warn` | Evidence Confirm pathway diagnostic `repository_failure:unsupported_row_locator_format`; warn severity only. |

### Score payload facts

The generated `score.json` records:

- `fund_scores[0].fund_code = "017641"`.
- `fund_scores[0].p0_status = "fail"`.
- `fund_scores[0].p0_failed_fields = ["manager_strategy_text"]`.
- `fund_scores[0].p1_status = "fail"`.
- `fund_scores[0].p1_failed_fields = ["holdings_snapshot"]`.
- `fund_quality[0].classified_fund_type = "qdii_fund"`.
- `fund_quality[0].app_category_status = "match"`.
- `fund_quality[0].preferred_lens_status = "resolved"`.
- `fund_quality[0].preferred_lens_key = "qdii_fund"`.
- `fund_quality[0].missing_field_rate = 0.26666666666666666`.
- `score_applicability_issues = []`.
- `failed_funds = []`.
- `field_applicability_decisions` excludes `turnover_rate` as `turnover_rate_pre_effective_report_year`; this is not the blocking issue.

### Static code facts

`fund_agent/fund/quality_gate.py`:

- `_aggregate_gate_status()` returns `block` if any issue severity is `block`.
- `_evaluate_field_score()` emits `FQ2/block` and `FQ3/block` for P0 coverage/traceability failures.
- `_evaluate_fund_score()` emits `FQ2F/block` when a single fund has P0 failures.
- `_evaluate_fund_quality()` emits `FQ4/block` only when `missing_field_rate >= 0.35`; `017641` has `0.26666666666666666`, so FQ4 is only warn.
- `_evaluate_fund_quality()` emits `FQ5/block` only for `preferred_lens_status=mismatch`; `017641` has `resolved`, so FQ5 is not a blocker.
- `_evaluate_failed_fund()` emits `FQ6/block`; `017641` has no `failed_funds` row.

`fund_agent/fund/extraction_score.py`:

- `APP_CATEGORY_ALLOWED_FUND_TYPES["海外股票类"]` includes only `qdii_fund`.
- `SUPPORTED_CONTRACT_FUND_TYPES` includes all current `FundType` values, including `qdii_fund`.
- `_derive_contract_applicability()` resolves standard supported fund types through CHAPTER_CONTRACT preferred_lens and ITEM_RULE evaluation.
- The only current field-specific replacement issue path is exact `bond_fund` holdings replacement into `bond_risk_evidence`; no equivalent QDII replacement path exists for `manager_strategy_text`.

## Interpretation

R5a is now narrowed:

- It is not a source/PDF access failure.
- It is not a QDII preferred_lens applicability failure.
- It is not a missing-field-rate block.
- It is not a complete extraction failure.
- It is not caused by `failed_funds`.
- It is not caused by a QDII-specific quality-gate rule.

The direct cause of the product quality-gate block is the generic P0 requirement that `manager_strategy_text` must have sufficient coverage and traceability. The blocked sample is QDII, but the blocker is field-level P0 coverage/traceability, not QDII category incompatibility.

Therefore Branch D from the accepted RR-09 plan cannot be accepted as written. The evidence does not prove that the `017641 / 2024` block is an expected QDII product limitation.

Branch E is also not currently justified as a narrow quality-gate bug fix. The quality gate is applying its current generic P0 semantics consistently. Changing the outcome would require a separate product/field applicability decision about whether `manager_strategy_text` should remain P0/blocking for QDII, or a narrower extraction/anchor fix that makes the P0 field pass.

## Validation

```bash
uv run pytest tests/fund/test_quality_gate.py tests/fund/test_extraction_score.py -q --tb=short
```

Result: `90 passed`.

Static evidence commands:

```bash
rg -n "017641|manager_strategy_text|FQ2|FQ3|FQ2F|FQ4|ECQ1|preferred_lens_status|qdii_fund|failed_funds|score_applicability_issues|quality_gate_status" \
  reports/quality-gate-runs/analyze-017641-2024-20260623T052502739090Z/quality_gate.json \
  reports/quality-gate-runs/analyze-017641-2024-20260623T052502739090Z/score.json \
  reports/live-evidence/evidence-confirm-release-readiness-rr-s2-20260623/cli-product-017641-2024/stderr.txt
```

Result: matched the issue and score facts summarized above.

```bash
rg -n "test_derive_fund_quality_records_resolves_all_standard_fund_types|test_run_quality_gate_warns_and_blocks_fq4_missing_rate_thresholds|test_run_quality_gate_blocks_failed_funds_as_fq6|test_run_quality_gate_synthetic_006597_like_bond_exclusion_does_not_mis_pass|test_run_quality_gate_preserves_fq4_thresholds_with_score_applicability_issue" \
  tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
```

Result: current tests cover standard fund type preferred_lens resolution, FQ4 thresholds, failed-fund FQ6 blocking, and bond-specific applicability replacement semantics.

## Residual Disposition

| Residual | Disposition |
|---|---|
| R5a `017641 / 2024` quality-gate block | Narrowed to `manager_strategy_text` P0 coverage/traceability block. Not accepted as expected QDII limitation. |
| Whether `manager_strategy_text` should be P0/blocking for QDII | Requires separate product/field applicability decision or field extraction/anchor evidence gate. |
| Whether extraction can satisfy QDII `manager_strategy_text` | Requires narrower extraction/anchor work unit or authorized diagnostic evidence. |
| R5b blocked-path EC summary propagation | Already accepted separately by Branch F selected-slice checkpoint. |
| R1-R4 product CLI EC `fail` under `warn` | Still require fact-level diagnostic evidence; not addressed by this artifact. |
| Release/readiness | Remains `NOT_READY`. |

## Result

R5a static/no-live evidence is complete. It narrows the blocker to `manager_strategy_text` P0 coverage/traceability and rejects a zero-code Branch D acceptance as currently unproven.

Completion token: `RR_09_R5A_STATIC_EVIDENCE_MANAGER_STRATEGY_P0_BLOCK_NOT_READY`
