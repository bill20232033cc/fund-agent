# Code Review: FundDisclosureDocument return_attribution.v1 Source-truth Slice 1

## Gate Metadata

- Gate: `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Implementation Gate`
- Review target: Slice 1 (Admission/reuse guard)
- Review role: AgentDS deep review
- Classification: `heavy`
- Plan artifact: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-plan-20260620.md`
- Controller judgment: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-plan-controller-judgment-20260620.md`
- Implementation evidence: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice1-implementation-evidence-20260620.md`
- Verdict: **PASS**

## Files Reviewed

- `fund_agent/fund/processors/fund_disclosure_processor.py` (diff + full context)
- `tests/fund/processors/test_fund_disclosure_processor.py` (diff + full context)
- `fund_agent/fund/processors/fund_disclosure_dispatch.py` (re-read for `admit_disclosure_intermediate`)

## Scope Adherence

| Constraint | Status |
|---|---|
| Only Slice 1 admission/reuse guard | ✅ PASS |
| `_validate_source_truth_admission()` unchanged | ✅ PASS |
| `return_attribution.v1` direct extractor is fail-closed skeleton | ✅ PASS |
| Proof-positive route suppresses `return_attribution.v1` candidate evidence | ✅ PASS |
| No value extraction for `return_attribution.v1` | ✅ PASS |
| No unauthorized field family extraction | ✅ PASS |
| No schema expansion (`EvidenceSourceKind`, `EvidenceAnchor`, `FundFieldFamilyResult`, etc.) | ✅ PASS |
| No source policy / repository changes | ✅ PASS |
| No parser replacement | ✅ PASS |
| No upper-layer consumption (Service/UI/Host/renderer/quality gate) | ✅ PASS |
| No readiness/release claim | ✅ PASS |
| No live/network commands | ✅ PASS |

## Findings

### F1 (INFO): `_extract_return_attribution_source_truth` correctly uses `_ = (intermediate, context)` to signal Slice-1 deferred usage

`fund_agent/fund/processors/fund_disclosure_processor.py:880`

The skeleton intentionally discards `intermediate` and `context` with `_ = (intermediate, context)` to silence unused-argument lint while preserving the full Slice 2 signature. This is consistent with the plan's explicit statement: "Slice 1 先 fail-closed 为 public missing".

No action required.

### F2 (INFO): Docstring for `_field_families_for_intermediate` properly updated

`fund_agent/fund/processors/fund_disclosure_processor.py:705-706`

The docstring was updated from the S6-B/S6-C/... notation to the current "proof-positive source-truth 路径可进入已授权 direct extractor" description. The update accurately describes the Slice 1 state.

No action required.

### F3 (INFO): Nested ternary in field_families construction is correct but worth noting for future slices

`fund_agent/fund/processors/fund_disclosure_processor.py:748-762`

The routing logic now has two nested ternary branches (`product_essence.v1` → `return_attribution.v1` → default). When Slice 2 adds more direct extraction (value construction), this pattern may warrant extraction into a dispatch dict. No change needed in Slice 1 — the logic is correct and scope is contained.

No action required.

### F4 (CONFIRMED): All existing S6-C candidate-only tests pass unchanged

`tests/fund/processors/test_fund_disclosure_processor.py:1603-1908`

The six existing `test_return_attribution_selector_*` tests all pass (confirmed via `uv run pytest`). The new routing logic does not interfere with proof-missing/invalid/candidate-boundary/no-match paths because `return_attribution_source_truth` is only non-None when `source_truth_extraction_allowed` is True, which requires a valid admission proof.

### F5 (CONFIRMED): 125/125 tests pass with no regressions

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
→ 125 passed in 0.64s
```

### F6 (CONFIRMED): Ruff lint passes

```text
uv run ruff check ...
→ All checks passed!
```

### F7 (CONFIRMED): No whitespace errors

```text
git diff --check
→ no output
```

## Contract Verification

### Proof-positive route → direct skeleton

`test_return_attribution_source_truth_route_suppresses_candidate_evidence` (`test_fund_disclosure_processor.py:1442`):

- Input: valid source_provenance + valid source_truth_admission proof + candidate_boundary=None + failure_class=None
- Output: `contract_status="missing"`, `family.status="missing"`, `family.extraction_mode="missing"`, `family.value={}`, `family.anchors=()`, `family.candidate_evidence=()`, gaps=`{"field_family_missing"}`
- ✅ Direct skeleton entered; candidate evidence suppressed

### Proof-missing route → candidate evidence preserved

`test_return_attribution_source_truth_requires_proof_even_when_candidate_boundary_none` (`test_fund_disclosure_processor.py:1485`):

- Input: valid provenance + candidate_boundary=None + `with_source_truth_proof=False`
- Output: `status="missing"`, candidate evidence preserved, gaps=`{"candidate_only_not_source_truth", "source_truth_admission_missing"}`
- ✅ Proof missing is correctly treated; candidate evidence not promoted

### Base admission invalid paths → blocked

`test_return_attribution_source_truth_rejects_base_admission_invalid_paths` (`test_fund_disclosure_processor.py:1536`):

- Input: `source_provenance=None` OR `failure_class="schema_drift"`
- Output: `contract_status="blocked"`, `field_families=()`, `anchors=()`
- ✅ Base admission correctly blocks both paths before `_field_families_for_intermediate()` runs

### Candidate boundary blocked

`test_return_attribution_source_truth_candidate_boundary_remains_blocked` (`test_fund_disclosure_processor.py:1585`):

- Input: `candidate_boundary=boundary` + valid proof
- Output: `contract_status="blocked"`, candidate evidence preserved, `status="missing"`, gaps=`{"candidate_only_not_source_truth"}`
- ✅ Candidate boundary not promoted to source truth even with proof present

## Adversarial Pass

### Can proof-positive route accidentally leak candidate evidence?

No. `return_attribution_evidence` is set to `()` when `return_attribution_source_truth is not None` (line 731), and `_extract_return_attribution_source_truth()` returns `_missing_field_family()` which has `candidate_evidence=()` by default (line 3608, no `candidate_evidence` kwarg passed).

### Can a proof-missing `return_attribution.v1` lose candidate evidence that `product_essence.v1` retains?

No. Each family's candidate evidence is independently selected. `return_attribution_evidence` is only suppressed when `return_attribution_source_truth is not None`. The `product_essence_evidence` suppression logic is independent (line 724-728).

### Can the new code make `source_truth_gap_code=None` when proof is actually missing?

No. `source_truth_gap_code` is set by `_validate_source_truth_admission()` at line 579, and the function was not modified. The `source_truth_extraction_allowed` flag (line 586) requires both `admission.contract_status != "blocked"` AND `source_truth_gap_code is None`.

### Can the nested ternary accidentally route `return_attribution.v1` to `product_essence.v1`'s direct result?

No. The first branch checks `family_id == "product_essence.v1"` which fails for other family IDs. The second branch checks `family_id == "return_attribution.v1"` explicitly. Other family IDs fall through to the default `_candidate_missing_field_family` / `_missing_field_family` path.

## Residual Risks

1. **Slice 2 complexity**: When `_extract_return_attribution_source_truth()` gains value extraction logic in Slice 2, the nested ternary in `_field_families_for_intermediate()` may need refactoring. This is a future concern, not a Slice 1 defect.
2. **Test coverage for interaction between families**: The current tests verify each family independently. No test verifies that when both `product_essence.v1` AND `return_attribution.v1` are source-truth direct, both families are correctly emitted in the same result. This is acceptable for Slice 1 since `_extract_return_attribution_source_truth()` is a fail-closed skeleton (always missing), so the interaction is trivial. Slice 2 should add an integration assertion.
3. **`_FAMILY_ORDER` unchanged**: The family ordering tuple at line 40 remains as-is. No regression risk.

## Validation Reviewed

| Command | Evidence Claim | Reproduced |
|---|---|---|
| `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py` | 125 passed | ✅ 125 passed in 0.64s |
| `uv run ruff check ...` | All checks passed | ✅ Passed |
| `git diff --check` | no output | ✅ Confirmed |

## Required Fixes

None.

## Final Recommendation

**`CODE_REVIEW_PASS_NOT_READY`**

Slice 1 implementation is correct, fully scoped, and passes all adversarial checks. The admission/reuse guard correctly routes proof-positive `return_attribution.v1` into a fail-closed direct skeleton, suppresses candidate evidence for direct families, and preserves all existing behavior for proof-missing, proof-invalid, candidate-boundary, and base-admission-failure paths. `_validate_source_truth_admission()` was not weakened. No unauthorized extraction, schema expansion, or upper-layer consumption is present. Ready for Slice 2 value extraction.
