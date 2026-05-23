# P19-S5 S5-2 Code Review (AgentDS) — 2026-05-23

## Scope

- **Mode**: current changes (uncommitted S5-2 workspace)
- **Branch**: `phase/p19-s5-all-a-pe-source-gate`
- **Base**: S5-1 accepted commit (`7a173ec`)
- **Output file**: `docs/reviews/p19-s5-s5-2-code-review-ds-20260523.md`
- **Included scope**: `fund_agent/services/thermometer_service.py`, `fund_agent/fund/data/thermometer_cache.py`, `tests/services/test_thermometer_service.py`, `tests/fund/data/test_thermometer_cache.py`
- **Excluded scope**: S5-3 CLI/docs files, `fund_analysis_service.py`, P19-S4 source files, public-page adapter, `docs/design.md`, `docs/implementation-control.md`
- **Review truth**: `AGENTS.md`, `docs/design.md` §11, `docs/implementation-control.md`, accepted implementation plan S5-2 slice, S5-1 controller acceptance (`docs/reviews/p19-s5-s5-1-code-review-controller-judgment-20260523.md`), S5-2 implementation artifact (`docs/reviews/p19-s5-s5-2-service-cache-implementation-20260523.md`)
- **Parallel review coverage**: 无 (单 reviewer 全链路走读)
- **Validation (recorded by controller)**: pytest 33 passed (S5-2 tests), 20 passed (analyze regression), ruff all clear, git diff --check passed

## Methodology

逐链路走读了以下关键路径：

1. **Request normalization → default all-A materialization**: `ThermometerRequest()` → `_normalize_request` → `_NormalizedThermometerRequest(index_code="wind_all_a")` → `run()` → `_load_index_reading("wind_all_a")`
2. **Token validation → malformed rejection**: `_normalize_index_codes` → `_is_six_ascii_digits` → ValueError for non-ASCII digits, non-six-digit tokens, empty tokens
3. **Support check → shared classifier**: `_load_index_reading` → `classify_thermometer_code` (S5-1 shared) → early unavailable for unsupported codes
4. **Cache key routing → namespace separation**: `_path_for("wind_all_a")` → `market/wind_all_a_history.json`; `_path_for("000300")` → `index/000300_history.json`; unsupported → ValueError
5. **Source failure → stale cache fallback**: `_load_index_reading` → `ThermometerSourceError` → `cache.load(allow_stale=True)` → stale reading or unavailable
6. **Calculation error propagation**: `calculate_thermometer_reading(insufficient_history)` → ValueError propagates uncaught
7. **Cache bypass prevention**: `ThermometerHistoryCache.load("999999")` → `classify_thermometer_code == "unsupported"` → returns None (before path/IO); `_path_for("999999")` → ValueError
8. **Batch ordering and dedup**: `_normalize_index_codes` → strip → validate → seen-set dedup → preserve-order tuple
9. **Source field isolation**: Service imports only classifier/constants from `thermometer_source`, never `akshare`, never field names (`middlePETTM`, `middlePB`, `date`)

## Findings

### 1-未修复-低-`_load_index_reading` 对 unsupported 的 unavailable 名称在 Service 层用 `thermometer_display_name` 返回原始代码，与 source 层 unavailable 名称路径存在细微不一致

- **入口/函数**: `ThermometerService._load_index_reading` (thermometer_service.py:218–223) vs source 层 `AkshareThermometerSource.load_index_history` (thermometer_source.py:148–168)
- **文件(行号)**: `thermometer_service.py:221–222`
- **输入场景**: 请求 well-formed 但不支持的六位代码如 `999999`，该代码存在于 `SUPPORTED_INDEX_SYMBOLS` 之外
- **实际分支**: `classify_thermometer_code("999999") == "unsupported"` → Service 直接返回 unavailable，`index_name=thermometer_display_name("999999")` → `"999999"`
- **预期行为**: Service 超前返回 unavailable 时，`index_name` 用代码本身是合理的——没有人类可读名称
- **实际行为**: `index_name="999999"`。如果代码后续被加入支持列表 (例如 P19-S4)，`thermometer_display_name` 会自动返回正确名称，行为正确。但如果代码 NEVER 被加入支持，名称字段只是一串数字——这是 unavoidable 的信息缺失，不是 bug
- **直接证据**: `thermometer_service.py:222` → `thermometer_display_name(index_code)` → `thermometer_source.py:102–107` → unsupported 返回 `code` 自身；`thermometer_service.py:248` → source 失败路径也用了同一 helper
- **影响**: 对当前 S5-2 scope 无功能影响；unsupported 代码始终 unavailable，名称字段不含误导信息
- **建议改法和验证点**: 无需修改。当前行为是正确的：没有可用名称时返回代码本身是最小信息损失策略，优于返回空字符串或编造名称。如果未来 P19-S4 增加了更多市场代码，确保 `thermometer_display_name` 同步更新
- **修复风险（低）**: 不适用
- **严重程度（低）**: 非阻塞；信息展示一致性已满足 S5-2 要求

### 2-未修复-低-默认 `AkshareThermometerSource()` 构建在 Service `__init__` 中引入了对 Capability 具体复合类的构造依赖

- **入口/函数**: `ThermometerService.__init__` (thermometer_service.py:146)
- **文件(行号)**: `thermometer_service.py:146`
- **输入场景**: 构造 `ThermometerService()` 时不注入 `index_source`
- **实际分支**: `self._index_source = index_source or AkshareThermometerSource()`
- **预期行为**: 按 plan §7.3，Service 应通过 `_IndexThermometerSource` Protocol 使用 source，不应知道具体 source 类型。当前 Service import 了 `AkshareThermometerSource` 用于默认构造
- **实际行为**: Service 在 `__init__` 中直接构造 `AkshareThermometerSource()`。虽然 Service 不 import `akshare`、不知道 source 字段名，但它知道具体的 Capability 复合类名
- **直接证据**: `thermometer_service.py:25–31` import block 包含 `AkshareThermometerSource`；`thermometer_service.py:146` 直接调用其构造器
- **影响**: 低——`AkshareThermometerSource` 是纯粹的复合派发器 (不含 akshare 调用逻辑)，Service 对它的依赖是类型名的依赖而非协议知识的依赖。如果未来替换 source 实现，Service 需要改一行默认构造代码，但不需要改任何调用逻辑
- **建议改法和验证点**: 可接受为当前最小实现。如果要消除，可以将默认工厂提取为模块级 `_default_index_source_factory()` 函数（类似已有的 `_default_adapter_factory`），使 `__init__` 只依赖 callable。但这在当前 scope 中是过度抽象
- **修复风险（低）**: 不适用
- **严重程度（低）**: 非阻塞；Service 已通过 Protocol 使用 source，构造依赖是合理的默认值提供方式

## Open Questions

- **Q1**: `_load_index_reading` 中对 unsupported 的提前返回（thermometer_service.py:218–223）发生在 cache 查询之前，这意味着即使 unsupported 代码在未来被加入支持，原有的 cache 文件路径也需要通过 `_path_for` 正确路由。当前 `_path_for("unsupported")` 会 raise ValueError，所以 `load()` 中的 `classify_thermometer_code == "unsupported"` 提前返回 None 避免了 ValueError。如果未来代码从 unsupported 变为 supported，`_path_for` 会正确路由，cache 文件如果存在就能被读取。此行为正确，但值得在未来 P19-S4 扩展时验证 cache 兼容性。

- **Q2**: public-page adapter 路径在 `run()` 的末尾（thermometer_service.py:170–171）现在是 dead code（因为 `_normalize_request` 总是返回 index_code 或 index_codes）。plan §7.5 明确说"keep the legacy public-page adapter path as internal/transitional only"。S5-3 CLI 实现需要确认 CLI 不会重新激活这条路径。

## Residual Risk

1. **Legulegu retry 常量差异 (S5-1 结转)**: `ALL_A_FETCH_MAX_ATTEMPTS = 2`（thermometer_source.py:31），而 plan §8.1 建议 `SOURCE_RETRY_ATTEMPTS = 3`。S5-1 controller 已裁决为 non-blocking residual。S5-2 的 stale cache fallback 和 unavailable 测试覆盖了 source failure 场景，降低了此差异的实际风险。

2. **Cache 并发写入**: `ThermometerHistoryCache.save()` 无文件锁。本地 CLI 工具场景下并发写入概率极低，但多次快速连续 `force_refresh=True` 调用可能导致最后写入者覆盖。影响为丢失中间写入的 `cache_updated_at` 时间戳精度，不影响数据正确性。

3. **Cache payload 无 index_code 一致性校验**: `_history_from_payload` (thermometer_cache.py:167–207) 读取 payload 中的 `index_code` 但不校验它与请求的 code 是否一致。路径路由 (`_path_for`) 提供了正确隔离，但如果缓存文件被手动移动到错误位置，可能加载错误数据。此风险仅在手动篡改缓存目录时存在，不影响正常工作流。

4. **S5-3 CLI/docs 风险**: CLI help 文本和 README 尚未更新（留给 S5-3）。当前 `fund-analysis thermometer --help` 可能仍显示旧的公开页快照描述。S5-3 需要确保 CLI default 行为和 help 文本与 S5-2 的 Service 默认 all-A 路由一致。

5. **Analyze 回归**: S5-2 未修改 `fund_analysis_service.py`，analyze 回归测试 20 passed。但 analyze 的 `000300` 集成测试应被扩展以显式断言 `ThermometerRequest(index_code="000300")` 而非依赖 Service 默认行为。当前 analyze 测试通过的事实已证明无回归，但缺少显式的"analyze 不会 fall through 到 default all-A"断言。

## Verdict

**PASS**

S5-2 实现正确完成了所有 plan 要求：

- 默认 `ThermometerRequest()` materialize `wind_all_a`，走 self-owned pipeline ✓
- `wind_all_a` + 6 位 ASCII 数字接受；其他 token malformed ✓
- Service/cache 共享 S5-1 classifier，无 duplicated/divergent support logic ✓
- Service 不 import akshare，不知道 source 字段名 ✓
- Cache namespace: `market/wind_all_a_history.json` + `index/*.json` ✓
- Unsupported 代码不能通过 cache 绕过 support check ✓
- All-A source failure → stale cache fallback → 正确 ✓
- All-A source failure 无 cache → unavailable + 正确 code/name + `valuation_state_candidate="unavailable"` ✓
- 计算契约错误 (样本不足) 传播，不变成 silent stale-cache fallback ✓
- P19-S3 analyze 未修改，analyze 回归 20 passed ✓
- 测试覆盖了 review focus 列出的全部风险面 ✓
