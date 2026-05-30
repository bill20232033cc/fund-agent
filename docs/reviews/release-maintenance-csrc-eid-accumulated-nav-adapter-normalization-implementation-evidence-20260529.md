# CSRC EID Accumulated NAV Adapter Normalization Implementation Evidence

日期：2026-05-29  
角色：implementation worker  
Gate：`CSRC EID accumulated NAV adapter normalization implementation gate`  
Accepted plan commit：`6dce229`

## 1. Scope

已按 accepted plan 实施 Slice 1-5，仅修改允许范围内的 Fund data、tests/docs 和本 evidence artifact。

未执行 controller/reviewer 工作；未 commit、push、PR、merge、release 或 golden promotion。

## 2. Changed Files

Production:

- `fund_agent/fund/data/nav_source_contract.py`
- `fund_agent/fund/data/nav_models.py`
- `fund_agent/fund/data/nav_data.py`
- `fund_agent/fund/data/csrc_eid_nav_source.py`
- `fund_agent/fund/data/nav_repository.py`

Tests/docs:

- `tests/fund/data/test_nav_repository_contract.py`
- `tests/fund/data/test_csrc_eid_nav_source.py`
- `tests/fund/data/test_nav_data.py`
- `docs/design.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-evidence-20260529.md`

未修改 bond extractor、score、snapshot、quality gate、golden、Service/UI、Host/Agent/dayu 或 reports artifacts。

## 3. Implementation Summary

- 新增 `nav_source_contract.py`，定义 `_NavSourceAdapter` Protocol 和 `_RawNavSourceResult` DTO。DTO 显式包含 `source_query_params`、`source_nav_type`、`source_adjustment_basis`，未使用 `extra_payload`、`**kwargs` 或 source options dict。
- `NavSourceMetadata` 增加 `source_query_params` 显式 provenance 字段，并规范化为 tuple。
- `FundNavDataAdapter.load_raw_nav_source()` 实现 Protocol-compatible 显式参数 `share_class/start_date/end_date/force_refresh`，legacy `load_nav_data()` 行为不变；raw-unit DTO 固定返回 `unit_nav/raw_unit_nav`。
- 新增 `CsrcEidNavSource`，使用 `httpx.AsyncClient`、显式 timeout/retry policy、stdlib `html.parser` parser，按 CSRC EID public search/detail/classification endpoints 解析 006597 家族 A/C/E/F 分类 NAV。未依赖 `rnd` / `t` 随机参数。
- `FundNavRepository()` 无参默认使用 `CsrcEidNavSource()`；CSRC classified failures 不 fallback 到 Akshare、stock-sdk、Eastmoney 或 product-level mixed source。constructor injection 保留 raw-unit tests/compatibility。
- repository 依据 `_RawNavSourceResult.source_nav_type/source_adjustment_basis` 分支：
  - `unit_nav/raw_unit_nav` -> legacy raw-unit normalizer，`strong_drawdown_evidence_eligible=False`
  - `accumulated_nav/accumulated_nav` -> CSRC accumulated normalizer，直接读取 `估值日期` 与 `累计净值`
- CSRC accumulated series 输出 `nav_type="accumulated_nav"`、`adjusted_basis="accumulated_nav"`、`dividend_adjustment_status="not_applicable"`、`identity_status="verified"`。`单位净值` 只做 diagnostics/raw_payload 验证，不作为 typed `nav_value`。
- A/C/E/F identity 固定验证为：
  - `006597=A/2030-1010`
  - `006598=C/2030-1020`
  - `014217=E/2030-1040`
  - `022176=F/2030-1050`
- F direct-search missing 只允许在 detail classification 验证成功后通过；A/C/E/F 不混合成 product-level NAV。
- stock-sdk runtime 保持拒绝：未新增 Node/npm/subprocess dependency；测试保留 date-shift `integrity_error` 与 dividend-list-only 不能构造 NAV series。

## 4. Validation

Focused validation:

```text
uv run ruff check fund_agent/fund/data/nav_source_contract.py fund_agent/fund/data/nav_models.py fund_agent/fund/data/nav_data.py fund_agent/fund/data/csrc_eid_nav_source.py fund_agent/fund/data/nav_repository.py tests/fund/data/test_nav_repository_contract.py tests/fund/data/test_csrc_eid_nav_source.py tests/fund/data/test_nav_data.py
All checks passed!

uv run pytest tests/fund/data/test_nav_repository_contract.py tests/fund/data/test_csrc_eid_nav_source.py tests/fund/data/test_nav_data.py -q
64 passed in 0.12s
```

Required full validation:

```text
uv run ruff check .
All checks passed!

uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
925 passed in 4.61s
TOTAL coverage: 92.37%
Required test coverage of 50% reached.
```

## 5. Real CSRC EID Smoke

命令通过 `FundNavRepository()` 默认 source 路径执行，`force_refresh=True`，未使用 Akshare/stock-sdk/Eastmoney fallback。

```json
[
  {
    "code": "006597",
    "share_class": "A",
    "source": "csrc_eid",
    "source_id": "5755:2030-1010",
    "nav_type": "accumulated_nav",
    "adjusted_basis": "accumulated_nav",
    "identity_status": "verified",
    "strong_drawdown_evidence_eligible": true,
    "record_count": 1807,
    "date_range_start": "2018-12-18",
    "date_range_end": "2026-05-28"
  },
  {
    "code": "006598",
    "share_class": "C",
    "source": "csrc_eid",
    "source_id": "5755:2030-1020",
    "nav_type": "accumulated_nav",
    "adjusted_basis": "accumulated_nav",
    "identity_status": "verified",
    "strong_drawdown_evidence_eligible": true,
    "record_count": 1807,
    "date_range_start": "2018-12-18",
    "date_range_end": "2026-05-28"
  },
  {
    "code": "014217",
    "share_class": "E",
    "source": "csrc_eid",
    "source_id": "5755:2030-1040",
    "nav_type": "accumulated_nav",
    "adjusted_basis": "accumulated_nav",
    "identity_status": "verified",
    "strong_drawdown_evidence_eligible": true,
    "record_count": 994,
    "date_range_start": "2022-04-25",
    "date_range_end": "2026-05-28"
  },
  {
    "code": "022176",
    "share_class": "F",
    "source": "csrc_eid",
    "source_id": "5755:2030-1050",
    "nav_type": "accumulated_nav",
    "adjusted_basis": "accumulated_nav",
    "identity_status": "verified",
    "strong_drawdown_evidence_eligible": true,
    "record_count": 398,
    "date_range_start": "2024-10-08",
    "date_range_end": "2026-05-28"
  }
]
```

Provenance notes:

- A/C earliest successful typed dates are `2018-12-18` after repository drops blank accumulated rows outside the requested window; deterministic tests cover exact blank rows `2018-12-07` and `2018-12-14`.
- F starts at `2024-10-08`, consistent with accepted F source-inception-forward limitation.
- Smoke only proves CSRC EID accumulated source identity and basis through the typed boundary.

## 6. Residuals / Non-Goals Preserved

- `drawdown_stress blocker remains unresolved`。
- 本 gate 未实现 max drawdown、volatility、drawdown_stress metric、risk scoring policy 或 reviewed metric contract。
- 未修改 bond extractor、snapshot、score、quality gate、golden fixture、Service/UI、Host/Agent/dayu。
- CSRC accumulated path 的 `strong_drawdown_evidence_eligible=True` 仅是 source-level eligibility，不是 metric evidence acceptance，不改变 `bond_risk_evidence.v1`，不解除 score/quality gate blocker。
- 未新增 stock-sdk runtime source；stock-sdk 仍是 evidence-only，date-shift 仍按 `integrity_error` 拒绝。
