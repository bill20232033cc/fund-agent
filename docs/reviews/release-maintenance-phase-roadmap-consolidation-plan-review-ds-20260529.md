# Release Maintenance Phase Roadmap Consolidation Plan — Independent Review (DS)

日期：2026-05-29

审查者：AgentDS，独立 plan reviewer。未启动 `/gateflow`，未实现代码，未修改生产代码，未修改被审查 plan，未 commit/push/PR/merge/release/promote。

## Review Scope

审查目标：`docs/reviews/release-maintenance-phase-roadmap-consolidation-plan-20260529.md`

审查标准：计划是否 handoff-ready，能否安全交给后续 gate 产出 docs-only roadmap artifact 和最小 control-doc 更新。

## Truth Source Cross-Reference

审查依据：

| 来源 | 路径 | 用途 |
|------|------|------|
| AGENTS.md | 根目录 | 规则真源、gate 分类、四层边界、FundDocumentRepository、fallback taxonomy |
| design.md | `docs/design.md` (v2.2) | 设计真源、fund_type/CHAPTER_CONTRACT/ITEM_RULE/preferred_lens 机制 |
| implementation-control.md | `docs/implementation-control.md` (v2.1) | Startup Packet、accepted artifacts、open residuals、next entry point |
| residual disposition manifest | `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` | control-plane residual decisions |
| fixture promotion state manifest | `docs/reviews/fixture-promotion-state-manifest-20260529.json` | fixture_state、promotion blockers |
| strict golden controller judgment | `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md` | 004393/004194/006597 条件裁决 |
| drawdown metric controller judgment | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-controller-judgment-20260529.md` | 006597 bond blocker 关闭证据 |
| typed NAV controller judgment | `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-controller-judgment-20260528.md` | typed NAV boundary、raw-unit ineligibility |
| CSRC EID source evaluation judgment | `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-controller-judgment-20260528.md` | CSRC EID primary candidate |
| CSRC EID normalization judgment | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-controller-judgment-20260529.md` | CSRC EID runtime typed source |
| source provenance rerun judgment | `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-controller-judgment-20260527.md` | 110020/017641 provenance terminal states |
| post-021539 consolidation judgment | `docs/reviews/release-maintenance-consolidation-post-021539-disposition-controller-judgment-20260527.md` | QDII probing stopped、FOF taxonomy gap |

## Focus Area Findings

### F1: Five Route Taxonomy Correctness

**Verdict: PASS**

五条路线与所有 truth sources 一致，不存在分类错误或边界模糊：

- **Route 1 (Minimum Golden V1 Readiness)**：正确聚焦 004393/004194/006597 三个 strict correctness candidate，并正确排序为 strict correctness → coverage decision → fixture promotion-prep → minimum v1 promotion。与 strict golden controller judgment (lines 15-27) 的决策表完全一致。与 implementation-control.md Startup Packet 的 next entry point (`004393 / 004194 / 006597 strict correctness follow-up gate`) 对接正确。

- **Route 2 (Deferred Coverage)**：QDII candidates (`096001`/`040046`/`019172`/`021539`)、`017641`、`FOF_SLOT`、`110020` 全部正确标记为 deferred from minimum v1、blocks_v1=true。与 residual disposition manifest 的 `blocks_minimum_v1=false, blocks_v1=true` 条目完全一致 (JSON lines 152-308)。与 fixture promotion manifest 的 `deferred_from_v1` 状态一致。

- **Route 3 (Source/Provenance Hardening)**：正确记录 CSRC EID typed source 已 accepted、raw_unit_nav 仍 ineligible、stock-sdk evidence-only。residual list (source_query_params split、CSRC EID generalization、parser/schema drift 等) 与 implementation-control.md Open Residuals (lines 163-168) 一致。

- **Route 4 (Future Host/Agent/Dayu Architecture)**：正确保持当前确定性过渡路径、future Host=`dayu.host`、future Agent=`dayu.engine`。与 AGENTS.md (lines 81-82) 和 design.md (lines 59-66) 的 Dayu 裁决一致。

- **Route 5 (Artifact/Manifest Lifecycle)**：正确区分 control-plane evidence vs promotion manifest vs runtime consumption。两个 manifest 的 `promotion_manifest: false` 字段 (residual manifest line 17, fixture manifest line 6) 直接证实这一区分。

**证据**：所有五条路线的关键声明均有 truth source 直接支撑，无跨路线污染。

### F2: 006597 Bond Blocker Closed But Not Promotion-Ready

**Verdict: PASS**

Plan 在三个位置正确处理了 006597 的微妙状态：

1. **Direct Evidence Summary (plan line 78)**：明确 bond blocker 已 closed，引用 drawdown controller judgment 的 max drawdown `-0.10%` 证据。drawdown judgment (line 62) 直接证实。

2. **Not Ready 声明 (plan line 79)**：明确 006597 `fixture_state="absent"`、blockers 包括 `strict_golden_not_configured` 和 `fixture_promotion_absent`、`promotion_allowed=false`。fixture promotion manifest (lines 115-153) 直接证实：`fixture_state: "absent"`、`promotion_blockers: ["strict_golden_not_configured", "fixture_promotion_absent"]`、`promotion_allowed: false`。

3. **Route 1 Must Not Include (plan lines 124-129)**：禁止将 006597 报告为 promotion-ready。

**证据**：plan 从未声称 006597 是 promotion-ready；`closed but not promotion-ready` 的表述精确匹配 truth sources。

### F3: 004393 Partial Coverage and 004194 index_profile-only/P0 Coverage Next Gates

**Verdict: PASS**

Plan 正确反映 strict golden controller judgment 的裁定：

- **004393** (plan line 80)：`conditional_candidate_pending_partial_coverage_decision`、`9/150` comparable、P0 `9/11`、P1 `0/10`。strict golden judgment (line 17) 直接证实 decision 字段。fixture promotion manifest (lines 50-81) 补充确认 `fixture_state: "absent"`、`quality_gate_status: "warn"`。

- **004194** (plan line 81)：`conditional_candidate_pending_p0_coverage_decision`、仅五个 `index_profile.*` records、P0 strict correctness coverage 为零。strict golden judgment (line 18) 直接证实。fixture promotion manifest (lines 82-113) 补充确认 `fixture_state: "absent"`。

- **Next Gate Order** (plan lines 227-232)：正确将 004393 partial coverage decision 和 004194 P0 coverage decision 列为 Route 1 的独立 gate。与 strict golden judgment 的 Next Entry Point (lines 69-76) 对接正确。

**证据**：两个 fund 的 coverage 状态描述与 strict golden judgment 和 fixture manifest 三方一致。

### F4: QDII/FOF/110020/017641 Deferred from Minimum V1, Still Full-V1 Blockers

**Verdict: PASS**

Plan 对所有 deferred items 的 `blocks_minimum_v1=false, blocks_v1=true` 处理正确：

| Item | Plan Claim | Residual Manifest Evidence | Fixture Manifest Evidence |
|------|-----------|---------------------------|--------------------------|
| QDII (4 funds) | deferred, blocks full v1 | `blocks_minimum_v1: false, blocks_v1: true` (lines 59-61, 152-153, 178-179, 203-204, 228-229, 253-254) | `fixture_state: "deferred_from_v1"` (lines 191, 227, 263, 299) |
| 017641 | deferred, blocks full v1 | `blocks_minimum_v1: false, blocks_v1: true` (lines 152-153) | `fixture_state: "deferred_from_v1"` (line 155) |
| FOF_SLOT | deferred, blocks full v1 | `blocks_minimum_v1: false, blocks_v1: true` (lines 279-280) | `fixture_state: "deferred_from_v1"` (line 338) |
| 110020 | deferred, blocks full v1 | `blocks_minimum_v1: false, blocks_v1: true` (lines 305-306) | `fixture_state: "deferred_from_v1"` (line 371) |

Plan 正确区分 policy decisions 与 implementation work (plan lines 143-145)，与 QDII probing stopped 裁决 (post-021539 judgment lines 26-28) 一致。

**证据**：所有 deferred items 的双重 block 状态在两个 manifest 中均可直接验证，plan 未将任何 deferred item 误报为 ready。

### F5: Control-Doc Update Compression

**Verdict: PASS**

Plan 的 Slice B (lines 252-266) 定义了最小 control-doc 更新策略：

- **Allowed edits**：Startup Packet current status、current roadmap pointer、accepted artifacts index、open residuals (five-route taxonomy)、next entry point。与 AGENTS.md (lines 47-50) 的控制面更新原则一致。

- **Forbidden edits**：long logs、historical narrative appendices、promotion status changes、runtime/preflight manifest consumption claims、architecture implementation claims。全部对应当前 guardrails。

- Plan 的 Non-Goals (line 44) 明确禁止修改 `docs/implementation-control.md` 于 planning worker 阶段，只允许后续 gate 做最小更新。与 implementation-control.md 的压缩先例 (post-021539 judgment line 24) 一致。

**证据**：更新范围严格限定，不违反 AGENTS.md 的 control doc 压缩纪律。

### F6: Facet Inference / ITEM_RULE Routing Residual

**Verdict: PASS**

Plan 的 Route 4 中 facet inference 设计 (lines 175-188) 正确且完整：

- **fund_type vs facet 边界 (plan line 178)**：`fund_type` 是 preferred_lens 和 ITEM_RULE 使用的粗粒度标准类型；facets 是更细粒度的证据驱动特征。与 design.md §3.4 的 fund_type 分类和 ITEM_RULE 的 `facets_any` 触发机制 (design.md lines 180-181) 一致。

- **Implicit unmodeled facets (plan lines 179-183)**：Bond (short-duration、credit-rating 等)、Index/enhanced index (ETF-linked、tracking-error 等)、QDII (QDII-FOF、FX 等)、FOF (pure FOF、holding look-through)。这些细分维度在当前 design.md 的 fund_type 体系中以 preferred_lens 的差异形式隐含存在，但未作为独立 facet 建模。Plan 的枚举是合理的需求提炼。

- **Deterministic inference 要求 (plan line 184)**：`must be deterministic and evidence-based; must consume structured annual-report/source facts and expose missing/ambiguous states, not LLM guesses`。与 AGENTS.md 的证据要求 (line 87) 和 design.md 的确定性原则一致。

- **Ownership (plan line 186)**：Agent/Fund 层，因为涉及 fund type、CHAPTER_CONTRACT、ITEM_RULE、preferred_lens 和 evidence audit。与 AGENTS.md 归属规则 (lines 137-138) 一致：CHAPTER_CONTRACT 解析和 preferred_lens 应用默认属于 Agent 层 `fund_agent/fund`。

- **不实现 (plan line 188)**：`Do not implement facet inference in this roadmap gate`。正确。

**证据**：facet inference 设计不违反任何 truth source，ownership 归属正确，且明确标记为 future gate。

### F7: No Non-Goal Violations

**Verdict: PASS**

逐项检查 plan 的 Non-Goals (lines 42-51) 和 Stop Conditions (lines 298-307)：

| Non-Goal | Plan Compliance | Evidence |
|----------|----------------|---------|
| 不修改生产代码 | Worker Self-Check (line 12) 明确禁止 | Plan 只允许新增一个 .md artifact |
| 不修改 golden answer/fixture | Non-Goals line 43 | 无相关声明 |
| 不修改 implementation-control.md (本 worker) | Non-Goals line 44 | 后续 gate 的 Slice B 才做 |
| 不执行 golden promotion | Non-Goals line 45 | Route 1 Must Not Include (line 129) 双重确认 |
| 不改变 score/quality gate 语义 | Non-Goals line 46 | 无相关声明 |
| 不重启 QDII probing | Non-Goals line 47 | Route 2 (line 137) 确认 QDII probing stopped |
| 不把 deferred 报告为 ready | Non-Goals line 48 | Route 2 Must Not Include (line 145) |
| 不创建 Host/Agent/dayu package | Non-Goals line 49 | Route 4 (line 170) 确认 no package creation |
| 不 PR/push/merge/release | Non-Goals line 50 | Worker Self-Check (line 13) |
| 不把显式参数藏入 extra_payload | Non-Goals line 51 | Route 4 (line 173) 确认 |

Stop Conditions 同样完整：所有 8 条 stop condition 都有对应的 plan 内约束。

**证据**：plan 未违反任何声明的 non-goal，stop conditions 覆盖了所有关键风险边界。

## Additional Observations

### O1 (INFO): Route 4 Facet Detail Level

Route 4 的 facet inference 部分 (lines 175-188) 细节丰富，包含了具体的 implicit unmodeled facets 枚举。这对 roadmap artifact 是有价值的设计方向，但后续 roadmap gate 应确保不把 facet 枚举误解为已接受的 facet taxonomy——当前状态是设计候选，需单独的 design gate 裁决。

### O2 (INFO): Residual Table — Source/Provenance Items

Residual table 要求 (plan line 219) 对 source/provenance items 的 `blocks_full_v1` 标记为 "should be explicit per item"。后续 roadmap artifact 应确保 Route 3 中每个 source/provenance residual 都有显式的 `blocks_minimum_v1` 和 `blocks_full_v1` 赋值，而非使用 "generally" 的集合表述。

### O3 (LOW): Preflight Artifacts Not Directly Quoted

Plan 引用 golden readiness preflight JSON/MD 作为 truth source (line 60)，但 plan 内未直接摘录 preflight 的具体数值。由于 residual disposition manifest 和 fixture promotion manifest 都以 preflight 为 source，且所有 controller judgment 都确认 `overall_status=block`，这一间接引用是可接受的。建议 roadmap artifact 在关键结论旁直接引用 preflight JSON 的具体字段路径（如 `overall_status`、`per_fund_readiness` 等）。

## Verdict

**PASS**

本 plan 是 handoff-ready 的 docs-only roadmap/control update 计划：

- 五条路线分类正确，与所有 truth sources 一致。
- 006597 bond blocker closed / not promotion-ready 的双重状态精确。
- 004393/004194 的 coverage 状态和 next gate 准确反映 strict golden controller judgment。
- QDII/FOF/110020/017641 的 deferral 状态在两个 manifest 中均可验证。
- Control-doc 更新策略遵守 AGENTS.md 压缩原则。
- Facet inference 设计正确，ownership 归属 Agent/Fund 层，明确不在此 gate 实现。
- 无 non-goal 违反。

三项 observations (O1-O3) 均为 INFO/LOW 级别，不构成阻塞。建议 controller 在接受前确认 O2 (source/provenance items 显式 blocks_full_v1) 在 roadmap artifact 中被落实。

## Self-Check

- 审查依据：7 个 truth source 文件的直接内容，非二手转述。
- 每条 finding 均标注了 truth source 的具体行号或 JSON 路径。
- 未修改任何文件（除本 review artifact）。
- 未启动 /gateflow，未实现代码，未 commit/push/PR。
- 审查结论：PASS，handoff-ready。
