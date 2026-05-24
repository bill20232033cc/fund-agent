# Release Maintenance 004393 Quality Gate Plan Review - MiMo - 2026-05-24

## Reviewed Target And Scope

- Reviewed target: `docs/reviews/release-maintenance-004393-quality-gate-plan-20260524.md`
- Handoff reviewed: `docs/reviews/release-maintenance-004393-quality-gate-plan-handoff-20260524-080633.md`
- Review posture: adversarial plan review only; no implementation, no source/test/config/runtime/README/golden edits.
- Current truth used: `AGENTS.md`, current `docs/design.md` architecture/document repository sections, `docs/implementation-control.md` Startup Packet/current gate, target plan, and handoff artifact.
- Historical `docs/reviews/` and implementation-control archive six-layer/Application/Runtime/Engine wording were not used as current architecture truth.

## Assumptions Tested

- S0 evidence can be acquired through `FundDocumentRepository` / `FundDataExtractor` without direct PDF/cache/source-helper access.
- S1/S2 are narrow enough to implement without hidden schema or quality-gate contract changes.
- S3 turnover applicability is sufficiently specified to include in the same work unit.
- S4 golden changes have enough authorization and row-level scope to be safe.
- The plan prevents 004393 hardcoding and derived turnover proxies.
- Tests prove failure paths, not just positive extraction.
- The plan preserves four-layer `UI -> Service -> Host -> Agent`, avoids Host/Agent placeholder packages, avoids `extra_payload`, and keeps production annual-report access inside the document repository boundary.

## Findings

### PR-A-未修复-[严重]-S0 证据获取入口不是可执行验收门

- **位置**: `Direct Evidence Acquisition` 与 `S0 - Evidence Artifact`
- **问题类型**: 不可直接实施 / 测试缺口 / 契约缺失
- **当前写法**: plan 要求 S0 先通过 `FundDocumentRepository.load_annual_report("004393", 2024, force_refresh=False)` 或 `FundDataExtractor.extract(...)` 记录同源证据，并给出一个 `uv run python -c 'import asyncio; ... async def main(): ...'` 的建议命令；S0 validation 只有 `git diff --check`。
- **反例/失败场景**: implementation agent 直接复制建议命令时，`python -c` 中在分号后定义 `async def main()` 属于不可执行命令形态，S0 可能在第一步失败。即使 agent 手工改写命令，S0 的唯一 validation 仍只检查 markdown diff，不强制证明 repository load 成功、artifact 的每个候选事实都被逐项确认/否决、或 evidence path 与 source metadata/fallback/cache 状态被记录。
- **为什么有问题**: `AGENTS.md` 要求 root cause 逻辑/数据同源，数值判断必须可溯源；handoff 明确本 gate 不能实现代码，必须先通过 repository/extractor 接口确认直接证据。S0 是后续 S1-S4 的共同前提，如果证据命令本身不可执行或验收只看 `git diff --check`，implementation agent 会被迫临场重设计证据脚本，甚至可能在证据不完整时推进 source/golden 变更。
- **直接证据**:
  - plan lines 57-75 要求先记录直接同源观察。
  - plan lines 77-83 给出建议一行命令并要求报告命令/cache hit/path。
  - plan lines 316-324 把 S0 validation 降为 `git diff --check` 和 artifact existence。
  - `AGENTS.md` lines 46、50、52、62 要求 root cause 同源、文档仓库边界和数值可溯源。
- **影响**: 实施 Agent 可能无法执行 S0；也可能生成形式上存在但证据不完整的 artifact，导致后续 fee、benchmark、share_change、turnover applicability 和 golden 更新都建立在未验收事实上。
- **建议改法和验证点**:
  - 把 S0 命令改为实际可复制执行的形态，例如使用临时脚本文件或 `python -c` 内显式换行，不在分号后定义 `async def`。
  - S0 completion signal 增加逐项 checklist：repository/extractor 命令 exit code、document key、section/table locator、source metadata/fallback/cache status、每个候选 fact 的 `confirmed/rejected/blocked` 状态。
  - S0 validation 至少包含成功运行的 evidence acquisition command；`git diff --check` 只能作为附加格式检查。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 严重

### PR-B-未修复-[高]-S2 holdings schema/status 仍隐藏 quality-gate 语义破坏

- **位置**: `holdings_snapshot` contract、S2 expected assertions
- **问题类型**: 架构边界 / 契约缺失 / 隐藏 schema break / 测试缺口
- **当前写法**: plan 允许保持 `top_holdings` key，同时可添加 `top_holdings_status`、`industry_distribution_status` 等可选 status；又规定 “holdings snapshot should be `direct` if either stock holdings or industry distribution is extracted”。S2 测试允许 existing top-ten fixture “outputs status 或 remains compatible if status is absent”。
- **反例/失败场景**: 某基金 §8 只有行业分布、没有 top ten、也没有 all-stock details。按当前写法，`holdings_snapshot` 可以整体标记为 `direct`，同时 status 字段又可能因“兼容”被省略。quality gate / extraction_score 只看到 P1 字段 direct，无法区分“持仓明细缺失但行业分布存在”与“持仓明细已直接披露”，从而把原本应暴露的 stock holdings 缺口从 P1 denominator 或 issue 里隐藏。
- **为什么有问题**: handoff 要求决定 “all stock investment details” 是否作为 top-10 source，以及 industry continuation 如何处理；它不是要求行业分布单独满足 top-holdings 语义。`AGENTS.md` 要求证据可溯源且 root cause 同源；把 `holdings_snapshot` 的整体 direct 状态建立在任一子表存在上，会让 downstream gate 失去字段级 root cause。当前设计也把 `QualityGateResult` 作为 Agent quality gate → Service/UI 的契约，不能通过可选 metadata 让 gate 解释依赖变成隐式。
- **直接证据**:
  - plan lines 175-194 定义 holdings fallback 与可选 status/schema。
  - plan lines 196-201 的测试允许 status 缺席，同时只要求 industry distribution 不 fabricate `top_holdings`。
  - handoff lines 48-49 要求明确 all-stock details 和 industry continuation 的处理。
  - `docs/design.md` lines 120-125 把 `QualityGateResult` / structured bundle 作为跨边界契约。
- **影响**: S2 可能表面修复 004393，但引入一个更宽的 schema ambiguity：P1 coverage/gate 不再能稳定表达 top holdings direct / all-stock fallback / industry-only missing 的区别。后续 code review 只能看到兼容字段，难以判断是否弱化 quality gate。
- **建议改法和验证点**:
  - 在 plan 中固定最小 schema，而不是让 implementation 选择：例如 `top_holdings_status` 必须存在并参与 score/gate interpretation，取值至少覆盖 `direct_top_ten` / `direct_all_stock_details` / `missing`。
  - 明确 `holdings_snapshot.extraction_mode=direct` 不等于 `top_holdings_status!=missing`；score/gate 必须按子字段 status 计算或报告。
  - 增加 failure-path test：industry-only fixture 不应让 top holdings 子项被视为 direct；quality gate/score 输出必须保留可观察 issue 或 status。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 高

### PR-C-未修复-[高]-S3 turnover applicability 不是同一 implementation work unit 的 code-generation-ready slice

- **位置**: success signal、`turnover_rate Disclosure Applicability`、S3、S5
- **问题类型**: 范围漂移 / 切片过粗 / open question 未收敛 / 隐藏 schema break
- **当前写法**: plan 的 success signal 把 pre-2026 missing `turnover_rate` 建模为 disclosure applicability；S3 引入 5 个 status、改变 extraction/snapshot/score/quality_gate 多处语义，并要求 controller 决定是否同 work unit 纳入；S5 又要求 S3 completed 或 deferred with owner。
- **反例/失败场景**: implementation agent 接到“code-generation-ready plan”后，可以先做 S1/S2，但 004393 smoke 仍因 turnover missing block；也可以直接实现 S3，却要在 `manager_ownership.py`、`extraction_snapshot.py`、`extraction_score.py`、`quality_gate.py`、integration tests 间设计新 applicability schema、denominator 规则和 FQ0/info reporting。任何一种路径都会让 implementation agent 重新做 policy/schema 设计，而不是执行计划。
- **为什么有问题**: handoff lines 67-69 明确建议如果 turnover applicability 大于 extraction fixes，应拆成 follow-up Gateflow candidate。plan 自己也在 lines 426-429 要求 controller 决定是否包含 S3，说明 S3 不是已收敛 slice。并且 S3 改变 quality gate denominator 和 missing-field penalties，属于跨 scorer/gate contract 的行为变更，不应和 S1/S2 extractor root-cause 修复捆绑。
- **直接证据**:
  - plan lines 23-24 把 turnover applicability 放进 overall success。
  - plan lines 269-299 定义新的 status vocabulary 和 scoring/gate 行为。
  - plan lines 422-468 把 S3 作为可选但未决的实现 slice。
  - plan lines 517-520 要求 S5 依赖 S3 completed 或 deferred。
  - handoff lines 67-69 要求必要时把 turnover applicability 拆成 follow-up。
  - `docs/implementation-control.md` lines 180-185 把 004393 candidate 定义为 direct extraction root causes plus turnover-rate disclosure applicability，但强调先 plan-review、turnover_rate 不作为 direct extraction bug。
- **影响**: 计划交付边界不稳定。S1/S2 完成后可能仍不能达成 “fix 004393 gate block”；S3 如果一起做又会扩大到 policy/schema/gate redesign，增加 reviewer 难度并提高误把 turnover derived proxy 或 applicability loophole 当成 quality fix 的风险。
- **建议改法和验证点**:
  - 将当前 plan 明确收窄为 S0-S2 extraction/correctness plan，并把 S3 改为独立 follow-up Gateflow candidate；或在本 plan 内先完成单独 S3 plan-review/fix 再允许 implementation。
  - S5 expected smoke 必须分两套：S3 deferred 时只证明原 direct extraction/correctness blockers 不再出现，并把 turnover block 分类为 accepted deferred applicability；S3 included 时才要求 004393 不因 turnover missing block。
  - S3 独立计划需要固定 status 所属 schema、score denominator 规则、FQ0/info schema、unknown applicability fail-closed 行为和 real/golden interaction。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 高

### PR-D-未修复-[高]-S4 golden 更新授权和范围仍不够精确

- **位置**: `Golden decision` sections、S4、Blocking Questions
- **问题类型**: open question 未收敛 / 范围漂移 / 不可直接实施 / 测试缺口
- **当前写法**: S4 要求 controller explicit approval 后修改 golden markdown/json；具体变更包括 fee rows、benchmark semantic text decision、可选 turnover skipped applicability note、以及 “Add `holdings_snapshot` golden only if the plan review accepts it as a comparable golden field”。
- **反例/失败场景**: plan review 给出 pass 或 pass-with-risks 后，implementation agent 可能把这解读为 review 已接受 `holdings_snapshot` 成为 comparable golden field，从而新增 correctness oracle rows。或者 direct evidence 后 fee/benchmark golden 可以改，但 applicability-only skipped row 需要 builder semantics，plan 又允许“only if parser supports such notes”，这会把 strict builder scope 决策推给 implementation。
- **为什么有问题**: 本轮 handoff 是 planning only，不能实施 golden；当前 implementation-control Startup Packet 还强调添加未计划 golden rows 需要显式授权。S4 涉及 correctness oracle 真值，不是普通测试 fixture。plan 必须在 implementation 前固定“哪些 rows 允许改、由谁在何时授权、哪些 rows 明确不改”，不能让 plan review 或 implementation report 代替 controller/user 的 golden approval。
- **直接证据**:
  - plan lines 170-173 只对 fee rows 给出较明确 golden decision。
  - plan lines 258-261 把 benchmark golden 改动留给 direct evidence 后决定。
  - plan lines 470-511 定义 S4，但 holdings golden、turnover skipped note、builder semantics 仍是条件式。
  - plan lines 621-622 只说 controller 需要批准 golden changes 和 final benchmark semantic text。
  - handoff line 12 明确当前 gate 不实施 golden answers。
  - `docs/implementation-control.md` line 138 要求添加未计划 golden rows 仍需显式授权。
- **影响**: Golden oracle 可能被过度扩张，或者为让 004393 pass 而把 direct extraction、normalization、applicability 的未决事项混进 truth fixture。后续 review 很难区分真实披露修复与 correctness answer 被改宽。
- **建议改法和验证点**:
  - S4 必须拆成独立 controller approval gate，approval artifact 逐行列出允许修改的 fund/field/subfield/current value/new value/evidence anchor/build command。
  - 当前 plan review 不应被视为接受 `holdings_snapshot` golden expansion；若要纳入，应另有 explicit decision。
  - 明确本 work unit 默认只允许 fee rows 和经 evidence 确认的 benchmark semantic normalization；turnover applicability note 和 holdings golden expansion 默认 deferred，除非 controller 在 S4 前单独批准。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 高

## Open Questions

- S3 是否明确拆出为 follow-up Gateflow candidate？当前 plan 仍把它放在 success signal 与 S5 prerequisite 中。
- S4 的 controller approval 是否必须是 S1/S2/S0 evidence 后的新 artifact，而不是本 plan review 的通过结论？
- `holdings_snapshot` 的最小稳定 schema 是固定新增 status keys，还是只在 score/gate 内部处理子字段状态？当前 plan 让 implementation 选择，风险偏高。
- S0 evidence artifact 是否需要记录 `AnnualReportSourceMetadata.fallback_used` / source category / cache hit / document key，以证明没有绕过 repository boundary？

## Residual Risks And Suggested Tracking Destination

- Parser table shape variability remains a real risk even after semantic tests；应在 S2 implementation report 中记录 uncovered table shapes，并由 future extractor hardening backlog 跟踪。
- Benchmark whitespace normalization limited to benchmark fields is reasonable, but仍需在 `tests/fund/test_extraction_score.py` 固定非 benchmark 字段不归一化的 negative tests。
- Share-class selection using fund name suffix `A` can still overfit parser/report naming；S2 code review 必须检查没有 fund-code suffix inference，也没有只为 `004393` 的 literal branch。
- S0 evidence acquisition可能因本地 cache/network 状态不稳定而 blocked；应在 S0 artifact 记录 blocked cause，不允许 fallback 到 direct PDF/cache inspection。

## Final Conclusion

**fail**

当前 plan 已经正确保留了四层边界、FundDocumentRepository 边界、禁止 Host/Agent 占位包、禁止 `extra_payload`、禁止 direct PDF/cache/source helper、禁止 derived turnover proxy 等核心 guardrails。但它还不能作为完整 code-generation-ready implementation plan 交付：S0 evidence command/验收不够可执行，S2 holdings schema 存在隐藏 gate 语义破坏，S3 turnover applicability 仍是未收敛的跨 scorer/gate policy slice，S4 golden 授权和行级范围不够精确。

建议先修 plan：固定 S0 可执行证据门；收窄 S1/S2 schema；将 S3 拆出或做独立 plan-review；把 S4 改为 evidence 后的独立 controller-approved golden gate。
