# CSRC EID Accumulated NAV Adapter Normalization Implementation Plan — Review (MiMo)

日期：2026-05-29
角色：plan review worker（非 controller，非 implementation worker）
Review target：`docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-20260529.md`

## Verdict

**accepted-with-required-fixes**

Plan 整体结构清晰、scope 合理、non-goal 边界严格，但存在 4 个 required findings 阻塞 code-generation-ready 状态，需要 plan fix 后才能派 implementation worker。

## Review Source Checklist

| Source | Read |
|---|---|
| `AGENTS.md` | Yes |
| `docs/design.md` | Yes |
| `docs/implementation-control.md` | Yes |
| Typed NAV controller judgment | Yes |
| CSRC EID / stock-sdk controller judgment | Yes |
| CSRC EID / stock-sdk evidence | Yes |
| `fund_agent/fund/data/nav_models.py` | Yes |
| `fund_agent/fund/data/nav_repository.py` | Yes |
| `fund_agent/fund/data/nav_data.py` | Yes |

## Findings

### F1 — Repository Source Selection Mechanism 未定义（Required）

**Severity**: blocking
**Location**: §4.8, §5 (`nav_repository.py`), §6 Slice 3

当前 `FundNavRepository.__init__` 接受 `FundNavDataAdapter | None`，默认创建 `FundNavDataAdapter()`（Akshare raw unit NAV）。Plan 声称 Slice 3 要 "Make default `FundNavRepository()` use `CsrcEidNavSource` for `load_nav_series()`"，但未指定实现机制：

- **方案 A**：修改 `__init__` 默认值为 `CsrcEidNavSource`。但 `CsrcEidNavSource` 的 `load_raw_nav_source` 签名包含 `share_class/start_date/end_date`，而 `FundNavDataAdapter` 不接受这些参数。两者没有共同 Protocol。
- **方案 B**：在 repository 内部根据 fund_code 路由到不同 source。但这违反 §4.8 "Repository 负责 source adapter selection" 的表述，且需要在 repository 中硬编码 fund_code 判断逻辑。
- **方案 C**：定义新的 source Protocol，两者都实现。但 plan 说 "不添加 broad `source_options` dict"，也未提到新 Protocol。

Plan 的 stop condition 说 "If repository cannot support both CSRC default and injected raw fake without a source-selection public API redesign, stop and ask controller"，但这个 stop condition 应该在 plan 阶段就被解决，而不是留给 implementation worker。

**Fix required**: 明确 repository source 选择机制。建议：定义 `_NavSourceAdapter` Protocol（包含 `load_raw_nav_source(fund_code, *, share_class, start_date, end_date, force_refresh)`），让 `FundNavDataAdapter` 和 `CsrcEidNavSource` 都实现它，repository 默认使用 `CsrcEidNavSource`，测试通过注入 `FundNavDataAdapter` 或 `_FakeRawNavAdapter` 覆盖 raw-unit 路径。

---

### F2 — `_RawNavSourceResult` 与 CSRC EID DTO 的类型不兼容（Required）

**Severity**: blocking
**Location**: §5 (`nav_data.py`), §6 Slice 1, §6 Slice 3

当前 `_RawNavSourceResult.records` 类型是 `NavPayload = list[dict[str, object]]`，其中每条 record 是 Akshare 返回的中文字段 dict（`净值日期`、`单位净值`、`日增长率`）。

CSRC EID source adapter 返回的 raw records 需要包含不同字段（`估值日期`、`累计净值`、`单位净值`、`基金代码`、`基金名称`、`份额类别`、`classification`）。Plan §6 Slice 3 说 "parse `累计净值` as record `nav_value`"，但 `_normalize_raw_record()` 当前硬编码读取 `净值日期`（`_REQUIRED_DATE_COLUMN`）和 `单位净值`（`_REQUIRED_UNIT_NAV_COLUMN`）。

Plan 说要 "将 CSRC EID raw DTO 规范化为 accumulated `FundNavSeries`"，使用 `_normalize_accumulated_nav_series(...)` 私有 helper，但未指定这个 helper 是直接读取 CSRC EID raw records 的字段名，还是需要先将 CSRC EID records 转换为与 Akshare 兼容的字段名。

**Fix required**: 明确 CSRC EID raw records 到 `FundNavRecord` 的 normalization 路径。建议：`_normalize_accumulated_nav_series` 直接读取 CSRC EID 特定字段名（`估值日期`、`累计净值`），不经过 `_normalize_raw_record` 的 Akshare 字段映射。

---

### F3 — `strong_drawdown_evidence_eligible` 状态语义冲突（Required）

**Severity**: blocking
**Location**: §2, §4.4, `nav_models.py:530-563`

Plan 声称 CSRC EID accumulated NAV series 设置 `identity_status="verified"` 和 `adjusted_basis="accumulated_nav"`。但当前 `_apply_strong_drawdown_eligibility()` 的逻辑是：只要 `identity_status != "requested_code_only"` 且 `adjusted_basis != "raw_unit_nav"`，就会设置 `strong_drawdown_evidence_eligible=True`。

这意味着 CSRC EID accumulated NAV series 会自动变成 strong drawdown evidence eligible——但 plan 明确说 "本 gate 不实现 drawdown metric、不解除 `drawdown_stress` blocker"。

这不是代码 bug，而是 plan 与现有 validator 之间的语义冲突。Implementation worker 如果按 plan 设置 typed fields，会产生一个 `strong_drawdown_evidence_eligible=True` 的 series，而 controller judgment 明确说 drawdown blocker 未解除。

**Fix required**: 明确 CSRC EID accumulated series 的 `strong_drawdown_evidence_eligible` 状态。两种选择：
- **选项 A**：接受 `strong_drawdown_evidence_eligible=True` 表示 "NAV source 已 verified 且 accumulated basis 已证明，但 drawdown metric contract 尚未实现"。在 plan 中明确说明这不等同于 blocker 解除。
- **选项 B**：在 `_apply_strong_drawdown_eligibility` 中增加条件，要求额外的 "metric contract accepted" 标志才能设为 `True`。但这需要修改 `FundNavSeries` 模型。

建议选 A，在 evidence artifact 中显式声明。

---

### F4 — Sync/async 和 HTTP client 选择未对齐（Required）

**Severity**: blocking
**Location**: §6 Slice 2

当前 `FundNavRepository.load_nav_series()` 是 `async` 方法，`FundNavDataAdapter.load_raw_nav_source()` 也是 `async`（内部通过 `asyncio.to_thread` 调用同步 akshare）。

Plan §6 Slice 2 说 "Use stdlib `urllib.request` or existing project HTTP pattern if present"。但 `urllib.request` 是同步阻塞调用。如果 `CsrcEidNavSource.load_raw_nav_source()` 是 async，它需要在内部用 `asyncio.to_thread` 包装 `urllib.request`；如果是同步的，repository 的 `await` 调用会失败。

Plan 未指定 `CsrcEidNavSource.load_raw_nav_source()` 的 async/sync 签名，也未说明如何桥接。

**Fix required**: 明确 `CsrcEidNavSource.load_raw_nav_source()` 为 `async` 方法，内部通过 `asyncio.to_thread` 调用同步 HTTP client（`urllib.request` 或 `httpx`）。或者明确使用 `httpx.AsyncClient`（项目已有 `httpx` 依赖用于年报下载）。

---

### F5 — HTML 解析依赖未声明（Minor）

**Severity**: non-blocking
**Location**: §6 Slice 2

CSRC EID 返回 HTML 页面，需要解析 table rows、pagination info、share-class links。Plan 未指定 HTML 解析方案。选项：

- stdlib `html.parser`：可用但编写复杂。
- `beautifulsoup4`：项目未声明为依赖，需要新增。
- 正则匹配：脆弱，违反 AGENTS.md 禁止魔法字符串原则。

**Fix recommended**: 在 plan 中声明 HTML 解析方案。建议使用 stdlib `html.parser` + `re` 模块组合，避免新增依赖；或者如果接受新增依赖，明确写入 plan 的 affected files。

---

### F6 — HTTP 超时/重试策略未定义（Minor）

**Severity**: non-blocking
**Location**: §6 Slice 2

CSRC EID 是外部 HTTP 端点，plan 未定义：
- 连接/读取超时
- 重试策略（瞬时网络失败 vs 持久失败区分）
- 并发限制

**Fix recommended**: 在 Slice 2 中增加超时配置（建议连接超时 10s、读取 30s），瞬时失败归类为 `unavailable` 且最多重试 2 次。不需要复杂的重试框架，但需要明确边界。

---

### F7 — Pagination Error Handling 缺少具体场景覆盖（Minor）

**Severity**: non-blocking
**Location**: §6 Slice 2, §7

Plan §7 test matrix 提到 "duplicate date / total mismatch / page gap -> `integrity_error`"，但未覆盖以下场景：

- 分页 total 为 0 但 search/detail 返回成功
- 分页 total 变化（中途新增记录导致 total 不一致）
- 最后一页记录数与预期不符（total % limit != 0 的边界）

**Fix recommended**: 在 test matrix 中补充上述场景，或在 plan 中明确这些边界由 implementation worker 按 fail-closed 原则自行处理。

---

### F8 — `strong_drawdown_evidence_eligible` 在 plan §7 test matrix 中缺失（Minor）

**Severity**: non-blocking
**Location**: §7

Plan §7 test matrix 未包含 CSRC EID accumulated series 的 `strong_drawdown_evidence_eligible` 状态测试。结合 F3，需要在 test matrix 中明确该字段的预期值。

**Fix recommended**: 在 §7 中增加一行：`| Drawdown eligibility | CSRC EID accumulated series strong_drawdown_evidence_eligible 状态与 plan 决策一致 |`。

---

### F9 — stock-sdk Rejection Test 的实现方式过于模糊（Minor）

**Severity**: non-blocking
**Location**: §6 Slice 4

Plan 说 "This may be a pure test helper asserting no production `stock-sdk` adapter exists and no dependency is imported, plus a source evaluation fixture function that classifies date-shift as `integrity_error`"。"may be" 不够 code-generation-ready。

**Fix recommended**: 明确为两个具体测试：
1. `test_no_stock_sdk_runtime_dependency`：断言 `fund_agent.fund.data` 不 import stock-sdk 相关模块。
2. `test_date_shift_classified_as_integrity_error`：给定 stock-sdk 风格的 date-shifted records，验证 normalization 产生 `integrity_error`。

---

### F10 — docs/design.md 更新范围需与真源规范对齐（Minor）

**Severity**: non-blocking
**Location**: §6 Slice 5

Plan 说 "`docs/design.md`：update current implemented NAV section to say typed repository now normalizes CSRC EID accumulated NAV as primary typed path"。但 `AGENTS.md` 真源规范要求 "只有经过当前 gate 裁决并回写的内容才可作为设计真源"。Plan 需要明确：design.md 的更新只写当前代码事实，不写 "CSRC EID 是 primary path" 这种设计决策（那属于 controller judgment 回写）。

**Fix recommended**: 将 design.md 更新限定为 "当前代码已实现 CSRC EID accumulated NAV normalization" 的事实陈述，不写 "primary" 或 "default" 等设计判断用语；设计决策由 controller judgment 回写。

---

## Residual Risks（无 blocking findings 时列出）

即使 required fixes 全部解决，以下 residual risks 需要 controller 和 implementation worker 持续关注：

1. **CSRC EID endpoint 稳定性**：CSRC EID 是政府网站，无版本化 API。HTML schema 变化会导致 `schema_drift`，但 plan 已有 fail-closed 处理。建议 implementation 完成后增加 schema version hash 监控。

2. **A/C 最早 blank accumulated rows**：evidence 已记录 A/C 2018-12-07 和 2018-12-14 有 blank accumulated NAV。Plan 的 missing_date_range 处理逻辑合理，但 real smoke 如果请求包含这些日期的窗口会触发 fail-closed。建议 real smoke 使用 `minimum_records=30`（已指定），这会自然跳过最早期 blank rows。

3. **F share search-index gap 的长期稳定性**：F `022176` direct search missing 是 CSRC 搜索索引限制。如果 CSRC 修复了搜索索引，adapter 的 F fallback 逻辑仍然安全（search 先尝试直接搜索，成功则不走 product anchor fallback）。但如果 CSRC 移除了 detail page 的 F classification links，adapter 会 fail closed with `identity_mismatch`。

4. **`source_query_params` tuple 的可扩展性**：`tuple[tuple[str, str], ...]` 结构简单但不可变。如果未来 source 需要更复杂的 query 描述（如 nested params），可能需要重构。当前 CSRC EID 场景足够。

5. **real smoke 网络依赖**：Slice 5 real smoke 依赖 CSRC EID 实时可用。如果 smoke 环境无网络访问，controller 需要决定是否接受 `unavailable` residual + fixture coverage 作为替代。

---

## Summary

| Category | Count |
|---|---|
| Blocking (required fixes) | 4 |
| Non-blocking (recommended) | 6 |
| Residual risks | 5 |

Plan 的架构方向正确：CSRC EID 作为 accumulated NAV primary source，通过 typed repository boundary 归一化，fail-closed taxonomy 不变，non-goal 边界严格。但 repository source selection 机制、DTO 类型兼容性、strong drawdown eligibility 语义和 async/HTTP client 对齐这 4 个问题需要在 plan fix 中明确，否则 implementation worker 需要自行做架构决策，违反 "plan 是否足够 code-generation-ready" 的 review 标准。

Controller 建议：派 planning fix worker 解决 F1-F4 后，即可派 implementation worker 按 Slice 1-5 实现。
