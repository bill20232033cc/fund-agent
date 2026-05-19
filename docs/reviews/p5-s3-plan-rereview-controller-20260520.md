# P5-S3 Plan Re-review Controller - 2026-05-20

## Verdict

P5-S3 plan passed after fix.

两个 plan finding 均已关闭，可以进入 implementation。

## Closure

### P5S3-PR-1: 子字段缺失不应因字段级 missing 直接 mismatch

状态：closed。

修订后 plan 明确：只有 `field_name` 和 `sub_field` 都在 comparable whitelist 中，且字段明确 missing，才允许返回 `None` 并进入 mismatch；非白名单字段或子字段必须保持 unavailable。

### P5S3-PR-2: `benchmark_name` 与当前 extractor 键名不一致

状态：closed。

修订后 plan 明确了字段内 alias：仅在 `benchmark` 字段中，`benchmark_name` 缺失且 `benchmark_text` 存在时，用 `benchmark_text` 填充 `benchmark_name`。不做跨字段同义词推断。

## Accepted Implementation Entry

实现范围：

- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/extraction_score.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- `fund_agent/fund/README.md`
- `tests/README.md`

不应修改 golden answer JSON schema、Service/CLI quality gate 策略或 quality gate 规则。

## Gate Decision

当前 gate 从 `P5-S3 plan patched after controller review` 推进为 `P5-S3 implementation`。

下一步进入 `P5-S3 implementation`。
