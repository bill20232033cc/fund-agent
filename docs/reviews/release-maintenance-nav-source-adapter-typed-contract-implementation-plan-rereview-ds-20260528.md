# NAV Repository / Source Adapter Typed Contract Implementation Plan — Re-Review (DS)

日期：2026-05-28

角色：独立 Gateflow plan/review worker（复用原始 DS review 身份）

Gate：`NAV repository/source adapter typed contract implementation gate`

Re-review 对象：
- Plan: `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md`
- Source review: `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-review-ds-20260528.md`
- Fix artifact: `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-fix-20260528.md`

## 结论

**accepted**

全部 4 个 required verification items (F1/F2/F3/F6) 均已修复。Controller 额外要求的 F6 cache metadata 方法签名已足够明确。Recommended items (F4/F5/F7/F8/F9) 均已纳入 plan 且未引入新 blocker。Plan 现已 handoff-ready / code-generation-ready。

---

## 逐项验证

### DS F1 — Slice 过粗拆分：已修复

原 finding：Slice 1 将 typed models + adapter/repository + tests 混在一起，IO 测试失败会阻断纯 model 验证。

Plan 变更：
- 原 Slice 1 拆为 **Slice 1a**（Typed Models And Pure Contract Tests，plan:274–328）和 **Slice 1b**（Adapter Metadata, Repository Normalization, Integration Tests，plan:329–391）。
- Slice 1a 仅涉及 `nav_models.py`、`data/__init__.py`、`test_nav_repository_contract.py`（纯 model tests），零 IO 依赖。
- Slice 1b 显式声明 prerequisite：`Slice 1a 已通过并被 controller 接受`（plan:341）。
- 两个 slice 有独立的 validation 命令和 stop conditions。

验证通过。typed model 设计和 IO 集成已正确解耦。

---

### DS F2 — NavType/AdjustmentBasis 决策：已修复

原 finding：controller judgment 要求显式解决 NavType/AdjustmentBasis 重叠，但 plan 未引用该要求、未决策。

Plan 变更（plan:164–173）：
- 明确决策为 DS 推荐 option A：**保留两者**。
- 新增语义区分：`NavType` = source-claimed / math shape；`AdjustmentBasis` = 本系统对调整基础的判定。
- 新增兼容矩阵（4 行）：

| NavType | Allowed AdjustmentBasis |
|---|---|
| `unit_nav` | `raw_unit_nav` |
| `accumulated_nav` | `accumulated_nav` |
| `adjusted_nav` | `dividend_adjusted_nav` |
| `total_return_index` | `total_return` |

- `unknown` 只允许作为中间状态，成功 series 不允许。
- 非法组合 → `schema_drift` fail-closed。
- Validator（plan:189）和 Slice 1a 测试（plan:304）均覆盖兼容矩阵校验。

验证通过。决策明确、矩阵完备、fail-closed。

---

### DS F3 — failure_category None 成功语义：已修复

原 finding：`NavSourceMetadata.failure_category` 在成功路径缺少 None 默认，无法区分"无失败"与"未记录"。

Plan 变更（plan:178）：
- 类型改为 `failure_category: NavFailureCategory | None`。
- 明确语义：成功 series 中必须为 `None`；非空仅用于 future fallback/diagnostic 场景。
- Slice 1a（plan:297）：`failure_category 类型为 NavFailureCategory | None，成功 series 默认为 None`。
- Slice 1a 测试（plan:302）：`failure_category is None success path`。

验证通过。语义明确，与 `identity_status` / `completeness_status` 的设计模式一致。

---

### DS F6 — Cache metadata 方法签名：已明确

原 finding：cache metadata 暴露方式只描述意图，未指定确切方法签名。

Controller 额外要求：确认 F6 方法签名是否已足够明确。

Plan 变更（plan:216–237）：
- 新增两个私有类型和方法的确切签名：

```python
@dataclass(frozen=True, slots=True)
class _NavCacheEntry:
    records: NavPayload
    source: str
    updated_at: str

def _load_cached_with_metadata(self, fund_code: str) -> _NavCacheEntry | None: ...
def _load_cached_sync(self, fund_code: str) -> NavPayload | None: ...
```

- 实现要求完整说明：
  - `_load_cached_with_metadata()` 查询 `payload_json`、`source`、`updated_at` → `_NavCacheEntry`
  - 旧 `_load_cached_sync()` 保持 `NavPayload | None` 返回类型，内部只调用新方法并取 records
  - `load_raw_nav_source()` 使用 `_load_cached_with_metadata()` 暴露 metadata
  - 旧 `load_nav_data()` cache hit 仍返回 `NavDataResult(source="nav_cache", cached=True)`
  - 私有类型 `_NavCacheEntry` 和 `_RawNavSourceResult` 不进入 `data/__init__.py` public re-export
- Slice 1b（plan:345–347）逐条复述上述变更。

验证通过。方法签名完全确定，implementation worker 无需自行设计。私有前缀正确隔离了 adapter 内部 DTO 与 public contract。

---

## Recommended Items 确认

Fix artifact 声明将以下 recommended/informational 项纳入 plan，本 re-review 逐条确认均未引入新 blocker：

| 原 Finding | 纳入方式 | 位置 | 是否引入问题 |
|---|---|---|---|
| DS F4 — record-level share_class | `FundNavRecord` 新增 `share_class: str`，validator 校验 record/series 一致性 | plan:180,187,305 | 否，字段类型简单，validator 明确 |
| DS F5 — consumer 三条件 gate | Future Consumer Rule 改为 `identity_status==verified` AND `strong_drawdown_evidence_eligible` AND `adjusted_basis` ∈ accepted set | plan:455 | 否，三条件比原规则更严格 |
| MiMo F1 — identity → strong eligibility | validator: `identity_status != "verified"` 时不能 strong eligible | plan:191,302 | 否，这是 F5 的 model 层执行 |
| MiMo F2 — date 重复不 silent dedupe | records 重复 date → `integrity_error` | plan:188,245,304,367 | 否，与 normalization rules 一致 |
| DS F7 — completeness 默认值 | 未传约束 → `unchecked`；通过 → `complete_enough` | plan:193 | 否，fail-closed 路径不构造 series |
| DS F8 — 单一 NAV type/basis | Residual risks 明确多类型 source 未来需拆分或另开 gate | plan:499 | 否，仅为 documented tradeoff |
| DS F9 — raw_payload bypass 风险 | docstring + Future Consumer Rule 禁止 consumer 读取 | plan:180-181,457 | 否，约束在 consumer 侧 |
| Coverage targets | Slice 1a/1b 新增模块单文件 ≥80% 报告要求 | plan:322,386 | 否，符合 design.md §12 要求 |
| Real smoke CI isolation | Residual risks 明确不进入 CI | plan:501 | 否 |

---

## Self-Check

- [x] 原始 DS review 的 F1/F2/F3/F6 全部逐项对比 fix artifact 声明与 plan 实际内容
- [x] 所有 required fix 的验证证据均引用 plan 具体行号
- [x] Controller 额外要求的 F6 确认已完成
- [x] Recommended items 逐条确认未引入新 blocker
- [x] 未声称本 re-review 可替代 controller judgment
- [x] 未要求更改 FQ0-FQ6、score、snapshot、golden、bond extractor
- [x] 未要求解除 drawdown_stress blocker
- [x] 结论为 accepted
- [x] 未修改任何代码文件
