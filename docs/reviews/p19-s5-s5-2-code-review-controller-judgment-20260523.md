# P19-S5 S5-2 Code Review Controller Judgment — 2026-05-23

## Scope

- Phase: P19 thermometer independent development
- Gate: P19-S5 S5-2 Service, Cache Key, And Request Normalization implementation/code review
- Design truth: `docs/design.md` v2.2 §11
- Control truth: `docs/implementation-control.md`
- Implementation artifact: `docs/reviews/p19-s5-s5-2-service-cache-implementation-20260523.md`
- Code reviews: `docs/reviews/p19-s5-s5-2-code-review-ds-20260523.md`, `docs/reviews/p19-s5-s5-2-code-review-glm-20260523.md`
- Reviewed files:
  - `fund_agent/services/thermometer_service.py`
  - `fund_agent/fund/data/thermometer_cache.py`
  - `tests/services/test_thermometer_service.py`
  - `tests/fund/data/test_thermometer_cache.py`

## Controller Decision

Verdict: `ACCEPTED`

S5-2 is accepted. The implementation routes no-argument `ThermometerRequest()` to the self-owned all-A thermometer via explicit `wind_all_a`, keeps Service free of akshare imports and source field knowledge, shares the S5-1 Capability classifier across Service/cache/source support checks, and separates market cache paths from index cache paths. The review evidence shows all-A source failure degrades to stale cache when available, returns unavailable all-A output when no cache exists, and still propagates calculation-contract errors instead of converting them into silent fallback.

Based on `docs/design.md` §11 and first principles, this is the correct Service/cache slice: all-A becomes the default self-owned thermometer route without leaking Capability source fields upward, without touching CLI/docs ahead of S5-3, and without changing P19-S3 analyze integration semantics.

## Review Finding Judgment

### DS F1 — Unsupported Display Name Is The Raw Code

- Reviewer severity: low
- Controller status: accepted as non-blocking current behavior
- Decision: no fix required

For unsupported well-formed codes such as `999999`, returning the raw code as `index_name` is the least misleading behavior because no supported display name exists. This also keeps future support expansion centralized in `thermometer_display_name`. No S5-2 correctness or stability issue exists.

### DS F2 — Service Default Constructs `AkshareThermometerSource`

- Reviewer severity: low
- Controller status: accepted as non-blocking default-construction dependency
- Decision: no fix required

The Service still consumes the source through the `_IndexThermometerSource` protocol and does not import akshare or all-A field constants. A one-line default constructor dependency on the S5-1 composite source is acceptable for this gate and avoids introducing a factory abstraction without current payoff.

## Accepted Guarantees

- `ThermometerRequest()` with no `index_code` and no `index_codes` materializes `wind_all_a`.
- Exact `wind_all_a` and exact six ASCII digit codes are accepted; other non-six-digit tokens fail request validation.
- Unsupported well-formed six-digit codes remain item-level unavailable and cannot be served from forged cache files.
- `wind_all_a` cache path is under `market/`; `000300` and `000905` remain under `index/`.
- Service/cache support checks use the shared Capability classifier.
- Service does not import akshare and does not know `date`, `middlePETTM`, or `middlePB`.
- P19-S3 analyze regression remains intact; exact supported `000300` does not fall through to default all-A.
- S5-3 CLI/docs work remains intentionally untouched.

## Validation

Controller verified:

```text
pytest tests/services/test_thermometer_service.py tests/fund/data/test_thermometer_cache.py -q
33 passed

pytest tests/services/test_fund_analysis_service.py -q
20 passed

ruff check fund_agent/services/thermometer_service.py fund_agent/fund/data/thermometer_cache.py tests/services/test_thermometer_service.py tests/fund/data/test_thermometer_cache.py
All checks passed!

git diff --check
passed with no output
```

## Next Gate

Proceed to `P19-S5 S5-3 CLI Output And Docs Sync implementation`.

S5-3 must expose the new default all-A behavior through CLI output/help and synchronize README documents without claiming `fund-analysis analyze` uses all-A.
