# P19-S2 Code Review GLM（2026-05-23）

## Verdict

`BLOCKED`

当前 HEAD `8ddad68` 的 P19-S2 主路径实现基本符合范围约束：没有接入 `fund-analysis analyze`，没有实现全 A / PB-only 全 A，没有改变 no-index public-page adapter 行为，也没有引入 Dayu、parquet 或 `extra_payload`。但 unsupported well-formed index 的数据态契约存在一个 cache-bypass support-check 缺陷：fresh cache 命中时会绕过 source 支持性校验，使 unsupported code 可能返回 available reading。这直接违反本轮 review 要求中“unsupported well-formed code 是 per-item unavailable”的契约。

## Scope Reviewed

- `fund_agent/fund/data/thermometer_source.py`
- `fund_agent/fund/data/thermometer_types.py`
- `fund_agent/fund/data/thermometer_cache.py`
- `fund_agent/fund/analysis/thermometer_calculator.py`
- `fund_agent/services/thermometer_service.py`
- `fund_agent/ui/cli.py`
- `tests/fund/data/test_thermometer_source.py`
- `tests/services/test_thermometer_service.py`
- `tests/ui/test_cli.py`
- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`

## Findings

### Blocking - Unsupported well-formed index can become available when a fresh cache file exists

Evidence:

- `fund_agent/services/thermometer_service.py:215-223` loads and returns fresh cache before calling `self._index_source.load_index_history(index_code)`.
- `fund_agent/fund/data/thermometer_source.py:78-80` is the only current support check for `SUPPORTED_INDEX_SYMBOLS`; it is only reached when the source is called.
- `fund_agent/fund/data/thermometer_cache.py:69-79` loads `cache/thermometer/index/<index_code>_history.json` and returns the payload without validating that the requested code is currently supported by the source contract.
- `tests/services/test_thermometer_service.py:264-300` covers unsupported `999999` only with no usable cache. It does not cover unsupported code with a pre-existing fresh cache.

What can go wrong:

1. A request such as `fund-analysis thermometer --index 000300,999999` is well-formed.
2. If `cache/thermometer/index/999999_history.json` exists and is fresh, `_load_index_reading()` returns `calculate_thermometer_reading(cached.history, cached=True, stale=False)` before the source has a chance to reject `999999`.
3. The batch result can contain an available reading for a code that P19-S2 says is unsupported, instead of per-item `unavailable=True`.

Why this is blocking:

The P19-S2 contract distinguishes malformed input from well-formed unsupported code. Unsupported code must be a coherent item-level unavailable state, not a cache-authorized success. The support truth currently lives in `AkshareIndexThermometerSource`, but Service places cache lookup before that truth. This creates two support authorities: source for cache misses, cache path existence for cache hits.

Suggested fix:

Move current-support validation ahead of fresh cache reuse without pushing the allowlist into UI. A small Capability-owned predicate/protocol such as `supports_index(index_code)` would let Service reject unsupported codes as item unavailable before reading cache. Also add tests for:

- Service batch `("000300", "999999")` with a fresh `999999_history.json` still returns `999999` as unavailable.
- CLI `--index 000300,999999 --cache-dir <dir> --json` exits 0 and reports the unsupported item unavailable even when that cache file exists.

## Non-Blocking Observations

- `000905 -> 中证500` mapping is implemented in `SUPPORTED_INDEX_SYMBOLS` and `INDEX_NAMES`; source tests parameterize both `000300` and `000905` and assert injected fetchers receive the expected symbol.
- PE/PB schema/date fail-closed behavior did not regress for tested cases. Strict date strings are validated with full `YYYY-MM-DD` matching, and tests cover timestamp strings, trailing content, and leading/trailing whitespace.
- `ThermometerBatchResult` is compact and stable enough for P19-S2: Decimal values remain inside per-reading dataclasses and are converted to strings in CLI JSON; unavailable readings use `None` for numeric fields; batch metadata includes requested codes, count flags, generated time, source, and disclaimer.
- Service owns normalization for mutual exclusion, empty sequence, empty segment, six-digit shape, preserve-order de-duplication, and legacy/single/batch routing. The blocking issue is not normalization; it is support validation being bypassed by cache.
- CLI only parses `--index`, constructs `ThermometerRequest`, and renders Service results. I did not find direct akshare, cache, calculator, or supported-index allowlist calls in UI.
- No range expansion found: no `fund-analysis analyze` integration, no all-A implementation, no PB-only all-A, no public-page fallback for indexed self-owned results, no Dayu/parquet/`extra_payload`.

## Residual Risks

- Batch execution is sequential. With live akshare, first refresh of `000300,000905` may be slow; current JSON cache mitigates normal use, but this remains an operational latency risk rather than a correctness blocker.
- Cache payloads restore stored dates without re-running the strict source date validator. Existing corrupted-cache handling drops invalid JSON/schema broadly, but semantically odd yet parseable payloads remain a cache-trust residual.
- Tests use fake Service for some CLI batch cases, so they prove rendering/exit-code behavior but not all real Service/cache/source combinations. The blocking finding above is one concrete gap.
- Live akshare availability and column drift are not covered by default tests; fixture tests correctly avoid network and rely on fail-closed source behavior.

## Validation Notes

Commands run:

```text
.venv/bin/python -m pytest tests/fund/data/test_thermometer_source.py tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
79 passed in 0.54s

.venv/bin/python -m ruff check fund_agent tests
All checks passed!

git diff --check
passed
```

