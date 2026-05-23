# P19-S4 Expanded Index Coverage Plan Review - GLM - 2026-05-23

Reviewed target: `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md`

## Findings

### F1-未修复-高-计划不能作为 P19-S4 最终 blocked closeout，因为尚未验证 design 允许的中证官方 / akshare 其他指数估值来源

- **位置**: `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md:7-9`, `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md:47-98`, `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md:270-278`
- **问题类型**: source feasibility gate 未收敛 / 非最优方案 / open question 未收敛
- **当前写法**: 计划证明本地 akshare `1.18.60` 的 `stock_index_pe_lg` / `stock_index_pb_lg` 对五个 P19-S4 目标的常见 symbol 返回 `KeyError`，并用非目标 symbol 成功返回来排除通用网络或 schema outage。随后给出 `BLOCKED_FOR_TARGET_IMPLEMENTATION`，并允许 controller “close P19-S4 as blocked/deferred with this artifact as evidence”。
- **反例/失败场景**: `stock_index_pe_lg/pb_lg` 只代表乐咕乐股这一组接口，不代表 design 允许的全部来源。本地 akshare 同时暴露 `stock_zh_index_value_csindex(symbol=...)`，docstring 为“中证指数-指数估值数据”，以及 `index_csindex_all()`、中证指数成分和权重接口；这些属于 design 明确允许的“中证指数官方或 akshare 指数估值接口”候选，但计划没有对五个目标逐一验证。
- **为什么有问题**: design 真源规定温度计数据来源是 “akshare + 中证指数官方或 akshare 指数估值接口”，不是仅限 `stock_index_pe_lg/pb_lg`。当前计划已经足以阻止在乐咕接口缺失时做近似映射，但不足以证明 P19-S4 五个目标全局不可实现；如果据此直接关闭 P19-S4，会把尚未验证的允许来源错误裁决为不可用。
- **直接证据**: `docs/design.md:841` 指定来源为 “akshare + 中证指数官方或 akshare 指数估值接口”；`docs/design.md:880-884` 把五个目标列为 P19-S4；`docs/design.md:895` 把 `ThermometerDataSource` 定义为从 akshare / 中证指数获取 PE/PB 数据；本地 akshare introspection 显示 `stock_zh_index_value_csindex` 位于 `.venv/lib/python3.11/site-packages/akshare/index/index_stock_zh_csindex.py:72`，签名为 `stock_zh_index_value_csindex(symbol: str = 'H30374')`，说明存在未验证的官方估值候选入口。
- **影响**: controller 可能过早接受 docs-only blocked closeout，导致 P19-S4 在仍有合法候选来源时被错误延期；或者后续 worker 缺少明确 probe 清单，继续只围绕乐咕接口重复验证。
- **建议改法和验证点**: 将 recommended next gate 收紧为“必须先执行 P19-S4 source feasibility gate”；在该 gate 中逐一验证至少 `stock_zh_index_value_csindex`、中证指数官方可下载估值文件、akshare 其他指数估值相关接口是否能为 `399006/000688/000922/000932/000933` 返回 exact identity 的 PE/PB 历史。只有所有 design-allowed 候选都缺少 PE 或 PB、或字段语义不能证明为目标指数历史估值时，才可更新 control 把 P19-S4 标为 blocked/deferred。
- **修复风险**: 中
- **严重程度**: 高

### F2-未修复-中-后续实现切片默认仍是乐咕字段形状，不能指导通过非乐咕 source gate 后的实现

- **位置**: `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md:122-138`, `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md:140-166`
- **问题类型**: 不可直接实施 / 架构边界 / 测试缺口
- **当前写法**: Source gate 要求 PE 包含 `滚动市盈率中位数`、PB 包含 `市净率中位数`；Slice 1 只计划扩展 `SUPPORTED_INDEX_SYMBOLS` / `INDEX_NAMES`，并要求保持 `PE_COLUMN = "滚动市盈率中位数"` 和 `PB_COLUMN = "市净率中位数"`。
- **反例/失败场景**: 如果 source gate 最终通过的是中证官方或 akshare 其他指数估值接口，字段形状可能不是乐咕 `stock_index_pe_lg/pb_lg` 的两张表。以本地 `stock_zh_index_value_csindex` 源码为例，该接口返回列名包括 `日期`、`指数代码`、`指数中文全称`、`市盈率1`、`市盈率2`、`股息率1`、`股息率2`，并不满足当前 hard-coded PE/PB 中位数字段契约。
- **为什么有问题**: P19 的必要事实是目标指数 PE/PB 历史，而不是特定接口的列名。计划一方面承认必须找其他 exact source，另一方面把后续实现限制为“加 mapping + 保持乐咕列名”，会让 worker 在 source gate 通过后仍无法判断是否应新增 source-specific adapter、字段语义转换、fixture freeze 或 fail-closed 规则。
- **直接证据**: `fund_agent/fund/data/thermometer_source.py:19-24` 当前只支持 `000300/000905` 和乐咕列名；`docs/design.md:888-898` 要求 Capability data 只返回结构化 PE/PB 数据，Service/UI 不感知具体来源；本地 akshare `stock_zh_index_value_csindex` 的返回列不包含当前计划要求的 PB 中位数字段。
- **影响**: 一旦新来源可用，implementation agent 可能被计划误导为只改常量，或为了适配测试把不同语义字段硬塞进 `滚动市盈率中位数` / `市净率中位数`，导致温度计 PE/PB 历史事实不可审计。
- **建议改法和验证点**: 把 source gate 输出拆成“source contract”：API / URL、目标 index identity 证明、PE 字段语义、PB 字段语义、日期覆盖、共同日期数量、缺失/异常语义、许可/稳定性说明。后续实现切片应根据 source contract 决定是扩展当前 `AkshareIndexThermometerSource` mapping，还是新增 source-specific Capability adapter；测试必须冻结原始 source-shaped fixture 和规整后的 `PePbHistory`。
- **修复风险**: 中
- **严重程度**: 中

## Questions

- Source feasibility gate 是否必须覆盖 `stock_zh_index_value_csindex` 和中证指数官方估值文件？如果不是，controller 需要明确为什么这些 design-allowed 来源在 P19-S4 被排除。
- 如果某个目标只有 PE 历史、没有 PB 历史，是否一律 blocked？按 design §11.2 / §11.3 当前应 blocked，不能用 PE-only 或股息率替代 PB。
- 如果五个目标中只有部分目标通过 exact PE/PB source gate，P19-S4 是否接受 subset implementation？当前计划的 acceptance criteria 允许“至少一个目标”实现，但 control 的 P19-S4 exit criteria 写的是五个目标温度计算通过测试，需要 controller 明确 partial accepted 的台账口径。
- 中证官方接口若返回的是成分股或指数级估值，是否满足“等权 PE/PB 中位数历史”的方法论语义？source gate 需要记录字段定义，不能只记录列存在。

## Verdict

PASS_WITH_FINDINGS

计划严守了关键非目标：不做全 A、不改 no-index 默认、不扩大 `analyze` 自动映射、不使用 public-page scrape / Dayu / `extra_payload`，也明确禁止用创业板50、上证红利、深证红利、中证1000等近似指数替代目标指数。它可以作为“当前乐咕接口不可用，禁止直接实现近似映射，进入 source feasibility gate”的计划接受。

但它不能作为 P19-S4 最终 blocked/deferred closeout 的充分证据。下一步应先补 source feasibility gate，验证 design 允许的中证官方与 akshare 其他指数估值来源；只有 source gate 仍无法证明五个目标的 exact PE/PB 历史，才应更新 control 把 P19-S4 记为 blocked/deferred。
