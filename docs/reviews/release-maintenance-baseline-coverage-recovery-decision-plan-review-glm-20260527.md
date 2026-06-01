# Baseline Coverage Recovery Decision Plan — GLM Review

> Reviewer: AgentGLM
> Date: 2026-05-27
> Target: `docs/reviews/release-maintenance-baseline-coverage-recovery-decision-plan-20260527.md`
> Truth sources: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals / Active Gate Ledger
> Verdict: **PASS_WITH_FINDINGS**

---

## 1. Review Scope

This review checks:

1. Next gate selection 是否从 coverage/root-cause 第一性原理成立
2. Index/QDII source recovery 是否足够 bounded，还是应该先做 candidate selection
3. 是否正确阻止 golden corpus v1 / durable baseline promotion
4. Source fallback taxonomy, QDII-FOF taxonomy, baseline_blocking, no GitHub mutation
5. Validation matrix 是否缺少 review/closeout requirement

---

## 2. Finding Summary

| # | Severity | Area | Finding |
|---|----------|------|---------|
| F1 | Medium | Validation closeout completeness | Section 8 只列了 `git diff --check` 作为 closeout validation，未显式要求 MiMo review + GLM review + controller judgment closeout 流程才能 authorize 下一 gate |
| F2 | Low | Next gate plan-before-evidence guard | Section 5 定义了 suggested commands 但未显式声明 index/QDII source recovery gate 自身需要独立 plan artifact 和 review matrix，防止 worker 跳过 plan 直接做 evidence collection |
| F3 | Informational | Gate sequencing readability | Section 3.3 bond positive-risk design 被正确 deferred，但 plan 未标注它与 source recovery 的自然组合关系：两个 gate 合计可解决 6 个 coverage blocker 中的 4 个 |

---

## 3. Detailed Analysis

### 3.1 Next Gate Selection — PASS

Plan 推荐 `index/QDII source recovery and replacement decision gate`，理由链：

- 当前 clean coverage 仅有 active / enhanced index / bond 三个 slot（3/6+），coverage deficit 是 dominant problem
- Index 和 QDII 的 blocker 是 crisp 的：fallback failure category 未知，recovery 或 replacement 路径受已有 design contract 约束
- Gate 可保持 decision-sized，不需要 implementation 或 evidence collection

从 control doc Next Entry Point 的 scope 验证：

> "Decide whether next safe gate should be index/QDII source recovery, pure FOF candidate recovery, bond positive-risk evidence design, holder/turnover evidence triage, or a durable baseline/golden preflight."

Plan 逐一排除了其他选项并给出了 first-principles 理由：

- **Not FOF first**: QDII-FOF ambiguity 存在，需要 new candidate 或 taxonomy design，boundedness 低于 source recovery — 成立
- **Not bond positive-risk first**: 改善一个已有 slot 但不解决两个缺失 slot — 成立
- **Not holder/turnover triage first**: accepted artifacts 分类为 `needs_more_evidence`，当前无 accepted evidence path — 成立
- **Not durable baseline/golden preflight**: entry conditions 为 false — 成立

结论：gate selection 从 coverage/root-cause 第一性原理成立，与 control doc scope 一致。

### 3.2 Index/QDII Source Recovery Boundedness — PASS

Plan 的 boundedness 约束：

1. Entry criteria 要求 candidate replacement 必须 controller-supplied 或 derived from accepted artifacts
2. Stop conditions 明确阻止 unbounded search：
   - Stop if failure category 是 `schema_drift` / `identity_mismatch` / `integrity_error`
   - Stop if replacement candidates 不是 controller-approved 或 repository-verified
   - Stop if recovering failure category 需要 direct source-helper/PDF/cache access
3. Forbidden surfaces 覆盖全面：no renderer, FQ0-FQ6, Service/CLI, Host/Agent, Dayu, source strategy, source helper, extractor, fund_type.py, golden/baseline fixture changes

这些约束足够 bounded。Plan 正确识别了风险（"Replacement search can become unbounded if not supplied with approved candidates"）并用显式 stop conditions 缓解。

关于"是否应该先做 candidate selection"：当前已通过的 `small baseline corpus candidate selection` artifact 已经完成了 candidate selection，确认了 `110020` / `017641` 的 fallback-blocked 状态。Source recovery 是在已有 candidate selection 基础上的下一步，不需要重新做 candidate selection。

### 3.3 Golden Corpus v1 / Durable Baseline Promotion Blocking — PASS

Section 6 列出 5 个解除 blocking 的必要条件：

1. Index/QDII recovered or replaced
2. FOF resolved (pure `fof_fund` or taxonomy gate)
3. `006597` no unresolved `baseline_blocking=true`
4. Holder/share/turnover residuals classified with reviewed evidence
5. Candidate rows have reviewed fact inputs, clean source boundaries

每个条件都有对应的 open residual 在 control doc Open Residuals 表中。Blocking 逻辑与 control doc 的以下决策一致：

- "Do not enter `golden answer corpus v1` until coverage and source/fund-type blockers are resolved."
- "`bond_risk_evidence_missing.baseline_blocking=true` remains blocking for baseline/golden promotion"
- `006597` 仍持有 `holder_structure` / `share_change` / `turnover_rate` residuals

Plan Section 2 的第一性原理声明也正确：`warn` ≠ baseline readiness，baseline-blocking evidence debt 不能成为 durable baseline/golden material。

### 3.4 Source Fallback Taxonomy — PASS

Plan 正确保留了 AGENTS.md / design.md 的 source fallback 语义：

- Only `not_found` / `unavailable` are fallback-eligible（§3.1, §5 stop condition）
- `schema_drift` / `identity_mismatch` / `integrity_error` remain fail-closed
- Stop condition §2: "Stop if failure category is `schema_drift`, `identity_mismatch`, or `integrity_error`; fail closed"
- Entry criteria §4: "The worker can use only `FundDocumentRepository`-based public/product paths"

### 3.5 QDII-FOF Taxonomy — PASS

Plan 在多处正确阻止 QDII-FOF 被计为 pure FOF coverage：

- Section 2: `007721` 和 `017970` 记录为 QDII-FOF / type-gap evidence
- Section 3.2: "Prevents the false-positive coverage error of counting QDII-FOF as pure FOF"
- Stop condition §5: "Stop if QDII-FOF is proposed as pure FOF coverage without a taxonomy gate"
- Section 6 condition 2: "FOF is either a pure `fof_fund` repository-verified row or a taxonomy gate has explicitly accepted how QDII-FOF is counted"

### 3.6 baseline_blocking — PASS

Plan 正确保留 `baseline_blocking=true` 的 blocking 语义：

- Stop condition §6: "Stop if any candidate with `baseline_blocking=true` is proposed for durable baseline/golden promotion"
- Section 6 condition 3: `006597` 必须在 `baseline_blocking=true` 问题解决或 consumer contract 定义后才能进入 baseline/golden
- Review matrix GLM focus: "`baseline_blocking=true` remains blocking"

### 3.7 No GitHub Mutation — PASS

Plan 在 forbidden surfaces 中明确列出 "No GitHub mutation"，validation matrix GLM focus 也包含 "no evidence run in planning artifact"。Section 1 verifier matrix 只包含 read-only 命令。

### 3.8 Validation Matrix — FINDING F1 (Medium)

Section 5 的 review/validation matrix 覆盖了 MiMo 和 GLM 的 review focus，Section 7 提供了 review checklist。但 Section 8 validation 只要求 `git diff --check`。

**问题**：按照项目已建立的 gate flow pattern（plan → MiMo review → GLM review → controller judgment），此 planning artifact 的 closeout 应显式要求：
- MiMo review artifact
- GLM review artifact（即本 review）
- Controller judgment
- 然后才能 authorize 下一 gate (index/QDII source recovery) 开始

当前 Section 8 缺少这一 closeout flow 声明。虽然这是项目惯例且 controller 通常不会跳过 review，但显式声明可防止未来 worker 误认为 `git diff --check` 通过即可进入下一 gate。

**建议修复**：在 Section 8 增加：
> This planning artifact requires MiMo review + GLM review + controller judgment closeout before the `index/QDII source recovery and replacement decision gate` may be authorized.

### 3.9 Next Gate Plan-Before-Evidence Guard — FINDING F2 (Low)

Section 5 列出了 "Suggested commands for a later accepted evidence gate"，但未显式声明下一 gate 自身需要先产出独立 plan artifact 并通过 review 后才能进入 evidence collection 阶段。

虽然 control doc Next Entry Point 已声明 "This next gate must start with Startup Packet replay and `$init-agents` / tmux multi-agent flow. It is a plan/review decision gate first; do not run broad corpus collection or implementation until the plan is accepted."，但在 plan artifact 内显式 restate 这一约束可提供额外安全层。

**建议修复**：在 Section 5 或 entry criteria 中增加：
> The next gate (`index/QDII source recovery and replacement decision gate`) must first produce a plan artifact and complete MiMo + GLM review + controller judgment before any evidence run or implementation begins.

---

## 4. Startup Packet Consistency Check

| Field | Plan claim | Control doc state | Match |
|-------|-----------|-------------------|-------|
| Branch | `codex/local-reconciliation` (implicit from context) | `codex/local-reconciliation` | OK |
| Phase | `release maintenance` | `release maintenance` | OK |
| Latest checkpoint | `5812a1e` | "use latest branch HEAD for exact hash" | OK — `5812a1e` is HEAD at plan time |
| Design truth | `docs/design.md` current design sections | `docs/design.md` (v2.2) | OK |
| Next entry point | `baseline coverage recovery decision gate` | `baseline coverage recovery decision gate` | OK |
| Current architecture | `UI -> Service -> Host -> Agent` | `UI -> Service -> Host -> Agent` | OK |

---

## 5. Material Findings Detail

### F1 — Validation closeout completeness (Medium)

**What**: Section 8 closeout validation 只列了 `git diff --check`，未显式要求 review + controller judgment closeout flow。

**Why it matters**: 此 planning artifact 的目的是决定下一 gate。如果 closeout flow 不显式声明，存在 worker 误读为 `git diff --check` 通过即可进入下一 gate 的风险，跳过 review 和 controller judgment。

**Fix**: 在 Section 8 增加显式 closeout flow 声明。

**Re-review required**: No — 此 finding 不改变 plan 的 gate selection 决策、stop conditions 或 forbidden surfaces，只补充 closeout 纪律。

### F2 — Next gate plan-before-evidence guard (Low)

**What**: Plan 未显式 restated 下一 gate 自身需要 plan-before-evidence 约束。

**Why it matters**: 虽然控制文档已包含此约束，但在 plan artifact 内显式 restate 可防止 worker 只读本 plan 不读 control doc 时跳过 plan 阶段。

**Fix**: 在 Section 5 entry criteria 或 next gate plan 中增加显式 guard。

**Re-review required**: No — 此 finding 是防御性增强，不改变 plan 逻辑。

### F3 — Gate sequencing readability (Informational)

**What**: Plan 正确 deferred bond positive-risk design，但未标注它和 source recovery 的组合覆盖效率。

**Why it matters**: Source recovery 解决 index + QDII (2 slots)，bond positive-risk 解决 `006597` baseline_blocking。两个 gate 合计可解除 4/6 coverage blocker。标注这一关系有助于 controller 做 gate sequencing 决策。

**Fix**: Optional — 可在 Section 4 decision reasoning 中补充一句。

**Re-review required**: No.

---

## 6. Verdict

**PASS_WITH_FINDINGS**

Plan 的核心决策（next gate = index/QDII source recovery）从第一性原理成立，正确阻止了 golden/baseline promotion，保留了所有 fail-closed 约束，stop conditions 和 forbidden surfaces 充分 bounded。两个 material finding 均为 closeout 纪律和防御性 guard 补充，不影响 plan 的 gate selection 逻辑或 blocking 语义。

Re-review not required unless controller or MiMo identifies additional material findings.

---

## 7. Review Checklist Cross-Check

| Check | Result |
|-------|--------|
| Truth hierarchy preserved (`AGENTS.md` > `docs/design.md` > control doc > historical) | PASS |
| Product `warn` not treated as baseline/golden readiness | PASS |
| `bond_risk_evidence_missing.baseline_blocking=true` remains blocking | PASS |
| Source fallback semantics preserved (only `not_found`/`unavailable` eligible) | PASS |
| Direct PDF/cache/source-helper access prohibited | PASS |
| QDII-FOF not counted as pure FOF | PASS |
| No renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, source strategy/helpers, extractors, golden, baseline fixture changes | PASS |
| One minimal next gate selected with clear deferral reasoning | PASS |
| Entry criteria, allowed files, commands, stop conditions, validation defined | PASS |
| No GitHub mutation or fixture promotion | PASS |
