# P19-S5 S5-3 CLI Output And Docs Sync — Code Review

## Scope

- Mode: current changes (uncommitted workspace)
- Branch: `phase/p19-s5-all-a-pe-source-gate`
- Base: current workspace uncommitted changes only
- Output file: `docs/reviews/p19-s5-s5-3-code-review-ds-20260523.md`
- Included scope:
  - `fund_agent/ui/cli.py` — CLI help text, `thermometer` command docstring, `--force-refresh` wording
  - `tests/ui/test_cli.py` — thermometer CLI tests (new all-A tests + existing regression)
  - `README.md` — root user manual temperature section and capability list
  - `fund_agent/fund/README.md` — Fund capability P19-S5 all-A and cache namespace
  - `tests/README.md` — test coverage descriptions
  - `docs/reviews/p19-s5-s5-3-cli-docs-implementation-20260523.md` — implementation artifact (reviewed for consistency)
- Excluded scope:
  - `fund_agent/services/thermometer_service.py` — not modified in S5-3 (Service ownership verified via read-through)
  - `fund_agent/fund/data/thermometer_source.py`, `thermometer_cache.py`, `thermometer_types.py` — not modified
  - `fund_agent/fund/analysis/` — not modified
  - `fund_agent/services/fund_analysis_service.py` — not modified
  - `docs/design.md`, `docs/implementation-control.md` — not modified
  - Untracked files (`docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`, other review artifacts) — pre-existing, out of scope
- Parallel review coverage: 无

## Review Truths Applied

- `AGENTS.md` — module boundary rules (UI only depends on Service; README synchronization rules)
- `docs/design.md` §11 — thermometer design: `wind_all_a` as P0 target, disclaimer requirement, non-goals, module boundaries
- `docs/implementation-control.md` — current gate is P19-S5 S5-3, S5-2 accepted
- `docs/reviews/p19-s5-all-a-market-thermometer-implementation-plan-20260523.md` Slice S5-3 — exact allowed changes
- `docs/reviews/p19-s5-s5-2-code-review-controller-judgment-20260523.md` — S5-2 accepted guarantees (default wind_all_a routing, cache namespace, no Service akshare import, P19-S3 analyze regression intact)

## Review Walkthrough

### Entry Point: `thermometer` CLI command

**Path**: `fund_agent/ui/cli.py:258-312`

1. `--index` option parses via `_parse_index_option()` (line 291) — when `None`, returns `(None, None)`; single code returns `(code, None)`; comma-separated returns `(None, tuple(...))`.
2. `ThermometerRequest(index_code=parsed_index_code, index_codes=parsed_index_codes, ...)` constructed at line 293-299.
3. `ThermometerService().run(request)` called — **Service owns default routing to `wind_all_a`** (verified in `thermometer_service.py:304`: `_normalize_request` returns `ALL_A_MARKET_CODE` when both fields are `None`).
4. Result dispatched through `_thermometer_snapshot_payload()` (line 308) — isinstance branches for `ThermometerReading` / `ThermometerBatchResult` / duck-typing fallback for `ThermometerSnapshot`.
5. JSON or plain output rendered (lines 309-312).

**Verdict**: CLI correctly delegates default routing to Service. No direct knowledge of `wind_all_a` in the default path — CLI only passes `None, None`.

### Help Text Changes

**File**: `fund_agent/ui/cli.py:261-271`

- `--index` help: `"自建温度计代码；支持 wind_all_a、000300、000905 或逗号分隔批量"` — matches plan requirement.
- `--force-refresh` help: `"强制刷新自有温度计历史数据"` — matches plan requirement (no longer says "公开页面数据").
- Command docstring: `"查询自建市场或指数温度计读数"` — matches plan (no longer says "查询温度计快照或…").
- Args docstring: `"为空时由 Service 默认路由到全 A 市场"` — accurate.

**Test evidence** (`tests/ui/test_cli.py:997-1018`): `test_thermometer_cli_help_documents_all_a_and_self_owned_history` asserts all three codes and "自有温度计历史数据" in help output. ✓

### No-Argument Default Path

**Test**: `test_thermometer_cli_no_arg_json_delegates_default_to_service` (line 1107-1138)

- Fake Service returns `_available_all_a_thermometer_reading()`.
- Asserts `last_request.index_code is None` and `last_request.index_codes is None` — CLI does not inject `wind_all_a`.
- Asserts JSON payload has `index_code: wind_all_a`, `index_name`, `temperature`, PE/PB percentiles, `valuation_state_candidate`, disclaimer.
- Asserts `disclaimer` contains "非有知有行官方数据".

**Verdict**: Default routing ownership is correctly placed in Service. ✓

### Explicit `--index wind_all_a` Path

**Test**: `test_thermometer_cli_prints_all_a_reading_json` (line 1171-1198)

- CLI passes `index_code="wind_all_a"` to Service.
- JSON payload includes `index_code: wind_all_a`, `index_name: 万得全 A / 全 A 市场`, `source: akshare_legulegu_all_a_pe_pb`.
- `last_request.index_code == "wind_all_a"`, `index_codes is None`.

**Verdict**: Explicit single-code path correctly forwards `wind_all_a`. ✓

### Mixed Batch `--index wind_all_a,000300` Path

**Test**: `test_thermometer_cli_prints_all_a_mixed_batch_reading_json` (line 1296-1325)

- CLI parses `wind_all_a,000300` → `index_codes=("wind_all_a", "000300")`, `index_code=None`.
- JSON payload has `requested_index_codes: ["wind_all_a", "000300"]`, `result_count: 2`.
- Order preserved: `readings[0].index_code == "wind_all_a"`, `readings[1].index_code == "000300"`.

**Verdict**: Mixed batch correctly preserves order and includes all-A alongside index readings. ✓

### Malformed Input Path

**Test**: `test_thermometer_cli_malformed_index_input_exits_two` (line 1432-1463)

Parametrized cases include `"wind_all_a,abc"` — the new all-A malformed case.
- All cases assert `exit_code == 2` and `"温度计请求参数错误" in result.output`.
- The `ValueError` originates from `_normalize_index_codes` in Service (line 330-331), propagated through CLI's `except ValueError` block (line 302-304).

**Verdict**: Malformed all-A input correctly exits 2. ✓

### Plain Output Completeness

**Test**: `test_thermometer_cli_prints_plain_summary` (line 1066-1104)

Default plain output assertions cover:
- `index_code: wind_all_a`
- `index_name: 万得全 A / 全 A 市场`
- `source: akshare_legulegu_all_a_pe_pb`
- `unavailable: false`
- `temperature: 35.25`
- `pe_percentile: 30.00`
- `pb_percentile: 40.50`
- `valuation_state_candidate: fair`
- `disclaimer: 本温度计基于有知有行公开方法论独立计算，非有知有行官方数据。`
- `last_request.index_code is None`, `index_codes is None`, `cache_dir` and `force_refresh` forwarded.

**Verdict**: All required fields present in plain output. Matches `docs/design.md` §11.8 disclaimer requirement. ✓

### All-A Unavailable Path

**Test**: `test_thermometer_cli_prints_json_for_unavailable_all_a_reading` (line 1141-1168)

- `_unavailable_all_a_thermometer_reading()` returns `index_code="wind_all_a"`, `unavailable=True`, `temperature=None`, etc.
- JSON payload correctly serializes `unavailable: true`, `unavailable_reason: "network down"`, null temperature/percentiles.
- Exit code 0 (data-level unavailable, not process failure).

**Verdict**: All-A unavailable state correctly rendered. ✓

### Existing Test Regression Coverage

All pre-existing tests preserved and updated:

| Test | Status |
|------|--------|
| `test_thermometer_cli_prints_index_reading_json` (000300 JSON) | Updated to use `_available_thermometer_reading()` (now 000300-based). ✓ |
| `test_thermometer_cli_prints_index_reading_plain` (000300 plain) | Unchanged, passes. ✓ |
| `test_thermometer_cli_prints_batch_reading_json` (000300,000905 JSON) | Unchanged, passes. ✓ |
| `test_thermometer_cli_prints_batch_reading_plain` (000300,000905 plain) | Unchanged, passes. ✓ |
| `test_thermometer_cli_partial_unavailable_batch_json_exits_zero` (000300,999999) | Unchanged, passes. ✓ |
| `test_thermometer_cli_unsupported_batch_item_returns_unavailable_json` | Updated: removed forged cache for 999999, added assertion for full code display. ✓ |
| `test_thermometer_cli_exits_nonzero_on_service_error` | Unchanged, passes. ✓ |
| `test_thermometer_cli_malformed_index_input_exits_two` | Extended with `wind_all_a,abc` case. ✓ |

Controller-verified: 38 CLI tests pass, 108 full-suite pass, 20 fund-analysis-service pass, ruff clean, git diff --check clean.

### README Documentation Accuracy

**Root README** (`README.md`):

Quick commands section (line 66-70):
- `fund-analysis thermometer` — "查询默认全 A 市场温度计" ✓
- `fund-analysis thermometer --index wind_all_a,000300,000905 --json` — "查询自建全 A / 宽基指数温度计" ✓

Current capabilities (lines 119-121):
- "有知有行温度计 data adapter：保留为过渡/对比能力，不再作为默认 CLI 查询路径" ✓
- "自建全 A 市场温度计 CLI 默认入口：`fund-analysis thermometer`" ✓
- "自建全 A / 宽基指数温度计 CLI 查询入口" ✓

Non-goals (line 137):
- "主动基金持仓估值、债券/QDII/FOF 估值状态自动判断" — all-A removed from non-goals (correct: it IS now implemented). ✓

Temperature section (lines 161-179):
- "默认查询全 A 市场 `wind_all_a`" ✓
- "analyze 自动估值仍只使用沪深300/中证500 exact supported-index 单指数路径，不把全 A 自动套用于主动基金" — explicitly separates CLI default from analyze behavior. ✓

**Fund README** (`fund_agent/fund/README.md`):
- Line 310: "P19-S1/S2/P19-S5" — updated from "P19-S1/S2". ✓
- Line 312: Default all-A, explicit all-A, batch coverage described. ✓
- Line 313: all-A PE/PB data source described. ✓
- Line 315: "按市场/指数隔离命名空间：全 A 使用 `cache/thermometer/market/wind_all_a_history.json`" ✓
- Line 317: `analyze` boundary preserved — only exact 000300/000905. ✓

**Tests README** (`tests/README.md`):
- Line 145-146: source/cache tests updated to mention all-A `wind_all_a` and market/index namespace. ✓
- Line 153-154: service/CLI tests updated to mention default all-A routing and `--index wind_all_a`. ✓
- Line 163: test constraint updated from "fake fetcher and HTML snippet" to include "fake akshare、临时缓存或 fake Service 覆盖 `wind_all_a`". ✓

**Verdict**: All four README files are consistent with implementation and with each other. No document claims `analyze` uses all-A. ✓

### Boundary Compliance

Checked against `AGENTS.md` module boundaries:

- UI (`cli.py`): only depends on `ThermometerService` and `ThermometerRequest` from Service layer; imports `ThermometerReading`/`ThermometerBatchResult` from Capability types. No direct akshare, source, or cache import. ✓
- Service (`thermometer_service.py`): not modified in S5-3; previously verified to own default routing, no akshare import, no Capability source field knowledge. ✓
- No `analyze`, renderer, audit, design, or control doc changes. ✓

### Adversarial Failure Pass

| Scenario | Path | Result |
|----------|------|--------|
| Empty `--index ""` | `_parse_index_option` → Service `_normalize_index_codes` → ValueError (not wind_all_a, not 6 digits) | exit 2 ✓ |
| `--index "   "` (whitespace) | `_parse_index_option` → single code → Service strips → ValueError (empty after strip) | exit 2 ✓ |
| `--index "wind_all_a,wind_all_a"` (duplicate) | Service `_normalize_index_codes` → dedup → single reading | no crash ✓ |
| Service returns `ThermometerSnapshot` (public-page path) | `_thermometer_snapshot_payload` duck-typing fallback | renders correctly ✓ |
| `ThermometerReading` with `disclaimer` at default | `_thermometer_reading_payload` uses `reading.disclaimer` (dataclass default) | always present ✓ |
| `None` temperature/percentiles in unavailable reading | `str(None)` would crash, but `_thermometer_reading_payload` checks `is not None` | safe ✓ |
| Concurrent CLI invocations | Each invocation creates independent `ThermometerService()` | no shared state ✓ |
| `--force-refresh` with no `--cache-dir` | forwarded as `force_refresh=True, cache_dir=None` | Service handles default ✓ |

No failure scenarios found where the CLI produces incorrect output, wrong exit code, or silent data corruption.

### Overcoupling Check

- CLI does not construct Capability objects directly. ✓
- CLI does not import akshare or source constants. ✓
- `_parse_index_option` is a pure string splitter — no knowledge of valid codes. ✓
- Service boundary: `index_code`/`index_codes` are explicit, not hidden in `extra_payload`. ✓
- Default routing (`wind_all_a`) lives in Service, not CLI — CLI and Service can evolve independently. ✓

## Findings

未发现实质性问题。

## Open Questions

无。

## Residual Risk

- The `_thermometer_snapshot_payload` duck-typing fallback for `ThermometerSnapshot` (cli.py:826-849) accesses `snapshot.market`, `snapshot.macro`, `snapshot.indexes` without an explicit isinstance guard. If a new return type is added to `ThermometerService.run()` without updating this function, it would silently fall into the `ThermometerSnapshot` branch. This is pre-existing and not introduced by S5-3; the current three return types are correctly handled.
- Public-page adapter tests (`tests/fund/data/test_thermometer.py`) remain unchanged. The default CLI path no longer exercises public-page snapshot output. This is intentional per S5-3 scope and the design decision to treat the public-page adapter as transitional/comparison only.
- Per-reading `disclaimer` is skipped in batch plain output (cli.py:940: `"disclaimer"` in skip set), while it is present in JSON. Batch-level disclaimer is shown in plain output. This is a reasonable UI choice (avoids repeating identical text), but consumers parsing plain batch output should be aware.

## Conclusion

**Verdict: PASS**

S5-3 implementation is correct and complete. All review focus items are satisfied: CLI help text, `--force-refresh` wording, no-arg default delegation to Service, explicit `wind_all_a` paths, mixed batch order preservation, malformed input exit codes, plain output field completeness, existing test regression, and all four README document accuracy. No Service/source/cache/analyze/renderer/audit/design/control changes were made. The implementation matches the accepted S5-3 plan slice exactly, preserves all S5-2 accepted guarantees, and contains no material defects.
