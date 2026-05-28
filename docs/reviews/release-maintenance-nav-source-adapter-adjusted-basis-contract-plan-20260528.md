# NAV Repository / Source Adapter Adjusted-Basis Contract Plan

日期：2026-05-28

角色：Gateflow worker

Gate：`NAV repository/source adapter adjusted-basis contract gate`

计划状态：`handoff-ready for next implementation gate`，但当前 gate 结论为 `blocked-with-contract-gap`

## 1. Scope Self-Check

- Current gate / role：当前是 primer / plan / contract evidence 产出；我是 worker，不是 controller。
- Source of truth：已读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、两个 controller judgment、最新 006597 snapshot / score / quality gate、006597 2024/2025 年报 repository smoke、当前 `FundNavDataAdapter` public smoke。
- Scope boundary：只新增 `docs/reviews/` artifact；不修改 Python、schema、score、quality gate、golden fixture、release、PR。
- Stop conditions：当前 adapter contract gap 已确认；不得进入 implementation 或解除 `drawdown_stress` blocker。
- Evidence and validation：完成三份 artifact，记录命令和事实；不跑 full ruff / pytest，因为无生产代码变更。
- Next action：停止，交 controller review；下一步只能由 controller 授权 source adapter implementation gate。

## 2. Goal

定义一个 typed Fund-layer NAV repository/source adapter contract，使未来 `drawdown_stress` derived evidence 只消费可证明 share-class、adjusted-basis、provenance、identity 和 failure semantics 的 NAV series。

本 plan 不接受当前 raw NAV 作为 strong drawdown evidence。当前结论为：

`blocked-with-contract-gap`

## 3. Non-Goals

- 不解除 `drawdown_stress` blocker。
- 不把“控制回撤”升级为 quantitative。
- 不把 A/C/E/F 多份额 NAV 混算。
- 不用 E 类有分红期间 raw unit NAV 直接算 strong drawdown。
- 不修改 `bond_risk_evidence` schema / score policy / quality gate / golden fixture。
- 不削弱 FQ0-FQ6。
- 不绕过统一 NAV adapter/repository。
- 不做 QDII、FOF、110020、golden readiness、release、Host-Agent-dayu。
- 不把显式参数塞进 `extra_payload`。

## 4. Ownership / Boundary Decision

稳定 contract 放在 Agent/Fund NAV repository/source adapter 层：

- 建议路径：`fund_agent/fund/data/nav_repository.py` 或在 `fund_agent/fund/data/nav_data.py` 内引入 typed models 后再拆分。
- Service、quality gate、score、renderer 只能消费公开 Fund-layer result，不直接调用 source helper、akshare、sqlite、PDF cache。
- 未来 derived drawdown implementation 只能消费 accepted NAV contract result，不读取具体 provider 返回字段。

原因：

- NAV path 是基金领域数据能力，不是 UI / Service / Host 生命周期能力。
- `drawdown_stress` 属于 Agent/Fund 风险证据，不应由 Service 或 quality gate 发明 source semantics。
- 当前 repository 规则已经要求年报通过 `FundDocumentRepository`；NAV 也应有等价 repository/adapter 公开契约。

## 5. Proposed Public Contract

### 5.1 Enum

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

NavIdentityStatus = Literal[
    "verified",
    "source_unverified",
    "identity_mismatch",
]

NavFailureCategory = Literal[
    "not_found",
    "unavailable",
    "schema_drift",
    "identity_mismatch",
    "integrity_error",
    "adjustment_basis_unknown",
    "insufficient_history",
]
```

### 5.2 Result Model

```python
@dataclass(frozen=True, slots=True)
class FundNavSeriesResult:
    fund_code: str
    share_class: str
    fund_code_mapping: NavFundCodeMapping
    records: tuple[FundNavRecord, ...]
    metadata: FundNavSeriesMetadata
    unavailable: bool = False
    unavailable_reason: str | None = None
```

### 5.3 Record Model

```python
@dataclass(frozen=True, slots=True)
class FundNavRecord:
    nav_date: date
    nav_value: Decimal
    nav_type: NavType
    adjustment_basis: AdjustmentBasis
    daily_return: Decimal | None = None
    source_payload: Mapping[str, object] = field(default_factory=dict)
```

`source_payload` 只能承载 diagnostic source echo，不得作为业务显式参数通道；业务参数必须是 typed fields。

### 5.4 Metadata Model

```python
@dataclass(frozen=True, slots=True)
class FundNavSeriesMetadata:
    source_name: str
    source_url: str | None
    source_id: str | None
    retrieved_at: datetime | None
    fund_code: str
    source_returned_fund_code: str | None
    share_class: str
    fund_code_mapping: NavFundCodeMapping
    date_range: NavDateRange
    record_count: int
    nav_type: NavType
    adjustment_basis: AdjustmentBasis
    identity_status: NavIdentityStatus
    failure_category: NavFailureCategory | None
    cached: bool
    cache_updated_at: datetime | None
    completeness_status: Literal["complete", "partial", "unknown"]
    dividend_adjustment_status: Literal[
        "not_applicable_no_distributions",
        "provider_adjusted",
        "derived_adjusted",
        "known_unadjusted",
        "unknown",
    ]
```

Decision point：

- `dividend_adjustment_status` 应作为 independent field，而不是塞入 `adjustment_basis`。
- `adjustment_basis` 描述序列数值口径。
- `dividend_adjustment_status` 描述分红事件处理证明状态。
- 两者都必须存在，避免 `accumulated_nav` 被误读为 total-return。

### 5.5 Fund Code / Share-Class Mapping

```python
@dataclass(frozen=True, slots=True)
class NavFundCodeMapping:
    requested_fund_code: str
    product_main_code: str
    share_class: str
    share_class_code: str
    mapping_source: Literal[
        "annual_report_section_2",
        "provider_identity",
        "explicit_request",
    ]
    mapping_evidence: tuple[EvidenceAnchor, ...]
```

006597 mapping rule：

- 请求 `006597` 默认是 A 类，产品主代码也是 `006597`。
- C / E / F 必须显式传入份额类别或份额代码：C `006598`，E `014217`，F `022176`。mapping 应由年报 §2 或 provider identity 验证。
- 产品层面报告可展示 share-class range / worst，但 calculator 不能混合序列。

## 6. Max Drawdown Eligibility Matrix

| adjustment_basis | 可否用于 max drawdown strong evidence | 条件 |
|---|---:|---|
| `total_return` | 是 | provider 或本项目 derivation 已明确分红再投资 / total-return 口径；identity verified；share_class verified；date_range 和 record_count 足够；failure_category 为 null |
| `dividend_adjusted_nav` | 是 | 明确分红、拆分、折算已调整；记录 path 足够；可追溯 source / calculation metadata |
| `accumulated_nav` | 有条件 | 只能作为 candidate；需明确 provider 累计净值 path 的分红处理与回撤含义；不能默认为 total-return |
| `raw_unit_nav` | 通常 weak / blocked | 仅当目标期间通过 §3.3 或事件源证明无分红、拆分、折算，且 share-class / identity / basis verified 时可 limited use；否则 fail-closed |
| `unknown` | 否 | `adjustment_basis_unknown` fail-closed |

## 7. Failure Taxonomy

| failure_category | 处理 |
|---|---|
| `not_found` | 可重试或 fallback |
| `unavailable` | 可重试或 fallback |
| `schema_drift` | fail-closed；不得 fallback 静默掩盖 |
| `identity_mismatch` | fail-closed；不得 fallback 静默掩盖 |
| `integrity_error` | fail-closed；不得 fallback 静默掩盖 |
| `adjustment_basis_unknown` | fail-closed；不得用于 drawdown strong evidence |
| `insufficient_history` | fail-closed for max drawdown；可用于普通展示 |

与年报 source taxonomy 对齐：eligible failure 可以 fallback，contract / identity / integrity / basis 问题必须 fail-closed。

## 8. Required Implementation Slices For Next Gate

### Slice 1: typed model / repository boundary

Files likely affected:

- `fund_agent/fund/data/nav_data.py`
- 新增 `fund_agent/fund/data/nav_repository.py` 或 `fund_agent/fund/data/nav_models.py`
- `fund_agent/fund/data/__init__.py`
- `tests/fund/data/test_nav_data.py`
- 新增 `tests/fund/data/test_nav_repository_contract.py`

Implementation:

- 引入 typed result / record / metadata。
- 保留 current `NavDataResult` 兼容路径，或在明确 migration gate 中替换。
- 不变更 score / quality gate / snapshot schema。

### Slice 2: current adapter explicit raw-basis classification

Implementation:

- 当前 akshare `单位净值走势` provider 必须显式输出 `nav_type="unit_nav"`、`adjustment_basis="raw_unit_nav"`。
- cache hit 必须通过 public result 暴露 origin source、cache updated_at、retrieved_at / cache_updated_at。不能要求消费者读 sqlite internals。
- 如果 source 返回字段没有 share_class / identity / adjusted basis，只能标记 `source_unverified` 或 `adjustment_basis_unknown`，不得假装 verified。

### Slice 3: share-class mapping using annual-report evidence

Implementation:

- 通过 `FundDocumentRepository` 读取 §2 share-class code mapping，不直接读 PDF/cache。
- `requested_fund_code=006597` 映射 A 类；C/E/F 通过显式 share-class code 或 request 参数选择。
- 多份额类别返回 separate series，不返回混合 records。

### Slice 4: provider extension research / adapter

Implementation only if source can prove adjusted basis:

- 查找并接入能公开提供累计净值、复权净值、total-return 或分红调整序列的方法。
- 如果 provider 不能提供 methodology / identity / basis，则 gate 继续 blocked。
- 禁止用当前 raw unit NAV 加年报端点拼接伪 total-return series。

### Slice 5: tests and documentation

Tests:

- raw unit NAV 不满足 strong drawdown eligibility。
- `adjustment_basis_unknown` fail-closed。
- E 类 2023 分红跨期 raw unit NAV fail-closed。
- A/C/E/F mapping 分离。
- cache-hit metadata 从 public adapter result 可见。
- not_found/unavailable 可 fallback；schema_drift/identity_mismatch/integrity_error/adjustment_basis_unknown fail-closed。

Docs:

- 修改 `fund_agent/fund/README.md`，只写当前 Fund NAV contract。
- 如改动 `fund_agent/fund/data/` 行为，更新 README 后再跑 tests。

## 9. Validation Matrix For Next Implementation Gate

Minimum:

- `uv run ruff check fund_agent/fund/data tests/fund/data`
- `uv run pytest tests/fund/data/test_nav_data.py tests/fund/data/test_nav_repository_contract.py`
- public smoke: `FundNavDataAdapter.load_nav_data("006597")` 或新 repository method，不读 sqlite/cache internals。
- repository smoke: `FundDocumentRepository.load_annual_report("006597", 2025)` 验证 share-class mapping / §3.3 分红证据。

Only if code touches extractor / snapshot integration:

- `uv run pytest tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py`
- real 006597 snapshot / score / quality gate rerun as diagnostic only，不解除 blocker。

## 10. Completion Criteria

Next implementation gate 可接受的完成信号：

- public NAV contract 明确返回 source_name、source_url/source_id、retrieved_at/cache_updated_at、fund_code、share_class、fund_code mapping、date_range、record_count、nav_type、adjustment_basis、identity_status、failure_category、dividend_adjustment_status。
- 当前 raw provider 被明确分类为 raw / ineligible 或 limited eligible，而不是误认为 adjusted。
- 如果没有 adjusted / cumulative / total-return provider，gate 必须继续 `blocked-with-contract-gap`。
- 不改变 `drawdown_stress` 状态、不改变 score / quality gate / golden。

## 11. Open Questions For Controller Review

1. 是否接受 `dividend_adjustment_status` 作为独立 metadata 字段，而不是纳入 `adjustment_basis` enum？
2. 下一 implementation gate 是否只允许先做 raw-basis typed contract + fail-closed metadata，还是允许并行 research 一个 adjusted provider？
3. 若无法找到 provider-level adjusted / total-return methodology，是否接受将后续工作拆成 dividend-event repository / local total-return derivation research gate，而不是继续 source adapter gate？
