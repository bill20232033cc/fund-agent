# Evidence Confirm Productionization EC-P3 Aggregate Deepreview Fix

- Gate: aggregate deepreview fix
- Work unit: Evidence Confirm productionization / EC-P3 semantic entailment
- Date: 2026-06-22
- Source finding: `docs/reviews/code-review-20260622-172254.md` finding 001
- Artifact path: `docs/reviews/evidence-confirm-productionization-ec-p3-aggregate-deepreview-fix-20260622.md`

## Finding Disposition

| Finding | Decision | Status | Evidence |
|---|---|---|---|
| 001 missing_bounded_excerpt fail-closed branch is untested | accepted | fixed | Added `test_semantic_missing_bounded_excerpt_does_not_call_client()` in `tests/fund/test_evidence_confirm_semantic.py` |

## What Changed

- Added a regression test with a passing V2 deterministic result and a semantic claim whose anchor does not intersect deterministic `matched_anchor_ids`.
- Asserted `overall_status == "fail"`.
- Asserted the claim result is `status == "insufficient"`, `severity == "block"`, `reason_code == "missing_bounded_excerpt"` and `matched_anchor_ids == ()`.
- Asserted the semantic client was not called.

## Boundary Decision

- No production code changed in this fix.
- No Service, UI, Host, renderer, quality-gate, provider, repository, PDF/cache/source-helper or live path was touched.
- No release/readiness, mark-ready, merge or PR state change was performed.

## Re-Review Evidence

- AgentDS targeted re-review: `docs/reviews/code-review-rereview-ds-ec-p3-aggregate-20260622.md` -> `pass`
- AgentMiMo targeted re-review: `docs/reviews/code-review-rereview-mimo-ec-p3-aggregate-20260622.md` -> `pass`
- AgentCodex aggregate after-fix review: `docs/reviews/code-review-codex-ec-p3-aggregate-20260622.md` -> no substantive findings

## Validation

```bash
uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_semantic.py -q
```

Result:

```text
60 passed
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

| Risk | Classification | Owner / Destination |
|---|---|---|
| Same-run binding between V2 result and references uses anchor ids, not excerpt hashes or reference identities | assigned to later work unit | Service/UI/renderer/quality-gate integration gate |
| Provider-backed semantic quality is unproven | assigned to later work unit | Controlled semantic provider evidence gate |
| Service/renderer claim extraction is not implemented | assigned to later work unit | Service/UI/renderer integration gate |
| Quality-gate consumption is not implemented | assigned to later work unit | Quality-gate integration gate |
| Release/readiness remains unproven | assigned to later work unit | Release/readiness gate |

No unclassified residual risk remains for EC-P3 aggregate finding 001.

## Completion Status

Aggregate finding 001 is fixed and re-reviewed. EC-P3 is ready for aggregate deepreview controller judgment.
