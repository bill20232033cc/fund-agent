# MVP Real LLM Smoke Re-baseline Gate Evidence Review — AgentDS

## 1. Scope

- Role: AgentDS independent evidence review，不启动 gateflow/phaseflow，不实现，不修改 evidence，不运行 provider，不 commit/push/PR。
- Review target: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-evidence-20260604.md`
- Plan: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-20260604.md`
- Controller judgment: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-controller-judgment-20260604.md`
- Design truth: `docs/design.md` /  Control truth: `docs/implementation-control.md` / Rule truth: `AGENTS.md`
- Allowed write: 仅本 review artifact。

## 2. Findings

按 severity 排序。无 blocking findings 时明确写 PASS / no blocking findings。

### Finding 1 — Secret-safe preflight 合规 (PASS, no finding)

Evidence §4 执行了 presence-only env preflight，仅输出布尔值和变量名：
- `FUND_AGENT_LLM_PROVIDER` / `FUND_AGENT_LLM_MODEL` / `FUND_AGENT_LLM_BASE_URL` 均为 `false`。
- API key env var name 仅输出变量名 `FUND_AGENT_LLM_API_KEY`，不输出值。
- Optional runtime env 均 `explicitly_set: false`，不输出默认值或实际值。

§4 Secret-safe statement 明确声明：无 API key value、base URL value、Authorization header、raw config dump、shell environment dump、raw prompt、raw provider response 或 raw audit response 输出；未执行 endpoint reachability check、HTTP request 或 provider call。

与 plan §5.1 的 presence-only 协议完全一致。与 controller judgment §4 secret-safe preflight 要求一致。

**Verdict: PASS**

### Finding 2 — environment_blocked 分类有直接证据，未伪造 smoke (PASS, no finding)

Evidence §4 Preflight classification 明确分类为 `environment_blocked`，理由为 "required LLM provider/model/base-url/key presence is absent"。

直接证据：
- §4 presence 表格：所有 required 字段均为 `false`。
- 无任何 live provider 命令被执行，无历史 retained artifact 被引用为当前 smoke 证据。
- 无 provider default/runtime/budget 被修改以绕过环境阻断。

Evidence §6 明确记录 live smoke `not run`，原因直接引用 Step 1 stop condition。§5 明确记录 local non-live validation `not_run_environment_blocked`，所有 6 条 planned validation commands 标注为 "explicitly not run"。

与 plan §5.3 stop condition "env/config absent 但 evidence 仍尝试伪造 smoke 或使用历史 retained run 代替 → hard stop / blocker" 对比：evidence 正确触发了 stop，未执行伪造。

与 plan §10 residual owner 分类 "environment_blocked → controller / environment owner" 一致。

**Verdict: PASS**

### Finding 3 — 无 secret/敏感信息泄漏 (PASS, no finding)

Evidence §7 redaction scan 覆盖：
- `sk-` pattern、Authorization header、Bearer token、API key assignment、configured key env var value、base URL value、raw prompt/raw provider response/raw audit response/message body/full request headers。
- 所有 scan 结果为 `false`，no blocking secret or raw payload hit。

§7 Policy-term note 解释 scan checklist label 中出现 `raw prompt` 等术语仅为 forbidden-scope 标签引用，非实际 payload content。该声明合理且必要，避免 scan 关键词触发误报。

Manual review of full evidence artifact 确认：全文无一 API key、base URL、Authorization header、raw config、prompt text、provider response、request headers 或 shell env dump。

与 plan §5.4 redaction scan requirements 和 controller judgment §4 temporary capture file lifecycle 要求一致。因无 live smoke 运行，无 temporary capture files 产生，controller 增加的 capture file lifecycle 要求不适用。

**Verdict: PASS**

### Finding 4 — Git pre/post integrity 仅新增允许 evidence artifact (PASS, no finding)

Pre-git (§3):
- `git branch --show-current` = `feat/mvp-llm-incomplete-run-artifacts` (correct branch)
- `git status --short` = pre-existing untracked files only
- `git diff --name-only` = empty (no tracked file modifications)

Post-git (§11):
- Branch 不变
- Status 新增 `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-evidence-20260604.md` 为唯一新增路径
- Runtime retained artifact: none (因 live smoke 未运行)
- `git diff --name-only` = empty (no tracked source/test/config/runtime behavior diff)

Post-git 新增文件与 plan allowed write path 完全匹配。未修改 `docs/design.md`、`docs/implementation-control.md`、`docs/current-startup-packet.md`、plan/review/controller artifacts、source、test、config 或 runtime behavior。

与 plan §5.3 git integrity 要求和 plan §1 allowed write path 一致。

**Verdict: PASS**

### Finding 5 — A1-A9 acceptance criteria mapping 合理性 (PASS, 1 minor residual observation)

Evidence §8 A1-A9 mapping:

| Criterion | Evidence 判定 | DS 审查 |
|---|---|---|
| A1 scope safety | `PASS` | 正确。Evidence 未修改 source/test/config/runtime。 |
| A2 secret-safe preflight | `BLOCKER` | 正确。Env absent 导致 blocker，但 preflight 本身 secret-safe。DS 确认: 此处 BLOCKER 标记针对 gate outcome 而非 evidence artifact 缺陷。 |
| A3 singular smoke | `BLOCKER` | 正确。Smoke 正确未运行，非 evidence 缺陷。 |
| A4 fail-closed/stdout | `BLOCKER` | 正确。因 live smoke 未运行，不可评价。 |
| A5 accepted report safety | `BLOCKER` | 正确。不可评价。 |
| A6 diagnostics/redaction | `BLOCKER` | 正确。Runtime matrix 不可用，但 artifact redaction 通过。DS 注: A6 有两个子维度——redaction scan (PASS) 和 runtime diagnostics (BLOCKED)。Evidence 把整体标为 BLOCKER 偏保守但可接受，因为 runtime diagnostics 是 A6 的核心直接证据。 |
| A7 evidence integrity | `PASS` | 正确。Git pre/post 已记录。 |
| A8 provider timeout/block | `BLOCKER` | 正确。Provider smoke 未运行，不可评价；runtime/default/budget 未改动。 |
| A9 boundary guardrails | `PASS` | 正确。Forbidden-scope checklist §9 全部 PASS。 |

**Minor residual observation (non-blocking):** A2 被标记为 `BLOCKER`，但 A2 原文要求的是 "Env/config presence preflight is secret-safe"。Evidence 对此的 secret-safe 执行实际是 PASS 的——presence preflight 本身正确且无 secret 泄漏。BLOCKER 标记更适合放在 A2 的 gate-outcome 维度而非 evidence-artifact-correctness 维度。但 evidence §8 B1 已在 §10 中将 environment_blocked 作为独立 blocking finding 列出，归属 controller/environment owner，因此 A2 BLOCKER 标记不构成 misclassification。此为 presentation nuance，不影响 evidence correctness。

**Verdict: PASS (mapping is reasonable; no misclassification that affects gate)**

### Finding 6 — Forbidden-scope checklist 完整性 (PASS, no finding)

Evidence §9 checklist 覆盖 plan §5.3 和 controller judgment §4, §5 中所有 forbidden scope:
- Provider default/runtime/budget 未改动 ✓
- Timeout/attempt/backoff/model/endpoint 未覆盖 ✓
- Agent runtime / multi-year / score-loop 未触及 ✓
- Golden/readiness / snapshot refresh / strict correctness rerun / release readiness 未触及 ✓
- PR/push/release 未执行 ✓
- External state command / Dayu runtime dependency 未引入 ✓
- Direct PDF/cache/source helper read 未发生 ✓
- Production annual-report access only through `FundDocumentRepository` → "no production annual-report access occurred" ✓
- `extra_payload` business params 未使用 ✓
- Public chapter ids `0-7` 未改 ✓
- Auditor/quality gate/fail-closed 未放松 ✓
- Deterministic fallback 未发生 ✓
- Partial report to stdout 未发生 ✓

Checker 总数 18 项，全部 PASS。覆盖完整，无遗漏。

**Verdict: PASS**

### Finding 7 — 本地 non-live validation 未执行的处理 (PASS, non-blocking observation)

Evidence §5 记录了 local non-live validation "not run due to Step 1 environment_blocked stop condition"，6 条 planned commands 全部标注未运行。

Plan §6 将这些命令定位为 "harness safety 验证"，Plan §6 stop rule 为 "如任一 local non-live validation command 失败……不得绕过失败直接运行 live smoke"。Plan §5.1 stop rule 为 "如果 required env/config absent，evidence 必须分类为 environment_blocked……并停止 live smoke"。

Evidence 在 Step 1 preflight 发现 env absent 后同时跳过了 local non-live validation。这是保守解释：plan 的 env-absent stop 明确针对 live smoke，但 evidence owner 判断 local validation 在 gate 已 blocked 时无执行价值。该判断不违反 plan 文字或精神：
- Local validation 不改变 `environment_blocked` 事实。
- 避免产生不必要的 harness 副作用。
- 不伪造或替代 live smoke evidence。

**Observation (non-blocking):** 如果 controller 后续期望在 env absent 时仍执行 local non-live validation 以验证 harness integrity，可在 controller judgment 中增加要求。当前 evidence 的保守跳过不构成缺陷。

### Finding 8 — Context read §2 完整性 (PASS, 1 minor note)

Evidence §2 列出了 required context read list，包含 `AGENTS.md`、`docs/implementation-control.md`、`docs/current-startup-packet.md`、`docs/design.md`、plan 和 controller judgment。

Evidence §2 "Key current facts confirmed" 中的事实与 design/control/startup 真源一致：
- `--use-llm` explicit opt-in fail-closed 语义 ✓
- Public chapter ids `0-7` ✓
- Production annual-report access through `FundDocumentRepository` ✓
- Provider/runtime defaults 不在 scope ✓

无矛盾。

**Verdict: PASS**

## 3. Verdict

### Evidence Artifact Correctness: PASS

Evidence artifact 合规。无 blocking findings。

Evidence 正确执行了 accepted plan 的 secret-safe preflight first 协议，在 env/config absent 时正确停止，未运行 live smoke，未伪造 smoke 或使用旧 retained artifact，未泄漏 secret/base URL/API key/Authorization/raw config/raw prompt/raw provider response，git pre/post integrity 仅新增允许 evidence artifact，A1-A9 mapping 合理，forbidden-scope checklist 完整。

### Gate Outcome: BLOCKED

Gate 被 B1 `environment_blocked` 阻断。Required LLM provider/model/base-url/key env/config 缺席，live smoke 无法执行。B1 的 owner 为 controller / environment owner，需由 controller 裁决 env 配置和后续 gate entry。

Artifact correctness PASS 与 gate outcome BLOCKED 同时成立：evidence 本身诚实、合规、secret-safe，但 gate 因环境缺失无法继续。

### Summary

| 维度 | 结果 |
|---|---|
| Evidence artifact correctness | **PASS** |
| Gate outcome | **BLOCKED** (B1 environment_blocked) |
| Blocking findings count | **0** (针对 evidence artifact；gate 层面 1 个 environment blocker B1，由 controller/environment owner 处理) |
| Allowed write only | **是**，仅写入本 review artifact |
