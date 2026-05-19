# P5-S2 Plan Review Controller - 2026-05-20

## Verdict

Plan requires changes before implementation.

P5-S2 方向正确：规则应留在 Capability 层，并从 snapshot/score 同源派生。但当前 plan 有两个会影响实现正确性的缺口：FQ5 容易被实现成 FQ1 的重复规则，`fund_quality` 的基金级字段一致性和 issue metadata schema 也不够稳定。

## Findings

### P5S2-PR-1 - 高 - FQ5 定义会把 `preferred_lens mismatch` 实现成 App 类别冲突的重复表达

当前 plan 说“App 类别可明确映射但与 `classified_fund_type` 冲突：`mismatch`，触发 `FQ5/block`”。这能表达类型冲突，但不能证明 `preferred_lens` 实际错配。

直接原因是当前系统没有机器可读 CHAPTER_CONTRACT parser，也没有把 Service 实际选择的 lens 写入 `score.json`。如果 P5-S2 直接按当前 plan 实现，FQ5 会和 FQ1 App 类别冲突完全重叠，容易让 control doc 误以为“preferred_lens 与实际报告 contract 已校验”。

要求修改：

- 将 FQ5 首版明确定义为 `preferred_lens_resolvability`，即“是否能从标准基金类型稳定解析出应使用的 preferred_lens key”。
- `fund_quality` 必须输出 `preferred_lens_key` 和 `preferred_lens_status`。
- `preferred_lens_key` 映射必须配置化并覆盖 6 个标准基金类型。
- App 类别冲突只能作为 `preferred_lens_status=mismatch` 的辅助原因，不能宣称已校验最终报告中的实际 lens。
- plan 需要把“机器可读 CHAPTER_CONTRACT 后再做实际 contract lens 校验”写为 residual risk，而不是在本 slice 中暗示已完成。

### P5S2-PR-2 - 高 - `fund_quality` 未规定基金级字段冲突如何处理

`fund_quality` 从 snapshot records 派生，而 snapshot 每个字段行都重复携带 `fund_code / fund_name / app_category / classified_fund_type`。当前 plan 只说输出这些字段，没有规定同一基金多行值不一致时如何裁决。

如果实现取第一行，单条异常记录可能静默决定 App 类别、基金类型或 preferred_lens。质量 gate 的 root cause 必须数据同源，不能靠“第一条看起来对”。

要求修改：

- `fund_quality` 派生时必须按基金聚合所有 snapshot records。
- 对 `app_category`、`classified_fund_type`、`fund_name` 做唯一性检查。
- 同一基金出现多个非空 `classified_fund_type` 或多个非空 `app_category` 时，标记 `app_category_status=unknown`、`preferred_lens_status=mismatch`，并在 `reason` 中列出冲突值。
- 该路径至少有单元测试覆盖。

### P5S2-PR-3 - 中 - 新规则 issue 缺少稳定 metadata 字段，容易把结构化信息塞进 message

现有 `QualityGateIssue` 只有 `coverage_rate / traceability_rate / expected_value / actual_value` 等字段。FQ1 App 类别冲突、FQ4 缺失率和 FQ5 lens resolvability 都需要结构化输出 App 类别、基金类型、缺失率、lens key/status。

如果只写到 message，后续 artifact、CLI 或回归测试只能解析自然语言，违反 P4/P5 质量闭环“结构化可比”的目标。

要求修改：

- plan 中明确扩展 `QualityGateIssue` 的可选字段，至少包括：
  - `app_category`
  - `classified_fund_type`
  - `preferred_lens_key`
  - `observed_rate`
  - `threshold`
- FQ4 不复用 `coverage_rate` 表示缺失率，避免字段语义混乱。

## Accepted Parts

- 不读取报告 Markdown 来实现 FQ4，方向正确。
- 旧 `score.json` 缺少 `fund_quality` 时保持兼容，方向正确。
- P5-S2 不修改 Service/CLI 接入策略，方向正确。
- correctness denominator 留给 P5-S3，边界正确。

## Gate Decision

当前 gate 维持 `P5-S2 plan review`。

下一步：修订 `docs/reviews/p5-s2-quality-gate-rules-plan-20260520.md` 后进入 plan re-review。
