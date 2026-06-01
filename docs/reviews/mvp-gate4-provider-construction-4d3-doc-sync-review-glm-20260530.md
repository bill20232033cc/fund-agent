# MVP Gate 4 Slice 4D3 Docs/Design/Control Sync Review (GLM)

日期：2026-05-30
角色：独立 review agent（非 implementation worker）
Gate：`MVP Gate 4 Slice 4D3: docs, design/control sync, and full regression gate`
审查范围：7 个文件 unstaged diff + implementation evidence artifact
Verdict：**pass_with_non_blocking**，附 1 条 blocking finding 需最小修复后 re-check

---

## Verdict

**pass_with_non_blocking**

7 个文档 diff 在以下方面准确反映了 4D1/4D2 accepted code facts：provider-backed CLI path 作为 current fact、默认 analyze/checklist 确定性、env contract 与代码一致、fail-closed 语义与代码一致、next entry point 清晰、release/golden residual 保留且未拉回主线、README 不泄漏过多内部细节、config/tests docs 说明 fake env/MockTransport/monkeypatch。

存在 1 条 **blocking finding**（用户已预发现的 control doc 冲突句），需要最小文本修复后确认。

---

## Blocking Findings

### B1. `docs/implementation-control.md` Current Decision Summary 句子与 accepted provider-backed path 冲突

**文件**：`docs/implementation-control.md`
**行号**：当前文件第 122 行（diff 未改动此行）

**冲突原文**：

> Current deterministic `fund-analysis analyze/checklist` remains the only production report/checklist mainline.

**问题**：`--use-llm` 已在 4D1/4D2 被 accepted 为 functional provider-backed opt-in production path（同一文件的 Guardrails 和 Gate Ledger 均已更新）。"the only production mainline" 与 "accepted provider-backed CLI opt-in" 直接矛盾：`analyze --use-llm` 配置完整时已是可用生产路径，而非仅 fail-closed 桩。

**最小修复建议**：将 "remains the only production report/checklist mainline" 改为等价于 "remains the default production report/checklist path; `analyze --use-llm` is an explicit opt-in provider-backed production path"。修复后此句应与同文件 Guardrails 第 32-34 行、Current Gate Objective 和 Recent Active Gate Ledger 的表述一致。

**严重度**：blocking——Current Decision Summary 是 control doc 最高频读取区域之一，与 Guardrails/Gate Ledger 的矛盾会导致后续 resume 时对 "当前是否有第二条生产路径" 产生歧义。

---

## Non-blocking / Residual

### N1. `docs/implementation-control.md` Guardrails "当前默认实现仍以确定性" 用词

Guardrails 第 21 行已正确加 "默认"，与 provider-backed path 不矛盾。无 action。

### N2. `docs/design.md` §1.2 确定性 MVP 主链路表新增 `analyze --use-llm` 后缀

表述为 "当前默认…组成；`analyze --use-llm` 是显式 opt-in provider-backed Route C 路径"，与整个 design.md Route C 已实现状态一致。无 action。

### N3. `fund_agent/README.md` 新增 "Service 当前拥有 Route C Gate 4 provider construction" 段落

只描述 Service-owned provider factory 和 Fund Protocol boundary，不泄漏 vendor SDK、API key 或 env 解析细节。边界正确。无 action。

### N4. `README.md` 环境变量表

`FUND_AGENT_LLM_API_KEY` 标注 "条件必填" 并解释 `FUND_AGENT_LLM_API_KEY_ENV_VAR` 指向关系，与 `fund_agent/config/README.md` 和 4D1 `load_llm_provider_config_from_env()` 代码一致。无 action。

### N5. `tests/README.md` 新增 LLM 测试维护约定

"LLM config/provider/CLI 测试必须使用 fake env mapping、httpx.MockTransport、monkeypatch 或测试替身；pytest 不需要真实 API key，不做 live provider smoke，不把 retry/backoff、provider fallback 或多模型 writer/auditor split 写成已实现行为。"——与 4D1/4D2 代码和 plan decision A4/A7 一致。无 action。

### N6. `fund_agent/config/README.md` 末尾未来约束更新

从 "环境变量覆盖或 prompt manifest" 改为 "provider fallback、retry/backoff 或 live smoke"——反映了当前 residuals 的准确边界。无 action。

---

## Validation Reviewed

- Implementation evidence 记录 ruff passed、125 targeted tests passed、1106 full tests passed、coverage 91.76% ≥ 50%。
- Evidence self-check 声明无 runtime changes、无 Python implementation changes、无 tests changed。
- Evidence preflight 无 tracked dirty；untracked 均为用户声明无关文件。
- `git diff --check` passed（无 trailing whitespace/conflict markers）。

---

## Scope Check

- ✅ 未把 Host/Agent/dayu 写成已实现
- ✅ 未把 retry/backoff、provider fallback、live smoke、多模型 writer/auditor split 写成已实现
- ✅ 未把 chapter 0/7 LLM polish、Evidence Confirm 写成已实现
- ✅ 未把 full FundToolService 写成已实现
- ✅ 未把 golden/score/snapshot/quality gate/fixture promotion 拉回 MVP 主线
- ✅ next entry point 明确指向 `MVP Gate 4 Slice 4D aggregate review gate`，不再指向 4D1/4D2
- ✅ commits `26203d3` 和 `ab0590a` 记录在 startup packet 和 control doc
- ✅ release/golden residual 保留在 Open Residuals 表
- ✅ 没有发现需要 runtime 修改的 diff 条目
- ⚠️ B1 发现 control doc 内部 self-conflict，需最小文本修复

---

## Review Lens Checklist

| # | Lens | 结果 |
|---|------|------|
| 1 | 4D1/4D2 provider-backed CLI path 写为 current fact；default analyze/checklist deterministic | ✅ pass |
| 2 | 未把 deferred items 写成 ready | ✅ pass |
| 3 | Env contract 与 4D1 code 一致 | ✅ pass |
| 4 | Failure semantics 与 4D2 code 一致 | ✅ pass |
| 5 | Control docs next entry point 明确到 aggregate review | ✅ pass |
| 6 | Release/golden residual 保留但不拉回主线 | ✅ pass |
| 7 | README 用户手册平衡 internal/external | ✅ pass |
| 8 | Config/tests docs 说明 fake env/MockTransport/monkeypatch | ✅ pass |
| 9 | implementation-control.md Decision Summary 冲突句 | ⚠️ **B1 blocking** |
