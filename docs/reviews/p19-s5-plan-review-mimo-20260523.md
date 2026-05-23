# P19-S5 Plan Review - Mimo - 2026-05-23

## Findings

### F1-未修复-严重-候选源矩阵遗漏 `akshare.stock_a_ttm_lyr()`，导致 all-A PE source gate 从错误前提出发

- **位置**: `docs/reviews/p19-s5-all-a-pe-source-gate-plan-20260523.md:51`, `docs/reviews/p19-s5-all-a-pe-source-gate-plan-20260523.md:74`, `docs/reviews/p19-s5-all-a-pe-source-gate-plan-20260523.md:322`, `docs/implementation-control.md:210`, `docs/design.md:841`
- **问题类型**: open question 未收敛 / 候选源遗漏 / 数据源证据错误 / 不可直接交给 source worker
- **当前写法**: plan 把当前已知证据写成 “all-A PB is available through `stock_a_all_pb()`, but all-A PE history remains unresolved”，候选源矩阵列了 `stock_a_all_pb()`、`stock_a_lg_indicator()`、market/index PE/PB、直接 Legulegu endpoint、东方财富/中证/交易所路径，但没有列 `stock_a_ttm_lyr()`。
- **反例/失败场景**: 当前仓库 `.venv` 的 akshare `1.18.60` 顶层已经导出 `stock_a_ttm_lyr()`，本地源码位置为 `.venv/lib/python3.11/site-packages/akshare/stock_feature/stock_ttm_lyr.py`，模块描述是“全部 A 股-等权重市盈率、中位数市盈率”，URL 为 `https://www.legulegu.com/stockdata/a-ttm-lyr`，接口调用 `https://legulegu.com/api/stock-data/market-ttm-lyr`。本地 live probe 返回：
  - `stock_a_ttm_lyr()`：`rows=5186`，字段含 `middlePETTM`, `averagePETTM`, `middlePELYR`, `averagePELYR`，日期 `2005-01-05` 到 `2026-05-22`。
  - `stock_a_all_pb()`：`rows=5184`，字段含 `middlePB`, `equalWeightAveragePB`，日期 `2005-01-04` 到 `2026-05-22`。
  - 两者共同日期数 `4828`，共同日期 `2005-01-05` 到 `2026-05-22`。
- **为什么有问题**: `docs/design.md` §11 要求全 A 温度计必须基于 PE 历史 + PB 历史、字段语义、共同日期、许可和缺失规则。`stock_a_ttm_lyr()` 不是边缘候选，而是当前 akshare 包内明确命名的全 A PE 历史接口；遗漏它会让 source worker 只重复验证已知失败路径，并可能错误输出 `BLOCKED_DEFERRED`。这也直接影响 `docs/implementation-control.md` P19-S5 exit criteria 对“全 A PE 历史来源通过验证”的裁决。
- **影响**: 当前 plan 不能作为 P19-S5 source gate 执行入口；它的候选矩阵不完整，且 Current Known Evidence 与本地环境事实冲突。继续按该 plan 推进会产生错误 closeout，或延误一个可能满足 PE+PB source gate 的同源 Legulegu/akshare 路径。
- **建议改法和验证点**:
  - 将 `akshare.stock_a_ttm_lyr()` 加入 Akshare / Legulegu 必探候选，并要求 source worker 记录源码 URL、请求参数、字段语义、行数、日期范围、缺失/非正值规则、license/access、与 `stock_a_all_pb()` 的共同日期数。
  - 把 `middlePETTM` / `middlePELYR` / `averagePETTM` / `averagePELYR` 的语义选择列为 gate 裁决点；不能只因接口存在就直接实现。
  - 重新评估 outcome：如果 `stock_a_ttm_lyr()` + `stock_a_all_pb()` 的 identity、字段语义、许可、共同日期和 fixture 均通过，应进入 `ACCEPT_IMPLEMENTATION_PLAN` 后的独立 implementation plan/review，而不是继续 `BLOCKED_DEFERRED`。
  - 更新 Current Known Evidence，避免继续沿用“all-A PE history unresolved”的绝对表述；在重跑 source feasibility 前，只能说“all-A PE source candidate exists and requires contract validation”。
- **修复风险**: 中
- **严重程度**: 严重

未发现以下方面的独立 blocker：

- plan 对 all-A thermometer 必要事实的定义正确：要求全 A PE 历史、全 A PB 历史、字段语义、共同日期、许可、缺失规则和最新日期。
- plan 明确拒绝 PB-only、PE-only、current-only、board-level、相邻指数、有知有行页面抓取，以及未经过单独设计的逐股重建。
- plan 把逐股重建 all-A PE 归入 `NEEDS_DESIGN_CHANGE`，并要求设计/storage/cost/license gate；这符合当前 P19-S5 source gate 边界。
- source gate 通过后的 outline 保持 Capability data / cache / analysis / Service / UI 分层，并明确下一步是 implementation plan/review，不直接编码。
- 除遗漏 `stock_a_ttm_lyr()` 外，计划覆盖了用户要求的 akshare、Legulegu、中证、交易所、东方财富大类和 package discovery 流程。

## Questions

1. `stock_a_ttm_lyr()` 的 all-A identity 是否等同于设计中的 `wind_all_a` / “万得全 A / 全 A 市场”，还是需要改名为 Legulegu 全部 A 股市场温度计并更新用户可见描述？
2. PE 字段应选 `middlePETTM` 还是 `middlePELYR`，是否与现有指数温度计使用的 `滚动市盈率中位数` 语义对齐？
3. `stock_a_ttm_lyr()` 和 `stock_a_all_pb()` 的 Legulegu access/license 是否满足生产使用，还是只能作为研究/对比输入？
4. 若 `stock_a_ttm_lyr()` 通过 source contract，P19-S5 是否仍需要与有知有行页面温度方向对比作为 acceptance signal，还是只在 implementation plan 阶段记录为 residual validation？

## Verdict

BLOCKED
