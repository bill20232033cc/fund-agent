# P19-S2 Plan Review Controller Judgment（2026-05-23）

## Verdict

`ACCEPTED_WITH_IMPLEMENTATION_CONSTRAINTS`

Two independent plan reviews returned `PASS_WITH_FINDINGS`:

- `docs/reviews/p19-s2-plan-review-mimo-20260523.md`
- `docs/reviews/p19-s2-plan-review-glm-20260523.md`

The P19-S2 plan is accepted because the data-source feasibility probe is sufficient for 中证500, the batch contract belongs in `ThermometerService`, and the plan stays inside P19-S2 boundaries: no `fund-analysis analyze` integration, no all-A market thermometer, no PB-only all-A, no Dayu runtime, and no `extra_payload`.

## Accepted Findings

| Finding | Source | Judgment | Implementation Constraint |
|---|---|---|---|
| Malformed CLI input must exit 2 rather than fall through current broad `except Exception` path | MiMo | Accepted | CLI thermometer must catch parse/request `ValueError` separately and return exit 2; unexpected exceptions remain exit 1. |
| Well-formed unsupported index must be item-level unavailable, not malformed input | MiMo / GLM | Accepted | UI parser may only validate shape; Service/source failure for `999999` or `399006` becomes per-item `ThermometerReading(unavailable=True)` in batch with CLI exit 0. |
| `index_code` / `index_codes` state machine needs a single Service normalization boundary | GLM | Accepted | Add one Service-owned normalization helper that handles mutually exclusive fields, empty values, six-digit shape validation, preserve-order de-duplication, and batch/single mode. |
| Duplicate index policy must be concrete | MiMo / GLM | Accepted | Preserve-order de-duplication is accepted; `requested_index_codes`, `readings`, and `result_count` use the normalized sequence. |

## Required Implementation Tests

Implementation must include automated tests for:

- CLI malformed input exits 2: `000300,abc`, `000300,`, `,000905`, and all-empty/blank batch forms.
- Service direct-call state machine: both `index_code` and `index_codes`, empty `index_codes`, malformed codes, duplicate codes, and normal `("000300", "000905")`.
- Well-formed unsupported batch item: `("000300", "999999")` or `("000300", "399006")` returns partial unavailable with exit 0 in CLI JSON.
- Legacy no-index public-page adapter remains unchanged.
- Single-index `--index 000300` JSON/plain output remains unchanged.

## Accepted Plan Scope

Implementation may:

- Add `000905 -> 中证500` to the self-owned index source mapping.
- Add a batch result type and Service batch orchestration.
- Extend CLI parsing/rendering for comma-separated `--index`.
- Update README and test documentation to describe current `000300`, `000905`, and batch behavior.

Implementation must not:

- Wire thermometer into `fund-analysis analyze`.
- Implement all-A market thermometer or PB-only all-A output.
- Change no-index `fund-analysis thermometer` public-page transitional behavior.
- Add parquet dependency, paid data source, Dayu runtime, or `extra_payload`.

## Validation Basis

The planning agent recorded a live feasibility probe:

```text
akshare 1.18.60
stock_index_pe_lg("中证500"): 4701 rows, includes 滚动市盈率中位数
stock_index_pb_lg("中证500"): 4701 rows, includes 市净率中位数
common PE/PB dates: 4701
latest date: 2026-05-22
```

This is enough to start fixture-based implementation. Live akshare latency remains a residual risk, not a default test gate.

## Next Gate

`P19-S2 implementation`

Implementation handoff should follow `docs/reviews/p19-s2-broad-index-thermometer-plan-20260523.md` plus the constraints in this judgment.
