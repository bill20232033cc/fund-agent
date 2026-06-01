# Plan Review: 110020 Reviewed Coverage Candidate Decision Plan

> **Reviewer**: AgentGLM (independent plan reviewer, not controller)
> **Date**: 2026-05-27
> **Target**: `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-20260527.md`
> **Worker**: AgentCodex planning worker
> **Verdict**: **PASS_WITH_FINDINGS**
> **Truth sources**: `AGENTS.md`; `docs/design.md` current design sections; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point; accepted artifacts as cited by the target plan

---

## Review Focus 1: 110020 是否应该进入 reviewed coverage candidate evidence gate

### 审查结论：应该进入，推荐 Candidate A 是正确的。

证据链完整且因果一致：

1. **Source provenance post-implementation bounded evidence rerun** 已被 controller 接受，确认 `110020` / 2024 为 `source_provenance_status=complete`、`fallback_used=true`、`primary_failure_category=unavailable`、`fallback_eligibility=eligible`。
2. **Quality status 为 `warn`**（非 `block`）：FQ2 `turnover_rate` P1 warn、FQ2F P1 field failure warn、FQ0 strict golden not configured info。`warn` 不阻断证据审查。
3. **Post-provenance coverage recovery decision plan** controller judgment 明确将 `110020 reviewed coverage candidate decision gate` 设为下一入口。
4. **整个 gate 链路中 110020 从未被 promoted**：从 small baseline corpus v1 的 fallback-blocked excluded row，到 provenance rerun 的 `provenance_eligible_for_next_review`，始终 `promotion_disposition=not_promoted`。

Defer（Candidate B）的理由不成立：当前未发现需要先于证据审查解决的特定缺失证据。证据审查 gate 本身就是为了发现和记录哪些 index-specific 证据足够或不足。Reject（Candidate C）的理由也不成立：无任何公共证据表明 1100020 provenance 退化为不完整/不合格、或 quality 退化为 `block`。

### 对实现总控的对齐

`docs/implementation-control.md` Startup Packet 的 Next Entry Point 明确为 `110020 reviewed coverage candidate decision gate`，且要求 "must use init-agents / tmux multi-agent flow"。Plan 的 scope 与此完全一致。

---

## Review Focus 2: Source/quality terminal state 是否严谨

### 审查结论：严谨，符合 fail-closed 语义。

| 字段 | Plan 声明状态 | 独立验证 |
|------|-------------|---------|
| `source_provenance_status` | `complete` | Rerun evidence 确认：16 snapshot rows，1 unique provenance tuple，zero `errors.jsonl` records |
| `fallback_used` | `true` | Rerun evidence 确认：`--force-refresh` 后公共字段暴露 `fallback_used=true` |
| `primary_failure_category` | `unavailable` | Rerun evidence 确认：公共 provenance 字段暴露 `primary_failure_category=unavailable` |
| `fallback_eligibility` | `eligible` | 符合 `AGENTS.md` 规则：`unavailable` 是 eligible 失败类别，允许 fallback |
| `quality_gate_status` | `warn` | Rerun evidence 确认：FQ2/FQ2F warn，非 block |
| `terminal_state` | `provenance_eligible_for_next_review` | 正确的中间态，不是 promotion 也不是 rejection |
| `promotion_disposition` | `not_promoted` | 始终保持，无任何 gate 曾改变此状态 |

`AGENTS.md` 规定的五类失败分类与 fallback 策略被正确执行：`unavailable` 属于 eligible 类别（网络、超时、服务端或本地依赖临时不可用），fallback 后 `metadata.fallback_used=True` 已被公共投影正确暴露。`schema_drift`、`identity_mismatch`、`integrity_error` 的 fail-closed 语义未被违反。

---

## Review Focus 3: Unresolved risks 是否足以阻止 golden corpus v1 但不阻止 evidence gate

### 审查结论：风险分离正确。

Plan 列出 5 项 unresolved risks，每项均正确区分了 "blocks golden/baseline promotion" 与 "does not block evidence review"：

| Risk | 阻止 golden corpus v1 | 不阻止 evidence gate | 判断 |
|------|----------------------|---------------------|------|
| `turnover_rate` P1 warn | 是：P1 字段质量不足 | 否：evidence gate 应记录并决定后续 | 正确 |
| Strict golden not configured | 是：无 golden 无法证明 correctness | 否：evidence gate 应记录 FQ0 info | 正确 |
| Reviewed fact readiness | 是：无 accepted reviewed-fact freeze | 否：evidence gate 应识别事实覆盖缺口 | 正确 |
| No fixture-promotion gate | 是：无 gate 不应 promotion | 否：evidence gate 不是 promotion gate | 正确 |
| Index slot methodology/constituents/tracking evidence | 是：index-lens 证据未经审查 | 否：evidence gate 正是为了审查 | 正确 |

此外，plan 的 "Why not enter golden answer corpus v1" 段落还额外列出了 broader corpus blockers：QDII quality、pure FOF coverage/taxonomy、bond positive-risk evidence、representative clean coverage targets。这些与 `docs/implementation-control.md` Active Gate Ledger 的 residual risks 一致。

---

## Review Focus 4: Public-only command matrix 是否安全

### 审查结论：安全，无 direct cache/PDF/source helper 或 fixture promotion 风险。

Acceptance Matrix 的 7 个 step 均为公共 CLI 命令或文档操作：

1. **Startup replay**：只读当前 truth sources
2. **Public snapshot**：`extraction-snapshot --force-refresh` → 输出到 ignored run directory
3. **Public score**：`extraction-score` → 输出到 ignored run directory
4. **Public quality gate**：`quality-gate` → 输出到 ignored run directory
5. **Evidence artifact**：tracked summary artifact → `docs/reviews/`，generated outputs remain ignored
6. **Independent reviews**：review artifacts → `docs/reviews/`
7. **Validation**：`git diff --check`

每一步都有明确的 stop condition，且没有一步涉及：
- Direct cache/PDF/source helper 内部访问
- `FundDocumentRepository` 之外的文件系统操作
- Fixture/baseline/golden promotion
- `docs/implementation-control.md` 更新
- Code changes, GitHub mutations, push, PR, merge

`--force-refresh` 的使用是正确的：确保不使用旧缓存元数据，与 provenance rerun 的做法一致。

---

## Review Focus 5: Stop conditions 是否覆盖关键回归场景

### 审查结论：覆盖充分。

| 回归场景 | 是否有 stop condition | 位置 |
|----------|---------------------|------|
| Quality regress to `block` | 是 | Candidate A stop condition; Acceptance Matrix Step 4 |
| Provenance regress（非 complete eligible fallback） | 是 | Candidate A stop condition; Acceptance Matrix Step 2 |
| Plan 尝试 promotion | 是 | Candidate A stop condition; Acceptance Matrix Step 5 |
| Direct PDF/cache/source helper 访问 | 是 | Acceptance Matrix Step 2 |
| Weaken FQ0-FQ6 semantics | 是 | Acceptance Matrix Step 4 |
| Score 被误读为 strict correctness proof | 是 | Acceptance Matrix Step 3 |
| Output 需要 tracked fixture promotion | 是 | Acceptance Matrix Step 2 |
| 代码/控制文档/source/fixture 变更 | 是 | Acceptance Matrix Step 7 |
| 少于要求数量的 independent reviews | 是 | Acceptance Matrix Step 6 |

三个候选 terminal state（`reviewed_coverage_candidate_input_accepted`、`deferred_pending_reviewed_facts`、`excluded_after_review`）均为 `not_promoted`，不会隐式晋升。

---

## Findings

### Finding 1: Non-blocking — Index-specific evidence 评估在 Acceptance Matrix 中缺少独立验证 step

**现状**：Plan 的 Unresolved Risks 正确识别了 "Index slot methodology / constituents / tracking evidence" 风险。Acceptance Matrix 的 "Evidence artifact" step 要求记录 "index slot evidence status"，"Independent reviews" step 要求确认 "explicit unresolved-risk disposition"。

**风险**：Index 基金如 110020 有独特的评估维度（指数编制规则、跟踪误差、成分股）。当前 Matrix 没有独立 step 要求在 evidence artifact 中显式判定 `index_profile`、`tracking_error`、benchmark-methodology 的证据充分性分类（sufficient / insufficient / out_of_scope）。这一判定被嵌入在 "Evidence artifact" step 的一般性要求中，容易被执行 worker 忽略。

**修订建议**：在 "Evidence artifact" step 的 Acceptance condition 中增加显式要求：artifact 必须包含一个独立的 `index_evidence_assessment` 段落，对 `index_profile`、`tracking_error` 和 benchmark-methodology 三项分别给出 sufficient / insufficient / out_of_scope 分类和理由。

**严重性**：Non-blocking。Independent reviews 和 controller judgment 可以补充此评估，但显式要求更安全。

### Finding 2: Non-blocking — `--source-csv` 路径版本一致性应显式声明

**现状**：Acceptance Matrix Step 2 使用 `--source-csv docs/code_20260519.csv`。Provenance rerun 也使用同一 CSV。但如果 CSV 在两次 gate 之间被更新，snapshot 结果可能不同。

**风险**：低。Stop conditions 会在 provenance/quality 回归时停止。

**修订建议**：在 "Public snapshot" step 的 Acceptance condition 中增加：确认 CSV 文件的 git hash 或修改时间与 provenance rerun 时一致，或在 evidence artifact 中记录当前 CSV 版本。

**严重性**：Non-blocking。Stop conditions 已提供安全网。

---

## Summary of Plan Compliance

| Check | Result |
|-------|--------|
| 与 `AGENTS.md` 规则一致 | 通过 |
| 与 `docs/design.md` 当前设计章节一致 | 通过 |
| 与 `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point 一致 | 通过 |
| 与 accepted artifacts（provenance rerun、post-provenance recovery decision、small baseline corpus v1）一致 | 通过 |
| 未违反 `UI -> Service -> Host -> Agent` 四层边界 | 通过 |
| 未涉及 direct PDF/cache/source helper 访问 | 通过 |
| 未涉及 baseline/golden/fixture promotion | 通过 |
| 未涉及 code changes / GitHub mutations | 通过 |
| 未涉及 `docs/implementation-control.md` 更新 | 通过 |
| Stop conditions 覆盖关键回归场景 | 通过 |
| Public-only command matrix 安全 | 通过 |

---

## Verdict

**PASS_WITH_FINDINGS**

Plan 的推荐（Candidate A: 接受 110020 / 2024 作为 reviewed coverage candidate evidence gate 输入）是有充分证据支持的。Source/quality terminal state 严谨，unresolved risks 正确区分了 golden corpus v1 阻断与 evidence gate 允许，public-only command matrix 安全，stop conditions 覆盖充分。

两项 non-blocking findings 建议在 controller 接受后、evidence gate 执行前作为 refinement 处理，但不阻断 plan acceptance。
