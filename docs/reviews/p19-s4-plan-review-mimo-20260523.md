# P19-S4 Plan Review - Mimo - 2026-05-23

## Findings

### F1-未修复-中-Source gate resolved 后的实现计划只覆盖现有 akshare/Legulegu schema，不覆盖设计允许的官方中证/交易所来源

- **位置**: `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md:111`, `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md:140`, `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md:155`, `docs/design.md:841`, `docs/design.md:895`
- **问题类型**: 不可直接实施 / 外部协议边界 / 测试缺口
- **当前写法**: plan 正确把当前实现停在 source feasibility gate，并要求 exact PE/PB source evidence；但 “Implementation Plan If Source Gate Is Resolved” 只描述扩展 `SUPPORTED_INDEX_SYMBOLS`、复用 `stock_index_pe_lg/pb_lg` 的 `滚动市盈率中位数` / `市净率中位数` 列。
- **反例/失败场景**: 下一步 source feasibility 如果从中证指数官方或交易所公开接口找到目标指数 PE/PB 历史，而不是 akshare `stock_index_pe_lg/pb_lg` 同构接口，实施 Agent 仍会被计划引导到“只加 symbol map / 保持列名”的路径。官方源很可能有不同 endpoint、字段名、日期格式、许可约束、分页/下载形态和失败语义，不能直接套现有 `AkshareIndexThermometerSource`。
- **为什么有问题**: `docs/design.md` 明确数据来源是 “akshare + 中证指数官方或 akshare 指数估值接口”，Capability data 只返回结构化数据且不参与 Service/UI 输出格式。现有实现 `fund_agent/fund/data/thermometer_source.py:19` 只支持 `000300/000905` 的 akshare symbol map，`fund_agent/fund/data/thermometer_source.py:94` 之后按该 map 调用同一 PE/PB schema。若 source gate 被官方源解决，当前 plan 不足以约束新 Capability data adapter、schema freeze、source name、permission/use terms、fail-closed taxonomy 和 fixture 测试。
- **影响**: source gate 一旦“非 akshare 同构”方式通过，计划不能安全交给 implementation agent；容易把官方源解析硬塞进现有 akshare 类，或把 source-specific 逻辑泄漏到 Service/UI。
- **建议改法和验证点**: 把 conditional implementation 分成两条明确分支：
  - 若 exact source 是 `akshare.stock_index_pe_lg/pb_lg` 同构 symbol，只执行当前 Slice 1-4。
  - 若 exact source 是中证/交易所/其他公开源，先补独立 source feasibility artifact 和 mini implementation plan：定义新的 Capability data source 或 adapter、字段契约、日期/数值 schema、许可说明、失败分类、fixture 原始样本、source_name、cache 兼容性测试；Service 仍只通过现有 Protocol/`ThermometerService` 编排。
- **修复风险**: 中
- **严重程度**: 中

### F2-未修复-低-当前 blocked 证据足以阻断 akshare 1.18.60 路径，但不足以声明所有 P19-S4 source 路径已穷尽

- **位置**: `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md:7`, `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md:47`, `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md:270`, `docs/design.md:841`
- **问题类型**: open question 未收敛 / 范围表述
- **当前写法**: plan 记录 akshare `1.18.60` 的 `stock_index_pe_lg/pb_lg` 对五个目标指数 KeyError，且源码 symbol map 不含目标指数；并建议 controller 可 “close P19-S4 as blocked/deferred with this artifact as evidence”。
- **反例/失败场景**: 如果该 artifact 被理解为“P19-S4 五个目标没有任何公开 PE/PB 历史来源”，会超过证据范围。计划证明的是当前 akshare/Legulegu interface family 不支持目标 symbol，而不是官方中证/交易所公开源不可行。
- **为什么有问题**: 本地复核支持 plan 的 akshare 结论：`.venv` 中 akshare `1.18.60` 的 `stock_index_pe_lg/pb_lg` source map 只有 `上证50/沪深300/上证380/创业板50/中证500/上证180/深证红利/深证100/中证1000/上证红利/中证100/中证800`，五个 P19-S4 目标不在 map 内；对计划列出的目标 symbol 本地调用均在请求前 `KeyError`。但 `docs/design.md:841` 同时保留中证指数官方来源选项。
- **影响**: 若作为 docs-only closeout，结论应是 “source gate unresolved / deferred”，而不是 “目标指数不可实现”。否则后续 source feasibility 的 owner 和验收标准可能被错误关闭。
- **建议改法和验证点**: 在 plan 的 Recommended Next Gate / Acceptance Criteria 中明确：当前 artifact 可支撑 “不实施代码、P19-S4 docs-only blocked/deferred closeout”，但只关闭 akshare `stock_index_pe_lg/pb_lg` 路径；官方中证/交易所公开 PE/PB 历史源验证应进入下一步 source feasibility，除非 controller 明确裁决该验证不属于当前 P19-S4。
- **修复风险**: 低
- **严重程度**: 低

未发现以下方面的 plan blocker：

- 目标指数列表与 `docs/design.md:875`-`884`、`docs/p19-phase-definition.md:71`-`74` 一致。
- plan 明确拒绝用创业板50、上证红利、深证红利、中证1000 等非目标替代；本地 akshare source map 也确认这些是可用但语义不同的非目标 symbol。
- plan 保持 P19-S4 不改 analyze 自动映射、不开全 A、不使用有知有行页面抓取作为生产源；这与 `docs/design.md:886`、`docs/design.md:898` 和现有 `ThermometerService` index/no-index 分流相符。
- 当 source gate 未解时，plan 选择 blocked/deferred docs-only closeout，而不是推进代码实现；这是当前最安全路径。
- 若 source gate 以现有 akshare 同构接口解决，计划的 Capability data、Service batch、CLI、README 和 P19-S3 回归测试边界清楚，基本可生成代码。

## Questions

1. Controller 是否接受本次 P19-S4 只做 docs-only blocked/deferred closeout，并把官方中证/交易所公开 PE/PB 历史源验证转入独立 source feasibility gate？
2. 如果后续找到官方中证/交易所数据源，是否需要先记录使用许可、下载限制、字段语义和历史覆盖，再允许实现进入 Capability data？
3. 若 source gate 只部分通过，例如五个目标中只有一个有 exact PE/PB 历史来源，P19-S4 是否按 plan 缩小范围交付该指数，还是整体继续 deferred？

## Verdict

PASS_WITH_FINDINGS
