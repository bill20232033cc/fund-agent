# MVP Template Truth Validation Gate Plan

## 1. Gate Objective And Classification

Gate：`MVP typed-template-to-agent report generation stabilization phase / Gate 1 Template truth validation gate`

目标：只验证上一 accepted gate 形成的 typed template truth source 是否仍能作为现有 report generation typed path 的直接事实基础。验证范围限定为：

- `docs/fund-analysis-template-draft.md` 中唯一 canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` 是否仍是 authored Fund template contract truth source。
- `fund_agent/fund/template/contracts.py` 与 `fund_agent/fund/template/typed_contracts.py` 是否仍从同一 JSON 投影并 fail-closed 校验。
- same-source consumers 是否保持一致：`EvidenceAvailability`、Fund writer/auditor typed path、Service `ChapterOrchestrator` typed path、`chapter_contract_constraints.py` sidecar。
- 当前 default deterministic `analyze/checklist`、quality gate、provider defaults、golden/readiness、Agent runtime、multi-year runtime、score-loop 和 public chapter ids `0-7` 是否未被改变。

分类：`heavy`。

理由：本 gate 虽不实现代码，但验证对象是 typed template/audit/evidence contract 的事实基础，影响未来 public template contract、programmatic auditor fail-closed 语义、report generation typed path 和后续 Agent migration 的输入边界。按 `AGENTS.md`，涉及公共契约、质量门控语义、Agent/Host 边界或不确定高影响范围时必须选择 `heavy`。本 gate 必须有完整 verifier matrix、两份独立 plan review、controller judgment、accepted local commit hash 和明确 residual owner；不得用旧日志或间接 review 代替当前直接证据。

## 2. Current Facts From Control And Design

直接真源：

- `AGENTS.md` 是最高执行规则真源；设计真源是 `docs/design.md`；控制真源是 `docs/implementation-control.md`；短启动入口是 `docs/current-startup-packet.md`。
- `docs/implementation-control.md` 与 `docs/current-startup-packet.md` 均记录上一 gate `MVP typed template truth-source replacement gate` 已 accepted locally，aggregate checkpoint `115b075`。
- `docs/design.md` 记录当前 typed template truth-source replacement 已成为代码事实：canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` 是 authored template contract truth source；`contracts.py` 投影 untyped manifest；`typed_contracts.py` 投影 typed dataclasses；当前 deterministic renderer/checklist/analyze、Agent runtime、multi-year runtime、provider/runtime defaults、score-loop、golden/readiness 和 public chapter ids `0-7` 未改变。

当前代码事实：

- `fund_agent/fund/template/contracts.py` 的模块说明和 loader 表明：契约内容来自 `docs/fund-analysis-template-draft.md` 中唯一 `TEMPLATE_CONTRACT_MANIFEST_JSON` 区块；`load_template_contract_manifest()` 走 `_load_template_contract_manifest_from_path()`，解析 JSON 后投影 `TemplateContractManifest`；`validate_template_contract_manifest()` 要求 8 章且章节 id 连续覆盖 `0..7`。
- `contracts.py` 的 parser 对缺失、重复、空 block、非法 JSON、非 object、未知顶层字段和 `public_chapter_ids` 非 `[0,1,2,3,4,5,6,7]` fail-closed。
- `fund_agent/fund/template/typed_contracts.py` 的模块说明表明它只把同一模板 JSON 投影为 typed dataclasses；`load_typed_template_contract_manifest(source_manifest=None)` 只把 `source_manifest` 用作 compatibility validation，stale/different 输入 fail-closed；typed validation 要求 `typed_chapter_contract.v1`、public chapter ids `0-7`、Ch2 internal subcontracts 不成为公开章节、`audit_focus` 闭集且 semantic-only。
- `fund_agent/fund/evidence_availability.py` 的模块说明和类型定义表明 `EvidenceAvailability` 只从 same-source `ChapterFactProjection` / facts / anchors / missing reasons / typed requirement ids 派生，不读取 repository、PDF/cache/source helper、Service、Host、provider、retained report、文件系统、环境变量或 dayu runtime。
- `fund_agent/fund/chapter_writer.py` typed required-output path 在存在 typed required output items 时强制要求显式 `EvidenceAvailability`，按 `when_evidence_missing` 执行 `render_evidence_gap`、`render_minimum_verification_question`、`delete_if_not_applicable` 或 `block`，缺 mapping 或缺 behavior 时 fail-closed。
- `fund_agent/fund/chapter_auditor.py` 用 `EvidenceAvailability` 执行 typed Ch3 evidence-conditional `must_not_cover`；未知 requirement 按 fail-closed 触发；`audit_focus` 只投影到 LLM bounded semantic audit request，未提供 typed contract 时走旧默认 focus，非法 focus fail-closed。
- `fund_agent/services/chapter_orchestrator.py` 的 typed path 由显式 `typed_template_path="typed_template_contract"` 选择；测试断言它在 typed path 派生 `EvidenceAvailability`，把 typed required-output items 传给 writer，把 typed chapter contract / `audit_focus` 传给 auditor，并保持正文章节独立执行。
- `fund_agent/fund/template/chapter_contract_constraints.py` 是 sidecar consumer：默认约束包裹 `load_template_contract_manifest()` 的 `must_answer` / `must_not_cover`，不建立平行章节真源。
- `tests/services/test_fund_analysis_service_llm.py` 与 `tests/ui/test_cli.py` 已有 focused assertions：deterministic analyze/checklist 不调用 LLM orchestrator；missing/partial/incomplete LLM result 不回退 deterministic；CLI incomplete stdout 为空、exit 1；LLM quality gate block/not-run 保持既有阻断语义。

当前未改变事实：

- default deterministic `fund-analysis analyze` 和 `fund-analysis checklist` 未改变。
- FQ0-FQ6 quality gate 未改变。
- provider budget/default/runtime 行为未改变。
- golden/readiness、snapshot refresh、promotion state 未改变。
- Agent runtime implementation、multi-year annual evidence runtime、score-loop 未实现且不在本 gate。
- public chapter ids 必须保持 `0-7`；Ch2 `performance / attribution / cost` 只能是第 2 章内部 typed subcontracts，不得成为公开章节。

## 3. Explicit Non-goals

- 不修改 source、tests、config、runtime behavior、README、design/control docs 或模板文档。
- 不运行 live provider、real LLM smoke、provider runtime/live probe、PASS-only live probe、endpoint/config/default change。
- 不做 provider budget/default、timeout default、runtime plan 或 provider factory 改动。
- 不做 Agent runtime implementation、Host/Agent durable runtime、tool-loop、ToolRegistry、ToolTrace、multi-year runtime、score-loop、chapter_generation_score、golden/readiness、snapshot refresh、promotion 或 release readiness。
- 不放松 auditor、programmatic blockers、quality gate、fail-closed、no deterministic fallback、stdout empty on incomplete 等语义。
- 不让 incomplete LLM result 回退 deterministic。
- 不向 stdout 输出半成品报告。
- 不直接读取生产 PDF/cache/source helper；生产年报访问仍只能经 `FundDocumentRepository`。
- 不把显式参数放进 `extra_payload`。
- 不直接依赖 `dayu-agent` / `dayu.host` / `dayu.engine`。
- 不创建 PR、不 push、不 commit，除非 controller 在本 plan review pass 后另行授权 accepted local commit。

## 4. Hard Stop Conditions

任一条件出现即停止 gate acceptance，不进入下一步：

- 当前验证需要改 source/test/config/runtime behavior 才能通过。
- 任一 proposed validation command 失败，且失败不能用当前 gate 外部环境问题解释。
- 发现 canonical JSON 不是唯一 authored truth source，或 `contracts.py` / `typed_contracts.py` 存在平行 code-authored template truth。
- `contracts.py` 与 `typed_contracts.py` 不再从同一 template JSON 投影，或 stale `source_manifest` 不 fail-closed。
- public chapter ids 偏离 `0-7`，或 Ch2 internal subcontracts 变成公开章节。
- `EvidenceAvailability`、writer/auditor/service typed path 或 `chapter_contract_constraints.py` 无法证明 same-source consumer regression。
- 任一验证暗示 deterministic analyze/checklist、quality gate、provider defaults、golden/readiness、Agent runtime、multi-year runtime 或 score-loop 被改变。
- 任一 LLM incomplete / partial path 输出 stdout report、回退 deterministic、或绕过 fail-closed。
- 验证计划要求 live provider、real key、promotion、golden readiness、snapshot refresh、release readiness、push 或 PR。
- 发现 Service/UI/Host/renderer/quality gate 直接读取 PDF/cache/source helper，或 Host/Agent/dayu 边界被绕过。

## 5. Verifier Matrix

| Acceptance criterion | Direct evidence required | Proposed validation command / artifact | Blocker vs residual | Accepted 后 next entry point |
|---|---|---|---|---|
| A1. canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` 是唯一 authored Fund template contract truth source | `docs/fund-analysis-template-draft.md` 只有一个 block；parser 缺失/重复/非法/未知字段 fail-closed；无 Python-authored stable text mapping truth | `uv run python -m fund_agent.fund.template.contracts --validate-template-doc`; `uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py -q` | 失败为 blocker；`lru_cache` 长进程 mutation masking 仅可作为 future cleanup residual，不能阻断当前一次性 validation | 若 pass，进入 A2/A3 validation；若 fail，开 scoped truth-source repair gate |
| A2. untyped 与 typed projections 来自同一 JSON 且 public ids 保持 `0-7` | `load_template_contract_manifest()` 与 `load_typed_template_contract_manifest()` 对同一 raw JSON 投影；stale `source_manifest` fail-closed；Ch2 subcontracts 仍是内部契约 | `uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py -q` | projection divergence、chapter id drift、Ch2 public split 均为 blocker；duplicate `TemplateLensRule` naming 属 future API cleanup residual | 若 pass，进入 same-source consumer validation |
| A3. `chapter_contract_constraints.py` 仍是 wrapper consumer，不形成平行 truth | 默认 constraints 的 `must_answer` / `must_not_cover` 等于 untyped manifest 与 typed text projection；overlay 只保留已接受 active/enhanced/bond sidecar scope | `uv run pytest tests/fund/template/test_chapter_contract_constraints.py -q` | wrapper divergence 为 blocker；sidecar overlay polish 可作为 future residual | 若 pass，进入 typed consumer validation |
| A4. `EvidenceAvailability` 从 same-source typed requirement ids 派生且不越界读取 | availability requirement ids 与 typed manifest 守卫一致；Ch2/Ch3 status、gap、anchor、internal subcontract 语义稳定；模块不读取 repository/PDF/cache/source helper/Service/Host/provider/dayu | `uv run pytest tests/fund/test_evidence_availability.py -q` | requirement id drift、unknown id 不 fail-closed、越界依赖均为 blocker；single-year Ch3 availability/multi-year 年份层级是 future multi-year gate residual | 若 pass，进入 writer/auditor validation |
| A5. Fund writer/auditor typed path 保持 fail-closed 和 semantic-only focus | writer 缺 `EvidenceAvailability` 或缺 behavior fail-closed；Ch2 block 在 provider 前停止；Ch3 gap/minimum verification/delete behavior 稳定；programmatic Ch3 `must_not_cover` 独立于 `audit_focus`；invalid focus 不调用 client | `uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q` | writer/auditor 放松 block、缺证静默渲染、focus 关闭 programmatic blocker 均为 blocker；diagnostic wording polish 可为 residual | 若 pass，进入 Service typed path validation |
| A6. Service report generation typed path 直接消费 same-source contract inputs | `typed_template_path` 显式为 `typed_template_contract`；runtime plan/request/policy 一致；orchestrator 在 typed path 派生 availability、传 typed required outputs 和 `audit_focus`；body chapters independent；legacy path typed inputs inactive | `uv run pytest tests/services/test_chapter_orchestrator.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py -q` | typed path 未传 availability/focus、request/runtime mismatch、fallback allowed、quality fail-closed policy 放松均为 blocker；duplicated `TypedTemplatePathMode` literal 可为 future cleanup residual | 若 pass，进入 CLI/fail-closed validation |
| A7. deterministic defaults、quality gate、no fallback、empty stdout on incomplete 保持 unchanged | deterministic analyze/checklist 不调用 LLM orchestrator；missing/partial/incomplete LLM result 不回退 deterministic；CLI stdout 空且 exit 1；quality gate block/not-run 仍 exit 2 且 stderr structured | `uv run pytest tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q` | fallback、半成品 stdout、quality gate 语义漂移均为 blocker；stderr progress wording polish 可为 residual | 若 pass，controller 可收集 evidence 并做 gate judgment |
| A8. No forbidden scope entered | 命令不需要 live provider/key、不触发 promotion/golden/readiness/snapshot/release、不改 runtime | Evidence artifact must record command list and explicitly state no live provider / no promotion / no external state | 任何 forbidden scope 命令执行为 blocker，需要 controller 裁决并可能重开 gate | 若 all pass，Template truth validation gate 可进入 controller acceptance；下一入口由 controller 明确授权后进入 typed-template-to-agent report generation stabilization 的下一 planning/implementation gate |

## 6. Proposed Validation Commands

这些命令是后续 validation/evidence agent 应运行并记录的命令。本 planning handoff 不运行它们，不把它们写成已通过证据。

1. `uv run python -m fund_agent.fund.template.contracts --validate-template-doc`
   - 覆盖 A1/A2：直接验证模板 doc canonical JSON 可被当前 untyped parser 读取、投影并 fail-closed 校验。

2. `uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py -q`
   - 覆盖 A1/A2：验证 untyped/typed projection、唯一 truth source、public chapter ids `0-7`、stale `source_manifest` fail-closed、typed JSON exact fields、closed `audit_focus`、Ch2 internal subcontract 边界。

3. `uv run pytest tests/fund/template/test_chapter_contract_constraints.py -q`
   - 覆盖 A3：验证 sidecar 默认约束包裹 current manifest，不重复章节 truth；active/enhanced/bond overlay 仍可解析。

4. `uv run pytest tests/fund/test_evidence_availability.py -q`
   - 覆盖 A4：验证 `EvidenceAvailability` 与 typed requirement ids / `ChapterFactProjection` same-source 派生一致，缺证/不可用/未复核/内部 subcontract 语义稳定。

5. `uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q`
   - 覆盖 A5：验证 typed writer required-output missing behavior、provider 前 fail-closed block、Ch3 typed `must_not_cover`、LLM `audit_focus` semantic-only 和 invalid focus fail-closed。

6. `uv run pytest tests/services/test_chapter_orchestrator.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py -q`
   - 覆盖 A6/A7：验证 Service explicit typed path wiring、request/runtime policy consistency、no deterministic fallback、quality fail-closed policy、deterministic analyze/checklist 不进入 LLM orchestrator。

7. `uv run pytest tests/ui/test_cli.py -q`
   - 覆盖 A7/A8：验证 CLI `--use-llm` incomplete/partial/provider construction failure stdout 为空、exit code/fail-closed、安全 stderr、quality gate block/not-run 语义；默认 analyze 不读取 LLM config/Host/artifact。

8. 可选 focused aggregate（当 controller 需要单条回归命令时）：

   ```bash
   uv run pytest \
     tests/fund/template/test_contracts.py \
     tests/fund/template/test_typed_contracts.py \
     tests/fund/template/test_chapter_contract_constraints.py \
     tests/fund/test_evidence_availability.py \
     tests/fund/test_chapter_writer.py \
     tests/fund/test_chapter_auditor.py \
     tests/services/test_chapter_orchestrator.py \
     tests/services/test_execution_contract.py \
     tests/services/test_fund_analysis_service_llm.py \
     tests/ui/test_cli.py \
     -q
   ```

禁止在本 gate 运行：

- live provider / real LLM smoke / PASS-only live probe。
- promotion、fixture promotion、golden readiness、snapshot refresh、strict correctness rerun、release readiness。
- PR/push/release 或任何外部状态变更。

## 7. Evidence Artifact Requirements For Validation Step

后续 validation/evidence artifact 必须记录：

- 当前 git branch 与 `git status --short`，并说明除验证 artifact 外没有 source/test/config/runtime behavior 改动。
- 每条 validation command 的完整命令、exit code、关键 stdout/stderr 摘要。
- 对每个 acceptance criterion A1-A8 的 pass/fail 判定和直接证据文件/测试名。
- 明确声明未运行 live provider、promotion、golden/readiness、snapshot refresh、release readiness、push、PR。
- 若失败，必须归类为 blocker 或 residual，并给出 root cause 同源证据；不得用间接日志或旧 review 结论替代。

## 8. Review Handoff Expectations

本 plan 需要两份独立 plan review：

- AgentDS：重点审查 verifier matrix 是否覆盖 direct facts、hard stop 是否充分、是否误把未来 Agent/multi-year/provider/score-loop 设计写成当前事实。
- AgentMiMo：重点审查命令矩阵是否足以验证 same-source consumer regression、no fallback/stdout/quality gate 语义，以及是否夹带 forbidden scope。

两份 review 都应输出 `PASS / BLOCKED / NEEDS_FIX`，并把 finding 绑定到本 artifact 的具体章节或 matrix row。controller 只能在两份 review 均无 blocking finding，或 blocking finding 已通过 plan fix + re-review 关闭后，进入 judgment。

## 9. Accepted Checkpoint Requirements

Template truth validation gate 的 plan 阶段 accepted 必须具备：

- 本 plan artifact 路径：`docs/reviews/mvp-template-truth-validation-gate-plan-20260604.md`。
- AgentDS 与 AgentMiMo 两份独立 plan review artifact。
- 如有 plan finding，必须有 plan fix artifact 和 re-review artifact，不能靠 conversation-only 口头关闭。
- Controller judgment artifact，逐条裁决 review findings，并用 `docs/design.md` / `docs/implementation-control.md` 当前事实说明为什么 accepted。
- Accepted local commit hash，且 commit 只包含允许的 plan/review/controller artifact；不得夹带 source/test/config/runtime behavior 改动。
- 不得使用旧日志、旧 aggregate review 或间接 evidence 代替本 gate 当前 plan review 与 controller judgment。

后续 validation/gate acceptance accepted 还必须额外具备：

- 当前 validation evidence artifact，包含 A1-A8 的直接命令结果。
- Controller judgment 明确 all blockers resolved / residual owner assigned。
- Accepted local commit hash。

## 10. Residual Owner Classification

可进入后续 gate 的 residual：

- `contracts.py` loader `lru_cache` 对长进程模板文档 mutation 的 masking 风险：future developer tooling/cache invalidation cleanup owner。
- `TemplateLensRule` untyped/typed duplicate class naming：future API cleanup owner。
- `TypedTemplatePathMode` literal duplication：future Service contract cleanup owner。
- 当前 Ch3 availability 单年、multi-year 年份层级、year-tier availability：future multi-year annual evidence implementation gate owner。
- Ch7 readiness metadata rendering polish：future final assembly/report polish owner。
- provider runtime timeout、provider budget/default、live PASS-only probe：future provider runtime calibration owner，不属于本 gate。
- Agent runner/tool-loop/ToolRegistry/ToolTrace migration：future Agent implementation gate owner，不属于本 gate。
- score-loop / `chapter_generation_score`：future score-loop gate owner，不属于本 gate。

必须阻断当前 gate 的 residual/blocker：

- 任何 template JSON 唯一 truth source、same-source projection、public chapter ids `0-7`、Ch2 internal subcontract 边界失败。
- `EvidenceAvailability`、writer/auditor/service typed path 或 sidecar 无法证明 same-source consumer regression。
- auditor/quality gate/fail-closed/no fallback/stdout empty 语义漂移。
- deterministic analyze/checklist、provider defaults、golden/readiness、Agent runtime、multi-year runtime、score-loop 出现行为变化。
- 需要改 source/test/config/runtime behavior 才能完成 validation。
- 任何直接 dayu runtime 依赖、PDF/cache/source helper 越界读取、`extra_payload` 业务参数传递。

