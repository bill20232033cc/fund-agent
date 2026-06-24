# Evidence Confirm Scoring V2 Implementation Evidence - 2026-06-22

## Gate

- Work unit: `Evidence Confirm Scoring V2 / Dayu-style Dimension Scoring`
- Current gate: `Evidence Confirm Scoring V2 Implementation Gate`
- Branch: `evidence-confirm-anchor-audit-score`
- Accepted plan commit: `f36437f`
- Classification: `heavy scoring-contract implementation`
- Verdict target: `IMPLEMENTATION_COMPLETE_VALIDATED_NOT_READY`
- Release/readiness: `NOT_READY`

## Changed Files

| File | Lines added | Nature |
|---|---|---|
| `fund_agent/fund/evidence_confirm.py` | +1038 | V2 schema, type aliases, dataclasses, five-dimension scoring, hard gate, score cap, public V2 functions |
| `tests/fund/test_evidence_confirm.py` | +371 | 19 new V2 tests covering all required assertions |

## Public API Added

### Constants

- `EVIDENCE_CONFIRM_V2_SCHEMA_VERSION = "evidence_confirm.v2"`

### Type Aliases

- `EvidenceConfirmGateStatus = Literal["pass", "warn", "fail", "not_applicable"]`
- `EvidenceConfirmDimension = Literal["anchor_precision", "source_support", "missing_evidence", "proof_boundary", "value_match"]`
- `EvidenceConfirmDimensionStatus = Literal["pass", "warn", "fail", "not_applicable"]`
- `EvidenceConfirmGateSeverity = Literal["blocking", "reviewable", "informational"]`
- `EvidenceConfirmNextGateRecommendation = Literal["evidence_anchor", "source_truth_proof", "value_matching", "manual_review", "not_applicable"]`

### Dataclasses

- `EvidenceConfirmDimensionResult` — single dimension scoring result
- `EvidenceConfirmHardGate` — hard gate with status, issue categorization, dimension counts
- `EvidenceConfirmFactResultV2` — V2 fact result with hard gate + five dimensions
- `EvidenceConfirmResultV2` — V2 aggregate result with hard gate + fact results

### Public Functions

- `confirm_chapter_evidence_v2(chapter, references) -> EvidenceConfirmResultV2`
- `confirm_projection_evidence_v2(projection, references) -> EvidenceConfirmResultV2`

## V1 Compatibility Statement

Existing V1 public functions `confirm_chapter_evidence()` and `confirm_projection_evidence()` are unchanged. Their return types, scores, and status semantics are preserved. Existing V1 tests (21 tests) continue to pass unchanged. V2 functions coexist with V1 using independent result types.

## Validation Outputs

### Test suite

```
$ uv run pytest tests/fund/test_evidence_confirm.py -q
40 passed in 0.89s
```

### Dependent test suites

```
$ uv run pytest tests/fund/test_chapter_auditor.py tests/fund/test_evidence_availability.py -q
60 passed in 0.54s
```

### Lint

```
$ uv run ruff check fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py
All checks passed!
```

### Whitespace

```
$ git diff --check -- fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py
(no output — clean)
```

## Required Test Assertion Coverage

| Assertion | Test function | Status |
|---|---|---|
| V2 result uses `evidence_confirm.v2` | `test_v2_result_uses_v2_schema_version` | PASS |
| V2 fact result includes all five dimensions in deterministic order | `test_v2_fact_result_includes_five_dimensions_in_order` | PASS |
| Blocking E3 produces hard gate fail | `test_v2_blocking_e3_produces_hard_gate_fail` | PASS |
| E1-only imprecision produces hard gate warn | `test_v2_e1_only_imprecision_produces_hard_gate_warn` | PASS |
| All applicable pass produces hard gate pass | `test_v2_all_applicable_pass_produces_hard_gate_pass` | PASS |
| Derived/not-applicable-only input produces hard gate not_applicable | `test_v2_derived_not_applicable_produces_hard_gate_not_applicable` | PASS |
| Candidate-only reference fails proof_boundary and source_support | `test_v2_candidate_only_reference_fails_proof_boundary_and_source_support` | PASS |
| Not-proven reference fails proof_boundary | `test_v2_not_proven_reference_fails_proof_boundary` | PASS |
| Invalid kind/source kind pair fails proof_boundary | `test_v2_invalid_kind_source_kind_pair_fails_proof_boundary` | PASS |
| Wrong document year fails proof_boundary | `test_v2_wrong_document_year_fails_proof_boundary` | PASS |
| Mixed references fail proof_boundary even when valid proof exists | `test_v2_mixed_references_fail_proof_boundary_even_with_valid_proof` | PASS |
| Proven same-anchor value mismatch fails value_match while source_support passes | `test_v2_value_mismatch_fails_value_match_while_source_support_passes` | PASS |
| Unrelated anchor excerpt cannot pass value_match | `test_v2_unrelated_anchor_excerpt_cannot_pass_value_match` | PASS |
| Projection aggregation deterministic and averages only numeric fact scores | `test_v2_projection_aggregation_deterministic_averages_numeric_scores` | PASS |
| Value mismatch hard-gate fail produces fact auditability_score <= 40 | `test_v2_value_mismatch_hard_gate_fail_score_cap` | PASS |
| Candidate-only proof failure produces fact auditability_score = 0 | `test_v2_candidate_only_proof_failure_score_zero` | PASS |
| Aggregate score with one blocking fact cannot report pass-like score >= 70 | `test_v2_aggregate_score_one_blocking_fact_cannot_report_pass_like_score` | PASS |
| Aggregate score with all passing facts uses uncapped average | `test_v2_aggregate_score_all_passing_uses_uncapped_average` | PASS |

## Boundary Confirmation

- No repository/PDF/cache/source helper/Service/UI/Host/provider/network/dayu reads.
- No `EvidenceSourceKind`, `EvidenceAnchor`, `StructuredFundDataBundle` changes.
- No parser, extractor, processor, quality gate, renderer, or CLI changes.
- No `docs/design.md`, `docs/implementation-control.md`, startup packet, README, or other docs/reviews artifact edits.
- No git index, commit, push, PR, or remote state changes.
- V1 public behavior preserved; V2 coexists independently.

## Residual Risks

| Risk | Owner | Next gate |
|---|---|---|
| V2 remains no-live and caller-supplied-reference only | Later live source/PDF Evidence Confirm gate | Separate reviewed gate |
| Semantic entailment beyond conservative material-token matching unimplemented | Later semantic Evidence Confirm gate | Separate reviewed gate |
| Report-quality bridge from V2 dimensions to `ReportScoreIssueLink` remains future work | Later report workflow adoption gate | Separate reviewed gate |
| Quality gate impact remains out of scope | Later FQ gate integration gate if authorized | Separate reviewed gate |
| Dayu upstream scoring details not locally re-read; only hard gate + dimension score idea used | Implementation controller if finer Dayu parity needed | Future gate |

## Verdict

IMPLEMENTATION_COMPLETE_VALIDATED_NOT_READY
