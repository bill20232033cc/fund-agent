# P19-S4 Expanded Index Coverage Plan（2026-05-23）

## Verdict

`BLOCKED_FOR_TARGET_IMPLEMENTATION`

P19-S4 的设计目标是扩展精确指数覆盖：创业板指 `399006`、科创50 `000688`、中证红利 `000922`、中证消费 `000932`、中证医药 `000933`。本地 `.venv` 中 akshare `1.18.60` 的 `stock_index_pe_lg` / `stock_index_pb_lg` 对这五个目标指数的常见 symbol 均不可用，且源码级 symbol map 不包含这些目标指数。

第一性原理裁决：温度计的核心事实是“目标指数的 PE/PB 历史序列”。如果当前数据源不能证明能返回目标指数，就不能用相近指数替代，也不能只因代码形状简单就扩展 `SUPPORTED_INDEX_SYMBOLS`。P19-S4 实现必须先停在 source feasibility gate，除非找到并验证这些精确指数的 PE/PB 历史来源。

## Required Context Read

- `AGENTS.md`
- `docs/design.md` §11.4 / §11.5
- `docs/implementation-control.md` Startup Packet and P19 exit criteria
- `docs/p19-phase-definition.md` P19-S4
- Existing implementation:
  - `fund_agent/fund/data/thermometer_source.py`
  - `fund_agent/services/thermometer_service.py`
  - `fund_agent/ui/cli.py`
  - `tests/fund/data/test_thermometer_source.py`
  - `tests/services/test_thermometer_service.py`
  - `tests/ui/test_cli.py`

## Scope Boundary

P19-S4 may only extend self-owned index thermometer coverage for:

| Index | Code | P19-S4 status |
|---|---:|---|
| 创业板指 | `399006` | blocked: no verified `stock_index_pe_lg` / `stock_index_pb_lg` symbol |
| 科创50 | `000688` | blocked: no verified `stock_index_pe_lg` / `stock_index_pb_lg` symbol |
| 中证红利 | `000922` | blocked: no verified `stock_index_pe_lg` / `stock_index_pb_lg` symbol |
| 中证消费 | `000932` | blocked: no verified `stock_index_pe_lg` / `stock_index_pb_lg` symbol |
| 中证医药 | `000933` | blocked: no verified `stock_index_pe_lg` / `stock_index_pb_lg` symbol |

P19-S4 must not:

- implement all-A market thermometer;
- make `fund-analysis thermometer` without `--index` default to all-A;
- change P19-S3 `ValuationStateResolution` mapping rules;
- auto-map these new indexes into `fund-analysis analyze`;
- substitute similar but different indexes such as 创业板50, 上证红利, 深证红利, or 中证1000;
- use Youzhiyouxing page scraping as production source;
- introduce paid data, parquet, Dayu runtime, or `extra_payload`.

## Akshare Probe

Command summary:

```text
.venv/bin/python - <<'PY'
import akshare as ak
for symbol in candidate_symbols:
    ak.stock_index_pe_lg(symbol=symbol)
    ak.stock_index_pb_lg(symbol=symbol)
PY
```

Environment:

```text
akshare_version 1.18.60
```

### Target Symbol Probe

| Code | Tried symbols | PE result | PB result | Decision |
|---|---|---|---|---|
| `399006` | `创业板指`, `创业板指数`, `创业板综` | `KeyError` for all | `KeyError` for all | blocked |
| `000688` | `科创50`, `科创 50`, `上证科创板50成份指数` | `KeyError` for all | `KeyError` for all | blocked |
| `000922` | `中证红利`, `中证红利指数` | `KeyError` for all | `KeyError` for all | blocked |
| `000932` | `中证消费`, `中证主要消费`, `中证主要消费指数` | `KeyError` for all | `KeyError` for all | blocked |
| `000933` | `中证医药`, `中证医药卫生`, `中证医药卫生指数` | `KeyError` for all | `KeyError` for all | blocked |

### Source Inspection

Local akshare source for `stock_index_pe_lg` and `stock_index_pb_lg` declares this symbol set:

```text
上证50, 沪深300, 上证380, 创业板50, 中证500, 上证180,
深证红利, 深证100, 中证1000, 上证红利, 中证100, 中证800
```

The five P19-S4 targets are absent from this symbol map.

### Non-target Control Probe

The same interface family is not globally broken. It successfully returned PE/PB fields for non-target symbols:

| Symbol | PE rows | PB rows | Latest date | Target columns |
|---|---:|---:|---|---|
| 创业板50 | 4021 | 4021 | 2026-05-22 | `滚动市盈率中位数`, `市净率中位数` |
| 上证红利 | 5191 | 5191 | 2026-05-22 | `滚动市盈率中位数`, `市净率中位数` |
| 深证红利 | 5191 | 5191 | 2026-05-22 | `滚动市盈率中位数`, `市净率中位数` |
| 中证1000 | 2818 | 2818 | 2026-05-22 | `滚动市盈率中位数`, `市净率中位数` |

This confirms the failure mode is target symbol unsupported, not a general network or schema outage. These non-target symbols must not be used as P19-S4 substitutes.

## Design Boundary Check

| Boundary | P19-S4 plan decision |
|---|---|
| Capability data | Only this layer may add verified index code -> symbol/name mappings. No mapping may be added without live/source-inspection evidence for the exact target index. |
| Capability analysis | `ThermometerCalculator` remains unchanged; PE/PB percentile formula and 30 common-date minimum are already generic. |
| Capability cache | `ThermometerHistoryCache` remains unchanged; existing per-index JSON path works for any verified code. |
| Service | `ThermometerService` normalization, support check, batch orchestration, stale fallback, and unsupported item unavailable semantics remain unchanged unless tests reveal a direct regression. |
| UI | `fund-analysis thermometer --index ...` rendering remains unchanged except help/readme text if verified indices are added. |
| Analyze integration | P19-S4 does not change `ValuationStateResolution`, benchmark mapping, or automatic valuation-state rules. New indices, if later verified, are only queryable through `fund-analysis thermometer --index ...` in this slice. |

## Implementation Plan If Source Gate Is Resolved

This section is code-generation-ready only after a reviewer/controller records exact PE/PB source evidence for one or more P19-S4 target indexes.

### Slice 0: Source Feasibility Gate

Files:

- `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md`
- optional follow-up artifact: `docs/reviews/p19-s4-index-source-feasibility-20260523.md`

Required evidence for each candidate:

- exact index code;
- exact symbol/API argument;
- PE rows > 30;
- PB rows > 30;
- PE contains `滚动市盈率中位数`;
- PB contains `市净率中位数`;
- common PE/PB dates >= 30;
- latest date present;
- failure output if unavailable.

Exit rule:

- implement only indexes with verified exact source evidence;
- defer unavailable targets explicitly;
- do not substitute nearby indexes.

### Slice 1: Capability Data Mapping

Files:

- `fund_agent/fund/data/thermometer_source.py`
- `tests/fund/data/test_thermometer_source.py`

Work after source gate:

- Extend `SUPPORTED_INDEX_SYMBOLS` only with verified exact mappings, for example:
  - `"399006": "<verified exact symbol>"`
  - `"000688": "<verified exact symbol>"`
  - `"000922": "<verified exact symbol>"`
  - `"000932": "<verified exact symbol>"`
  - `"000933": "<verified exact symbol>"`
- Extend `INDEX_NAMES` with the exact display names from `docs/design.md` §11.4.
- Keep `PE_COLUMN = "滚动市盈率中位数"` and `PB_COLUMN = "市净率中位数"`.
- Keep strict date behavior from P19-S1: no truncation and no trim for string dates.
- Keep unsupported code fail-closed in `AkshareIndexThermometerSource`.

Tests:

- Parametrize existing source merge test over all supported verified mappings.
- Assert each verified code calls injected PE/PB fetchers with its exact verified symbol.
- Keep unsupported `999999` rejection.
- Keep strict date schema tests unchanged.
- Add a support helper test if implementation exports/uses `is_supported_index_code`.

### Slice 2: Service Batch Coverage Tests

Files:

- `tests/services/test_thermometer_service.py`

Work after source gate:

- Keep Service code unchanged unless tests reveal direct need.
- Add batch fixture covering all currently supported codes, preserving order:
  - existing `000300`, `000905`;
  - plus every source-verified P19-S4 code.
- Assert:
  - `requested_index_codes` equals normalized sequence;
  - `readings` length equals normalized sequence length;
  - each reading `index_code` is preserved;
  - `unavailable=False` when fixture data is valid;
  - duplicate de-duplication still works with a P19-S4 code.
- Keep tests that `999999` is item-level unavailable and cannot bypass support check through fresh cache.

No Service changes should be made for P19-S4 unless a verified code needs a new source failure taxonomy. The existing Service-owned normalization and batch orchestration already satisfy the slice.

### Slice 3: CLI Rendering And Help

Files:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`

Work after source gate:

- Update `--index` help text to mention the newly verified codes.
- Do not add UI allowlist validation; UI still only splits string into `index_code` / `index_codes`.
- Add CLI batch JSON/plain tests for all currently supported codes.
- Keep malformed input exit 2 tests unchanged.
- Keep `000300,999999` partial unavailable JSON exit 0 test unchanged.
- Keep no-index `fund-analysis thermometer` public-page behavior unchanged.

### Slice 4: README Sync

Files:

- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`

Work after source gate:

- Update user-facing current commands to show all verified `--index` codes.
- State that P19-S4 indices are queryable via `fund-analysis thermometer --index ...`.
- State explicitly that P19-S4 does not change default no-index thermometer output and does not change `fund-analysis analyze` automatic mapping.
- Update Fund README supported-index list and tests README coverage.

### Slice 5: Implementation Artifact

File:

- `docs/reviews/p19-s4-expanded-index-coverage-implementation-20260523.md`

Required content:

- accepted verified index list;
- deferred blocked index list with probe output;
- files changed;
- validation commands and results;
- explicit non-goal confirmation.

## Test Plan

Run after implementation, if source gate resolves at least one exact target:

```text
.venv/bin/python -m pytest tests/fund/data/test_thermometer_source.py tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
.venv/bin/python -m pytest tests/services/test_fund_analysis_service.py tests/fund/analysis/test_checklist.py tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py -q
.venv/bin/python -m ruff check fund_agent tests
git diff --check
```

The second pytest command is required because P19-S3 already connected thermometer-derived valuation state into analyze for existing exact benchmark mappings. P19-S4 must prove it did not unintentionally broaden or change those mappings.

## Acceptance Criteria

P19-S4 implementation may be accepted only if:

- at least one P19-S4 target has exact PE/PB source evidence, or controller explicitly accepts a docs-only blocked/deferred closeout;
- every implemented code has fixture tests proving symbol mapping, source merge, batch Service output, and CLI output;
- no target is represented by a semantically adjacent substitute;
- `fund-analysis thermometer --index <supported>` works for every implemented code;
- `fund-analysis thermometer --index 000300,000905,<implemented P19-S4 codes>` works in batch;
- malformed CLI inputs still exit 2;
- unsupported well-formed code still renders item-level unavailable with exit 0 in batch;
- no-index public-page adapter behavior remains unchanged;
- P19-S3 `ValuationStateResolution` mapping rules remain unchanged.

## Residual Risks

- Live akshare availability remains external and can fail or time out.
- Legulegu schema drift can remove or rename `滚动市盈率中位数` / `市净率中位数`; existing source parsing should continue to fail closed.
- akshare `1.18.60` currently lacks exact P19-S4 target symbols in `stock_index_pe_lg` / `stock_index_pb_lg`; source feasibility is the blocker.
- Future analyze automatic mapping for these expanded indices must be separately planned and reviewed. P19-S4 must not silently widen benchmark-to-valuation behavior.
- All-A market thermometer remains P19-S5 / all-A PE source gate and must not be pulled into P19-S4.

## Recommended Next Gate

`P19-S4 source feasibility review`

The controller should review this plan and decide one of:

- close P19-S4 as blocked/deferred with this artifact as evidence;
- assign a source-feasibility worker to find exact PE/PB historical sources for the five target indexes;
- reduce P19-S4 scope only to exact targets that pass a new source gate.
