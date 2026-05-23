# P19-S5 All-A PE Source Gate Plan Review - GLM - 2026-05-23

Reviewed target: `docs/reviews/p19-s5-all-a-pe-source-gate-plan-20260523.md`

## Findings

### F1-未修复-高-ACCEPT gate 没有把“等权/中位数同口径”写成硬门槛，仍可能接受不符合当前温度计设计的全 A PE/PB

- **位置**: `docs/reviews/p19-s5-all-a-pe-source-gate-plan-20260523.md:18-45`, `docs/reviews/p19-s5-all-a-pe-source-gate-plan-20260523.md:146-158`, `docs/reviews/p19-s5-all-a-pe-source-gate-plan-20260523.md:172-182`
- **问题类型**: 契约缺失 / source semantics gate 不够硬 / 设计边界
- **当前写法**: 计划要求记录 `Field semantics`，并在 `ACCEPT_IMPLEMENTATION_PLAN` 中要求 PE/PB 字段“have documented semantics”，且来自一个兼容 source family 或两个可合并 source contracts。
- **反例/失败场景**: 如果 source gate 找到一个 exact all-A PE 历史，但字段是市值加权 PE、静态 PE 或另一种非中位数口径；同时 PB 使用 `stock_a_all_pb()` 的中位数 PB。当前 acceptance 文本可能因为“identity exact、PE/PB 都有历史、语义已记录、日期可合并”而放行，但这并不满足 design 的“等权 PE/PB 中位数历史分位数综合”。
- **为什么有问题**: P19-S5 的首要风险正是“找到一个市场 PE 数字就误当全 A 温度计”。当前计划已经排除了 PB-only、PE-only、current-only、board-level、adjacent-index 和逐股重建，但对“exact all-A 但 weighting / metric type 不符合 design”的情况只要求记录语义，没有明确要求拒绝或进入 `NEEDS_DESIGN_CHANGE`。
- **直接证据**: `docs/design.md:841-845` 选择“等权中位数”和“PE 分位 + PB 分位各 50%”；`docs/design.md:850-858` 把输入定义为 A 股市场或目标指数成分的当日 PE/PB 与历史 PE/PB 序列，并显式写 PE/PB 等权中位数；`docs/design.md:886` 明确 PB-only 不可冒充完整温度计。计划的 accept 条件只写 documented semantics，没有写必须为 current design-compatible semantics。
- **影响**: source worker 可能把一个“字段存在且可合并”的 exact all-A 市场估值序列标成 accepted，后续实现会在用户界面输出“全 A 温度计”，但实际计算口径偏离设计，且偏离不再经过 design change gate。
- **建议改法和验证点**: 在 `ACCEPT_IMPLEMENTATION_PLAN` 增加硬条件：PE 与 PB 必须同为 design-compatible 的等权/中位数口径，且 PE 类型（TTM/LYR/static）与既有 P19 指数温度计所选 PE 口径一致或有单独设计裁决；若 exact all-A 数据存在但 weighting、统计口径、PE 类型或 PB 口径与 design 不一致，必须归入 `NEEDS_DESIGN_CHANGE`，不得直接 accept implementation plan。Probe matrix 中也应增加 `weighting_method`、`statistic_type`、`pe_basis`、`pb_basis` 或等价字段。
- **修复风险**: 低
- **严重程度**: 高

## Questions

- 对网络失败的操作口径是否需要更机械化？计划已经把 `network_unavailable` 独立分类，并要求“network failures prevent source proof”时 `BLOCKED_DEFERRED`，但 source worker 是否需要在不同时段重试、记录 HTTP 状态/异常链、或用 known-good negative controls 区分网络抖动与 source missing？
- `stock_a_all_pb()` 的 PB 字段语义已作为既有证据带入，但 P19-S5 是否要求重新冻结 source-shaped fixture，并证明当前安装版本的 URL、token、列名、日期范围仍与旧证据一致？计划写了 revalidate，建议 controller 明确这是 source gate 的必做项。
- 如果找到 exact all-A PE 与 PB，但两个来源的 universe definition 都称“全 A”却来自不同供应商，是否需要额外的 identity reconciliation 证据，例如指数/市场定义、排除规则、上市板块范围、ST/退市/北交所处理？

## Verdict

PASS_WITH_FINDINGS

计划总体是可接受的 source feasibility gate：它不会把一个孤立市场 PE 数字直接当作全 A 温度计；候选来源覆盖了 akshare package discovery、Legulegu direct endpoints、Eastmoney spot/valuation discovery、官方 index/value pages；也明确要求 PE/PB 历史、common dates、source contracts、license/access、network failure 分类，并保持不改 `analyze`、不做 PB-only、不逐股重建、不使用 public-page scrape / Dayu / `extra_payload`。

但在进入 source worker 前应修正 F1：把“PE/PB 字段语义必须匹配当前 design 的等权/中位数同口径；否则进入 NEEDS_DESIGN_CHANGE”写成 acceptance hard gate。否则仍存在 exact all-A 但口径错误的数据被误接收的风险。
