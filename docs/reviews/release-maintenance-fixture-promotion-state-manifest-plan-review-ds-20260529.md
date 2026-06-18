# Fixture Promotion State Manifest Plan — Adversarial Review (DS)

日期：2026-05-29
角色：AgentDS plan review worker；不是 controller
Review target：`docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-20260529.md`
Output artifact：`docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-review-ds-20260529.md`

## Reviewed Target And Scope

- **Target**: handoff-ready plan for producing a machine-readable fixture promotion state manifest JSON + evidence artifact under `docs/reviews/`.
- **Scope boundary**: docs/reviews JSON/evidence only; no runtime/preflight consumption, no code/test/score/quality/FQ/golden fixture/promotion changes.
- **Sources of truth verified against**: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, preflight JSON (`golden_readiness_preflight.json`), 12-entry residual disposition manifest (`golden-readiness-residual-disposition-manifest-20260529.json`), residual disposition controller judgment.

## Assumptions Tested

| # | Assumption | Evidence check | Holds? |
|---|-----------|---------------|--------|
| A1 | Preflight has exactly 10 fund/slot rows | Preflight `rows[]` has 10 entries (004393, 004194, 017641, 006597, 110020, 096001, 040046, 019172, 021539, FOF_SLOT) | Yes |
| A2 | Residual manifest has 2 GLOBAL + 10 fund/slot = 12 entries | Residual manifest `entries[]` has 12 entries; 2 with `fund_or_slot="GLOBAL"`, 10 with fund codes or `FOF_SLOT` | Yes |
| A3 | Static disposition manifest has source paths for all fund rows | Static disposition `entries[]` has `snapshot_path`/`score_path`/`quality_gate_path` for all 9 fund rows; `FOF_SLOT` paths are null | Yes |
| A4 | 006597 bond blocker is resolved in preflight | Preflight `006597.resolved_items[]` has `original_blocker_code: "bond_risk_evidence_missing"` with status `blocker_resolved`; `006597.blockers[]` does not include `bond_risk_evidence_missing` | Yes |
| A5 | All residual entries have `promotion_allowed=false` | Every residual manifest entry has `promotion_allowed: false` | Yes |
| A6 | QDII/FOF/110020 are `defer_from_v1` in residual manifest | Residual manifest entries for 096001/040046/019172/021539/017641/FOF_SLOT/110020 all have `decision: "defer_from_v1"` | Yes |
| A7 | 004393/004194/006597 are `needs_fixture_promotion_gate` in residual manifest | Residual manifest entries confirm this decision for all three | Yes |
| A8 | Plan's `fixture_state` enum covers all needed states | Six enum values: `absent`, `not_promoted`, `deferred_from_v1`, `blocked`, `ready_for_future_promotion`, `promoted` | Yes, with derivation caveat (Finding 1) |

## Findings

### 1-未修复-中-`fixture_state` 推导规则不完整，无法让 implementation agent 确定性产出

- **位置**: Manifest Semantics (line 62-77)、Consuming The 12-Entry Residual Disposition Manifest Step 7 (line 180-182)、Required Current Row Mapping (line 192-212)
- **问题类型**: 不可直接实施
- **当前写法**: Plan 在第 180-182 行说 "keep preflight `fixture_promotion_state` as evidence, but normalize output `fixture_state` according to row decision and blocker status"。第 207-212 行给出了当前首批 manifest 的推荐值（`absent` for 004393/004194/006597，`deferred_from_v1` for 其余），但没有给出可复用的推导规则。
- **反例/失败场景**: 当前首批 manifest 之后，如果有新的 fund 加入或有 row 的 blocker 状态改变（例如 006597 的 `strict_golden_not_configured` 被解决但 `fixture_promotion_absent` 仍在），implementation agent 没有规则判断 output `fixture_state` 应该变成什么。`absent` vs `not_promoted` 的语义区分（no accepted state exists vs prior state explicitly says not promoted）在当前所有 row 都从未有过 accepted fixture state 的上下文中无法验证——所有 row 的 preflight `fixture_promotion_state` 要么是 `"absent"` 要么是 `"not_applicable"`，但 preflight 的 `promotion_state` 字段全是 `"not_promoted"`。
- **为什么有问题**: Implementation agent 需要在不咨询 controller 的情况下产出确定性 JSON。如果推导规则不完整，agent 可能：
  - 对所有 `needs_fixture_promotion_gate` row 一律输出 `absent`，即使未来某些 row 的 preflight `promotion_state` 语义不同；
  - 对 deferred row 一律输出 `deferred_from_v1`，即使 `blocked` 也可能适用（plan 在第 199-205 行列出了 `deferred_from_v1` or `blocked` 两种可能）。
- **直接证据**:
  - Plan line 180-182: "normalize output `fixture_state` according to row decision and blocker status" — 没有给出 normalization 函数。
  - Plan line 199: `017641` 的 `fixture_state` 列为 `deferred_from_v1` or `blocked` — 两个值都是 plan 认为允许的，但没有选择规则。
  - Preflight: `004393.fixture_promotion_state = "absent"`, `004393.promotion_state = "not_promoted"` — 两个字段对 `absent` vs `not_promoted` 的选择给出了矛盾信号。
  - Residual manifest: 没有 `fixture_state` 字段，所以没有上游真源可以直接复制。
- **影响**: 实施 Agent 跑偏 / 后续返工 / review 不可验收（reviewer 无法判断 `absent` vs `not_promoted` 的选择是否正确）
- **建议改法和验证点**:
  1. 给出确定性映射规则，例如：
     - 若 residual `decision == "needs_fixture_promotion_gate"` 且 preflight `fixture_promotion_state == "absent"` → output `absent`
     - 若 residual `decision == "defer_from_v1"` 且 preflight `quality_gate_status == "block"` → output `blocked`
     - 若 residual `decision == "defer_from_v1"` 且 preflight `quality_gate_status != "block"` → output `deferred_from_v1`
  2. 或者：在当前首批 manifest 范围内接受推荐值 `absent` / `deferred_from_v1` 作为一次性硬编码，但在 plan 中明确标注该映射仅适用于当前首批、未来 gate 需要独立 plan。
  3. 验证点：用当前 10 个 row 逐一过映射规则，所有 row 产出唯一确定值。
- **修复风险（低）**:
- **严重程度（中）**:

### 2-未修复-中-消费算法 Step 7 "conflict materially" 未定义，stop condition 模糊

- **位置**: Consuming The 12-Entry Residual Disposition Manifest Step 7 (line 182)
- **问题类型**: 不可直接实施 / 契约缺失
- **当前写法**: "if preflight and residual blocker sets conflict materially, stop for controller."
- **反例/失败场景**:
  - 场景 A: preflight 报告 `quality_gate_block` 为 blocker，但 residual manifest 的 `current_blockers` 中没有这个 code（例如 residual 只在 `decision_reason` 中提了 quality block，但没放进 `current_blockers`）。这是 material 还是 immaterial？
  - 场景 B: preflight 的 warning（如 `quality_gate_warn`）不在 residual blocker 中——这算 conflict 吗？根据 plan 的 precedence rules（line 185-190），residual disposition 决定 decision/owner/next_gate，preflight 决定 current blocker observations。如果 preflight 观察到一个 residual 没列出的 blocker，应该 stop 还是继续？
  - 实际检查当前数据：004393 preflight blocker 只有 `fixture_promotion_absent`，residual blocker 也是 `["fixture_promotion_absent"]`。一致。006597 preflight blockers: `strict_golden_not_configured` + `fixture_promotion_absent`，residual blockers: `["strict_golden_not_configured", "fixture_promotion_absent"]`。一致。当前数据没有触发冲突，但 plan 没有定义未来触发时怎么判断。
- **为什么有问题**: Implementation agent 遇到 blocker 差异时需要自行判断是否 stop，这违背了 "stop for controller" 的设计意图——stop condition 本身不应该需要 agent 做 policy 判断。
- **直接证据**: Plan line 182: "if preflight and residual blocker sets conflict materially, stop for controller." "materially" 在全文没有定义。
- **影响**: 实施 Agent 跑偏（可能忽略重要冲突继续执行，也可能在无关差异上 stop）/ review 不可验收
- **建议改法和验证点**:
  1. 将 "materially" 替换为具体条件，例如：
     - preflight blocker 中存在 residual `current_blockers` 不包含的 `severity="block"` code → stop
     - residual `current_blockers` 中存在 preflight 不报告的 code → stop
     - 只有 `severity="warn"` 级别的差异 → 记录到 evidence 但继续
  2. 或者：当前首批 manifest 范围内，如果逐行检查 preflight blockers 与 residual blockers 完全一致（当前事实），则声明 Step 7 不触发，并标注该 stop condition 的具体定义推迟到未来 gate。
  3. 验证点：对当前 10 row 逐一比对 preflight blocker codes 与 residual `current_blockers`，确认无冲突，并在 evidence 中记录比对结果。
- **修复风险（低）**:
- **严重程度（中）**:

### 3-未修复-低中-`blocking_reason` 人类可读字段无填充规则

- **位置**: Schema Entry object fields (line 113)、Field rules (line 138)
- **问题类型**: 不可直接实施
- **当前写法**: `blocking_reason` 定义为 "Human-readable explanation for why `promotion_allowed=false`"，但没有说明如何从 source artifacts 生成。
- **反例/失败场景**: Implementation agent 需要为 10 个 row 各写一段人类可读的 blocking reason。不同 agent 可能从不同 source 提取（residual `decision_reason` vs preflight blocker messages vs 自行组合），导致 manifest 中同一类 row 的 `blocking_reason` 风格和详略不一致。
- **为什么有问题**: 作为 machine-readable manifest 中唯一的人类可读摘要字段，不一致会降低 reviewability——reviewer 无法判断某段 reason 是否正确覆盖了所有 blocker。
- **直接证据**:
  - Plan line 113: 示例 `blocking_reason` 值为 "Fixture state is absent and strict golden correctness remains unresolved." — 这是合成文本，没有标注来自哪些 source 字段。
  - Plan line 138: 字段规则只说 "Human-readable explanation"，没有 derivation rule。
  - Residual manifest 有 `decision_reason` 字段（如 006597: "Immediate fixture candidate only if bond blocker remains closed..."），语义接近但不等同于 `blocking_reason`。
- **影响**: review 不可验收 / 后续返工
- **建议改法和验证点**:
  1. 至少给出组合规则：`blocking_reason` = residual `decision_reason` + 逗号 + 列出 preflight blocker 的 `message` 摘要；或者
  2. 明确允许 implementation agent 自由组合并在 evidence 中记录组合逻辑；或者
  3. 将 `blocking_reason` 标注为 optional 或降低为 best-effort。
  4. 验证点：所有 10 row 的 `blocking_reason` 至少覆盖 residual `decision_reason` 的核心语义。
- **修复风险（低）**:
- **严重程度（低中）**:

## Architecture Boundary Review

Plan 的 scope 限制为 `docs/reviews` JSON/evidence only，不跨越任何架构边界。不引入新的代码、不修改 Service/Host/Agent 层、不改变 `FundDocumentRepository` 边界、不改变 FQ0-FQ6/score/quality/snapshot 语义。四层边界安全。无过度耦合。

## Best-Practice Review

- Plan 明确区分 state ledger vs action ledger 语义，符合 control-plane/data-plane 分离惯例。
- JSON schema 设计了 `schema_version` 字段，为未来演进留了空间。
- Stop conditions 覆盖面广（line 372-380），包含了 promotion/regression/probing/scope creep 等关键风险。
- 验证策略（`python -m json.tool` + 自检脚本）与 JSON-only scope 匹配，没有过度要求 ruff/pytest。
- 推荐 output 为 timestamp 命名而非 `001` 计数器，符合 project convention。

## Optimal-Solution Review

Plan 推荐 first implementation scope 为 docs/reviews JSON/evidence only，明确拒绝 runtime/preflight consumption。这是当前 gate 的最简路径：manifest 作为 control-plane state 记录，不触发任何生产行为变更。更重的方案（同时实现 parser/validator/runtime consumption）会增加不必要的 blast radius。推荐方案是最优的。

## Overengineering Review

无过度设计。Schema 字段集刚好覆盖需求，没有预留未证实的 future fields。`ready_for_future_promotion` enum value 虽未在当前 manifest 中使用，但其语义区分（future controller may set this）是 schema 完整性所需，不算过度设计。

## Overcoupling Review

无过度耦合。Manifest 作为独立 JSON artifact，与 preflight、residual disposition、runtime 之间都是单向引用（manifest 引用 source paths），没有循环依赖或双向绑定。

## Open Questions

1. Plan 在 line 397-401 自述 "No blocking open question"。同意——对 JSON/evidence-only scope 没有 block 级 open question。
2. 未来 preflight consumption 已在 plan line 260-276 中作为 separate gate 处理，当前 gate 不依赖此决策。

## Residual Risks

| Risk | Likelihood | Impact | Suggested tracking |
|------|-----------|--------|-------------------|
| `fixture_state` 推导歧义在未来 gate 中复现 | 中 | 中：manifest 的 fixture_state 可能在不同 gate 间语义不一致 | 在 implementation evidence 中记录当前 10 row 的 fixture_state 选择依据；未来 gate 必须引用该 evidence 或重新 plan |
| 006597 bond blocker regression 检测依赖手动检查 | 低 | 高：如果 regression 未被发现，006597 可能带着 bond blocker 进入 fixture candidacy | Plan 已有 stop condition（line 231），但 detection 依赖 implementation agent 主动检查 source artifacts；建议在 implementation evidence 中显式记录 regression check 的通过证据 |

## Conclusion

**Verdict: `pass-with-risks`**

Plan 对用户需求（schema fields、fixture_state enum、12-entry residual manifest consumption、006597 bond resolved but fixture absent、QDII/FOF/110020 deferred/blocked、no promotion/score/quality/FQ/golden fixture changes、validation policy）的覆盖是完整的。Scope 边界、stop conditions、non-goals 和 validation strategy 与 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md` 一致。

两个中等问题（`fixture_state` 推导规则不完整、material conflict 未定义）和一个低中问题（`blocking_reason` 无填充规则）不会在首批 manifest 的当前数据上触发——当前 10 row 的输入数据没有 blocker 冲突，且 plan 给出了推荐的具体 fixture_state 值。但这些 gap 意味着 implementation agent 在首批数据之外的情况需要自行判断。建议在进入 implementation 前至少对 Finding 1 做最低限度修补（明确首批映射为硬编码、未来需要独立 rule），或由 controller 在 judgment 中接受这些 implementation agent 的合理裁量空间。

## Reviewer Self-Check

- [x] Reviewed target、scope、source of truth、assumptions tested 已写清
- [x] Findings 是 evidence-based、adversarial、可执行的，无 style/nit/speculation
- [x] Open questions、residual risks、tracking destination 与 findings 分开
- [x] Conclusion 为 `pass-with-risks`
- [x] Output path 匹配用户指定路径
