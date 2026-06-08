# MVP Small Golden Set / Extractor Correctness Slice C Option 1 Implementation Evidence

## Scope

Role: implementation/evidence worker only.

Gate: `small golden set extractor correctness implementation gate` Slice C Option 1 source identity acquisition mini-slice.

This slice is evidence/guard work only. It does not restart the workflow, does not modify extractors or production code, does not change provider/default/runtime/budget/config, does not access repository/PDF/network/provider/fallback, does not change golden/readiness/quality gate promotion semantics, and does not implement extractor correctness.

## Changed Files

- `docs/reviews/mvp-small-golden-set-extractor-correctness-source-identity-evidence-20260608.md`
- `docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-option1-implementation-evidence-20260608.md`
- `tests/fund/test_small_golden_set_source_identity.py`

No fixture `expected_fields.json` was modified because no row had sufficient accepted/pre-existing offline provenance to prove matched source identity.

## Implementation Summary

- Reviewed current control truth, Slice C reconciliation plan, Slice A/B artifacts, current fixture metadata, and accepted historical row-specific evidence candidates.
- Recorded row-level Option 1 decisions in the source identity evidence artifact.
- Added deterministic source-identity guard tests:
  - exact five-row coverage remains `004393`, `110020`, `004194`, `006597`, `017641` for `2024`;
  - any future `matched` row must include source document title/id, fund code, report year, share class, annual-report source kind, evidence anchor and accepted provenance origin;
  - current unmatched synthetic rows remain non-correctness fixtures;
  - fallback and promotion remain prohibited.

## Row Decision Summary

| fund_code | report_year | decision | reason |
|---|---:|---|---|
| `004393` | 2024 | unmatched | Accepted 004393 evidence explicitly records source provenance limitation and cannot prove source identity or `fallback_used=false`. |
| `110020` | 2024 | unmatched | Accepted evidence uses historical fallback tuple and lacks source document title/id or source-safe identifier for a matched fixture identity. |
| `004194` | 2024 | unmatched | Accepted evidence proves only five narrow `index_profile.*` benchmark-context score matches; no complete source document identity is accepted. |
| `006597` | 2024 | unmatched | Accepted score/run evidence does not establish matched annual-report document identity for fixture use. |
| `017641` | 2024 | unmatched | Accepted evidence records complete eligible fallback tuple and data-gap state, not no-fallback matched fixture identity. |

Option 1 found no matched identity.

## Boundary Evidence

- Live LLM: not run.
- Retry / endpoint / DNS / curl / socket / PASS-only probe: not run.
- Repository/PDF/network/provider/akshare/EID access: not run.
- `FundDocumentRepository` live access: not run.
- Source fallback invocation: not run.
- Provider/default/runtime/budget/config changes: none.
- Extractor or production code changes: none.
- Golden/readiness/quality gate promotion semantic changes: none.
- Fixture promotion / `promotion_allowed=true`: none.
- Exact/numeric correctness claims: none.

## Validation

```bash
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py -q
```

Result:

```text
...............                                                          [100%]
15 passed in 0.03s
```

```bash
uv run ruff check tests/fund/test_small_golden_set_source_identity.py
```

Result:

```text
All checks passed!
```

```bash
git diff --check -- docs/reviews/mvp-small-golden-set-extractor-correctness-source-identity-evidence-20260608.md docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-option1-implementation-evidence-20260608.md tests/fund/test_small_golden_set_source_identity.py tests/fixtures/fund/small_golden_set tests/README.md
```

Result: passed with no output.
