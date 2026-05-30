# NAV Repository / Source Adapter Adjusted-Basis Contract Plan — Review (DS)

日期：2026-05-28

角色：独立 Gateflow plan/review worker（非 controller，非 implementation worker）

Gate：`NAV repository/source adapter adjusted-basis contract gate`

Review 对象：
- `docs/reviews/release-maintenance-nav-source-adapter-adjusted-basis-primer-20260528.md`
- `docs/reviews/release-maintenance-nav-source-adapter-adjusted-basis-contract-plan-20260528.md`
- `docs/reviews/release-maintenance-nav-source-adapter-adjusted-basis-contract-evidence-20260528.md`

## 结论

**accepted**

三个 artifact 整体保守、fail-closed，正确复述真源，contract 不过宽，不削弱 FQ0-FQ6，不改生产代码。以下 findings 均为 informational / minor，不要求 artifact 返工即可进入下一 gate。

---

## 独立核验方法

本 review 执行了以下独立核验（不依赖被 review artifact 的声明）：

1. `FundDocumentRepository.load_annual_report("006597", 2025)` → 读取 §3.1 全文，定位 E 类期末基金份额净值
2. `FundNavDataAdapter().load_nav_data("006597")` → public smoke，检查 result 字段和 records keys
3. 读取 `fund_agent/fund/data/nav_data.py` → 确认 `_fetch_nav_with_akshare()` 只调用 `indicator="单位净值走势"`，`_load_cached_sync()` 只返回 `payload_json`
4. 读取最新 006597 snapshot / score / quality_gate JSON

---

## Finding 1 (informational): 006597 2025 §3.1 E 类 NAV 核验结果

**独立核验证实：artifact 写的 `1.1967` 是正确的。**

通过 `FundDocumentRepository` 读取 2025 年报 §3.1，E 类表格行明确显示：

```text
期末基金份额净值  1.1967  1.1819  1.1566
（2025年末 / 2024年末 / 2023年末）
```

全文搜索 `1.1744` 未命中。`1.1744` 可能来自：
- 其他报告期（2025 中报、季报）
- 非年末日期（如 2025 中报期末净值）
- 其他来源或旧版本缓存

**裁决：`1.1967` 是本 gate repository 年报事实。handoff 中的 `1.1744` 不是 2025 §3.1 年末值，不得作为本 gate 真源。**

Primer artifact §5 对此差异的处理正确：声明不一致并请求 controller 复核。但 primer 将 `1.1744` 归于"用户给定的"，建议在 controller 复核时明确该值的实际来源（handoff 链路中的哪个 artifact）。

---

## Finding 2 (confirmed): FundNavDataAdapter 只返回 raw 单位净值三列

**独立 public smoke 证实 artifact 描述完全准确。**

```json
{
  "fund_code": "006597",
  "source": "nav_cache",
  "cached": true,
  "record_count": 1809,
  "first": {"净值日期": "2018-12-03", "单位净值": 1.0, "日增长率": 0.0},
  "last": {"净值日期": "2026-05-27", "单位净值": 1.2275, "日增长率": 0.01},
  "keys": ["净值日期", "单位净值", "日增长率"]
}
```

`NavDataResult` 公开字段只有 6 个：`fund_code`、`records`、`source`、`cached`、`unavailable`、`unavailable_reason`。

代码确认：
- `_fetch_nav_with_akshare()` (nav_data.py:72) 固定调用 `indicator="单位净值走势"`，不可配置为累计净值或复权净值
- `_load_cached_sync()` (nav_data.py:300) 只 SELECT `payload_json`，丢弃 `source` 和 `updated_at` 列
- cache hit 返回 `source="nav_cache"` 无 origin source / cache updated_at

**目前没有任何 share_class、adjustment_basis、provenance、identity、failure taxonomy。artifact 的 contract gap 判断成立。**

---

## Finding 3 (confirmed): artifact 正确复述真源，未将未来设计写成当前事实

逐项核验：

| 真源声明 | 真源 | 复述正确？ |
|---|---|---|
| 四层架构 `UI -> Service -> Host -> Agent` | `design.md` §2.1 | 是 |
| 当前主链路是过渡实现 UI → Service → fund_agent/fund | `design.md` §2.2 | 是 |
| Host/Agent 未接入，dayu.host/dayu.engine 未声明 | `design.md` §9.1 | 是 |
| 年报访问只通过 `FundDocumentRepository` | `AGENTS.md` 硬约束 | 是 |
| Fallback 只在 not_found/unavailable 允许 | `AGENTS.md` + `design.md` §6.1 | 是 |
| drawdown_stress 保持 weak qualitative | controller judgment | 是 |
| NAV-derived drawdown 只是 future candidate | controller judgment | 是 |
| bond_risk_evidence_missing.baseline_blocking=true | score.json | 是 |
| missing_evidence_groups 只剩 drawdown_stress | score.json | 是 |

**未发现将未实现内容写成当前事实的案例。** 三个 artifact 在描述当前状态 vs 未来设计时边界清晰。Contract plan 明确标注为 `handoff-ready for next implementation gate`，未声称已实现。

---

## Finding 4 (informational): Primer 覆盖率评估

Primer 覆盖：

- §3.1 单位净值：概念、contract 含义、可用于/不可用于 drawdown 的边界 ✅
- §3.2 累计净值：概念、端点 vs path 区别、年报披露口径 ✅
- §3.3 复权/分红调整净值：累计净值 vs 复权净值区分、total-return 要求 ✅
- §3.4 净值增长率：§3.2 区间披露的可用性和局限性 ✅
- §4 证据能力矩阵：§3.1/§3.2/§3.3 各自的能证明/不能证明 ✅
- §5 多份额类别：A/C/E/F mapping、E 类分红影响、F 类起算日限制 ✅
- §6 drawdown 证据要求：adjustment basis 优先级链条、fail-closed 条件 ✅

**Primer 足以支撑后续 contract 设计。** 监管来源部分正确标注了缺口（未找到编报规则第2号原文），未过度宣称。

---

## Finding 5 (confirmed): Contract 不过宽，raw_unit_nav 不会在有分红时误通过

Contract plan §6 Max Drawdown Eligibility Matrix 的 fail-closed 设计：

| adjustment_basis | strong evidence? | 006597 E 类 2023 分红场景 |
|---|---|---|
| `total_return` | 是 | 当前 provider 不可用 → 不触发 |
| `dividend_adjusted_nav` | 是 | 当前 provider 不可用 → 不触发 |
| `accumulated_nav` | 有条件 | 需说明 provider 口径，不能默认为 total-return |
| `raw_unit_nav` | 通常 weak/blocked | E 类 §3.3 有分红证据 → fail-closed |
| `unknown` | 否 | fail-closed |

**raw_unit_nav 的 limited use 条件（目标期间无分红且 share-class/identity/basis verified）对 006597 E 类不成立**，因为 §3.3 已证明 2023 分红。A/C 类无分红但当前 adapter 无法提供 identity/basis verified → 也不满足 limited use 前提。不存在 raw_unit_nav 在有分红或 basis unknown 时误通过 strong evidence 的路径。

---

## Finding 6 (confirmed): Failure taxonomy 保持 fail-closed，未削弱 FQ0-FQ6

Contract plan §7 failure taxonomy：

| 类别 | 处理 | 与年报 taxonomy 对齐？ |
|---|---|---|
| `not_found` | retry/fallback | 是 |
| `unavailable` | retry/fallback | 是 |
| `schema_drift` | fail-closed | 是 |
| `identity_mismatch` | fail-closed | 是 |
| `integrity_error` | fail-closed | 是 |
| `adjustment_basis_unknown` | fail-closed | 新增，NAV 特有 |
| `insufficient_history` | fail-closed for max drawdown | 新增，NAV 特有 |

新增类别 `adjustment_basis_unknown` 和 `insufficient_history` 均为 fail-closed。无 weaken 现有类别。Quality gate JSON 证实 FQ0-FQ6 语义未被本 gate 改变：evidence artifact §2 正确复述了 `FQ0=info, FQ2=warn, FQ2F=warn, FQ4=warn`。

---

## Finding 7 (confirmed): Next gate 应为 typed contract implementation gate

Contract plan §8 定义了 5 个 implementation slice，其中 Slice 4 将 provider extension research 纳入 implementation gate 范围。Evidence artifact §8 建议下一 gate 为 `NAV repository/source adapter typed contract implementation gate`。

**同意此建议。** 理由：
- Contract 已充分定义（typed models、enum、eligibility matrix、failure taxonomy、share-class mapping）
- Provider research 不需要独立 gate——如果找不到 adjusted provider，implementation gate 应继续 blocked，无需预先开 research-only gate
- Current adapter gap 已完整表征，implementation gate 的 Slice 1-3（typed models + explicit raw-basis classification + share-class mapping）不依赖外部 provider 发现，可以先落地 fail-closed typed contract
- Slice 4-5 可并行或顺序执行

---

## Finding 8 (minor, for next implementation gate): `NavType` 与 `AdjustmentBasis` 语义重叠

Contract plan §5.1 定义了两个 enum：

```python
NavType = Literal["unit_nav", "accumulated_nav", "adjusted_nav", "total_return_index"]
AdjustmentBasis = Literal["raw_unit_nav", "accumulated_nav", "dividend_adjusted_nav", "total_return", "unknown"]
```

两套字面量有显著重叠（`unit_nav`/`raw_unit_nav`、`accumulated_nav`/`accumulated_nav`、`adjusted_nav`/`dividend_adjusted_nav`、`total_return_index`/`total_return`），且 `FundNavRecord` 同时持有 `nav_type: NavType` 和 `adjustment_basis: AdjustmentBasis`。

建议在 implementation gate 中明确两者关系，或合并为单一 enum。`FundNavSeriesMetadata` 另有独立的 `nav_type` 和 `adjustment_basis` 字段——这使 record 内的 nav_type 和 metadata 的 nav_type 产生冗余。

这不影响本 gate acceptance，但 implementation gate 应解决。

---

## Finding 9 (minor, for next implementation gate): `FundNavCodeMapping` 依赖外部 `EvidenceAnchor`

Contract plan §5.5 的 `mapping_evidence: tuple[EvidenceAnchor, ...]` 引用了当前 extractors 层的 `EvidenceAnchor` dataclass。如果 NAV contract 模型放在 `fund_agent/fund/data/`，需注意对 `fund_agent/fund/extractors/models.py` 的依赖方向。Implementation gate 可选择：复用现有 `EvidenceAnchor`、定义 NAV 专用 anchor 类型、或将 `EvidenceAnchor` 提升到共享层。

---

## 验证摘要

| 验证项 | 方法 | 结果 |
|---|---|---|
| 006597 2025 §3.1 E NAV | `FundDocumentRepository` 独立读取 | `1.1967` 确认 |
| `1.1744` 是否存在 | 全文搜索 §3.1 提取文本 | 未命中 |
| `FundNavDataAdapter` public contract | public smoke + 代码审阅 | 仅 raw 三列 |
| Cache metadata 暴露 | 代码审阅 `_load_cached_sync()` | 丢弃 source/updated_at |
| Akshare indicator | 代码审阅 `_fetch_nav_with_akshare()` | 固定 `单位净值走势` |
| 006597 artifact 状态 | 读取 score.json / quality_gate.json | blocker 仅 drawdown_stress |
| FQ0-FQ6 语义 | quality_gate.json | 无变更 |

工具链：`ruff` / `pytest` 未运行——本 gate 零生产代码变更，与 prior controller judgment 口径一致。

---

## Residuals

- `006597 / 2024` drawdown_stress 继续保持 weak qualitative，baseline blocker 有效。
- `NavType` / `AdjustmentBasis` 语义重叠留待 implementation gate 解决。
- `FundNavCodeMapping` 对 `EvidenceAnchor` 的依赖方向留待 implementation gate 决定。
- Golden corpus v1 仍 blocked。不做 promotion。
