# P19-S2 Plan Review（GLM Reviewer 之二，2026-05-23）

## Reviewed Target And Scope

- Target: `docs/reviews/p19-s2-broad-index-thermometer-plan-20260523.md`
- Scope: P19-S2 broad-index thermometer plan only.
- Reviewer role: independent adversarial plan review reviewer 之二。
- Review timestamp: `20260523-011629`
- Explicit non-edit boundary: 本 review 未修改生产代码、测试代码或原计划文件；只写入本 artifact。

## Verdict

`PASS_WITH_FINDINGS`

P19-S2 计划的主方向可以进入 implementation：数据源探针足以支撑中证500 `000905` 的 slice；批量契约放在 Service 层而不是 UI 层符合当前分层；计划明确排除了 `fund-analysis analyze`、全 A / PB-only 全 A、Dayu runtime 和 `extra_payload`。

但在交给 implementation 前，建议 controller 接受并收紧两个契约 finding：

1. `index_code` + `index_codes` 双字段状态机可实施，但当前方案让互斥/去重/空值规范分散在 UI 与 Service，容易让实现出现双重解析或状态漂移。
2. “well-formed but unsupported index code” 的语义在计划内部不够一致：一处要求 item-level unavailable，另一处仍要求 source 层抛 `ThermometerSourceError`，需要明确 Service 才是把 unsupported 转为 unavailable 的边界。

两者都不是结构性 blocker；它们是 implementation handoff 前应固化的约束。

## Assumptions Tested

- P19-S2 只扩展 `000905` 与 `--index 000300,000905`，不自动接入 `fund-analysis analyze`。
- `AkshareIndexThermometerSource` 是 Capability data 层，`ThermometerCalculator` 是 Capability analysis 层，`ThermometerHistoryCache` 是 Capability cache 层，`ThermometerService` 是跨 source/cache/calculator 的编排入口，CLI 只解析参数并渲染。
- no-index thermometer 继续走 `FundThermometerAdapter` 公开页过渡 adapter。
- 数据不可用是数据状态，well-formed item failure 不应导致 CLI 进程失败；malformed input 是请求错误，CLI exit 2；unexpected internal exception exit 1。
- P19-S1 当前实现已存在单指数 `ThermometerRequest.index_code` 和 `ThermometerService.run()` 返回 `ThermometerReading` 的契约。

## Findings

### F1-未修复-中-index_code/index_codes 双字段状态机需要单一规范化入口

- **位置**: plan `Request Contract` 行 56-69；`Service Batch Orchestration` 行 229-245；`CLI Batch Parsing And Rendering` 行 257-270。
- **问题类型**: 状态机漏洞 / 过度耦合 / 契约缺失。
- **当前写法**: 计划保留 `ThermometerRequest.index_code`，新增 `index_codes`，要求三种模式互斥；UI 按逗号决定传单字段或批量字段；Service 再做 exactly-one validation、去重和校验。
- **反例/失败场景**: CLI 对 `--index "000300,000300"` 做了去重并传 `index_codes=("000300",)`，Service 可能返回 `ThermometerBatchResult`；但另一路测试或调用方直接传 `index_code="000300"` 会返回 `ThermometerReading`。同一逻辑请求可能因为入口不同产生不同返回 shape。再如 CLI 只校验逗号，Service 只校验字段互斥，空 segment、首尾空白、重复项的最终归属容易分裂。
- **为什么有问题**: P19-S2 的用户可见契约不是“是否有逗号”，而是“请求的是一个 self-owned index reading 还是一组 readings”。如果规范化分散在 UI 和 Service，后续 P19-S3 analyze 映射或内部调用 Service 时会绕过 UI 解析规则，导致状态不一致。
- **直接证据**:
  - plan 行 58-63 同时保留 `index_code` 与新增 `index_codes`，并要求 exactly-one。
  - plan 行 64-69 将 comma parsing 和 duplicate decision 放在 UI parsing 描述里。
  - plan 行 229-245 又要求 Service validation、去重和 malformed validation。
  - 当前代码事实：`fund_agent/services/thermometer_service.py` 只有 `ThermometerRequest.index_code`，Service 是当前单指数行为的真实契约入口。
- **影响**: implementation agent 可能把部分输入规范写在 CLI，部分写在 Service，导致 direct Service caller 与 CLI 行为不一致；测试也可能只覆盖 CLI happy path，漏掉 direct request 状态机。
- **建议改法和验证点**:
  - 在 Service 层增加单一规范化函数，例如 `_normalize_index_request(request) -> tuple[Literal["legacy","single","batch"], tuple[str, ...]]`，由它完成互斥校验、6 位数字校验、空值拒绝、去重和顺序保持。
  - UI 的 `_parse_index_option()` 只把原始 CLI 字符串转成显式字段，不决定最终语义；或者更稳健地把 request 统一成 `index_codes`，Service 根据规范化后数量返回 single 或 batch。
  - 测试必须覆盖 direct Service caller：`index_code` + `index_codes` 同时设置、`index_codes=()`, `index_codes=("000300","000300")`, `index_codes=("000300","abc")`, `index_codes=("000300","000905")`。
  - 明确一个去重后单元素 batch 的返回 shape：建议保持“CLI 单值无逗号 -> single；逗号输入 -> batch”，但 Service direct caller 应按 `index_codes` 字段返回 batch，即使去重后只有一个 reading。
- **修复风险（低/中/高）**: 中。
- **严重程度（低/中/高/严重）**: 中。

### F2-未修复-unsupported well-formed code 的不可用语义和 source 异常语义需要明确边界

- **位置**: plan `Per-Index Failure Semantics` 行 94-98；`Supported Index Mapping` 行 201-205；`Exit Criteria` 行 316。
- **问题类型**: 契约缺失 / 测试缺口 / 可验收性风险。
- **当前写法**: 计划要求 “well-formed but unsupported index code” 产生 per-item `ThermometerReading(unavailable=True)`；同时 Slice 1 测试仍要求 source 层对 unsupported well-formed code 抛 `ThermometerSourceError`。
- **反例/失败场景**: 用户运行 `fund-analysis thermometer --index 000300,999999 --json`。如果 CLI 或 Service 在请求校验阶段把 `999999` 当作 unsupported 而抛 `ValueError`，exit 2；如果 source 抛 `ThermometerSourceError` 且 Service 捕获，则 batch exit 0 且该 item unavailable。两种行为都能从计划部分文字推导出来，但用户可见 exit code 完全不同。
- **为什么有问题**: “malformed” 和 “unsupported but well-formed” 是不同失败类别。前者是请求错误，后者是覆盖范围内的数据/支持状态。P19-S2 计划已经选择 well-formed unavailable exit 0，但 implementation slice 没有要求 Service/CLI 测试锁住 `000300,999999` 这一关键反例。
- **直接证据**:
  - plan 行 94 写明 well-formed but unsupported 应产生 item-level unavailable。
  - plan 行 204 写明 source tests 仍要求 unsupported well-formed code raises `ThermometerSourceError`。
  - plan 行 269 只列出 malformed `000300,abc` exit 2，未列出 unsupported `999999` exit 0。
  - 当前代码事实：`AkshareIndexThermometerSource.load_index_history()` 对不支持指数抛 `ThermometerSourceError("暂不支持指数")`，`ThermometerService._load_index_reading()` 捕获 `ThermometerSourceError` 并返回 unavailable reading。
- **影响**: 如果 implementation 把 unsupported 代码提前纳入 request validation，会破坏 P19-S2 “well-formed unavailable is data state” 的 exit-code 约定；如果只在 source 层测试，则 CLI batch 反例未被自动验证。
- **建议改法和验证点**:
  - 明确边界：source 层继续对 unsupported well-formed code 抛 `ThermometerSourceError`；Service 批量聚合层负责把该异常转为该 item 的 `ThermometerReading(unavailable=True)`；CLI 对 `000300,999999` exit 0。
  - 增加 service test：`index_codes=("000300","999999")` 返回一个 available、一个 unavailable，`partial_unavailable=True`，`unavailable_count == 1`。
  - 增加 CLI test：`fund-analysis thermometer --index 000300,999999 --json` exit 0，payload 中 `999999` item unavailable 且 reason 包含“不支持”或同等明确文本。
  - 保留 `000300,abc` exit 2 测试，证明 malformed 与 unsupported 的分界。
- **修复风险（低/中/高）**: 低。
- **严重程度（低/中/高/严重）**: 中。

## Open Questions

- Duplicate codes 的最终契约建议由 controller 在 implementation 前裁决为“preserve-order de-duplication”，并要求 Service direct caller 与 CLI 行为一致。当前计划已有推荐，但仍以 question 形式存在。
- `ThermometerBatchResult.generated_at` 建议由 Service 生成 UTC aware ISO 字符串；测试只断言 parseable/非空，不断言精确值。若为 deterministic tests 设为 `None`，会削弱输出审计性。
- calculation-contract insufficiency 是否转 item unavailable：建议维持当前计划推荐，P19-S2 默认 preserve P19-S1 fail-closed；只有非常明确的数据不足异常才可转 unavailable，且必须有专门测试。

## Recommended Changes

- 保持批量契约在 Service 层，不要让 UI split 多次单指数调用。计划对此判断是正确的。
- 在 plan 或 controller judgment 中补充“Service 单一请求规范化入口”作为 implementation constraint。
- 在 Exit Criteria 中加入 unsupported well-formed code 的服务层和 CLI 层测试：`000300,999999` exit 0 且 partial unavailable。
- 在 Exit Criteria 中加入 batch direct Service caller 状态机测试，不只依赖 CLI parser 测试。
- 保持 source tests 不打 live akshare；`000905` 可用性由已记录 live probe 支撑，默认验证用 fixture。

## Validation Notes

- 未运行测试；本任务是 plan review，不改生产代码。
- 已读取目标计划、`docs/design.md` / `docs/implementation-control.md` 中 P19 相关设计边界，以及当前 P19-S1 `ThermometerService`、`ThermometerRequest`、`ThermometerReading`、CLI thermometer 输出和 `AkshareIndexThermometerSource` 的代码事实。
- 数据源可行性证据评估：计划中的 akshare 1.18.60 live probe 覆盖 `stock_index_pe_lg("中证500")`、`stock_index_pb_lg("中证500")`、目标列、最新日期和共同日期数量，足以支持 P19-S2 implementation；37.5s live latency 已被正确列为 residual，而不是默认测试 gate。
- 边界评估：未发现计划越界到 `fund-analysis analyze`、P19-S5 all-A、PB-only all-A、外部 Dayu runtime 或 `extra_payload`。

## Final Plan Review Conclusion

`pass-with-risks`

P19-S2 计划可以继续，但 controller 应把 F1/F2 作为 implementation constraints 接受，尤其要用自动化测试锁定 request 状态机和 unsupported well-formed code 的 exit-code / item-state 分界。
