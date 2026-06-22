# EC-P3 PR Review Fix

## Gate

- Work unit: PR #40 EC-P3 semantic contract PR review fix.
- Branch: `evidence-confirm-productionization`.
- Accepted finding source: `docs/reviews/pr-40-review-codex-ec-p3-20260622.md` finding 001.
- Scope: fix only for incompatible semantic client `status` / `reason_code` pairs.

## Decision

- Finding 001 status: 已修复。
- The semantic client return boundary now accepts only explicit compatible pairs:
  - `entailed` -> `entailed_by_excerpt`
  - `contradicted` -> `contradicted_by_excerpt`
  - `insufficient` -> `insufficient_excerpt_support`
  - `not_applicable` -> `not_applicable`
- Internal fail-closed reason codes remain module-generated outcomes and are not accepted as successful client-returned pairs.
- Incompatible pairs now produce `malformed_client_result` with block severity, so aggregate status fails closed.

## Changed Files

- `fund_agent/fund/evidence_confirm_semantic.py`
- `tests/fund/test_evidence_confirm_semantic.py`
- `docs/reviews/evidence-confirm-productionization-ec-p3-pr-review-fix-20260622.md`

## Validation

- `uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_semantic.py -q`
  - Result: pass, `62 passed in 0.77s`.
- `uv run ruff check fund_agent/fund/evidence_confirm_semantic.py tests/fund/test_evidence_confirm_semantic.py`
  - Result: pass, `All checks passed!`.
- `git diff --check -- fund_agent/fund/evidence_confirm_semantic.py tests/fund/test_evidence_confirm_semantic.py docs/reviews/evidence-confirm-productionization-ec-p3-pr-review-fix-20260622.md`
  - Result: pass, no output.

## Residual Risks

- Provider-backed semantic quality remains unproven; assigned to later semantic provider evidence gate.
- Service/UI/Host/renderer/quality-gate integration remains outside this fix gate; assigned to later integration work.
- Same-run binding between V2 result and references remains anchor-id based; assigned to later Service/UI/renderer/quality-gate integration work.
- Release/readiness remains `NOT_READY`.

## Completion Status

- Implementation and regression tests completed.
- No V1/V2 deterministic schema, repository/source/PDF, Service/UI/Host/renderer/quality-gate, provider/live path, PR state, staging, commit, push, reviewer request, merge, or ready-state change was performed.
- Artifact path: `docs/reviews/evidence-confirm-productionization-ec-p3-pr-review-fix-20260622.md`.
