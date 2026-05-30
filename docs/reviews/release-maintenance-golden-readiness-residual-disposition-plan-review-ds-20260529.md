# Golden Readiness Residual Disposition Plan — Plan Review (DS)

日期：2026-05-29

角色：AgentDS plan review worker。不是 controller，不改代码，不 commit/push/PR/merge/release/golden promotion。

Work unit：`golden readiness residual disposition gate` — plan review

Target：`docs/reviews/release-maintenance-golden-readiness-residual-disposition-plan-20260529.md`

## Verdict

**accepted-with-required-fixes**

2 条 required-fix（F1 017641 replace 未传播；F2 blocks_minimum_v1 未入初始 schema），2 条 advisory（F3 006597 coverage 维度说明缺失；F4 fixture promotion manifest 路径未预留）。无 blocking finding。所有边界检查通过。

---

## Boundary Self-Check

| 检查项 | 结论 |
|---|---|
| 是否绕过 golden promotion？ | 否。Plan 全文 `promotion_allowed=false`。 |
| 是否绕过 golden fixture？ | 否。不修改 golden fixture。 |
| 是否削弱 FQ0-FQ6？ | 否。Plan 明确 `不削弱 FQ0-FQ6`（§3 017641 段）。 |
| 是否绕过 FundDocumentRepository？ | 否。年报访问不在本 gate scope。 |
| 是否引入 Host/Agent/dayu？ | 否。纯 disposition docs gate。 |
| 是否误把 deferred 标为 ready？ | 否。全部 `promotion_allowed=false`。 |
| 是否允许 controller 不用户裁决 defer QDII/FOF/110020？ | 是。Plan 将最终裁决权留给 controller（Blocking Questions For Controller），不要求用户升级。 |
| 是否逐项覆盖所有 residual？ | 是。Fixture promotion absent、QDII hard stop、FOF taxonomy/data gap、110020 index evidence insufficient、strict golden correctness/coverage、017641 quality block、006597 resolved invariant 全部有 disposition row。 |

---

## Findings

### F1 [required-fix] — 017641 `replace` disposition 未传播到 disposition matrix 与 JSON schema

**位置：** Plan §3 Decision 3（line 68–72），Disposition Output Matrix 017641 行（line 164），JSON schema 示例（line 126–138）

**直接证据：**

- Prior controller judgment `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-controller-judgment-20260527.md` line 25 明确裁决 `QDII / 017641 / 2024 → replace`。
- 同一 judgment line 60 硬约束：`Preserve 017641 as replace / not_promoted; do not convert it into extractor work or policy change.`
- Plan §3 Decision 3 只说 `defer_from_v1` 并保留 prior `replace/not_promoted` disposition，但 Disposition Output Matrix 行和 JSON schema 示例均未记录 `replace` 语义。
- `defer_from_v1` 的语义是"以后再处理此条目"，而 `replace` 的语义是"此条目已被替换，slot 需要新候选基金"。两者不可互换。

**影响：** 若 disposition manifest 只记 `defer_from_v1` 而不记 `replace`，后续 fixture promotion gate 或 QDII gate 可能误将 017641 当作"暂缓、以后重新评估"，而非"已被替换、不应重新纳入"。这违反了 prior controller judgment 的硬约束。

**建议修法：**

1. Disposition Output Matrix 017641 行的 decision 列改为 `defer_from_v1; replacement_disposition=replace`。
2. JSON schema `entries[]` 增加可选字段 `replacement_disposition`，enum `replace | exclude | null`，017641 条目设为 `"replace"`。
3. Schema constraints 补充：`replacement_disposition=replace` 时，该 entry 不得在后续 gate 中被重新评估为 v1 candidate。

---

### F2 [required-fix] — `blocks_minimum_v1` 推迟到 schema v1.1，但本 gate 就可能需要

**位置：** Plan Schema constraints，line 145–146

**直接证据：**

```text
If controller accepts minimum v1 excluding QDII/FOF/110020,
the manifest may add blocks_minimum_v1=false in a v1.1 schema,
but must not silently redefine blocks_v1.
```

- Plan 的核心推荐是 controller 接受 minimum v1 排除 QDII/FOF/110020（§ Golden v1 Minimum Viable Scope, line 39）。
- Plan Slice A 产出 disposition manifest JSON，Slice B 产出 controller judgment。
- 若 controller 在 Slice B 接受 minimum v1 scope，Slice A 产出的 manifest 无法表达"QDII/FOF/110020 不阻塞 minimum v1"——因为 `blocks_minimum_v1` 字段要等 v1.1 schema。
- 这意味着要么 manifest 产出后立即需要 schema revision，要么 controller acceptance 无法被 machine-readable manifest 捕获。

**影响：** Disposition manifest 失去了表达当前 gate 裁决结果的完整能力。后续 fixture promotion gate 读取 manifest 时，无法区分"阻塞 full v1"与"阻塞 minimum v1"，可能错误地将 QDII/FOF/110020 视为 fixture promotion gate 的前置条件。

**建议修法：**

1. 将 `blocks_minimum_v1` 纳入初始 schema（不推迟到 v1.1），默认值 `true`。
2. Schema constraints 更新为：controller 接受 minimum v1 排除某 entry 时，将该 entry 的 `blocks_minimum_v1` 设为 `false`，`blocks_v1` 保持 `true`。
3. 在 Disposition Output Matrix 增加 `blocks_minimum_v1` 列，QDII/FOF/110020 行初始为 `true`，标注"待 controller 裁决后可能改为 false"。

---

### F3 [advisory] — 006597 `strict_golden_coverage=covered` 与 `strict_golden_not_configured` 的维度差异未说明

**位置：** Plan §2 line 65，§7 line 93–96

**直接证据：**

- Preflight JSON 显示 006597 同时具有 `strict_golden_coverage: "covered"`（fund-level 在 golden answer manifest 中）和 blocker `strict_golden_not_configured`（score correctness 未配置）。
- Plan §2 说 006597 需要处理 `strict_golden_not_configured`，§7 说 `strict golden answer v1 当前只执行 fund-level coverage；score correctness not_configured 仍是 blocker`。
- 两个维度（coverage vs correctness）容易混淆，读者可能认为"covered 就不应该有 not_configured blocker"。

**影响：** 低。Plan 逻辑正确，但措辞可能导致后续 gate 的 worker 误解两个维度的关系。

**建议修法：** 在 §7 或 §2 006597 段增加一句说明：`strict_golden_coverage=covered` 表示该基金代码存在于 golden answer manifest 的 fund-level 索引中；`strict_golden_not_configured` 表示该基金的 score correctness 比对尚未配置（缺少同年的 reviewed golden rows）。两者独立，不矛盾。

---

### F4 [advisory] — Fixture promotion state manifest 路径未预留

**位置：** Plan Slice A line 196–198，Slice C line 235–243

**直接证据：**

- Plan 为 disposition manifest 预留了明确路径：`docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`。
- Plan 为 fixture promotion state manifest 未预留路径，只说"Produce accepted fixture promotion state manifest"（Slice C）。
- `docs/implementation-control.md` Open Residuals 表中 `Fixture promotion state manifest absent` 行也没有预留路径。

**影响：** 低。Fixture promotion gate 的 plan 可以自行定义路径。但若此处预留约定（如 `docs/reviews/fixture-promotion-state-manifest-{date}.json`），可减少后续 gate 的协调成本。

**建议修法：** 在 Slice C 或 Open Residuals 引用中注明建议路径约定，如 `docs/reviews/fixture-promotion-state-manifest-{date}.json`，并注明最终路径由 fixture promotion gate plan 决定。

---

## Coverage Verification

逐项验证 plan 是否覆盖所有 residual：

| Residual | Plan 覆盖？ | 位置 | 结论 |
|---|---|---|---|
| Fixture promotion absent | 是 | §1, Disposition Matrix GLOBAL 行 | `needs_fixture_promotion_gate` |
| QDII hard stop / 4 candidate quality block | 是 | §4, Matrix 096001/040046/019172/021539 行 | `defer_from_v1` / `blocked_until_policy` |
| FOF taxonomy/data gap | 是 | §5, Matrix FOF_SLOT 行 | `defer_from_v1` / `needs_candidate_gate` |
| 110020 index evidence insufficient | 是 | §6, Matrix 110020 行 | `defer_from_v1` / `needs_candidate_gate` |
| Strict golden correctness/coverage | 是 | §7 | 分两类处理：candidate 走 fixture gate，deferred 保持 blocked |
| 017641 quality block | 是 | §3, Matrix 017641 行 | `defer_from_v1`（缺 replace 标注，见 F1） |
| 006597 resolved invariant | 是 | § How To Keep 006597 Bond Blocker Closed | 四项 invariant 控制 + regression 处理 |
| Machine-readable disposition manifest | 是 | §8, Slice A | Schema 设计完整（缺 blocks_minimum_v1，见 F2） |

全部 8 项 residual 均有 disposition row，owner/next_gate/evidence 完整。

---

## Schema Adequacy Assessment

Plan 提出的 JSON schema 逐项对照需求：

| 需求字段 | Schema 支持？ | 备注 |
|---|---|---|
| `decision` | 是 | enum: fix_now / defer_from_v1 / needs_candidate_gate / needs_fixture_promotion_gate / blocked_until_policy |
| `owner` | 是 | 字符串，指向 future gate |
| `next_gate` | 是 | 字符串 |
| `blocks_v1` | 是 | boolean |
| `promotion_allowed` | 是 | boolean，全部 false |
| `evidence_artifacts` | 是 | 字符串数组 |
| `current_blockers` | 是 | 字符串数组（见 F1/F2 建议补充字段） |
| `replacement_disposition` | 否 | 缺失，见 F1 |
| `blocks_minimum_v1` | 否 | 缺失，见 F2 |

Schema 整体足以表达 disposition 语义。F1/F2 补全后可达完整。

---

## Design Boundary Cross-Check

按 `docs/design.md` §12 Plan Review 设计边界检查清单逐项验证：

| 检查项 | 结论 |
|---|---|
| 是否违反 §1.3 非目标？ | 否。不做组合管理、不输出买卖建议、不引入 Host/Agent。 |
| 是否保持四层边界？ | 是。纯 docs/disposition gate，不触及代码边界。 |
| 年报访问是否只通过 FundDocumentRepository？ | N/A。本 gate 不涉及年报访问。 |
| 是否误拼接 Host/tool loop/LLM 写作？ | 否。 |
| 是否遵守 pyproject.toml 工程基线？ | N/A。纯 docs gate。 |
| 是否说明测试覆盖率策略？ | 是。Validation Policy 分 docs-only / JSON-only / runtime-consumption 三级。 |
| License/repo hygiene？ | N/A。不修改代码。 |
| 是否以 Dayu 四层为规则真源？ | 是。无越界。 |
| Success signal 是否可验证且不激励错误接受？ | 是。`promotion_allowed=false` 全表约束 + controller judgment 显式裁决。 |

---

## Self-Check

| 检查项 | 结论 |
|---|---|
| 所有 finding 是否有 plan 位置？ | 是。每条 finding 标注了 plan 行号或章节。 |
| 所有 finding 是否有直接证据？ | 是。引用 prior controller judgment、preflight JSON、plan 原文。 |
| 所有 finding 是否说明了影响和建议修法？ | 是。 |
| 是否误判 plan 为 rejected？ | 否。2 条 required-fix 均可局部修补，不推翻 plan 结构。 |
| 是否越权做 controller 裁决？ | 否。本 review 只输出 findings，controller acceptance 由 controller judgment 执行。 |
| 是否建议改代码？ | 否。 |
| Verdict 是否与 findings 严重性一致？ | 是。required-fix 不阻塞 plan 接受，修正后即可进入 Slice A 实现。 |

**Self-check: pass**
