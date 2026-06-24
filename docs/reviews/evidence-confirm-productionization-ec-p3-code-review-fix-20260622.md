# Evidence Confirm Productionization EC-P3 Code Review Fix

- Gate: code review fix
- Work unit: Evidence Confirm productionization / EC-P3 semantic entailment
- Slice: EC-P3-S1 Semantic Companion Contract
- Review artifact: `docs/reviews/code-review-20260622-172047.md`
- Artifact path: `docs/reviews/evidence-confirm-productionization-ec-p3-code-review-fix-20260622.md`

## Accepted Findings

### 001 not_applicable semantic judgment is incorrectly escalated to warn under anchor_precision warning

- Status: accepted
- Fix status: 已修复

## Fix Applied

- Updated `_severity_for_judgment()` so `judgment.status == "not_applicable"` returns `severity="info"` before applying the deterministic hard-gate warning rule.
- Added regression test `test_semantic_not_applicable_stays_info_under_anchor_precision_warn()`.

## Validation

```bash
uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_semantic.py -q
```

Result:

```text
59 passed
```

```bash
uv run ruff check fund_agent/fund/evidence_confirm_semantic.py tests/fund/test_evidence_confirm_semantic.py
```

Result:

```text
All checks passed!
```

```bash
git diff --check -- fund_agent/fund/evidence_confirm_semantic.py tests/fund/test_evidence_confirm_semantic.py fund_agent/fund/README.md tests/README.md
```

Result: pass.

## Residual Risks

- Same-run reference/result binding remains assigned to later Service/provider integration design if semantic output becomes product-visible.
- Provider-backed semantic quality remains assigned to later controlled semantic provider evidence gate.
- Service/renderer claim extraction and quality-gate consumption remain assigned to later integration gates.

No unclassified residual risk remains for the accepted code-review finding.
