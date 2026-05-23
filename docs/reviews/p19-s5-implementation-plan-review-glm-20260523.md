# P19-S5 Implementation Plan Review (AgentGLM) — 2026-05-23

## Reviewer

AgentGLM（独立 adversarial review，未参考 AgentDS 输出）

## Target

`docs/reviews/p19-s5-all-a-market-thermometer-implementation-plan-20260523.md`

## Scope

判断 P19-S5 all-A market thermometer implementation plan 是否足够 code-generation-ready，能否安全交给 implementation agent，不存在 blocker。

## Assumptions Tested

1. All-A source adapter 能复用现有 `AkshareIndexThermometerSource` 或 Protocol 接口。
2. `wind_all_a` 可安全通过现有 Service 规范化和支持性检查。
3. Fixtures 形态与实际 akshare source 输出一致。
4. Cache 命名空间隔离可行且不引入过度耦合。
5. CLI 默认行为变更是安全的，不会回归 P19-S1/S2/S3。
6. Strict parsing 规则对现有 index source 无副作用。
7. Slice sequencing 不会让 implementation agent 提前做 future-slice work。

## Findings

### F1-未修复-[严重]-Fixture 日期列名与源证据矛盾

- **位置**: §9 Fixture Strategy
- **问题类型**: 契约缺失 / 不可直接实施
- **当前写法**: "All-A PE fixture rows must include `日期` and `middlePETTM`"; "All-A PB fixture rows must include `日期` and `middlePB`"
- **反例/失败场景**: Implementation agent 按 plan 创建 `日期` 列 fixture，测试通过。但实际 akshare source `stock_a_ttm_lyr()` 返回列名为 `date`（英文），`stock_a_all_pb()` 同样返回 `date`。真实 source 数据将因缺 `日期` 列触发 `ThermometerSourceError("缺少字段：日期 / ...")`。测试给出假阳性。
- **为什么有问题**: 源可行性 artifact `p19-s5-source-feasibility-20260523.md` §3.1 明确记录 `columns: ['date', 'middlePETTM', ...]`。plan §7.3 也承认"if source-shaped fixtures show a different exact key, freeze that key in constants"，但未在 §9 修正。两处互相矛盾。Fixtures 是所有测试的基础；fixture 列名错误会让全部 source parsing 测试证伪能力为零。
- **直接证据**:
  - Source feasibility §3.1: `columns: ['date', 'middlePETTM', ...]`，首行 `date=2005-01-05`。
  - 本 review 独立复验 `ak.stock_a_all_pb()` columns: `['date', 'middlePB', ...]`，首行 `date=2005-01-04`。
  - 现有 index source 使用 `DATE_COLUMN = "日期"`（`stock_index_pe_lg` / `stock_index_pb_lg` 返回中文列名）。
  - Plan §9: "All-A PE fixture rows must include `日期`"。
- **影响**: Implementation agent 生成错误 fixtures → 全部 source 测试假阳性 → 生产环境 source 解析必定失败 → 温度计不可用。
- **建议改法和验证点**: Plan §9 修正为 `date`（英文），与 source feasibility 一致。同时 §7.3 显式冻结 `ALL_A_DATE_COLUMN = "date"`，与 index source 的 `DATE_COLUMN = "日期"` 区分。验证：fixture fixture 中 `date` 列必须与 akshare 实际输出列名精确匹配。
- **修复风险**: 低。仅修改 plan artifact 文本和常量名。
- **严重程度**: 严重。Fixtures 是测试真源；列名错误让全部 source parsing 测试失去证伪能力。

---

### F2-未修复-[高]-All-A source adapter 与现有 index source 的接口边界不够 code-generation-ready

- **位置**: §7.3 Source Adapter, §10 Slice S5-1
- **问题类型**: 架构边界 / 不可直接实施
- **当前写法**: "Existing index adapter may be evolved or a small all-A adapter may be added in the same module"; "Extend source class or add `AkshareThermometerSource`"; "Required fetchers: `pe_fetcher: Callable[[], object] | None`"
- **反例/失败场景**: Implementation agent 需要在以下三个选项中自行决策：
  1. 新建独立 `AkshareAllAThermometerSource` 类，实现 `ThermometerDataSource` Protocol。
  2. 扩展现有 `AkshareIndexThermometerSource`，内部按 `index_code` 分支。
  3. 用统一的 `AkshareThermometerSource` 替换 `AkshareIndexThermometerSource`。

  如果选方案 2，all-A 的 no-arg fetcher（`Callable[[], object]`）与 index 的 symbol-arg fetcher（`Callable[[str], object]`）在同一类中共存，需要 union type 或 Optional 分支。Service 层注入 `index_source: _IndexThermometerSource` 的 fake 测试也需要适配。

  如果选方案 1，需要修改 Service 构造函数增加第二个 source 注入点或让 Protocol 更通用。Plan 没有排除任何选项，也没有给出推荐。

- **为什么有问题**: "code-generation-ready" 要求 plan 不留让 implementation agent 自行做架构决策的空间。现有代码事实：
  - `ThermometerDataSource` Protocol 定义 `async def load_index_history(self, index_code: str) -> PePbHistory`，方法名和参数已暗示 index-only 语义。
  - `AkshareIndexThermometerSource` 使用 `PeFetcher = Callable[[str], object]`，需要 symbol 参数。
  - Service `__init__` 只注入一个 `_IndexThermometerSource`。

  Plan 应明确选择一种方案并定义精确的接口变更。

- **直接证据**:
  - `thermometer_source.py:65-66`: `PeFetcher = Callable[[str], object]`, `PbFetcher = Callable[[str], object]`。
  - `thermometer_source.py:44-58`: `ThermometerDataSource` Protocol 只有 `load_index_history(self, index_code: str)`。
  - `thermometer_service.py:123-145`: Service 只注入一个 `index_source: _IndexThermometerSource`。
  - Plan §7.3: "pe_fetcher: Callable[[], object] | None" — 这与现有签名不兼容。

- **影响**: Implementation agent 可能选择最简单的方案（扩展现有类加 if/else 分支），导致 index 和 all-A 逻辑耦合在同一类中，增加后续 P19-S4 扩展难度；或选择新建类但忘记更新 Protocol 和 Service 注入点，导致类型不匹配。

- **建议改法和验证点**: Plan 应明确推荐一种方案（例如：新建 `AkshareAllAThermometerSource` 实现 `ThermometerDataSource` Protocol，复用 Protocol 方法 `load_index_history`；Service 维持单一 source 注入，生产时用 union source 包装），并指出 Protocol docstring 从 "index" 更新为 "index or market" 的精确位置。Slice S5-1 应列出 "allowed interface changes" 而非 "may be evolved or added"。

- **修复风险**: 中。需要 plan 作者做出一个架构选择并写清楚。
- **严重程度**: 高。架构边界决策是 plan 应该解决的，不应留给 implementation agent。

---

### F3-未修复-[高]-Service `_normalize_index_codes` 硬编码 6 位数字校验，Plan 未给出精确修改位置

- **位置**: §7.6 Batch Behavior, §10 Slice S5-2
- **问题类型**: 契约缺失 / 不可直接实施
- **当前写法**: "Extend normalization to accept exact `wind_all_a` plus six-digit index codes"; "Malformed tokens exit 2. For this gate, valid token shape is either: exact `wind_all_a`, or exactly six ASCII digits."
- **反例/失败场景**: Implementation agent 修改 `_normalize_index_codes` 接受 `wind_all_a`。但当前函数代码是：
  ```python
  if not text.isdigit() or len(text) != 6:
      raise ValueError(f"{field_name} 必须是 6 位数字")
  ```
  修改此函数需要同时处理：
  - 单个 `index_code`（通过 `_normalize_request` 的 `_normalize_index_codes((request.index_code,), field_name="index_code")` 路径）
  - 批量 `index_codes`
  - `wind_all_a` 与 6 位数字混合
  - CLI `_parse_index_option` 只是简单 split，不做校验；如果 CLI 传入 `wind_all_a,000300`，split 后 Service 的 `_normalize_index_codes` 收到 `("wind_all_a", "000300")`

  Plan 描述了意图但未指出精确的修改行和修改后的校验逻辑。Implementation agent 需要自行设计校验分支。

- **为什么有问题**: 这是 Service 层的核心请求校验函数，直接决定 `wind_all_a` 能否通过。如果修改不当：
  - 可能放行其他非 `wind_all_a` 的非数字字符串。
  - 可能在 `_normalize_request` 中对 `index_code` 和 `index_codes` 走不同路径产生不一致。
  - Plan §7.1 提到 `is_supported_thermometer_code` 或 `is_supported_market_code`，但未说明它和 `_normalize_index_codes` 的关系。

- **直接证据**:
  - `thermometer_service.py:305-335`: `_normalize_index_codes` 函数完整实现。
  - `thermometer_service.py:279-302`: `_normalize_request` 调用路径。
  - Plan §7.6: "valid token shape is either: exact `wind_all_a`, or exactly six ASCII digits"。
  - Plan §7.1: "Add a separate helper, for example `is_supported_thermometer_code(code)`"。

- **影响**: Implementation agent 可能在 normalization 层和 support-check 层分别实现不同的 code 分类逻辑，导致 `wind_all_a` 在 normalization 通过但在 support check 被拒，或反之。

- **建议改法和验证点**: Plan 应明确：
  1. `_normalize_index_codes` 的修改后逻辑（接受 `text == "wind_all_a"` 或 6 位数字）。
  2. 新 helper（`is_supported_thermometer_code` 或 `is_all_a_market_code`）放在 `thermometer_source.py` 还是 `thermometer_service.py`。
  3. Service `_load_index_reading` 的 support check 是否改为使用新 helper，还是继续调用 `is_supported_index_code` 加新分支。

- **修复风险**: 中。
- **严重程度**: 高。请求规范化是 Service 入口，修改不当直接影响 `wind_all_a` 是否可用。

---

### F4-未修复-[中]-Service 默认路由从 public page 改为 all-A 的精确代码路径未指定

- **位置**: §7.5 CLI Default Behavior, §10 Slice S5-2
- **问题类型**: 不可直接实施
- **当前写法**: "Default `ThermometerRequest()` should normalize to `index_code="wind_all_a"` or an internal equivalent, so no-argument thermometer uses all-A."
- **反例/失败场景**: 当前 Service `run()` 方法中，`index_code=None, index_codes=None` 走 public page adapter 路径。Plan 要求改为走 all-A。Implementation agent 需要在以下位置之一插入逻辑：
  1. `_normalize_request` 返回 `_NormalizedThermometerRequest(index_code="wind_all_a", index_codes=None)`。
  2. `run()` 方法在 `normalized.index_code is None` 分支中调用 `_load_index_reading(request, "wind_all_a")`。

  如果选 1，`_normalize_request` 的返回类型和语义改变（原本 `None` 表示"走 public page"，现在变成"走 all-A"）。如果选 2，`run()` 方法需要额外分支。Plan 未指定哪种。

- **为什么有问题**: 这是一个用户可见的行为变更（CLI 默认从 public page 变为 self-owned all-A）。如果 implementation agent 选择在 `_normalize_request` 中硬编码默认值，测试中构造 `ThermometerRequest(index_code=None)` 的场景会意外路由到 all-A 而非 public page，可能破坏现有 adapter 测试。

- **直接证据**:
  - `thermometer_service.py:163-169`: `run()` 的三路分支（batch → single index → public page）。
  - `thermometer_service.py:279-302`: `_normalize_request` 返回 `index_code=None, index_codes=None` 表示"无显式 index"。
  - Plan §7.5: "The CLI should no longer default to Youzhiyouxing public-page snapshot in P19-S5."

- **影响**: Implementation agent 可能在错误层级插入默认逻辑，导致测试回归或 public page adapter 路径意外断裂。

- **建议改法和验证点**: Plan 应在 Slice S5-2 明确：修改 `_normalize_request` 还是 `run()`；如果修改 `_normalize_request`，是否需要保留 public page 路径（如通过显式 `--legacy-public-page` 标记或 Service 配置参数），还是直接移除。同时应列出需要修改的现有测试（`test_thermometer_service_delegates_to_injected_adapter` 当前依赖 `index_code=None` 走 public page）。

- **修复风险**: 低。
- **严重程度**: 中。意图正确但实现路径不明确，可能导致测试回归。

---

### F5-未修复-[中]-Strict parsing 规则应用于共享函数可能影响现有 index source 行为

- **位置**: §8 Strict Parsing Rules, §10 Slice S5-1
- **问题类型**: 过度耦合 / 非回归风险
- **当前写法**: "Harden parsing to enforce strict date, positive Decimal, duplicate conflict detection, common-date intersection."
- **反例/失败场景**: Slice S5-1 "Exact changes" 中列出的修改对象是 `thermometer_source.py`。当前 `_records_by_date`、`_normalize_date`、`_to_decimal` 是模块级共享函数，被 index source 的 `_merge_pe_pb_rows` 调用。如果 implementation agent 在这些共享函数中添加 strict duplicate conflict detection，且现有 index source（`stock_index_pe_lg` / `stock_index_pb_lg`）返回的数据碰巧有重复日期但同值行（5k+ 行中不排除），则：
  - 同值重复：当前代码是 dict 赋值覆盖（幂等），但如果改为显式检测并 collapse，行为改变但安全。
  - 异值重复：当前代码是 later row 静默覆盖 earlier row。如果改为 raise `ThermometerSourceError`，现有 index source 测试可能因 fixture 中没有覆盖 duplicate 而在生产遇到时崩溃。

- **为什么有问题**: Plan §8 的 strict parsing 规则（特别是 duplicate conflict detection）如果应用于共享 `_records_by_date`，会改变现有 index source 的 parsing 行为。Plan 在 S5-1 Stop conditions 中说"Preserve existing tests for `000300` and `000905`"，但没说"preserve existing runtime behavior for index sources"。

- **直接证据**:
  - `thermometer_source.py:161-178`: `_merge_pe_pb_rows` 调用 `_records_by_date`。
  - `thermometer_source.py:181-213`: `_records_by_date` 用 `values[date_text] = value` 静默覆盖重复日期。
  - Plan §8: "Duplicate same-date rows with conflicting positive values must fail closed"。
  - Plan §8: "Do not silently let later rows overwrite earlier rows"。
  - Plan S5-1 stop conditions: "Stop if all-A cannot be supported without making `wind_all_a` look like a six-digit index"（未提到 index source 行为保持）。

- **影响**: 现有 index source 在生产环境中遇到重复日期时可能从静默降级变为抛异常，导致 `000300` / `000905` 温度计不可用。

- **建议改法和验证点**: Plan 应明确：strict parsing（duplicate detection）是仅应用于 all-A source branch，还是统一应用于 `_records_by_date`。如果统一应用，应增加一条 index source 的 duplicate-date 测试来证明非回归。推荐仅应用于 all-A branch，index source 保持现有行为。

- **修复风险**: 低。
- **严重程度**: 中。有 P19-S1/S2 非回归风险，但可通过限制 scope 规避。

---

### F6-未修复-[中]-Cache `_path_for` 需要引入 code 分类器但 plan 未指定与 Service/source 分类器的一致性要求

- **位置**: §7.4 Cache Key, §10 Slice S5-2
- **问题类型**: 过度耦合
- **当前写法**: "Cache path for `wind_all_a` must be `market/wind_all_a_history.json` or another tested non-index namespace"; "Cache load/save must use the same code classifier as Service/source support checks."
- **反例/失败场景**: 三处需要 code 分类器：
  1. `thermometer_source.py` — 判断 `wind_all_a` 走 all-A branch 还是 index branch。
  2. `thermometer_service.py` — `_normalize_index_codes` 和 `_load_index_reading` 的 support check。
  3. `thermometer_cache.py` — `_path_for` 决定 `index/` 还是 `market/` 子目录。

  Plan 说"must use the same code classifier"但没说 classifier 放在哪个模块、什么函数名、什么签名。如果 implementation agent 在三个地方分别用 `code == "wind_all_a"` / `code.startswith("wind_")` / 正则 / 常量 set 做判断，三处可能不一致。

- **为什么有问题**: Cache 的 `_path_for` 当前是 `self.root_dir / "index" / f"{index_code}_history.json"`，硬编码 `"index"` 子目录。如果 Service 传入 `wind_all_a`，cache 会生成 `index/wind_all_a_history.json`，与 plan 的 `market/wind_all_a_history.json` 矛盾。

- **直接证据**:
  - `thermometer_cache.py:113-126`: `_path_for` 硬编码 `self.root_dir / "index"`。
  - Plan §7.4: "Preferred path: `cache/thermometer/market/wind_all_a_history.json`"。
  - Plan §7.4: "Cache load/save must use the same code classifier as Service/source support checks"。

- **影响**: 如果三处分类逻辑不一致，可能出现 cache 写到 `market/` 但 Service 从 `index/` 读的 bug。

- **建议改法和验证点**: Plan 应指定：
  1. 分类函数名（如 `_classify_code(code) -> Literal["index", "market"]`）。
  2. 所在模块（推荐 `thermometer_source.py`，因为它是 Capability data 层的 source of truth）。
  3. Service 和 cache 通过 import 使用同一函数。
  4. Slice S5-2 测试中必须包含"cache 文件在 `market/` 下"的断言。

- **修复风险**: 低。
- **严重程度**: 中。一致性风险可通过集中分类逻辑规避。

---

### F7-未修复-[低]-Plan 未要求 P19-S3 analyze 非回归测试

- **位置**: §3 Non-Goals, §7.5 CLI Default Behavior, §10 Slice S5-3
- **问题类型**: 测试缺口
- **当前写法**: "不改变 `fund-analysis analyze` 已接受的 P19-S3 行为"；"Stop if docs would need to claim `analyze` uses all-A"。
- **反例/失败场景**: Slice S5-2 修改 Service 默认路由后，如果 `ThermometerRequest(index_code=None, index_codes=None)` 的语义从"走 public page"变为"走 all-A"，而 `FundAnalysisService` 内部构造 `ThermometerRequest` 时使用了 `index_code=None`（作为 analyze 的 valuation-state 自动集成路径），则 analyze 会意外从指数温度计切换到全 A 温度计。
- **为什么有问题**: Plan 声明不改变 analyze 行为，但未要求验证。P19-S3 的 analyze 集成路径经过 `ThermometerService`，如果 Service 默认路由变更，analyze 可能间接受影响。
- **直接证据**:
  - `fund_analysis_service.py` 中 P19-S3 集成代码构造 `ThermometerRequest` 时的具体参数。
  - Plan §3: "不改变 `fund-analysis analyze` 已接受的 P19-S3 行为"。
  - Plan §10 S5-3 validation commands 只跑 source/cache/service/CLI 测试，不包含 analyze 相关测试。
- **影响**: Analyze 的 valuation-state 自动集成可能静默从指数温度计切到全 A 温度计，影响报告判断。
- **建议改法和验证点**: Slice S5-2 或 S5-3 添加一条验证：`FundAnalysisService` 对已知指数基金（如 `000300` 跟踪的指数基金）的 analyze 仍然使用 exact identity 映射到 `000300` 温度计，不受默认路由变更影响。可以是现有 analyze 测试的回归运行。
- **修复风险**: 低。
- **严重程度**: 低。P19-S3 集成代码使用显式 `index_code`，大概率不受默认路由影响，但 plan 应显式验证。

---

## Open Questions

1. **PB source date column**: Source feasibility artifact 未显式记录 `stock_a_all_pb()` 的日期列名。本 review 独立复验确认为 `date`（与 PE 一致）。后续 plan 修正时应将此信息同步更新到 source feasibility artifact。

2. **Public page adapter 退役策略**: Plan §7.5 说"The CLI should no longer default to Youzhiyouxing public-page snapshot"，但 Service 的 `_ThermometerAdapterFactory` 和 `_default_adapter_factory` 仍然存在。Plan 未说明是否在 S5-2/S5-3 中标记为 deprecated 或移除 default path，还是仅改 Service 路由。

3. **`_IndexThermometerSource` Protocol 方法名**: 当前方法名为 `load_index_history(self, index_code: str)`。如果 all-A 也走这个 Protocol，方法名中的 "index" 语义变为 "index or market"。Plan §7.2 提到 docstring 更新但未提及 Protocol 方法名是否需要更新。

## Residual Risks

| 风险 | 等级 | 建议跟踪 |
|------|------|---------|
| Legulegu SSL EOF / token 变更 | 低 | Plan 已覆盖 retry/cache/unavailable；实现时测试即可 |
| All-A universe 定义不完全可审计 | 低 | Source feasibility 已接受为设计限制 |
| `ThermometerBatchResult.source` 默认值 `"self_owned_index_thermometer_batch"` 是否改为 `"self_owned_thermometer_batch"` | 低 | Plan §7.7 已识别为 optional wording change |
| P19-S4 扩展指数来源仍然 deferred | 低 | 不在 S5 scope 内 |
| 未来 `analyze` 主动基金全 A 映射 | 低 | 不在 S5 scope 内 |

## Conclusion

**pass-with-risks**

Plan 的核心设计方向正确：复用现有 `ThermometerService` / `ThermometerCalculator` / `ThermometerHistoryCache` 管线，仅在 Capability data source 层扩展 all-A adapter，不引入新 UI/Service/Calculator。Slice sequencing（S5-1 source → S5-2 service/cache → S5-3 CLI/docs）合理，非回归意识明确。

但存在一个严重事实性错误（F1：fixture 日期列名 `日期` 应为 `date`）和两个高严重度 code-generation-ready 缺口（F2：source adapter 架构选择未定；F3：Service normalization 修改位置未指定）。这些不影响方向正确性，但会导致 implementation agent 做出错误的代码生成决策。

建议 controller 在接受前要求 plan 修正 F1（事实性错误），并就 F2/F3 补充精确的实现选择。F4-F7 为中低风险，可由 implementation agent 在 stop condition 检查中自行处理。

## Verification

- 本 review 期间未修改任何源码、测试、design doc、control doc。
- 仅创建了本 artifact 文件。
