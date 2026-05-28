# NAV Repository / Source Adapter Adjusted-Basis Contract Plan — Independent GLM Review

日期：2026-05-28

角色：独立 Gateflow plan/review worker（不是 controller，不是 implementation worker）

Gate：`NAV repository/source adapter adjusted-basis contract gate`

审查对象：

- `docs/reviews/release-maintenance-nav-source-adapter-adjusted-basis-primer-20260528.md`（以下简称 Primer）
- `docs/reviews/release-maintenance-nav-source-adapter-adjusted-basis-contract-plan-20260528.md`（以下简称 Plan）
- `docs/reviews/release-maintenance-nav-source-adapter-adjusted-basis-contract-evidence-20260528.md`（以下简称 Evidence）

## 结论

**accepted**

三份 artifact 正确复述真源、无未实现设计冒充当前事实、primer 足以支撑后续证据能力判断、contract 不过宽、failure taxonomy 保持 fail-closed、next gate 方向正确。存在 4 项非阻断 findings，均不要求修改被审查 artifact。

---

## 1. 审查范围与方法

已读取并作为审查真源：

- `AGENTS.md`
- `docs/design.md`（v2.2）
- `docs/implementation-control.md`
- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-controller-judgment-20260528.md`（上一 NAV capability controller judgment）
- `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-controller-judgment-20260528.md`（上一 drawdown contract controller judgment）
- 最新 006597 snapshot / score / quality gate（`bond-risk-crosscheck-suffix-006597-2024-20260528/`）

独立核验：

- 通过 `FundDocumentRepository` 读取 006597 2025 年报 §3，独立核验 E 类期末基金份额净值
- 通过 `FundNavDataAdapter.load_nav_data("006597")` public smoke，独立核验 adapter 公开契约

未执行 ruff / pytest：本 review 只审查 artifact 文档，不修改任何文件。

---

## 2. Finding 列表

### F1（positive）真源复述准确，无未实现设计冒充当前事实

三份 artifact 的真源复述与以下权威来源一致：

- `AGENTS.md`：中文回答、FundDocumentRepository 边界、fallback failure taxonomy、四层架构、禁止 extra_payload
- `docs/design.md`：FundNavDataAdapter 在 P1 extraction 中加载 NAV、NavDataResult 当前字段、cache-hit 返回 source="nav_cache"
- `docs/implementation-control.md` Startup Packet：current gate、next entry point、residuals

未发现把已接受未来设计写成当前代码事实的情况。Plan 明确标注 "当前 adapter contract gap 已确认；不得进入 implementation"。

### F2（positive）§3.1 E 类期末基金份额净值 1.1967 经独立核验正确

独立执行 `FundDocumentRepository.load_annual_report("006597", 2025)` 并读取 §3 原文，确认：

- 2025 §3.1 E 类期末基金份额净值 = **1.1967**
- 2024 §3.1 E 类期末基金份额净值 = **1.1819**

handoff 中出现的 `1.1744` 在 2024 和 2025 年报 §3.1 的 E 类期末份额净值中均无匹配。`1.1744` 可能来自非年末日期的其他公告或来源，但不能作为本 gate 的 repository 年报事实。

**判定**：artifact 写 1.1967 是正确的本 gate 真源。1.1744 不能作为真源。

### F3（positive）FundNavDataAdapter public smoke 独立确认只返回 raw 三列

独立执行 `FundNavDataAdapter().load_nav_data("006597")`：

- keys = `["净值日期", "单位净值", "日增长率"]`
- 无 share_class、nav_type、adjustment_basis、dividend_adjustment_status、identity_status、failure_category、source_url、retrieved_at 等字段
- source = "nav_cache"，cached = true，record_count = 1809

**判定**：Evidence §4 和 Plan §2 关于"当前 adapter 只能证明 raw unit NAV rows reachable"的断言与独立核验完全一致。

### F4（observation）source_payload 应在 implementation gate 强化类型约束

Plan §5.3 `FundNavRecord.source_payload` 标注为 "只能承载 diagnostic source echo，不得作为业务显式参数通道"。该文字约束与 `AGENTS.md` 禁止 extra_payload 的硬约束方向一致。

但建议在后续 implementation gate 中考虑以下强化措施：

- `source_payload` 的值类型限制为 `Mapping[str, object]` 且只允许 diagnostic 标量（str / int / float / None），不允许嵌套 dict 或 callable
- 或考虑改为 `frozenset[tuple[str, str, ...]]` 更严格的 diagnostic echo 类型

**严重度**：非阻断。当前文字约束已足够支撑本 gate 的 plan 方向。implementation gate 再细化。

### F5（observation）NavFundCodeMapping.mapping_evidence 复用 EvidenceAnchor 需注意适用范围

Plan §5.5 `NavFundCodeMapping.mapping_evidence: tuple[EvidenceAnchor, ...]` 复用了 `fund_agent/fund/extractors/models.py` 的 `EvidenceAnchor`。当前 `EvidenceAnchor.source_kind` 为 `Literal["annual_report", "external_api", "derived"]`，对于 provider identity 映射证据（如 akshare 返回的基金名称与代码匹配）可能需要新增 source_kind 或将 mapping_source 字段本身作为证据来源。

**严重度**：非阻断。当前 Plan 已定义 `mapping_source: Literal["annual_report_section_2", "provider_identity", "explicit_request"]`，足以区分来源。implementation gate 再决定是否需要扩展 EvidenceAnchor.source_kind。

### F6（positive）contract 不过宽，raw_unit_nav 不会误通过 max drawdown strong evidence

Plan §6 Max Drawdown Eligibility Matrix 正确地将 raw_unit_nav 设为 "通常 weak / blocked"，仅在以下全部满足时允许 limited use：

1. 目标期间通过 §3.3 或事件源证明无分红、拆分、折算
2. share_class / identity / basis verified
3. contract 明确允许

006597 E 类存在 2023 分红（Primer §5 独立验证），意味着 E 类 raw unit NAV 跨分红期间会被 fail-closed 阻断。A/C/F 类虽然无分红，但当前 adapter 无 share_class 标记，无法自动区分，也会被 fail-closed。

**判定**：contract 设计正确保守，不会允许 raw_unit_nav 在有分红或 adjusted basis unknown 时误通过。

### F7（positive）failure taxonomy 保持 fail-closed，未削弱 FQ0-FQ6

Plan §7 failure taxonomy：

| failure_category | 处理 | 与真源一致 |
|---|---|---|
| not_found / unavailable | 可重试/fallback | 与 AGENTS.md 年报 fallback taxonomy 一致 |
| schema_drift / identity_mismatch / integrity_error | fail-closed | 与 AGENTS.md 硬约束一致 |
| adjustment_basis_unknown | fail-closed | 新增但方向正确：未知的调整基础不能用于风险证据 |
| insufficient_history | fail-closed for max drawdown | 合理：路径依赖指标需要足够历史 |

FQ0-FQ6 语义、quality gate 状态、score policy 和 golden fixture 均未改变。Plan §3 Non-Goals 明确声明"不削弱 FQ0-FQ6"。

**判定**：failure taxonomy 与现有 fail-closed 纪律一致，未引入任何削弱。

### F8（recommendation）next gate 应为 typed contract implementation gate，不需要额外 source research gate

三份 artifact 一致推荐下一步为 `NAV repository/source adapter typed contract implementation gate`。审查支持这一判断：

1. **typed model 可以立即实现**：Plan Slice 1-3（typed result/record/metadata、raw-basis 显式分类、share-class mapping）只涉及当前已有数据和代码结构，不依赖新的外部 provider。
2. **adjusted provider research 可并行但不阻塞**：Plan Slice 4 明确标注 "Implementation only if source can prove adjusted basis"。如果找不到 adjusted provider，gate 继续 blocked-with-contract-gap。
3. **不需要额外的 source research gate**：当前 gap 的核心不是"有没有 adjusted 数据"（行业实践中复权/累计净值是常见的），而是"当前 adapter 的 public contract 不暴露 basis / identity / provenance"。即使只对 raw data 做 typed contract，也能消除当前的 contract gap 中关于 metadata 和 identity 的部分。
4. **与上一 controller judgment 对齐**：NAV source capability controller judgment 要求 "typed public adapter contract, source name, origin source, retrieved time, source-returned identity or explicit identity status, date range, NAV type, adjustment basis, dividend adjustment status, record count, completeness status, and fail-closed data-quality classification"。这些在 Slice 1-3 中都可以实现。

**判定**：next gate 方向正确。建议 implementation gate 的最小接受标准为：当前 raw provider 必须被显式标记为 `nav_type=unit_nav`、`adjustment_basis=raw_unit_nav`、`identity_status=source_unverified`；即使找不到 adjusted provider，typed contract 本身就是有价值的 contract gap 收窄。

---

## 3. Primer 对证据能力的支撑评估

| 需要支撑的证据能力 | Primer 覆盖 | 评估 |
|---|---|---|
| 单位净值（raw_unit_nav） | §3.1 | 充分：明确定义了 raw_unit_nav 只能表示未声明分红调整的净值路径 |
| 累计净值（accumulated_nav） | §3.2 | 充分：正确区分了年报 §3.1 累计净值增长率（端点）与逐日累计净值 path |
| 复权/分红调整（dividend_adjusted_nav / total_return） | §3.3 | 充分：明确要求 provider 必须给出 adjustment basis、分红事件处理方式等 |
| 净值增长率 | §3.4 | 充分：正确指出 §3.2 区间增长率不能替代 path-dependent max drawdown |
| §3.1/§3.2/§3.3 证据能力矩阵 | §4 | 充分：表格清晰区分了"能证明"与"不能证明" |
| 006597 多份额类别 | §5 | 充分：A/C/E/F 分离、E 类分红事实、F 类新增时间均已通过 repository 验证 |

**判定**：Primer 足以支撑后续 contract 的证据能力判断。

---

## 4. 未覆盖的审查要点确认

- 是否有把未实现 future design 写成当前事实：**未发现**
- primer 是否足以支撑各种证据能力：**是**
- 006597 2025 §3.1 E 类 1.1967 vs handoff 1.1744：**1.1967 正确，1.1744 非本 gate 真源**
- FundNavDataAdapter 是否只返回 raw 三列：**是，独立 smoke 确认**
- contract 是否过宽：**否，raw_unit_nav 正确设为 weak/blocked**
- failure taxonomy 是否保持 fail-closed：**是**
- next gate 方向：**typed contract implementation gate 正确**

---

## 5. 总结

| Finding | 严重度 | 处置 |
|---|---|---|
| F1 真源复述准确 | positive | 无需修改 |
| F2 §3.1 E 类 1.1967 独立核验正确 | positive | 无需修改 |
| F3 adapter public smoke 独立确认 | positive | 无需修改 |
| F4 source_payload implementation 细化 | observation（非阻断） | 交 implementation gate |
| F5 EvidenceAnchor source_kind 适用性 | observation（非阻断） | 交 implementation gate |
| F6 contract 不允许 raw 误通过 | positive | 无需修改 |
| F7 failure taxonomy 保持 fail-closed | positive | 无需修改 |
| F8 next gate 方向正确 | recommendation | 建议接受 |

**总体结论：accepted**

三份 artifact 可以作为 `NAV repository/source adapter adjusted-basis contract gate` 的有效 worker 产出，交 controller judgment。
