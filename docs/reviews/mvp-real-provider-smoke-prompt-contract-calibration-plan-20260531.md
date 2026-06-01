# MVP real provider smoke prompt-contract calibration plan

日期：2026-05-31

角色：Gateflow planning specialist。本文只写 handoff-ready / code-generation-ready implementation plan，不启动完整 gateflow，不进入 implementation，不修改运行时代码，不 commit、不 push、不开 PR、不 merge。

## 1. Worker self-check

- Current gate / role：当前 gate 是 `MVP real provider smoke acceptance rerun with prompt-contract calibration`；我是 planning worker，不是 controller、implementation worker 或 reviewer。
- Source of truth：已读取 `AGENTS.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`、`docs/reviews/mvp-provider-runtime-timeout-hardening-controller-judgment-20260531.md`、`docs/reviews/mvp-provider-runtime-timeout-hardening-implementation-evidence-20260531.md` 和 `reports/mvp-local-acceptance/20260531-provider-timeout-hardening/` 脱敏 smoke 证据。
- Scope boundary：本 turn 只新增本计划 artifact；后续 implementation 只能在本文 allowed files/modules 内工作。
- Stop conditions：未发现需要 controller 先回答的 blocking open question；provider config/auth 已验证可用，不回退到 provider_config/provider_auth。
- Evidence hygiene：只引用脱敏摘要、章节状态矩阵和 stop reason；不得记录 API key、Authorization header、完整 prompt、完整 draft 或完整 provider response。
- Completion signal：本文可直接交给 implementation worker；若 plan review 通过，implementation worker 可按切片执行。

## 2. Handoff readiness

Status：handoff-ready。

Gate classification：heavy。原因是本 gate 会校准真实 LLM writer/auditor safety contract、failure taxonomy 和 smoke evidence 口径，影响 provider-backed `--use-llm` 的安全失败语义。分类不确定时按 `AGENTS.md` 选择更重一级。

## 3. Goal / motivation

目标：在 provider config/auth 已验证可用的前提下，校准真实模型输出与 writer/auditor contract，使：

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

更接近可接受的完整 0-7 章报告；若仍失败，必须把失败精确分类为可修复的最小下一入口。

动机：

- 当前 blocker 已不是 missing config、HTTP 401 或 provider auth。控制面记录 provider/auth 已通过，真实 smoke 已调用真实模型。
- 最新 controller CLI rerun：exit `1`、stdout empty、无 deterministic fallback，第 1 章 `llm_timeout`，第 2-6 章 `dependency_missing`，final assembly incomplete。
- controller supplemental service rerun 还观察到第 1 章 `llm_contract_violation`，说明 prompt/marker/line protocol 仍可能让真实模型偏离 contract。
- 本 gate 的核心不是放松审计，而是降低模型遵守 contract 的认知负担，并让所有失败按最小可修复入口分类。

## 4. Direct evidence

控制面证据：

- `docs/current-startup-packet.md`：当前 phase 为 `MVP real-provider stabilization and score-loop phase`，当前 gate 为 `MVP real provider smoke acceptance gate`，状态 blocked，下一入口为 `MVP real provider smoke acceptance rerun with prompt-contract calibration`。
- `docs/implementation-control.md`：provider auth/config verification 已通过；Gate A writer/auditor contract hardening 已本地接受；provider runtime timeout hardening 已本地接受；当前真实 smoke blocker 是 `llm_timeout` 或 `llm_contract_violation`。
- `docs/reviews/mvp-provider-runtime-timeout-hardening-controller-judgment-20260531.md`：timeout hardening accepted locally，但 real-provider smoke remains blocked；下一最小入口就是 prompt-contract calibration。

脱敏 smoke evidence：

- `reports/mvp-local-acceptance/20260531-provider-timeout-hardening/controller-real-provider-006597-2024.exitcode`：`1`。
- `reports/mvp-local-acceptance/20260531-provider-timeout-hardening/controller-real-provider-006597-2024.stdout`：0 bytes。
- `reports/mvp-local-acceptance/20260531-provider-timeout-hardening/controller-real-provider-006597-2024.stderr`：安全摘要显示 `orchestration_status=blocked`、`final_assembly_status=incomplete`、`first_failed_chapter_id=1`、`first_failed_stop_reason=llm_timeout`。
- `reports/mvp-local-acceptance/20260531-provider-timeout-hardening/controller-real-provider-006597-2024-diagnostic.json`：第 1 章 `status=failed` / `stop_reason=llm_timeout`；第 2-6 章 `status=skipped` / `stop_reason=dependency_missing`；final issues 包含每章 `chapter_not_accepted`、`missing_accepted_draft`、`missing_accepted_conclusion`。
- controller judgment 记录 supplemental service-level rerun：第 1 章 `status=blocked` / `stop_reason=llm_contract_violation` / `attempt_count=1`，第 2-6 章 `dependency_missing`。

代码事实证据：

- `fund_agent/fund/chapter_writer.py` 已有固定结构段落、required output marker、anchor marker、missing marker、candidate facet disclaimer、超长和 incomplete finish reason parser，但真实模型仍可能不稳定遵守，需要进一步校准 prompt 形态和可解析输出约束。
- `fund_agent/fund/chapter_auditor.py` 已有 line protocol parser，parse failure fail-closed；本 gate 需要校准 auditor prompt 和分类，确保 parse failure 不被误当 pass。
- `fund_agent/services/chapter_orchestrator.py` 已有 `ChapterRepairContext`、`max_repair_attempts` 默认 1、provider runtime diagnostics 和 stop reason mapping；本 gate 需要确保 regenerate 输入带上一轮失败原因，且 timeout、audit parse、prompt contract 分类清楚。
- `fund_agent/services/llm_provider.py` 已有 timeout-only bounded retry/backoff 和 provider-safe diagnostics；本 gate 不回退 provider auth/config，也不引入 provider fallback。

## 5. Non-goals / hard constraints

本 gate 不做：

- 不修改 deterministic `fund-analysis analyze` / `fund-analysis checklist` 默认行为。
- 不为 `--use-llm` 增加 deterministic fallback。
- 不修改 golden、fixtures、score、snapshot、FQ0-FQ6 quality gate、quality gate semantics、manifest、promotion state 或 release/readiness 状态。
- 不进入 Gate 5，不新增 Host/Agent/dayu runtime，不新增 `dayu.host` / `dayu.engine` 依赖。
- 不修改 PR 状态，不 push，不 merge，不 release，不 mark ready。
- 不修改 `AGENTS.md` 或 `docs/fund-analysis-template-draft.md`。
- 不放松 evidence anchor、ITEM_RULE、candidate facet、交易建议、E2 deferred、must_not_cover 或 final judgment safety boundary。
- 不把 `non_asserted_facets` 写成事实，不把弱证据或缺证据包装成通过。
- 不把 `audit_parse` failure 当 pass，不让 parse failure silent pass。
- 不引入 multi-model writer/auditor split、provider fallback、streaming、并发、chapter 0/7 LLM polish 或 Evidence Confirm。
- 不扩大基金范围，不做 golden promotion，不做 `004393` / `004194` / QDII / FOF / `110020` / `017641`。

## 6. Allowed files / modules

后续 implementation worker 只能编辑：

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/llm_provider.py`
- `fund_agent/ui/cli.py`
- `tests/fund/test_chapter_writer.py`
- `tests/fund/test_chapter_auditor.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_llm_provider.py`
- `tests/ui/test_cli.py`
- `fund_agent/fund/README.md`，仅当 writer/auditor public contract 当前用法发生变化。
- `fund_agent/config/README.md`，仅当 LLM timeout/env 当前用法说明发生变化。
- `tests/README.md`，仅当新增测试运行约定或测试分层说明需要同步。
- `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-implementation-evidence-20260531.md`，用于 implementation evidence。
- `reports/mvp-local-acceptance/20260531-prompt-contract-calibration/`，仅保存脱敏 smoke stdout/stderr/exitcode/diagnostic summary。

禁止编辑：

- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/fund-analysis-template-draft.md`
- `AGENTS.md`
- golden / fixtures / score / snapshot / quality gate / promotion state
- `fund_agent/host/`
- `fund_agent/agent/`
- 任意 dayu integration 文件

控制面同步如需发生，应由 controller closeout 单独授权，不由 implementation worker 自行修改。

## 7. Contract decisions

### 7.1 Writer prompt contract calibration

保持现有 fail-closed parser，不放松任何安全规则。校准重点是让真实模型更容易输出可解析 Markdown。

Implementation decisions：

1. Writer prompt 必须把输出协议放在 prompt 前部，并使用短、编号化、可复制的格式块。
2. 第 1-6 章必须输出且只能输出这些顶层结构段落：
   - `### 结论要点`
   - `### 详细情况`
   - `### 证据与出处`
3. 每个 `required_output_items` 必须在正文中出现 exact marker，格式固定：

```markdown
<!-- required_output:<exact required output item> -->
```

4. required marker 后必须二选一：
   - 写同源事实，并在相关事实断言附近使用 allowed anchor marker。
   - 写缺口表达，并在 allowed missing reason 存在时使用 allowed missing marker。
5. anchor marker 只能使用 allowed anchor set 中的 exact id：

```markdown
<!-- anchor:<anchor_id> -->
```

6. missing marker 只能使用本章 allowed missing reason：

```markdown
<!-- missing:<reason> -->
```

7. `non_asserted_facets` 只能作为候选信息出现，不得写成本基金事实。Prompt 应给出固定句式：

```markdown
候选/未断言信息：<facet> 仅为候选标签，当前结构化证据不足，不能写成本基金属于/是/定位为该 facet。
```

8. Prompt 必须明确禁止这些 candidate facet 断言形式：`是<facet>`、`为<facet>`、`属于<facet>`、`定位为<facet>`、`可判定为<facet>`。
9. 输出长度防护：
   - `max_output_chars` 继续作为 writer parser 硬上限。
   - Prompt 要求“宁可简短覆盖 required markers，不要扩写长段落”。
   - Prompt 要求每个 required item 后写 1-3 句，不输出附录、JSON 或分析过程。
   - 如果 provider `finish_reason` 为 `length`、`max_tokens`、`content_filter` 或同义 incomplete reason，继续 `response_incomplete` fail-closed，禁止部分接受。
10. 不要把 parser 改成自动补 marker、自动截断或自动修正文案。模型输出不符合 contract 时必须 blocked，并保留可修复分类。

Expected writer failure categories：

- 缺结构段落：`missing_required_structure`，chapter failure category `prompt_contract`。
- 缺 required marker：`missing_required_output_marker`，chapter failure category `prompt_contract`。
- 未授权 anchor：`unknown_anchor`，chapter failure category `prompt_contract`。
- 非法 anchor/missing marker 或 candidate facet 断言：`llm_contract_violation`，chapter failure category `prompt_contract`。
- 空响应：`llm_empty_response`，chapter failure category `prompt_contract`。
- 输出超长：`response_too_long`，chapter failure category `prompt_contract`。
- finish reason incomplete：`response_incomplete`，chapter failure category `prompt_contract`。
- provider timeout exception：`llm_timeout`，chapter failure category `llm_timeout`。

### 7.2 Auditor protocol calibration

保持 line protocol 可解析和 fail-closed，不把 parse failure 当 pass。

Implementation decisions：

1. Auditor system prompt 必须更短更硬，首句说明“只返回一行或多行 line protocol”。
2. Auditor user prompt 必须把唯一 pass 格式放在最前：

```text
PASS|chapter|no issues
```

3. 非 pass 只允许：

```text
BLOCKING|<location>|<message>
REVIEWABLE|<location>|<message>
INFO|<location>|<message>
```

4. `<location>` 必须非空，优先用 required output item、heading、anchor id 或 `line:N`。
5. `<message>` 必须同时包含“为什么不通过”和“最小修复动作”，不得要求补外部来源。
6. 禁止 Markdown、JSON、编号列表、解释性前后缀、总结句、代码块。
7. Parser 行为必须保持：
   - 空响应：`llm:parse_failure` blocked。
   - `PASS|chapter|no issues` 之外混入任何文本：parse failure blocked。
   - line split 不是三段：parse failure blocked。
   - severity 不在 allowlist：parse failure blocked。
   - location/message 为空：parse failure blocked。
8. Programmatic audit 继续优先于 LLM audit；programmatic blocked 不得被 LLM PASS 覆盖。
9. Parse failure 进入 failure taxonomy 的 `audit_parse`，而不是 `prompt_contract` 或 pass。
10. LLM audit 如果输出 `BLOCKING` 或 `REVIEWABLE` 且格式可解析，分类为 `audit_rule_too_strict` 只在满足本文 7.4 的条件时允许，否则按具体 programmatic/audit issue 分类。

### 7.3 Repair / regenerate calibration

实现必须确保 regenerate 带上一轮失败原因，timeout 分类清楚，最大轮次固定，无无限重试。

Implementation decisions：

1. `ChapterOrchestrationPolicy.max_repair_attempts` 保持固定默认值 `1`，不改为无限循环，不从 provider response 动态增加。
2. 每章最大 writer attempts = `1 + max_repair_attempts`。Budget 耗尽返回 `repair_budget_exhausted` 或更精确 stop reason，不继续调用 provider。
3. Regenerate prompt 必须包含上一轮失败摘要：
   - `attempt_index`
   - previous issue ids
   - sanitized previous messages
   - deterministic required corrections
4. `required_corrections` 必须由稳定映射生成：
   - `missing_required_structure` -> 补齐三个固定结构段落。
   - `missing_required_output_marker` / `C2` -> 为每个 required item 输出 exact marker。
   - `unknown_anchor` / `E1` -> 只使用 allowed anchor marker。
   - `llm:parse_failure` -> 不改变事实内容，重写为 writer contract 可审计格式；auditor 自身 parse failure 的 regenerate 应提示 writer 不要试图绕过 auditor。
   - `non_asserted_facet_boundary` / L2 -> candidate facet 只能候选，不得断言。
   - `response_too_long` -> 缩短每个 required item 到 1-2 句。
   - `response_incomplete` -> 缩短章节，优先覆盖 required markers。
5. 上一轮 messages 必须脱敏和限长，不包含完整 draft、完整 provider response 或 prompt。
6. Timeout 不触发“补事实”或“放松审计”。`llm_timeout` 必须归为独立 `llm_timeout` failure category，由 provider runtime budget 或 prompt length reduction 的最小下一入口处理。
7. Provider timeout retry 继续只在 provider client 内按 typed config 有界执行，不在 orchestrator 外层重复 provider retry。

### 7.4 Failure taxonomy

本 gate 必须把以下 taxonomy 实现为代码级 `ChapterFailureCategory` 扩展，而不是只用于 evidence/reporting。若现有 dataclass Literal 需要扩展，必须同步 tests；新增 Literal 值至少包含 `llm_timeout` 和 `audit_rule_too_strict`。

Required code-level decision：

- 选择方案 A：把 `llm_timeout` 添加为独立 `ChapterFailureCategory` 成员。
- timeout provider diagnostics / exception category 必须返回 `llm_timeout`。
- `rate_limit` / `malformed` / `network` / `http_error` 仍归 `provider_runtime`。
- smoke evidence 和 CLI safe summary 必须优先显示 `first_failed_category=llm_timeout`，不要只显示 `provider_runtime`。
- 选择方案 A：在 `ChapterRunResult` 增加可选 `failure_category: ChapterFailureCategory | None` 字段，由 writer blocked、audit blocked/failed、exception result construction、repair budget exhausted/result construction 等路径填入。
- CLI `first_failed_category` 只能从 `ChapterRunResult.failure_category` 读取，不得遍历 attempts、runtime_diagnostics 或 provider diagnostics 内部结构。
- CLI stdout 必须保持 empty/no fallback；category 只允许进入 stderr safe summary。

| Category | Definition | Typical stop reasons | Next minimal entry |
|---|---|---|---|
| `prompt_contract` | Writer 模型输出不符合结构、marker、anchor、missing、candidate facet 或长度/finish contract | `llm_contract_violation`, `missing_required_structure`, `missing_required_output_marker`, `unknown_anchor`, `response_too_long`, `response_incomplete`, `llm_empty_response` | Writer prompt contract calibration 或 prompt length reduction |
| `audit_parse` | Auditor LLM 响应不是可解析 line protocol | `auditor_blocked` with `llm:parse_failure` | Auditor protocol calibration |
| `llm_timeout` | Provider timeout after bounded provider attempts | `llm_timeout` | Provider runtime budget tuning or prompt runtime-cost reduction |
| `fact_gap` | 结构化事实或证据缺口导致 writer/auditor不能安全断言 | `missing_required_facts`, `needs_more_facts`, `evidence_anchor_missing` | Fact projection / extraction / source evidence gate |
| `audit_rule_too_strict` | Draft 满足 programmatic safety，但 LLM auditor 可解析地提出过严或与 contract 不一致的 blocking/reviewable finding | `auditor_failed`, `auditor_blocked` with parseable issue | Auditor rubric calibration, not pass override |
| `code_bug` | 输入同源、provider 成功、contract 合规但代码异常或 impossible state | `llm_exception`, `ValueError`, invariant failure | Code bug fix gate |
| `provider_runtime` | Provider HTTP/network/rate limit/malformed response/runtime 非 timeout failures | `llm_rate_limited`, `llm_malformed_response`, `llm_network_error`, `llm_exception` when provider category known | Provider runtime gate |

Classification rules：

- `llm_timeout` 是独立 top-level category，同时也属于 provider runtime family；代码级 `ChapterFailureCategory`、runtime diagnostics、`ChapterRunResult.failure_category`、CLI safe summary 和 smoke evidence 都必须优先记为 `llm_timeout`，不要只写泛化 `provider_runtime`。
- `audit_parse` 不得被 `audit_rule_too_strict` 覆盖。只有可解析 `BLOCKING` / `REVIEWABLE` 才可能是 `audit_rule_too_strict`。
- `audit_rule_too_strict` 只能在全部条件同时满足时使用：programmatic audit accepted/pass；LLM audit 是可解析的 fail/blocked/reviewable issue；不存在 `llm:parse_failure`；不存在 `needs_more_facts` repair hint 或 fact-gap 类 issue。programmatic fail 仍按 `prompt_contract` 或 `fact_gap` 分类，不得被 LLM audit 覆盖。
- `fact_gap` 不得通过 prompt 文案包装成 pass。
- `code_bug` 必须只用于没有更具体 provider/runtime/prompt/audit/fact 分类的异常。

### 7.5 Smoke evidence policy

真实 provider smoke 必须记录脱敏 evidence，不记录 secret 或大文本。

Allowed evidence：

- command label and exact command
- exit code
- stdout byte length or empty/non-empty
- stderr safe first-failed summary
- orchestration status
- final assembly status
- per chapter acceptance/failure matrix：chapter id、status、stop reason、failure category、attempt count
- first failed chapter/phase：writer、auditor、repair、provider runtime、final assembly
- provider-safe diagnostics fields：operation、chapter id、provider attempt index、provider max attempts、runtime category、elapsed ms、status code、request id、finish reason、response char count、sanitized error type/message
- secret leak scan command and result

Forbidden evidence：

- API key
- Authorization header
- full prompt
- full draft
- full provider response body
- full provider request body
- raw environment dump
- provider response content
- any copied credential-like string

Recommended evidence paths：

- `reports/mvp-local-acceptance/20260531-prompt-contract-calibration/real-provider-006597-2024.stdout`
- `reports/mvp-local-acceptance/20260531-prompt-contract-calibration/real-provider-006597-2024.stderr`
- `reports/mvp-local-acceptance/20260531-prompt-contract-calibration/real-provider-006597-2024.exitcode`
- `reports/mvp-local-acceptance/20260531-prompt-contract-calibration/real-provider-006597-2024-diagnostic.json`
- `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-implementation-evidence-20260531.md`

## 8. Implementation slices

### Slice A：Writer prompt and parser calibration

Files:

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`

Tasks:

1. Refactor writer prompt text into lower-cognitive-load sections:
   - `OUTPUT CONTRACT`
   - `EXACT MARKERS`
   - `ALLOWED EVIDENCE`
   - `MISSING DATA`
   - `CANDIDATE FACETS`
   - `LENGTH BUDGET`
2. Add or adjust prompt tests to assert:
   - fixed body headings appear near top of prompt.
   - required marker example and per-item marker payload appear.
   - anchor marker and missing marker exact syntax appear.
   - `non_asserted_facets` are explicitly labeled candidate-only.
   - prompt says allowed anchors are an allowlist, not all-required.
   - prompt says no JSON/prefix/appendix and keep each required item short.
3. Keep parser fail-closed behavior:
   - no auto marker insertion.
   - no partial acceptance on response too long.
   - no partial acceptance on incomplete finish reason.
4. If new constants are introduced, keep them module-level and covered by tests.

Expected tests:

- writer prompt contains all contract blocks and exact marker syntax.
- fake LLM valid response still drafts.
- missing structure still blocks as `missing_required_structure`.
- missing required marker still blocks as `missing_required_output_marker`.
- candidate facet asserted as fact still blocks as `llm_contract_violation`.
- response too long and incomplete finish reason remain blocked.

### Slice B：Auditor line protocol and taxonomy calibration

Files:

- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/services/chapter_orchestrator.py`
- `tests/fund/test_chapter_auditor.py`
- `tests/services/test_chapter_orchestrator.py`

Tasks:

1. Tighten auditor prompt so line protocol is front-loaded and example-driven.
2. Keep parser strict and fail-closed; add tests for:
   - prefixed `审计结果：PASS|chapter|no issues` blocks.
   - Markdown bullet line blocks.
   - JSON object blocks.
   - `PASS|chapter|no issues` plus extra text blocks.
   - valid multi-line `BLOCKING|...` parses and fails.
3. Ensure parse failure maps to taxonomy `audit_parse` in Service runtime diagnostics.
4. Ensure parseable LLM audit blocking/reviewable output can be classified distinctly from parse failure.
5. Do not allow LLM auditor PASS to override programmatic audit blocking issues.

Expected tests:

- `test_llm_audit_parse_failure_is_blocked` remains PASS.
- new orchestrator test proves parse failure diagnostic has `chapter_failure_category="audit_parse"`.
- parseable blocking auditor issue does not become `audit_parse`.

### Slice C：Repair context and bounded regenerate calibration

Files:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/services/chapter_orchestrator.py`
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`

Tasks:

1. Verify `ChapterRepairContext` is always present on regenerate after audit fail/block and contains previous issue ids/messages/required corrections.
2. Expand deterministic required correction mapping for current failure categories in 7.3.
3. Ensure sanitized previous messages are length-limited and never include full draft.
4. Add tests proving max repair attempts is fixed:
   - default policy performs at most one regenerate after initial failed audit.
   - `max_repair_attempts=0` performs no regenerate.
   - repeated failure exits with `repair_budget_exhausted` or more precise category and no additional provider calls.
5. Ensure timeout exceptions from writer/auditor do not enter repair loop.

Expected tests:

- fake writer captures regenerate request and sees previous issue ids/messages.
- timeout exception returns `llm_timeout` and `provider_runtime` diagnostics without regenerate.
- repair context does not contain full draft text.

### Slice D：Failure taxonomy and CLI/evidence summary

Files:

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/llm_provider.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_llm_provider.py`
- `tests/ui/test_cli.py`

Tasks:

1. Add or align taxonomy Literal values with 7.4 if needed:
   - `prompt_contract`
   - `audit_parse`
   - `llm_timeout`
   - `fact_gap`
   - `audit_rule_too_strict`
   - `code_bug`
   - `provider_runtime`
2. Keep provider-safe diagnostics secret-free.
3. CLI incomplete message should remain concise but include first failed chapter id/status/stop reason/category. Extraction path is fixed: `_first_failed_chapter_summary()` reads `ChapterRunResult.failure_category` directly and emits `first_failed_category=<category>` when non-`None`; it must not inspect attempts, audit result internals, runtime diagnostics or provider diagnostics.
4. Do not print prompt/draft/provider response to stderr.
5. Tests must prove missing-config still fails before Service and stdout remains empty.

Expected tests:

- CLI timeout fail-closed stderr includes `llm_timeout` and no deterministic report.
- CLI prompt-contract fail-closed stderr includes precise stop reason.
- CLI first failed category comes from `ChapterRunResult.failure_category`; tests must fail if category exists only in nested diagnostics.
- CLI missing-config smoke behavior unchanged.
- provider diagnostic sanitizer still redacts sensitive tokens.

### Slice E：Real provider smoke rerun and implementation evidence

Files:

- `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-implementation-evidence-20260531.md`
- `reports/mvp-local-acceptance/20260531-prompt-contract-calibration/`

Tasks:

1. Run full validation matrix in section 10.
2. Run real provider smoke only after local unit/regression validation passes and provider env is available.
3. Capture only allowed evidence listed in 7.5.
4. If real provider smoke passes:
   - record complete chapters 0-7 presence.
   - record chapter 1-6 accepted matrix.
   - record final assembly accepted.
   - record secret leak scan PASS.
5. If real provider smoke fails:
   - record first failed chapter.
   - record phase: writer/auditor/repair/provider_runtime/final_assembly.
   - classify into one of 7.4 categories.
   - write the minimal next entry as `Next minimal gate`.

## 9. Tests

Targeted pytest should cover at minimum:

```bash
uv run pytest \
  tests/fund/test_chapter_writer.py \
  tests/fund/test_chapter_auditor.py \
  tests/services/test_chapter_orchestrator.py \
  tests/services/test_llm_provider.py \
  tests/ui/test_cli.py \
  -q
```

Required assertions:

- Writer prompt includes fixed body headings, required markers, anchor markers, missing markers, candidate-only facet text and length budget guidance.
- Writer parser still fail-closes missing structure, missing required marker, unknown anchor, response too long, incomplete finish reason and candidate facet assertion.
- Auditor line protocol parser accepts only exact pass or valid severity lines.
- Auditor parse failure remains blocked and cannot become pass.
- Programmatic audit blocking cannot be overridden by LLM PASS.
- Orchestrator regenerate includes previous issue ids/messages/required corrections.
- Orchestrator max repair attempts remains bounded and finite.
- Timeout maps to `llm_timeout`, not `prompt_contract`, `audit_parse` or `code_bug`.
- `ChapterRunResult.failure_category` is filled for writer blocked, audit parse, audit rule too strict, fact gap, timeout and provider runtime failures.
- Parse failure maps to `audit_parse`.
- Fact gaps map to `fact_gap`.
- `audit_rule_too_strict` requires programmatic pass, parseable LLM audit issue, no `llm:parse_failure` and no `needs_more_facts`; programmatic fail remains `prompt_contract` or `fact_gap`.
- CLI `--use-llm` fail-closed path keeps stdout empty and no deterministic fallback.
- Missing config still fails before Service.

## 10. Validation matrix

Implementation worker must run and record:

| Validation | Command | Expected |
|---|---|---|
| Ruff | `uv run ruff check .` | PASS |
| Targeted writer/auditor/orchestrator/provider/CLI pytest | see section 9 command | PASS |
| Full coverage gate | `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS |
| Deterministic analyze smoke | `uv run fund-analysis analyze 006597 --report-year 2024` | exit `0`; complete deterministic report; no LLM requirement |
| Deterministic checklist smoke | `uv run fund-analysis checklist 006597 --report-year 2024` | exit `0` |
| Missing-config `--use-llm` fail-closed smoke | run with `FUND_AGENT_LLM_*` unset or isolated env | exit `1`; stdout empty; config error; Service not called |
| Real provider smoke | `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` | either accepted complete 0-7 report or fail-closed with taxonomy category |
| Secret leak scan | `rg -n "Authorization|Bearer|FUND_AGENT_LLM_API_KEY|sk-|full provider|writer user|draft markdown|prompt|api_key" reports/mvp-local-acceptance/20260531-prompt-contract-calibration docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-implementation-evidence-20260531.md` | no secret-bearing values; safe text hits must be explained |

Notes:

- Real provider smoke must not be implemented as pytest and must not require a live key in CI.
- If provider env is absent in implementation shell, record `provider_config_missing_in_validation_shell` as validation blocked, but do not change code to fallback.
- If real provider smoke times out, record configured timeout seconds/max attempts/backoff as safe scalar values only, not the key or full env.

## 11. Docs decision

Update docs only if current user/developer-facing behavior changes:

- If writer/auditor public contract text or failure taxonomy changes materially, update `fund_agent/fund/README.md`.
- If LLM config/env behavior changes, update `fund_agent/config/README.md`.
- If test commands or smoke evidence conventions change, update `tests/README.md`.
- Do not update `docs/design.md`, `docs/implementation-control.md` or `docs/current-startup-packet.md` in implementation. Controller owns control/doc truth updates after review.

If no README update is needed, implementation evidence must state: `Docs decision: no README update needed because runtime behavior and public usage commands are unchanged`.

## 12. Stop conditions

Implementation worker must stop and report to controller if any occurs:

- A change would require editing golden, fixtures, score, quality gate, schema/promotion state, Host/Agent/dayu, `AGENTS.md` or template draft.
- Provider auth/config appears broken despite previously verified config; record as environment regression and do not redesign provider auth.
- Real provider smoke needs storing full prompt, draft or provider response to debug; stop and ask controller for a secret-safe diagnostic plan.
- Failure cannot be classified into section 7.4 taxonomy.
- Passing the smoke would require weakening evidence anchor, ITEM_RULE, candidate facet, transaction advice, E2 deferred or must_not_cover rules.
- Repair loop would need more than fixed max attempts or unbounded retry to pass.
- Implementation touches unrelated dirty workspace files or cannot separate current work from existing dirty changes.
- Test failures suggest deterministic analyze/checklist behavior changed.

## 13. Residual risk owner

| Residual | Owner / next gate |
|---|---|
| Real provider still `llm_timeout` after prompt length reduction and bounded retry | Provider runtime budget tuning gate |
| Real provider returns repeated writer marker/structure violations | Writer prompt contract calibration follow-up |
| Auditor returns repeated parse failures | Auditor protocol calibration follow-up |
| Auditor returns parseable but over-strict blocking findings | Auditor rubric calibration gate, not pass override |
| Fact gaps block required chapter content | Fact projection / extraction evidence gate |
| Code invariant or impossible state appears | Code bug fix gate |
| Full 0-7 accepted but quality remains not promotion-ready | Future score-loop / golden promotion gate, not this gate |
| Host/Agent/dayu integration absent | Future Route C Gate 5 |

## 14. Completion report format

Implementation evidence must include:

```markdown
# MVP real provider smoke prompt-contract calibration implementation evidence

日期：2026-05-31

Gate：
Role：

## Self-check
- Current gate / role：
- Source of truth：
- Scope boundary：
- Stop condition：

## Changed files
- ...

## Implemented slices
- Slice A：
- Slice B：
- Slice C：
- Slice D：
- Slice E：

## Contract changes
- Writer prompt：
- Auditor protocol：
- Repair/regenerate：
- Failure taxonomy：

## Validation
| Command | Result | Notes |
|---|---|---|

## Real provider smoke evidence
| Field | Value |
|---|---|
| command_label | real-provider-smoke-006597-2024 |
| exit_code | ... |
| stdout | empty / non-empty byte count |
| orchestration_status | ... |
| final_assembly_status | ... |
| first_failed_chapter_id | ... |
| first_failed_phase | writer / auditor / repair / provider_runtime / final_assembly |
| first_failed_stop_reason | ... |
| first_failed_category | prompt_contract / audit_parse / llm_timeout / fact_gap / audit_rule_too_strict / code_bug / provider_runtime |

## Chapter matrix
| Chapter | Status | Stop reason | Category | Attempt count |
|---|---|---|---|---|

## Secret hygiene
- API key/header/full prompt/full draft/full provider response stored：no
- Secret scan command：
- Secret scan result：

## Docs decision
- ...

## Residual risks
- ...

## Next minimal gate
- If PASS：controller may review real provider acceptance evidence.
- If FAIL：...
```

Completion status rules:

- If real provider smoke outputs complete 0-7 chapters and chapters 1-6 are accepted, evidence may say `implementation complete; ready for review`.
- If real provider smoke still fails but taxonomy and next minimal gate are precise, evidence may say `implementation complete; acceptance still blocked by <category>`.
- If failure category is unknown or evidence would require unsafe logging, evidence must say `blocked` and include `Blocking Questions For Controller`.

## 15. Blocking Questions For Controller

None.
