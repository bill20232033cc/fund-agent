# P19-S5 Implementation Plan Re-Review (AgentGLM) — 2026-05-23

## Reviewer

AgentGLM（targeted re-review，仅判断原 F1-F7 是否关闭及 patch 是否引入新 blocker）

## Target

`docs/reviews/p19-s5-all-a-market-thermometer-implementation-plan-20260523.md`（controller patched 版本）

## Method

逐条比对原 review 7 个 findings（`docs/reviews/p19-s5-implementation-plan-review-glm-20260523.md`）与 patched plan 的对应修改，判断 closed / partially-closed / not-closed。然后检查 patch 是否引入新的 material blocker。

## Original Findings Disposition

### F1 [严重] Fixture 日期列名 `日期` 应为 `date` — **CLOSED**

Patched plan 精确修正了三处：

1. §7.3 冻结常量 `ALL_A_DATE_COLUMN = "date"`（英文），并显式声明 "existing index date column remains `DATE_COLUMN = "日期"` and must not be reused for all-A fixtures"。
2. §9 fixture 策略修正为 "All-A PE fixture rows must include `date` and `middlePETTM`"，PB 同理。
3. §9 新增反向测试："Add at least one source test whose fixture intentionally uses Chinese `日期` for all-A rows and assert it fails closed"——这证明 all-A contract 是 source-shaped 而非从 index source 复制。

Slice S5-1 常量列表和测试要求与 §9 一致。原严重事实性错误已完全关闭。

### F2 [高] All-A source adapter 架构选择未定 — **CLOSED**

Patched plan §7.3 做出明确架构决策：

- "Controller decision: add a separate `AkshareAllAMarketThermometerSource` … and keep `AkshareIndexThermometerSource` for six-digit indexes. Do not merge no-arg all-A fetchers into the symbol-based index source class."
- "Add a thin composite source, for example `AkshareThermometerSource`, that implements `ThermometerDataSource.load_index_history(code)` by dispatching to the index source or all-A market source using the shared classifier."
- "Service keeps one injected thermometer source object and does not learn akshare field names."

Slice S5-1 exact changes 完整列出三步：新建 `AkshareAllAMarketThermometerSource`（no-arg fetchers）、保留 `AkshareIndexThermometerSource`（symbol-based）、加 composite dispatch。Implementation agent 不再需要做架构决策。§11 review gates 也新增对应检查。

### F3 [高] Service `_normalize_index_codes` 修改位置未指定 — **CLOSED**

Patched plan §7.6 给出精确修改要求：

- "Modify `_normalize_index_codes()` to accept only exact `wind_all_a` or exactly six ASCII digits."
- "The error message should mention both allowed shapes."
- 列出必须拒绝的 token：`abc`, `wind`, `wind_all_a1`, non-ASCII digit variants。

§10 S5-2 exact changes 给出两个修改点：
- "Modify `_normalize_request()` to materialize the default all-A code in the normalized request."
- "Modify `_normalize_index_codes()` to allow exact `wind_all_a` or six ASCII digits; do not add broader market-code grammar."

S5-2 tests 新增 "`_normalize_index_codes` accepts `wind_all_a` for both single and batch paths and still rejects all other non-six-digit tokens."

Implementation agent 现在有精确的修改函数、修改逻辑和测试要求。

### F4 [中] Service 默认路由精确代码路径未指定 — **CLOSED**

Patched plan §7.5 明确指定修改位置：

- "Implement the default by changing `_normalize_request()` so the no-index request returns `_NormalizedThermometerRequest(index_code="wind_all_a", index_codes=None)`. `run()` should then continue through the existing single-reading path."
- "The legacy public-page adapter path becomes internal/transitional only in this gate. Do not remove `FundThermometerAdapter`; keep its dedicated data-layer tests."

S5-2 tests 明确："`ThermometerService().run(ThermometerRequest(cache_dir=tmp_path))` calls source for `wind_all_a`, not public-page adapter." 以及 "Public-page adapter tests remain in `tests/fund/data/test_thermometer.py`; Service no-arg default test is updated from public-page delegation to all-A source routing."

默认路由逻辑在单一函数 `_normalize_request()` 中实现，`run()` 方法不需要额外分支。

### F5 [中] Strict parsing 对共享 `_records_by_date` 的影响 — **CLOSED**

Patched plan S5-1 exact changes 显式限定 scope：

- "Harden all-A parsing to enforce strict `date`, positive Decimal, duplicate conflict detection, and common-date intersection. **Do not change existing index `_records_by_date()` duplicate overwrite behavior** in this slice unless adding explicit index regression tests proving no P19-S1/S2 behavior regression."

all-A strict parsing 有自己的解析路径，不修改共享的 `_records_by_date`。现有 index source 行为不受影响。

### F6 [中] Cache/source/service 分类器一致性 — **CLOSED**

Patched plan §7.3 定义了单一分类器：

- "Expose one shared code classifier from the Capability data layer, for example `classify_thermometer_code(code) -> Literal["index", "market", "unsupported"]`, plus helper name lookups. Service and cache must import this classifier instead of duplicating `code == "wind_all_a"` checks."

§7.4 指定 cache 使用同一分类器："Implement `_path_for()` using the shared classifier."

S5-1："export/import it consistently from source/cache/service code."
S5-2："Cache, Service support checks, and source dispatch must all use the same classifier/helper exported from Capability data. Tests must fail if `wind_all_a` is saved under `index/`."

三处（source dispatch、cache path、service support check）共享同一 Capability 层分类器，导入路径一致。

### F7 [低] P19-S3 analyze 非回归测试缺失 — **CLOSED**

Patched plan S5-2 新增：

- "Run or add P19-S3 analyze non-regression coverage proving exact `000300` analyze integration still sends `ThermometerRequest(index_code="000300", ...)`, not default `wind_all_a`."
- S5-2 validation commands 包含 `pytest tests/services/test_fund_analysis_service.py -q`。
- S5-3 validation commands 同样包含此回归测试。

## New Issues Introduced By Patch

逐条检查 patch 新增内容是否引入新 blocker：

### NI-1: 无新 blocker

Patch 修改集中在 §7（contract decisions）、§9（fixtures）、§10（slice exact changes）、§11（review gates）。所有修改都是对原 findings 的精确回应，没有扩展 scope、引入新依赖、改变分层或增加新的未覆盖风险。

逐一确认：

- **Composite source 命名**：`AkshareThermometerSource` 使用 "for example" 措辞，但意图明确（index + all-A dispatch）。Implementation agent 可直接采用此名称或等价命名。不构成 blocker。
- **`is_supported_index_code` 去留**：Plan 要求 Service/cache 使用新分类器而非 `code == "wind_all_a"` 重复检查。旧的 `is_supported_index_code` 可在内部委托给新分类器或保持为 convenience wrapper。Implementation agent 有足够上下文决定。不构成 blocker。
- **`_IndexThermometerSource` Protocol docstring**：方法名 `load_index_history` 和参数名 `index_code` 在 all-A 场景下语义略有偏移（"index" → "index or market"）。Plan §7.2 要求更新 `PePbHistory` docstring。Protocol docstring 也应同步更新，但这是 docstring-only 变更，S5-1 allowed files 已包含 `thermometer_types.py` 的 docstring 修改。不构成 blocker。
- **Public-page adapter 保留但 default 不可达**：Plan 明确说 "Do not remove `FundThermometerAdapter`; keep its dedicated data-layer tests" 且 adapter 只通过 Service 构造函数注入可达（测试可显式注入）。默认路径不再走 public page，但 adapter 本身不被删除。这是合理的过渡策略。不构成 blocker。

## Conclusion

**pass**

全部 7 个原 findings 已关闭。Patch 精确回应了每个 finding，包括：
- F1 严重事实性错误：fixture 列名从 `日期` 修正为 `date`，新增反向 fail-closed 测试。
- F2 架构选择：明确新建 `AkshareAllAMarketThermometerSource` + composite `AkshareThermometerSource`。
- F3 规范化修改：精确指定 `_normalize_request()` 和 `_normalize_index_codes()` 修改逻辑。
- F4 默认路由：在 `_normalize_request()` 中 materialize `wind_all_a`。
- F5 shared parsing scope：显式限定 all-A 独立解析路径，不动 `_records_by_date`。
- F6 分类器一致性：定义 Capability 层 `classify_thermometer_code`，source/cache/service 共享。
- F7 analyze 非回归：新增 P19-S3 analyze 回归测试要求。

Patch 未引入新 blocker。Plan 已达到 code-generation-ready 标准，可安全交给 implementation agent。

## Verification

- 本 re-review 期间未修改任何源码、测试、design doc、control doc。
- 仅创建了本 artifact 文件。
