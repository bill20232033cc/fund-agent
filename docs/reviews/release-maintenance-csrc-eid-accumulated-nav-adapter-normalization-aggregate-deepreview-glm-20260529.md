# CSRC EID Accumulated NAV Adapter Normalization — Aggregate Deepreview (GLM)

> **reviewer**: GLM aggregate deepreview worker
> **date**: 2026-05-29
> **review base**: commit 73da81b
> **review range**: 73da81b..HEAD (commits 6dce229, 537d252)
> **gate classification**: heavy
> **verdict**: **accepted**

---

## 0. 审查范围与方法

本 aggregate deepreview 是 CSRC EID accumulated NAV adapter normalization implementation gate 的最终聚合审查。审查对象包括：

- accepted plan (commit 6dce229)
- plan fix
- plan review GLM / MiMo
- plan rereview GLM / MiMo
- implementation evidence (commit 537d252)
- implementation review GLM / MiMo
- 生产代码 diff：`csrc_eid_nav_source.py`(新增)、`nav_source_contract.py`(新增)、`nav_models.py`、`nav_data.py`、`nav_repository.py`
- 测试 diff：`test_csrc_eid_nav_source.py`(新增)、`test_nav_repository_contract.py`、`test_nav_data.py`
- 文档 diff：`docs/design.md`、`fund_agent/fund/README.md`、`tests/README.md`

审查方法：逐文件阅读生产代码，逐 artifacts 阅读 plan/review/evidence 文档，对照 AGENTS.md、design.md 和 implementation-control.md 验证。

---

## 1. 前序 Plan Review Findings 关闭验证

### 1.1 Plan Review 发现关闭

| Review | Finding | 严重度 | 关闭状态 | 验证方式 |
|--------|---------|--------|----------|----------|
| MiMo F1 | Repository source selection 未定义 | blocking | **Closed** | `FundNavRepository.__init__` 默认 `CsrcEidNavSource()`；无 fallback；constructor injection 保留 |
| MiMo F2 | DTO 类型不兼容 | blocking | **Closed** | `_RawNavSourceResult` 统一 DTO；`source_nav_type`/`source_adjustment_basis` 为 required fields |
| MiMo F3 | `strong_drawdown_evidence_eligible` 语义冲突 | blocking | **Closed** | Option A 实行：CSRC accumulated verified → `True`，但仅 source-level eligibility，不解除 blocker |
| MiMo F4 | Sync/async 桥接 | blocking | **Closed** | `CsrcEidNavSource.load_raw_nav_source` 为 async；使用 `httpx.AsyncClient` |
| MiMo F5 | HTML parser 依赖 | non-blocking | **Closed** | stdlib `html.parser.HTMLParser`，无第三方依赖 |
| MiMo F6 | HTTP 超时/重试 | non-blocking | **Closed** | `connect=10, read=30, write=10, pool=10`；最多 3 次尝试 |
| MiMo F7 | Pagination 边界场景 | non-blocking | **Closed** | total=0 → `not_found`；total 跨页变化 → `integrity_error`；last-page boundary → `integrity_error` |
| MiMo F8 | `strong_drawdown` 测试缺失 | non-blocking | **Closed** | test matrix 增加 CSRC source eligibility 专项测试 |
| MiMo F9 | stock-sdk 拒绝测试模糊 | non-blocking | **Closed** | 三个具体测试：无运行时依赖、date-shift integrity_error、dividend-only 不能构造 series |
| MiMo F10 | docs/design.md 更新范围 | non-blocking | **Closed** | 只写当前事实，禁止策略措辞 |
| GLM R1 | Source adapter Protocol/类型契约 | required | **Closed** | `nav_source_contract.py` 新增 `_NavSourceAdapter` Protocol 和 `_RawNavSourceResult` DTO |
| GLM R2 | Repository source selection mechanism | required | **Closed** | 与 MiMo F1 同源，统一解决 |
| GLM N1 | `source_nav_type` deferred choice | non-blocking | **Closed** | 明确为 required field |
| GLM N2 | HTTP/parser 选择 | non-blocking | **Closed** | httpx.AsyncClient + stdlib HTMLParser |
| GLM N3 | A/C 空白日期枚举 | non-blocking | **Closed** | fixture 增加 `2018-12-07`、`2018-12-14` |
| GLM N4 | `单位净值` 空白处理语义 | non-blocking | **Closed** | 先处理 blank `累计净值`；`累计净值` 有值但 `单位净值` blank → `schema_drift` |

### 1.2 Plan Rereview 确认

两份独立 rereview（GLM 和 MiMo）均确认所有前期发现 **Closed**，plan 内部一致性检查 8 项全部通过，code-generation-readiness 5 项标准全部满足。无新发现。

**结论：前序 plan review findings 全部真正关闭，无遗漏。**

---

## 2. Implementation Review Residual 可接受性评估

### 2.1 GLM Implementation Review Findings (4 项)

| # | 严重度 | 内容 | 可接受性 |
|---|--------|------|----------|
| F1 | LOW | `source_query_params` 混入非 HTTP provenance 元数据 | **可接受** — 无 consumer 受影响；建议后续 cleanup gate 拆分 |
| F2 | LOW | 累计净值路径无显式重复日期检测 | **可接受** — model 层 `_validate_record_shape` 已有重复日期检测（nav_models.py:416-423）；smoke 1807 条无重复 |
| F3 | LOW | `_normalize_raw_unit_series` 与 `load_nav_series` 冗余空 records 检查 | **可接受** — 纯防御性编码，无功能影响 |
| F4 | INFO | `NavSourceMetadata.__post_init__` docstring 冗余 | **可接受** — 不影响正确性 |

### 2.2 MiMo Implementation Review Findings (3 项)

| # | 严重度 | 内容 | 可接受性 |
|---|--------|------|----------|
| 3.1 | LOW | `force_refresh` 出现在 `source_query_params` 中语义偏差 | **可接受** — 与 GLM F1 同源；建议后续 cleanup |
| 3.2 | LOW | `_parse_share_class_from_text` 正则依赖 CSRC EID HTML 格式 | **可接受** — 格式变化时触发 `identity_mismatch` fail-closed；行为正确 |
| 3.3 | LOW | `_EXPECTED_SHARE_CLASSES` 硬编码 006597 家族 | **可接受** — 当前 gate 范围限定为 006597 家族；未来扩展需同步更新 |

### 2.3 Residual 综合评估

7 项 residual 全部为 LOW/INFO 级别，不影响功能正确性、fail-closed 语义或生产行为。建议在后续 cleanup 或扩展 gate 中处理 F1/3.1（`source_query_params` 语义拆分）和 3.2（HTML 格式稳定性监控）。

---

## 3. CSRC EID Source Adapter 跨文件风险评估

### 3.1 Identity

- **search → detail → classification** 三步确定性验证
- `fund_id == _VERIFIED_FUND_ID ("5755")` 双重检查（`_resolve_fund_id` 第 382 行 + `_select_share_class` 第 732 行）
- A/C/E/F 份额 code 映射验证：`_EXPECTED_SHARE_CLASSES` + `_select_share_class` 的 `share_class/classification/product_fund_code` 三重校验
- F direct-search gap：仅在 `NavDataContractError` 且 `category ∈ {"not_found", "schema_drift"}` 时回退到产品锚点 `_PRODUCT_FUND_CODE`（第 370-381 行），非 F 代码不触发
- **评估：无跨文件风险。** identity 验证逻辑完全自包含在 `csrc_eid_nav_source.py`，repository 层通过 `_extract_identity` + `_validate_returned_identity` 做二次校验。

### 3.2 Pagination

- `expected_total` 首页初始化后跨页不变性校验（第 444-449 行）
- 每页 `range_start/range_end` 与 `start/limit` 计算值一致性校验（第 451-458 行）
- 每页 `len(page.rows)` 与 `expected_count` 一致性校验（第 459-464 行）
- 翻页完成后总 `len(rows)` 与 `expected_total` 一致性校验（第 470-475 行）
- **评估：无跨文件风险。** 分页逻辑完全在 `_load_all_pages` 内，校验结果直接 raise `NavDataContractError`。

### 3.3 Parser

- stdlib `HTMLParser` 子类 `_TableParser`，无第三方依赖
- 表头检测要求 6 个必需列（第 863 行）
- 行过滤通过 `_DATE_RE.fullmatch` 确保日期格式（第 908 行）
- 分页 total 通过两个正则提取（`_TOTAL_RE` + `_PAGE_RE`，第 51-52 行）
- **评估：无跨文件风险。** parser 结果通过 `_CsrcNetPage` dataclass 传递，schema_drift 场景全部 fail-closed。

### 3.4 Fail-Closed

- 所有错误路径使用 `NavDataContractError` 并携带显式 `category`
- `schema_drift`、`identity_mismatch`、`integrity_error` → 直接传播，无静默降级
- repository 层 `except NavDataContractError: raise`（第 143-144 行）保持 source 错误语义
- `except Exception` → 包装为 `unavailable`（第 145-152 行）
- 无 CSRC EID → Akshare/stock-sdk/Eastmoney fallback
- **评估：无跨文件风险。** fail-closed 语义贯穿 source adapter → repository → model validator 全链路。

### 3.5 source_query_params

- `NavSourceMetadata` 新增 `source_query_params: tuple[tuple[str, str], ...] = ()`
- `__post_init__` 规范化为不可变 tuple（nav_models.py:154-158）
- CSRC EID 填充 HTTP 参数 + provenance 上下文（csrc_eid_nav_source.py:476-488）
- Legacy Akshare 填充空 tuple（nav_data.py:328, 351）
- **评估：无跨文件风险。** 默认空 tuple 保证向后兼容；类型为 immutable tuple，consumer 安全。残余：HTTP 参数与 provenance 混合（GLM F1 / MiMo 3.1），建议后续 cleanup。

### 3.6 HTTP Retry

- `httpx.AsyncClient` + 显式 timeout（connect=10, read=30, write=10, pool=10）
- 最多 `_MAX_ATTEMPTS = 3` 次尝试
- 重试范围：`TimeoutException`、`TransportError`、HTTP 5xx（通过 `_TransientHttpError`）
- 4xx → `unavailable`，不重试
- 空响应 → `schema_drift`
- 重试间隔 `asyncio.sleep(0)`（第 540 行），不阻塞
- **评估：无跨文件风险。** HTTP 层完全封装在 `_request_text` 内。

---

## 4. Typed Contract 与 Repository 兼容性

### 4.1 Default Source

- `FundNavRepository()` 无参构造创建 `CsrcEidNavSource()`（nav_repository.py:88）
- Constructor injection 保留：`source_adapter: _NavSourceAdapter | None = None`（nav_repository.py:75）
- Legacy Akshare 路径通过注入 `FundNavDataAdapter` 进入 raw-unit 分支
- **评估：一致。** 默认行为变更合理，injection 兼容。

### 4.2 No Fallback

- CSRC EID 失败 → `NavDataContractError` 直接传播
- Repository 不捕获 `NavDataContractError` 后 fallback
- `except Exception` → 包装为 `unavailable`（非 eligible 失败不 fallback）
- **评估：一致。** 与 plan 4.4 "no fallback" 完全对齐。

### 4.3 Raw-Unit 兼容

- `(source_nav_type, source_adjustment_basis) == ("unit_nav", "raw_unit_nav")` → `_normalize_raw_unit_series`（nav_repository.py:162-174）
- `FundNavDataAdapter` 新增 `load_raw_nav_source` 方法实现 `_NavSourceAdapter` Protocol（nav_data.py:282-357）
- `NavDataResult` 旧路径 `load_nav_data()` 不变（nav_data.py:242-280）
- **评估：一致。** Legacy 路径完全保留，无破坏性变更。

### 4.4 Unknown Pair Fail-Closed

- 非识别的 `(source_nav_type, source_adjustment_basis)` 组合 → `adjustment_basis_unknown`（nav_repository.py:188-196）
- **评估：一致。** 禁止未知组合静默通过。

---

## 5. `strong_drawdown_evidence_eligible` 误用路径分析

### 5.1 当前设置

- CSRC accumulated verified series：`strong_drawdown_evidence_eligible=True`（nav_repository.py:402）
- Raw-unit series：`strong_drawdown_evidence_eligible=False`（nav_repository.py:294）
- Requested-code-only series：`strong_drawdown_evidence_eligible=False`（由 `_apply_strong_drawdown_eligibility` 强制设置，nav_models.py:564-569）

### 5.2 Validator 行为

`_apply_strong_drawdown_eligibility`（nav_models.py:550-583）只添加 reason 设为 `False`：
- `identity_status == "requested_code_only"` → False
- `identity_status != "verified"` → False
- `adjusted_basis == "raw_unit_nav"` → False

对于 `identity_status="verified"` + `adjusted_basis="accumulated_nav"`，validator 不添加任何 reason，保持 repository 设置的 `True`。

### 5.3 消费路径检查

- **当前无任何代码** 读取 `strong_drawdown_evidence_eligible` 来：
  - 修改 score/snapshot/quality gate 状态
  - 解除 `drawdown_stress` blocker
  - 改变 `bond_risk_evidence.v1` 满足条件
  - 影响最终判断或检查清单
- `drawdown_stress` 仍为 `bond_risk_evidence_missing.baseline_blocking=true`
- 后续 drawdown metric gate 仍需 reviewed contract 才能消费该字段

### 5.4 误用风险评估

- `strong_drawdown_evidence_eligible=True` 是一个 **source-level 声明**，不自动触发任何 metric/blocker 状态变更
- Plan fix (MiMo F3, Option A) 在 6 个位置统一了这一语义
- `docs/design.md` 明确写了"当前未实现 drawdown metric，未解除债券基金 `drawdown_stress` blocker"

**结论：不存在误用路径。** 当前无代码消费该字段来解除 `drawdown_stress` blocker。

---

## 6. 边界违反检查

| 禁止修改的模块 | 是否触碰 | 验证方式 |
|---------------|---------|---------|
| extractors/ | **否** | diff stat 确认 |
| data_extractor | **否** | diff stat 确认 |
| score/quality_gate | **否** | diff stat 确认 |
| snapshot | **否** | diff stat 确认 |
| renderer | **否** | diff stat 确认 |
| services/ | **否** | diff stat 确认 |
| ui/ | **否** | diff stat 确认 |
| host/ | **否** | diff stat 确认 |
| agent/ | **否** | diff stat 确认 |
| golden fixtures | **否** | diff stat 确认 |
| dayu runtime | **否** | 无新依赖 |

全部修改文件限定在 `fund_agent/fund/data/` + `tests/fund/data/` + `docs/` 范围内。

**结论：无边界违反。**

---

## 7. Docs/Design/Control Truth 检查

### 7.1 design.md 更新

- 只描述当前代码实现事实
- 新增 CSRC EID accumulated path 描述，包含 `nav_type`、`adjusted_basis`、`identity_status` 的具体值
- 明确声明"当前未实现 drawdown metric，未解除债券基金 `drawdown_stress` blocker"
- 未使用 "primary"、"permanent" 或 "default source strategy" 等设计判断用语
- Legacy Akshare 路径保留为"兼容分支"描述

**评估：未提前宣称 metric/golden/readiness。**

### 7.2 implementation-control.md

未在本次 diff 范围内修改（controller judgment 单独处理），control doc 的 Next Entry Point 和 Open Residuals 仍准确指向当前状态。

### 7.3 README 更新

- `fund_agent/fund/README.md` 和 `tests/README.md` 只更新模块描述和测试说明
- 未宣称架构变更或能力升级

**结论：文档与代码事实对齐，无提前宣称。**

---

## 8. Validation 与 Smoke Evidence

### 8.1 静态检查

- `uv run ruff check .`: All checks passed
- `uv run ruff check`（focused on modified files）: All checks passed

### 8.2 测试覆盖

- Focused tests: 64 passed (0.12s)
- Full suite: **925 passed** (4.61s)，覆盖率 **92.37%**
- CI 门槛 50%：远超

### 8.3 Real CSRC EID Smoke

| 份额 | 记录数 | 日期范围 | identity_status | nav_type |
|------|--------|----------|-----------------|----------|
| A (006597) | 1807 | 2018-12-18 ~ 2026-05-28 | verified | accumulated_nav |
| C (006598) | 1807 | 2018-12-18 ~ 2026-05-28 | verified | accumulated_nav |
| E (014217) | 994 | 2022-04-25 ~ 2026-05-28 | verified | accumulated_nav |
| F (022176) | 398 | 2024-10-08 ~ 2026-05-28 | verified | accumulated_nav |

四份额全部 `strong_drawdown_evidence_eligible=True`，`adjusted_basis="accumulated_nav"`。

### 8.4 Validation 充分性评估

- 生产代码 5 个文件，测试代码 3 个文件，测试/代码行比约 0.67
- 覆盖了 identity 验证、分页完整性、schema_drift、fail-closed taxonomy、份额分离、空白累计净值、单位净值 diagnostics、stock-sdk 拒绝、raw-unit 兼容、显式参数、docs 一致性等全部验证矩阵领域
- Real smoke 验证了四份额端到端可达

**结论：validation 和 real smoke evidence 足以接受。**

---

## 9. Residuals 汇总

| Residual | 严重度 | 建议归属 | 处理建议 |
|----------|--------|---------|---------|
| `source_query_params` 语义混合（HTTP params + provenance） | LOW | 后续 cleanup gate | 拆分为 `http_query_params` + `request_context_params` |
| 累计净值路径无显式重复日期检测 | LOW | model 层补强 | `_validate_record_shape` 已在 model 层覆盖；smoke 无重复 |
| `_parse_share_class_from_text` 正则依赖 HTML 格式 | LOW | 监控/schema_drift 处理 | 格式变化 → fail-closed；需关注 CSRC EID schema 稳定性 |
| `_EXPECTED_SHARE_CLASSES` 硬编码 | LOW | 后续扩展 gate | 新份额类别需同步更新 |
| `drawdown_stress` blocker 未解除 | 已接受 | 后续 drawdown metric gate | 需 reviewed metric contract + implementation gate |
| CSRC EID 无 SLA | 已接受 | 运维 | 依赖政府网站可用性 |

---

## 10. Verdict

### **accepted**

理由：

1. 前序 plan review 16 项 findings 全部真正关闭，两份独立 rereview 确认
2. Implementation review 7 项 findings 全部为 LOW/INFO，无阻塞项
3. CSRC EID source adapter 的 identity/pagination/parser/fail-closed/source_query_params/HTTP retry 设计严格 fail-closed，无跨文件风险
4. Typed contract 与 repository default source/no fallback/raw-unit compatibility 完全一致
5. 不存在 `strong_drawdown_evidence_eligible=True` 被误用为 drawdown_stress blocker 解除的路径
6. 未越界修改 extractor/score/snapshot/quality/golden/Host/Agent/dayu
7. docs/design.md 只写当前代码事实，未提前宣称 metric/golden/readiness
8. 验证矩阵和 real smoke evidence 充分（925 passed, 92.37% coverage, 四份额 smoke 全部成功）

### 需要 Controller Judgment 记录的事项

- 确认 residuals 接受并指定后续 gate owner
- 确认 `drawdown_stress` blocker 下一步入口：reviewed drawdown metric contract gate
- 确认 `implementation-control.md` 控制面更新（current gate checkpoint、accepted artifacts 列表、next entry point）
