# P19-S2 Plan Review - MiMo（2026-05-23）

## Verdict

`PASS_WITH_FINDINGS`

P19-S2 plan 可以进入 controller 裁决，但实施前应把 malformed request 的 CLI exit-code 映射和 well-formed unsupported index 的测试矩阵收敛为硬约束。当前计划的主方向成立：中证 500 数据源证据足够支撑 P19-S2，批量语义应归 Service 层，且没有越界到 `fund-analysis analyze`、全 A、PB-only 全 A、Dayu runtime 或 `extra_payload`。

## Reviewed Target And Scope

- Target: `docs/reviews/p19-s2-broad-index-thermometer-plan-20260523.md`
- Scope: P19-S2 plan review only；不审查生产代码实现，不修改生产代码。
- Review timestamp: `20260523-011535`
- Source-of-truth checks:
  - `docs/design.md` §11.4 明确 P19-S2 只扩展中证 500，all-A 延后到 P19-S5 / all-A PE source gate。
  - `docs/design.md` §11.5 要求 UI 只依赖 Service，Service 编排请求、缓存策略、数据源选择和输出模型。
  - `docs/design.md` §11.7 明确 P19-S1/S2 不改变 `fund-analysis analyze` 默认行为。
  - `docs/design.md` §12 要求 plan review 显式检查边界、Dayu runtime、外部适配器和 `extra_payload`。

## Assumptions Tested

- `000905` 使用 akshare `stock_index_pe_lg("中证500")` + `stock_index_pb_lg("中证500")` 可以复用 P19-S1 数据形态。
- 批量查询不是 UI 展示细节，而是温度计查询 use case 的聚合语义，应由 `ThermometerService` 负责。
- `ThermometerRequest.index_code` + `index_codes` 双字段可以靠 exactly-one validation 保持状态机清晰。
- well-formed unavailable data 是数据状态，malformed input 是请求错误，unexpected exception 是进程失败。
- P19-S2 不触碰 `FundAnalysisService`、全 A、PB-only 全 A、Dayu runtime、外部页面生产抓取或 `extra_payload`。

## Findings

### F1-未修复-中-CLI malformed request exit 2 的实施路径仍不够显式

- **位置**: Plan `CLI Exit Code` lines 179-185；`Slice 4: CLI Batch Parsing And Rendering` lines 255-269；current code `fund_agent/ui/cli.py:275-287`
- **问题类型**: 契约缺失 / 状态机漏洞 / 测试缺口
- **当前写法**: 计划要求 malformed CLI/request input exit 2，并新增 `_parse_index_option()`；同时 Service validation 会对非法 `index_codes` 抛 `ValueError`。但计划没有明确 CLI 应把 `_parse_index_option()` 的 `ValueError` 或 Service validation 的 `ValueError` 单独捕获为 exit 2。
- **反例/失败场景**: implementation agent 按当前代码结构直接在 `try: ThermometerService().run(...) except Exception` 内构造请求和调用 Service。由于当前 thermometer CLI 分支把所有异常统一映射为 exit 1，`--index 000300,abc` 或空段输入可能违反计划的 exit 2 契约。
- **为什么有问题**: 用户可见 CLI contract 的核心区别是 malformed request=用户输入错误、well-formed unavailable=数据状态、unexpected=内部失败。若捕获策略不显式，最容易被现有 broad catch 回归成 exit 1，导致测试只能事后发现，而不是计划直接约束实现。
- **直接证据**:
  - Plan lines 181-183: exit 0/2/1 三分法。
  - Plan lines 258-259: UI 会解析 `--index` 并传给 `ThermometerRequest`。
  - Current code `fund_agent/ui/cli.py:275-287`: thermometer CLI 当前 `except Exception` 后固定 `typer.Exit(code=1)`。
- **影响**: malformed input 的 exit code 与计划不一致；用户和脚本无法区分输入错误与内部错误；P19-S2 acceptance 可能在 CLI 测试阶段返工。
- **建议改法和验证点**:
  - 在计划或 controller acceptance 中明确：`_parse_index_option()` 必须在 Service 调用前执行；解析错误捕获为 `typer.Exit(code=2)`。
  - 若 Service validation 仍可能抛 `ValueError`，CLI thermometer 分支必须先 `except ValueError as exc` 并 exit 2，再捕获 unexpected exception exit 1。
  - CLI 测试至少覆盖 `000300,abc`、`000300,`、`,000905`、空白/全空段输入，均 exit 2。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### F2-未修复-中-well-formed unsupported index 的 batch 语义缺少端到端测试约束

- **位置**: Plan `Per-Index Failure Semantics` lines 92-99；`Slice 3` service tests lines 237-246；`Slice 4` CLI tests lines 264-271
- **问题类型**: 测试缺口 / 契约缺失
- **当前写法**: 计划说 well-formed but unsupported index code 应产生 item-level `ThermometerReading(unavailable=True)`，malformed input 才 exit 2。但测试矩阵只明确 source 层 unsupported code raises `ThermometerSourceError`，以及 batch partial/all source failure；没有明确 Service/CLI 对 `000300,399006` 这类 well-formed unsupported code 的端到端断言。
- **反例/失败场景**: implementation agent 在 UI parser 中把“当前支持列表之外”的 6 位代码当作 malformed input 拦截，导致 `000300,399006` exit 2；或者 Service validation 只允许 `000300/000905`，使 unsupported well-formed code 无法进入 item-level unavailable。这样会把可恢复的数据不可用状态错误升级为请求错误。
- **为什么有问题**: P19-S2 的 partial unavailable 价值正是允许批量请求中单项数据不可用而整体可渲染。well-formed unsupported 与 malformed 的边界是最容易被实现混淆的地方；如果没有端到端测试，exit code 和 JSON/plain 数据状态可能分裂。
- **直接证据**:
  - Plan line 94: well-formed but unsupported index code 应产生 per-item unavailable。
  - Plan line 96: malformed CLI/request input 才是 request error / exit 2。
  - Plan lines 241-245: service tests 覆盖 partial/all failures 和 malformed `index_codes`，但没有点名 unsupported well-formed batch。
  - Plan lines 266-269: CLI tests 覆盖 happy path、partial unavailable 和 malformed batch，未点名 `000300,399006`。
- **影响**: Service/UI 可能把支持范围判断前移到 UI，破坏 Service owns aggregation 的边界；批量查询对未来 P19-S4 指数扩展不稳；用户看到的 exit code 与数据状态不一致。
- **建议改法和验证点**:
  - 增加 Service 测试：`index_codes=("000300", "399006")` 返回两个 readings，其中 `399006.unavailable=True`，batch `partial_unavailable=True`，`unavailable_count == 1`。
  - 增加 CLI JSON 测试：`fund-analysis thermometer --index 000300,399006 --json` exit 0，输出 `partial_unavailable: true`，并包含 `399006` 的 `unavailable_reason`。
  - 明确 UI parser 只做形态校验（6 位数字、空段、重复策略），不做 supported-index allowlist 判断。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

## Open Questions

- `ThermometerRequest.index_code` + `index_codes` 双字段不是 blocker，但长期更稳健的状态机是只保留一个规范化 tuple 字段：`index_codes=None` 表示 legacy no-index，`("000300",)` 表示 single，多个值表示 batch。P19-S2 为了减少 P19-S1 public contract churn 保留双字段可以接受，但必须通过 exactly-one validation 和 focused tests 防止 impossible state。
- 重复代码策略应在 controller acceptance 中从 open question 变成硬约束。当前计划推荐 preserve-order de-duplication，我同意这个选择；实现时 `requested_index_codes` 和 `readings` 都应使用去重后的规范化序列，避免 result_count 与实际网络调用次数不一致。
- `generated_at` 建议由 Service 生成 UTC ISO 字符串；测试只断言字段存在、可 parse 和 timezone-aware，不断言具体值。

## Recommended Changes

- 在 P19-S2 acceptance constraints 中加入：CLI thermometer 必须区分 `ValueError`/request parse error exit 2 与 unexpected exception exit 1。
- 把 well-formed unsupported batch code 的 Service/CLI 端到端测试列为 Exit Criteria。
- 把 duplicate policy 从 Open Question 提升为明确要求：preserve-order de-duplication；UI 不做 supported-index allowlist。
- 保持现有 plan 的边界约束：不接入 `fund-analysis analyze`，不实现全 A 或 PB-only 全 A，不改变 no-index public-page adapter，不引入 Dayu runtime，不使用 `extra_payload`。

## Validation Notes

- 本次 review 未运行测试，也未改生产代码。
- 已静态读取并对照：
  - `docs/reviews/p19-s2-broad-index-thermometer-plan-20260523.md`
  - `docs/design.md`
  - `docs/implementation-control.md`
  - `fund_agent/services/thermometer_service.py`
  - `fund_agent/ui/cli.py`
  - `fund_agent/fund/data/thermometer_types.py`
  - `fund_agent/fund/data/thermometer_source.py`
  - `tests/ui/test_cli.py`

## Final Plan Review Conclusion

`pass-with-risks`

P19-S2 plan 的架构边界和范围控制是正确的，数据源探针足够支撑 `000905` implementation。批量契约应在 Service 层实现，而不是 UI split。当前不需要 blocker，但 controller 应接受上述两个 findings 为实施约束，否则最可能在 CLI exit-code 和 unsupported well-formed code 的数据状态上出现可见回归。
