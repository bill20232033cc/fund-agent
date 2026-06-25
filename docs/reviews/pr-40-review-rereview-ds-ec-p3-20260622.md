# EC-P3 PR Review Fix Targeted Re-review

## Gate

- Mode: targeted re-review only, finding 001 fix verification.
- Branch: `evidence-confirm-productionization`.
- Accepted finding source: `docs/reviews/pr-40-review-codex-ec-p3-20260622.md` finding 001.
- Fix artifact: `docs/reviews/evidence-confirm-productionization-ec-p3-pr-review-fix-20260622.md`.
- Review timestamp: `2026-06-22`.

## Scope

- Only verify whether finding 001 is fully fixed.
- Confirm incompatible client status/reason pair now returns `malformed_client_result` fail-closed.
- Confirm valid client status/reason pairs remain accepted.
- No V1/V2 deterministic schema, repository/source/PDF, Service/UI/Host/renderer/quality-gate, provider/live path, PR state, mark-ready, merge, or readiness/release scope expansion.

## Finding 001 Verification

### Fix Implementation

The fix adds a compatibility table `_CLIENT_REASON_CODES_BY_STATUS` at `fund_agent/fund/evidence_confirm_semantic.py:45-50`:

| Status | Allowed reason_code |
|---|---|
| `entailed` | `entailed_by_excerpt` |
| `contradicted` | `contradicted_by_excerpt` |
| `insufficient` | `insufficient_excerpt_support` |
| `not_applicable` | `not_applicable` |

And an additional guard in `_judgment_is_valid()` at line 439:

```python
return judgment.reason_code in _CLIENT_REASON_CODES_BY_STATUS[judgment.status]
```

This guard runs after the existing type/literal-closed-set checks. Internal fail-closed reason codes (`deterministic_gate_failed`, `missing_claim`, `missing_bounded_excerpt`, `malformed_client_result`, `client_exception`) are not present in any status's allowed set, so they can never pass through client-result validation — they remain module-generated only.

### Incompatible Pair → Fail-Closed

Test `test_semantic_incompatible_client_status_reason_pair_fails_closed` (tests/fund/test_evidence_confirm_semantic.py:306-330) reproduces the exact scenario from finding 001:

- Input: deterministic V2 pass, bounded excerpt exists, client returns `EvidenceEntailmentJudgment(status="entailed", reason_code="contradicted_by_excerpt")`
- Assertions:
  - `overall_status == "fail"` (was previously `pass`)
  - `claim_results[0].status == "insufficient"`
  - `claim_results[0].severity == "block"`
  - `claim_results[0].reason_code == "malformed_client_result"`
  - client was called exactly once

### Valid Pairs Remain Accepted

Test `test_semantic_valid_client_status_reason_pairs_remain_accepted` (tests/fund/test_evidence_confirm_semantic.py:333-365) verifies all 4 compatible pairs survive the new validation without regression:

- `(entailed, entailed_by_excerpt)` → pass, info
- `(contradicted, contradicted_by_excerpt)` → fail, block
- `(insufficient, insufficient_excerpt_support)` → warn, warn
- `(not_applicable, not_applicable)` → not_applicable, info

### Existing Malformed Test Unchanged

Test `test_semantic_malformed_client_result_fails_closed` (line 284) still covers the non-dataclass `object()` return path.

## Validation Evidence (Reproduced)

```
$ uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_semantic.py -q
62 passed in 0.70s

$ uv run ruff check fund_agent/fund/evidence_confirm_semantic.py tests/fund/test_evidence_confirm_semantic.py
All checks passed!

$ git diff --check
(no output)
```

## Scope Boundary Check

- No changes to V1/V2 deterministic result schema or `evidence_confirm.py`.
- No changes to repository/source/PDF/docx helpers.
- No changes to Service/UI/Host/renderer/quality-gate code.
- No provider/live path, network, or filesystem calls introduced.
- No PR state mutation, staging, commit, push, reviewer request, merge, or ready-state change.
- The fix is confined to two files: `evidence_confirm_semantic.py` (compatibility table + one guard line) and `test_evidence_confirm_semantic.py` (two test functions).

## Residual Risks

- Same as the fix artifact: provider-backed semantic quality remains unproven; Service/UI/Host/renderer/quality-gate integration is outside this gate; same-run binding between V2 result and references remains anchor-id based.
- None of these are in scope for this targeted re-review.

## Conclusion

PASS. Finding 001 is fully fixed. The incompatible client status/reason pair `(entailed, contradicted_by_excerpt)` now correctly produces `malformed_client_result` with block severity, causing aggregate fail-closed. All 4 valid pairs remain accepted without regression. No scope boundary violations detected.
