# Evidence Confirm Scoring V2 Aggregate Fix Evidence

## Gate

- Gate: `Evidence Confirm Scoring V2 Targeted Fix Gate`
- Trigger artifact: `docs/reviews/code-review-20260622-094644.md`
- Accepted finding: `001-未修复-高-V2 对部分悬空 evidence_anchor_ids 误报 hard gate pass`
- Scope: fix only V2 no-live dangling-anchor fail-closed behavior; no V1 behavior change; no Service/UI/Host/renderer/quality-gate/readiness integration.

## Fix Summary

- `fund_agent/fund/evidence_confirm.py`
  - Added `_dangling_anchor_ids_for_fact()` to detect anchor ids declared by a fact but absent from the current chapter's `evidence_anchors`.
  - Passed `dangling_anchor_ids` into `_dimension_missing_evidence()`.
  - If any dangling id exists, `missing_evidence` now emits E3 blocking issues, returns `status="fail"` and `score=0`.
  - Existing valid proof references can still make `source_support` pass independently, but they no longer hide dangling anchor ids.
- `tests/fund/test_evidence_confirm.py`
  - Added `test_v2_dangling_anchor_fails_missing_evidence_even_with_valid_proof`.
  - Regression asserts `overall_status == "fail"`, fact score `0`, `missing_evidence.status == "fail"`, and `source_support.status == "pass"`.
- `tests/README.md`
  - Updated focused test count from `42 passed` to `43 passed`.
  - Added dangling-anchor coverage to the Evidence Confirm test description.

## Validation

```bash
uv run pytest tests/fund/test_evidence_confirm.py -q
```

Result:

```text
43 passed in 0.56s
```

```bash
uv run ruff check fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py
```

Result:

```text
All checks passed!
```

```bash
git diff --check
```

Result: clean.

## Boundary Check

- V1 public functions remain untouched.
- No document repository, PDF/cache/source helper, Service, UI, Host, renderer, quality gate, provider, LLM, live source, network, PR ready, merge or release path was added.
- Release/readiness remains `NOT_READY`.

## Conclusion

Targeted fix implemented locally. Ready for targeted re-review of accepted finding `001`.
