# NAV Repository / Source Adapter Typed Contract Implementation Plan — Review (DS)

日期：2026-05-28

角色：独立 Gateflow plan/review worker（非 controller，非 implementation worker）

Gate：`NAV repository/source adapter typed contract implementation gate`

Gate classification：`heavy`

Review 对象：
- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md`

## 结论

**accepted-with-required-fixes**

Plan 整体保守、fail-closed，正确复述真源，不削弱 FQ0-FQ6，不解除 drawdown_stress blocker。typed contract 的 Literal domain、fail-closed taxonomy、向后兼容策略均正确。但 Slice 1 过粗（typed models 与 adapter/repository 应拆分），且存在 3 个必须在 implementation 前解决的 contract 设计问题（NavType/AdjustmentBasis 重叠、NavSourceMetadata.failure_category 语义冲突、cache metadata 暴露方式 underspecified）。以下 F1-F3 为 required-fix，implementation worker 不应在修复前开始写代码；F4-F6 为 recommended；F7-F9 为 informational。

---

## 独立核验方法

本 review 执行了以下独立核验（不依赖被 review artifact 的声明）：

1. 读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md` — 真源三件套
2. 读取上一 gate controller judgment：`release-maintenance-nav-source-capability-adjusted-basis-controller-judgment-20260528.md`、`release-maintenance-nav-source-adapter-adjusted-basis-contract-controller-judgment-20260528.md`
3. 读取 `fund_agent/fund/data/nav_data.py` — 确认 `_fetch_nav_with_akshare()` 只调用 `indicator="单位净值走势"`，`_load_cached_sync()` 只 SELECT `payload_json`，SQLite schema 有 `source` 和 `updated_at` 列但被丢弃
4. 读取 `fund_agent/fund/data_extractor.py` — 确认 `_NavDataProvider` Protocol、`_load_nav_data_or_unavailable()`、`StructuredFundDataBundle.nav_data: NavDataResult`
5. 读取 `fund_agent/fund/extraction_snapshot.py:989` — 确认 snapshot 只消费旧 `NavDataResult.source/cached/records/unavailable`
6. 读取 `tests/fund/data/test_nav_data.py` — 确认现有 tests 锁定 `source="akshare"` / `source="nav_cache"` 行为
7. 读取最新 006597/2024 snapshot / score — 确认 `nav_data` note 为 `source=nav_cache; cached=True; records=1802`，anchor_present=false，score bond_risk_evidence 字段 pass
8. SQLite schema 核验：`nav_cache` 表确实有 `source TEXT` 和 `updated_at TEXT` 列，当前 `_load_cached_sync()` 丢弃了它们

---

## Finding 1 (required-fix): Slice 1 过粗 — typed models 必须独立为一个 slice

**证据**：Plan 将 6 个文件（新增 `nav_models.py`、`nav_repository.py`、`test_nav_repository_contract.py`，修改 `nav_data.py`、`data/__init__.py`、`test_nav_data.py`）全部放入 Slice 1。

`nav_models.py` 是纯 typed dataclass / Literal / Exception 定义，零 IO 依赖，可以被独立 review、独立 ruff、独立导入验证。`nav_repository.py` 和 `nav_data.py` 改动依赖真实 adapter / cache / akshare 行为。把它们合在一起：

- 纯 contract 定义和 IO 集成混在一个 slice，reviewer 难以独立判断 typed model 设计是否自洽
- IO 相关 test 失败（如 akshare unavailable）会阻断 typed model 的验证
- controller 无法在 typed model 设计有问题时只 reject repository 实现而保留 model 设计

**建议改法**：拆为 Slice 1a 和 Slice 1b（原 Slice 2 顺延为 Slice 3）：

- **Slice 1a — Typed Models**：仅 `nav_models.py` + `data/__init__.py` re-export 更新 + `test_nav_repository_contract.py` 中纯 model validation 测试（dataclass 构造、validator、Literal 穷举、`NavDataContractError` 字段）— 不涉及 adapter/repository IO。
- **Slice 1b — Adapter Metadata + Repository**：修改 `nav_data.py`（cache metadata 暴露 + `load_raw_nav_source()`）+ 新增 `nav_repository.py` + `test_nav_data.py` 扩展 + `test_nav_repository_contract.py` 中 repository 集成测试。

Slice 1a 可独立通过 `uv run ruff check fund_agent/fund/data/nav_models.py` 和 focused model tests。Slice 1b 的 IO 测试失败不会污染 typed model 的 acceptance。

---

## Finding 2 (required-fix): NavType 与 AdjustmentBasis 语义重叠未解决

**证据**：Controller judgment（`release-maintenance-nav-source-adapter-adjusted-basis-contract-controller-judgment-20260528.md`）明确要求：

> NavType and AdjustmentBasis overlap must be resolved or intentionally retained in the next implementation gate.

Plan 定义了两组 enum：

| NavType | AdjustmentBasis |
|---------|-----------------|
| `unit_nav` | `raw_unit_nav` |
| `accumulated_nav` | `accumulated_nav` |
| `adjusted_nav` | `dividend_adjusted_nav` |
| `total_return_index` | `total_return` |
| — | `unknown` |

对应当前 Akshare `单位净值走势` path：series 同时标记 `nav_type="unit_nav"` 和 `adjusted_basis="raw_unit_nav"`。这两个值编码了同一事实（raw unit NAV，未调整），但存在四种不一致风险：

- `nav_type="accumulated_nav"` + `adjusted_basis="raw_unit_nav"` — 含义矛盾
- `nav_type="unit_nav"` + `adjusted_basis="dividend_adjusted_nav"` — 语义不一致
- 未来 source adapter 需要同时设置两个字段，增加出错面
- `FundNavRecord` 也同时携带两者，每条 record 都需要保持一致性

Plan 未引用 controller 的这一要求，未说明是保留重叠还是合并。

**建议改法**：在 plan 的 Contract Design Decisions 中新增一段，明确决策：

- 选项 A（推荐）：保留两者但声明 `NavType` 描述 source-claimed NAV 类型（source 声称返回什么），`AdjustmentBasis` 描述本系统对调整基础的判定（实际可用于什么证据层级）。在 `FundNavSeries.__post_init__` 中校验两者兼容矩阵（如 `unit_nav` 只能配 `raw_unit_nav`，`total_return_index` 只能配 `total_return`），非法组合 raise `NavDataContractError(category="schema_drift")`。
- 选项 B：合并为单一 `AdjustmentBasis`，删除 `NavType`。

无论选 A 或 B，必须在 plan 中记录决策和理由，不应留给 implementation worker 自行判断。

---

## Finding 3 (required-fix): NavSourceMetadata.failure_category 在成功路径上的语义冲突

**证据**：Plan 定义：

```python
class NavSourceMetadata:
    failure_category  # 无 None 默认，暗示必填
```

同时 `FundNavSeries.source: NavSourceMetadata` — 成功的 series 也携带 `NavSourceMetadata`。但成功路径没有 failure，`failure_category` 应为何值？如果填 `""` 或 dummy 值，未来 consumer 无法区分"无失败"和"未记录"。

对比 `FundNavSeries` 自身的 `identity_status` 和 `completeness_status` 都有明确的非失败值（`"verified"`, `"complete_enough"`），但 `NavSourceMetadata` 缺少对等设计。

**建议改法**：将 `failure_category` 改为 `NavFailureCategory | None`，默认 `None`，仅在 source adapter 调用失败且 repository 决定不 fail-closed（如 eligible fallback 场景）时设置。在 docstring 中注明：`None` 表示 source 调用成功；非 `None` 表示 source 调用触发了对应失败类别但未 fail-closed。

---

## Finding 4 (recommended): `FundNavRecord` 缺少 `share_class` 字段

**证据**：Plan 定义 `FundNavRecord` 包含 `date`、`nav_value`、`nav_type`、`adjusted_basis`、`raw_change_rate`、`raw_payload`，不含 `share_class`。`FundNavSeries` 有 `share_class` 和 `share_class_mapping`，contract 要求不混合份额。

但 record-level `share_class` 是防御性设计：如果未来 source adapter 有 bug 导致同 series 内混入不同份额的 record，缺少 record-level 字段会使 bug 不可检测。增加后可让 `__post_init__` validator 逐 record 校验 share_class 一致性。

**建议改法**：在 `FundNavRecord` 中新增 `share_class: str`，`FundNavSeries.__post_init__` 校验所有 record 的 `share_class == series.share_class`。额外的内存开销可忽略（每条 record 只多一个 interned string 引用）。

---

## Finding 5 (recommended): 允许 `identity_status="requested_code_only"` 返回 series 安全，但需强化 future consumer guard

**证据**：Plan 允许 `identity_status="requested_code_only"` 时返回 series 但 `strong_drawdown_evidence_eligible=False`。当前这是安全的，因为：

- `strong_drawdown_evidence_eligible` 是显式 boolean gate
- 所有 future drawdown consumer 必须检查该 flag
- 当前 raw_unit_nav path 永远不会 strong eligible

但 plan 的 Future Consumer Rule 只说"必须检查 `strong_drawdown_evidence_eligible is True`"，未要求同时检查 `identity_status`。如果未来某个 source 能提供 `dividend_adjusted_nav` 但 identity 仍是 `requested_code_only`（source 不返回身份信息），consumer 可能因只看 `strong_drawdown_evidence_eligible` 而接受未验证身份的 adjusted NAV。

**建议改法**：在 Future Consumer Rule 中增加一条：future drawdown consumer 必须同时检查 `identity_status in {"verified"}` AND `strong_drawdown_evidence_eligible is True` AND `adjusted_basis in {"dividend_adjusted_nav", "total_return"}`。三条件缺一不可。

---

## Finding 6 (recommended): cache metadata 暴露方式 underspecified — 实现 worker 需要确切方法签名

**证据**：Plan 只描述意图（cache hit 能暴露 `origin_source` 和 `cache_updated_at`），未指定确切方法。当前代码事实：

- `_load_cached_sync()` (nav_data.py:299-306)：只 `SELECT payload_json`，返回 `NavPayload | None`
- SQLite `nav_cache` 表有 `source TEXT` 和 `updated_at TEXT` 列，当前被丢弃
- 旧 `load_nav_data()` cache hit 返回 `source="nav_cache"` 无 origin info

Plan 提到两个可能方向：改 `_load_cached_sync()` 返回值，或新增 `load_raw_nav_source()`。实现 worker 不应在写代码时才选择。

**建议改法**：在 plan 中明确选择一种方法并给出签名：

推荐选项：新增私有方法 `_load_cached_with_metadata(fund_code) -> tuple[NavPayload, str, str] | None`，返回 `(records, source, updated_at)`。旧 `_load_cached_sync()` 内部调用它但只取 `records`。`load_raw_nav_source()` 调用它并返回完整 metadata。这样旧路径完全不受影响。

---

## Finding 7 (informational): NavCompletenessStatus 与 fail-closed 决策的关系不完整

**证据**：Plan 定义 `NavCompletenessStatus` 有四个值：`complete_enough`、`missing_date_range`、`insufficient_records`、`unchecked`。Fail-closed 表中，caller 传入 `start_date`/`end_date` 但覆盖不足 → fail-closed `missing_date_range`；`minimum_records` 不足 → fail-closed `insufficient_records`。

但 caller 不传 `start_date`/`end_date`/`minimum_records` 时，`completeness_status` 默认值是什么？Plan 未指定。如果默认 `"unchecked"`，这是对的（未请求就不检查）。但如果默认 `"complete_enough"`，就是错的（未检查不能声称完整）。

**建议**：在 `FundNavSeries.__post_init__` 规则中明确：caller 未传约束参数时 `completeness_status="unchecked"`；caller 传了约束且通过时 `completeness_status="complete_enough"`；不通过时直接 fail-closed 不构造 series。

---

## Finding 8 (informational): Series-level nav_type 排除同一 source 返回多种 NAV 类型的场景

**证据**：Plan 定义 `FundNavSeries.nav_type` 和 `adjusted_basis` 为单一值（非 collection）。这意味着如果未来 source adapter 在一次调用中同时返回 unit NAV 和 accumulated NAV（某些数据源的行为），repository 必须拆分成多个 `FundNavSeries` 调用。

这是合理的设计简化（单一系列单一类型），但 plan 未承认这个 tradeoff。如果未来需要多类型 series（如一次请求获取 unit + accumulated，用于 cross-validation），当前 contract 不支持。

**建议**：在 plan 的 Residual Risks 中记录这一设计选择，注明"如果未来 source 在一次响应中返回多种 NAV 类型，需要 repository 层拆分多次 `load_nav_series()` 调用或扩展 contract 为 `FundNavBundle`"。

---

## Finding 9 (informational): `raw_payload: Mapping[str, object]` 创建 future bypass 风险

**证据**：`FundNavRecord.raw_payload` 保留了原始 source 返回的完整 dict。这在当前 gate 是合理的（保留原始数据供 diagnostics），但存在风险：future consumer 可能绕过 typed `nav_value`/`nav_type`/`adjusted_basis`，直接从 `raw_payload` 读取字段。

**建议**：在 `FundNavRecord` docstring 中注明：`raw_payload` 仅供 diagnostics/debugging，production consumer（特别是 drawdown metric）必须只消费 typed 字段。在 Future Consumer Rule 中增加禁止直接读取 `raw_payload` 的条款。

---

## 逐项检查

### 1. Plan 是否 handoff-ready/code-generation-ready？

**部分**。Slice 1a (typed models) 在 F2 解决后可直接实现。Slice 1b (repository + adapter) 需要 F1/F3/F6 解决。

### 2. Slice 是否过粗？

**是**。见 F1。Slice 1 应拆为 typed models (1a) 和 adapter/repository (1b)。

### 3. 是否保持旧兼容？

**是**。旧 `load_nav_data()` 签名和 `NavDataResult` shape 不变；现有 test 的 `source`/`cached` 断言仍通过。Plan 正确识别了 snapshot 只消费旧 result 的事实。

### 4. Typed contract 是否正确表达所有概念？

**基本正确，但有 gap**。见 F2（NavType/AdjustmentBasis 重叠）、F3（failure_category 语义）、F4（record-level share_class）。

### 5. raw_unit_nav 是否明确 not strong-evidence eligible？

**是**。Plan 多处明确：`adjusted_basis="raw_unit_nav"` → `strong_drawdown_evidence_eligible=False`；raw unit NAV 不伪装 adjusted/total-return。

### 6. Fail-closed taxonomy 是否充分？

**是**。覆盖 `not_found`、`unavailable`、`schema_drift`、`identity_mismatch`、`integrity_error`、`adjustment_basis_unknown`、`missing_date_range`、`insufficient_records`。与现有 `AnnualReportSourceFailure` taxonomy 一致。前两类保留为 future fallback eligible，后六类禁止 fallback。

### 7. 允许返回 series 但 not strong eligible 是否安全？

**是，但需强化 consumer guard**。见 F5。当前安全因为 `raw_unit_nav` path 永不为 strong eligible。未来若出现 `dividend_adjusted_nav` + `identity="requested_code_only"` 场景，需三条件 gate。

### 8. Cache metadata 暴露是否通过 adapter/repository 边界？

**意图正确，方法 underspecified**。见 F6。Plan 正确要求不直接读 SQLite，但未指定具体方法签名。

### 9. 是否改动 bond extractor/score/snapshot/quality gate/golden 或削弱 FQ0-FQ6？

**否**。Plan non-goals 明确排除所有这些。独立核验证实 snapshot 只消费旧 `NavDataResult`，新 typed path 不触及这些模块。

### 10. Tests/validation/docs scope 是否足够？

**基本足够，缺一项**。Slice 1 validation 为 focused pytest + ruff；Slice 2 为 full ruff + full pytest coverage + real 006597 smoke。但 plan 未讨论：
- 单文件覆盖率目标（`nav_models.py`、`nav_repository.py` 新增模块是否朝 ≥80% 目标）
- CI 全局 `--cov-fail-under=50` 当前值是否仍足够（见 `docs/design.md` §12 plan review 检查项）
- 真实 smoke 是否应标记为 network-dependent，不应进入 CI

建议在 plan 中补充：新增模块目标单文件 ≥80%；真实 006597 smoke 仅作为 implementation evidence artifact，不进入 CI。

---

## Residual Risks（本 review 追加）

- `NavType`/`AdjustmentBasis` 如果选合并方案（F2 选项 B），会影响 `FundNavSeries` 和 `FundNavRecord` 字段布局，增加返工风险；建议选选项 A（保留两者 + 兼容矩阵）。
- 当前 cache SQLite schema 的 `source` 列存储的是 `"akshare"` 字符串，无 source URL/ID/version；未来如需更丰富的 provenance 需 schema migration。
- Plan 未讨论 `FundNavDataAdapter` 的 `fetcher` 注入如何与 `FundNavRepository` 协作 — repository 默认构造 `FundNavDataAdapter()`，但如果未来有多个 source adapter（如 Eastmoney NAV vs Akshare NAV），repository 的单一 adapter 注入不够。

---

## Self-Check

- [x] 独立核验了所有关键代码和真源
- [x] 所有 findings 有直接证据（代码行号、controller judgment 引用、SQLite schema 核验）
- [x] 未声称本 review 可以替代 controller judgment
- [x] 未要求更改 FQ0-FQ6、score、snapshot、golden、bond extractor
- [x] 未要求解除 drawdown_stress blocker
- [x] 结论为 accepted-with-required-fixes，符合 gateflow plan review 格式
- [x] Required fixes 给出了具体建议改法
- [x] 未修改任何代码文件
