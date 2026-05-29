# Golden Readiness Residual Disposition Plan — Plan Review (MiMo)

日期：2026-05-29

Reviewer：MiMo；planreview stance。

Review target：`docs/reviews/release-maintenance-golden-readiness-residual-disposition-plan-20260529.md`

## Evidence Read

- `AGENTS.md`
- `docs/design.md` (v2.2)
- `docs/implementation-control.md` (v2.1)
- `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json`
- `docs/reviews/release-maintenance-golden-readiness-preflight-controller-judgment-20260529.md`
- Review target plan artifact

## Findings

### F1 — `blocks_v1` 语义在 deferred 行上混淆

**位置**：Disposition Output Matrix，017641 / QDII / FOF / 110020 行的 `blocks_v1` 列。

**证据**：Preflight JSON 中所有 static disposition entries 均设 `blocks_v1: true`，包括 004393/004194/006597 等 immediate fixture promotion candidates。Plan 的 disposition matrix 对 017641/QDII/FOF/110020 使用 `blocks_v1: true until controller accepts QDII deferred from minimum v1` 的条件语义。

**影响**：`blocks_v1` 在 schema 定义中是 boolean，但 plan 对 deferred 行使用条件式 `true until ...`，未定义 `blocks_v1=false` 的生效时机和触发条件。如果 controller 接受 minimum v1 排除 QDII/FOF/110020，是否自动将这些行 `blocks_v1` 改为 `false`？plan 第 145 行提到 "If controller accepts minimum v1 excluding QDII/FOF/110020, the manifest may add `blocks_minimum_v1=false` in a v1.1 schema"，但这引入了第二个字段 `blocks_minimum_v1` 而未解决原始 `blocks_v1` 的语义。当前 manifest JSON schema 示例中 `blocks_v1: true` 是静态值，没有条件逻辑。

**建议修法**：在 disposition manifest schema 中显式定义 `blocks_v1` 的 controller-judgment-driven 状态转换规则。要么 (a) 在 Slice B controller judgment 中显式裁决每行 `blocks_v1` 的最终 boolean 值，要么 (b) 在 schema 中增加 `blocks_v1_override_pending: boolean` 字段表示等待 controller 裁决，或者 (c) 直接在 plan 中声明：controller 接受 minimum v1 排除 deferred items 后，由 controller judgment artifact 将这些行 `blocks_v1` 更新为 `false`，无需引入 v1.1 schema。

**严重级别**：`warn` — 不阻塞 plan handoff，但 controller judgment 必须在 Slice B 中显式处理此语义。

### F2 — Schema 示例只有一行 entry，未覆盖所有 disposition 类型

**位置**：Minimum JSON schema，`entries` 数组。

**证据**：Schema 示例只包含 `004393` 一个 `needs_fixture_promotion_gate` 条目。实际 disposition matrix 包含 `needs_fixture_promotion_gate`、`defer_from_v1`、`blocked_until_policy`、`needs_candidate_gate` 四种 decision 类型、GLOBAL 行、以及 QDII-FOF 和 110020 等不同 blocker 组合。示例未展示 `fund_or_slot="GLOBAL"` 的写法、`decision` 为 `defer_from_v1` / `blocked_until_policy` 的联合行、或 `evidence_artifacts` 包含多条 controller judgment paths 的情况。

**影响**：Implementer 可能对复合 decision（如 `defer_from_v1 / blocked_until_policy`）的编码方式产生歧义。`fund_or_slot` 字段类型未明确定义是 string fund_code 还是 enum（含 `GLOBAL`、`FOF_SLOT` 等特殊值）。

**建议修法**：在 schema 中增加 `decision` enum 的完整值列表（已列在 schema constraints 中，但示例未体现），并在 schema 说明中明确 `fund_or_slot` 接受 fund code string 或 slot identifier string（如 `GLOBAL`、`FOF_SLOT`）。至少补充一个 GLOBAL 行和一个 `defer_from_v1` 行的示例。

**严重级别**：`warn` — 不阻塞，但减少歧义。

### F3 — 006597 bond blocker invariant 的回归检测依赖前置条件未明确

**位置**：How To Keep 006597 Bond Blocker Closed。

**证据**：Plan 声明 "Any 006597 regression in score/quality/snapshot reclassifies 006597 as `fix_now` or `needs_evidence_gate`, not fixture candidate"。但未定义"回归"的检测机制：是由 fixture promotion gate 手动检查，还是由 preflight 自动检测？Preflight 当前输出中 006597 的 `blocker_resolved` with `original_blocker_code=bond_risk_evidence_missing` 是只读输出；如果 preflight 被重跑且 bond blocker 重新出现，preflight 会将其列为 blocker，但 plan 未明确这种情况下的 disposition 变更流程。

**影响**：如果 fixture promotion gate 在 preflight 重跑之前执行，可能使用已过期的 snapshot/score artifacts，误将 006597 视为 fixture candidate。

**建议修法**：在 Slice C（Future Fixture Promotion Gate）中明确：fixture promotion gate 必须在 gate 开始时重跑或验证 006597 的 latest preflight/snapshot/score/quality artifacts，确认 `bond_risk_evidence_missing` 仍为 resolved，然后才能将 006597 纳入 fixture promotion candidate。如果重跑发现回归，立即 reclassify 为 `fix_now` 或 `needs_evidence_gate`，不进入 promotion。

**严重级别**：`warn` — invariant 本身正确，但检测机制需要更明确的 gate-level 约束。

### F4 — Controller 在不用户裁决下 defer QDII/FOF/110020 的权限边界

**位置**：Golden v1 Minimum Viable Scope。

**证据**：Plan 推荐 "golden v1 不继续追求 QDII / FOF / 110020 纳入 v1；三者均 `defer_from_v1`"，并列出理由。但 plan 同时声明这是 "推荐 controller disposition"，需要 controller 接受。

**影响**：Plan 本身作为 planning worker 产出，正确地将此决策权交给 controller，未擅自执行。但 plan 的 Blocking Questions For Controller 节（第 260-263 行）明确列出三个 controller decisions required before implementation，这意味着 controller 必须在 Slice B 中显式裁决，不能默认接受。这是正确的治理设计。

**结论**：此项无 finding。Plan 正确地将 defer 决策权保留给 controller，未越权。

**严重级别**：`pass` — 无问题。

### F5 — Machine-readable disposition manifest 的必要性论证充分

**位置**：Machine-Readable Disposition Manifest 节。

**证据**：Plan 引用 preflight controller judgment 的 lifecycle_semantics："任一 controller judgment 改变 coverage disposition、owner、revisit condition、blocks_v1 或 promotion disposition 时，停止扩展代码内 manifest"。Plan 正确论证了当前 gate 将 QDII/FOF/110020 从 blocking-v1 改为 `defer_from_v1` 属于 disposition 变化，需要 tracked manifest。

**结论**：此项无 finding。论证充分，schema 设计合理。

**严重级别**：`pass` — 无问题。

### F6 — Schema 不足以表达 `defer_from_v1` 与 `blocked_until_policy` 的联合 decision

**位置**：Disposition Output Matrix，QDII 四候选行。

**证据**：QDII 四候选（096001/040046/019172/021539）的 decision 列写为 `defer_from_v1 / blocked_until_policy`，使用斜杠分隔两个 decision 值。但 schema constraints 定义 `decision` 为 enum，值为 `fix_now` / `defer_from_v1` / `needs_candidate_gate` / `needs_fixture_promotion_gate` / `blocked_until_policy`，是单一值。

**影响**：JSON schema 中 `decision` 是 string enum，无法存储 `defer_from_v1 / blocked_until_policy` 这样的联合值。Implementer 必须选择一个值，或修改 schema 支持数组。

**建议修法**：两种方案：
- (a) 将 `decision` 改为 `string[]` 数组，允许多个 decision 并存。
- (b) 选择一个 primary decision（如 `defer_from_v1`），将 `blocked_until_policy` 作为 metadata 或 reason 字段记录。

推荐方案 (b)，因为 `defer_from_v1` 是实际执行决策，`blocked_until_policy` 是原因说明，可以放入 `decision_reason` 或 `notes` 字段。

**严重级别**：`block` — schema 与 matrix 不一致，必须在 Slice A 中解决才能产出可解析的 JSON。

### F7 — 006597 的 `strict_golden_not_configured` blocker 处理路径未完全闭合

**位置**：Disposition Output Matrix，006597 行。

**证据**：006597 行列出 blockers 为 `strict_golden_not_configured`、`fixture_promotion_absent`、`quality_gate_warn`。Plan 在 §2（004393/004194/006597 Immediate Fixture Promotion Candidates）中说 006597 "还必须处理 `strict_golden_not_configured` 与 fixture absent"，但未明确 `strict_golden_not_configured` 的处理方式。Preflight JSON 中 006597 的 blockers 包含 `strict_golden_not_configured`。

**影响**：`strict_golden_not_configured` 是全局状态（strict golden answer v1 当前只执行 fund-level coverage；score correctness `not_configured` 仍是 blocker），不是 006597 特有的问题。Plan 在 §7（Strict Golden Correctness / Coverage Incomplete）中说明 "score correctness `not_configured` 仍是 blocker，不能通过文档声明解除"，但未明确此 blocker 如何影响 006597 的 fixture promotion gate 路径。

**建议修法**：在 §2 的 006597 前提条件中，明确 `strict_golden_not_configured` 是全局 blocker，fixture promotion gate 必须先解决或显式 accept 这个 blocker 的 residual owner，才能将 006597 纳入 promotion。或者明确：`strict_golden_not_configured` 不阻塞 fixture promotion state manifest 的创建（因为 fixture promotion state manifest ≠ golden promotion manifest），但阻塞最终的 golden promotion。

**严重级别**：`warn` — 不阻塞 plan handoff，但 fixture promotion gate 的 plan 必须明确处理此 blocker。

## Boundary Checks

### B1 — 是否直接服务 phase 目标

**结论**：是。当前 phase 是 release maintenance，当前 gate 是 golden readiness residual disposition gate。Plan 直接服务于该 gate 的目标：对 preflight remaining blockers 做 controller-accepted residual disposition matrix。

### B2 — 是否逐项覆盖所有 required blockers

| Blocker | Plan 覆盖 | 行号 |
|---|---|---|
| fixture_promotion_absent | §1, §2, §7 | 全局 + 逐基金 |
| QDII hard stop | §4 | 017641 + 四候选 |
| FOF data/taxonomy gap | §5 | FOF_SLOT |
| 110020 not promoted / index evidence insufficient | §6 | 110020 |
| strict golden correctness/coverage | §7 | 全局 + 逐基金 |
| 017641 quality block | §3 | 017641 |
| 006597 resolved invariant | How To Keep 006597 Bond Blocker Closed | 006597 |

**结论**：全部覆盖。

### B3 — 是否允许 controller 在不用户裁决下 defer QDII/FOF/110020

**结论**：否。Plan 将 defer 决策权保留给 controller（Blocking Questions For Controller 节），controller 必须在 Slice B 中显式裁决。Plan 作为 planning worker 未越权执行。

### B4 — 是否误把 deferred 当 ready

**结论**：否。所有 deferred 行的 `promotion_allowed=false`，`blocks_v1=true`（有条件语义，见 F1）。Plan 明确声明 "本 gate不允许把它们标为 ready"。

### B5 — 是否绕过 promotion/golden fixture/FQ0-FQ6/FundDocumentRepository/Host-Agent-dayu 边界

**结论**：否。Plan 是 docs-only artifact，不修改代码、runtime、score、quality、snapshot、golden answer、golden fixture、fixture promotion state、FQ0-FQ6、FundDocumentRepository、Host/Agent/dayu。Validation Policy 节明确说明。

### B6 — Gate 分类

**结论**：Plan 未显式声明 gate 分类。`docs/implementation-control.md` 的 Startup Packet 已将 next gate 分类为 `heavy`。Plan 作为 planning worker artifact 属于 heavy gate 的输入，符合 `AGENTS.md` 的 Gate 轻重分类规则（涉及 golden baseline promotion 相关 disposition）。

## Self-Check

| 检查项 | 结论 |
|---|---|
| 是否读取所有 required evidence | pass |
| 是否逐项覆盖所有 blockers | pass |
| 是否有 blocking finding | 1 (F6 — schema decision enum 与 matrix 联合值不一致) |
| 是否有 warn finding | 4 (F1, F2, F3, F7) |
| 是否误把 deferred 当 ready | pass |
| 是否绕过边界 | pass |
| Self-check final | blocked — F6 需要 schema 修复 |

## Verdict

**accepted-with-required-fixes**

Plan 整体设计正确，disposition matrix 覆盖完整，治理边界清晰。但存在一个 blocking finding（F6）需要在 Slice A 实施前修复：schema `decision` enum 与 matrix 中 QDII 行的联合 decision 值不一致。建议在 Slice A 中选择 primary decision + `decision_reason` 方案，或改为 `decision` 数组。

其余四个 warn findings（F1/F2/F3/F7）不阻塞 plan handoff，但应在 Slice B controller judgment 或 Slice C fixture promotion gate 的 plan 中显式处理。
