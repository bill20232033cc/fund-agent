# CSRC EID Accumulated NAV Adapter Normalization — Implementation Plan

日期：2026-05-29
角色：planning worker
Gate：`CSRC EID accumulated NAV adapter normalization implementation gate`
Gate classification：`heavy`

## 0. Step Self-Check

- Current gate / role：当前只写 implementation plan；我是 planning worker，不是 controller / implementation / review worker。
- Source of truth：已读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、typed NAV controller judgment、DS/GLM aggregate deepreview、CSRC EID / stock-sdk controller judgment 与 evidence、最新 006597 snapshot/score/quality gate，以及 MiMo/GLM plan review findings。
- Scope boundary：本 plan 只允许 Fund data 层 CSRC EID NAV source adapter、typed repository normalization、tests、minimal docs 和 `docs/reviews/` artifacts；禁止 bond extractor、scoring、snapshot、quality gate、golden fixture、Service/UI/Host/Agent-dayu、release/PR/push/promotion。
- Stop conditions：当前没有 material unresolved option；若实现时发现 CSRC EID public endpoint schema 与 accepted evidence 不一致，必须 fail closed 并停给 controller，不得临时改成 Eastmoney/stock-sdk fallback。
- Evidence and validation：实现完成必须跑 ruff、全量 pytest coverage、real CSRC EID smoke；本 gate不实现 drawdown metric，不解除 `drawdown_stress` blocker。
- Next action：controller 可派 implementation worker 按本 plan 分 slice 实现，然后派独立 review。

## 1. 真源复述

### 1.1 `AGENTS.md`

- 本仓库规则真源是 `AGENTS.md`；回答用中文。
- 当前目标架构固定为 `UI -> Service -> Host -> Agent`。NAV source/repository 属于 Agent 层 `fund_agent/fund` data 能力；UI/Service/Host 不得直接绕过 Fund data 边界访问具体来源、cache 或 helper。
- 所有参数必须显式声明，禁止把显式参数塞进 `extra_payload`。
- 代码必须有中文模块/类/函数 docstring，复杂逻辑用中文注释说明意图。
- 年报和生产文档访问必须走 `FundDocumentRepository`；本 gate 不读取 PDF 文件系统、不绕过文档仓库。
- fallback 必须按失败分类决策：`not_found`、`unavailable` 可 fallback；`schema_drift`、`identity_mismatch`、`integrity_error` 必须 fail closed。NAV 已扩展的 `adjustment_basis_unknown`、`missing_date_range`、`insufficient_records` 也必须 fail closed。
- `fast_path` 不能改变 public contract/schema/source strategy；本 gate改变 NAV runtime source normalization，分类必须是 `heavy`。

### 1.2 `docs/design.md`

- 当前确定性生产链路仍是 UI -> Service -> `fund_agent/fund` 过渡实现，尚未接入 Host/Agent 调度；不得创建 Host/Agent 包或引入 `dayu.host` / `dayu.engine`。
- `FundNavRepository.load_nav_series()` 是后续路径型 NAV 指标唯一 typed 边界；旧 `FundNavDataAdapter.load_nav_data()` 只保留 legacy/snapshot/analyze 兼容。
- 当前 typed NAV contract 已有 `FundNavSeries`、`FundNavRecord`、`NavSourceMetadata`、`ShareClassMapping`、failure taxonomy 和 `nav_type` / `adjusted_basis` 兼容矩阵。
- 当前已实现事实仍是 Akshare raw unit NAV：`nav_type="unit_nav"`、`adjusted_basis="raw_unit_nav"`、`identity_status="requested_code_only"`、`strong_drawdown_evidence_eligible=False`。本 gate 只能把 CSRC EID accumulated NAV 归一化进同一 typed 边界，不能宣称 drawdown metric 已实现。

### 1.3 `docs/implementation-control.md`

- Current phase：`release maintenance`。
- Next entry point：`CSRC EID accumulated NAV adapter normalization implementation gate`。
- 已接受事实：CSRC EID internal ID `5755` 映射到国泰利享中短债债券 A/C/E/F 分类 NAV 表；CSRC EID 是 future primary `accumulated_nav` adapter candidate；stock-sdk 仅 evidence-only；raw_unit_nav 仍不能作为强回撤证据。
- 当前 006597 最新 score 仍有 `bond_risk_evidence_missing.baseline_blocking=true`，缺口只剩 `drawdown_stress`。本 gate 不得解除该 blocker。
- 允许范围要求：只通过 `FundNavRepository.load_nav_series()` 消费 NAV；显式传 `fund_code`、`share_class`、`start_date`、`end_date`、`minimum_records`；绑定 CSRC EID public search / internal ID / classification；A/C/E/F 分离；fail closed；不改 bond extractor、score、snapshot、quality gate、golden、Host/Agent/dayu。

### 1.4 Typed NAV Implementation Judgment / DS / GLM Aggregate Deepreview

- 已接受的 typed contract 包括 `NavType`、`AdjustmentBasis`、`DividendAdjustmentStatus`、`NavIdentityStatus`、`NavCompletenessStatus`、`NavFailureCategory`、`FundNavSeries`、`FundNavRecord`、`NavSourceMetadata`、`ShareClassMapping`。
- 当前失败分类 8 类已覆盖：`not_found`、`unavailable`、`schema_drift`、`identity_mismatch`、`integrity_error`、`adjustment_basis_unknown`、`missing_date_range`、`insufficient_records`。本 gate不新增 taxonomy。
- 已接受兼容矩阵：`unit_nav -> raw_unit_nav`、`accumulated_nav -> accumulated_nav`、`adjusted_nav -> dividend_adjusted_nav`、`total_return_index -> total_return`。
- DS/GLM residuals：raw unit reason 常量可后续清理；防御性分支测试缺口可补；`raw_payload` 不能被 future consumer 用来绕过 typed fields。
- 旧 `load_nav_data()` 兼容性必须保持；source/cache 私有 DTO 不应泄漏到 public API。

### 1.5 CSRC EID / stock-sdk Source Evaluation Judgment + Evidence

- CSRC EID decision：`accepted-primary-candidate`。
- Verified internal ID：`5755`。
- Search endpoint：`POST /fund/disclose/validate_fund.do`，参数 `cFundCode=<基金名或份额代码>`；已验证 `国泰利享中短债债券`、`006597`、`006598`、`014217` 均返回 `fundId=5755`，`022176` direct search missing。
- Detail endpoint：`GET /fund/disclose/fund_detail_search.do?cFundCode=5755`；页面包含 A/C/E/F 份额分类名称、代码和更多净值链接。
- Classification endpoint：`GET /fund/disclose/list_net_classification.do?fundCode=006597&classification=<classification>&limit=20&start=<offset>`。
- Share-class proof：A `006597=2030-1010`，C `006598=2030-1020`，E `014217=2030-1040`，F `022176=2030-1050`。必须分份额输出，不得混成产品级 NAV。
- CSRC EID row columns：`估值日期`、`单位净值`、`累计净值`、`基金资产净值`、`备注`。
- E-class distribution anchor：`2023-01-11` 后 `累计净值 - 单位净值` 增加 `0.0080`，与年报 §3.3 每 10 份 `0.080` 一致。该证据只证明 `accumulated_nav`，不证明 `dividend_adjusted_nav` 或 `total_return`。
- stock-sdk decision：`evidence-only`。`getFundNavHistory` 因 date shift 属于 `integrity_error`，不得作为 runtime typed source；`getFundDividendList` 只能做 diagnostics/cross-check。

### 1.6 Latest 006597 Artifacts

- Snapshot：`bond_risk_evidence.v1` 为 `partial`，satisfied groups 包含 `duration_rate_risk`、`credit_risk`、`leverage_liquidity`、`asset_allocation_holdings_mix`、`redemption_share_pressure`、`convertible_bond_equity_exposure`；weak groups 仍为 `drawdown_stress`。
- Score：`bond_risk_evidence` 字段 pass，但 fund status 仍 fail；`nav_data` traceability fail；P1 failed fields 仍含 `turnover_rate`、`holder_structure`、`share_change`。这不是本 gate 的修复目标。
- Quality gate：status `warn`，仍有 `bond_risk_evidence_missing` 语义提示。实现 CSRC EID adapter 后不得重跑/修改 snapshot、score、quality gate 来宣称 blocker 解除。

## 2. Goal

实现 CSRC EID accumulated NAV source adapter normalization，把官方 CSRC EID A/C/E/F share-class NAV 表通过 `FundNavRepository.load_nav_series()` 归一化为现有 typed NAV contract：

- `nav_type="accumulated_nav"`
- `adjusted_basis="accumulated_nav"`
- `dividend_adjustment_status="not_applicable"`
- `identity_status="verified"`
- source provenance 显式记录 `source_name/source_url/source_id/retrieved_at/query params/record_count/date_range/identity_status/failure_category`
- A/C/E/F share class 严格分离
- `strong_drawdown_evidence_eligible=True` 只表示 source identity 与 accumulated basis 已满足路径型指标的 source-level eligibility；它不产生 drawdown metric，不构成 `drawdown_stress` evidence acceptance，也不解除 blocker。

实现完成后，future consumer 仍只能通过 `FundNavRepository` 使用 typed series；本 gate不实现 drawdown metric、不修改 bond extractor、不解除 `drawdown_stress` blocker。

## 3. Non-Goals

- 不实现 max drawdown、volatility、drawdown_stress metric、risk scoring policy 或 reviewed metric contract。
- 不修改 `fund_agent/fund/extractors/bond_risk_evidence.py`、`data_extractor.py`、snapshot、score、quality gate、golden fixture。
- 不把 accumulated NAV 解释为 dividend-adjusted NAV、total-return index 或 total return。
- 不引入 stock-sdk runtime dependency、Node subprocess adapter、Eastmoney fallback 或 Akshare accumulated source fallback。
- 不绕过 `FundNavRepository`，不在 extractor 中放 source-specific helper。
- 不修改 Service/UI/Host/Agent-dayu，不创建 Host/Agent 包。
- 不做 QDII/FOF/golden/release/PR/push/merge/promotion。

## 4. Required Design Decisions

### 4.0 Source Adapter Protocol / DTO Contract

实现必须先建立 repository 依赖的统一 source adapter contract，避免 implementation worker 自行选择架构。

File location：

- 新增 `fund_agent/fund/data/nav_source_contract.py`。
- 该模块只放 Fund data 层内部 source contract，不在 `fund_agent/fund/data/__init__.py` 中导出为 public API，除非 controller 后续另行批准。

Exact DTO：

```python
@dataclass(frozen=True, slots=True)
class _RawNavSourceResult:
    fund_code: str
    records: list[dict[str, object]]
    source: str
    origin_source: str
    source_id: str | None
    source_url: str | None
    source_query_params: tuple[tuple[str, str], ...]
    source_nav_type: NavType
    source_adjustment_basis: AdjustmentBasis
    cached: bool
    retrieved_at: str | None
    cache_updated_at: str | None
```

Exact Protocol：

```python
class _NavSourceAdapter(Protocol):
    async def load_raw_nav_source(
        self,
        fund_code: str,
        *,
        share_class: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        force_refresh: bool = False,
    ) -> _RawNavSourceResult:
        ...
```

Implementation requirements：

- `FundNavDataAdapter.load_raw_nav_source()` must explicitly implement the same signature; `share_class/start_date/end_date` are accepted for Protocol compatibility and ignored by the legacy raw-unit adapter.
- `CsrcEidNavSource.load_raw_nav_source()` must explicitly implement the same signature and use all relevant explicit params.
- No `extra_payload`、no `**kwargs`、no broad `source_options` dict。
- `FundNavRepository.__init__` must be updated to `source_adapter: _NavSourceAdapter | None = None` and store only the Protocol dependency.
- `_RawNavSourceResult.source_nav_type/source_adjustment_basis` are required fields, not optional deferred design. Repository must branch by this explicit source contract:
  - `("unit_nav", "raw_unit_nav")` -> `_normalize_raw_unit_series(...)`
  - `("accumulated_nav", "accumulated_nav")` -> `_normalize_accumulated_nav_series(...)`
  - any other pair -> `adjustment_basis_unknown` or `schema_drift` according to the typed compatibility matrix.

### 4.1 CSRC EID Stable Access

实现必须使用 public endpoint 的 deterministic identity flow：

1. Search：
   - `POST http://eid.csrc.gov.cn/fund/disclose/validate_fund.do`
   - form body：`cFundCode=<requested fund code or fund name>`
   - 用于把 `006597` / `006598` / `014217` / 产品名解析到 internal `fundId=5755`。
2. Detail：
   - `GET http://eid.csrc.gov.cn/fund/disclose/fund_detail_search.do?cFundCode=5755`
   - 用于解析 product title、A/C/E/F share-class name/code/classification links。
3. Classification NAV：
   - `GET http://eid.csrc.gov.cn/fund/disclose/list_net_classification.do`
   - query：`fundCode=006597`、`classification=<2030-1010|2030-1020|2030-1040|2030-1050>`、`limit=20`、`start=<offset>`
   - 使用 HTML pagination 的 total records / current range 驱动翻页。

实现不得依赖随机 `rnd` 或 `t`：

- evidence 中的 `rnd` / `t` 是前端 cache-busting 参数，不是 identity、authorization 或 schema contract。
- Adapter 的 correctness 必须来自 search response、detail page identity 和 classification rows，不来自 random token。
- 默认请求应省略 `rnd` / `t`；如果后续 controller 证明服务端必须接受 cache-busting 参数，必须使用显式 deterministic 参数名并把它记录进 `source_query_params`，但不得把随机值作为 identity evidence。

### 4.2 Field Normalization

CSRC EID raw row 到 typed model 的字段映射：

| CSRC EID raw | Typed field |
|---|---|
| `估值日期` | `FundNavRecord.date`，ISO/date parser，空或不可解析 -> `schema_drift` |
| `累计净值` | `FundNavRecord.nav_value`，Decimal 正数，空/缺失 -> 按请求窗口 fail closed |
| `单位净值` | `FundNavRecord.raw_payload["单位净值"]` 且可选解析为 diagnostics；不作为 `nav_value` |
| 份额代码 | `FundNavSeries.fund_code` / `ShareClassMapping.resolved_fund_code` |
| 份额名称 | `NavSourceMetadata.returned_fund_name` / mapping evidence |
| classification | `NavSourceMetadata.source_id` 和 mapping evidence |
| detail/list URL | `NavSourceMetadata.source_url` |

成功 series 必须：

- `nav_type="accumulated_nav"`
- `adjusted_basis="accumulated_nav"`
- 每条 record 同样是 `nav_type="accumulated_nav"` / `adjusted_basis="accumulated_nav"`
- `dividend_adjustment_status="not_applicable"`，因为 accumulated NAV 是披露口径，不是 dividend-adjusted total-return basis。
- `raw_change_rate=None`，除非 CSRC EID row 明确提供日增长率；不得用单位净值推导。

### 4.3 Share-Class Identity

Adapter 必须先通过 detail page 解析 share classes，再选择 requested share class：

| Requested | Share class | Product fundCode param | Classification |
|---|---|---:|---:|
| `006597` / `share_class="A"` | A | `006597` | `2030-1010` |
| `006598` / `share_class="C"` | C | `006597` | `2030-1020` |
| `014217` / `share_class="E"` | E | `006597` | `2030-1040` |
| `022176` / `share_class="F"` | F | `006597` | `2030-1050` |

Rules：

- `006597=A`、`006598=C`、`014217=E` 必须由 public search -> `fundId=5755` 加 detail page classification 双重验证。
- `022176=F` direct search missing 是 accepted search-index limitation；必须由 verified `5755` detail page classification 证明。若 detail page 无 F code/classification，`identity_mismatch` fail closed。
- A/C/E/F 必须各自构造独立 `FundNavSeries`；禁止把 product-level `006597` 或不同 classification rows 混成一条 product-level NAV。
- `share_class` 参数与 `fund_code` 冲突时 fail closed：如 `fund_code="006598", share_class="A"` 必须 `identity_mismatch`。

### 4.4 Adjustment Basis

- CSRC EID `累计净值` 只映射为 `nav_type="accumulated_nav"` 和 `adjusted_basis="accumulated_nav"`。
- 禁止声称 `dividend_adjusted_nav`、`total_return` 或 `total_return_index`。
- Raw unit NAV path 仍保留为 `nav_type="unit_nav"` / `adjusted_basis="raw_unit_nav"` / `strong_drawdown_evidence_eligible=False`。
- CSRC EID accumulated verified series 使用 Option A：在 source identity verified、date range complete、minimum_records satisfied 后，`strong_drawdown_evidence_eligible=True` 可以成立。该字段是 source-level eligibility flag，只说明 NAV source 的身份与 accumulated basis 已通过 typed contract；它不等于 drawdown metric evidence，不修改 `bond_risk_evidence.v1`，不让 score/quality gate 接受 `drawdown_stress`，也不解除 blocker。

### 4.5 Provenance Contract

现有 failure taxonomy 不扩展；provenance 需要 plan-approved explicit field extension：

- 在 `NavSourceMetadata` 增加显式字段 `source_query_params: tuple[tuple[str, str], ...] = ()`。
- 不使用 `extra_payload`、自由 dict 或 `**kwargs`。
- `record_count`、`date_range_start`、`date_range_end` 继续使用 `FundNavSeries` 现有字段。
- `identity_status` 继续使用 `FundNavSeries.identity_status` 与 `ShareClassMapping.identity_status`。
- `failure_category` 继续使用 `NavSourceMetadata.failure_category` / `NavDataContractError.category`。

CSRC EID successful series provenance：

- `source_name="csrc_eid"`
- `origin_source="csrc_eid"`
- `source_id="5755:<classification>"`
- `source_url=<classification list URL without rnd>`
- `cached=False`，除非本 gate 显式实现 CSRC EID cache；推荐首版不加新 cache。
- `retrieved_at=<UTC datetime>`
- `requested_fund_code=<user fund_code>`
- `returned_fund_code=<share-class code>`
- `returned_fund_name=<share-class name>`
- `source_query_params=(("fundCode","006597"),("classification","2030-1010"),("limit","20"),...)`；分页 `start` 可在 `raw_payload` 记录每页或在 mapping evidence 汇总，不得用 extra_payload。

### 4.6 Failure Taxonomy

不新增 taxonomy。实现按现有 8 类归类：

| Condition | Category | Fallback |
|---|---|---|
| search 正常响应但无匹配 fundId | `not_found` | 可由 future strategy fallback；本 gate默认不 fallback 到 stock-sdk |
| HTTP/network/timeout | `unavailable` | 可由 future strategy fallback；本 gate默认抛出 |
| HTML/JSON schema、pagination shape、columns 变化 | `schema_drift` | fail closed |
| requested code/share class/detail identity/classification 冲突 | `identity_mismatch` | fail closed |
| duplicate date、record total mismatch、非正 NAV、分页缺口 | `integrity_error` | fail closed |
| source 未能证明 accumulated basis | `adjustment_basis_unknown` | fail closed |
| requested date range 包含 A/C blank accumulated rows、F pre-inception 或 source 不覆盖窗口 | `missing_date_range` | fail closed |
| records 少于 `minimum_records` | `insufficient_records` | fail closed |

Missing accumulated NAV handling：

- 若 blank `累计净值` rows 落在 requested window 内，归类 `missing_date_range`，因为该窗口无法形成 accumulated NAV series。
- 若 blank accumulated 出现在 requested_start_date 之前，可丢弃这些 blank rows，并用剩余 records 构造 series；实际 `date_range_start` 从第一条有 accumulated NAV 的日期开始。
- 若无 explicit date constraints 且 source earliest blank rows 存在，允许丢弃 blank accumulated rows，但必须在 mapping evidence 记录 dropped count/date sample；若全部为空，`adjustment_basis_unknown`。

### 4.7 stock-sdk Decision

- `getFundNavHistory` 仍因 date-normalization `integrity_error` 被拒绝进入 runtime。
- `getFundDividendList` 只允许作为 diagnostics/cross-check；本 gate不新增 Node dependency、不调用 stock-sdk 做 production source、不把 stock-sdk 包进 repository fallback。

### 4.8 Repository Boundary

- Future consumer 只能调用 `FundNavRepository.load_nav_series()`。
- Bond extractor 不得直接 fetch CSRC EID、不引入 source-specific helper、不读 cache/PDF、不读 snapshot JSONL。
- Repository 负责 source adapter selection、identity normalization、typed model construction 和 fail-closed；source module 只负责 HTTP/page parsing 和返回 raw source DTO。

### 4.9 Repository Source Selection

- `FundNavRepository()` 无参构造时必须创建 `CsrcEidNavSource()`。
- 该 gate 不实现 source fallback。CSRC EID 返回 `not_found`、`unavailable`、`schema_drift`、`identity_mismatch`、`integrity_error`、`adjustment_basis_unknown`、`missing_date_range` 或 `insufficient_records` 时，repository 直接抛出 classified `NavDataContractError`。
- 不 fallback 到 Akshare raw unit NAV、stock-sdk、Eastmoney 或任何 product-level mixed source。
- Raw-unit compatibility 只通过 constructor injection 覆盖：tests 可传入 `_FakeRawNavAdapter` 或 `FundNavDataAdapter`，并由 `_RawNavSourceResult.source_nav_type/source_adjustment_basis` 进入 raw-unit normalization branch。
- 不添加 `source_options`、`fallback_strategy`、自由 dict 或 runtime source selector。

### 4.10 HTTP / Parser Strategy

- `CsrcEidNavSource.load_raw_nav_source()` 是 async 方法。
- 使用项目既有依赖 `httpx.AsyncClient`；不得新增 HTTP dependency。
- Timeout policy：`httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)`。
- Retry policy：最多 3 次尝试（initial + 2 retries），仅对 `httpx.TimeoutException`、`httpx.TransportError` 和 HTTP 5xx 重试；最终失败统一 `unavailable` 并保留 cause。HTTP 4xx 视具体 endpoint：search/detail/list 无可解析响应时 `unavailable`；响应可解析但业务无匹配时 `not_found`。
- HTML parser：使用 stdlib `html.parser.HTMLParser` 的小型 table/link parser，加 `html.unescape` 与 `urllib.parse` 解析 query；禁止新增 BeautifulSoup/lxml 依赖。
- Parser 不得靠单个大正则读取整页；允许少量正则只用于分页文本中的数字提取，并在 schema 变化时 `schema_drift` fail closed。

## 5. Affected Files / Allowed Changes

Allowed production files：

- `fund_agent/fund/data/nav_source_contract.py`（新增）
  - 定义 `_NavSourceAdapter` Protocol 与 `_RawNavSourceResult` explicit DTO。
  - DTO 包含 `source_nav_type` / `source_adjustment_basis`，repository 以此选择 normalization branch。
- `fund_agent/fund/data/nav_models.py`
  - 增加 `NavSourceMetadata.source_query_params` 显式字段。
  - 保持 taxonomy 不变。
- `fund_agent/fund/data/nav_data.py`
  - 移除或导入使用 `nav_source_contract.py` 的 `_RawNavSourceResult`，避免 CSRC module 跨模块引用 Akshare adapter 私有 DTO。
  - `FundNavDataAdapter.load_raw_nav_source()` 必须实现 Protocol signature：`async load_raw_nav_source(fund_code, *, share_class, start_date, end_date, force_refresh) -> _RawNavSourceResult`；新增参数显式忽略，用于 raw-unit compatibility。
  - Legacy `load_nav_data()` 不变。
- `fund_agent/fund/data/csrc_eid_nav_source.py`（新增）
  - CSRC EID HTTP client、HTML parser、pagination、share-class resolver。
- `fund_agent/fund/data/nav_repository.py`
  - `FundNavRepository.__init__(source_adapter: _NavSourceAdapter | None = None)`；默认 `CsrcEidNavSource()`。
  - 无 fallback；CSRC EID classified error 直接向上抛。
  - 默认使用 CSRC EID accumulated source path。
  - 保留 raw-unit adapter normalization helper，用于 legacy injected adapter tests 和 future explicit raw path。
  - 将 CSRC EID raw DTO 规范化为 accumulated `FundNavSeries`。
- `fund_agent/fund/data/__init__.py`
  - 仅按需导出稳定 public symbols；不要导出 CSRC EID private parser helpers。

Allowed tests：

- `tests/fund/data/test_nav_repository_contract.py`
- 新增 `tests/fund/data/test_csrc_eid_nav_source.py`
- `tests/fund/data/test_nav_data.py`（仅为 DTO/signature/legacy compatibility 必要时）
- `tests/README.md`

Allowed docs：

- `docs/design.md`：只写当前实现事实；不得写 drawdown metric 已完成。
- `fund_agent/fund/README.md`：Fund data typed NAV 边界和 CSRC EID accumulated source 当前行为。
- `tests/README.md`：新增 CSRC EID deterministic fixture tests 与 real smoke 说明。
- `docs/reviews/`：implementation evidence、review、controller judgment artifacts。

Forbidden files/modules：

- `fund_agent/fund/extractors/`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py`
- `fund_agent/fund/quality_gate_integration.py`
- `fund_agent/services/`
- `fund_agent/ui/`
- `fund_agent/host/`、`fund_agent/agent/`
- `reports/extraction-snapshots/`、`reports/scoring-runs/`、`reports/quality-gate-runs/`
- golden fixtures / release / PR state

## 6. Implementation Slices

### Slice 1 — Contract / DTO Provenance Extension

Files：

- `fund_agent/fund/data/nav_source_contract.py`
- `fund_agent/fund/data/nav_models.py`
- `fund_agent/fund/data/nav_data.py`
- `tests/fund/data/test_nav_repository_contract.py`
- `tests/fund/data/test_nav_data.py` if needed

Exact changes：

- Add `source_query_params: tuple[tuple[str, str], ...] = ()` to `NavSourceMetadata`; normalize to tuple in `__post_init__` if a post-init is needed.
- Create/move `_RawNavSourceResult` in `nav_source_contract.py` with explicit fields:
  - `source_id: str | None`
  - `source_url: str | None`
  - `source_query_params: tuple[tuple[str, str], ...]`
  - `source_nav_type: NavType`
  - `source_adjustment_basis: AdjustmentBasis`
- Define `_NavSourceAdapter` Protocol exactly as §4.0.
- Update current Akshare raw source construction to set `source_id=normalized_fund_code`、`source_url=None`、`source_query_params=()`、`source_nav_type="unit_nav"`、`source_adjustment_basis="raw_unit_nav"`，保持 legacy `load_nav_data()` unchanged。
- Update `FundNavDataAdapter.load_raw_nav_source()` signature to accept explicit `share_class/start_date/end_date/force_refresh`; no `**kwargs`。
- Add/update tests:
  - metadata query params are immutable tuple.
  - legacy Akshare raw DTO still reports raw path and cache origin.
  - `load_nav_series` signature still has no `extra_payload` / `**kwargs`.
  - Protocol-compatible fake adapter method signature includes `share_class/start_date/end_date/force_refresh`.

Stop conditions：

- If adding `source_query_params` requires many downstream call-site rewrites outside data/tests/docs, stop and ask controller.

Completion signal：

- Focused tests for NAV contract pass.

### Slice 2 — CSRC EID Source Adapter

Files：

- `fund_agent/fund/data/csrc_eid_nav_source.py`
- `tests/fund/data/test_csrc_eid_nav_source.py`

Exact changes：

- Implement `CsrcEidNavSource` with async public method:
  - `load_raw_nav_source(fund_code: str, *, share_class: str | None = None, start_date: date | None = None, end_date: date | None = None, force_refresh: bool = False) -> _RawNavSourceResult`
- Use `httpx.AsyncClient` because `httpx>=0.28.0` is already a project dependency and document sources already use it; no new dependency.
- Use `httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)` and at most 3 attempts. Retry only timeout/transport/HTTP 5xx; final HTTP/network failure -> `unavailable` with cause.
- Use stdlib `html.parser.HTMLParser` based parser classes for detail/list tables and links. Use `urllib.parse` for query params and limited regex only for pagination numbers.
- Define module-level constants for endpoint paths, classification IDs are not hardcoded as sole truth; they are expected values validated against detail page. Constants may serve as expected mapping for 006597 family tests but production must parse detail page.
- Search flow:
  - For A/C/E, search requested code and require `fundId=5755` for 006597 family.
  - For F, if direct search fails, search product anchor (`006597` or accepted product name) and require detail page contains F code/classification.
- Detail parser:
  - Extract share-class rows/links for A/C/E/F.
  - Verify requested `fund_code` and optional `share_class` agree with parsed mapping.
- Classification parser:
  - Fetch pages with `limit=20`, `start=0,20,...`.
  - Parse total record count and table rows.
  - Stop when fetched rows == total; mismatch -> `integrity_error`.
  - `total=0` after verified identity -> `not_found`.
  - total changes between pages -> `integrity_error`.
  - last page row count must match `total - start`; mismatch -> `integrity_error`.
- Raw output records must include explicit normalized keys for repository:
  - `估值日期`
  - `单位净值`
  - `累计净值`
  - `基金代码`
  - `基金名称`
  - `份额类别`
  - `classification`
  - `source_url`
- Convert HTTP/network failures to `NavDataContractError(category="unavailable", source="csrc_eid")`.
- Convert parser/schema failures to `schema_drift`; identity conflicts to `identity_mismatch`; pagination duplicate/mismatch to `integrity_error`.
- Returned `_RawNavSourceResult` must set `source_nav_type="accumulated_nav"` and `source_adjustment_basis="accumulated_nav"`; repository must not infer CSRC basis from raw field names alone.

Tests / fixtures：

- Use deterministic HTML/JSON fixtures embedded as small strings in tests or under `tests/fixtures/fund/data/csrc_eid/`.
- Cover:
  - normalize success for A.
  - prove A/C/E/F mapping from detail page.
  - F direct-search missing but detail classification succeeds.
  - identity mismatch when requested code/share_class conflict.
  - malformed search/detail/list schema -> `schema_drift`.
  - unavailable HTTP error -> `unavailable`.
  - pagination total mismatch -> `integrity_error`.
  - pagination total 0 -> `not_found`.
  - pagination total changes mid-fetch -> `integrity_error`.
  - last page boundary where `total % limit != 0` succeeds only with exact expected row count.
  - A/C blank accumulated exact fixture rows `2018-12-07` and `2018-12-14`.

Stop conditions：

- If live CSRC EID requires non-public auth, JavaScript execution, random token as state, or endpoint no longer returns machine-readable rows, stop and classify as `unavailable`/`schema_drift` evidence for controller.

Completion signal：

- Source adapter fixture tests pass without network.

### Slice 3 — Repository Normalization to Accumulated Typed Series

Files：

- `fund_agent/fund/data/nav_repository.py`
- `tests/fund/data/test_nav_repository_contract.py`

Exact changes：

- Make default `FundNavRepository()` use `CsrcEidNavSource` for `load_nav_series()`.
- `FundNavRepository.__init__` type becomes `source_adapter: _NavSourceAdapter | None = None`; if `None`, construct `CsrcEidNavSource()`.
- On any CSRC EID classified failure, raise the `NavDataContractError`; do not fallback to Akshare/stock-sdk/Eastmoney.
- Preserve tests with injected `_FakeRawNavAdapter` for raw-unit path by branching on `_RawNavSourceResult.source_nav_type/source_adjustment_basis` and using private normalizer split:
  - `_normalize_raw_unit_series(...)`
  - `_normalize_accumulated_nav_series(...)`
- Pass explicit `share_class/start_date/end_date/force_refresh` from repository to source adapter; no `extra_payload`.
- For CSRC EID accumulated source:
  - parse `累计净值` as record `nav_value` Decimal positive.
  - parse `估值日期` as date.
  - validate `单位净值` separately as Decimal positive for diagnostics and store original value in `raw_payload`; do not use `单位净值` as typed `nav_value`.
  - if `累计净值` is blank, apply missing accumulated handling before validating `单位净值`.
  - if `累计净值` has value but `单位净值` is blank/non-numeric/nonpositive, classify as `schema_drift` for blank/non-numeric and `integrity_error` for nonpositive.
  - set series and record `nav_type="accumulated_nav"` and `adjusted_basis="accumulated_nav"`.
  - set `dividend_adjustment_status="not_applicable"`.
  - set `identity_status="verified"`.
  - set `strong_drawdown_evidence_eligible=True` after model validation when identity and accumulated basis are verified; test and evidence must state this is source-level eligibility only.
  - set `ShareClassMapping.mapping_status="csrc_eid_classification_verified"`.
  - mapping evidence must include `fundId=5755` and classification ID.
  - set `source.source_url/source_id/source_query_params`.
- `_normalize_accumulated_nav_series(...)` must read CSRC-specific fields `估值日期` / `累计净值` directly and must not call `_normalize_raw_record(...)`, because `_normalize_raw_record(...)` is the Akshare raw-unit path that reads `净值日期` / `单位净值` as typed nav value.
- Missing accumulated handling:
  - Drop blank accumulated rows outside requested range and record evidence.
  - Blank accumulated inside requested range -> `missing_date_range`.
  - All accumulated blank -> `adjustment_basis_unknown`.
- Duplicate dates remain model-level `integrity_error`.
- `minimum_records` and requested date constraints use existing `FundNavSeries` validators.
- Raw unit path remains ineligible:
  - Existing injected raw adapter tests must still assert `adjusted_basis="raw_unit_nav"` and `strong_drawdown_evidence_eligible=False`.

Tests：

- CSRC EID fake adapter records normalize to:
  - `nav_type="accumulated_nav"`
  - `adjusted_basis="accumulated_nav"`
  - `identity_status="verified"`
  - `source.source_name="csrc_eid"`
  - `source.source_id="5755:2030-1010"`
  - `record_count`, `date_range_start/end`, `source_query_params` populated.
- A/C/E/F separation:
  - Same product `006597` but requested codes/classes return distinct `fund_code/share_class/source_id/nav_value` series.
  - Conflicting request fails `identity_mismatch`.
- Missing accumulated:
  - blank before requested window dropped.
  - blank inside requested window -> `missing_date_range`.
  - all blank -> `adjustment_basis_unknown`.
- malformed date/value:
  - date -> `schema_drift`
  - nonpositive accumulated -> `integrity_error`
  - nonnumeric accumulated -> `schema_drift`
- raw unit path still ineligible.
- CSRC accumulated path has `strong_drawdown_evidence_eligible is True` while evidence text still says no drawdown metric/no blocker解除.
- `累计净值` present but `单位净值` blank -> `schema_drift`.

Stop conditions：

- If Protocol + explicit `source_nav_type/source_adjustment_basis` still cannot support both CSRC default and injected raw fake without public API redesign, stop and ask controller. Do not add broad `source_options` dict.

Completion signal：

- `uv run pytest tests/fund/data/test_nav_repository_contract.py tests/fund/data/test_csrc_eid_nav_source.py -q` passes.

### Slice 4 — Stock-SDK Rejection Lock Tests

Files：

- `tests/fund/data/test_csrc_eid_nav_source.py` or `tests/fund/data/test_nav_repository_contract.py`

Exact changes：

- Add `test_no_stock_sdk_runtime_dependency`:
  - assert project dependency metadata and `fund_agent.fund.data` source modules do not import `stock-sdk`, `node`, `subprocess`, or package-specific runtime glue.
  - Do not shell out to npm.
- Add `test_stock_sdk_date_shift_classified_as_integrity_error`:
  - fixture contains CSRC reference row `{date: "2023-01-12", nav: "1.1254", acc_nav: "1.1334"}` and stock-sdk-style row exposing the same values under `date="2023-01-11"`.
  - helper/classifier must raise or return `NavDataContractError(category="integrity_error")`.
  - This helper is test-local or diagnostics-only; it must not become a runtime adapter.
- Add `test_dividend_list_cross_check_cannot_construct_fund_nav_series`:
  - a dividend event fixture may be used to verify diagnostics wording, but no `FundNavSeries` can be constructed from dividend-list-only input.

Stop conditions：

- Do not install npm packages or add package files.

Completion signal：

- Tests pass and no project dependency file changed.

### Slice 5 — Docs / Evidence / Real Smoke

Files：

- `docs/design.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-evidence-20260529.md`

Exact docs decisions：

- `docs/design.md`：after implementation, update only current code facts: `FundNavRepository()` currently defaults to CSRC EID accumulated NAV normalization for verified 006597 family share classes, raw-unit legacy injected path remains ineligible, and no drawdown metric / blocker解除 is implemented. Do not write broader design decision wording such as "CSRC EID is the permanent primary source"; controller judgment owns source-strategy decision wording.
- `fund_agent/fund/README.md`：document `FundNavRepository.load_nav_series()` current source behavior, share-class separation, provenance, failure categories.
- `tests/README.md`：document deterministic CSRC EID fixture tests and real smoke as network-dependent evidence only.
- Do not update root README unless CLI/user workflow changes; this plan does not change CLI.

Validation commands：

```bash
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

Real CSRC EID smoke：

- Required at least:
  - `FundNavRepository().load_nav_series("006597", share_class="A", minimum_records=30, force_refresh=True)`
- If feasible in the environment:
  - `006598/C`
  - `014217/E`
  - `022176/F`
- Smoke expected for A:
  - `source.source_name="csrc_eid"`
  - `source_id="5755:2030-1010"`
  - `fund_code="006597"`
  - `share_class="A"`
  - `nav_type="accumulated_nav"`
  - `adjusted_basis="accumulated_nav"`
  - `identity_status="verified"`
  - `record_count >= 30`
  - `date_range_end` close to latest CSRC row available at run time.

Evidence artifact must explicitly state:

- `drawdown_stress blocker remains unresolved`
- No snapshot/score/quality gate/golden changes.
- No stock-sdk runtime source.
- Any network smoke failure category (`unavailable` vs `schema_drift`) and whether it blocks acceptance.

Stop conditions：

- Full tests/ruff fail without a clear local fix.
- Real smoke fails as `schema_drift`, `identity_mismatch`, `integrity_error`, `adjustment_basis_unknown`, `missing_date_range` or `insufficient_records`; controller must classify before acceptance.
- Real smoke `unavailable` may be recorded as environment residual only if deterministic fixture tests fully pass and controller accepts.

Completion signal：

- Full validation passes.
- Evidence artifact written.
- No forbidden files changed.

## 7. Test Matrix

| Area | Test requirement |
|---|---|
| Fixture normalize | CSRC EID A fixture normalizes to accumulated typed series with provenance |
| Share-class identity | Prove 006597=A, 006598=C, 014217=E, 022176=F; no mixed product NAV |
| Identity mismatch | code/share_class conflict and wrong returned code -> `identity_mismatch` |
| Missing accumulated | A/C exact blank fixtures `2018-12-07` and `2018-12-14`; outside-window blank dropped; inside-window blank -> `missing_date_range`; all blank -> `adjustment_basis_unknown` |
| Unit NAV diagnostics | `累计净值` present but `单位净值` blank/non-numeric -> `schema_drift`; nonpositive unit NAV -> `integrity_error`; unit NAV never becomes typed `nav_value` |
| Malformed date/value | bad date -> `schema_drift`; nonnumeric accumulated -> `schema_drift`; nonpositive -> `integrity_error` |
| Unavailable | HTTP/network error -> `unavailable` with cause preserved |
| Pagination integrity | duplicate date / total mismatch / page gap / total changes / last-page boundary mismatch -> `integrity_error`; total 0 after verified identity -> `not_found` |
| Schema drift | missing columns / changed table shape -> `schema_drift` |
| stock-sdk rejected | concrete date-shift fixture remains `integrity_error`; no runtime dependency; dividend-list-only cannot construct `FundNavSeries` |
| raw unit ineligible | existing raw unit path still `strong_drawdown_evidence_eligible=False` |
| CSRC source eligibility | CSRC EID accumulated verified series has `strong_drawdown_evidence_eligible=True` as source-level eligibility only; no metric evidence/score acceptance |
| explicit params | no `extra_payload`, no `**kwargs`, repository passes explicit args to source |
| docs | design/Fund README/tests README reflect current code facts only |

## 8. Validation Matrix

Required local validation:

```bash
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

Required focused validation:

```bash
uv run pytest tests/fund/data/test_nav_repository_contract.py tests/fund/data/test_csrc_eid_nav_source.py -q
```

Required real smoke:

```bash
uv run python - <<'PY'
import asyncio
from fund_agent.fund.data import FundNavRepository

async def main():
    repo = FundNavRepository()
    for code, share_class in (("006597", "A"), ("006598", "C"), ("014217", "E"), ("022176", "F")):
        series = await repo.load_nav_series(
            code,
            share_class=share_class,
            minimum_records=30,
            force_refresh=True,
        )
        print(code, share_class, series.source.source_name, series.source.source_id,
              series.nav_type, series.adjusted_basis, series.identity_status,
              series.strong_drawdown_evidence_eligible,
              series.record_count, series.date_range_start, series.date_range_end)

asyncio.run(main())
PY
```

If A/C/E/F full smoke is blocked by network, minimum acceptance requires at least 006597/A real smoke or controller-approved `unavailable` residual plus deterministic A/C/E/F fixture coverage.

## 9. Review Focus For Reviewers

Reviewers must check:

- CSRC EID source identity uses public search/detail/classification endpoints and does not depend on random `rnd` / `t`.
- A/C/E/F are separated; no product-level NAV mixing.
- `accumulated_nav` is not mislabeled as dividend-adjusted or total-return.
- Provenance fields are explicit and no `extra_payload` / free dict was introduced.
- Failure taxonomy uses existing 8 categories and fail-closed semantics.
- stock-sdk remains evidence-only and date shift is still rejected.
- Repository remains the only consumer boundary; no extractor/source helper bypass.
- Raw unit path remains ineligible.
- CSRC accumulated verified path may be `strong_drawdown_evidence_eligible=True`, and reviewers must verify this is documented as source-level eligibility only, not metric acceptance.
- No drawdown metric, score, snapshot, quality gate, golden, Host/Agent/dayu changes.
- Docs do not claim `drawdown_stress` blocker解除.

## 10. Blocking Questions For Controller

无。

Working assumptions：

- CSRC EID endpoints remain public and machine-readable as accepted on 2026-05-28.
- Adding `NavSourceMetadata.source_query_params` is acceptable within this heavy implementation gate because provenance query params are a required plan decision and taxonomy remains unchanged.
- Default `FundNavRepository.load_nav_series()` becomes CSRC EID accumulated NAV for verified supported share classes; legacy `load_nav_data()` and constructor-injected raw adapter tests preserve raw-unit compatibility.
- `strong_drawdown_evidence_eligible=True` on CSRC accumulated series is a source-level contract result only; a later reviewed drawdown metric gate is still required before `drawdown_stress` can be accepted.

## 11. Completion Signals

Implementation gate can be considered ready for review when:

- All planned slices are implemented.
- Required validations pass or any real-smoke `unavailable` residual is explicitly classified for controller.
- Evidence artifact exists under `docs/reviews/`.
- `git diff --name-only` shows only allowed files.
- Artifact explicitly states `drawdown_stress` blocker remains unresolved.
- No report/snapshot/score/quality/golden fixture was modified.

## 12. Controller Handoff Summary

Artifact path：

`docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-20260529.md`

Recommended next controller action：

- 派 implementation worker 按 Slice 1-5 实现。
- 实现后派至少两份独立 review，重点审查 source identity、share-class separation、provenance、failure taxonomy、no drawdown metric/no blocker解除。
