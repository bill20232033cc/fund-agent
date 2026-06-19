# Code Review: return_attribution.v1 Source-truth Direct Extraction Slice 1

## Review Metadata

- Review gate: `Code Review Gate`
- Reviewer: AgentMiMo
- Artifact: `docs/reviews/code-review-20260620-064539-mimo-return-attribution-source-truth-slice1.md`
- Plan artifact: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-plan-20260620.md`
- Controller artifact: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-plan-controller-judgment-20260620.md`
- Implementation evidence: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice1-implementation-evidence-20260620.md`
- Review scope: Slice 1 admission/reuse guard only
- Verdict: `PASS_WITH_FINDINGS`

## Validation Reproduction

| Command | Result |
|---|---|
| `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py` | PASS: 125 passed in 0.86s |
| `uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py` | PASS: All checks passed |
| `git diff --check` | PASS: no whitespace errors |

Validation reproduced independently and matches implementation evidence claims.

## Findings

### Finding 1: Dead code on `return_attribution_evidence` initial assignment — LOW

**Location:** `fund_agent/fund/processors/fund_disclosure_processor.py` line 730 (in `_field_families_for_intermediate`)

**Evidence:**

```python
return_attribution_evidence = _select_return_attribution_candidate_evidence(intermediate)  # line 730
return_attribution_evidence = (                                                              # line 731
    () if return_attribution_source_truth is not None else return_attribution_evidence
)
```

Line 730 assigns `return_attribution_evidence`, then line 731 unconditionally reassigns it. When `return_attribution_source_truth is not None`, line 730's value is discarded entirely (dead code). When `return_attribution_source_truth is None`, line 731 re-reads the same value from line 730 (redundant round-trip).

The product_essence counterpart uses a single conditional expression:

```python
product_essence_evidence = (
    ()
    if product_essence_source_truth is not None
    else _select_product_essence_candidate_evidence(intermediate)
)
```

**Impact:** Functional correctness is preserved. The dead code does not alter runtime behavior or produce incorrect output. However, it creates a misleading signal that `_select_return_attribution_candidate_evidence()` is always called, which could confuse future readers about the candidate-evidence suppression contract.

**Severity:** LOW (code hygiene; no functional impact)

### Finding 2: No additional findings

- `_validate_source_truth_admission()` has zero lines changed in the diff — guard is not weakened.
- `_extract_return_attribution_source_truth()` correctly delegates to `_missing_field_family()` as a fail-closed skeleton.
- Field-family tuple construction correctly uses the direct result for `return_attribution.v1` and falls back to `_candidate_missing_field_family()` with original candidate evidence for all other families.
- Candidate evidence suppression (`()`) correctly applies only when `return_attribution_source_truth is not None` (proof-positive path).
- `_with_source_truth_admission_gap()` continues to apply to all families when `source_truth_gap_code` is non-None.
- No unauthorized value extraction, schema expansion, source policy changes, parser replacement, upper-layer consumption, or live/network commands.

## Test Review

| Test | Verdict | Notes |
|---|---|---|
| `test_return_attribution_source_truth_route_suppresses_candidate_evidence` | PASS | Correctly asserts proof-positive enters skeleton, candidate_evidence == (), field_family_missing gap. Verifies routing and suppression contract. |
| `test_return_attribution_source_truth_requires_proof_even_when_candidate_boundary_none` | PASS | Correctly asserts proof-missing path keeps candidate evidence and source_truth_admission_missing + candidate_only_not_source_truth gaps. |
| `test_return_attribution_source_truth_rejects_base_admission_invalid_paths` | PASS | Tests both source_provenance=None and failure_class="schema_drift"; asserts blocked status and empty field_families. |
| `test_return_attribution_source_truth_candidate_boundary_remains_blocked` | PASS | Correctly asserts candidate_boundary path stays blocked even with proof present. |

All four new tests assert the correct contract. Existing tests (121 remaining) all pass — no regression.

## Scope Boundary Verification

| Boundary | Status |
|---|---|
| Only Slice 1 admission/reuse guard | SATISFIED — no value extraction, anchor construction, or facade changes |
| `_validate_source_truth_admission()` not weakened | SATISFIED — zero lines changed in diff |
| Proof-positive enters fail-closed direct skeleton only | SATISFIED — `_missing_field_family()` returns `status="missing"`, `value={}`, `anchors=()` |
| Proof-positive suppresses `return_attribution.v1` candidate evidence | SATISFIED — `candidate_evidence=()` when direct result present |
| Proof-missing/proof-invalid/candidate-boundary/base admission unchanged | SATISFIED — existing candidate selector + gap behavior preserved |
| No unauthorized schema expansion, source policy, parser replacement, upper-layer consumption, or live commands | SATISFIED |
| Tests are meaningful and do not assert wrong contract | SATISFIED — all assertions match plan contract |

## Residual Risks

1. **Slice 1 skeleton is intentionally non-functional for public output.** `return_attribution.v1` remains `status="missing"`, `value={}` in Slice 1. This is by design — value extraction is deferred to Slice 2. Risk: zero, as long as no downstream consumer depends on proof-positive `return_attribution.v1` having non-empty values before Slice 2 is accepted.

2. **Dead code on line 730.** Low risk — does not affect correctness but should be cleaned up in a subsequent slice or fix pass to match the product_essence pattern.

## Required Fixes

None. Finding 1 is LOW severity and does not block the review gate. It can be addressed in a future slice or fix pass.

## Final Recommendation

- Verdict: `PASS_WITH_FINDINGS`
- Recommendation token: `CODE_REVIEW_PASS_NOT_READY`
