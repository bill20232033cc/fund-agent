# RR-09 Product Provenance Tier Contract PR Review Fix

## Gate

- Work unit: RR-09 Product Provenance Tier Contract
- Gate: PR Review Fix Gate
- PR: `https://github.com/bill20232033cc/fund-agent/pull/41`
- Accepted finding: `PR41-CI-001`

## Verdict

`RR_09_PRODUCT_PROVENANCE_TIER_CONTRACT_PR_REVIEW_FIX_READY_FOR_REREVIEW_NOT_READY`

## Fix

Updated `tests/fund/integration/test_p3_cli_e2e_matrix.py` so `_EXPECTED_APPENDIX_EVIDENCE_FRAGMENTS` asserts the current appendix locator format:

```text
source_field_path=<field>; locator=<locator>
```

The fix keeps the test on the same product path and validates the current provenance-rich CLI output rather than the pre-RR-09 legacy `行fund_name` / `行benchmark` style fragments.

## Docs

Updated `tests/README.md` to state that P3 CLI end-to-end appendix evidence assertions use the current `source_field_path=...; locator=...` source locator format.

## Validation

```text
uv run pytest tests/fund/integration/test_p3_cli_e2e_matrix.py::test_p3_cli_outputs_complete_reports_for_three_sample_funds tests/fund/integration/test_p3_cli_e2e_matrix.py::test_p19_s6_cli_auto_valuation_uses_exact_index_thermometer -q
```

Result: `2 passed`

```text
uv run pytest tests/fund/integration/test_p3_cli_e2e_matrix.py -q
```

Result: `2 passed`

```text
uv run ruff check tests/fund/integration/test_p3_cli_e2e_matrix.py
```

Result: `All checks passed!`

```text
git diff --check -- tests/fund/integration/test_p3_cli_e2e_matrix.py
```

Result: passed.

## Residual Risk

- PR #41 CI still shows failure for the old remote head until this fix checkpoint is pushed.
- No live/PDF, repository/source-helper/parser, product CLI or provider/LLM command was run.
- No mark-ready, reviewer request, merge, tag, release or readiness action was performed.

Artifact path: `docs/reviews/evidence-confirm-productionization-rr-09-product-provenance-tier-contract-pr-review-fix-20260624.md`
