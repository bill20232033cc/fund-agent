# CSRC EID Accumulated NAV Adapter Normalization — Aggregate Deepreview

日期：2026-05-29
角色：aggregate deepreview worker（MiMo）
Gate：`CSRC EID accumulated NAV adapter normalization implementation gate`
Gate classification：`heavy`
Review base：commit `73da81b`
Review range：`73da81b..HEAD`（含 plan artifacts 和 accepted implementation commit `537d252`）

---

## 0. Scope 与规则复述

### 0.1 规则真源

- `AGENTS.md` 是本仓库所有 Agent 执行规则的唯一权威入口。
- 当前目标架构固定为 `UI -> Service -> Host -> Agent`。
- `docs/design.md` 是设计真源，`docs/implementation-control.md` 是实施总控。
- 本 review 是 aggregate deepreview worker，不是 controller/implementation/fix。不修改文件、commit、push、PR、merge、release 或 golden promotion。

### 0.2 Review 输入

已读取：
- `AGENTS.md`
- `docs/design.md`（当前设计章节）
- `docs/implementation-control.md`（Startup Packet、Current Gate、Next Entry Point）
- Accepted plan：`docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-20260529.md`
- Plan fix：`docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-fix-20260529.md`
- Plan reviews：MiMo/GLM（初审 + rereview）
- Implementation evidence：`docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-evidence-20260529.md`
- Implementation reviews：MiMo/GLM
- Full diff `73da81b..HEAD`（20 files changed, 4739 insertions, 104 deletions）
- Production code：`nav_source_contract.py`、`nav_models.py`、`nav_data.py`、`csrc_eid_nav_source.py`、`nav_repository.py`
- Tests：`test_nav_repository_contract.py`、`test_csrc_eid_nav_source.py`、`test_nav_data.py`
- Docs：`docs/design.md`、`fund_agent/fund/README.md`、`tests/README.md`

---

## 1. 前序 Plan Review Findings 关闭状态

### 1.1 MiMo Plan Review F1-F10

| Finding | Severity | Disposition | 真关闭验证 |
|---|---|---|---|
| F1 Repository Source Selection Mechanism 未定义 | blocking | Closed | `nav_source_contract.py` 定义 `_NavSourceAdapter` Protocol；`nav_repository.py:75-88` 实现 `source_adapter: _NavSourceAdapter \| None = None`，默认 `CsrcEidNavSource()` |
| F2 `_RawNavSourceResult` 与 CSRC EID DTO 类型不兼容 | blocking | Closed | `nav_source_contract.py` 定义统一 DTO 含 `source_nav_type`/`source_adjustment_basis` required fields；`nav_repository.py:162-196` 按 explicit pair 分支 |
| F3 `strong_drawdown_evidence_eligible` 状态语义冲突 | blocking | Closed (Option A) | `nav_repository.py:402` CSRC verified → `True`；docs/evidence 多处明确 "仅 source-level eligibility，不产生 drawdown metric，不解除 blocker" |
| F4 Sync/async 和 HTTP client 选择未对齐 | blocking | Closed | `csrc_eid_nav_source.py:246` `load_raw_nav_source` 是 async；使用 `httpx.AsyncClient` |
| F5 HTML 解析依赖未声明 | non-blocking | Closed | `csrc_eid_nav_source.py:107` `_TableParser(HTMLParser)` 使用 stdlib |
| F6 HTTP 超时/重试策略未定义 | non-blocking | Closed | `csrc_eid_nav_source.py:35-40` timeout policy；`csrc_eid_nav_source.py:517-547` retry policy（3 attempts, timeout/transport/5xx） |
| F7 Pagination Error Handling 缺少具体场景覆盖 | non-blocking | Closed | `csrc_eid_nav_source.py:438-475` 覆盖 total=0、total changes、last page boundary mismatch |
| F8 `strong_drawdown_evidence_eligible` 测试缺失 | non-blocking | Closed | `test_nav_repository_contract.py` 含 CSRC source eligibility 断言 |
| F9 stock-sdk Rejection Test 方式模糊 | non-blocking | Closed | 三个具体测试：no runtime dependency、date-shift integrity_error、dividend-list-only |
| F10 docs/design.md 更新范围需对齐真源规范 | non-blocking | Closed | `docs/design.md` diff 只写当前代码事实，不宣称 drawdown metric 或 permanent primary source |

### 1.2 GLM Plan Review R1-R2 / N1-N4

| Finding | Severity | Disposition | 真关闭验证 |
|---|---|---|---|
| R1 Source adapter Protocol / type contract 未定义 | required | Closed | `nav_source_contract.py` 定义完整 Protocol 和 DTO |
| R2 Repository source selection mechanism 未明确 | required | Closed | `nav_repository.py:88` 默认 `CsrcEidNavSource()`，no fallback |
| N1 `source_nav_type`/`source_adjustment_basis` 为 deferred choice | non-blocking | Closed | 改为 required fields，repository 按 explicit pair 分支 |
| N2 HTTP client 和 HTML parser 选择未指定 | non-blocking | Closed | `httpx.AsyncClient` + stdlib `html.parser` |
| N3 A/C blank accumulated NAV 日期集合未完全枚举 | non-blocking | Closed | tests 覆盖 `2018-12-07` 和 `2018-12-14` exact blank rows |
| N4 `单位净值` blank 处理语义需明确 | non-blocking | Closed | `_validate_csrc_unit_nav_diagnostics` 明确 blank/non-numeric → `schema_drift`，nonpositive → `integrity_error` |

**结论**：所有前序 plan review findings 均已真关闭。Plan fix 和 rereview 确认 plan 达到 code-generation-ready 状态。

---

## 2. Implementation Review Residual 分析

### 2.1 MiMo Implementation Review Residuals

| Residual | Severity | 是否可接受 | 分析 |
|---|---|---|---|
| `force_refresh` 出现在 `source_query_params` 中 | low | 可接受 | 语义略有偏差但不影响功能正确性；future consumer 不会误用为可重放 HTTP 参数 |
| `_parse_share_class_from_text` 正则依赖 detail 页特定格式 | low | 可接受 | fail-closed 行为正确；`schema_drift`/`identity_mismatch` 覆盖页面格式变化 |
| `_EXPECTED_SHARE_CLASSES` 硬编码常量 | low | 可接受 | 当前 gate 范围只覆盖 006597 家族，hardcoded 是 accepted design decision |
| `drawdown_stress` blocker 仍未解除 | expected | 可接受 | 本 gate 只实现 source-level eligibility，后续需要 reviewed drawdown metric gate |

### 2.2 GLM Implementation Review Residuals

| Residual | Severity | 是否可接受 | 分析 |
|---|---|---|---|
| CSRC EID endpoint 可用性 | low | 可接受 | 依赖公开 HTTP endpoint，endpoint 变化会触发 fail-closed |
| 006597 家族硬编码 | low | 可接受 | 当前 scope 正确限定为单家族 |
| F direct-search 回退路径硬编码 | low | 可接受 | 当前 scope 内可接受 |
| 重复日期检测缺失 | low | 可接受 | 应在后续 model-level invariant gate 中统一补强 |
| `source_query_params` 语义混合 | low | 可接受 | 与 MiMo F1 一致 |
| `drawdown_stress` blocker 未解除 | expected | 可接受 | 与 MiMo 一致 |

**结论**：所有 residual risks 均为 low severity 或 expected（drawdown_stress blocker）。无 blocking residual。

---

## 3. 新 CSRC EID Source Adapter 跨文件风险分析

### 3.1 Identity 验证

| 检查项 | 结果 | 文件/行号 |
|---|---|---|
| Search endpoint `POST /fund/disclose/validate_fund.do` | ✅ | `csrc_eid_nav_source.py:362-367` |
| Detail endpoint `GET /fund/disclose/fund_detail_search.do` | ✅ | `csrc_eid_nav_source.py:275-279` |
| Classification endpoint `GET /fund/disclose/list_net_classification.do` | ✅ | `csrc_eid_nav_source.py:427` |
| fundId=5755 双重验证（search + detail） | ✅ | `csrc_eid_nav_source.py:382-388` |
| A/C/E/F 分份额独立输出 | ✅ | `_select_share_class` 验证 |
| F direct-search gap fail-closed | ✅ | `csrc_eid_nav_source.py:370-381` |
| 不依赖随机 `rnd`/`t` 参数 | ✅ | 无 `rnd`/`t` 出现 |

### 3.2 Pagination

| 检查项 | 结果 | 文件/行号 |
|---|---|---|
| total=0 → `not_found` | ✅ | `csrc_eid_nav_source.py:438-443` |
| total changes mid-fetch → `integrity_error` | ✅ | `csrc_eid_nav_source.py:444-449` |
| last page boundary mismatch → `integrity_error` | ✅ | `csrc_eid_nav_source.py:459-464` |
| 总 row 数与 total 一致性 | ✅ | `csrc_eid_nav_source.py:470-475` |

### 3.3 Parser

| 检查项 | 结果 |
|---|---|
| stdlib `html.parser.HTMLParser` | ✅ |
| 无 BeautifulSoup/lxml 依赖 | ✅ |
| `_find_header_index` 验证必需表头 | ✅ |

### 3.4 Fail-Closed

| 检查项 | 结果 |
|---|---|
| 8 类 failure taxonomy 正确使用 | ✅ |
| 未新增 taxonomy | ✅ |
| classified errors 直接传播，不 fallback | ✅ |

### 3.5 Source Query Params

| 检查项 | 结果 |
|---|---|
| 显式包含 `fundCode`/`classification`/`limit`/`start` 等 HTTP 参数 | ✅ |
| `source_query_params` 规范化为 tuple | ✅ |
| `force_refresh` 混入（residual，non-blocking） | ⚠️ low |

### 3.6 HTTP Retry

| 检查项 | 结果 | 文件/行号 |
|---|---|---|
| `httpx.Timeout(connect=10, read=30, write=10, pool=10)` | ✅ | `csrc_eid_nav_source.py:35-40` |
| 最多 3 次尝试（initial + 2 retries） | ✅ | `csrc_eid_nav_source.py:97` |
| 重试范围：timeout/transport/5xx | ✅ | `csrc_eid_nav_source.py:517-547` |
| 4xx 不重试 | ✅ | 非 5xx 直接 raise |
| 最终失败 `unavailable` + cause preserved | ✅ | |

**结论**：CSRC EID source adapter 的 identity/pagination/parser/fail-closed/source_query_params/HTTP retry 实现正确，无跨文件风险。

---

## 4. Typed Contract 与 Repository 一致性

### 4.1 Default Source / No Fallback

| 检查项 | 结果 |
|---|---|
| `FundNavRepository()` 无参默认 `CsrcEidNavSource()` | ✅ `nav_repository.py:88` |
| CSRC classified failure 直接上抛，无 fallback | ✅ |
| constructor injection 保留 raw-unit tests/compatibility | ✅ |

### 4.2 Source Nav Type / Adjustment Basis Branching

| 检查项 | 结果 |
|---|---|
| `("unit_nav", "raw_unit_nav")` → `_normalize_raw_unit_series` | ✅ `nav_repository.py:162-174` |
| `("accumulated_nav", "accumulated_nav")` → `_normalize_accumulated_nav_series` | ✅ `nav_repository.py:175-187` |
| 其他组合 → `adjustment_basis_unknown` | ✅ `nav_repository.py:188-196` |

### 4.3 Raw-Unit Compatibility

| 检查项 | 结果 |
|---|---|
| `FundNavDataAdapter.load_raw_nav_source()` Protocol-compatible | ✅ |
| `load_nav_data()` 行为不变 | ✅ |
| raw-unit → `strong_drawdown_evidence_eligible=False` | ✅ `nav_repository.py:294` |

### 4.4 CSRC Accumulated Normalization

| 检查项 | 结果 |
|---|---|
| 直接读 `估值日期`/`累计净值`，不复用 `_normalize_raw_record` | ✅ |
| `单位净值` 只 diagnostics，不作为 `nav_value` | ✅ |
| `nav_type="accumulated_nav"` / `adjusted_basis="accumulated_nav"` | ✅ |
| `dividend_adjustment_status="not_applicable"` | ✅ |
| `identity_status="verified"` | ✅ |
| `strong_drawdown_evidence_eligible=True`（source-level only） | ✅ |

**结论**：typed contract 与 repository default source/no fallback/raw-unit compatibility 完全一致。

---

## 5. `strong_drawdown_evidence_eligible=True` 误用风险分析

### 5.1 语义边界检查

| 检查项 | 结果 |
|---|---|
| `strong_drawdown_evidence_eligible=True` 只表示 source-level eligibility | ✅ `nav_repository.py:402` + docs |
| 不产生 drawdown metric | ✅ 未实现 drawdown metric |
| 不构成 `drawdown_stress` evidence acceptance | ✅ |
| 不解除 `drawdown_stress` blocker | ✅ |
| bond extractor 未修改 | ✅ diff 无 `bond_risk_evidence.py` |
| score 未修改 | ✅ diff 无 `extraction_score.py` |
| snapshot 未修改 | ✅ diff 无 `extraction_snapshot.py` |
| quality gate 未修改 | ✅ diff 无 `quality_gate.py` |
| golden 未修改 | ✅ diff 无 `golden_*.py` |

### 5.2 Consumer 误用路径分析

| 潜在误用路径 | 是否存在 | 分析 |
|---|---|---|
| `strong_drawdown_evidence_eligible=True` → 自动解除 `drawdown_stress` blocker | ❌ 不存在 | bond extractor / score / snapshot / quality gate 均未修改 |
| `strong_drawdown_evidence_eligible=True` → 自动接受 drawdown metric evidence | ❌ 不存在 | 当前未实现 drawdown metric |
| `strong_drawdown_evidence_eligible=True` → 改变 `bond_risk_evidence.v1` | ❌ 不存在 | diff 无 bond extractor 修改 |
| future consumer 误读为 metric evidence | ⚠️ 潜在 | docs 多处明确说明 "仅 source-level eligibility"；需在 reviewed metric gate 时再次验证 |

**结论**：当前没有任何路径会把 `strong_drawdown_evidence_eligible=True` 误用成 `drawdown_stress` blocker解除。docs 多处明确语义边界。

---

## 6. 边界合规检查

### 6.1 禁止越界修改

| 检查项 | 结果 |
|---|---|
| 未修改 extractor（`extractors/`） | ✅ |
| 未修改 score（`extraction_score.py`） | ✅ |
| 未修改 snapshot（`extraction_snapshot.py`） | ✅ |
| 未修改 quality gate（`quality_gate.py`） | ✅ |
| 未修改 golden（`golden_*.py`） | ✅ |
| 未修改 Service/UI（`services/`、`ui/`） | ✅ |
| 未修改 Host/Agent/dayu | ✅ |
| 未修改 reports artifacts | ✅ |
| 未引入 stock-sdk runtime dependency | ✅ |
| 未引入 Node/npm/subprocess | ✅ |
| 未引入 Eastmoney fallback | ✅ |

### 6.2 允许修改文件

| 文件 | 是否在允许范围 |
|---|---|
| `fund_agent/fund/data/nav_source_contract.py`（新增） | ✅ |
| `fund_agent/fund/data/nav_models.py` | ✅ |
| `fund_agent/fund/data/nav_data.py` | ✅ |
| `fund_agent/fund/data/csrc_eid_nav_source.py`（新增） | ✅ |
| `fund_agent/fund/data/nav_repository.py` | ✅ |
| `tests/fund/data/test_nav_repository_contract.py` | ✅ |
| `tests/fund/data/test_csrc_eid_nav_source.py`（新增） | ✅ |
| `tests/fund/data/test_nav_data.py` | ✅ |
| `docs/design.md` | ✅ |
| `fund_agent/fund/README.md` | ✅ |
| `tests/README.md` | ✅ |
| `docs/reviews/` artifacts | ✅ |

**结论**：无越界修改。所有修改均在 Fund data 层允许范围内。

---

## 7. Docs/Design/Control Truth 对齐检查

### 7.1 `docs/design.md` 更新

| 检查项 | 结果 |
|---|---|
| 只写当前代码事实 | ✅ |
| 不宣称 drawdown metric 已完成 | ✅ |
| 不宣称 permanent primary source | ✅ |
| 不宣称 `drawdown_stress` blocker解除 | ✅ |
| 准确描述 CSRC EID default path | ✅ |
| 准确描述 legacy Akshare 兼容 | ✅ |

### 7.2 `docs/implementation-control.md` 对齐

| 检查项 | 结果 |
|---|---|
| Next entry point 仍为 drawdown metric gate | ✅ |
| `drawdown_stress` blocker 仍标记为未解除 | ✅ |
| 未提前宣称 readiness | ✅ |

### 7.3 `fund_agent/fund/README.md` 更新

| 检查项 | 结果 |
|---|---|
| 准确描述 source adapter 行为 | ✅ |
| 准确描述份额分离 | ✅ |
| 准确描述 provenance | ✅ |
| 不宣称 blocker解除 | ✅ |

**结论**：docs/design/control truth 均未提前宣称 metric/golden/readiness。

---

## 8. Validations 与 Real Smoke Evidence

### 8.1 静态验证

| 验证项 | 结果 |
|---|---|
| `ruff check .` | ✅ All checks passed |
| Full pytest | ✅ 925 passed, 92.37% coverage |
| Focused pytest（data 层） | ✅ 64 passed |

### 8.2 Real CSRC EID Smoke

| 份额 | source | source_id | nav_type | adjusted_basis | identity_status | strong_drawdown_evidence_eligible | record_count | date_range |
|---|---|---|---|---|---|---|---|---|
| A (006597) | csrc_eid | 5755:2030-1010 | accumulated_nav | accumulated_nav | verified | true | 1807 | 2018-12-18 ~ 2026-05-28 |
| C (006598) | csrc_eid | 5755:2030-1020 | accumulated_nav | accumulated_nav | verified | true | 1807 | 2018-12-18 ~ 2026-05-28 |
| E (014217) | csrc_eid | 5755:2030-1040 | accumulated_nav | accumulated_nav | verified | true | 994 | 2022-04-25 ~ 2026-05-28 |
| F (022176) | csrc_eid | 5755:2030-1050 | accumulated_nav | accumulated_nav | verified | true | 398 | 2024-10-08 ~ 2026-05-28 |

### 8.3 Smoke 证明范围

| 证明项 | 是否证明 |
|---|---|
| CSRC EID accumulated source identity | ✅ |
| A/C/E/F share-class separation | ✅ |
| `nav_type="accumulated_nav"` | ✅ |
| `adjusted_basis="accumulated_nav"` | ✅ |
| `identity_status="verified"` | ✅ |
| `strong_drawdown_evidence_eligible=True`（source-level only） | ✅ |
| drawdown metric evidence | ❌ 不证明 |
| `drawdown_stress` blocker解除 | ❌ 不证明 |

**结论**：validations 和 real smoke evidence 足以接受。smoke 证明了 source identity 和 accumulated basis，未越界宣称 metric evidence 或 blocker解除。

---

## 9. 跨文件风险总结

### 9.1 风险矩阵

| 风险类别 | 风险描述 | 严重度 | 缓解措施 |
|---|---|---|---|
| CSRC EID endpoint 稳定性 | 依赖公开 HTTP endpoint，无 SLA | low | fail-closed 覆盖；endpoint 变化触发 `schema_drift`/`unavailable`/`identity_mismatch` |
| 006597 家族硬编码 | `_EXPECTED_SHARE_CLASSES` 固定为 006597 家族 | low | 当前 scope 正确限定；扩展需新增 verified identity |
| F direct-search 回退硬编码 | `if fund_code != "022176"` 硬编码 | low | 当前 scope 内可接受 |
| 重复日期检测缺失 | `_normalize_csrc_accumulated_records` 不检测重复 | low | 应在后续 model-level invariant gate 补强 |
| `source_query_params` 语义混合 | HTTP 参数与请求上下文共存 | low | 不影响功能；future consumer 应区分使用 |
| `force_refresh` 混入 query params | 控制参数出现在 source provenance | low | 语义偏差不影响正确性 |
| detail 页正则依赖 | `_parse_share_class_from_text` 依赖特定 HTML 格式 | low | fail-closed 行为正确 |

### 9.2 无跨文件风险

| 检查项 | 结果 |
|---|---|
| 无 extractor/score/snapshot/quality/golden 跨文件影响 | ✅ |
| 无 Service/UI/Host/Agent/dayu 跨文件影响 | ✅ |
| 无 bond_risk_evidence 跨文件影响 | ✅ |
| 无 reports artifacts 跨文件影响 | ✅ |
| 无 pyproject.toml 依赖变更 | ✅ |

---

## 10. Aggregate Verdict

### 10.1 Verdict

**accepted**

### 10.2 理由

1. **前序 plan review findings 全部真关闭**：MiMo F1-F10 和 GLM R1-R2/N1-N4 均通过 plan fix 和 rereview 验证关闭。

2. **Implementation review residuals 均可接受**：MiMo 和 GLM 的 implementation review 共识别 7 项 residuals，全部为 low severity 或 expected（drawdown_stress blocker）。无 blocking residual。

3. **CSRC EID source adapter 实现正确**：
   - identity：search → detail → classification 三重验证，fundId=5755 双重验证
   - pagination：total=0/total changes/last page boundary 均有 fail-closed
   - parser：stdlib html.parser，无外部依赖
   - fail-closed：8 类 taxonomy 正确使用，classified errors 直接传播
   - source_query_params：显式包含 HTTP 参数，规范化为 tuple
   - HTTP retry：3 次尝试，timeout/transport/5xx 可重试，4xx 不重试

4. **typed contract 与 repository 一致**：
   - default source：`FundNavRepository()` 默认 `CsrcEidNavSource()`
   - no fallback：CSRC classified failure 直接上抛
   - raw-unit compatibility：constructor injection 保留，`load_nav_data()` 行为不变
   - source branching：按 explicit `(source_nav_type, source_adjustment_basis)` 分支

5. **`strong_drawdown_evidence_eligible=True` 无误用路径**：
   - 只表示 source-level eligibility
   - bond extractor / score / snapshot / quality gate / golden 均未修改
   - docs 多处明确语义边界
   - 当前未实现 drawdown metric，无 consumer 可误用

6. **无越界修改**：所有修改均在 Fund data 层允许范围内，未触及 extractor/score/snapshot/quality/golden/Service/UI/Host/Agent/dayu。

7. **docs/design/control truth 对齐**：只写当前代码事实，不宣称 metric/golden/readiness/blocker解除。

8. **validations 和 real smoke evidence 充足**：ruff passed、925 tests passed、92.37% coverage、A/C/E/F real smoke 全部成功。

### 10.3 Residuals（需 controller judgment 记录）

| Residual | Owner | Required handling |
|---|---|---|
| `force_refresh` 出现在 `source_query_params` 中 | future cleanup gate | 可将 `force_refresh` 从 `source_query_params` 移除，或显式确认属于 adapter 请求上下文 |
| `_parse_share_class_from_text` 正则依赖 detail 页格式 | future schema drift gate | 已被 `schema_drift`/`identity_mismatch` fail-closed 覆盖 |
| `_EXPECTED_SHARE_CLASSES` 硬编码 006597 家族 | future extension gate | 扩展到其他基金家族需新增 verified identity 常量 |
| F direct-search 回退路径硬编码 | future generalization gate | 若有其他份额出现 direct-search gap 需通用化 |
| 重复日期检测缺失 | future model-level invariant gate | 应在后续 gate 中与 raw-unit 路径统一补强 |
| `source_query_params` 语义混合 | future provenance hardening gate | 可考虑拆分为 `source_http_params` 和 `request_context` |
| CSRC EID endpoint 可用性 | future caching strategy gate | 建议后续 gate 评估缓存策略 |
| `drawdown_stress` blocker 仍未解除 | future reviewed drawdown metric gate | 需要独立的 reviewed drawdown metric gate 才能解除 blocker |

### 10.4 是否需 controller judgment 记录

**是**。以下事项需 controller judgment 记录：

1. **`drawdown_stress` blocker 状态**：本 gate 实现了 CSRC EID accumulated NAV source adapter normalization，`strong_drawdown_evidence_eligible=True` 表示 source-level eligibility。但 `drawdown_stress` blocker 仍未解除，需要独立的 reviewed drawdown metric gate。

2. **Next entry point**：下一入口应为 reviewed drawdown metric implementation gate，需先定义 drawdown metric contract（max drawdown、volatility 等），再实现 metric，最后才能宣称 blocker解除。

3. **Residual owner 分配**：上述 8 项 residuals 已分配到 future gates，需 controller 确认 owner 和优先级。

---

## 11. Gate Ledger 更新建议

建议在 `docs/implementation-control.md` 的 Recent Active Gate Ledger 中新增：

| Gate | Status | Artifact | Validation / judgment | Next action |
|---|---|---|---|---|
| `CSRC EID accumulated NAV adapter normalization implementation` | accepted local | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-aggregate-deepreview-mimo-20260529.md` + MiMo/GLM implementation reviews | CSRC EID A/C/E/F accumulated NAV normalized through typed boundary；`strong_drawdown_evidence_eligible=True` source-level only；drawdown_stress blocker remains；ruff/pytest/real smoke passed | reviewed drawdown metric implementation gate |

---

## 12. 文件路径

| 文件 | 路径 |
|---|---|
| 本 aggregate deepreview | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-aggregate-deepreview-mimo-20260529.md` |
| Implementation evidence | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-evidence-20260529.md` |
| Implementation review (MiMo) | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-review-mimo-20260529.md` |
| Implementation review (GLM) | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-review-glm-20260529.md` |
| Accepted plan | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-20260529.md` |
| Plan fix | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-fix-20260529.md` |
| Plan rereview (MiMo) | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-rereview-mimo-20260529.md` |
| Plan rereview (GLM) | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-rereview-glm-20260529.md` |
