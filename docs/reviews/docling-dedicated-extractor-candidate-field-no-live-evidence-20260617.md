# Docling Dedicated Extractor Candidate-field No-live Evidence - 2026-06-17

Gate: `Docling Dedicated Extractor Candidate-field No-live Evidence Gate`
Role: evidence worker
Accepted plan commit: `1d9350b`
Status: `EVIDENCE_COMPLETE_NOT_READY`
Verdict: `CANDIDATE_FIELD_EVIDENCE_NEGATIVE_NOT_READY`
Release/readiness: `NOT_READY`

## Evidence Artifacts

- Matrix: `reports/docling-dedicated-extractor-candidate-field-no-live-evidence/20260617/template_field_coverage_matrix.json`
- Plan: `docs/reviews/docling-dedicated-extractor-candidate-field-no-live-evidence-plan-20260617.md`
- Plan review: `docs/reviews/plan-review-20260617-171534.md`

## Scope

This evidence gate ran the accepted candidate-only Docling template-field extractor against accepted Docling candidate representation envelopes.

The gate did not:

- modify extractor rules;
- modify production extractor code;
- access PDF/cache/source helpers directly;
- run fresh Docling conversion;
- run live/network/provider/LLM/golden/readiness/release/PR commands;
- compare values with source truth;
- claim baseline qualification, parser replacement, source truth, field correctness, release readiness, or PR readiness.

## Runnable Inputs

| Sample | Fund | Year | Input |
|---|---:|---:|---|
| S1 | 004393 | 2025 | `reports/representation-json/004393_2025_docling_current_envelope.json` |
| S4 | 006597 | 2024 | `reports/representation-json/006597_2024_docling_full.json` |
| S5 | 017641 | 2024 | `reports/representation-json/017641_2024_docling_full.json` |
| S6 | 110020 | 2024 | `reports/representation-json/110020_2024_docling_full.json` |

## Blocked Inputs

| Sample | Fund | Year | Input | Reason |
|---|---:|---:|---|---|
| S1 | 004393 | 2025 | `reports/representation-json/004393_2025_docling_full.json` | `ValueError: unsupported candidate representation schema_version` |

The blocked S1 full JSON is excluded from the coverage denominator. This is a retained schema residual, not a compatibility authorization.

## Aggregate Result

| Metric | Value |
|---|---:|
| Runnable sample count | 4 |
| Blocked input count | 1 |
| Target field slots | 92 |
| Direct slots | 0 |
| Missing slots | 92 |
| Blocked slots | 0 |
| Candidate anchors | 0 |
| Direct coverage ratio | 0.0 |
| Missing ratio | 1.0 |

## Per-sample Result

| Sample | Fund | Year | Target fields | Direct | Missing | Blocked | Anchors |
|---|---:|---:|---:|---:|---:|---:|---:|
| S1 | 004393 | 2025 | 23 | 0 | 23 | 0 | 0 |
| S4 | 006597 | 2024 | 23 | 0 | 23 | 0 | 0 |
| S5 | 017641 | 2024 | 23 | 0 | 23 | 0 | 0 |
| S6 | 110020 | 2024 | 23 | 0 | 23 | 0 | 0 |

## Per-field Result

Every default target field path had `direct_count=0` and `missing_count=4`:

- `basic_identity.fund_name`
- `basic_identity.fund_code`
- `basic_identity.management_company`
- `basic_identity.custodian`
- `product_profile.investment_objective`
- `product_profile.investment_scope`
- `benchmark.benchmark_text`
- `risk_characteristic_text.risk_characteristic_text`
- `fee_schedule.management_fee`
- `fee_schedule.custody_fee`
- `nav_benchmark_performance.nav_growth_rate`
- `nav_benchmark_performance.benchmark_return_rate`
- `tracking_error.value_text`
- `portfolio_managers`
- `turnover_rate`
- `manager_alignment.manager_holding_range`
- `holdings_snapshot.top_holdings`
- `holdings_snapshot.bond_top_holdings`
- `holdings_snapshot.target_fund_holdings`
- `manager_strategy_text`
- `holder_structure`
- `share_change`
- `bond_risk_evidence`

## Interpretation

Accepted evidence facts:

- `project_candidate_representation()` can load the four selected current-schema Docling candidate envelopes.
- `extract_docling_template_fields()` can run against all four loaded documents without exception.
- The extractor emits exactly 23 candidate field records per sample.
- All emitted fields are `missing`.
- No candidate anchors are emitted.
- Candidate statuses remain `not_proven`.
- Production parser replacement status remains `not_authorized`.
- The old S1 full JSON remains blocked by schema version.

This is negative evidence for immediate integration planning.

It does not prove:

- source text lacks the target values;
- Docling cannot support the target fields;
- the candidate representation is unusable;
- the extractor implementation is generally wrong;
- baseline is impossible.

It does prove that the current accepted extractor rules do not match these accepted candidate envelope shapes strongly enough to produce candidate template fields.

## Validation

Command:

```text
uv run pytest tests/fund/documents/test_docling_template_field_extraction.py -q
```

Result:

```text
10 passed in 0.38s
```

No-live matrix generation command:

```text
uv run python -c '<load selected candidate JSON payloads; project_candidate_representation(payload); extract_docling_template_fields(document); write template_field_coverage_matrix.json>'
```

Result:

```text
{"anchor_count": 0, "blocked_input_count": 1, "blocked_slot_count": 0, "blocked_slot_ratio": 0.0, "direct_coverage_ratio": 0.0, "direct_slot_count": 0, "missing_ratio": 1.0, "missing_slot_count": 92, "runnable_sample_count": 4, "target_field_slot_count": 92}
```

## Residual Risks

Assigned to next diagnostic/remediation planning gate:

- Determine why real candidate envelopes yield zero direct field matches.
- Compare extractor expectations with actual projected table/text shapes.
- Identify whether the mismatch belongs to representation projection, section context, table family normalization, row/column label paths, or extractor label rules.
- Decide whether to add targeted diagnostics before modifying matching rules.

Assigned to later field contract stabilization gate:

- Field path schema;
- missing/block reason taxonomy;
- multi-row value representation;
- anchor shape guarantees.

Assigned to later comparative correctness gate:

- field value correctness against production truth or independent source truth.

Assigned to later integration planning gate:

- production projection to `ExtractedField` / `EvidenceAnchor`;
- quality-gate semantics;
- `FundDataExtractor` or report generation usage.

## Next Gate Recommendation

Do not enter integration planning yet.

Recommended next gate:

`Docling Dedicated Extractor Real-envelope Mismatch Diagnostic Planning Gate`

Purpose:

- inspect actual projected text/table field shapes for the 4 runnable samples;
- identify the smallest rule/projection mismatch that explains zero direct coverage;
- plan a narrow remediation slice without changing source-truth, parser-replacement, or production integration boundaries.

VERDICT: `CANDIDATE_FIELD_EVIDENCE_NEGATIVE_NOT_READY`
