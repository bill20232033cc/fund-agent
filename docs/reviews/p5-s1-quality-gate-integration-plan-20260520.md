# P5-S1 Quality Gate Integration Plan - 2026-05-20

## Verdict

P5-S1 plan is ready for review.

目标是把 P4 已建立的 extraction snapshot / score / quality gate 能力接入 `fund-analysis analyze` 主链路，避免用户通过正常报告入口静默绕过低质量输入保护。

本 plan 只进入 review，不直接进入 implementation。

## Code Facts

当前代码事实：

- `fund-analysis analyze` 只构造 `FundAnalysisRequest` 并调用 `FundAnalysisService().analyze(...)`。
- `FundAnalysisService.analyze()` 已经抽取一次 `StructuredFundDataBundle`，随后执行 R=A+B-C、言行一致性、投资者获得感、风险检查、模板渲染和程序审计。
- `fund-analysis quality-gate` 是独立 CLI，只通过 `QualityGateService` 消费既有 `score.json`。
- `fund_agent.fund.extraction_snapshot.build_snapshot_records(...)` 已能把 `StructuredFundDataBundle` 转成 P4 字段级 snapshot records。
- `fund_agent.fund.extraction_score.run_extraction_score(...)` 当前主入口消费 `snapshot.jsonl` 并写出 `score.json`；底层已有 `score_snapshot_records(...)`、`score_fund_records(...)`、`compare_snapshot_correctness(...)` 等可复用能力。
- `fund_agent.fund.quality_gate.run_quality_gate(...)` 当前只消费 `score.json`，符合 P4-S4 skeleton 边界。

关键陷阱：P5-S1 不能简单让 CLI 在 `analyze` 前串跑 `extraction-snapshot -> extraction-score -> quality-gate`，否则会重复抽取同一份年报，并把领域编排泄漏到 UI 层。

## Integration Contract

### Request fields

在 `FundAnalysisRequest` 增加显式字段：

| Field | Type | Default | Purpose |
|---|---|---|---|
| `quality_gate_policy` | `Literal["off", "warn", "block"]` | `"block"` | 控制 quality gate 对报告输出的影响 |
| `quality_gate_source_csv` | `Path | None` | `docs/code_20260519.csv` | 提供 App 类别和基金池元数据 |
| `quality_gate_output_dir` | `Path | None` | `None` | 显式质量产物输出目录 |
| `quality_gate_run_id` | `str | None` | `None` | 质量产物运行 ID；为空时 Service 生成唯一 run id |
| `quality_gate_golden_answer_path` | `Path | None` | `reports/golden-answers/golden-answer.json` if exists, else `None` | strict correctness 输入 |

不允许使用 `extra_payload`。这些字段必须从 CLI 到 Service 显式传递。

### Result fields

在 `FundAnalysisResult` 增加：

| Field | Type | Purpose |
|---|---|---|
| `quality_gate_result` | `QualityGateResult | None` | `off` 或 prerequisites unavailable 时可为空 |
| `quality_gate_not_run_reason` | `str | None` | 未运行原因，必须可展示 |

`report_markdown` 仍只返回报告正文，不混入 gate 说明，避免污染用户可保存的 Markdown 报告。

### Blocked error contract

`quality_gate_policy=block` 且 gate status 为 `block` 时，Service 不得只抛普通 `ValueError`。必须定义结构化异常，例如 `QualityGateBlockedError`，至少携带：

- `quality_gate_result: QualityGateResult`
- `policy: Literal["block"]`
- `message: str`

CLI 专门捕获该异常，把 gate status、issue 数、`quality_gate.json` 路径和 `quality_gate.md` 路径写入 stderr，然后以非零状态退出。stdout 不输出完整报告。

### CLI behavior

`fund-analysis analyze` 增加显式参数：

- `--quality-gate-policy off|warn|block`
- `--quality-gate-source-csv PATH`
- `--quality-gate-output-dir PATH`
- `--quality-gate-run-id TEXT`
- `--quality-gate-golden-answer-path PATH`

CLI 输出规则：

- stdout 只输出报告 Markdown。
- quality gate summary 输出到 stderr。
- `quality_gate_policy=block` 且 gate status 为 `block` 时，CLI 非零退出，不输出完整报告。
- `quality_gate_policy=warn` 且 gate status 为 `block/warn` 时，stderr 输出明确 warning，stdout 仍输出报告。
- `quality_gate_policy=off` 时不运行 gate，stderr 输出 `quality gate skipped: policy=off`。
- prerequisites unavailable 时必须 stderr 明示 `quality gate not run: <reason>`；默认不阻断任意非精选基金分析。

## Implementation Slices

### P5-S1a: Capability adapter

新增或扩展 Capability 层函数，输入为已抽取的 `StructuredFundDataBundle` 和显式 gate 参数，输出 `QualityGateResult` 或 not-run reason。

要求：

- 复用 `build_snapshot_records(...)`，不重新调用 `FundDataExtractor.extract(...)`。
- 复用 score / correctness / quality gate 规则，不把评分规则复制到 Service。
- 保留 `run_quality_gate(...)` “只消费 `score.json`”的 P4 契约：adapter 可以生成本次 `score.json`，再调用 `run_quality_gate(...)`。
- 运行产物写到显式 `quality_gate_output_dir`；为空时使用 `reports/quality-gate-runs/<quality_gate_run_id>`。若 request 未提供 `quality_gate_run_id`，Service 必须生成唯一 run id，避免连续运行覆盖证据产物。
- 若用户提供已存在的 `quality_gate_output_dir`，P5-S1 必须明确覆盖语义：默认允许覆盖显式目录，但 CLI stderr 要输出实际目录；自动目录不应覆盖前一次默认运行。
- 若 `quality_gate_source_csv` 缺失、基金代码不在 CSV、CSV schema 不可用，应返回 not-run reason，不伪造 App 类别。

### P5-S1b: Service integration

扩展 `FundAnalysisService.analyze()`：

1. 校验新增 gate 参数。
2. 抽取 `StructuredFundDataBundle` 一次。
3. 在模板渲染前运行 quality gate adapter。
4. 若 policy 为 `block` 且 gate status 为 `block`，抛出 `QualityGateBlockedError`，不渲染完整报告。
5. 若 policy 为 `warn`，保留 gate result 并继续报告生成。
6. `off` 时跳过 gate，但 result 中记录 skipped reason。

不把 `QualityGateResult` 合并进 `ProgrammaticAuditResult`。P5-S1 是输入质量预检编排，程序审计仍负责模板结构、R=A+B-C、检查清单与最终判断一致性。

### P5-S1c: CLI integration

扩展 `fund_agent/ui/cli.py`：

- 将新增参数映射到 `FundAnalysisRequest`。
- block 失败时输出清晰错误并非零退出。
- warn / not-run / skipped summary 写 stderr，避免污染 stdout report。

### P5-S1d: Documentation and tests

测试覆盖：

- Service 层：`block` policy 阻断报告且 extractor 只调用一次。
- Service 层：`block` policy 抛出结构化 `QualityGateBlockedError`，异常携带 gate result 和 artifact 路径。
- Service 层：`warn` policy 在 gate block 时继续返回报告并携带 gate result。
- Service 层：`off` policy 不运行 gate。
- Service 层：基金不在 source CSV 时返回 not-run reason，不伪造 App 类别。
- Service/Capability 层：连续两次默认运行生成不同 `quality_gate_run_id` / 输出目录，或显式目录覆盖行为被清楚测试。
- CLI 层：新增参数显式传入 Service。
- CLI 层：block 时非零退出、stdout 不输出完整报告、stderr 包含 gate status / issue count / artifact paths。
- Capability 层：bundle-to-gate adapter 复用 `build_snapshot_records(...)` 并输出 `score.json` / `quality_gate.json`。

文档同步：

- `README.md`：更新 `fund-analysis analyze` 成功路径和新增 gate 参数。
- `fund_agent/README.md`：说明 Service 编排 quality gate，但规则仍在 Capability。
- `fund_agent/fund/README.md`：说明 bundle-to-gate adapter 与 P4 score/gate 契约。
- `tests/README.md`：补充 P5-S1 测试分层。

## Non-goals

P5-S1 不做：

- 不补齐 FQ4/FQ5 或 App 类别冲突新规则；这些属于 P5-S2。
- 不扩大 correctness denominator；属于 P5-S3。
- 不修 `share_change` 多份额列选择；属于 P5-S5。
- 不接入 LLM 审计或 Evidence Confirm。
- 不把 quality gate 逻辑放进 UI 或程序审计模块。

## Acceptance Criteria

P5-S1 implementation 通过条件：

- `fund-analysis analyze` 默认不再静默绕过 quality gate；运行、跳过或不可用都必须显式可见。
- 对精选基金池中可构造 score 的基金，`quality_gate_policy=block` 能阻断 `block` 状态报告输出。
- 单次 `analyze` 不重复抽取同一基金年报。
- block 状态通过结构化异常传递，CLI 可展示 gate artifact path，而不是只展示普通错误字符串。
- 默认质量产物目录不会覆盖上一轮自动运行。
- Service / CLI / Capability 分层符合 `docs/design.md` 与 AGENTS 模块边界。
- 新增/更新测试通过，且不依赖真实网络或 PDF。

## Review Questions

Plan review 重点检查：

1. 默认 `quality_gate_policy="block"` 是否过严；若 reviewer 认为会破坏任意基金分析入口，需提出不静默绕过的替代默认策略。
2. Adapter 生成中间 `score.json` 再调用 `run_quality_gate(...)` 是否保持了 P4 “quality gate 只消费 score.json” 契约。
3. `quality_gate_result` 不合并进 `ProgrammaticAuditResult` 的边界是否正确。
4. prerequisites unavailable 时继续报告但显式 not-run，是否足够保护用户。

## Gate Decision

当前 gate：`P5-S1 quality gate integration plan drafted`

Plan review fix: accepted controller findings from `docs/reviews/p5-s1-plan-review-controller-20260520.md`:

- `P5S1-PR-1`: added structured `QualityGateBlockedError` contract.
- `P5S1-PR-2`: added `quality_gate_run_id` and non-overwriting default output directory requirement.

下一 gate：`P5-S1 plan re-review`
