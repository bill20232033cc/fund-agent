# Drawdown Stress NAV-Derived Metric Implementation Plan

日期：2026-05-29

角色：planning worker only。本文只产出 code-generation-ready plan；不实现、不 review、不 commit、不 push、不建 PR、不改 golden / score policy / quality gate 语义。

Verdict：handoff-ready。

## Plan Fix Notes

2026-05-29 planning fix 根据 GLM / MiMo plan review 与 controller disposition 更新：

- 修复 MiMo accepted finding 01：明确 `strength="quantitative_derived"` 时 `measurement_kind` 必须为 `"derived_metric"`；`accepted + quantitative_derived + actual_metric/actual_exposure/其他 measurement_kind` 必须被 validator 拒绝。
- 折叠 MiMo 02：澄清 repository `minimum_records` 只是 full-series early sanity check，metric helper 必须独立检查 period-filtered records，并要求 full series >=30 但 period-filtered <30 的 fail-closed 测试。
- 折叠 MiMo 03 / GLM N3：明确 derived anchor projection 若遇到 snapshot 假设 `annual_report` source_kind 或拒绝 `derived:nav`，必须停回 controller；否则不改 production snapshot。
- 折叠 GLM N4 / controller 要求：新增回归测试要求，证明当 `drawdown_stress` 仍是唯一未满足组时 score 继续发出 `bond_risk_evidence_missing`。
- 收紧 Slice 4 / evidence 边界：任何 production `extraction_snapshot.py` / `extraction_score.py` 修改必须在 implementation evidence 中逐项说明原因；仍禁止 score threshold / policy / FQ 语义变化。

## Worker Self-Check

- Current gate / role：当前是 `drawdown_stress NAV-derived metric contract / implementation gate` 的 planning worker；只允许写本 plan artifact。
- Source of truth：已读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、指定 typed NAV / CSRC EID accepted artifacts、最新 006597 snapshot / score / quality gate，以及相关代码路径。
- Scope boundary：plan 允许后续实现触碰 Fund data / extractor / snapshot / tests/docs 的最小范围；本次未改 production code、tests、score policy、quality gate、golden fixture。
- Stop conditions：未发现需要 controller 先裁决的 material schema option；计划明确选择 contract extension，且不弱化 FQ0-FQ6。
- Evidence and validation：完成信号是本 artifact 存在且 plan 可直接交给 implementation worker。
- Next action：停止并交回 controller 派发 plan review / implementation。

## Truth Sources Restated

### AGENTS.md

- `AGENTS.md` 是本仓库所有 Agent 执行规则唯一权威入口；用中文回答。
- 当前目标架构固定为 `UI -> Service -> Host -> Agent`；当前确定性 CLI 主链路仍是 UI -> Service -> `fund_agent/fund` Agent 层基金能力过渡实现。
- 基金分析必须先识别基金类型，再应用 `preferred_lens`；债券基金第 6 章必须覆盖最大回撤 / 压力测试等风险证据。
- 生产年报 PDF 访问必须经 `FundDocumentRepository`；本 gate 的 NAV-derived work 不读取 PDF，也不得绕过 `FundNavRepository` 直接取 CSRC/Eastmoney/stock-sdk/cache。
- 禁止 `extra_payload`；所有 `fund_code`、`share_class`、`start_date`、`end_date`、`minimum_records`、`force_refresh` 等参数必须显式声明。
- 证据必须可溯源；所有数值判断必须标注来源。弱“控制回撤”文本不能被当成定量事实。

### docs/design.md

- `FundNavRepository.load_nav_series()` 是当前 Fund data 层 typed NAV repository contract；后续路径型 drawdown metric 只能消费该 typed 边界，不得直接读取 CSRC EID、Akshare、SQLite cache、snapshot JSONL 或旧 raw payload。
- `FundNavRepository()` 当前默认 CSRC EID 分类累计净值 source；已验证 006597=A、006598=C、014217=E、022176=F 分份额输出 `nav_type="accumulated_nav"`、`adjusted_basis="accumulated_nav"`、`dividend_adjustment_status="not_applicable"`、`identity_status="verified"`。
- `strong_drawdown_evidence_eligible=True` 只表示 source identity 与 accumulated basis 具备路径型指标的 source-level eligibility；当前未实现 drawdown metric，未解除债券基金 `drawdown_stress` blocker。
- legacy Akshare / 天天基金 raw unit path 仍只能输出 `raw_unit_nav`、`requested_code_only`、`strong_drawdown_evidence_eligible=False`，不能作为模板第 6 章强 drawdown evidence。
- FQ0-FQ6 是当前 quality gate 规则；本 gate 不应改变 FQ0-FQ6 语义。

### docs/implementation-control.md

- Current phase：release maintenance。
- Current gate：CSRC EID accumulated NAV adapter normalization 已 accepted local validation。
- Next entry point：`drawdown_stress NAV-derived metric contract / implementation gate`，classification 为 heavy。
- `FundNavRepository()` 默认 CSRC EID source；A/C/E/F source-level smoke accepted：
  - 006597/A：`accumulated_nav` / `accumulated_nav` / `verified` / 1807 records。
  - 006598/C：`accumulated_nav` / `accumulated_nav` / `verified` / 1807 records。
  - 014217/E：`accumulated_nav` / `accumulated_nav` / `verified` / 994 records。
  - 022176/F：`accumulated_nav` / `accumulated_nav` / `verified` / 398 records。
- `drawdown_stress` 仍是 weak qualitative；latest 006597 score 仍有 `bond_risk_evidence_missing.baseline_blocking=true`，`missing_evidence_groups=["drawdown_stress"]`。
- Next gate allowed scope explicitly要求：只消费 `FundNavRepository.load_nav_series()`；显式参数；拒绝 raw unit / requested_code_only；A/C/E/F 保持分离；保留 fail-closed taxonomy；不改 score/snapshot/quality gate/golden 以制造通过。

### Accepted NAV Typed Contract Artifacts

- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-controller-judgment-20260528.md` 接受 typed NAV models / repository boundary；raw-unit path 不解除 blocker，不实现 max drawdown / volatility / stress metric。
- DS / GLM aggregate deepreview 均确认：
  - `FundNavRepository.load_nav_series()` 签名显式，无 `extra_payload` / `**kwargs`。
  - raw_unit_nav 与 requested_code_only 双重保证 `strong_drawdown_evidence_eligible=False`。
  - fail-closed taxonomy 覆盖 `not_found`、`unavailable`、`schema_drift`、`identity_mismatch`、`integrity_error`、`adjustment_basis_unknown`、`missing_date_range`、`insufficient_records`。
  - 未修改 extractor / snapshot / score / quality / golden；drawdown blocker intentional residual。

### Accepted CSRC EID Normalization Artifacts

- `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-controller-judgment-20260529.md` 接受 `FundNavRepository()` 默认 CSRC EID accumulated NAV source，A/C/E/F 分份额输出 verified accumulated series。
- `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-evidence-20260529.md` 记录 real smoke：006597/A 2018-12-18 到 2026-05-28 共 1807 records，source `csrc_eid`，source_id `5755:2030-1010`，`strong_drawdown_evidence_eligible=true`。
- MiMo / GLM aggregate deepreview 均确认：source-level eligibility 不会自动解除 `drawdown_stress`；stock-sdk 仍 evidence-only；F direct-search gap 和 006597 family hardcoded scope 是 accepted residual；no fallback 到 Akshare / Eastmoney / stock-sdk / mixed product-level NAV。

### Latest 006597 Run Facts

- `reports/extraction-snapshots/bond-risk-crosscheck-suffix-006597-2024-20260528/snapshot.jsonl` 中 `bond_risk_evidence` 行：
  - `classified_fund_type="bond_fund"`。
  - `bond_risk_contract_status="partial"`。
  - satisfied groups：`duration_rate_risk`、`credit_risk`、`leverage_liquidity`、`asset_allocation_holdings_mix`、`redemption_share_pressure`、`convertible_bond_equity_exposure`。
  - weak groups：`drawdown_stress`。
  - missing / ambiguous groups 为空。
- `reports/scoring-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/score.json` 中唯一 bond risk issue 为 `bond_risk_evidence_missing`，`baseline_blocking=true`，`missing_evidence_groups=["drawdown_stress"]`。
- `reports/quality-gate-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/quality_gate.json` 当前 status 为 `warn`，仍包含 FQ2F `reason="bond_risk_evidence_missing"`；本 plan 不通过修改 FQ 规则消除它，只让 snapshot/score 在新 metric accepted 后自然不再派生该 issue。

## Goal

实现 NAV-derived quantitative `drawdown_stress` evidence：基于 accepted CSRC EID `accumulated_nav` typed series，计算 006597/A 在 2024 年报期间的最大回撤，并把结果作为 `bond_risk_evidence.v1` 的派生定量证据投影到 `drawdown_stress` 组。成功后，006597/2024 应自然达到七组 satisfied，score 不再产生 `missing_evidence_groups=["drawdown_stress"]`，quality gate 不再出现由该缺口导致的 FQ2F issue。

## Non-Goals

- 不修改 score policy、quality gate FQ0-FQ6、baseline/golden fixture 或 snapshot schema 以制造通过。
- 不使用 raw_unit_nav、stock-sdk date-shift NAV、Eastmoney raw payload、SQLite cache 或直接 CSRC fetch。
- 不混合 A/C/E/F 为 product-level NAV，不计算份额加权产品 NAV。
- 不做 QDII、FOF、110020、golden readiness、release、Host/Agent/dayu、PR/push/merge。
- 不输出买入/卖出建议，不预测未来收益。
- 不把 annual-report “控制回撤”文本提升为 quantitative evidence。
- 不新增 volatility 作为本 gate accepted metric；见 residual。

## Core Decisions

### 1. Minimum Accepted Metric

选择：max drawdown alone。

理由：

- `drawdown_stress` 的当前阻断源是缺少“最大回撤、波动率、压力测试阈值状态，或带来源锚点的回撤/压力计算”之一；最大回撤直接度量净值路径从峰值到谷值的最大损失，最贴合债券基金第 6 章“核心风险”中回撤压力问题。
- 006597 当前 annual-report “控制回撤”文本只是控制意图，不能证明实际回撤；CSRC EID accumulated NAV path 可以给出实际路径指标，补足同一组的定量事实。
- 波动率衡量收益离散度，不等同于最坏路径损失；作为后续增强指标有价值，但不是解除 `drawdown_stress` blocker 的最小必要条件。
- 只接受一个最小指标可以减少 contract/snapshot 扩面，降低 heavy gate 风险。

Residual / non-goal：volatility 不在本 gate 实现；后续如需要波动率，应单独定义日收益率、年化因子、交易日样本、节假日缺口和单位。

### 2. Main Share Class

生产 evidence 只使用请求基金代码对应的 main share class：006597/A。

- 对 006597/2024，调用 `FundNavRepository().load_nav_series("006597", share_class="A", start_date=date(2024,1,1), end_date=date(2024,12,31), minimum_records=30, force_refresh=<explicit>)`。
- 不计算 C/E/F worst / range 来替代 A 类 evidence；A/C/E/F 有不同代码、份额、成立日期和费用路径，混合会破坏 source identity。
- C/E/F 仅允许在独立 smoke / diagnostics 中验证 source path 仍可达，不能进入 `drawdown_stress` group 的 metric_value，不能影响 006597/A 的 accepted 状态。

### 3. Period

选择 2024 annual/report period：`2024-01-01` 到 `2024-12-31` inclusive。

理由：

- `bond_risk_evidence.v1` 当前由 2024 年报驱动，snapshot / score 也是 `fund_code + report_year` 粒度；同年 period 能与 annual-report 风险披露同源对齐。
- trailing window 会引入 report cutoff 之后的信息，对 2024 年报证据不公平，也可能让 006597/2024 因 2025/2026 数据变化而不稳定。
- CSRC EID source 返回交易日记录；非交易日缺失不补齐、不插值。metric helper 只消费 `record.date` 落入 inclusive period 的 records。

Implementation invariant：repository 的 `start_date/end_date` 用于显式覆盖检查；metric helper 仍必须二次过滤 `period_start <= record.date <= period_end`，因为 current repository 返回完整 series 而非窗口裁剪 series。repository `minimum_records` 是 full-series early sanity check，只证明 source 返回的整体 series 不是空壳；metric helper 的 `minimum_records` 是 period-filtered final check，必须独立执行，不能因为 repository 已传 `minimum_records=30` 就跳过。

### 4. Formula

Input：按日期升序的 `FundNavRecord.nav_value`，必须是 positive `Decimal`，`nav_type="accumulated_nav"`，`adjusted_basis="accumulated_nav"`，`identity_status="verified"`，`strong_drawdown_evidence_eligible is True`。

Algorithm：

1. 将 records 过滤到 `period_start <= date <= period_end`。
2. 按 `date` 升序排序。
3. 若过滤后记录数 `< minimum_records`，fail-closed `insufficient_records`；这里的 `minimum_records` 指 period-filtered records 数量，不是 repository 对 full series 做的 early sanity check。
4. 若存在重复 date，fail-closed `integrity_error`。不要 silent dedupe。
5. 若任一 NAV `<= 0`，fail-closed `integrity_error`。
6. 迭代维护 running peak：
   - 初始 peak 为第一条记录。
   - 对每条记录计算 `drawdown = nav_value / peak_value - 1`。
   - `drawdown` 为 `Decimal`，非正数；0 表示无回撤。
   - 当当前 `nav_value > peak_value` 时更新 peak date/value。
   - 记录最小 `drawdown` 及其对应的 peak date/value 与 trough date/value。
7. 输出：
   - `max_drawdown_ratio`：负数 ratio，例如 `-0.0123` 表示 -1.23%。
   - display metric value 建议保留 2 位百分比：`-1.23%`；内部 dataclass 保留 Decimal ratio。
   - peak/trough date/value：用于 provenance，不用于另行评分。

Tie handling：

- 若多个 trough 有相同最大回撤，保留最早 trough。
- 若同日创新高后又作为 trough 不可能发生，因为单日只有一条 NAV。
- 若全期单调不跌，`max_drawdown_ratio=Decimal("0")`，peak/trough 均可为第一条记录；仍是 accepted quantitative evidence。

### 5. Volatility

不实现。

如后续实现，必须单独 gate 定义日收益率 `nav_t/nav_{t-1}-1`、样本标准差或总体标准差、年化因子、minimum records、节假日处理、单位和 provenance。不得在本 gate 中顺手加入。

## Data Boundary

- 新 metric consumer 只能通过 `FundNavRepository.load_nav_series()` 读取 series。
- 禁止在 extractor 里直接调用 `CsrcEidNavSource`、httpx endpoint、stock-sdk、Eastmoney、Akshare、SQLite cache 或 `FundNavDataAdapter.load_nav_data()`。
- 显式参数必须包括 `fund_code`、`share_class`、`start_date`、`end_date`、`minimum_records`、`force_refresh`；禁止 `extra_payload` / `**kwargs` / 自由 dict。
- 不读取 `FundNavRecord.raw_payload` 来计算 NAV 或日期；只用 typed `date`、`nav_value`、`nav_type`、`adjusted_basis`、`share_class`。

## Contract / Projection Into bond_risk_evidence.v1

### Required Contract Extension

需要小型 contract extension：

- `BondRiskEvidenceStrength` 增加 `"quantitative_derived"`。
- `_BOND_RISK_EVIDENCE_STRENGTHS` 增加 `"quantitative_derived"`。
- `_BOND_RISK_ACCEPTED_STRENGTHS` 从 `("quantitative_direct", "qualitative_direct")` 扩展为包含 `"quantitative_derived"`。
- `BondRiskEvidenceMeasurementKind` 增加 `"derived_metric"`。
- `_BOND_RISK_EVIDENCE_MEASUREMENT_KINDS` 增加 `"derived_metric"`。
- `_validate_bond_risk_status_strength()` 允许 `status="accepted"` + `strength="quantitative_derived"` + `measurement_kind="derived_metric"`。
- `_validate_bond_risk_status_strength()` 必须额外强制：只要 `strength=="quantitative_derived"`，`measurement_kind` 必须等于 `"derived_metric"`；`status="accepted"` + `strength="quantitative_derived"` + `measurement_kind="actual_metric"`、`"actual_exposure"` 或其他 measurement kind 必须 fail validation。

为什么需要扩展：

- 当前 `quantitative_direct` 语义是年报直接披露或表格直接给出数值；NAV max drawdown 是由 external typed source series 计算出来的，不能谎称 direct。
- 当前 `actual_metric` 可表达指标事实，但无法区分“直接披露指标”和“派生计算指标”；加入 `derived_metric` 可降低 reviewer 误读。
- 这是质量强化，不是 quality-gate weakening：仍要求 accepted status、强证据锚点、七组完整性、typed source eligibility 和 fail-closed metric；score / quality gate 仍只消费结构化 satisfied groups，不改变阈值。

No schema version bump：仍保持 `bond_risk_evidence.v1`，因为 dataclass 字段形状不变，只扩展 Literal 枚举值。若 plan review 认为 Literal extension 是 public contract breaking，应由 controller 升级为 explicit schema decision；本 plan 认为在 internal extractor contract 内 additive enum extension 可在 heavy gate 下实现。

### Drawdown Group Record

成功时将 `drawdown_stress` group 替换/升级为：

- `status="accepted"`
- `strength="quantitative_derived"`
- `summary="CSRC EID A 类累计净值路径计算 2024 年报期间最大回撤"`
- `measurement_kind="derived_metric"`
- `metric_name="最大回撤"`
- `metric_value`：例如 `"-1.23%"`，应由 Decimal ratio 格式化得到。
- `metric_unit="ratio"`
- `period_label="2024-01-01 至 2024-12-31"`
- `source_anchor_ids=(derived_anchor_id,)`
- `na_reason=None`
- `reviewer_note`：可记录 weak annual-report companion，例如 `"annual-report drawdown control intent remains weak companion; quantitative source is CSRC EID accumulated NAV"`；不得把控制意图作为定量来源。

`BondRiskEvidenceValue.satisfied_group_ids` 必须自然包含 `drawdown_stress`；若其他六组仍 satisfied，则 `contract_status="satisfied"`。

## Anchor / Provenance Format

Existing `EvidenceAnchor.source_kind` already supports `"derived"`，but `BondRiskEvidenceAnchorRef` 当前要求 `section_id`、`row_locator` 和 stable id。Implementation should represent derived source in existing anchor shape without changing snapshot schema.

Recommended anchor convention：

- Stable ID：`bond-risk:<fund_code>:<report_year>:drawdown_stress:<ordinal>`，继续沿用 `_build_group_anchors()` ordinal shape。
- `EvidenceAnchor.source_kind="derived"`。
- `EvidenceAnchor.document_year=report_year`。
- `EvidenceAnchor.section_id="derived:nav"`。
- `EvidenceAnchor.page_number=None`。
- `EvidenceAnchor.table_id=None`。
- `EvidenceAnchor.row_locator="metric:max_drawdown:<share_class>:<period_start>:<period_end>"`。
- `EvidenceAnchor.note` 必须包含可审计 provenance，建议为分号分隔 stable key/value：
  - `source=CSRC EID`
  - `source_name=csrc_eid`
  - `source_id=5755:2030-1010`
  - `source_url=<series.source.source_url>`
  - `source_query_params=<stable serialized tuple>`
  - `retrieved_at=<series.source.retrieved_at.isoformat or None>`
  - `fund_code=006597`
  - `share_class=A`
  - `date_range=2024-01-01..2024-12-31`
  - `record_count=<period_record_count>`
  - `series_record_count=<series.record_count>`
  - `nav_type=accumulated_nav`
  - `adjusted_basis=accumulated_nav`
  - `dividend_adjustment_status=not_applicable`
  - `identity_status=verified`
  - `calculation_method=max_drawdown_on_accumulated_nav_path`
  - `peak_date=<YYYY-MM-DD>`
  - `peak_value=<Decimal string>`
  - `trough_date=<YYYY-MM-DD>`
  - `trough_value=<Decimal string>`
  - `max_drawdown_ratio=<Decimal string>`
- `BondRiskEvidenceAnchorRef.section_id="derived:nav"`。
- `BondRiskEvidenceAnchorRef.row_locator` 同上。
- `BondRiskEvidenceAnchorRef.evidence_role="derived_max_drawdown_metric"`。

This is compatible with snapshot/report evidence paths because snapshot only projects the first anchor/ref into `section_id/page/table/row_id` and tracks group satisfaction via structured fields. No snapshot schema change is required. Implementation must first prove this with tests; if snapshot projection assumes `source_kind="annual_report"` or rejects `section_id="derived:nav"`, stop for controller instead of changing schema or weakening projection semantics.

## Annual-Report Weak Text Coexistence

- `_extract_drawdown_stress()` 当前会把“控制回撤”识别为 weak `qualitative_control_intent`。
- 新 implementation must not promote this text.
- If NAV-derived metric succeeds, the weak text may be:
  - preserved as an extra annual-report companion anchor only if code can do so without confusing `source_anchor_ids`; or
  - summarized in `reviewer_note` / `EvidenceAnchor.note` as context.
- It must never determine `metric_value`、`strength`、`measurement_kind` or accepted status.
- Existing test `test_drawdown_control_text_alone_is_weak` must continue to pass when no NAV-derived metric is provided.

## Fail-Closed Behavior

Metric consumer should classify source/metric failures as follows:

| Scenario | Category / status outcome |
|---|---|
| `FundNavRepository.load_nav_series()` raises `not_found` | group remains weak if annual-report control text exists, else missing; `na_reason="drawdown_nav_not_found"` |
| source raises `unavailable` | group remains weak/missing; `na_reason="drawdown_nav_unavailable"` |
| source raises `schema_drift` | fail-closed; group must not be accepted; preserve category in reviewer_note / na_reason |
| source raises `identity_mismatch` | fail-closed; group must not be accepted |
| source raises `integrity_error` | fail-closed; group must not be accepted |
| source raises `adjustment_basis_unknown` | fail-closed; group must not be accepted |
| source raises `missing_date_range` | fail-closed; group must not be accepted |
| source raises `insufficient_records` | fail-closed; group must not be accepted |
| returned `nav_type!="accumulated_nav"` | reject; group weak/missing with `na_reason="drawdown_nav_type_ineligible"` |
| returned `adjusted_basis!="accumulated_nav"` | reject; group weak/missing with `na_reason="drawdown_adjusted_basis_ineligible"` |
| `strong_drawdown_evidence_eligible is not True` | reject; group weak/missing with `na_reason="drawdown_source_not_strong_eligible"` |
| `identity_status!="verified"` | reject; group weak/missing |
| period-filtered records `< 30` | reject; `na_reason="drawdown_period_insufficient_records"` |
| duplicate dates in period | reject; `na_reason="drawdown_period_duplicate_dates"` or propagated `integrity_error` |
| unsorted source records | sort before calculation; if duplicate/non-date discovered, fail-closed |
| NAV <= 0 | reject; `integrity_error` |
| metric calculation error | reject; `na_reason="drawdown_metric_calculation_error"` and do not satisfy group |

No failure should bubble up to make annual-report extraction fail unless it indicates an implementation bug in constructing `bond_risk_evidence.v1`. NAV source unavailability should degrade the group to weak/missing so existing score continues to block naturally.

## Implementation Design

### New Metric Module

Add `fund_agent/fund/data/nav_metrics.py`.

Types/functions:

- `NavMaxDrawdownMetric` dataclass:
  - `fund_code: str`
  - `share_class: str`
  - `period_start: date`
  - `period_end: date`
  - `record_count: int`
  - `max_drawdown_ratio: Decimal`
  - `peak_date: date`
  - `peak_value: Decimal`
  - `trough_date: date`
  - `trough_value: Decimal`
  - `calculation_method: Literal["max_drawdown_on_accumulated_nav_path"]`
  - `source: NavSourceMetadata`
  - `nav_type: NavType`
  - `adjusted_basis: AdjustmentBasis`
  - `dividend_adjustment_status: DividendAdjustmentStatus`
  - `identity_status: NavIdentityStatus`
- `calculate_max_drawdown_from_nav_series(series: FundNavSeries, *, period_start: date, period_end: date, minimum_records: int) -> NavMaxDrawdownMetric`
- `format_max_drawdown_percent(value: Decimal) -> str`

Rules:

- Reject ineligible series by raising `NavDataContractError` with existing taxonomy, preferably `adjustment_basis_unknown` for source basis issues and `integrity_error` / `insufficient_records` for metric input issues.
- Do not import extractor models into data module.

### DataExtractor Integration

Current `FundDataExtractor` has only `_NavDataProvider` for legacy `NavDataResult`. Add a separate protocol for typed drawdown NAV provider:

- `_NavSeriesRepository` Protocol with async `load_nav_series(fund_code: str, *, share_class: str | None, start_date: date | None, end_date: date | None, minimum_records: int | None, force_refresh: bool = False) -> FundNavSeries`。
- `FundDataExtractor.__init__(..., nav_series_repository: _NavSeriesRepository | None = None)` defaults to `FundNavRepository()`.
- Preserve `nav_provider` legacy behavior and tests.
- In `extract()`, after `classified_fund_type` is known and only for `bond_fund`, pass the typed repository to bond risk extraction. For non-bond funds, do not call typed NAV repository.

Recommended extractor call shape:

```python
bond_risk_evidence = await extract_bond_risk_evidence(
    report,
    classified_fund_type=classified_fund_type,
    nav_series_repository=self._nav_series_repository,
    force_refresh=force_refresh,
)
```

Because current `extract_bond_risk_evidence()` is sync, implementation may either:

- Make it async and update call sites/tests; or
- Keep it sync and add a new async wrapper in `FundDataExtractor`.

Preferred option: keep public extractor sync for annual-report-only tests, and add a small async helper in `data_extractor.py` that obtains optional `NavMaxDrawdownMetric` via repository, then calls an extended sync extractor with `drawdown_metric: NavMaxDrawdownMetric | None` and `drawdown_metric_error: NavDataContractError | None`.

This keeps `bond_risk_evidence.py` deterministic and free of repository/network calls, satisfying “bond extractor must not fetch CSRC EID directly.”

### Bond Extractor Extension

Change `extract_bond_risk_evidence()` signature add optional explicit params:

- `drawdown_metric: NavMaxDrawdownMetric | None = None`
- `drawdown_metric_error: NavDataContractError | None = None`

No repository parameter in `bond_risk_evidence.py`.

Modify `_extract_drawdown_stress(report, drawdown_metric, drawdown_metric_error)`:

- If `drawdown_metric` exists, return accepted `quantitative_derived / derived_metric` group with derived anchor.
- Else retain current annual-report direct table metric branch if present.
- Else retain current weak control intent branch.
- Else missing.

The existing direct annual-report max drawdown table branch can remain `quantitative_direct / actual_metric`.

### Anchor Builder

Add a private `_derived_nav_metric_anchor_draft()` or equivalent. Current `_AnchorDraft.section_id` is typed as `str`; allow value `"derived:nav"`. No schema change.

Ensure `_build_group_anchors()` sets `EvidenceAnchor.source_kind="derived"` for `section_id.startswith("derived:")`, otherwise `"annual_report"`. This is a behavior change in extractor anchor generation but not snapshot schema.

Do not create nested functions/classes.

## Tests

### Production File Scope

Allowed production files:

- `fund_agent/fund/data/nav_metrics.py` (new)
- `fund_agent/fund/data/__init__.py` (export metric types/functions if needed)
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/bond_risk_evidence.py`
- `fund_agent/fund/extraction_snapshot.py` only if needed for derived anchor projection tests; no schema field additions
- `fund_agent/fund/extraction_score.py` only if tests reveal issue wording needs no change; do not change satisfaction policy
- `fund_agent/fund/README.md`
- `tests/README.md`

Disallowed production files:

- `fund_agent/fund/quality_gate.py` / `quality_gate_integration.py`
- score threshold/policy logic except tests verifying natural issue disappearance
- golden fixtures / reports fixtures
- Service/UI/Host/Agent/dayu
- CSRC source adapter unless a blocking bug is discovered and controller approves scope expansion

### Test File Scope

Allowed test files:

- `tests/fund/data/test_nav_metrics.py` (new)
- `tests/fund/test_data_extractor.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py` only for natural FQ2F disappearance from score_applicability_issues; no FQ semantic change
- `tests/README.md`

### Required Tests

1. Max drawdown calculation:
   - NAV path `[1.00, 1.10, 1.05, 1.20, 1.08]` produces `-0.10` from peak 1.20 to trough 1.08.
   - Monotonic increasing path produces `0`.
   - Peak/trough dates/values are exact.
2. Bad series fail-closed:
   - period insufficient records raises `insufficient_records`.
   - full series has `>=30` records but period-filtered records have `<30` records must fail closed in the metric helper; this proves repository `minimum_records` and metric helper `minimum_records` are independent checks.
   - duplicate dates raises `integrity_error`.
   - non-positive NAV raises `integrity_error`.
   - ineligible `raw_unit_nav` / `strong_drawdown_evidence_eligible=False` rejects.
3. Raw-unit rejection:
   - constructor-injected raw `FundNavDataAdapter` / fake raw series never yields accepted drawdown group.
4. 006597/A accepted path:
   - fake typed repository returns A accumulated verified series for 2024 with enough records.
   - `FundDataExtractor.extract("006597", 2024)` calls typed repository with `share_class="A"`, `start_date=date(2024,1,1)`, `end_date=date(2024,12,31)`, `minimum_records=30`, explicit `force_refresh`.
   - resulting `bond_risk_evidence.value.satisfied_group_ids` contains `drawdown_stress`.
5. No A/C/E/F mixing:
   - fake repository records calls and asserts only one call for `006597/A`; no calls to 006598/014217/022176 in production extraction path.
6. Provenance completeness:
   - derived anchor note includes source, source_id, source_url/query params, retrieved_at, fund_code, share_class, date_range, record_count, nav_type, adjusted_basis, calculation_method, peak/trough and ratio.
   - `EvidenceAnchor.source_kind=="derived"` and `BondRiskEvidenceAnchorRef.section_id=="derived:nav"`.
7. Weak qualitative not promoted:
   - existing control text alone remains `status="weak"`, `strength="qualitative_control_intent"`, not satisfied.
   - when NAV metric is unavailable/error, weak annual-report text still remains weak and score still lists `drawdown_stress`.
8. Snapshot/score/quality true path:
   - build snapshot from bundle with derived drawdown evidence: `bond_risk_contract_status=="satisfied"` and no weak/missing/ambiguous groups.
   - `derive_score_applicability_issues()` returns no `bond_risk_evidence_missing` issue when all seven groups satisfied.
   - quality gate generated from such score has no FQ2F issue with `reason="bond_risk_evidence_missing"`.
   - regression failure path: when the other six groups are satisfied but `drawdown_stress` is the only weak/missing/ambiguous/absent group, `derive_score_applicability_issues()` must still emit `bond_risk_evidence_missing` with `missing_evidence_groups=("drawdown_stress",)`。
9. Contract extension tests:
   - `validate_bond_risk_evidence_value()` accepts `status="accepted"`, `strength="quantitative_derived"`, `measurement_kind="derived_metric"` for `drawdown_stress`.
   - `validate_bond_risk_evidence_value()` rejects `status="accepted"`, `strength="quantitative_derived"`, `measurement_kind="actual_metric"`; equivalent non-`derived_metric` measurement kinds must not pass as accepted derived metrics.
   - It still rejects weak/ambiguous/missing incompatible combinations.

## Validation Commands

Focused deterministic:

```bash
uv run ruff check fund_agent/fund/data/nav_metrics.py fund_agent/fund/data_extractor.py fund_agent/fund/extractors/models.py fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/data/test_nav_metrics.py tests/fund/test_data_extractor.py tests/fund/extractors/test_bond_risk_evidence.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
uv run pytest tests/fund/data/test_nav_metrics.py tests/fund/test_data_extractor.py tests/fund/extractors/test_bond_risk_evidence.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
```

Full:

```bash
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

Real CSRC EID NAV smoke:

```bash
uv run python -c 'import asyncio; from datetime import date; from fund_agent.fund.data import FundNavRepository; async def main():\n repo=FundNavRepository();\n for code,cls in ((\"006597\",\"A\"),(\"006598\",\"C\"),(\"014217\",\"E\"),(\"022176\",\"F\")):\n  s=await repo.load_nav_series(code, share_class=cls, start_date=date(2024,1,1), end_date=date(2024,12,31), minimum_records=30, force_refresh=True);\n  print(code, cls, s.nav_type, s.adjusted_basis, s.identity_status, s.strong_drawdown_evidence_eligible, s.record_count, s.date_range_start, s.date_range_end)\nasyncio.run(main())'
```

Real 006597 extraction / score / quality gate:

```bash
uv run fund-analysis extraction-snapshot --run-id bond-risk-drawdown-nav-006597-2024-20260529 --fund-code 006597 --report-year 2024 --force-refresh
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl --errors-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/errors.jsonl --output-dir reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529
uv run fund-analysis quality-gate --score-path reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json --output-dir reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529
```

Expected real-run assertions:

- snapshot `bond_risk_evidence` row has `bond_risk_contract_status="satisfied"`。
- `bond_risk_satisfied_groups` contains all seven groups including `drawdown_stress`。
- `bond_risk_weak_groups` no longer contains `drawdown_stress`。
- score `score_applicability_issues` has no `bond_risk_evidence_missing` for 006597.
- quality gate has no FQ2F issue with `reason="bond_risk_evidence_missing"` for 006597.
- Any remaining FQ2/FQ4/FQ0 warnings are not part of this gate unless caused by the new implementation.

## Docs Decision

- Update `fund_agent/fund/README.md` because Fund data / extractor behavior changes: document NAV-derived max drawdown as current Fund package capability, source boundary, period, fail-closed rules and weak text coexistence.
- Update `tests/README.md` because new tests cover `nav_metrics` and derived `bond_risk_evidence` path.
- Update `docs/design.md` only if implementation changes current design facts. If updated, state narrowly that `drawdown_stress` can be satisfied by reviewed NAV-derived max drawdown from CSRC EID accumulated typed series; do not claim volatility, score/quality weakening, golden readiness, or product-level NAV.
- Do not update root README unless CLI usage changes; this plan does not require CLI changes.

## Slices

### Slice 1: Metric Contract And Calculation

- Objective：add pure NAV max drawdown metric helper.
- Allowed files：
  - `fund_agent/fund/data/nav_metrics.py`
  - `fund_agent/fund/data/__init__.py`
  - `tests/fund/data/test_nav_metrics.py`
  - `tests/README.md`
- Changes：
  - Add `NavMaxDrawdownMetric` and calculation/format helpers.
  - Enforce accumulated_nav / accumulated_nav / verified / strong eligible.
  - Enforce period filter, sorted records, duplicates, positive NAV, min period records.
- Non-goals：no extractor integration, no bond_risk_evidence model change.
- Validation：focused ruff + `pytest tests/fund/data/test_nav_metrics.py -q`。
- Stop condition：any uncertainty about formula sign or period must return to controller before Slice 2.

### Slice 2: bond_risk_evidence Contract Extension And Derived Anchor Projection

- Objective：allow derived quantitative metric in `bond_risk_evidence.v1` and project `drawdown_stress`.
- Allowed files：
  - `fund_agent/fund/extractors/models.py`
  - `fund_agent/fund/extractors/bond_risk_evidence.py`
  - `tests/fund/extractors/test_bond_risk_evidence.py`
- Changes：
  - Add `quantitative_derived` and `derived_metric` Literal support.
  - Extend `_extract_drawdown_stress` to accept optional `NavMaxDrawdownMetric`.
  - Build derived anchor with `source_kind="derived"` and `section_id="derived:nav"`.
  - Preserve direct annual-report metric and weak control intent behavior.
- Non-goals：no repository call inside extractor.
- Validation：focused ruff + `pytest tests/fund/extractors/test_bond_risk_evidence.py -q`。
- Stop condition：if snapshot validator rejects derived anchor shape, stop for controller rather than weakening anchor validation.

### Slice 3: FundDataExtractor Wiring

- Objective：load typed NAV metric through repository boundary only for bond funds.
- Allowed files：
  - `fund_agent/fund/data_extractor.py`
  - `tests/fund/test_data_extractor.py`
- Changes：
  - Add `_NavSeriesRepository` Protocol and constructor injection.
  - For exact `bond_fund`, call repository with explicit A share class and annual period.
  - Calculate max drawdown via Slice 1 helper.
  - Pass metric or classified error into sync bond extractor.
  - Non-bond funds do not call typed repository.
- Non-goals：no changes to legacy `nav_provider` / `NavDataResult` behavior.
- Validation：focused ruff + `pytest tests/fund/test_data_extractor.py -q`。
- Stop condition：if async/sync integration forces broad extractor signature churn, return to controller.

### Slice 4: Snapshot / Score / Quality Natural Path Tests

- Objective：prove natural projection without policy weakening.
- Allowed files：
  - `tests/fund/test_extraction_snapshot.py`
  - `tests/fund/test_extraction_score.py`
  - `tests/fund/test_quality_gate.py`
  - `fund_agent/fund/extraction_snapshot.py` only if tests prove derived anchors cannot be projected without a narrow source_kind/section handling fix; no schema additions and no annual-report anchor regression.
  - `fund_agent/fund/extraction_score.py` only if tests prove already-satisfied groups are not recognized because of an implementation bug; no threshold, policy, issue severity, baseline_blocking, FQ, or satisfaction weakening changes.
- Changes：
  - Add tests for satisfied contract row with derived drawdown.
  - Add score test that all-seven satisfied groups produce no bond risk missing issue.
  - Add score regression test that drawdown-only unsatisfied groups still produce `bond_risk_evidence_missing`.
  - Add quality gate test that no FQ2F `bond_risk_evidence_missing` is emitted when score has no applicability issue.
- Non-goals：no threshold / FQ semantic changes.
- Validation：focused ruff + relevant pytest.
- Stop condition：any need to change `missing_evidence_groups` derivation semantics beyond already satisfied/unsatisfied logic must return to controller. If snapshot projection assumes annual-report source_kind or rejects `derived:nav`, stop for controller unless the needed production change is a narrow projection compatibility fix with tests and no schema change.

### Slice 5: Docs And Real Evidence

- Objective：sync docs and run accepted validation.
- Allowed files：
  - `docs/design.md`
  - `fund_agent/fund/README.md`
  - `tests/README.md`
  - implementation evidence artifact under `docs/reviews/`
- Changes：
  - Document current implemented max drawdown path and non-goals.
  - Run full validation and real 006597 snapshot/score/quality commands.
- Non-goals：no report/golden fixture promotion; generated reports remain local run outputs unless controller separately accepts evidence artifact.
- Validation：full ruff/full pytest/real smoke commands above.
- Stop condition：real CSRC EID unavailable should be reported as validation residual, not papered over by fixture/golden edits.

## Residual Risks

- CSRC EID endpoint has no SLA; source `unavailable` should keep blocker rather than accepting weak data.
- `source_query_params` currently mixes HTTP params and request context; plan only serializes existing metadata, not cleanup.
- CSRC source is currently scoped to verified 006597 family constants; metric works naturally for 006597/A but is not generalized to all funds.
- Accumulated NAV is accepted basis for path drawdown, not total-return index; this gate should not relabel it as dividend-adjusted or total-return.
- Volatility remains non-goal.

## Completion Report Format For Implementation Worker

Implementation evidence must report:

- Assigned slice id(s) and approved plan path.
- Changed files and confirmation no disallowed files changed.
- Contract decisions implemented exactly, especially `quantitative_derived` / `derived_metric`.
- Any production change to `fund_agent/fund/extraction_snapshot.py` or `fund_agent/fund/extraction_score.py` must be justified with the exact failing test/behavior it fixes; implementation evidence must explicitly confirm no score threshold, score policy, issue severity, `baseline_blocking`, FQ semantics, snapshot schema, quality gate, or golden fixture weakening occurred.
- Validation commands and exact outcomes.
- Real 006597 run outcome or unavailable residual.
- Residual risks classified as fixed / later slice / later work unit / controller decision.
- `Self-check: pass` or `Self-check: blocked - <reason>`.
