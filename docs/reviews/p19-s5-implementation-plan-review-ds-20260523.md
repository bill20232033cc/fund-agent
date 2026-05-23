# P19-S5 All-A Market Thermometer — Implementation Plan Review (AgentDS)

## Verdict

**`pass-with-risks`**

Plan 已经 code-generation-ready，分层边界、契约决策、slice 顺序和 stop conditions 基本清晰。以下 5 个 findings 都不是 blocker，但 implementation agent 若不注意会在具体实现时跑偏或引入回归。

---

## Reviewed Target And Scope

- **Target**: `docs/reviews/p19-s5-all-a-market-thermometer-implementation-plan-20260523.md`
- **Scope**: 全 A 市场温度计实现 plan，覆盖 Capability source、Service/cache normalization、CLI/docs 三个 slice
- **Evidence read**:
  - `AGENTS.md`（模块边界、硬约束）
  - `docs/design.md` §11（温度计设计）§12（Plan Review 边界检查）
  - `docs/implementation-control.md`（P19-S5 gate 状态、entry point）
  - `docs/reviews/p19-s5-source-feasibility-20260523.md`（数据源契约）
  - `docs/reviews/p19-s5-source-feasibility-controller-judgment-20260523.md`（Controller 约束）
  - 现有源码：`thermometer_source.py`、`thermometer_cache.py`、`thermometer_service.py`、`thermometer_calculator.py`、`thermometer_types.py`、`cli.py`、`paths.py`、`__init__.py`
  - 现有测试：`test_thermometer_source.py`、`test_thermometer_service.py`

---

## Assumptions Tested

| # | Assumption | Evidence | Holds? |
|---|-----------|----------|--------|
| A1 | `wind_all_a` 不与六位指数代码语义冲突 | Plan §7.1 明确分离 `is_supported_thermometer_code` 与 `is_supported_index_code` | Yes |
| A2 | 现有 calculator 可直接用于 all-A `PePbHistory` | `calculate_thermometer_reading()` 只读 `points` 的 `pe`/`pb`/`date`，不区分 index vs market | Yes |
| A3 | Cache namespace `market/` 不与 `index/` 碰撞 | 当前 `_path_for` 硬编码 `index/` 前缀；plan 要求分类路由 | Yes, 但需改 `_path_for` |
| A4 | Service 不改 `analyze` 行为 | Plan 明确不修改 `fund_analysis_service.py`、renderer、audit | Yes |
| A5 | All-A fetcher 是 no-arg，与 index fetcher（接受 symbol）签名不同 | Source feasibility artifact 确认 `stock_a_ttm_lyr()` 和 `stock_a_all_pb()` 无参 | Yes, plan §7.3 承认但未解决 unified class 的签名张力 |
| A6 | `_records_by_date` 的 drop-non-positive 行为对 all-A 足够 | 现有逻辑 `if value > 0` 丢弃非正值；plan §8 要求一致 | Yes, 但 duplicate-date 是新增逻辑 |
| A7 | `_normalize_index_codes` 会被 S5-2 更新以接受 `wind_all_a` | 当前只接受 `isdigit() and len==6`；plan §7.6 要求接受 `wind_all_a` | Yes, S5-2 职责 |

---

## Findings

### F1-未修复-中-index/unavailable 名称映射位置未指定

- **位置**: Plan §7.8 / §8 (unavailable semantics), 现有代码 `thermometer_service.py:216-221`、`thermometer_service.py:243-247`
- **问题类型**: 契约缺失
- **当前写法**: Plan §7.8 说 "returns unavailable reading with all-A code/name"。现有 Service 代码在 `_load_index_reading` 中构造 `ThermometerUnavailable(index_code=index_code, index_name=index_code, ...)` — 将 `index_name` 直接设为 `index_code` 字符串。
- **反例/失败场景**: 当 all-A source 失败且无缓存时，Service 返回 `ThermometerUnavailable(index_code="wind_all_a", index_name="wind_all_a", ...)`，CLI 输出 `index_name: wind_all_a` 而非 `index_name: 万得全 A / 全 A 市场`。用户看到的是技术代码而非人类可读名称。
- **为什么有问题**: Plan 声称要返回 "all-A code/name"，但当前 Service 代码没有 name 查找机制。`index_name` 映射只在 `AkshareIndexThermometerSource` 内部的 `INDEX_NAMES` dict 中，Service 层不可见。要么 Service 需要知道 all-A name（在 Service 层引入 `ALL_A_MARKET_NAME` 常量），要么 source 层需暴露 name 查询接口。
- **直接证据**:
  - `thermometer_service.py:243-247`: `ThermometerUnavailable(index_code=index_code, index_name=index_code, reason=...)`
  - `thermometer_source.py:20`: `INDEX_NAMES` 是 source 模块私有常量
  - Plan §5.2 列出了所有常量（`ALL_A_MARKET_CODE`, `ALL_A_MARKET_NAME` 等），但 Service 的 `_load_index_reading` 未引用
- **影响**: 实施 Agent 可能忽略 unavailable 路径中的 name 展示，导致 CLI 输出质量下降
- **建议改法和验证点**:
  - 在 Capability data 层提供 `get_thermometer_name(code: str) -> str` 或让 Service 引用 `ALL_A_MARKET_NAME` 常量
  - 测试: unavailable reading 的 `index_name` 应为人类可读名称，不是原始 code
- **修复风险（低）**:
- **严重程度（中）**:

### F2-未修复-中-duplicate-date 检测会影响现有指数路径

- **位置**: Plan §8 (Duplicate Dates), 现有代码 `thermometer_source.py:181-213` (`_records_by_date`)
- **问题类型**: 架构边界 / 过度耦合
- **当前写法**: `_records_by_date` 是 index 和 all-A 共享的解析函数。当前实现是 last-write-wins: `values[date_text] = value`（line 212），不检测重复日期冲突。Plan §8 要求 "Duplicate same-date rows with conflicting positive values must fail closed"。
- **反例/失败场景**: 如果在共享函数 `_records_by_date` 中直接加入 duplicate-conflict 检测，现有 000300/000905 路径也会受此约束。如果 akshare 的 `stock_index_pe_lg` 返回数据中某天有两条相同日期但不同 PE 值的行（目前 fixture 中未出现，但真实数据可能），原本 last-write-wins 行为会变成 `ThermometerSourceError`，导致已工作的指数温度计回归。
- **为什么有问题**: Plan §5.1 说 "Preserve existing tests for 000300 and 000905"，但未说明 duplicate-date 检测是否只用于 all-A 路径。Implementation agent 可能把检测直接写入共享的 `_records_by_date`，影响 index 路径。
- **直接证据**:
  - `thermometer_source.py:212`: `values[date_text] = value` — 无条件覆盖
  - Plan §5.1: "Harden parsing to enforce strict date, positive Decimal, duplicate conflict detection, common-date intersection" — 在 S5-1 上下文中似乎针对 all-A，但实现位置可能是共享函数
- **影响**: 指数温度计回归；P19-S1/S2 测试可能因 fixture 不含重复日期而通过，但生产数据可能触发 fail-closed
- **建议改法和验证点**:
  - 要么为 all-A 写独立的 `_merge_all_a_pe_pb_rows`，不修改共享 `_records_by_date`
  - 要么在共享函数中加入 duplicate detection，但必须对 index 路径做回归测试（用含重复日期的 fake frame 验证 index 路径行为）
  - Plan 应明确 duplicate 检测的作用范围
- **修复风险（低）**:
- **严重程度（中）**:

### F3-未修复-低-fetcher 签名与 unified source class 的张力

- **位置**: Plan §7.3, 现有代码 `thermometer_source.py:65-66`, `thermometer_source.py:78-79`
- **问题类型**: 不可直接实施
- **当前写法**: Plan §7.3 说 "Existing index adapter may be evolved or a small all-A adapter may be added in the same module." 但同时定义了 `pe_fetcher: Callable[[], object] | None`（no-arg）作为 all-A fetcher。现有 `AkshareIndexThermometerSource` 的 `PeFetcher = Callable[[str], object]` 接受 symbol 参数。两者的函数签名不同。
- **反例/失败场景**: Implementation agent 试图在 `AkshareIndexThermometerSource` 的 `__init__` 中同时接受两种不同签名的 fetcher，用 `if/else` 分支选择调用路径。当 `index_code == "wind_all_a"` 时调用 `self._all_a_pe_fetcher()`（no-arg），否则调用 `self.pe_fetcher(symbol)`（带 symbol）。这会导致 `load_index_history` 方法中出现隐式的 code-based dispatch，违背"不要让 wind_all_a 看起来像六位指数"的原则。
- **为什么有问题**: 如果用一个 class 处理两种不同契约的数据源，`load_index_history` 内部会出现 `if code == "wind_all_a": ... else: ...` 分支，这恰恰是 plan §5.1 stop condition 要防止的："Stop if all-A cannot be supported without making wind_all_a look like a six-digit index."
- **直接证据**:
  - `thermometer_source.py:65`: `PeFetcher = Callable[[str], object]`
  - `thermometer_source.py:78`: `pe_fetcher: PeFetcher | None = None`
  - Plan §7.3: `pe_fetcher: Callable[[], object] | None`
  - `thermometer_source.py:94`: `symbol = SUPPORTED_INDEX_SYMBOLS.get(index_code)` — 当前按 symbol 查找
- **影响**: 实施 Agent 可能写出过度耦合的 unified class 或困惑于如何注入两种不同签名的 fake fetcher
- **建议改法和验证点**:
  - 推荐路径：新增独立的 all-A source class（如 `AkshareAllAMarketSource`），与 `AkshareIndexThermometerSource` 并行，只实现相同的 `ThermometerDataSource` protocol。这比强行 unified 更安全、更可测试。
  - 如果选择 unified class，plan 应明确 branch 策略和 fetcher 注入契约
- **修复风险（低）**:
- **严重程度（低）**:

### F4-未修复-低-CLI 公共页快照访问路径消失

- **位置**: Plan §7.5, 现有代码 `cli.py:257-309`, `thermometer_service.py:166-169`
- **问题类型**: 范围漂移 / 契约缺失
- **当前写法**: Plan §7.5 决定 "fund-analysis thermometer with no --index now queries self-owned all-A market thermometer"，并说 "no new public-page flag is required." 当前代码在 `index_code=None and index_codes=None` 时走 `FundThermometerAdapter`（公开页快照）。Plan 变更后，CLI 默认行为变为 all-A 自建温度计，公开页快照路径在 CLI 层不再可访问。
- **反例/失败场景**: 用户或开发者想对比自建温度计与有知有行公开页读数时，没有 CLI 入口可用。`FundThermometerAdapter` 代码仍在但变成死代码。如果未来需要公开页作为对比基准或回归测试参考，必须加回 CLI flag，造成二次改动。
- **为什么有问题**: Plan non-goals 说 "现有 FundThermometerAdapter 只能继续作为过渡公开页查询或对比输入"，这与 "no new public-page flag is required" 存在张力 — 如果它是合法的对比输入，但没有 CLI 入口，它就只是死代码。不是 blocker（Controller 可后续决定），但 implementation agent 可能不知道该保留还是该标记 deprecated。
- **直接证据**:
  - `thermometer_service.py:168-169`: `adapter = self._adapter_factory(request.cache_dir); return await adapter.load_thermometer(...)`
  - Plan §3 Non-Goals: "不使用有知有行页面作为生产温度计数据源；现有 FundThermometerAdapter 只能继续作为过渡公开页查询或对比输入"
  - Plan §7.5: "no new public-page CLI flag unless controller explicitly asks"
- **影响**: 后续返工（如需加回对比入口）；`FundThermometerAdapter` 变成无测试覆盖的死代码
- **建议改法和验证点**:
  - Plan 应明确：公开页快照在未来是否保留 CLI 入口（如 `--source public-page`），还是标记为 deprecated/internal-only
  - 如标记为 internal-only，应在代码中加 `# transitional` 注释，并在 README 中移除公开页相关描述
- **修复风险（低）**:
- **严重程度（低）**:

### F5-未修复-低-`_records_by_date` 的 NaN 处理未出现在 plan 中

- **位置**: Plan §8 (Strict Parsing Rules), 现有代码 `thermometer_source.py:247-268` (`_to_decimal`)
- **问题类型**: 测试缺口
- **当前写法**: Plan §8 说 "Reject None, bool, non-numeric, NaN, Infinity and <= 0"。当前 `_to_decimal` 用 `Decimal(str(value))` 转换，对于 `float('nan')` 会变成 `Decimal('NaN')`，对于 `float('inf')` 会变成 `Decimal('Infinity')`。这些值能通过 `Decimal(str(value))` 不抛异常，但后续 `if value > 0` 比较中 `Decimal('NaN') > 0` 的行为是 `Decimal('NaN')` 比较 — 实际上 `Decimal('NaN')` 的比较会抛出 `InvalidOperation`（在默认 context 下），或者在某些 context 下返回 False。行为不确定。
- **反例/失败场景**: 如果 akshare DataFrame 中某个 `middlePETTM` 值是 `numpy.nan`，它被 `str()` 转换为 `'nan'`，`Decimal('nan')` 可以成功构造但后续比较行为不确定。Plan 说 "reject NaN" 但没有给实现 agent 明确的检测方式。
- **为什么有问题**: 当前的 `_to_decimal` 不检测 NaN/Infinity，plan 说应该拒绝但没有说明是 `_to_decimal` 的职责还是调用方的职责。
- **直接证据**:
  - `thermometer_source.py:266`: `return Decimal(str(value))` — 不检测 NaN/Inf
  - Plan §8: "Reject None, bool, non-numeric, NaN, Infinity and <= 0"
  - Source feasibility 确认 `middlePETTM` 和 `middlePB` 实际数据 0 NaN，但防御性代码应覆盖
- **影响**: 实施 Agent 可能遗漏 NaN/Inf 检测，导致未定义行为
- **建议改法和验证点**:
  - 在 `_to_decimal` 返回前或调用方加入 NaN/Inf 检测：`if dec.is_nan() or dec.is_infinite(): raise ThermometerSourceError(...)`
  - 测试: 注入 `float('nan')` 和 `float('inf')` 作为估值字段值，验证 fail-closed
- **修复风险（低）**:
- **严重程度（低）**:

---

## Open Questions

1. **Q1**: 公开页快照 (`FundThermometerAdapter`) 在 P19-S5 后是否完全不可通过 CLI 访问？如果是，是否需要标记为 internal/deprecated？（见 F4）
2. **Q2**: duplicate-date 冲突检测是否只用于 all-A 路径，还是也加固 index 路径？如果也加固，是否需要先在 `stock_index_pe_lg` / `stock_index_pb_lg` 的真实数据上验证没有冲突重复？（见 F2）

---

## Residual Risks And Suggested Tracking

| 风险 | 跟踪目标 |
|------|---------|
| Legulegu SSL EOF 在生产环境的频率和恢复时间 | P19-S5 implementation 的 retry/stale-cache 已覆盖；后续 observability phase |
| `_records_by_date` 共享修改导致 index 路径回归 | 在 P19-S5 test suite 中保留全部现有 index 测试，确保绿色 |
| All-A unavailable 时 `index_name` 展示 | Implementation agent 应在 Service 层引用 `ALL_A_MARKET_NAME` |
| `FundThermometerAdapter` 变成死代码 | Controller 后续裁决保留/标记 deprecated/加回 CLI flag |
| NaN/Inf 检测遗漏 | `_to_decimal` 或调用方显式检测 |

---

## Final Plan Review Conclusion

**`pass-with-risks`**

Plan 的分层边界、契约决策（§7）、strict parsing（§8）、fixture 策略（§9）和 slice sequencing（§10）均已达到 code-generation-ready 水平。五个 findings 均为中低严重度，不构成 blocker。核心风险集中在：unavailable 路径的 name 展示、duplicate-date 检测对共享解析函数的影响范围、以及 all-A fetcher 与 index fetcher 的签名张力。Implementation agent 在编码时明确处理这三点即可安全推进。

---

*Review by AgentDS, 2026-05-23 09:48 CST. No source, test, control, or design files were modified.*
