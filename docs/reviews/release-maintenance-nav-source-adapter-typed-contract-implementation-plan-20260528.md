# NAV Repository / Source Adapter Typed Contract Implementation Plan

日期：2026-05-28

Work unit：`NAV repository/source adapter typed contract implementation gate`

角色：planning agent

Gate classification：`heavy`

目标状态：`handoff-ready / code-generation-ready`

## Worker Self-Check

- Current gate / role：当前是 typed NAV repository/source adapter contract 的 `plan` gate；我是 planning agent，不是 controller。
- Role boundary：本 artifact 只规划后续 worker implementation；不启动 `$gateflow` / `/gateflow`，不 implementation、commit、push、PR、merge。
- Branch / status preflight：`codex/local-reconciliation`；`git status --short --branch` 只有已知无关 untracked：`--help`、旧 repo-review / comprehensive audit artifacts、`docs/tmux-agent-memory-store.md`，无 tracked dirty。
- Scope boundary：允许规划 `fund_agent/fund/data/` typed NAV contract、兼容旧 `NavDataResult`、对应测试和最小 docs；不得触碰 bond extractor、snapshot schema、score policy、quality gate、golden fixture、Host/Agent/dayu、release/PR 外部状态。
- Stop conditions：当前没有需要 controller 先回答的 blocking question；实现中若发现必须改变 `bond_risk_evidence`、FQ0-FQ6、snapshot/score schema 或旧 `load_nav_data()` 行为，应停止并回报 controller。

## Source Replay

已读取并用于本计划的真源：

- `AGENTS.md`：规则真源。回答必须中文；当前目标架构是 `UI -> Service -> Host -> Agent`；`fund_agent/fund` 属于 Agent 层基金领域能力包；显式参数不得塞入 `extra_payload`；年报 PDF 必须通过 `FundDocumentRepository`；分类不确定时选择更重 gate；函数/类/模块需要中文 docstring；代码修改需同步测试和必要 README/docs。
- `docs/design.md`：设计真源。当前确定性链路是 UI -> Service -> `fund_agent/fund` 过渡实现；`FundDataExtractor` 编排 `FundDocumentRepository`、`FundNavDataAdapter` 和章节 extractor；`NavDataResult` 当前只承担 legacy 净值读取结果，NAV provider/cache/akshare 失败由 `FundDataExtractor` 在单次 `load_nav_data()` 调用边界降级为 unavailable；`nav_data` 当前不投影为 report facts。
- `docs/implementation-control.md`：当前 phase 是 release maintenance；当前 accepted checkpoint 是 NAV adjusted-basis contract `accepted blocked-with-contract-gap`；下一入口是本 typed contract implementation gate，分类为 `heavy`；最新 006597 仍只有 `drawdown_stress` weak，blocker 不得解除。
- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-controller-judgment-20260528.md`：当前 public `FundNavDataAdapter.load_nav_data("006597")` smoke 可达，但只证明 raw `净值日期` / `单位净值` / `日增长率` rows；直接 SQLite 只能作为 diagnostic，不能作为生产访问路径；当前 capability 不能证明 adjusted / cumulative / total-return / dividend-aware basis。
- `docs/reviews/release-maintenance-nav-source-adapter-adjusted-basis-contract-controller-judgment-20260528.md`：已接受 NAV primer/contract，但 runtime 仍 blocked-with-contract-gap；未来实现必须在 Agent/Fund data boundary 暴露 typed NAV series、share class、adjusted basis、dividend adjustment status、identity/provenance/failure taxonomy；A/C/E/F 份额不得混合；raw_unit_nav 默认不 eligible for strong drawdown evidence。
- 最新 006597 artifacts：
  - `reports/extraction-snapshots/bond-risk-crosscheck-suffix-006597-2024-20260528/snapshot.jsonl`：`bond_risk_evidence` 的 satisfied groups 为 `duration_rate_risk`、`credit_risk`、`leverage_liquidity`、`asset_allocation_holdings_mix`、`redemption_share_pressure`、`convertible_bond_equity_exposure`；weak groups 只有 `drawdown_stress`；`nav_data` 当前 note 为 `source=nav_cache; cached=True; records=1802` 且无 anchor。
  - `reports/scoring-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/score.json`：`bond_risk_evidence` 字段 pass；`nav_data` 是 P2 且 traceability fail；单基金仍有 P1 缺失字段，但 `drawdown_stress` blocker 是本 gate 相关 residual。
  - `reports/quality-gate-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/quality_gate.json`：status `warn`；FQ2F 仍提示 `bond_risk_evidence_missing`，原因是当前七组债券风险证据仍未形成已复核完整强证据；不得通过本 gate 改 FQ0-FQ6。

## Current Code Facts

- [fund_agent/fund/data/nav_data.py](/Users/maomao/fund-agent/fund_agent/fund/data/nav_data.py:55)：默认 fetcher 调用 `ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")`，返回 raw JSON-compatible records。
- [fund_agent/fund/data/nav_data.py](/Users/maomao/fund-agent/fund_agent/fund/data/nav_data.py:99)：`NavDataResult` 仅包含 `fund_code`、`records`、`source`、`cached`、`unavailable`、`unavailable_reason`。
- [fund_agent/fund/data/nav_data.py](/Users/maomao/fund-agent/fund_agent/fund/data/nav_data.py:227)：旧 `load_nav_data()` 是多个调用点的兼容入口；cache hit 返回 `source="nav_cache"`，不公开原始 source / updated_at。
- [fund_agent/fund/data_extractor.py](/Users/maomao/fund-agent/fund_agent/fund/data_extractor.py:63)：`_NavDataProvider` Protocol 只要求 `load_nav_data()`；`FundDataExtractor` 依赖旧 `NavDataResult`。
- [fund_agent/fund/data_extractor.py](/Users/maomao/fund-agent/fund_agent/fund/data_extractor.py:247)：`_load_nav_data_or_unavailable()` 只 catch NAV provider 单次调用异常并降级，不 catch 年报仓库/PDF/source fallback。
- [fund_agent/fund/extraction_snapshot.py](/Users/maomao/fund-agent/fund_agent/fund/extraction_snapshot.py:989)：snapshot 对 `nav_data` 只读旧 `NavDataResult.source/cached/records/unavailable`，当前 schema 不承载 typed NAV provenance。
- [fund_agent/fund/data/__init__.py](/Users/maomao/fund-agent/fund_agent/fund/data/__init__.py:9)：data 包公共入口当前只 re-export `FundNavDataAdapter` 和 `NavDataResult`。
- [tests/fund/data/test_nav_data.py](/Users/maomao/fund-agent/tests/fund/data/test_nav_data.py:12)：现有 tests 锁定旧 adapter cache 复用、force refresh、unavailable helper。
- `rg NavDataResult/FundNavDataAdapter/load_nav_data/nav_data` 显示多个测试、`FundDataExtractor`、snapshot、renderer/report evidence 相关路径消费旧 `NavDataResult`；不能粗暴替换旧 `load_nav_data()`。

## Goal

实现 Fund/Agent data 层的 typed NAV repository/source adapter contract，让后续 drawdown extractor / metric 只能消费已接受 typed contract，而不是直接依赖 Akshare-specific adapter、cache SQLite 或网页/helper。

本 gate 只建立 typed contract 和 raw-unit-only normalization：

- 当前 Akshare `单位净值走势` 必须明确标记为 `adjusted_basis="raw_unit_nav"`。
- 当前 raw unit NAV 必须明确 `strong_drawdown_evidence_eligible=False`，不能伪装成 adjusted / total-return / cumulative strong evidence。
- `drawdown_stress` blocker 保留；不得改变 bond risk satisfaction、score acceptance、snapshot schema、quality gate semantics 或 golden fixtures。

## Non-Goals

- 不解除 `drawdown_stress` blocker。
- 不把 raw unit NAV、`控制回撤` 文本或 annual-report interval performance 升级为 quantitative strong evidence。
- 不改 `bond_risk_evidence` extractor、snapshot schema、score policy、quality gate、FQ0-FQ6、golden/baseline fixtures。
- 不做 QDII / FOF / 110020 / golden readiness / release readiness。
- 不创建 Host/Agent package，不引入 `dayu.host` / `dayu.engine`。
- 不在 extractor 内抓网页、读 NAV cache SQLite、调用 source-specific helper；所有未来 drawdown 只能走 typed NAV repository。
- 不 push、PR、merge 或做 GitHub mutation。

## Contract Design Decisions

### Module Ownership

Typed NAV contract 属于 Agent 层 `fund_agent/fund` 数据能力，不属于 Service、UI、Host 或 renderer。

实现位置：

- 新增 `fund_agent/fund/data/nav_models.py`：纯 typed model、Literal domain、contract error。
- 新增 `fund_agent/fund/data/nav_repository.py`：统一 typed NAV repository wrapper，负责调用 source adapter、做 normalization / validation / fail-closed classification。
- 扩展 `fund_agent/fund/data/nav_data.py`：保持旧 `FundNavDataAdapter.load_nav_data()` 行为；新增 cache metadata 内部读取能力和/或 typed source snapshot 方法供 repository 使用。
- 更新 `fund_agent/fund/data/__init__.py`：re-export 新 typed public contract。

不要把 typed model 放入 `fund_agent/fund/extractors/`、`fund_agent/fund/analysis/`、Service 或 CLI；否则未来 drawdown metric 会形成错误依赖方向。

### Public Typed Interface

新增 repository 方法建议为：

```python
class FundNavRepository:
    async def load_nav_series(
        self,
        fund_code: str,
        *,
        share_class: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        minimum_records: int | None = None,
        force_refresh: bool = False,
    ) -> FundNavSeries:
        ...
```

约束：

- 所有业务输入必须是显式参数；签名不得出现 `extra_payload`、`**kwargs` 或自由 dict 参数。
- `share_class=None` 表示 repository 执行显式默认份额映射；不得混合 A/C/E/F。
- 006597 当前可默认到 A 类，但必须在 `ShareClassMapping` 中标记 `mapping_status="requested_code_default_a"` 或同等显式状态；不得声称 C/E/F 已加载。
- `start_date` / `end_date` 用于路径指标所需覆盖范围检查；缺失范围不代表 strong evidence，未来 drawdown metric 必须显式传入。
- `minimum_records` 用于 fail-closed 的 path metric record count 检查；不得由未来 extractor 在本地自行判断后绕过 repository。

### Typed Models

`nav_models.py` 必须使用 frozen/slotted dataclass 或同等不可变模型，所有类/函数提供中文 docstring。建议值域：

```python
NavType = Literal[
    "unit_nav",
    "accumulated_nav",
    "adjusted_nav",
    "total_return_index",
]

AdjustmentBasis = Literal[
    "raw_unit_nav",
    "accumulated_nav",
    "dividend_adjusted_nav",
    "total_return",
    "unknown",
]

DividendAdjustmentStatus = Literal[
    "not_adjusted",
    "adjusted",
    "unknown",
    "not_applicable",
]

NavIdentityStatus = Literal[
    "verified",
    "requested_code_only",
    "identity_mismatch",
    "unknown",
]

NavCompletenessStatus = Literal[
    "complete_enough",
    "missing_date_range",
    "insufficient_records",
    "unchecked",
]

NavFailureCategory = Literal[
    "not_found",
    "unavailable",
    "schema_drift",
    "identity_mismatch",
    "integrity_error",
    "adjustment_basis_unknown",
    "missing_date_range",
    "insufficient_records",
]
```

`NavFailureCategory` 与 documents 层年报来源失败类型（如 `AnnualReportSourceFailure`）保持类别名称语义对齐，但类型独立；不得为复用名称而让 NAV data 层依赖 documents source failure 类型。

`NavType` 与 `AdjustmentBasis` 决策：本 gate 选择保留两者。`NavType` 描述 source-claimed / math shape，即 source 声称返回的是单位净值、累计净值、调整净值还是总回报指数；`AdjustmentBasis` 描述本系统对该 series 调整基础的判定，即是否可视为未调整、累计、分红调整、总回报或未知。两者不是同义字段，必须通过兼容矩阵校验，非法组合归类为 `schema_drift` fail-closed：

| NavType | Allowed AdjustmentBasis | 说明 |
|---|---|---|
| `unit_nav` | `raw_unit_nav` | 当前 Akshare `单位净值走势` 路径，仅代表未调整单位净值 |
| `accumulated_nav` | `accumulated_nav` | source 明确返回累计净值且语义已验证 |
| `adjusted_nav` | `dividend_adjusted_nav` | source 明确返回分红调整后净值且语义已验证 |
| `total_return_index` | `total_return` | source 明确返回总回报指数或等价 total-return series |

`unknown` 只能作为 source/normalization 中间状态；成功 `FundNavSeries` 不允许 `adjusted_basis="unknown"`。

Required dataclasses：

- `NavContractError` / `NavDataContractError(Exception)`：字段至少包含 `category: NavFailureCategory`、`message: str`、`source: str | None`、`fund_code: str | None`、`cause: Exception | None`。Fail-closed paths raise this error; do not return half-valid series.
- `NavSourceMetadata`：`source_name`、`origin_source`、`source_id`、`source_url`、`cached`、`retrieved_at`、`cache_updated_at`、`requested_fund_code`、`returned_fund_code`、`returned_fund_name`、`failure_category: NavFailureCategory | None`。成功 series 中 `failure_category` 必须为 `None`；非空仅用于 future fallback/diagnostic 场景表达曾发生但未成为最终 fail-closed 的 source failure。
- `ShareClassMapping`：`requested_fund_code`、`requested_share_class`、`resolved_fund_code`、`resolved_share_class`、`mapping_status`、`identity_status`、`mapping_evidence`。`mapping_evidence` 必须是显式字符串或 tuple，不要依赖年报 extractor 类型，避免 data layer 反向依赖 extractor。
- `FundNavRecord`：`date: date`、`share_class: str`、`nav_value: Decimal`、`nav_type: NavType`、`adjusted_basis: AdjustmentBasis`、`raw_change_rate: Decimal | None`、`raw_payload: Mapping[str, object]`。`raw_payload` 仅供 diagnostics/debugging；production consumer，尤其 future drawdown metric，不得读取 `raw_payload` 绕过 typed 字段。
- `FundNavSeries`：`fund_code`、`share_class`、`records: tuple[FundNavRecord, ...]`、`nav_type`、`adjusted_basis`、`dividend_adjustment_status`、`identity_status`、`completeness_status`、`strong_drawdown_evidence_eligible: bool`、`strong_drawdown_ineligibility_reason: str | None`、`source: NavSourceMetadata`、`share_class_mapping: ShareClassMapping`、`date_range_start`、`date_range_end`、`record_count`。

`FundNavSeries.__post_init__` 或 module-level validator 必须保证：

- `record_count == len(records)`。
- `records` 不为空；空数据由 repository 归类为 `not_found` 或 `insufficient_records`。
- 每条 record 的 `share_class`、`nav_type`、`adjusted_basis` 与 series-level 字段一致。
- `records` 中 `date` 不得重复；重复 date 归类为 `integrity_error`。
- `nav_type` 与 `adjusted_basis` 必须满足上方兼容矩阵；非法组合归类为 `schema_drift`。
- `adjusted_basis="unknown"` 必须触发 fail-closed `adjustment_basis_unknown`，不得构造成功 series。
- `identity_status != "verified"` 时 `strong_drawdown_evidence_eligible=False`；其中 `requested_code_only` 的 reason 必须说明 source-returned identity 未验证，`identity_mismatch` 必须 fail-closed。
- `adjusted_basis="raw_unit_nav"` 时 `strong_drawdown_evidence_eligible=False`，reason 明确说明 raw unit NAV 未处理分红/拆分/份额转换。
- caller 未传 `start_date` / `end_date` / `minimum_records` 约束时，`completeness_status="unchecked"`；约束全部通过时为 `complete_enough`；不通过时直接 fail-closed，不构造 series。

### Raw Akshare Normalization

当前 `FundNavDataAdapter` 只代表 Akshare / 天天基金 raw `单位净值走势` source adapter。Implementation 必须保留旧方法：

- `load_nav_data()` 返回旧 `NavDataResult`，字段和 cache 行为对现有 snapshot/tests 兼容。
- 不把 `NavDataResult` 直接扩成 future drawdown contract 的唯一载体；旧结果太多消费点，且语义已绑定 raw rows。

新增 adapter 内部 source snapshot。该结构不进入 `data/__init__.py` re-export；它只作为 `FundNavDataAdapter.load_raw_nav_source()` 与 `FundNavRepository` 之间的 source-adapter DTO：

```python
@dataclass(frozen=True, slots=True)
class _RawNavSourceResult:
    fund_code: str
    records: NavPayload
    source: str
    origin_source: str
    cached: bool
    retrieved_at: str | None
    cache_updated_at: str | None
```

Cache metadata 暴露方法必须使用以下签名，不留给 implementation worker 自行选择：

```python
@dataclass(frozen=True, slots=True)
class _NavCacheEntry:
    records: NavPayload
    source: str
    updated_at: str

def _load_cached_with_metadata(self, fund_code: str) -> _NavCacheEntry | None:
    ...

def _load_cached_sync(self, fund_code: str) -> NavPayload | None:
    ...
```

实现要求：

- Cache hit 不得只暴露 `source="nav_cache"`；typed provenance 必须能看到 `origin_source="akshare"` 和 `cache_updated_at`。
- `_load_cached_with_metadata()` 查询 `payload_json`、`source`、`updated_at` 并返回 `_NavCacheEntry`；旧 `_load_cached_sync()` 继续保持 `NavPayload | None` 返回类型，内部只调用 `_load_cached_with_metadata()` 并取 `records`。
- `load_raw_nav_source(fund_code, *, force_refresh=False) -> _RawNavSourceResult` 使用 `_load_cached_with_metadata()` 暴露 metadata；旧 `load_nav_data()` 在 cache hit 时仍返回 `NavDataResult(source="nav_cache", cached=True)`，现有 cache tests 不需要改期望。
- 不允许任何 production code 直接读取 SQLite；SQLite 访问仍封装在 adapter 内。

Normalization rules：

- Required raw columns：`净值日期`、`单位净值`。`日增长率` 可选。
- `净值日期` parse 为 `datetime.date`；非法日期是 `schema_drift`。
- `单位净值` parse 为 `Decimal`；缺失、空字符串、非数值、非正数是 `schema_drift` 或 `integrity_error`。建议非数值为 `schema_drift`，非正数为 `integrity_error`。
- `日增长率` 若存在则 parse 为 `Decimal | None`；非法不应 silently drop，归类 `schema_drift`。
- Parsed records 必须按 date 形成唯一序列；重复 date 不做 silent dedupe，直接归类为 `integrity_error` fail-closed。排序可由 repository 统一按 date 升序输出；若排序前后发现重复或不可稳定排序，归类 `integrity_error`。
- Series-level fixed values for current path：
  - `nav_type="unit_nav"`
  - `adjusted_basis="raw_unit_nav"`
  - `dividend_adjustment_status="not_adjusted"`
  - `strong_drawdown_evidence_eligible=False`
  - `strong_drawdown_ineligibility_reason` 包含 `raw_unit_nav` 和 `dividend/total-return basis not proven` 同义信息。
- Source-returned identity 当前不可得时用 `identity_status="requested_code_only"`，不是 `verified`；未来 source 若返回 fund code/name 且冲突，必须 `identity_mismatch` fail-closed。

### Fail-Closed Taxonomy

`FundNavRepository.load_nav_series()` 必须把以下情况归类为 `NavDataContractError`：

| 场景 | category | 处理 |
|---|---|---|
| fund_code 为空 / share_class 非法 | `identity_mismatch` 或 `schema_drift` 前置错误 | fail-closed；建议 ValueError 只用于纯调用方空参，contract error 用于 source/identity 语义 |
| source 调用异常、akshare import/network/cache sqlite 失败 | `unavailable` | fail-closed；保留 cause |
| source 成功但 0 raw records | `not_found` | fail-closed |
| raw columns 缺失或字段类型/日期格式不可解析 | `schema_drift` | fail-closed |
| NAV 值非正、records 日期重复导致路径不可用、排序无法稳定 | `integrity_error` | fail-closed |
| source-returned code/name 与请求或 share-class mapping 冲突 | `identity_mismatch` | fail-closed |
| adjusted basis 缺失或等于 `unknown` | `adjustment_basis_unknown` | fail-closed |
| caller 传入 `start_date` / `end_date` 但 series 覆盖不足 | `missing_date_range` | fail-closed |
| caller 传入 `minimum_records` 但 parsed records 不足 | `insufficient_records` | fail-closed |

注意：`not_found` / `unavailable` 是未来多 source fallback eligible 类别；本 gate 可以先单 source fail-closed，不实现 fallback。`schema_drift`、`identity_mismatch`、`integrity_error`、`adjustment_basis_unknown` 必须禁止 fallback 静默掩盖。

## Implementation Slices

### Slice 1a - Typed Models And Pure Contract Tests

Objective：先落地不依赖 IO 的 typed model / Literal domain / validator / exception contract，使 model 设计可被独立 review。

Allowed files：

- `fund_agent/fund/data/nav_models.py`
- `fund_agent/fund/data/__init__.py`
- 新增 `tests/fund/data/test_nav_repository_contract.py`

Exact changes：

1. 新增 `nav_models.py`，定义 Literal domain、typed dataclasses、`NavDataContractError`，全部中文 docstring。
2. `FundNavSeries` validator / `__post_init__` 覆盖：
   - record count、非空 records；
   - record-level `share_class/nav_type/adjusted_basis` 与 series-level 一致；
   - date 唯一性，重复 date -> `integrity_error`；
   - `NavType` / `AdjustmentBasis` 兼容矩阵，非法组合 -> `schema_drift`；
   - `adjusted_basis="unknown"` -> `adjustment_basis_unknown`；
   - `identity_status != "verified"` 时不得 strong eligible；
   - `raw_unit_nav` 不得 strong eligible；
   - completeness unchecked / complete_enough 语义。
3. `NavSourceMetadata.failure_category` 类型为 `NavFailureCategory | None`，成功 series 默认为 `None`。
4. `FundNavRecord` 包含 `share_class`，`raw_payload` docstring 明确仅供 diagnostics。
5. 更新 `data/__init__.py` re-export typed model public symbols，但不 re-export adapter 内部 `_RawNavSourceResult` 或 `_NavCacheEntry`。
6. 在 `test_nav_repository_contract.py` 先放纯 model tests：
   - dataclass 构造字段完整；
   - `failure_category is None` success path；
   - `identity_status="requested_code_only"` + adjusted candidate 也必须 not strong eligible 或 validator 拒绝 strong flag；
   - illegal `NavType` / `AdjustmentBasis` combination raises `schema_drift`；
   - duplicate dates raise `integrity_error`；
   - record share class mismatch raises `identity_mismatch` 或 `integrity_error`（implementation 选一类但必须 fail-closed 并在 docstring 说明）；
   - `raw_payload` 不参与 equality/consumer rules 之外的业务判断。

Slice 1a non-goals：

- 不修改 `nav_data.py`。
- 不新增 repository IO。
- 不调用 akshare、SQLite 或 cache。
- 不改 `FundDataExtractor`、snapshot、score、quality gate。

Slice 1a validation：

```bash
uv run pytest tests/fund/data/test_nav_repository_contract.py -q
uv run ruff check fund_agent/fund/data/nav_models.py tests/fund/data/test_nav_repository_contract.py
```

Expected result：pure model tests pass；新 `nav_models.py` 单文件覆盖率目标 ≥80%，若未达到必须在 implementation report/residual 中说明原因和补测计划。

Stop conditions：

- 如果 typed model 需要依赖 `FundNavDataAdapter`、SQLite、akshare 或 extractor 类型才能自洽，停止并回报 controller。
- 如果 validator 无法表达 `identity_status != "verified"` 不得 strong eligible，停止并回报 controller。

### Slice 1b - Adapter Metadata, Repository Normalization, Integration Tests

Objective：在保持旧 `load_nav_data()` 兼容的前提下，暴露 cache/source metadata，并通过 repository 把当前 Akshare raw rows normalize 为 typed `raw_unit_nav` series。

Allowed files：

- `fund_agent/fund/data/nav_data.py`
- `fund_agent/fund/data/nav_repository.py`
- `fund_agent/fund/data/__init__.py`
- `tests/fund/data/test_nav_data.py`
- `tests/fund/data/test_nav_repository_contract.py`

Prerequisite：Slice 1a 已通过并被 controller 接受，typed symbols 已稳定。

Exact changes：

1. 在 `nav_data.py` 中新增私有 `_NavCacheEntry` dataclass 和 `_load_cached_with_metadata(fund_code) -> _NavCacheEntry | None`，查询 `payload_json`、`source`、`updated_at`。
2. 保留 `_load_cached_sync(fund_code) -> NavPayload | None`，内部调用 `_load_cached_with_metadata()` 后只返回 records；旧 `load_nav_data()` cache hit 继续返回 `NavDataResult(source="nav_cache", cached=True)`。
3. 在 `nav_data.py` 中新增 `load_raw_nav_source(fund_code, *, force_refresh=False) -> _RawNavSourceResult`，返回 records + source/cache metadata。该方法是 source adapter 边界，不做 drawdown 计算，不进入 `data/__init__.py` public re-export。
4. 新增 `nav_repository.py`：
   - `FundNavRepository.__init__(source_adapter: FundNavDataAdapter | None = None)`；
   - `load_nav_series(...)` 使用显式参数；
   - 调用 source adapter；
   - normalize raw records；
   - apply share-class default mapping；
   - validate date range / minimum records；
   - fail-closed 抛 `NavDataContractError`。
5. `FundNavRepository` 中禁止 `extra_payload`、`**kwargs` 和 source-specific helper 直连；所有输入必须经显式参数。
6. 更新 `data/__init__.py` re-export `FundNavRepository`，继续保留 Slice 1a typed symbols。
7. 扩展现有 `test_nav_data.py`：
   - 旧 cache 复用、force refresh、unavailable helper 继续通过；
   - 新增 cache metadata 测试：fetch 后再 cache hit，typed source result 能暴露 `origin_source="akshare"` 和 `cache_updated_at`，旧 `load_nav_data()` 仍显示 `source="nav_cache"`。
8. 扩展 `test_nav_repository_contract.py` repository integration assertions：
   - 006597-like raw fixture Chinese keys 被转成 `FundNavSeries`，字段包含 `fund_code`、`share_class`、record `date/nav_value/nav_type/adjusted_basis`、source/provenance、identity/share-class mapping。
   - raw fixture series 标记 `adjusted_basis="raw_unit_nav"`、`nav_type="unit_nav"`、`dividend_adjustment_status="not_adjusted"`、`strong_drawdown_evidence_eligible is False`。
   - `identity_status="requested_code_only"` 时 series 可返回但不得 strong eligible；fake source returned identity mismatch 时 raise `NavDataContractError(category="identity_mismatch")`。
   - 缺少 `净值日期` 或 `单位净值` raise `schema_drift`。
   - `adjusted_basis="unknown"` 或 normalization helper 缺 basis raise `adjustment_basis_unknown`。
   - duplicate raw dates raise `integrity_error`。
   - requested date range 覆盖不足 raise `missing_date_range`。
   - `minimum_records` 不足 raise `insufficient_records`。
   - source adapter 抛异常时 raise `unavailable` 且 cause 可追溯。
   - `inspect.signature(FundNavRepository.load_nav_series)` 不包含 `extra_payload`、`kwargs`、自由 dict 参数。

Slice 1b non-goals：

- 不改 `FundDataExtractor` 默认注入，不把 `StructuredFundDataBundle.nav_data` 改成 typed series。
- 不改 `extraction_snapshot.py` note/schema。
- 不引入 drawdown metric 或 bond risk extractor 消费。

Slice 1b validation：

```bash
uv run pytest tests/fund/data/test_nav_data.py tests/fund/data/test_nav_repository_contract.py -q
uv run ruff check fund_agent/fund/data tests/fund/data
```

Expected result：focused tests pass；旧 tests 对 `load_nav_data()` 的 source/cached 行为不回归；新增 `nav_repository.py` 单文件覆盖率目标 ≥80%，若未达到必须在 implementation report/residual 中说明原因和补测计划。

Stop conditions：

- 如果必须改旧 `NavDataResult` 必填字段或 `load_nav_data()` 返回 shape 才能实现 typed path，停止并回报 controller。
- 如果需要 snapshot/score/quality gate schema 变更，停止并回报 controller。

### Slice 2 - Docs, Design Sync, Real 006597 Smoke Evidence

Objective：把新 typed contract 作为当前 Fund data boundary 记录清楚，并用真实 006597 smoke 证明 raw-unit-only typed path 可达但不 strong eligible。

Allowed files：

- `docs/design.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-evidence-20260528.md`
- 如 controller 指派，可最小更新 `docs/implementation-control.md`；否则 control doc 由 controller acceptance gate 更新。

Exact changes：

1. `docs/design.md` 最小同步：
   - 在 `NavDataResult` 当前描述旁新增 typed NAV repository contract 当前事实。
   - 明确旧 `NavDataResult` 是 legacy snapshot/analyze 兼容结果；typed `FundNavRepository.load_nav_series()` 是 future drawdown metric 的唯一可消费边界。
   - 明确当前 Akshare path 只证明 `raw_unit_nav`，`strong_drawdown_evidence_eligible=False`；不得写成 adjusted/total-return 当前事实。
2. `fund_agent/fund/README.md` 最小同步：
   - data 层新增 `FundNavRepository` / typed NAV series contract；
   - 旧 `FundNavDataAdapter.load_nav_data()` 继续供 P1/snapshot 兼容；
   - raw_unit_nav 不可作为强 drawdown evidence。
3. `tests/README.md` 更新：
   - 新增 `test_nav_repository_contract.py` 说明；
   - 保留常规 pytest 不依赖真实 akshare 网络；真实 006597 smoke 只作为人工/implementation evidence。
4. 真实 smoke 命令通过 typed repository 加载 006597：

```bash
uv run python -c 'import asyncio, json; from fund_agent.fund.data import FundNavRepository; async def main(): s = await FundNavRepository().load_nav_series("006597", minimum_records=30); print(json.dumps({"fund_code": s.fund_code, "share_class": s.share_class, "records": s.record_count, "adjusted_basis": s.adjusted_basis, "nav_type": s.nav_type, "dividend_adjustment_status": s.dividend_adjustment_status, "identity_status": s.identity_status, "strong_drawdown_evidence_eligible": s.strong_drawdown_evidence_eligible, "source": s.source.source_name, "origin_source": s.source.origin_source, "cached": s.source.cached, "cache_updated_at": s.source.cache_updated_at}, ensure_ascii=False, default=str)); asyncio.run(main())'
```

Expected smoke assertions：

- `fund_code == "006597"`
- `adjusted_basis == "raw_unit_nav"`
- `nav_type == "unit_nav"`
- `dividend_adjustment_status == "not_adjusted"`
- `strong_drawdown_evidence_eligible is False`
- provenance includes source/cache metadata and identity status; if cache hit, origin source remains visible.

5. 写 implementation evidence artifact，记录 focused tests、full validation、real smoke JSON、docs decision、non-goal preservation。Artifact 必须明说 `drawdown_stress` blocker 未解除。

Slice 2 validation：

```bash
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

Expected result：full ruff pass；full pytest coverage gate pass。无需 rerun snapshot/score/quality gate，因为本 plan 不触碰相关路径；若 implementation 实际改了 snapshot/score/quality gate 相关文件，则必须停止或追加 controller-approved validation。

Stop conditions：

- 真实 smoke 因网络/source unavailable 失败：记录 `unavailable` category 和 cause；不要改测试放宽 contract。Controller 可决定是否接受 unit-level proof + blocked real smoke residual。
- 如果 docs update 需要声称 drawdown evidence accepted，停止；这超出本 gate。

## Future Consumer Rule

后续 `drawdown_stress` extractor / metric gate 必须满足：

- 只能依赖 `FundNavRepository.load_nav_series(...) -> FundNavSeries`。
- 必须显式传入 `fund_code`、`share_class`、`start_date`、`end_date`、`minimum_records` 等参数；不得用 `extra_payload`。
- 必须同时检查三条件：`identity_status == "verified"`、`strong_drawdown_evidence_eligible is True`、`adjusted_basis in {"dividend_adjusted_nav", "total_return"}` 或后续 accepted set。三条件缺一不可；`raw_unit_nav` 和 `requested_code_only` 默认拒绝。
- 不得直接调用 `FundNavDataAdapter.load_nav_data()`、Akshare、网页 helper、SQLite cache、snapshot JSONL 或 source-specific internals。
- 不得读取 `FundNavRecord.raw_payload` 参与 drawdown 计算、身份判定、adjusted-basis 判定或 evidence eligibility；`raw_payload` 只用于 diagnostics/debugging。

## Review Requirements

因为本 gate 是 `heavy` 且改变 Fund data public contract：

- 需要至少两份独立 review。
- Review 必须检查四层边界、显式参数/无 `extra_payload`、旧 `load_nav_data()` 兼容、fail-closed taxonomy、raw_unit_nav evidence eligibility、docs sync、测试覆盖。
- Review 不能接受解除 `drawdown_stress` blocker、FQ0-FQ6 变更、score/golden/snapshot schema 变更。

## Completion Report Format For Implementation Worker

Implementation worker 完成后必须报告：

- Modified files。
- Slice 1 / Slice 2 completion status。
- Typed contract public symbols。
- Backward compatibility proof for `load_nav_data()`。
- Test results：
  - focused tests；
  - `uv run ruff check .`；
  - `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`。
- 006597 real smoke JSON summary，至少包含 `adjusted_basis`、`nav_type`、`dividend_adjustment_status`、`identity_status`、`source/provenance`、`strong_drawdown_evidence_eligible`。
- Explicit statement：`drawdown_stress blocker remains unresolved`。
- Residual risks and uncovered areas。

## Blocking Questions

无 blocking questions。

Working assumptions：

- 当前 source path 不返回 source identity；因此 typed series 可用 `identity_status="requested_code_only"` 返回，但不得 strong eligible。
- `FundNavRepository` 是未来 drawdown consumer 的统一边界；旧 `FundNavDataAdapter.load_nav_data()` 只保留兼容。
- 006597 默认 share class 可先映射为 A class，因为当前输入 fund name / code 是 `国泰利享中短债债券A` / `006597`，但 mapping 必须显式标注为 default/requested-code mapping，不得推断 C/E/F。

## Residual Risks

- 当前 provider 仍只有 raw unit NAV，typed contract 不提供 strong drawdown evidence；这是 intentional residual。
- 当前 source-returned identity 不可得，identity 只能是 `requested_code_only`，不是 verified；未来强证据 gate 需要更强 source identity 或独立 share-class proof。
- Cache metadata 当前 SQLite schema 有 `source` / `updated_at`，但旧 cache rows 的 source semantics 仍需要通过 typed smoke 复核；不得通过外部 SQLite 读取绕过 adapter。
- Full real smoke 可能受 akshare/cache/network 环境影响；失败时应记录 typed `unavailable` residual，不应削弱 contract。
- 单一 `FundNavSeries` 只表达一个 `nav_type` / `adjusted_basis` / `share_class`。如果未来 source 一次响应返回 unit NAV 与 accumulated NAV 等多种 series，repository 必须拆分为多个 `load_nav_series()` 结果，或另开 gate 设计 `FundNavBundle`。
- 当前 cache SQLite `source` 列只能暴露 `"akshare"` 等粗粒度 origin；source URL、source ID、provider version 等更丰富 provenance 需要未来 schema migration gate。
- 真实 006597 smoke 是 implementation evidence，不进入 CI；CI 只运行 deterministic unit/focused/full pytest。

## Handoff Readiness

本 plan 已 handoff-ready / code-generation-ready。后续 worker 可以按 Slice 1、Slice 2 直接实现，无需重新选择模块、发明 schema、决定 failure taxonomy 或判断 docs/test scope。
