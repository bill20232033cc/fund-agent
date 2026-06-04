# Real LLM Smoke Re-baseline Gate Plan Review — AgentMiMo

> **Reviewer**: AgentMiMo
> **Date**: 2026-06-04
> **Review target**: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-20260604.md`
> **Gate**: `MVP typed-template-to-agent report generation stabilization phase / Gate 2 Real LLM smoke re-baseline gate`
> **Design truth**: `docs/design.md`
> **Control truth**: `docs/implementation-control.md`
> **Rule truth**: `AGENTS.md`
> **Previous gate accepted**: Template truth validation gate checkpoint `c907258`；control sync `e11f5a3`

---

## Review Lenses And Findings

### Lens 1: 命令协议是否只允许后续 evidence step 的 exactly-one real smoke command，且 plan 阶段没有运行 provider

**检查项**：plan 阶段是否禁止 live provider；后续 evidence 是否只允许一条 reviewed smoke command。

- Plan §1 明确声明"本 plan 阶段不运行真实 LLM smoke、不检查 secret、不调用 provider"。
- Plan §3 Non-goals 第二条："不在 plan 阶段运行 live smoke、检查 secret、调用 provider、做 provider readiness probe 或 PASS-only live probe。"
- Plan §5 标题："本节只规划后续 evidence step；本 plan 阶段禁止运行这些 live/provider 命令。"
- Plan §5.2 明确只允许一条命令：`uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`，并列出约束：不添加 timeout/attempt/backoff/model/endpoint/provider override，不运行第二个基金/年份/provider probe/PASS-only timing probe/chapter-only live command，不运行 deterministic fallback command。
- Plan §10 Stop Conditions 第二条：plan 阶段运行 live provider 为 hard stop/blocker。

**Verdict**: **PASS** — 命令协议严格限定为 exactly-one reviewed smoke command，plan 阶段明确禁止运行 provider。

---

### Lens 2: preflight/env presence 是否不会泄露 secret/base URL/Authorization/raw config

**检查项**：preflight 是否只输出布尔 presence 和变量名。

- Plan §5.1 明确要求"只能输出布尔 presence 和变量名，不得输出 API key 值、base URL 值、Authorization header、完整 config dump 或 shell environment"。
- §5.1 建议的 preflight 语义只输出 `api_key_present=true/false`、变量名、optional env 是否 explicitly set。
- §5.1 明确"不校验 endpoint 可达性，不做 HTTP request，不调用 provider，不打印 base URL"。
- Plan §4 A2 要求 evidence artifact 记录"presence booleans、redaction statement"。
- Plan §5.4 Secret scan requirements 要求覆盖 `sk-`、`Authorization`、`Bearer `、base URL value 等模式。

**Verdict**: **PASS** — preflight 语义严格限定为 presence-only，不泄露 secret。

---

### Lens 3: smoke evidence 是否要求 stdout empty on incomplete、exit code、retained artifact path、safe diagnostic matrix、no deterministic fallback

**检查项**：incomplete/blocked/timeout 时 stdout 是否必须 empty；exit code 语义是否保持；artifact 是否保留。

- Plan §4 A4 明确：若 incomplete/blocked/timeout，exit non-zero，stdout empty，stderr 只含 safe summary，retained artifact path 存在，不回退 deterministic。stdout 半成品、exit 0 on incomplete、deterministic fallback、artifact 缺失均为 blocker。
- Plan §4 A5 明确：若 accepted，exit 0，stdout 是完整 8 章 final report，章节 ids `0-7`，quality gate/final assembly accepted，stderr 无 secret。
- Plan §5.2 必须记录项：exit code、stdout 是否 empty、stderr safe summary、retained artifact manifest path、final assembly status、orchestration status、per-chapter matrix、failure_category、failure_subcategory、safe runtime diagnostics allowlist、no deterministic fallback 证据。
- Plan §10 Stop Conditions：incomplete/blocked/timeout 时 stdout 非空、exit 0、生成半成品报告或 deterministic fallback 均为 hard stop/blocker。

**Verdict**: **PASS** — stdout empty on incomplete 和 no deterministic fallback 要求充分且一致。

---

### Lens 4: 是否要求 secret/redaction scan 和 forbidden-scope checklist

**检查项**：evidence 是否必须包含 secret scan 和 forbidden-scope checklist。

- Plan §5.3 要求 evidence artifact 记录 `git branch --show-current`、`git status --short`、`git diff --name-only`、前后对比和 forbidden-scope checklist。
- Plan §5.4 要求 evidence owner 对 plan/evidence artifacts 和 retained artifact summaries 做 redaction scan，覆盖 API key patterns、Provider internals、Base URL value。
- Plan §4 A6 要求 evidence 记录 safe diagnostic matrix，不含 prompt/draft/raw provider response/API key/Authorization/base URL。
- Plan §7 Evidence Artifact Requirements 明确包含 Secret/redaction scan result 和 Forbidden-scope checklist。

**Verdict**: **PASS** — secret/redaction scan 和 forbidden-scope checklist 均为 evidence 必备项。

---

### Lens 5: 是否把 provider timeout/block 保留为 fail-closed evidence，而不是修改 timeout/default/budget 或放松 repair

**检查项**：timeout/block 发生时是否保持 fail-closed，不修改 default/runtime/budget。

- Plan §5.5 明确：保留 fail-closed direct evidence；不修改 timeout/default/budget/attempt/backoff；不扩大 repair budget；不改 prompt/provider/runtime 来追求 pass。
- Plan §4 A8 要求：如果 provider timeout/block 发生，保留 fail-closed direct evidence，不修改 timeout/default/budget，不扩大 repair budget，不改 provider。修改 timeout/default 来追求 pass、把 timeout 误报 accepted、伪造 smoke 均为 blocker。
- Plan §3 Non-goals 第一条："不改变 provider default、provider budget、timeout default、attempt/backoff default、endpoint、model、provider construction、runtime plan 或 provider factory。"
- Plan §10 Stop Conditions：provider timeout/block 发生后通过修改 default/runtime/budget 来追求 pass 为 hard stop/blocker。

**Verdict**: **PASS** — timeout/block 严格保留为 fail-closed evidence，不提供任何修改 default/budget 的逃生口。

---

### Lens 6: 是否覆盖 no provider default/runtime/budget change、no Agent runtime、no multi-year runtime、no score-loop、no golden/readiness、no PR/push/release

**检查项**：non-goals 和 stop conditions 是否完整覆盖所有禁止范围。

- Plan §3 Non-goals 完整列出：不改变 provider default/runtime/budget；不做 Agent runtime/multi-year/score-loop/golden/readiness/PR/push/release；不修改 source/test/config/runtime behavior。
- Plan §10 Stop Conditions Hard stop 列表覆盖：执行 golden/readiness、snapshot refresh、fixture promotion、strict correctness rerun、score-loop、Agent runtime、multi-year runtime、PR、push、release 均为 blocker。
- Plan §4 A9 Boundary guardrails：不新增 dayu runtime 依赖、不绕过 FundDocumentRepository、不直接读 PDF/cache/source helper、不使用 `extra_payload`。

**Verdict**: **PASS** — 禁止范围覆盖完整，无遗漏。

---

### Lens 7: 是否没有用历史 retained run 或旧日志替代当前 direct evidence

**检查项**：plan 是否明确禁止用旧日志/retained run 作为当前 smoke accepted 证据。

- Plan §2 Current Facts 第九条："该历史记录只能作为背景，不能替代本 gate 的当前真实 smoke 直接证据。"
- Plan §3 Non-goals 最后一条："不把旧日志、旧 retained run、旧 aggregate review 或 historical control note 当作本 gate smoke accepted 证据。"
- Plan §9 Accepted Checkpoint Requirements："不得用旧日志、旧 retained run、旧 aggregate review 或间接证据替代本 gate plan review/controller judgment。"
- Plan §10 Stop Conditions："使用旧日志、旧 review、旧 retained artifact 作为当前 smoke accepted 证据"为 hard stop/blocker。
- Plan §7 Evidence Artifact Requirements："Root cause / residual 分类必须使用同源 direct evidence：命令输出、retained artifact safe fields、current git state；不得使用旧日志或间接证据。"

**Verdict**: **PASS** — 多处重复强调禁止使用历史数据替代当前 direct evidence。

---

### Lens 8: 是否可能过度授权 live smoke before plan accepted

**检查项**：plan 是否要求 plan review + controller judgment + accepted checkpoint 后才允许 live smoke。

- Plan §8 Review Handoff Expectations：需要两份独立 plan review（DS + MiMo），两份 review 都必须输出 PASS/BLOCKED/NEEDS_FIX，controller 只能在两份 review 均无 blocking finding 后进入 plan judgment。
- Plan §9 Accepted Checkpoint Requirements：必须有 plan artifact、两份独立 plan review、controller judgment artifact（显式说明本 plan 不授权 live smoke）、accepted local commit hash。
- Plan §11 Next Entry Point："若本 plan 经 DS/MiMo review、controller judgment 和 accepted local checkpoint 接受，下一入口是 Real LLM smoke re-baseline evidence execution"。
- Plan §10 Stop Conditions："plan 阶段运行 live provider"为 hard stop/blocker。

**Verdict**: **PASS** — plan 严格要求完整的 review → judgment → accepted checkpoint 流程后才允许进入 evidence step。

---

## Overall Assessment

本次 plan review 按 8 个 lens 逐一检查，未发现任何 blocking finding 或 non-blocking residual。

Plan 在以下方面设计严谨：

1. **命令协议**：严格限定为 exactly-one reviewed smoke command，plan 阶段明确禁止 provider 调用。
2. **Secret 安全**：preflight 只输出 presence boolean，evidence 要求 redaction scan，多处禁止泄露 API key/base URL/Authorization。
3. **Fail-closed 语义**：incomplete 时 stdout 必须 empty、exit non-zero、no deterministic fallback，与现有代码语义一致。
4. **Timeout/block 处理**：严格保留为 fail-closed evidence，不提供修改 default/budget 的路径。
5. **禁止范围**：non-goals、stop conditions、boundary guardrails 覆盖完整，无遗漏。
6. **Direct evidence 完整性**：多处禁止使用旧日志/retained run 替代当前 direct evidence。
7. **Plan acceptance gate**：要求 DS/MiMo 双 review + controller judgment + accepted checkpoint 后才允许 live smoke。
8. **Verifier matrix**：A1-A9 覆盖 plan scope、preflight safety、singular command、fail-closed、accepted report、diagnostic matrix、direct evidence integrity、timeout/block classification 和 boundary guardrails，每个 criterion 都有明确的 blocker vs residual 分类。

---

## Verdict

**PASS** — 无 blocking findings。

plan artifact 符合全部 8 个 review lens 要求，verifier matrix A1-A9 完整且 blocker/residual 分类清晰，可以进入 DS review 和 controller judgment 流程。
