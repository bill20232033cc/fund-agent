# NAV Repository / Source Adapter Typed Contract Implementation Plan Review

日期：2026-05-28

Reviewer：MiMo

Artifact under review：`docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md`

Work unit：`NAV repository/source adapter typed contract implementation gate`

Gate classification：`heavy`

## Conclusion

**accepted-with-required-fixes**

## Review Scope

Review 依据：`AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、上一 NAV adjusted-basis contract controller judgment、上一 NAV capability controller judgment、最新 006597 snapshot/score/quality_gate、计划 artifact、`fund_agent/fund/data/nav_data.py`、`fund_agent/fund/data_extractor.py`、`tests/fund/data/test_nav_data.py`、`fund_agent/fund/data/__init__.py`、`fund_agent/fund/extraction_snapshot.py`。

## Findings

### F1 — `identity_status="requested_code_only"` 缺少显式 strong-eligible 约束

**Severity**：required-fix

**Evidence**：plan §Typed Models — FundNavSeries validator 约束列表只写了：

- `adjusted_basis="raw_unit_nav"` 时 `strong_drawdown_evidence_eligible=False`
- `identity_status in {"identity_mismatch", "unknown"}` 不得成为 strong evidence

但 `identity_status="requested_code_only"` 不在上述禁止集合中。当前 Akshare path 因为 `adjusted_basis="raw_unit_nav"` 所以安全，但 plan 的 contract 设计意图是让 typed contract 成为 future drawdown consumer 的唯一可消费边界。如果未来有新 source adapter 返回 `adjusted_basis="dividend_adjusted_nav"` 且 `identity_status="requested_code_only"`，按当前 validator 规则它会成为 strong eligible —— 但 source-returned identity 未验证时不应作为 strong evidence。

**Evidence source**：plan §Typed Models, line 176-178; contract controller judgment §Drawdown Evidence Boundary, line 64-67

**Suggested fix**：在 FundNavSeries validator 约束中增加：

> `identity_status="requested_code_only"` 时，`strong_drawdown_evidence_eligible=False`，reason 必须说明 source-returned identity 未验证。

或扩大禁止集合为 `identity_status not in {"verified"}` 时不得 strong eligible。

---

### F2 — 日期去重验证归属不明确

**Severity**：required-fix

**Evidence**：plan §Fail-Closed Taxonomy 表格写：

> NAV 值非正、records 日期重复导致路径不可用、排序无法稳定 → `integrity_error` → fail-closed

但 §Typed Models — FundNavSeries validator 约束列表没有提到日期唯一性检查。validator 只检查 `record_count == len(records)`、records 非空、record-level nav_type/adjusted_basis 与 series 一致、adjusted_basis 不是 unknown、identity_status 约束。

如果 validator 不检查日期唯一性，repository normalization 必须检查；但 plan §Slice 1 Exact Changes 的 normalization rules 也没有明确日期去重步骤。

**Evidence source**：plan §Fail-Closed Taxonomy line 230; §Typed Models validator line 170-178; §Slice 1 Exact Changes line 208-218

**Suggested fix**：在以下两处之一显式声明日期去重检查：

1. FundNavSeries validator 约束增加：`records` 中 `date` 不得重复；重复时 raise `NavDataContractError(category="integrity_error")`。
2. 或在 §Raw Akshare Normalization rules 中增加：parsed records 按 date 去重；重复 date 是 `integrity_error`。

推荐放在 repository normalization 阶段（Fail-Closed Taxonomy 的语义归属），但必须在 plan 中显式声明，不留歧义。

---

### F3 — `NavType` 与 `AdjustmentBasis` 语义重叠未消解

**Severity**：advisory

**Evidence**：contract controller judgment §Residuals 已指出：

> `NavType` 和 `AdjustmentBasis` overlap must be resolved or intentionally retained in the next implementation gate.

plan §Typed Models 定义了 `NavType = Literal["unit_nav", "accumulated_nav", "adjusted_nav", "total_return_index"]` 和 `AdjustmentBasis = Literal["raw_unit_nav", "accumulated_nav", "dividend_adjusted_nav", "total_return", "unknown"]`。两者都包含 `accumulated_nav`，语义有重叠。

当前 Akshare path 下 `nav_type="unit_nav"` + `adjusted_basis="raw_unit_nav"` 可以区分，但 plan 没有说明 `NavType` 和 `AdjustmentBasis` 的正交关系或何时两者值不同。

**Evidence source**：plan §Typed Models line 114-128; controller judgment §Residuals line 93

**Suggested fix**：在 §Typed Models 或 §Contract Design Decisions 中增加一句说明：

> `NavType` 描述 series 的数学形态（单位净值 / 累计净值 / 调整净值 / 总回报指数）；`AdjustedBasis` 描述 series 的处理管线（未处理 / 累计 / 分红调整 / 总回报 / 未知）。当前 Akshare path 两者都固定为 unit_nav/raw_unit_nav；未来 source 若返回累计净值，`nav_type="accumulated_nav"` + `adjusted_basis` 仍需独立验证。

---

### F4 — `RawNavSourceResult` 提议与 Slice 1 实现方案不一致

**Severity**：advisory

**Evidence**：plan §Raw Akshare Normalization 提议了 `RawNavSourceResult` dataclass（含 `fund_code`、`records`、`source`、`origin_source`、`cached`、`retrieved_at`、`cache_updated_at`），但 §Slice 1 Exact Changes 第 2-3 步改用"私有 cache entry dataclass 或等价结构" + `load_raw_nav_source()` 方法。两处描述的实现路径不同。

`RawNavSourceResult` 是 public 还是 private？是 dataclass 还是 tuple？worker 需要选择一个。

**Evidence source**：plan §Raw Akshare Normalization line 189-200; §Slice 1 Exact Changes line 256-258

**Suggested fix**：在 plan 中明确：`RawNavSourceResult` 是 repository 内部使用的 private 结构（不进入 `data/__init__.py` re-export），或改为明确说 `load_raw_nav_source()` 返回一个 private `_RawNavCacheEntry` dataclass。消除两处描述的歧义。

---

### F5 — `NavDataContractError` 与现有 `AnnualReportSourceFailure` 的关系未说明

**Severity**：advisory

**Evidence**：`docs/design.md` §6.1 定义了年报来源失败分类（`not_found`、`unavailable`、`schema_drift`、`identity_mismatch`、`integrity_error`），对应 `AnnualReportSourceFailure`。plan §Fail-Closed Taxonomy 定义了 `NavFailureCategory`，增加了 `adjustment_basis_unknown`、`missing_date_range`、`insufficient_records`。

两者 failure category 有重叠（`not_found`、`unavailable`、`schema_drift`、`identity_mismatch`、`integrity_error`），但 plan 没有说明它们是否共享基础类型或完全独立。

**Evidence source**：`docs/design.md` §6.1; plan §Typed Models line 150-159

**Suggested fix**：在 plan 中加一句：`NavFailureCategory` 与 `AnnualReportSourceFailure` 的 failure category 是独立定义，不共享基础类型；重叠的类别名称保持语义一致但类型独立。这避免 worker 误引入跨层依赖。

---

### F6 — Slice 1 未显式声明 `_load_cached_sync` 返回变更对旧 `load_nav_data()` 的影响路径

**Severity**：advisory

**Evidence**：plan §Slice 1 Exact Changes 第 2 步说：

> 修改 `_load_cached_sync()` 为私有 cache entry 返回 records/source/updated_at，再让旧 `load_nav_data()` 只取 records 并继续返回旧 source `nav_cache`。

当前 `_load_cached_sync` 只 SELECT `payload_json`（见 `nav_data.py:300-306`）。修改后需要同时 SELECT `source` 和 `updated_at`。这改变了 SQLite 查询语句。

旧测试 `test_nav_data_adapter_persists_and_reuses_cache` 验证 cache hit 时 `source=="nav_cache"` 和 `cached==True`。如果 worker 把 `_load_cached_sync` 返回值改为包含 source/updated_at 的结构但 `load_nav_data()` 正确忽略这些字段，旧测试不受影响。但 plan 应该显式声明这个兼容性保证。

**Evidence source**：`nav_data.py:299-306`; `tests/fund/data/test_nav_data.py:49-57`

**Suggested fix**：在 §Slice 1 Exact Changes 第 2 步增加：旧 `load_nav_data()` 在 cache hit 时仍返回 `NavDataResult(source="nav_cache", cached=True)`，旧测试不需要修改。

---

### F7 — `NavSourceMetadata.failure_category` 何时为 None 未说明

**Severity**：advisory

**Evidence**：plan §Typed Models 定义 `NavSourceMetadata` 包含 `failure_category`，但没有说明成功时该字段的值。成功 series 应该 `failure_category=None` 还是不设该字段？

如果 `FundNavSeries` 代表成功结果（失败时 raise `NavDataContractError`），那 `NavSourceMetadata.failure_category` 在成功 series 中应该是 `None`。但 plan 没有显式声明。

**Evidence source**：plan §Typed Models line 165-166

**Suggested fix**：在 `NavSourceMetadata` 定义旁注明：成功 series 中 `failure_category=None`；`failure_category` 只在 future fallback 或 diagnostic 场景中非空。

---

## Review Dimension Summary

| # | Review Focus | Verdict |
|---|---|---|
| 1 | handoff-ready / code-generation-ready | PASS — plan 有完整的 slices、exact file changes、test assertions、validation commands 和 stop conditions |
| 2 | slice 是否过粗 | PASS — Slice 1 内聚（models + repository + adapter normalization + tests），Slice 2 独立（docs + smoke）；拆分 typed models/adapter metadata/repository/docs 不增加价值反而增加集成风险 |
| 3 | 旧 `load_nav_data()` / `NavDataResult` 兼容 | PASS with advisory (F6) — plan 显式保留旧方法和返回类型；F6 要求补充 `_load_cached_sync` 查询变更的兼容性声明 |
| 4 | typed contract 是否正确表达 | PASS with advisory (F3, F5, F7) — Literal domain 和 dataclass 覆盖了所需维度；F3/F5/F7 是语义清晰度改进 |
| 5 | `raw_unit_nav` 明确 not strong-evidence eligible | PASS — plan 显式 `strong_drawdown_evidence_eligible=False` 并要求 reason 说明 |
| 6 | fail-closed taxonomy 充分 | PASS with required-fix (F2) — 8 类 failure category 覆盖完整；F2 要求显式声明日期去重验证 |
| 7 | 返回 series 但 not strong eligible 安全性 | PASS with required-fix (F1) — 当前 raw_unit_nav path 安全；F1 要求补 `requested_code_only` 约束 |
| 8 | cache metadata 通过 adapter/repository 边界 | PASS — plan 显式禁止 production 直读 SQLite |
| 9 | 不改动 bond extractor/snapshot/score/quality gate/FQ0-FQ6 | PASS — plan 显式 non-goal，新增模块不影响现有路径 |
| 10 | tests/validation/docs scope 足够 | PASS — focused tests + full ruff + full pytest + real smoke + docs sync；无需 snapshot/score/quality gate rerun 因为不触碰相关路径 |

## Required Fixes Summary

| ID | Fix |
|---|---|
| F1 | 在 FundNavSeries validator 增加 `identity_status="requested_code_only"` 时 `strong_drawdown_evidence_eligible=False` 约束 |
| F2 | 在 validator 或 normalization rules 中显式声明日期去重检查和 `integrity_error` 归属 |

## Self-Check

- [x] 读取了 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`
- [x] 读取了上一 NAV adjusted-basis contract controller judgment
- [x] 读取了上一 NAV capability controller judgment（通过 implementation-control.md Active Gate Ledger 确认）
- [x] 读取了最新 006597 snapshot/score/quality_gate
- [x] 读取了 `nav_data.py`、`data_extractor.py`、`test_nav_data.py`、`data/__init__.py`、`extraction_snapshot.py`
- [x] 10 个 review focus 全部覆盖
- [x] Findings 使用 gateflow plan finding 格式，含 severity、evidence、evidence source、suggested fix
- [x] 结论为 `accepted-with-required-fixes`
- [x] 未修改除 review artifact 外的任何文件
- [x] 未启动 `$gateflow` / `/gateflow`，未 implementation、fix、commit、push、PR、merge
