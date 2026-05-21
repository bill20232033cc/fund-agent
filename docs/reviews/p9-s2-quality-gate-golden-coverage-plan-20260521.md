# P9-S2 Quality Gate / Golden Coverage Calibration Plan

- **Date**: 2026-05-21
- **Slice**: P9-S2 quality gate / golden coverage product-path calibration
- **Baseline commits**: `e8be00f` / `7cde828` / `2bacdb3`
- **Design source**: `docs/design.md`
- **Control source**: `docs/implementation-control.md`
- **Prior decision**: `docs/reviews/post-p9-s1-follow-up-planning-20260521.md`
- **Scope**: planning only; do not modify implementation in this slice.

## 1. Current Facts

P9-S1 changed the normal `fund-analysis analyze` path into product mode:

- Product mode fixes `quality_gate_policy="block"`.
- `warn/off` and fixture-style analysis parameters require `--dev-override`.
- Product mode default `quality_gate_source_csv` is `docs/code_20260519.csv`.
- Product mode default strict golden path is `reports/golden-answers/golden-answer.json`; if this default file is absent, Service resolves it to `None` and correctness becomes unavailable instead of `not_run`.

Current selected-pool and golden coverage:

- `docs/code_20260519.csv`: 56 rows, 55 unique fund codes, duplicate `016492`.
- CSV categories: 国内股票类 26, 国内债券类 14, 海外股票类 11, 海外债券/稳健类 3, 黄金类 1, 货币基金类 1.
- `reports/golden-answers/golden-answer.json`: 6 funds, all present in the CSV.
- Covered codes: `004393`, `000216`, `007721`, `007360`, `006597`, `001548`.
- CSV unique codes without strict golden coverage: 49.

Current quality gate semantics:

- `gate not-run`: `quality_gate_for_bundle` cannot run because selected-pool CSV is unavailable, malformed, blocking-invalid, or the fund is not a member.
- `correctness unavailable`: score/gate ran, but strict golden answer comparison is absent or has no comparable coverage.
- `correctness mismatch`: strict golden answer exists and snapshot comparable value conflicts; current rule is `FQ1/block`.

## 2. First-Principles Decision

Strict golden coverage is a correctness oracle, not the membership contract and not the only quality signal. Product mode must fail closed when the gate cannot run or detects quality failure, but it should not collapse "no human golden label exists yet" into "quality gate not-run".

Therefore:

- Missing strict golden coverage for a selected-pool fund is `FQ0/info`, not `block`, while extraction coverage, traceability, fund-quality, source failure accounting, App-category conflicts, template applicability, and explicit correctness mismatches remain blocking or warning as already defined.
- Strict golden coverage becomes `block` only when a policy explicitly requires correctness coverage for a given fund/category and that fund/category is declared in-scope for strict coverage. P9-S2 should not expose this as a normal product-mode user option.
- Product mode must keep `block` policy and must not expose `warn/off`.

This preserves the P9-S1 safety boundary: users cannot bypass gate failure, but product usability is not limited to the 6 current human-labeled funds.

## 3. State Model To Implement

Introduce explicit state names in score/gate outputs and messages:

| State | Meaning | Product block? |
|---|---|---:|
| `gate_not_run` | CSV missing, CSV schema invalid, blocking CSV validation error, or fund not in selected pool | yes |
| `selected_pool_member` | Fund is present in the product quality source CSV | no by itself |
| `selected_pool_non_member` | Fund is absent from product source CSV | yes as `gate_not_run` |
| `correctness_not_configured` | No strict golden answer path was available | no, `FQ0/info` |
| `correctness_fund_not_covered` | Golden file exists but has no records for this fund | no, `FQ0/info` |
| `correctness_no_comparable_fields` | Golden file exists and current fund has records, but none of that fund's records is comparable in the current snapshot contract | no, `FQ0/info` |
| `correctness_field_not_comparable` | Golden has records, but an individual subfield is outside snapshot comparable support | no by itself; contributes to unavailable count and may explain `correctness_no_comparable_fields` |
| `correctness_missing_comparable_value` | Golden covers a comparable subfield and snapshot explicitly says the value is missing | diagnostic sub-case of mismatch; still `FQ1/block` |
| `correctness_mismatch` | Comparable expected and actual values conflict | yes, `FQ1/block` |

Do not use `not_run` for golden coverage absence. `gate_not_run` must mean pre-gate execution failure only: selected-pool CSV missing, CSV schema/validation failure, or membership failure before score/gate execution. It must not include gate-internal sub-rules that ran but produced `FQ0/info`, such as missing `fund_quality`, missing strict golden coverage, or non-comparable correctness fields.

`correctness_missing_comparable_value` is not a new non-blocking state. It is a diagnostic label for the existing mismatch path where the golden record is comparable and expected to exist, but snapshot explicitly marks the value as missing. The behavior remains `FQ1/block`.

## 3.1 Mapping To Existing CorrectnessSummary

`coverage_scope` is a new field in the `correctness` section. It augments the existing `CorrectnessSummary.status`; it does not replace `status`. The existing `status` remains the coarse execution status: `available / unavailable`. The new `coverage_scope` explains whether the correctness oracle actually covered the current run's fund(s).

| Proposed state | Existing / new score fields | `status` | `coverage_scope` | `reason` requirement | `record_results` expectation |
|---|---|---|---|---|---|
| `correctness_not_configured` | `golden_answer_path=None`; default golden path missing resolved to `None` | `unavailable` | `not_configured` | `not_configured` | empty |
| `correctness_fund_not_covered` | golden file exists; target fund code absent from golden fund list | `available` | `fund_not_covered` | `fund_not_covered` with target `fund_code` | may contain records for other funds in multi-fund score, but none for target fund |
| `correctness_no_comparable_fields` | golden file exists; target fund has records; target fund `comparable_records=0` | `available` | `no_comparable_fields` | `no_comparable_fields` with target `fund_code` | target-fund records exist but all are `unavailable` because no comparable field/subfield is exposed |
| `correctness_field_not_comparable` | a target-fund golden record is outside `COMPARABLE_SUB_FIELDS_BY_FIELD` | `available` | `partially_covered` or contributes to `no_comparable_fields` | `field_not_comparable` on FQ0 issue when it explains missing coverage | record has `status=unavailable` |
| `correctness_missing_comparable_value` | target-fund comparable record has no actual value because snapshot explicitly marked it missing | `available` | `covered` or `partially_covered` | mismatch reason must say the comparable value is explicitly missing | record has `status=mismatch` |
| `correctness_mismatch` | target-fund comparable expected/actual conflict | `available` | `covered` or `partially_covered` | mismatch reason must explain normalized conflict | record has `status=mismatch` |
| covered with matches | target-fund comparable records exist and match | `available` | `covered` or `partially_covered` | matched summary | record has `status=match` |

Single-fund `analyze` should derive target-fund coverage in this order:

1. If `golden_answer_path is None`, use `coverage_scope=not_configured`.
2. If a non-default explicit golden path is missing, malformed, schema-invalid, or semantically invalid, fail closed with `FileNotFoundError`, `GoldenAnswerValidationError`, `json.JSONDecodeError`, or a structured equivalent; do not degrade it to `not_configured`.
3. If the default golden path exists but is malformed or invalid, also fail closed or raise a structured exception; only default path absence is `not_configured`.
4. If the golden file is valid but the target fund is absent, use `coverage_scope=fund_not_covered`.
5. If the target fund exists but `comparable_records=0`, use `coverage_scope=no_comparable_fields`.
6. If the target fund has comparable records and some unavailable records, use `coverage_scope=partially_covered`.
7. If all target-fund golden records that should be compared are comparable, use `coverage_scope=covered`.

For multi-fund `extraction-score`, the same fields may include `covered_fund_codes` and `missing_fund_codes`; aggregate `status=available` must not hide per-fund missing coverage.

## 4. Default Source Decision

Keep `docs/code_20260519.csv` as product mode default membership source.

Do not switch product mode to the curated 6-fund covered subset. That would make 49 selected funds fail as `gate_not_run`, which is false: they are selected-pool members with missing correctness labels. A curated covered subset should exist only as a golden maintenance/reporting artifact, not as the product quality source.

Implementation should add a derived coverage view, for example in score JSON:

- `correctness.coverage_scope`: `not_configured / fund_not_covered / no_comparable_fields / partially_covered / covered`
- `correctness.covered_fund_codes`
- `correctness.missing_fund_codes` for the current run
- `correctness.coverage_required`: `false` for product default
- `correctness.coverage_reason`: `not_configured / fund_not_covered / no_comparable_fields / partially_covered / covered`

For single-fund `analyze`, this can be computed from the run's one fund and the strict golden file.

P9-S2 must not implement a `correctness_required` policy mechanism. The field `coverage_required=false` is only a diagnostic/default-policy fact in this slice, not a new configurable enforcement system.

## 5. User Error Messages

CLI stderr must distinguish three user-visible cases:

1. Gate not run:
   - `quality_gate_status: not_run`
   - `quality_gate_not_run_reason: fund_code \`xxxxxx\` not found in quality gate source csv`
   - Message should say the fund is outside the currently supported product quality pool, not that golden coverage is missing.

2. Gate block:
   - `quality_gate_status: block`
   - `quality_gate_issues: N`
   - `quality_gate_json: ...`
   - `quality_gate_md: ...`
   - Existing report suppression remains correct.

3. Gate pass/warn with missing strict golden coverage:
   - Keep report output.
   - stderr still prints `quality_gate_status`.
   - stderr should print one short informational line when a fund-scoped `FQ0/info` correctness coverage issue exists, for example `quality_gate_info: strict golden answer not covered for fund_code xxxxxx`.
   - `quality_gate.md/json` should contain the full `FQ0/info` metadata explaining that strict correctness golden coverage is absent for this fund.
   - The stderr info line is not a failure, must not change exit code, and must not be phrased as a warning or block.

Recommended FQ0 message:

`基金 \`xxxxxx\` 在精选池中，但 strict golden answer 尚未覆盖；本次 quality gate 已执行 coverage/traceability/fund_quality 检查，未执行 correctness oracle。`

## 5.1 FQ0/Info Metadata Contract

Every correctness coverage `FQ0/info` issue must be machine-diagnostic, not just prose. Required metadata:

- `rule_code="FQ0"`
- `severity="info"`
- `fund_code`: target fund code when the issue is fund-scoped; for multi-fund aggregate coverage gaps, either emit one issue per affected fund or include `missing_fund_codes` in metadata while preserving traceability to each fund.
- `reason`: one of `not_configured`, `fund_not_covered`, `no_comparable_fields`, `field_not_comparable`.
- `golden_answer_path`: present when a golden file was configured and valid.
- `coverage_scope`: matching the derived coverage scope.
- `comparable_records`, `unavailable_records`, and `total_records` where applicable.

Reason semantics:

- `not_configured`: only allowed when no strict golden path is available because the default path is absent or no path was configured.
- `fund_not_covered`: golden file is valid, but target fund has no golden fund entry.
- `no_comparable_fields`: golden file is valid and target fund has records, but target-fund comparable denominator is zero.
- `field_not_comparable`: at least one target-fund golden row exists but its `field_name.sub_field` is outside current comparable support; use this as detailed metadata, or roll up to `no_comparable_fields` when all rows are non-comparable.

Invalid existing golden files are not `FQ0/info`. Empty, malformed, wrong schema version, duplicate, missing required fields, or otherwise invalid strict golden files must fail closed or raise a structured exception. This prevents a broken oracle from being silently treated as absent coverage.

## 6. File-Level Implementation Plan

Capability layer:

- `fund_agent/fund/extraction_score.py`
  - Extend `CorrectnessSummary` with coverage scope fields.
  - In `compare_snapshot_correctness(...)`, distinguish no golden file, golden file present but no fund record, fund record present but no comparable record, and explicit mismatch.
  - Preserve `CorrectnessSummary.status` as coarse `available / unavailable`; add `coverage_scope` and reason fields for coverage calibration.
  - Treat valid golden file + current fund records + `comparable_records=0` as `no_comparable_fields`, not generic aggregate pass.
  - Keep malformed or invalid existing golden files fail-closed; only absent default path can become `not_configured`.
  - Keep mismatch behavior unchanged.
  - Do not guess expected values or broaden `COMPARABLE_SUB_FIELDS_BY_FIELD` without evidence-backed labels.

- `fund_agent/fund/quality_gate.py`
  - Convert missing/partial correctness coverage into fund-scoped `FQ0/info`.
  - Require `FQ0/info` issue metadata to include `reason`, `fund_code`, `coverage_scope`, and count fields.
  - Emit `FQ0/info` for `not_configured`, `fund_not_covered`, and `no_comparable_fields`; preserve `field_not_comparable` as detailed reason metadata when useful.
  - Keep explicit mismatch as `FQ1/block`.
  - Keep unknown malformed correctness schema fail-closed via `ValueError`.
  - Keep `FQ2/FQ2F/FQ3/FQ4/FQ5/FQ6` behavior unchanged.

- `fund_agent/fund/quality_gate_integration.py`
  - Preserve membership short-circuit semantics.
  - Ensure single-fund score/gate output carries enough selected-pool membership and correctness coverage metadata for user diagnostics.

Service/UI:

- `fund_agent/services/fund_analysis_service.py`
  - Keep product defaults: `block`, `docs/code_20260519.csv`, default golden path.
  - Keep default missing golden file as correctness unavailable, not gate not-run.
  - Do not add product-mode knobs for `warn/off` or strict coverage override.

- `fund_agent/ui/cli.py`
  - Improve top-level stderr only for `not_run` wording if needed.
  - Print one concise `quality_gate_info: ...` stderr line for fund-scoped correctness coverage `FQ0/info`.
  - Do not print FQ0/info as a product failure, warning, or block.

Docs/tests:

- `README.md`
  - Clarify that product default source is selected-pool membership, while strict golden coverage is currently partial.
- `fund_agent/fund/README.md`
  - Document the distinction between gate execution, selected-pool membership, and correctness coverage.
- `tests/README.md`
  - Add maintenance rule: tests must not conflate golden coverage absence with `not_run`.

## 7. Test Matrix

Add or update focused tests only; no real network/PDF path is required.

| Layer | Case | Expected |
|---|---|---|
| extraction score | no golden path | `correctness.status=unavailable`, scope `not_configured`, no mismatch |
| extraction score | default golden path missing | scope `not_configured`; no exception |
| extraction score | explicit golden path missing | fail closed with `FileNotFoundError`; not `not_configured` |
| extraction score | golden file exists but malformed/invalid | fail closed with JSON/schema validation error; not `not_configured` |
| extraction score | golden file exists but current fund absent | `status=available`, scope `fund_not_covered`, no mismatch |
| extraction score | golden fund present and comparable fields match | scope `covered` or `partially_covered`, matched count > 0 |
| extraction score | golden fund present but all fields unavailable / target `comparable_records=0` | scope `no_comparable_fields`; this must be distinguishable from aggregate pass |
| extraction score | comparable explicit missing value | mismatch diagnostic sub-case; record status `mismatch` |
| quality gate | correctness unavailable only | `FQ0/info` present with `reason=not_configured`, aggregate status stays `pass` absent other issues |
| quality gate | correctness fund not covered only | fund-scoped `FQ0/info` present with `reason=fund_not_covered`, aggregate status stays `pass` absent other issues |
| quality gate | golden fund present but no comparable fields | fund-scoped `FQ0/info` present with `reason=no_comparable_fields`, aggregate status stays `pass` absent other issues |
| quality gate | correctness mismatch | `FQ1/block` |
| quality gate integration | selected-pool member without golden coverage | gate runs; not `not_run`; FQ0/info recorded with `fund_code`, `reason`, and `coverage_scope` |
| quality gate integration | fund not in CSV | `not_run_reason` returned before score/gate |
| Service product | selected member without golden coverage and good P0/P1 | report allowed, gate result pass/warn with FQ0/info metadata |
| Service product | fund not in CSV | `QualityGateNotRunBlockedError` before expensive extraction |
| Service product | explicit mismatch | `QualityGateBlockedError` |
| CLI | not-run | stderr says `quality_gate_status: not_run` and reason |
| CLI | block | stderr says block status and artifact paths |
| CLI | pass with missing coverage | stdout report is emitted; stderr includes `quality_gate_info: ...` plus normal gate status/artifacts |
| CLI/API guard | `--quality-gate-policy warn/off` without `--dev-override` | still rejected |

## 8. Acceptance Criteria

P9-S2 implementation can be accepted only if:

- Product mode still uses `block` and still rejects dev-only quality options without `--dev-override`.
- A selected-pool member with no strict golden answer is not reported as gate not-run.
- Missing strict golden coverage is visible as `FQ0/info` with fund-scoped metadata including `fund_code`, `reason`, and `coverage_scope`.
- Valid golden file plus current fund records but target-fund `comparable_records=0` triggers `FQ0/info` with `reason=no_comparable_fields`.
- Explicit correctness mismatch remains `FQ1/block`.
- Comparable value explicitly missing remains a mismatch diagnostic sub-case and still blocks as `FQ1`.
- Malformed or invalid existing golden files fail closed; only absent default golden path is `not_configured`.
- Non-member or invalid selected-pool source still blocks as gate not-run.
- CLI emits a concise informational stderr line for fund-scoped correctness coverage `FQ0/info` without changing exit status.
- `docs/code_20260519.csv` remains the default product membership source.
- The 6 currently covered golden funds remain human-labeled facts; no expected values are guessed.

## 9. Non-Goals

- Do not weaken `--dev-override` isolation.
- Do not expose `warn/off` to product users.
- Do not bypass product quality gate.
- Do not switch product default source to the 6-fund covered subset.
- Do not implement a `correctness_required` policy mechanism in P9-S2.
- Do not infer or generate missing golden expected values.
- Do not broaden correctness field coverage without evidence-backed golden labels and explicit comparable-value support.
- Do not include repo hygiene, CI, license, or `.gitignore` cleanup in this slice.

## 10. Residual Risks

- Product quality for the 49 non-covered selected funds will rely on extraction coverage, traceability, fund-quality checks, and template applicability rather than strict correctness oracle.
- `docs/code_20260519.csv` still has duplicate `016492`; current validation treats duplicate codes as non-blocking. This remains human-owned unless a later slice changes CSV governance.
- Current correctness denominator is intentionally conservative; expanding it requires new comparable fields and human-reviewed golden labels, not automatic prefill values.
