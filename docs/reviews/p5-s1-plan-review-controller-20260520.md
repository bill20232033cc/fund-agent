# P5-S1 Plan Review Controller - 2026-05-20

## Reviewed Target

- Plan: `docs/reviews/p5-s1-quality-gate-integration-plan-20260520.md`
- Design truth: `docs/design.md`
- Control docs:
  - `docs/implementation-control.md`
  - `docs/implementation-control-p4.md`
- Code facts:
  - `fund_agent/services/fund_analysis_service.py`
  - `fund_agent/ui/cli.py`
  - `fund_agent/fund/extraction_snapshot.py`
  - `fund_agent/fund/extraction_score.py`
  - `fund_agent/fund/quality_gate.py`

## Assumptions Tested

- `analyze` integration can reuse the already extracted `StructuredFundDataBundle` without a second PDF/document extraction.
- Service can expose quality gate outcomes without moving fund-domain rules into UI.
- Blocking gate behavior can be reported to CLI without polluting report Markdown.
- Quality gate artifacts remain durable enough for audit/debugging across repeated runs.

## Findings

### P5S1-PR-1-未修复-高-block 路径缺少结构化失败契约

- **位置**: `P5-S1b: Service integration`、`P5-S1c: CLI integration`
- **问题类型**: 契约缺失 / 状态机漏洞 / 不可直接实施
- **当前写法**: plan 要求 `quality_gate_policy=block` 且 gate status 为 `block` 时，Service 抛出明确 `ValueError`，CLI “输出清晰错误并非零退出”。
- **反例/失败场景**: Capability adapter 已生成 `quality_gate.json`、`quality_gate.md` 和多条 block issues，但 Service 只抛普通 `ValueError`。CLI 当前统一捕获 `Exception` 并输出 `分析失败：{exc}`，因此无法稳定展示 gate status、issue 数、gate artifact 路径，也无法保证 stdout 不输出报告之外的同时给 stderr 足够诊断信息。
- **为什么有问题**: P5-S1 的目标是“运行、跳过或不可用都必须显式可见”。普通异常字符串不是稳定公共契约，implementation agent 很容易把 gate 结果压扁成不可解析文本，导致用户和测试只能匹配脆弱错误文案。
- **直接证据**:
  - `fund_agent/ui/cli.py` 当前 `analyze` 捕获 `Exception` 后只输出 `分析失败：{exc}`。
  - plan 的 Result fields 只覆盖成功返回的 `FundAnalysisResult`；block 时 Service 抛异常，未定义携带 `QualityGateResult` 的异常或 blocked result。
- **影响**: block 状态不可审计；CLI 无法可靠展示 gate artifact；测试只能断言错误字符串；后续 PR review 难以判断 “不静默绕过” 是否真实达成。
- **建议改法和验证点**: plan 应要求新增结构化阻断契约，例如 `QualityGateBlockedError`，至少携带 `QualityGateResult`、policy、human message；CLI 专门捕获该异常，把 status/issues/path 写 stderr 并以非零退出。测试必须断言 gate artifact path 和 issue count 出现在 stderr，stdout 不包含完整报告。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 高

### P5S1-PR-2-未修复-中-默认输出目录会覆盖质量产物

- **位置**: `P5-S1a: Capability adapter`
- **问题类型**: 数据覆盖 / 可观测性缺口 / 状态机漏洞
- **当前写法**: plan 建议默认输出目录为 `reports/quality-gate-runs/<fund_code>-<report_year>`。
- **反例/失败场景**: 用户连续两次运行 `fund-analysis analyze 004393 --report-year 2024`，第二次会覆盖第一次的 `score.json` / `quality_gate.json`。如果第一次 block、第二次 warn 或 not-run，控制台日志和磁盘 artifact 无法对应，debug 和回归比较都会混淆。
- **为什么有问题**: P4 质量闭环依赖 durable artifact。默认目录不带 run id 或时间戳，会让质量证据不可复盘，和 P4 snapshot 使用 `<run-id>` 输出目录的既有模式不一致。
- **直接证据**:
  - P4 snapshot 默认输出到 `reports/extraction-snapshots/<run-id>`。
  - plan 的默认目录示例未包含 run id、时间戳或 overwrite 语义。
- **影响**: 重复运行覆盖证据；失败追踪不可靠；review 或用户排查时可能引用到后一轮产物。
- **建议改法和验证点**: plan 应要求显式 `quality_gate_run_id` 或 Service 自动生成稳定 run id，默认目录使用 `reports/quality-gate-runs/<run-id>`；若用户提供 `quality_gate_output_dir`，需要明确是否允许覆盖。测试覆盖连续两次默认运行输出目录不同，或覆盖时有显式 opt-in。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

## Open Questions

- `quality_gate_policy="block"` 作为默认值是否对精选基金池以外的任意基金过严：当前 plan 通过 prerequisites unavailable 时 not-run 缓解，review 未将其列为 blocking finding，但 implementation 需要测试非精选基金路径。

## Residual Risks

- P5-S2 / P5-S3 仍需补齐 FQ4/FQ5 与 correctness denominator；不阻断 P5-S1，但必须继续在总控中追踪。

## Conclusion

`fail` until plan is patched.

当前计划方向符合架构边界，但 block 状态缺少结构化失败契约，默认输出目录也会覆盖质量证据。修复这两个 plan 层问题后，可进入 P5-S1 implementation handoff。
