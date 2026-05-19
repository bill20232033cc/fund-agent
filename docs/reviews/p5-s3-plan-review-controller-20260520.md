# P5-S3 Plan Review Controller - 2026-05-20

## Verdict

Plan requires changes before implementation.

方向正确：通过 snapshot `comparable_values` 扩大 correctness denominator，且不解析报告 Markdown。但当前计划对“字段存在但子字段缺失”的处理容易制造 false mismatch，也没有明确 `benchmark_name` 与当前 extractor 输出键名的兼容策略。

## Findings

### P5S3-PR-1 - 高 - 子字段缺失不应因字段级 `value_present=False` 直接 mismatch

当前计划说：如果 golden key 的 `field_name` 存在 snapshot record，但 `sub_field` 不在 `comparable_values`，且 `value_present=False`，返回 `None`，后续判为 mismatch。

这个规则过宽。字段级 `value_present=False` 只能证明整个字段缺失，不能证明某个白名单 sub-field 应该存在但缺失。举例：`fee_schedule` 或 `product_profile` 不在本 slice 白名单时，即使对应 field record 是 missing，也不应让 golden 子字段进入 mismatch。

要求修改：

- 只有当 `field_name` 在 P5-S3 comparable whitelist 中，且 `sub_field` 也在该字段白名单中，才允许使用 `None` 表示明确缺失并进入 mismatch。
- 非白名单字段或非白名单 sub-field 必须保持 unavailable。
- plan 和测试都要覆盖“非白名单字段 missing 仍 unavailable”。

### P5S3-PR-2 - 中 - `benchmark_name` 与当前 extractor 键名不一致，需明确 alias 策略

当前 fake 和部分实现使用 `benchmark_text`，golden answer 使用 `benchmark_name`。计划把两者都列入白名单，但没有说明如何从当前结构化值映射。

如果实现只复制原 dict 键，`benchmark_name` 仍会 unavailable，P5-S3 对 P0 benchmark 的分母扩大不稳定。

要求修改：

- 明确 `benchmark_name` alias：当 `benchmark_name` 缺失但 `benchmark_text` 存在时，`comparable_values["benchmark_name"] = benchmark_text`。
- alias 必须只在 `benchmark` 字段内发生，不做跨字段推断。
- 测试覆盖 `benchmark_name` golden key 能从 `benchmark_text` 命中。

## Accepted Parts

- `comparable_values` 作为 snapshot 结构化字段是合适入口。
- 首版不纳入 `product_profile` 长文本和 `fee_schedule`，边界正确。
- 旧 snapshot 兼容要求正确。

## Gate Decision

当前 gate 维持 `P5-S3 plan review`。

下一步：修订 plan 后进入 `P5-S3 plan re-review`。
