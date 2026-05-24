# Release Maintenance 004393 Quality Gate Plan Review - GLM - 2026-05-24

- Reviewed target: `docs/reviews/release-maintenance-004393-quality-gate-plan-20260524.md`
- Reviewer role: Gateflow plan review specialist B
- Timestamp source: local `date +%Y%m%d-%H%M%S` -> `20260524-081604`
- Scope: adversarial plan review only; no source, test, golden, README, or plan fix implemented.
- Truth sources checked: `AGENTS.md` user-provided rules, `docs/design.md` current four-layer sections, `docs/implementation-control.md` Startup Packet/current gate, handoff artifact `docs/reviews/release-maintenance-004393-quality-gate-plan-handoff-20260524-080633.md`, target plan, and current code facts.
- Conclusion: `fail`

## Assumptions Tested

- Annual-report evidence collection must stay inside `FundDocumentRepository` / `FundDataExtractor` and be executable by an implementation agent.
- `holdings_snapshot` status/source additions must not silently change snapshot/score/golden/public contract semantics.
- `share_change` A/C selection must be based on direct same-source evidence and must not rely on fund-code suffix.
- Benchmark normalization must be field-scoped and must not hide non-benchmark correctness mismatches.
- `turnover_rate` disclosure applicability must not be coupled to 004393 direct extraction fixes unless the scoring/gate contract is exact enough to implement safely.
- Validation must prove the quality gate still blocks real failures instead of being bypassed through denominator or status changes.

### PR-004393-1-未修复-高-S0/S5 给出的关键命令不可运行，导致证据和最终 smoke 不能作为 gate 证明

- **位置**: Direct Evidence Acquisition suggested command；S5 Required 004393 smoke。
- **问题类型**: 不可直接实施 / 测试缺口 / quality gate 验证缺口。
- **当前写法**: S0 建议使用一行 `uv run python -c '...; async def main(): ...; asyncio.run(main())'`；S5 smoke 使用 `uv run fund-analysis analyze 004393 --year 2024 --quality-gate-policy block`。
- **反例/失败场景**: Python 不允许在分号后的 simple-statement 位置定义 `async def`，该 `python -c` 会直接 `SyntaxError`，implementation agent 无法按 plan 采集 S0 证据。当前 CLI 的年报参数是 `--report-year`，不是 `--year`，S5 smoke 会因参数不存在而失败，implementation report 可能把 CLI 用法错误误判成质量门阻断或跳过 smoke。
- **为什么有问题**: 该 work unit 的核心要求是“先 direct evidence，再证明 quality gate 不是被绕过”。计划中的两条关键命令分别承担 S0 证据采集和 S5 最终验收，但它们本身不可执行，计划不满足 code-generation-ready。
- **直接证据**:
  - Target plan lines 77-81 给出 `python -c` 证据命令，包含 `; async def main():`。
  - 本地验证同形命令返回 `SyntaxError: invalid syntax`。
  - Target plan lines 539-543 使用 `--year 2024`。
  - `fund_agent/ui/cli.py:59-63` 当前 `analyze` 参数声明为 `typer.Option("--report-year", help="年报年份")`。
  - README 当前成功路径也使用 `fund-analysis analyze 004393 --report-year 2024`。
- **影响**: 实施 Agent 可能无法取得同源证据；或者把无法运行的 smoke 当成环境问题跳过，导致 plan 的 final validation 不能证明 004393 root cause 已修复且质量门未被绕过。
- **建议改法和验证点**: 将 S0 改成可运行的脚本文件或 `python -c` 中使用 `asyncio.run(FundDocumentRepository().load_annual_report(...))` 的合法表达式；S5 smoke 改为当前真实 CLI 参数 `--report-year 2024`。plan review 后应要求 implementation report 粘贴实际命令、退出码和 gate issue 分类。
- **修复风险（低/中/高）**: 低。
- **严重程度（低/中/高/严重）**: 高。

### PR-004393-2-未修复-高-`holdings_snapshot` 状态/source 契约不足，可能把“只有行业分布”误计为完整 P1 覆盖

- **位置**: `holdings_snapshot` Schema decision；S2 exact changes/tests；Residual Risks。
- **问题类型**: 契约缺失 / public contract 风险 / quality gate 验证缺口。
- **当前写法**: plan 允许新增可选 `top_holdings_status` / `industry_distribution_status`，同时写明“`holdings_snapshot` should be `direct` if either stock holdings or industry distribution is extracted”；测试只要求“Industry distribution alone does not fabricate `top_holdings`”，但没有要求 snapshot/score/gate 把 stock holdings 缺失继续暴露为缺口。
- **反例/失败场景**: 某基金 §8 只有行业分布，没有前十大或 all-stock details。按 plan，extractor 可以返回 `extraction_mode="direct"`、`value` 中只有行业分布和 `top_holdings_status="missing"`。当前 snapshot 只按字段级 `extraction_mode != missing` 和 `_has_present_value(value)` 设置 `value_present=True`，score/gate 只看到 `holdings_snapshot` 已覆盖，不会理解嵌套 `top_holdings_status=missing`。结果是 P1 `holdings_snapshot` 从 missing 变成 pass，质量门被“状态塞进 value”绕过。
- **为什么有问题**: 用户特别要求检查新增 status/source keys 是否破坏 snapshot/score/golden/public contract。当前 plan 没有把嵌套状态如何进入 snapshot schema、score denominator、FQ issue 或 golden 可比边界说清楚，implementation agent 只能自由发挥。
- **直接证据**:
  - Target plan lines 190-194 把 status/source keys 定义为 optional/additive。
  - Target plan lines 196-201 的测试没有要求 score/gate 对 `top_holdings_status=missing` 产生可观察结果。
  - Target plan lines 394-395 只说“Preserve or explicitly extend holdings output keys”。
  - `fund_agent/fund/extraction_snapshot.py:847-852` 字段级 `value_present` 只由 extraction mode 和非空 value 决定。
  - `fund_agent/fund/extraction_score.py:1260-1263`、`1326-1358` 缺失率和 P0/P1 missing fields 只看字段级 `value_present`。
  - `fund_agent/fund/quality_gate.py:420-471` 当前 FQ0/FQ issue schema 没有 holdings 子状态字段。
- **影响**: 质量门可能被非预期放宽；`holdings_snapshot` public shape 变得“看似兼容但语义漂移”；golden 继续 skip 时 correctness 也无法捕捉该退化。
- **建议改法和验证点**: plan 必须先裁决 `holdings_snapshot` 的最小公共契约：如果 stock holdings 缺失但行业分布存在，字段级 coverage 是否算 covered、是否需要单独 `fund_quality`/FQ0 info、是否要新增 snapshot 可机器读取的 metadata 字段，而不是只放在 nested value。测试应覆盖 industry-only fixture 经 `build_snapshot_records -> write_extraction_score_records -> run_quality_gate` 后的具体预期，避免只测 extractor。
- **修复风险（低/中/高）**: 中。
- **严重程度（低/中/高/严重）**: 高。

### PR-004393-3-未修复-中-`share_change` A/C 选择依赖的“当前基金 A 类身份”没有落到 S2 可用的数据边界

- **位置**: `share_change` Required behavior / Schema decision；S2 allowed files。
- **问题类型**: 不可直接实施 / 架构边界 / direct evidence 缺口。
- **当前写法**: plan 规定 strict share-class match 只能在“report/key/identity evidence directly identifies current fund as that share class”时使用，并说 004393 可用 `basic_identity.fund_name` 或 current report key/name，但 S2 allowed files 只包含 `holdings_share_change.py`、`extraction_score.py` 和测试。
- **反例/失败场景**: 当前 `extract_holdings_share_change(report)` 只接收 `ParsedAnnualReport`，而 `ParsedAnnualReport.key` 只有 fund code/year/document kind；`FundDataExtractor.extract()` 是先独立 `extract_profile(report)`，再独立 `extract_holdings_share_change(report)`，没有把 `basic_identity.fund_name` 传给 §10 extractor。implementation agent 若严格遵守 S2 allowed files，不能直接消费已抽取的 `basic_identity`；若为了通过 004393 回归，容易退回到 fund-code suffix、重扫 §2 文本但没有 plan 约束，或越界修改 `data_extractor.py`。
- **为什么有问题**: A/C 选择是本次重点风险之一。plan 已经正确禁止 fund-code suffix，但没有指定“直接 A 类证据”的可实施来源、提取 helper、失败条件和测试输入形状，导致最关键的 fail-closed 规则无法稳定实现。
- **直接证据**:
  - Target plan lines 215-220 允许 strict share-class match，但把证据来源写成 `basic_identity.fund_name` / report key/name 的条件式表述。
  - Target plan lines 384-390 的 S2 allowed files 不包含 `fund_agent/fund/data_extractor.py` 或 `profile.py`。
  - `fund_agent/fund/data_extractor.py:160-171` 当前独立调用 `extract_profile(report)`、`extract_performance(report)`、`extract_manager_ownership(report)`、`extract_holdings_share_change(report)`。
  - `fund_agent/fund/documents/models.py:437-448` `ParsedTable` 只有页码、表序号、headers、rows；表自身没有 section id 或基金名称。
- **影响**: 实施 Agent 可能扩大 scope 修改 extraction pipeline，或写出依赖 004393 parser artifact 的局部规则。更糟糕的是，A/C 选择若从 fund code 末位推断，会直接违反 plan 和用户要求。
- **建议改法和验证点**: plan 应在 S2 明确 class identity helper 的同源输入，例如在 `holdings_share_change.py` 内通过 `ParsedAnnualReport.get_section_text("§2")` / §2 profile table提取基金全名并判定是否显式以 A/C 类结尾；或调整 slice 边界，允许 data_extractor 传入 profile-derived identity，但这会扩大 scope，需 controller 裁决。测试必须覆盖：有 §2 A 类名称才选 A；只有 fund code 不选；§2 名称缺失或非 A/C fail closed。
- **修复风险（低/中/高）**: 中。
- **严重程度（低/中/高/严重）**: 中。

### PR-004393-4-未修复-高-S3 turnover applicability 与直接抽取修复仍然过度耦合，且 status/denominator/gate contract 不够具体

- **位置**: Goal/Success Signal；`turnover_rate` Disclosure Applicability；S3 slice；S5 prerequisites。
- **问题类型**: 过度耦合 / 契约缺失 / quality gate 风险 / public contract 风险。
- **当前写法**: plan 把 pre-2026 missing `turnover_rate` 建模为 disclosure applicability 纳入同一个 implementation plan；S3 允许修改 extractor、snapshot、score、quality_gate、integration；但只说“value or note must carry a machine-readable applicability status”和“Report applicability as info”，没有定义具体 JSON schema、snapshot 字段、score payload 字段或 FQ0/rule_result 形状。
- **反例/失败场景**: implementation agent 为了让 004393 不被 P1 缺失阻断，把 `turnover_rate` record 从 scorable records 移除，或者把 status 写进自由文本 `note` 后在 scoring 中字符串解析。这样短期能降低 missing-rate，但质量门没有稳定公开契约可审计，也可能影响所有 pre-2026 active funds 的 P1 denominator。若 `quality_gate.py` 只加 info issue，不同步 `fund_scores` / `fund_quality` 的 missing fields，FQ2/FQ4 仍可能触发；反之如果只改 score denominator，gate info 又不可见。
- **为什么有问题**: handoff 明确建议若 turnover applicability 大于抽取修复，应拆成 follow-up。当前 plan 虽写“Controller confirms whether to include S3”，但整体 success signal、S5 prerequisite 和 validation matrix 仍把它并入同一 root-cause work unit。该 slice 已经超出 004393 direct extraction，且对 public score/gate contract 的改动比 S1/S2 更大。
- **直接证据**:
  - Target plan lines 269-288 定义新 status vocabulary，但没有绑定到现有 dataclass/schema。
  - Target plan lines 431-441 允许 S3 横跨 `manager_ownership.py`、`extraction_snapshot.py`、`extraction_score.py`、`quality_gate.py`、`quality_gate_integration.py`。
  - Target plan lines 443-448 只描述行为，未定义 score JSON / gate JSON 的新字段。
  - Target plan lines 517-521 把 S3 完成或 defer 作为 S5 prerequisite。
  - `fund_agent/fund/extraction_snapshot.py:1008-1028` 当前 `SnapshotRecord` 没有 applicability/status 字段，只有 `note`。
  - `fund_agent/fund/extraction_score.py:1223-1283` 和 `1326-1358` 当前 denominator/missing fields 只消费 `value_present`。
  - `fund_agent/fund/quality_gate.py:432-471` 现有 info issue 结构主要服务 correctness coverage，没有通用 applicability payload。
- **影响**: 质量门可能被 denominator 改动隐式绕过；implementation diff 可能跨 extractor/snapshot/score/gate/integration 大范围漂移；后续 reviewer 难以判断“004393 修好了”还是“P1 turnover 被全局降权了”。
- **建议改法和验证点**: 将 S3 从本 work unit 的 code-generation-ready 范围中拆出，至少在 S1/S2 通过后单独 plan-review。若必须保留，plan 需先定义精确契约：status 位于 `turnover_rate.value["applicability_status"]` 还是 snapshot 顶层、score JSON 如何记录 excluded denominator、quality gate 的 FQ0/rule_result 字段名、unknown/2026+ 如何 fail closed，并用 integration test 证明 FQ2/FQ4 没被非目标字段静默放宽。
- **修复风险（低/中/高）**: 高。
- **严重程度（低/中/高/严重）**: 高。

## Open Questions

- `holdings_snapshot` 的质量门语义到底是“任一 §8 持仓相关披露即 covered”，还是“stock holdings 与 industry distribution 分别有子状态、其中 stock holdings 缺失仍可见”？当前 plan 必须二选一并写入 snapshot/score/gate 契约。
- S2 是否允许修改 `FundDataExtractor` 以把 profile identity 传入 share-change extractor？若不允许，plan 必须指定在 `holdings_share_change.py` 内可用的同源 A/C identity extraction route。
- S3 是否应从本 work unit 拆出？当前 plan 的 controller decision 只写在后置问题里，但 implementation slices 和 S5 已经把它纳入验收路径。

## Residual Risks

- Benchmark normalization 方向基本正确：target plan 将 normalization 限定在 `benchmark.benchmark_name` / `benchmark.benchmark_text`，并要求非 benchmark 字段不应用该规则。剩余风险是实现时 `_normalize_comparable_value(value)` 需要变成 field-aware，review 时应检查没有全局删除中文空格。
- `fee_schedule` §7.4.10.2 fallback 和 `basic_identity` comparable fields 的计划相对可实施，但仍依赖 S0 direct evidence；在 S0 命令修正前不能进入代码实现。
- Real 004393 smoke 可能仍受网络/cache/精选池/golden 影响；implementation report 必须区分 CLI 参数错误、repository unavailable、真实 gate block、以及本 plan 声称修复的 root cause。

## Final Plan Review Conclusion

`fail`

该 plan 有正确的总体方向，也明确禁止了 direct PDF/cache 访问、fund-code suffix inference、turnover proxy 和 Host/Agent scope creep。但它还不能安全交给 implementation agent：关键证据/验收命令不可运行，`holdings_snapshot` 和 `turnover_rate` 的 status/schema/score/gate 契约不足，`share_change` 的 A/C direct evidence 在当前 S2 边界下不可直接消费。建议先修正上述四个 finding，再进入 implementation。
