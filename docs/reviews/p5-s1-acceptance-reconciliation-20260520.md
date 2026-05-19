# P5-S1 Acceptance Reconciliation - 2026-05-20

## Verdict

P5-S1 accepted.

P4 quality gate 已接入 `fund-analysis analyze` 主链路。当前实现满足 post-P4 第一优先级目标：报告入口不再静默绕过已存在的输入质量 gate；Service 层能按显式策略运行、跳过、警告或阻断；CLI 能暴露 gate 状态和 artifact 路径。

下一 gate：`P5-S2 quality gate rules plan/review`。

## Inputs

- Plan: `docs/reviews/p5-s1-quality-gate-integration-plan-20260520.md`
- Plan review: `docs/reviews/p5-s1-plan-review-controller-20260520.md`
- Plan re-review: `docs/reviews/p5-s1-plan-rereview-controller-20260520.md`
- Implementation: `docs/reviews/p5-s1-implementation-20260520.md`
- Code review: `docs/reviews/code-review-20260520-0350.md`
- Global control doc: `docs/implementation-control.md`
- P4 control doc: `docs/implementation-control-p4.md`

## Accepted Scope

- Capability 层新增 bundle-to-gate adapter：复用已抽取的 `StructuredFundDataBundle`，不在 `analyze` 路径二次调用 `FundDataExtractor.extract(...)`。
- Service 层新增显式 quality gate 输入：`quality_gate_policy`、`quality_gate_source_csv`、`quality_gate_output_dir`、`quality_gate_run_id`、`quality_gate_golden_answer_path`。
- Service 层新增显式结果：`quality_gate_result` 与 `quality_gate_not_run_reason`。
- block 策略使用结构化 `QualityGateBlockedError`，携带 `QualityGateResult`，避免把质量阻断降级成普通文本失败。
- CLI 层新增显式参数，并在 gate block 时退出非零、输出 gate 状态与 artifact 路径，不输出形式完整但质量不可用的报告。
- 默认 run id 使用时间戳，避免自动运行覆盖上一轮 quality gate 产物。
- 文档和测试已同步覆盖 Capability adapter、Service 策略、CLI 参数与阻断输出。

## Review Closure

Controller code review 发现 1 个高风险问题：adapter 复用 `run_extraction_score(...)` 会让只包含当前基金的合法单基金 CSV 被 `select_minimal_golden_set(...)` 误伤为 fatal error。

该问题已通过新增 `write_extraction_score_records(...)` 修复：

- 独立 CLI scoring 仍保留 minimal golden set 行为。
- `analyze` quality gate adapter 使用已加载 snapshot records 写 score/gate，不再要求 source CSV 包含完整最小 golden set。
- 新增测试覆盖单基金合法 CSV 可运行，并断言 gate 专用 `golden_set.records == []`。

## Validation Accepted

- `.venv/bin/python -m pytest tests/fund/test_quality_gate_integration.py tests/fund/test_extraction_score.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q`: `26 passed`
- `.venv/bin/python -m pytest tests/ -q`: `179 passed`
- `.venv/bin/ruff check .`: passed
- `git diff --check`: passed

## Boundary Judgment

- Capability 继续负责 snapshot、score、quality gate、correctness 和基金质量规则。
- Service 只编排质量预检与报告生成，不承载基金领域规则。
- CLI 只做参数映射和输出渲染，不直接判断基金质量。
- P5-S1 未把 quality gate 混入 `ProgrammaticAuditResult`；二者仍是不同质量面。
- 显式参数均作为 `FundAnalysisRequest` 字段声明，未放入 `extra_payload`。

## Deferred Scope

- P5-S2：补齐 P4-R9，包括 FQ1 App 类别冲突分支、FQ4 数据不足比例、FQ5 preferred_lens mismatch。
- P5-S3：扩大 correctness denominator，暴露更多 P0 子字段。
- P5-S4：失败基金进入 fund-level accounting，避免只落在 `errors.jsonl` 后被 gate 忽略。
- RR-13：`016492` 重复仍需用户核对 App 源数据。
- `reports/quality-gate-runs/` 是运行产物，不纳入 PR scope。

## Gate Decision

当前 gate 从 `P5-S1 code review passed after fix` 推进为 `P5-S1 accepted`。

下一步进入 `P5-S2 quality gate rules plan/review`。
