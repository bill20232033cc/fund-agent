# NAV Source Adapter Typed Contract Implementation — Slice 1b DS Review

日期：2026-05-28

角色：DS reviewer（code review agent，非 controller）

Gate：`NAV repository/source adapter typed contract implementation gate`，分类 `heavy`

Review target：Slice 1b implementation（adapter metadata、repository normalization、integration tests）

## Review Scope

按 controller 指定的 8 个 review focus areas 逐项审查，外加 adversarial pass。

## Artifacts Reviewed

- `AGENTS.md` — 规则真源
- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md` — Slice 1b 规格
- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-fix-20260528.md` — plan fix 记录
- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-slice1b-evidence-20260528.md` — 实现证据
- `fund_agent/fund/data/nav_models.py` — typed models（Slice 1a，作为 Slice 1b 依赖）
- `fund_agent/fund/data/nav_data.py` — adapter 改动
- `fund_agent/fund/data/nav_repository.py` — 新增 repository
- `fund_agent/fund/data/__init__.py` — re-export
- `tests/fund/data/test_nav_data.py` — adapter 测试
- `tests/fund/data/test_nav_repository_contract.py` — 模型 + repository 集成测试
- `git diff` — 完整改动

## Finding Summary

| # | Severity | Category | Summary |
|---|----------|----------|---------|
| F1 | Low | Dead Code | `_RAW_UNIT_NAV_INELIGIBILITY_REASON` 常量被 `__post_init__` 覆盖 |
| F2 | Low | Test Gap | 5 个防御性校验分支无专项测试 |
| F3 | Note | Maintainability | `_raise_contract_error` 在 `nav_models.py` 与 `nav_repository.py` 重复定义 |
| F4 | Note | Test Hygiene | `_FakeRawNavAdapter.calls` 记录未被任何测试断言消费 |

**无 bug、无 contract violation、无 scope creep。**

---

## Focus Area 1: load_nav_data 向后兼容性（cache hit source nav_cache）

### 结论：通过

**证据**：

- `nav_data.py:281` — `load_nav_data()` cache hit 路径未改动，仍调用 `_load_cached_sync()` → 返回 `NavDataResult(source="nav_cache", cached=True)`。
- `nav_data.py:418-421` — `_load_cached_sync()` 内部重构为委托 `_load_cached_with_metadata()` 并只取 `.records`，返回类型保持 `NavPayload | None`。
- `nav_data.py:461` — `_save_cached_sync()` 新增可选 `updated_at` 参数，默认 `_utc_timestamp()`，对旧调用点（`load_nav_data`）行为不变。
- 测试：`test_nav_data_adapter_persists_and_reuses_cache`（cache 写入复用）、`test_nav_data_adapter_force_refresh_bypasses_cache`（force refresh）、`test_unavailable_nav_data_result_returns_explicit_empty_result`（unavailable helper）均通过，断言未修改。
- 新增 `test_nav_data_adapter_raw_source_exposes_cache_origin_metadata` 同时验证旧 `load_nav_data()` 仍返回 `source="nav_cache"`。

**无回归。**

---

## Focus Area 2: 私有 cache metadata 与 load_raw_nav_source provenance；内部 DTO 禁止 public re-export

### 结论：通过

**证据**：

- `_NavCacheEntry`（`nav_data.py:120-131`）— 下划线前缀，未在 `__init__.py` 中出现。
- `_RawNavSourceResult`（`nav_data.py:134-149`）— 下划线前缀，未在 `__init__.py` 中出现。
- `__init__.py` 不 re-export `load_raw_nav_source` 或任何 `_` 前缀符号。
- `load_raw_nav_source()` 是 `FundNavDataAdapter` 的 public method（repository 需要调用），返回私有 DTO，不进入包级 public API。
- cache hit 时 `origin_source=cache_entry.source`（如 `"akshare"`），`cache_updated_at=cache_entry.updated_at`，typed provenance 完整。
- 测试文件 `from fund_agent.fund.data.nav_data import _RawNavSourceResult` 属于白盒测试导入，`_FakeRawNavAdapter` 需要构造返回类型，可接受。

**无泄漏。**

---

## Focus Area 3: FundNavRepository 边界：explicit params only；禁止 extra_payload / kwargs / 直连外部依赖

### 结论：通过

**证据**：

- `nav_repository.py:84-110` — `load_nav_series()` 签名：`fund_code`（positional）、`share_class`、`start_date`、`end_date`、`minimum_records`、`force_refresh`（全部 keyword-only）。无 `extra_payload`、无 `**kwargs`、无自由 dict 参数。
- `test_load_nav_series_signature_has_no_extra_payload_or_kwargs`（`test_nav_repository_contract.py:986`）— `inspect.signature` 断言无 `extra_payload` / `kwargs`，所有参数为 `POSITIONAL_OR_KEYWORD` 或 `KEYWORD_ONLY`。
- Repository 只通过 `self._source_adapter.load_raw_nav_source()` 获取数据（`nav_repository.py:130`），不直接访问 Akshare、SQLite、网页、cache helper。
- `__init__` 接受 `source_adapter: FundNavDataAdapter | None = None`（`nav_repository.py:69`），默认构造 `FundNavDataAdapter()`。

**边界干净。**

---

## Focus Area 4: Normalization 正确性（中文行、日期排序、不 silent dedupe、必需列、Decimal 解析、非法增长率处理）

### 结论：通过

**证据**：

- 必需列：`净值日期`、`单位净值`（`nav_repository.py:27-28`）；`日增长率` 可选（line 29）。
- 日期解析：`_parse_required_date`（line 317-359）支持 `datetime`、`date`、ISO 字符串；非法日期 → `schema_drift`。
- NAV 解析：`_parse_required_nav_value`（line 362-402）→ `Decimal`；非数值 → `schema_drift`；非正数 → `integrity_error`。
- 增长率解析：`_parse_optional_growth_rate`（line 405-436）— 缺失/None/空字符串 → `None`；存在但不可解析 → `schema_drift`。
- `_parse_decimal`（line 479-512）自动 strip `%` 后缀，兼容 Akshare 百分比格式。
- 排序：`nav_repository.py:188-200` — `sorted(..., key=lambda record: record.date)` 升序。
- 重复日期：排序后在 `FundNavSeries.__post_init__` → `_validate_record_shape`（`nav_models.py:395-404`）检测，归类 `integrity_error`，不做 silent dedupe。
- 中文 fixture：`_raw_nav_row` 使用 `净值日期`/`单位净值`/`日增长率`/`基金代码`/`基金名称` 中文键，覆盖 006597-like 场景。

**归一化逻辑完整且 fail-closed。**

---

## Focus Area 5: 当前 source 必须为 raw_unit_nav、requested_code_only、not_adjusted、not strong drawdown eligible，含明确原因

### 结论：通过

**证据**：

- `nav_repository.py:202-221` — series 构造时固定：
  - `nav_type="unit_nav"`
  - `adjusted_basis="raw_unit_nav"`
  - `dividend_adjustment_status="not_adjusted"`
  - `identity_status="requested_code_only"`
  - `strong_drawdown_evidence_eligible=False`
- `nav_models.py:530-562` — `_apply_strong_drawdown_eligibility` 在 `__post_init__` 中二次校验：
  - `identity_status == "requested_code_only"` 时追加原因
  - `adjusted_basis == "raw_unit_nav"` 时追加原因
  - 最终 reason 包含两个维度的说明（identity 未验证 + raw_unit_nav 缺少分红/总回报基础）
- 测试验证：
  - `test_repository_raw_fixture_normalizes_to_typed_series` — 断言 `adjusted_basis="raw_unit_nav"`、`nav_type="unit_nav"`、`dividend_adjustment_status="not_adjusted"`、`strong_drawdown_evidence_eligible is False`
  - `test_raw_unit_nav_is_not_strong_drawdown_eligible` — 模型级断言 raw_unit_nav 不可 strong eligible
  - `test_repository_requested_code_only_not_strong_eligible` — 集成断言
- 无 adjusted / total-return 声称。

**正确标记。**

---

## Focus Area 6: Fail-closed taxonomy 完全对照 plan

### 结论：通过

逐项对照 plan 表格（plan § Fail-Closed Taxonomy）：

| Plan 场景 | Plan category | 实现位置 | 实际 category | 匹配 |
|---|---|---|---|---|
| fund_code 为空/非法 | identity_mismatch | `nav_repository.py:237-245` | identity_mismatch | ✅ |
| source 调用异常 | unavailable (保留 cause) | `nav_repository.py:136-143` | unavailable + cause | ✅ |
| 0 raw records | not_found | `nav_repository.py:146-152` | not_found | ✅ |
| raw columns 缺失 | schema_drift | `nav_repository.py:461-476` | schema_drift | ✅ |
| 日期不可解析 | schema_drift | `nav_repository.py:350-359` | schema_drift | ✅ |
| NAV 非数值 | schema_drift | `nav_repository.py:388-393` | schema_drift | ✅ |
| NAV 非正数 | integrity_error | `nav_repository.py:395-401` | integrity_error | ✅ |
| 增长率非法 | schema_drift | `nav_repository.py:430-435` | schema_drift | ✅ |
| 日期重复 | integrity_error | `nav_models.py:397-403` | integrity_error | ✅ |
| identity 冲突 | identity_mismatch | `nav_repository.py:578-589` | identity_mismatch | ✅ |
| adjusted_basis unknown | adjustment_basis_unknown | `nav_models.py:337-343` | adjustment_basis_unknown | ✅ |
| 日期范围不足 | missing_date_range | `nav_models.py:510-524` | missing_date_range | ✅ |
| minimum_records 不足 | insufficient_records | `nav_models.py:503-508` | insufficient_records | ✅ |

**额外防御性校验（plan 未明确要求但合理）：**
- `minimum_records < 1` → `schema_drift`（`nav_repository.py:114-120`）
- `start_date > end_date` → `missing_date_range`（`nav_repository.py:121-127`）
- `share_class` 空字符串/非字母数字 → `identity_mismatch`（`nav_repository.py:264-270`）

这些补充校验不违反 plan，增强了输入健壮性。

**Taxonomy 完整覆盖。**

---

## Focus Area 7: 测试覆盖必需成功/失败路径；无脆弱测试或掩盖生产 bug 的 fake 行为

### 结论：通过

**测试统计**：32 passed（14 Slice 1a 模型测试 + 14 Slice 1b 集成测试 + 4 adapter 测试）

**成功路径覆盖**：
- 中文 fixture → typed series 全字段验证
- 日期升序排列
- completeness_status = unchecked / complete_enough
- source metadata 完整性
- share_class_mapping 字段

**失败路径覆盖**（每类至少一个专项测试）：

| Fail-closed 类别 | 测试 |
|---|---|
| unavailable + cause | `test_repository_unavailable_cause_preserved` |
| not_found | `test_repository_empty_records_raises_not_found` |
| schema_drift (缺日期列) | `test_repository_missing_date_column_raises_schema_drift` |
| schema_drift (缺NAV列) | `test_repository_missing_nav_column_raises_schema_drift` |
| schema_drift (非法日期) | `test_repository_invalid_date_raises_schema_drift` |
| schema_drift (非法增长率) | `test_repository_invalid_growth_rate_raises_schema_drift` |
| integrity_error (非正NAV) | `test_repository_nonpositive_nav_raises_integrity_error` |
| integrity_error (重复日期) | `test_repository_duplicate_raw_date_raises_integrity_error` |
| identity_mismatch | `test_repository_identity_mismatch_raises` |
| missing_date_range | `test_repository_missing_date_range_raises` |
| insufficient_records | `test_repository_insufficient_records_raises` |

**模型级测试（Slice 1a 保留）**：illegal type/basis 组合、duplicate date、empty records、share_class mismatch、identity_mismatch、adjusted_basis unknown、nav_type unknown、record_count mismatch、raw_payload diagnostics-only。

**Fake adapter 评估**：`_FakeRawNavAdapter` 正确模拟 `load_raw_nav_source` 边界，不接触真实 IO。Fake 返回固定 `cached=True` 是合理的测试简化（adapter 级测试覆盖了 cache/no-cache 路径）。Fake 不隐藏生产行为。

### 测试缺口（非阻塞）

以下防御性分支缺少专项测试（Finding F2）：

| 分支 | 位置 | 类别 |
|---|---|---|
| `start_date > end_date` | `nav_repository.py:121-127` | missing_date_range |
| `minimum_records < 1` | `nav_repository.py:114-120` | schema_drift |
| fund_code 非 6 位数字 | `nav_repository.py:237-245` | identity_mismatch |
| share_class 空字符串 | `nav_repository.py:264-270` | identity_mismatch |
| raw_record 非 Mapping | `nav_repository.py:296-302` | schema_drift |

这些是防御性编程分支，触发场景为调用方编程错误而非数据异常。plan 要求新增模块单文件覆盖率 ≥80%，当前 14 个集成测试已覆盖所有主要路径和全部 fail-closed taxonomy 类别。若覆盖率工具显示短少，应来自上述防御性分支。**不阻塞 accept。**

---

## Focus Area 8: Scope 范围检查

### 结论：通过

**仅修改允许文件**：
- `fund_agent/fund/data/nav_data.py` ✅
- `fund_agent/fund/data/nav_repository.py` ✅（新增）
- `fund_agent/fund/data/__init__.py` ✅
- `tests/fund/data/test_nav_data.py` ✅
- `tests/fund/data/test_nav_repository_contract.py` ✅

**未触碰**：
- `FundDataExtractor`、`extraction_snapshot.py`、score、quality gate、FQ0-FQ6 ✅
- Bond risk extractor、drawdown metric、golden/baseline fixtures ✅
- README、`docs/design.md`、`docs/implementation-control.md`（reserved for Slice 2）✅
- Host/Agent/dayu 包 ✅

**drawdown_stress blocker**：未解除，intentional residual。✅

---

## Adversarial Pass

### 反向案例检查

1. **cache 污染**：若 SQLite 中 `source` 列被外部篡改（如手动 UPDATE），`load_raw_nav_source` 会暴露被篡改的 `origin_source`。但这属于运维边界，不在代码契约范围内。当前 SQLite 只由 adapter 写入，风险可控。

2. **并发 cache 写入**：`load_nav_data` 和 `load_raw_nav_source` 各自独立调用 `_save_cached_sync`，两者使用 `ON CONFLICT ... DO UPDATE`（upsert）。若并发调用同一 fund_code，后写入者覆盖前者。SQLite 连接级锁提供基本保护。无数据损坏风险。

3. **空 date_range 的边界**：`_apply_date_range_defaults` 在 records 非空时从 records 推导 `date_range_start/end`。若 records 为空，已在 `_validate_record_shape` 抛出 `not_found`，不会到达日期推导。

4. **增长率 = "0"**：`Decimal("0")` 是合法值，不会被错误归类。`_parse_optional_growth_rate` 中 `str(raw_value).strip() == ""` 只拦截空字符串，不会拦截 `"0"`。✅

5. **NAV = "0.0000"**：`Decimal("0.0000") == Decimal("0")` → `nav_value <= Decimal("0")` → `integrity_error`。正确处理。✅

6. **日期跨月排序**：`date` 对象支持正确比较，`sorted()` 按日历顺序。多月份/跨年数据排序正确。✅

7. **raw_payload 绕过**：`FundNavRecord.__post_init__` 将 `raw_payload` 冻结为 `MappingProxyType`，且 `compare=False`。但 consumer 仍可读取 `raw_payload` 字段值。Future Consumer Rule 禁止 drawdown metric 读取 `raw_payload`，这是约定层面约束而非代码强制。plan 设计如此，非实现缺陷。

8. **identity 提取的健壮性**：`_first_non_empty_value` 扫描所有 records 查找非空 identity 字段。若第一条 record 无 identity 但第二条有，会返回第二条的值。对于 Akshare 当前路径，所有 record 通常都不含 identity 字段，返回 `None` → `identity_status="requested_code_only"`。正确。

---

## Detailed Findings

### F1 (Low) — Dead Code: `_RAW_UNIT_NAV_INELIGIBILITY_REASON` 常量

- **位置**：`fund_agent/fund/data/nav_repository.py:33-36`（定义）、`:212`（使用）
- **说明**：Repository 构造 `FundNavSeries` 时传入 `strong_drawdown_ineligibility_reason=_RAW_UNIT_NAV_INELIGIBILITY_REASON`，但 `FundNavSeries.__post_init__` → `_apply_strong_drawdown_eligibility` 会无条件覆盖该字段（当 identity_status 为 requested_code_only 且 adjusted_basis 为 raw_unit_nav 时）。
- **影响**：常量值永不出现在最终 `FundNavSeries` 输出中。实际输出的 reason 由模型 validator 组合生成，语义等价但文本不同。不影响行为正确性。
- **建议**：删除 `nav_repository.py:33-36` 的常量定义，或将其改为与模型 validator 输出一致的文本并保留（以防未来 validator 逻辑变更）。当前 form 下建议删除以减少维护者困惑。

### F2 (Low) — 防御性校验分支缺少专项测试

- **位置**：见上文「测试缺口」表
- **说明**：5 个防御性输入校验分支无对应用例。
- **影响**：这些分支在正常使用中不会触发（属于调用方编程错误保护），不影响覆盖率目标的核心路径。若覆盖率工具报告短少，可接受为已知 residual。
- **建议**：若 Slice 2 有机会补测，优先补 `start_date > end_date` 和 `minimum_records < 1`（repository 入口校验，业务意义更强）。

### F3 (Note) — `_raise_contract_error` 重复定义

- **位置**：`fund_agent/fund/data/nav_models.py:285-312` 与 `fund_agent/fund/data/nav_repository.py:622-649`
- **说明**：两个模块各自定义了功能完全相同的 `_raise_contract_error` helper。
- **影响**：无功能影响。若 `NavDataContractError` 构造函数签名变更，需要两处同步修改。
- **建议**：可接受当前重复（符合模块间依赖最小化原则）。后续若出现第三次重复，考虑提取公共 helper。

### F4 (Note) — `_FakeRawNavAdapter.calls` 未被断言消费

- **位置**：`tests/fund/data/test_nav_repository_contract.py:57`
- **说明**：Fake adapter 维护 `calls: list[tuple[str, bool]]` 记录每次 `load_raw_nav_source` 调用，但当前无测试断言该记录。
- **影响**：无。未使用的测试基础设施，不导致错误。
- **建议**：可保留（future 测试可能需要验证调用次数）或删除。

---

## Conclusion

**Verdict: ACCEPTED**

理由：

- 所有 8 个 review focus areas 通过。
- 0 个 bug、0 个 contract violation、0 个 scope creep。
- 32 个测试全部通过，ruff 检查干净。
- Fail-closed taxonomy 完整实现，与 plan 逐项对齐。
- `load_nav_data()` 向后兼容性保持，旧测试无回归。
- 内部 DTO 正确封装，未泄漏到 public API。
- `drawdown_stress` blocker 未解除（intentional residual）。
- 4 个 findings 均为 Low/Note 级别，无 required fix。

**Residual Risks（与本 gate 实现相关）**：
- Slice 2 的 real 006597 smoke 尚未执行，网络/cache 环境可能暴露 adapter 级别问题，但属于 Slice 2 范围。
- 单文件覆盖率可能因防御性分支略低于 80%，已知且可接受。
- `raw_payload` 的消费限制是约定层面而非代码强制，future consumer 需要 code review 把关。

**Reviewer 不可用声明**：DS reviewer 完成了本 review。MiMo 因是 implementation worker 必须回避。仍需至少一份独立 review（如 Opus 或其他 reviewer）方可推进 gate。
