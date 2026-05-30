# Plan Review: Baseline Coverage / Source Recovery / Taxonomy + Bond Triage

> **Reviewer**: AgentGLM (independent plan reviewer)
> **Date**: 2026-05-27
> **Review target**: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-20260527.md`
> **Truth sources**: `AGENTS.md`, `docs/design.md` current design, `docs/implementation-control.md` Startup Packet / current gate / next entry, accepted artifacts
> **Previous gate evidence**: Gate 4 run review (`release-maintenance-small-baseline-corpus-v1-run-review-glm-20260527.md`)

---

## Findings

### F1 — INFO: Gate 4 reconciliation 正确且完整

**Evidence**:
- Reconciliation 准确陈述 Gate 4 为 evidence-only acceptance，非 golden-corpus readiness（lines 18-25）。
- 三 clean candidates / 三 slots 覆盖率低于 5-10 目标的判断与 Gate 4 run evidence 一致。
- 006597 quality-gate block 原因（missing-field rate，非 golden mismatch）与 Gate 4 run Interpretation Notes 吻合。
- Fallback-blocked / FOF data-gap / 004393-2025 probe-only 状态与 accepted evidence chain 无矛盾。
- Golden corpus v1 routing 被正确阻断，next gate 目标（增加 coverage + 解决 bond blocker）与 Gate 4 decision rule 对齐。

**Risk**: 无。

---

### F2 — INFO: Subgate 分解避免 big-bang，implementation 正确 gate 在 evidence 之后

**Evidence**:
- First-Principles Decomposition 明确分解三个独立 blocker（Problem A/B/C），并声明"merging them into one implementation would hide root cause"（line 30）。
- Subgate 1 是 evidence-only triage，不涉及任何代码变更（lines 94-108）。
- Subgate 2A-2D 均以 Subgate 1 的 same-source evidence 为前提条件（"Only authorize if Subgate 1 proves..."，lines 112, 122, 131）。
- Recommendation 明确说 "Authorize Subgate 1 evidence-only triage next. Do not authorize implementation yet."（line 378）。
- Subgate 1 同时处理三个 problem 的 observation 不构成 big-bang risk——observation 可合并，implementation 不可。

**Risk**: 无。分解策略与第一性原理一致。

---

### F3 — MINOR: Index/QDII/FOF replacement 探测依赖 controller 提供候选列表，Subgate 1 可能在此处 stall

**Evidence**:
- Slice 1 suggested commands 使用 `<INDEX_REPLACEMENT>`, `<QDII_REPLACEMENT>`, `<FOF_REPLACEMENT>` 占位符（line 176）。
- Line 179 要求："Candidate replacement commands must be filled from accepted selected-fund CSV evidence or a controller-approved candidate list. If no candidate list is accepted, stop and ask controller for the candidate source."
- 当前 accepted selected-fund CSV（`docs/code_20260519.csv`）是精选基金池，可能已经包含 index/QDII/FOF 候选，但 plan 未确认 CSV 中是否有合适的 replacement candidates。
- Stop condition 覆盖了这种场景（line 192: "Source failure category cannot be observed through public paths"），但未明确覆盖"候选列表为空"的 stall 场景。

**Risk**: 低风险。Plan 的 stop condition 和 controller-approval guard 已经正确处理了这种不确定性。但 implementation worker 在执行 Subgate 1 时可能发现 replacement 探测无法开始（无候选），导致 bond triage 部分独立完成而 index/QDII/FOF 部分只能标记 "needs controller input"。

**Recommendation**: 不阻塞。Implementation worker 在 Subgate 1 开始前应先确认 CSV 中可用的 replacement candidates，将 bond triage 和 coverage probing 作为可独立交付的两部分处理。若 coverage probing 缺少候选，bond triage 证据仍可独立 close。

---

### F4 — INFO: Fallback recovery/replacement 规则严格对齐 AGENTS.md fail-closed 语义

**Evidence**:
- Problem A 正确列出五个失败类别，仅 `not_found` 和 `unavailable` 允许 fallback（lines 37-38），与 `AGENTS.md` 年报来源 fallback 策略表一致。
- `schema_drift`, `identity_mismatch`, `integrity_error` 必须 fail-closed（lines 41-43）。
- 新增 `unknown_upstream_failure_category` 也必须排除（line 45），这是对之前 residual 的正确处理。
- Safe recovery path 明确禁止从 successful Eastmoney fallback 反推上游失败类别（line 50），防止掩盖 fail-closed 问题。
- Source fallback semantic changes 被排除出 scope，需单独 gate（line 52）。
- Slice 2C 的 stop condition 包括 "Any fail-closed source category appears" 和 "Recovery requires modifying source fallback semantics"（lines 297-298）。

**Risk**: 无。Fail-closed 纪律与 `AGENTS.md` 硬约束和 `docs/design.md` §6.1 完全一致。

---

### F5 — INFO: FOF taxonomy 处理不提前将 QDII-FOF 计为纯 FOF

**Evidence**:
- Problem B 明确 "Do not count QDII-FOF as pure FOF without an accepted taxonomy gate"（line 65）。
- 优先 pure FOF search（line 67），taxonomy 仅在 search 失败后开启。
- Slice 2D stop condition: "The plan would count QDII-FOF as pure FOF without explicit taxonomy decision"（line 315）。
- Taxonomy change 不与 renderer / Service/CLI / quality gate / golden corpus 同 gate 实现（line 316）。
- Golden eligibility criteria 明确排除 `taxonomy_pending`（line 371）。

**Risk**: 无。FOF 处理保守且分层正确。

---

### F6 — INFO: Bond block triage 四类根因分类严谨，same-source 约束充分

**Evidence**:
- Problem C 定义四个互斥根因类别：`extractor_gap`、`field_applicability_policy`、`evidence_anchor_or_score_projection`、`bond_lens_contract_gap`（lines 82-86）。
- 对 006597 每个具体 missing field 给出合理假设（lines 75-79）：
  - `turnover_rate`: bond fund stock turnover 可能不适用——与 `docs/design.md` §7.3 的 fund-type-conditional field applicability 模式一致。
  - `holder_structure`: 可能为真实抽取 gap——合理假设。
  - `holdings_snapshot`: equity holdings snapshot 对 bond fund 是错误 lens——正确，§8 bond holdings 不同于 stock holdings。
  - `share_change`: 可能为多份额类别 extractor 歧义——合理假设。
- "Root-cause decision must be same-source"（line 81）对齐 `AGENTS.md` 硬约束"找问题的 root cause 一定要逻辑/数据同源"。
- "Do not weaken FQ0-FQ6"（line 88）明确且与 Non-Goals 一致。
- Reclassify N/A 必须发生在 score/fund-quality applicability 层，不在 quality-gate threshold 层（lines 88-89）——这利用了 `docs/design.md` §7.3 已有的 fund-type conditional applicability 模式，不引入新机制。

**Risk**: 无。Triage 分类充分且 same-source 约束正确。

---

### F7 — INFO: Implementation slice 文件范围最小，test 聚焦，全部 gated behind evidence

**Evidence**:
- Slice 2A 允许文件限于 `extraction_score.py` + 可能 `fund_type.py` + README sync（lines 199-203）。
- Slice 2A 对 `quality_gate.py` 设为 default forbidden，仅当 tests 证明 score 层无法保留 FQ 语义时才放开（line 213）。
- Slice 2B 允许文件限于 narrow extractor module + snapshot/score projection（lines 242-245）。
- Slice 2C 明确 **不授权** source changes（line 283），source 文件列在 "Possible implementation files only for a later separate source-boundary gate"。
- Slice 2D 明确 evidence-only，implementation 仅在 accepted taxonomy plan 之后（lines 303-304）。
- 每个 Slice 都有 focused test files、validation commands 和 explicit stop conditions。
- 所有 implementation slice 以 Subgate 1 same-source evidence 为前提。

**Risk**: 无。文件范围约束比 `AGENTS.md` 模块边界规则更窄，是正确的最小切片策略。

---

### F8 — INFO: Verifier matrix 和 golden eligibility criteria 充分

**Evidence**:
- Verifier matrix 按 gate type 分行，每行标注 required/conditional（lines 333-342）。
- Plan-only closeout 只需 `git diff --check`，与 plan-only artifact 策略一致。
- Evidence-only triage 复用 Gate 4 已验证的 snapshot/score/quality-gate 命令链。
- Implementation tests 使用 focused test files 而非 full pytest——与最小变更策略一致。
- Golden eligibility criteria 五项全部量化且无歧义（lines 368-374）：
  - ≥5 candidates across ≥half target fund-type slots ✓
  - 无 `unknown_upstream_failure_category`、fail-closed、`taxonomy_pending`、`probe_only` ✓
  - 无 quality-gate blocked ✓
  - same-year golden separated ✓
  - 需要 curated-fixture gate ✓
- Criteria 与 Gate 4 plan 修订版 decision rules 完全一致。

**Risk**: 无。

---

## Verdict

**PASS**

Plan 的 Gate 4 reconciliation 正确，subgate 分解遵循第一性原理，fallback fail-closed 语义严格对齐 truth sources，FOF taxonomy 处理保守安全，bond triage 四类根因分类严谨且 same-source，implementation slice 范围最小且全部 gated behind evidence，golden eligibility criteria 充分。

一个 MINOR finding（F3: replacement 候选列表依赖 controller input）已被 plan 的 stop condition 正确覆盖，不阻塞 closeout。

| Finding | Severity | Blocks gate? |
|---------|----------|-------------|
| F1: Gate 4 reconciliation correct | INFO | No |
| F2: Subgate decomposition avoids big-bang | INFO | No |
| F3: Replacement candidate list dependency | MINOR | No |
| F4: Fallback fail-closed rules aligned | INFO | No |
| F5: FOF taxonomy safe | INFO | No |
| F6: Bond triage four-category rigorous | INFO | No |
| F7: Slice scopes minimal and evidence-gated | INFO | No |
| F8: Verifier matrix and golden criteria sufficient | INFO | No |

---

## Truth Source Alignment Confirmation

- [x] Plan 不违反 `AGENTS.md` 硬约束：四层边界未突破、FundDocumentRepository 直访禁止、fallback 分类对齐、extra_payload 禁止、root cause 同源。
- [x] Plan 不违反 `docs/design.md` 非目标：不引入 Host/Agent、不拼接 tool loop、不改 renderer/FQ0-FQ6 阈值或 severity。
- [x] Plan 与 `docs/implementation-control.md` Startup Packet 一致：Gate 4 accepted、next entry point 对齐、accepted artifacts 引用正确。
- [x] Plan 不引入 source/test/product-flow 变更。Non-Goals 完整覆盖所有禁止项。
