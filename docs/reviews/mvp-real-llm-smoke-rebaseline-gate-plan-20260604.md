# MVP Real LLM Smoke Re-baseline Gate Plan

## 1. Gate Objective And Classification

Gate：`MVP typed-template-to-agent report generation stabilization phase / Gate 2 Real LLM smoke re-baseline gate`

目标：规划如何在不改变 provider defaults/runtime、不放松 fail-closed/no-fallback/stdout 语义的前提下，重新建立真实 LLM smoke baseline 的直接证据。这个 gate 只重新建立 evidence protocol 和 review/acceptance 规则；本 plan 阶段不运行真实 LLM smoke、不检查 secret、不调用 provider、不修改 source/test/config/runtime 行为。

分类：`heavy`。

理由：真实 provider smoke baseline 会影响后续 chapter acceptance calibration、provider runtime residual 分类和 gate sequencing。它触及 provider-backed `--use-llm` fail-closed 证据、stdout 安全语义、质量门控语义、Service/Host/Agent 边界和未来 calibration 入口。按 `AGENTS.md`，涉及公共契约、质量门控语义、Host/Agent/provider 外部状态或 release/readiness 相邻风险时必须选择 `heavy`。本 gate 必须有完整 verifier matrix、两份独立 plan review、controller judgment、后续 evidence 直接证据、evidence review、controller judgment 和 accepted local checkpoint；不得用历史日志或间接 review 代替真实 smoke 的当前直接证据。

## 2. Current Facts From Design And Control

直接真源：

- `AGENTS.md` 是规则真源；`docs/design.md` 是设计真源；`docs/implementation-control.md` 是控制真源；`docs/current-startup-packet.md` 是短启动入口。
- `Template truth validation gate` 已 accepted locally at checkpoint `c907258`，control sync checkpoint `e11f5a3`。上一 gate 直接证据 A1-A8 全部 PASS，DS/MiMo plan review 和 validation evidence review 均 PASS，controller judgment accepted。
- `docs/fund-analysis-template-draft.md` canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` 已 validated 为 authored Fund template contract truth source；`contracts.py` 和 `typed_contracts.py` 从同一 JSON 投影/验证；same-source consumers 覆盖 `EvidenceAvailability`、writer/auditor typed path、Service `ChapterOrchestrator` typed path 和 `chapter_contract_constraints.py`。
- public chapter ids 必须保持 `0-7`；Ch2 `performance / attribution / cost` 仍只能是第 2 章内部 typed subcontracts，不得成为公开章节。
- 当前 `fund-analysis analyze --use-llm` 是显式 opt-in provider-backed 路径：CLI 构造 Service-owned `FundLLMExecutionRequest` / `FundLLMExecutionContract`，经本地 Host runtime runner 调用 Service，Service 使用 `fund_agent/fund` writer/auditor primitives 和 openai-compatible HTTP clients。
- 当前 `--use-llm` 路径 fail-closed：missing/invalid config、provider construction failure、provider runtime failure、writer/auditor blocked、partial orchestration 或 final assembly incomplete 均失败关闭；incomplete result 不回退 deterministic；incomplete/Host failure 不向 stdout 输出半成品报告。
- typed incomplete artifact retention 已实现：typed incomplete `analyze --use-llm` run 写入 local ignored `reports/llm-runs/` 诊断 artifact；artifact 写入失败只输出安全 warning，不改变原 fail-closed 退出。
- LLM progress/timeout UX 已实现：只向 stderr 输出安全 progress/stage/timeout 摘要；不输出 prompt、draft、raw provider response、API key、Authorization header 或 base URL secret。
- provider runtime timeout residual 仍存在。当前 control truth 记录历史 accepted provider-runtime 证据：`006597 / 2024 --use-llm` 曾保持 exit `1`、stdout empty、no deterministic fallback、`orchestration_status=partial`、`final_assembly_status=incomplete`，并显示 provider timeout / prompt_contract 等 residual。该历史记录只能作为背景，不能替代本 gate 的当前真实 smoke 直接证据。
- provider runtime budget calibration 只有 accepted plan/evidence residual，不代表 provider budget/default/runtime 行为已改变。不得在本 gate 调整 timeout、attempt、backoff、model、endpoint、provider default 或 runtime plan。
- Route C 是 accepted MVP LLM report generation route；Agent runner/tool-loop/ToolRegistry/ToolTrace、multi-year annual evidence runtime、score-loop、golden/readiness、PR/push/release 均不是当前实现范围。
- 生产年报 PDF 访问必须经过 `FundDocumentRepository`；Service、UI、Host、renderer、quality gate 不得直接调用具体来源、PDF cache 或下载 helper。

## 3. Explicit Non-goals

- 不改变 provider default、provider budget、timeout default、attempt/backoff default、endpoint、model、provider construction、runtime plan 或 provider factory。
- 不在 plan 阶段运行 live smoke、检查 secret、调用 provider、做 provider readiness probe 或 PASS-only live probe。
- 不做 Agent runtime implementation、Host durable runtime、tool-loop、ToolRegistry、ToolTrace、multi-year runtime、score-loop、`chapter_generation_score`、golden/readiness、snapshot refresh、fixture promotion、strict correctness rerun、release readiness、PR、push 或 release。
- 不修改 source、test、config、runtime behavior、模板文档、design/control/startup 文档或 README；本 plan 只允许写本 artifact。
- 不放松 auditor、programmatic blockers、quality gate、fail-closed、no deterministic fallback、stdout empty on incomplete、safe stderr 或 redaction 语义。
- 不让 incomplete LLM result 回退 deterministic。
- 不向 stdout 输出半成品报告；stdout 只能在 final accepted report 时输出。
- 不直接读取 PDF/cache/source helper；生产年报访问必须继续通过 `FundDocumentRepository`。
- 不把显式参数塞进 `extra_payload`。
- 不直接依赖 `dayu-agent` / `dayu.host` / `dayu.engine`。
- 不把旧日志、旧 retained run、旧 aggregate review 或 historical control note 当作本 gate smoke accepted 证据。

## 4. Verifier Matrix

| Acceptance criterion | Direct evidence required | Proposed validation command / artifact | Blocker vs residual | Accepted 后 next entry point |
|---|---|---|---|---|
| A1. Plan scope and forbidden-scope safety | Plan 明确 heavy 分类、当前事实、non-goals、stop conditions，且不授权 live provider in plan | 本 artifact + DS/MiMo plan reviews + controller judgment | 任何 provider/default/runtime/live execution 被夹带为 blocker | 若 pass，进入后续 evidence execution；仍不进入 calibration |
| A2. Env/config presence preflight is secret-safe | 后续 evidence step 只记录 presence/absence 和变量名，不输出 API key、base URL 值、Authorization header、raw config dump | Evidence artifact 记录 preflight command、exit code、presence booleans、redaction statement | env/config absent 分类为 `environment_blocked` 或 blocker；不能伪造 smoke | 若 presence pass，允许 exactly one reviewed smoke command |
| A3. Reviewed real-smoke command is singular and scoped | 只运行一条 reviewed command：`006597 / 2024 / --use-llm`，不加 provider budget/default/runtime override | Evidence artifact 记录完整命令、exit code、stdout/stderr 摘要、artifact path | 多命令 live probe、参数漂移、timeout/default override 均为 blocker | 若 run 完成，进入 stdout/artifact/fail-closed verification |
| A4. Incomplete fail-closed and stdout safety | 若 incomplete/blocked/timeout：exit non-zero，stdout empty，stderr 只含 safe summary，retained artifact path 存在，不回退 deterministic | Smoke command output + retained `reports/llm-runs/` manifest/summary/chapter artifacts | stdout 半成品、exit 0 on incomplete、deterministic fallback、artifact 缺失均为 blocker；artifact write warning 可按现有语义分类 residual 但必须保留 fail-closed evidence | 若 pass，进入 diagnostics/redaction verification |
| A5. Accepted report safety if smoke succeeds | 若 accepted：exit 0，stdout 是完整 8 章 final report，章节 ids `0-7`，quality gate/final assembly accepted，stderr 无 secret | Smoke stdout/stderr + optional retained evidence summary；不得把 accepted report 写入 incomplete artifact | 缺章、Ch2 public split、quality gate bypass、stdout 不完整均为 blocker | 若 accepted，进入 evidence review；不得直接 promotion/golden/readiness |
| A6. Safe diagnostic matrix and no secret leakage | Evidence 记录 orchestration/final assembly status、per-chapter matrix、first_failed、failure_category/subcategory、runtime diagnostics allowlist；不含 prompt、draft、raw provider response、raw audit response、API key、Authorization、base URL value | Evidence artifact + secret/redaction scan command summaries | 任何 secret/raw provider/prompt 泄漏为 blocker；diagnostic wording polish 可为 residual | 若 pass，进入 review |
| A7. Direct evidence integrity | Evidence 记录 git branch/status/diff、command list、pre/post allowed file changes、artifact path；不依赖旧日志 | `git branch --show-current`、`git status --short`、`git diff --name-only` summaries in evidence | source/test/config/runtime behavior diff、unreviewed artifact promotion、旧日志替代为 blocker | 若 pass，进入 controller judgment |
| A8. Provider timeout/block classification preserves current semantics | 如果 provider timeout/block 发生，保留 fail-closed direct evidence，不修改 timeout/default/budget，不扩大 repair budget，不改 provider | Smoke result + retained artifact + failure category matrix | 修改 timeout/default 来追求 pass、把 timeout 误报 accepted、伪造 smoke 为 blocker | 若 pass with blocked residual，next entry 是 residual classification / calibration planning，不是 runtime change |
| A9. Boundary guardrails | Evidence 不新增 dayu runtime 依赖、不绕过 FundDocumentRepository、不直接读 PDF/cache/source helper、不使用 `extra_payload` 业务参数 | Forbidden-scope checklist + git diff integrity | 任一边界绕过为 blocker | 若 pass，Real LLM smoke re-baseline evidence execution 可进入 independent review |

## 5. Proposed Real-smoke Evidence Protocol

本节只规划后续 evidence step；本 plan 阶段禁止运行这些 live/provider 命令。

### 5.1 Preflight: env/config presence without secrets

后续 evidence owner 必须先执行 secret-safe presence preflight，只能输出布尔 presence 和变量名，不得输出 API key 值、base URL 值、Authorization header、完整 config dump 或 shell environment。

建议 preflight 语义：

- 检查 required env presence：`FUND_AGENT_LLM_PROVIDER`、`FUND_AGENT_LLM_MODEL`、`FUND_AGENT_LLM_BASE_URL`。
- 解析 key env var name：`FUND_AGENT_LLM_API_KEY_ENV_VAR` 若存在则只输出该变量名；缺省只输出 `FUND_AGENT_LLM_API_KEY` 这个变量名。
- 检查 key env var value 是否 present；只输出 `api_key_present=true/false`。
- optional runtime env 只输出是否 explicitly set：`FUND_AGENT_LLM_TIMEOUT_SECONDS`、`FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS`、`FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS`、`FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS`、`FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS`、`FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS`、`FUND_AGENT_LLM_MAX_OUTPUT_CHARS`。
- 不校验 endpoint 可达性，不做 HTTP request，不调用 provider，不打印 base URL。

如果 required env/config absent，evidence 必须分类为 `environment_blocked` 或 controller-defined blocker，并停止 live smoke。不得伪造 smoke、不得用历史 retained artifact 替代、不得修改 provider defaults/runtime 来补足环境。

### 5.2 Exactly one reviewed smoke command

若 preflight presence pass，后续 evidence step 只允许运行一条 reviewed command：

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

约束：

- 不添加 timeout、attempt、backoff、model、endpoint、provider、max-output、repair-budget 或 prompt/debug override。
- 不运行第二个基金、第二个年份、第二个 provider probe、PASS-only timing probe 或 chapter-only live command。
- 不运行 deterministic fallback command 来补充 report。
- 可由 evidence owner 用 shell 重定向捕获 stdout/stderr 到本地临时 evidence 文件，但 artifact 中只能记录安全摘要；若捕获文件中含 secret/raw provider/prompt，必须作为 blocker 处理并不得提交。

必须记录：

- command、exit code。
- stdout 是否 empty；若非 empty，说明是否为 accepted full report。incomplete/blocked/timeout 时 stdout 必须 empty。
- stderr safe summary：progress、terminal summary、first_failed、chapter matrix、retained artifact path；不得包含 secret/base URL/raw prompt/raw response。
- retained artifact manifest path（incomplete 时必须存在，通常在 `reports/llm-runs/`）。
- final assembly status、orchestration status、per-chapter accepted/failed matrix、failure_category、failure_subcategory、safe runtime diagnostics allowlist。
- no deterministic fallback 证据：stderr/manifest/status 显示 incomplete/partial 没有生成 deterministic report；stdout empty；Service/CLI 退出码符合当前语义。

### 5.3 Git integrity and forbidden-scope checklist

后续 evidence artifact 必须记录：

- `git branch --show-current`
- `git status --short`
- `git diff --name-only`
- live command 前后对比：除允许的 evidence artifact 和 local ignored `reports/llm-runs/` retained artifact 外，不得出现 source/test/config/runtime behavior diff。
- forbidden-scope checklist：no provider default/runtime/budget change；no Agent runtime/multi-year/score-loop/golden/readiness/PR/push/release；no direct PDF/cache/source helper read；no `extra_payload` business parameters；no dayu production runtime dependency；public chapter ids remain `0-7`。

### 5.4 Secret scan requirements

后续 evidence owner 必须对 plan/evidence artifacts 和 retained artifact summaries 做 redaction scan，至少覆盖：

- API key patterns and canaries：`sk-`、`Authorization`、`Bearer `、`api_key` value-looking fields、configured key env var value。
- Provider internals that must not be serialized：raw prompt、draft、raw provider response、raw audit response、message body、full request headers。
- Base URL value：可以记录 `base_url_present=true`，不得记录实际 URL。
- Artifact manifest / summary / per-chapter files 必须符合现有 redaction policy；若 scan 命中不可解释内容，分类为 blocker。

### 5.5 Timeout/block outcome handling

如果 provider timeout、rate limit、network、malformed response、prompt_contract、programmatic audit block 或 final assembly incomplete 发生：

- 保留 fail-closed direct evidence。
- 不修改 timeout/default/budget/attempt/backoff。
- 不扩大 repair budget。
- 不改 prompt/provider/runtime 来追求 pass。
- 不把 incomplete artifact 或 historical retained run 写成 accepted smoke。
- 将结果按 `blocker`、`environment_blocked`、`provider_runtime_residual`、`content_contract_residual` 或 `code_contract_blocker` 分类，交由 controller judgment 裁决 next gate。

## 6. Proposed Local Non-live Validation Commands

这些命令只用于后续 plan/evidence harness safety 验证；本 plan 阶段不运行它们。它们不得替代真实 smoke 直接证据。

1. `uv run pytest tests/services/test_llm_run_artifacts.py -q`
   - 验证 incomplete artifact 写入、redaction、manifest/summary/chapter schema、accepted final report 不写 artifact、`.gitignore` 忽略 `reports/llm-runs/`。

2. `uv run pytest tests/ui/test_cli.py -q`
   - 验证 `--use-llm` missing/invalid config fail-closed、incomplete stdout empty、exit code、安全 stderr matrix、timeout fail-closed、progress 不污染 stdout、quality gate block/not-run 语义。

3. `uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q`
   - 验证 Service typed execution request、quality fail-closed policy、no deterministic fallback、runtime plan/request consistency、Host boundary generic fields。

4. `uv run pytest tests/services/test_chapter_orchestrator.py -q`
   - 验证 provider runtime 分类、per-chapter matrix、timeout diagnostics、writer/auditor fail-closed 分类。

5. `uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q`
   - 验证 writer incomplete response block、auditor parse failure fail-closed、programmatic blocker 不被 LLM auditor 覆盖。

6. `uv run pytest tests/services/test_llm_provider.py -q`
   - 验证 openai-compatible adapter 的 timeout/rate-limit/malformed/network 分类和 safe error behavior，使用 mock transport，不访问 live provider。

如任一 local non-live validation command 失败，后续 evidence owner 必须先分类为 harness blocker 或 unrelated test failure；不得绕过失败直接运行 live smoke，除非 controller 明确裁决该失败与 smoke evidence safety 无关。

## 7. Evidence Artifact Requirements For Execution Step

后续 Real LLM smoke re-baseline evidence artifact 必须包含：

- Scope、role、allowed write path、plan checkpoint、review artifacts、controller judgment artifact。
- Required context read list：`AGENTS.md`、`docs/implementation-control.md`、`docs/current-startup-packet.md`、`docs/design.md`、本 plan、plan reviews、plan controller judgment。
- Preflight results：presence-only，no secret/no base URL value。
- Local non-live validation command results（如 controller 要求运行）：完整命令、exit code、stdout/stderr 安全摘要。
- Exactly one reviewed live smoke command result：command、exit code、stdout empty/full-report 判定、stderr safe summary、retained artifact path、orchestration/final assembly status、chapter matrix、failure categories。
- Secret/redaction scan result。
- Git integrity pre/post：branch、status、diff。
- Forbidden-scope checklist。
- Acceptance criteria A1-A9 的 pass/fail/blocker/residual 判定。
- Root cause / residual 分类必须使用同源 direct evidence：命令输出、retained artifact safe fields、current git state；不得使用旧日志或间接证据。

## 8. Review Handoff Expectations

本 plan 需要两份独立 plan review：

- AgentDS：重点审查 verifier matrix、preflight/no-secret 协议、direct evidence 要求、blocker/residual 分类、stop conditions 是否充分，是否误把历史 retained run 当作 direct evidence。
- AgentMiMo：重点审查 smoke command 是否 singular/scoped、是否夹带 provider default/runtime/budget change、是否保持 fail-closed/no-fallback/stdout empty、是否覆盖 artifact/redaction/git integrity/forbidden-scope checklist。

两份 review 都必须输出 `PASS / BLOCKED / NEEDS_FIX`，finding 必须绑定本 artifact 章节或 matrix row。controller 只能在两份 review 均无 blocking finding，或 blocking finding 经过 plan fix + re-review 关闭后，进入 plan judgment。

## 9. Accepted Checkpoint Requirements

Plan 阶段 accepted 必须具备：

- 本 plan artifact：`docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-20260604.md`。
- AgentDS 与 AgentMiMo 两份独立 plan review artifact。
- 如有 finding，必须有 plan fix artifact 和 re-review artifact；不得 conversation-only 关闭。
- Controller judgment artifact，逐条裁决 review findings，并显式说明本 plan 不授权 live smoke。
- Accepted local commit hash；commit 只能包含允许的 plan/review/controller artifacts，不得夹带 source/test/config/runtime behavior change。
- 不得用旧日志、旧 retained run、旧 aggregate review 或间接证据替代本 gate plan review/controller judgment。

Evidence execution 阶段 accepted 还必须额外具备：

- 当前 real-smoke evidence artifact，包含 A1-A9 直接证据。
- DS/MiMo 两份独立 evidence review artifact。
- Controller judgment，明确 all blockers resolved 或 residual owner assigned。
- Accepted local commit hash；commit 只包含 evidence/review/controller artifacts，不包含 source/test/config/runtime/provider default change。

## 10. Stop Conditions And Residual Owner Classification

### Hard stop / blocker

- plan 或 evidence 需要修改 source/test/config/runtime behavior、provider default/runtime/budget、timeout default、attempt/backoff default、model/endpoint/provider factory 才能推进。
- plan 阶段运行 live provider、real LLM smoke、secret check、provider readiness probe 或 external state command。
- env/config absent 但 evidence 仍尝试伪造 smoke 或使用历史 retained run 代替。
- live evidence 运行多于一条 reviewed smoke command，或加入 unreviewed runtime/provider overrides。
- incomplete/blocked/timeout 时 stdout 非空、exit 0、生成半成品报告或 deterministic fallback。
- retained artifact 泄漏 prompt、draft、raw provider response、raw audit response、API key、Authorization header 或 base URL value。
- provider timeout/block 发生后通过修改 default/runtime/budget 来追求 pass。
- public chapter ids 偏离 `0-7` 或 Ch2 internal subcontracts 被当作公开章节。
- 直接依赖 `dayu-agent` / `dayu.host` / `dayu.engine`，绕过 `FundDocumentRepository`，直接读 PDF/cache/source helper，或通过 `extra_payload` 传递业务参数。
- 使用旧日志、旧 review、旧 retained artifact 作为当前 smoke accepted 证据。
- 执行 golden/readiness、snapshot refresh、fixture promotion、strict correctness rerun、score-loop、Agent runtime、multi-year runtime、PR、push、release。

### Residual owners that may carry forward after direct evidence

- `environment_blocked`：controller / environment owner。缺 env/config 时停止 live smoke，保留 blocker evidence，不进入 calibration。
- `provider_runtime_residual`：future provider runtime calibration owner。timeout/rate limit/network 等必须保留 fail-closed evidence，不在本 gate 改 default。
- `content_contract_residual`：future chapter acceptance calibration owner。prompt_contract、audit_rule_too_strict、programmatic blocker 等需用 direct same-run evidence 分类。
- `code_contract_blocker`：implementation owner。若 current code 违反 fail-closed/stdout/artifact/redaction/boundary 语义，必须开 scoped repair gate。
- `secret_redaction_blocker`：security/evidence owner。任何 secret/raw payload 泄漏必须先清理证据路径并重做安全 evidence protocol。
- `Agent runtime / multi-year / score-loop`：future design/implementation gate owner；不得在本 gate 消化。
- `golden/readiness/release/PR`：future release gate owner；不得由 smoke baseline 自动推进。

## 11. Next Entry Point

若本 plan 经 DS/MiMo review、controller judgment 和 accepted local checkpoint 接受，下一入口是：

`Real LLM smoke re-baseline evidence execution`

进入该 evidence step 后仍只允许按本 plan 的 preflight 和 exactly-one reviewed smoke command 收集直接证据。不得进入 `Chapter acceptance calibration gate`，直到 Real LLM smoke re-baseline evidence、evidence reviews、controller judgment 和 accepted checkpoint 全部完成。若 evidence 结果是 fail-closed timeout/block，该结果本身可以成为 re-baseline evidence，但后续是否进入 calibration、provider runtime residual disposition 或 scoped repair gate，必须由 controller judgment 单独裁决。
