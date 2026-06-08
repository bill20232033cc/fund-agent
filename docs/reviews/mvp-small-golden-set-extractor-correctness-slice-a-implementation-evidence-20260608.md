# Small Golden Set / Extractor Correctness Slice A Implementation Evidence

## Scope

Gate: `small golden set extractor correctness implementation gate Slice A`.

Allowed implementation files:

- `docs/reviews/mvp-small-golden-set-manifest-20260608.json`
- `tests/fund/test_small_golden_set_manifest.py`

No source excerpts, extractor code, provider/default/runtime/budget/config, golden/readiness production artifacts or unrelated untracked files were modified for this slice.

## Changed Files

- `docs/reviews/mvp-small-golden-set-manifest-20260608.json`
- `tests/fund/test_small_golden_set_manifest.py`

## Implementation Summary

- Added review-owned manifest schema `fund-agent.small_golden_set_manifest.v1`.
- Manifest has exactly five rows: `004393`, `110020`, `004194`, `006597`, `017641`.
- All rows use `report_year=2024`.
- Global and row-level promotion remains disabled with `promotion_allowed_default=false` and `promotion_allowed=false`.
- Ordinary pytest network use remains disabled with `ordinary_pytest_network_allowed=false`.
- Fallback invocation remains prohibited with `fallback_invocation_allowed=false` and row-level `fallback_invocation=prohibited`.
- Source identity remains `pending_offline_fixture`; no row claims `matched` identity.
- No exact, normalized-text or numeric correctness assertion is accepted in Slice A.
- Added schema guard tests for exact row set, field group completeness, pending identity, fallback prohibition, promotion boundary, closed manifest key sets and absence of source excerpt/raw text fields.

## Validation

```bash
uv run pytest tests/fund/test_small_golden_set_manifest.py -q
```

Result:

```text
6 passed in 0.03s
```

```bash
git diff --check -- docs/reviews/mvp-small-golden-set-manifest-20260608.json tests/fund/test_small_golden_set_manifest.py
```

Result: passed with no output.

## Boundary Checks

- Live LLM: not run.
- Retry / endpoint / DNS / curl / socket / PASS-only probe: not run.
- Fallback invocation: not run.
- Provider/default/runtime/budget/config changes: none.
- Source excerpts / PDF / repository live access: none.
- Extractor code changes: none.
- Golden/readiness production artifact changes: none.
- `tests/README.md` sync: not required for Slice A because no fixture directory was added and the test command is already captured in gate evidence.

## Residuals

Slice A intentionally leaves source identity as `pending_offline_fixture`. Slice B must provide fixture-retention evidence and may only move a row to `matched` through retained real excerpt anchors or pre-existing offline repository metadata/public provenance. Synthetic fixtures cannot satisfy source identity or exact/numeric correctness.
